from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import logging
from pathlib import Path
import threading
import time
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from src.alert_store import AlertStore
from src.config import account_connection_payload
from src.config import load_settings
from src.config import save_account_connection
from src.live_trading import LiveTrading
from src.paper_trading import PaperTrading
from src.polymarket_account_client import AccountClientConfig
from src.polymarket_account_client import PolymarketAccountClient
from src.polymarket_client import PolymarketClient
from src.scanner import ArbitrageScanner
from src.smart_wallet_tracker import SmartWalletTracker
from src.trader_tracker import TraderTracker
from src.watchlist import Watchlist


STATIC_DIR = Path(__file__).resolve().parent.parent / "web"
WATCHLIST_MONITOR_INTERVAL_SECONDS = 30

LOGGER = logging.getLogger(__name__)
_watchlist_monitor_lock = threading.Lock()
_watchlist_refresh_lock = threading.Lock()
_live_reconcile_lock = threading.Lock()
_watchlist_monitor_started = False
_watchlist_monitor_state: dict[str, Any] = {
    "running": False,
    "intervalSeconds": WATCHLIST_MONITOR_INTERVAL_SECONDS,
    "lastRunAt": None,
    "lastResult": None,
    "lastError": None,
}


def decimal_to_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: decimal_to_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_to_json(item) for item in value]
    if isinstance(value, tuple):
        return [decimal_to_json(item) for item in value]
    return value


def clob_collateral_amount(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        raw = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return float(raw / Decimal("1000000"))


def clob_collateral_allowance(value: Any) -> float | str | None:
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        amounts = [clob_collateral_amount(item) for item in value.values()]
        numeric_amounts = [amount for amount in amounts if amount is not None]
        if not numeric_amounts:
            return None
        if any(amount > 1_000_000_000 for amount in numeric_amounts):
            return "Unlimited"
        return min(numeric_amounts)
    amount = clob_collateral_amount(value)
    if amount is not None and amount > 1_000_000_000:
        return "Unlimited"
    return amount


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    settings = load_settings()

    def build_scanner() -> ArbitrageScanner:
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        return ArbitrageScanner(client)

    def build_trader_tracker() -> TraderTracker:
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        return TraderTracker(client)

    def build_smart_wallet_tracker() -> SmartWalletTracker:
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        return SmartWalletTracker(client=client, database_path=settings.database_path)

    def build_watchlist() -> Watchlist:
        return Watchlist(database_path=settings.database_path)

    def build_alert_store() -> AlertStore:
        return AlertStore(database_path=settings.database_path)

    def build_paper_trading() -> PaperTrading:
        return PaperTrading(database_path=settings.database_path)

    def build_live_trading() -> LiveTrading:
        return LiveTrading(database_path=settings.database_path)

    def live_markets_for_open_positions(live_trading: LiveTrading) -> dict[str, dict[str, Any]]:
        condition_ids = live_trading.list_open_condition_ids()
        if not condition_ids:
            return {}
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        return client.get_markets_by_condition_ids(condition_ids)

    def live_account_user_ids() -> list[str]:
        account_settings = load_settings()
        users = [
            account_settings.polymarket_funder_address,
            account_settings.polymarket_account_address,
        ]
        unique_users = []
        for user in users:
            clean = str(user or "").strip()
            if clean and clean.lower() not in {item.lower() for item in unique_users}:
                unique_users.append(clean)
        return unique_users

    def live_account_positions() -> tuple[list[dict[str, Any]], list[str]]:
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        positions = []
        errors = []
        for user in live_account_user_ids():
            try:
                positions.extend(client.get_user_positions_raw(user, limit=500))
            except Exception as error:  # pragma: no cover - external API
                LOGGER.exception("Could not load live account positions")
                errors.append(f"positions {user[:6]}...: {error}")
        return positions, errors

    def reconcile_live_trading(live_trading: LiveTrading | None = None) -> dict[str, Any]:
        with _live_reconcile_lock:
            live_trading = live_trading or build_live_trading()
            client = PolymarketClient(
                gamma_base_url=settings.gamma_base_url,
                clob_base_url=settings.clob_base_url,
                data_base_url=settings.data_base_url,
                timeout_seconds=settings.request_timeout_seconds,
            )
            account_positions = []
            account_trades = []
            account_closed_positions = []
            errors = []
            users = live_account_user_ids()
            loaded_position_users = 0
            for user in users:
                try:
                    account_positions.extend(client.get_user_positions_raw(user, limit=500))
                    loaded_position_users += 1
                except Exception as error:  # pragma: no cover - external API
                    LOGGER.exception("Could not load live account positions for reconciliation")
                    errors.append(f"positions {user[:6]}...: {error}")
                try:
                    account_trades.extend(client.get_user_trade_activity(user, limit=100))
                except Exception as error:  # pragma: no cover - external API
                    LOGGER.exception("Could not load live account trades for reconciliation")
                    errors.append(f"trades {user[:6]}...: {error}")
                try:
                    account_closed_positions.extend(client.get_user_closed_positions(user, limit=100))
                except Exception as error:  # pragma: no cover - external API
                    LOGGER.exception("Could not load live account closed positions for reconciliation")
                    errors.append(f"closed positions {user[:6]}...: {error}")
            if users and loaded_position_users != len(users):
                return {
                    "closedPositions": 0,
                    "closedSize": 0.0,
                    "realizedPnlUsdc": 0.0,
                    "errors": errors,
                    "checkedUsers": len(users),
                    "skipped": True,
                    "reason": "Skipped live reconciliation because not every linked account position read succeeded.",
                }
            markets = live_markets_for_open_positions(live_trading)
            result = live_trading.reconcile_account_positions(
                account_positions,
                account_trades,
                account_closed_positions,
                markets,
            )
            result["errors"] = errors
            result["checkedUsers"] = len(users)
            return result

    def refresh_watchlist_trades(trades_per_wallet: int = 20) -> dict[str, Any]:
        with _watchlist_refresh_lock:
            client = PolymarketClient(
                gamma_base_url=settings.gamma_base_url,
                clob_base_url=settings.clob_base_url,
                data_base_url=settings.data_base_url,
                timeout_seconds=settings.request_timeout_seconds,
            )
            return build_watchlist().refresh_saved_wallet_trades(
                client=client,
                trades_per_wallet=trades_per_wallet,
                paper_trading=build_paper_trading(),
                live_trading=build_live_trading(),
            )

    def record_open_position_marks() -> None:
        paper_trading = build_paper_trading()
        open_positions = paper_trading.list_positions(status="OPEN", limit=5000)
        if not open_positions:
            live_trading = build_live_trading()
            reconcile_live_trading(live_trading)
            account_positions, _position_errors = live_account_positions()
            live_trading.save_account_snapshot(
                live_trading.account_summary(live_markets_for_open_positions(live_trading), account_positions)
            )
            return
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        markets = client.get_markets_by_condition_ids([str(position["condition_id"]) for position in open_positions])
        paper_trading.mark_positions(open_positions, markets, save_snapshots=True)
        paper_trading.get_marked_account(markets, save_snapshot=True)
        live_trading = build_live_trading()
        reconcile_live_trading(live_trading)
        account_positions, _position_errors = live_account_positions()
        live_trading.save_account_snapshot(
            live_trading.account_summary(live_markets_for_open_positions(live_trading), account_positions)
        )

    def reconcile_paper_trading(client: PolymarketClient | None = None) -> dict[str, Any]:
        paper_trading = build_paper_trading()
        client = client or PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        condition_ids = paper_trading.list_open_condition_ids()
        markets = client.get_markets_by_condition_ids(condition_ids)
        settlement_result = paper_trading.reconcile_settled_positions(markets)

        closed_positions = []
        for wallet in build_watchlist().list_saved_wallet_addresses():
            closed_positions.extend(client.get_user_closed_positions(user=wallet, limit=100))
        copytrade_result = paper_trading.reconcile_closed_copy_positions(closed_positions)

        return {
            "settlement": settlement_result,
            "copytradeClosedPositions": copytrade_result,
            "settledPositions": settlement_result["settledPositions"] + copytrade_result["closedCopyPositions"],
            "skippedPositions": settlement_result["skippedPositions"] + copytrade_result["skippedCopyPositions"],
            "realizedPnl": settlement_result["realizedPnl"] + copytrade_result["realizedPnl"],
            "checkedMarkets": settlement_result["checkedMarkets"],
            "closedPositionSignals": copytrade_result["closedPositionSignals"],
            "reconciledAt": datetime.now(UTC).isoformat(),
        }

    def start_watchlist_monitor() -> None:
        global _watchlist_monitor_started
        with _watchlist_monitor_lock:
            if _watchlist_monitor_started:
                return
            _watchlist_monitor_started = True
            _watchlist_monitor_state["running"] = True

        def monitor_loop() -> None:
            while True:
                try:
                    result = refresh_watchlist_trades(trades_per_wallet=20)
                    reconcile_paper_trading()
                    record_open_position_marks()
                    _watchlist_monitor_state.update(
                        {
                            "running": True,
                            "lastRunAt": datetime.now(UTC).isoformat(),
                            "lastResult": result,
                            "lastError": None,
                        }
                    )
                except Exception as error:  # pragma: no cover - defensive background loop
                    LOGGER.exception("Watchlist monitor refresh failed")
                    _watchlist_monitor_state.update(
                        {
                            "running": True,
                            "lastRunAt": datetime.now(UTC).isoformat(),
                            "lastError": str(error),
                        }
                    )
                time.sleep(WATCHLIST_MONITOR_INTERVAL_SECONDS)

        thread = threading.Thread(target=monitor_loop, name="watchlist-monitor", daemon=True)
        thread.start()

    start_watchlist_monitor()

    @app.get("/")
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.get("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(STATIC_DIR / "assets", filename)

    @app.get("/api/config")
    def config():
        return jsonify(
            {
                "scanLimit": settings.scan_limit,
                "minProfitBps": settings.min_profit_bps,
                "requestTimeoutSeconds": settings.request_timeout_seconds,
                "mode": "read-only scanner",
                "traderCategories": [
                    "OVERALL",
                    "POLITICS",
                    "SPORTS",
                    "CRYPTO",
                    "CULTURE",
                    "MENTIONS",
                    "WEATHER",
                    "ECONOMICS",
                    "TECH",
                    "FINANCE",
                ],
                "traderTimePeriods": ["DAY", "WEEK", "MONTH", "ALL"],
            }
        )

    @app.get("/api/account/status")
    def account_status():
        account_settings = load_settings()
        account_address = account_settings.polymarket_account_address
        live_settings_payload = build_live_trading().get_settings()
        api_creds_configured = all(
            [
                account_settings.polymarket_api_key,
                account_settings.polymarket_api_secret,
                account_settings.polymarket_api_passphrase,
            ]
        )
        payload: dict[str, Any] = {
            "connectionMode": "READ_ONLY",
            "liveTradingEnabled": bool(live_settings_payload.get("enabled")),
            "tradingBlockedReason": (
                "Live trading is armed."
                if live_settings_payload.get("enabled")
                else "Kill switch is ON. Live trading is stopped."
            ),
            "accountConfigured": bool(account_address),
            "accountAddress": account_address,
            "funderConfigured": bool(account_settings.polymarket_funder_address),
            "funderAddress": account_settings.polymarket_funder_address,
            "signatureType": account_settings.polymarket_signature_type,
            "apiCredentialsConfigured": api_creds_configured,
            "privateKeyConfigured": bool(account_settings.polymarket_private_key),
            "authenticatedConfigured": bool(account_settings.polymarket_private_key and api_creds_configured),
            "authenticatedConnected": False,
            "signerAddress": "",
            "balanceAllowance": None,
            "openOrders": [],
            "authenticatedTrades": [],
            "collateralBalanceUsdc": None,
            "collateralAllowanceUsdc": None,
            "openPositionCount": 0,
            "recentTradeCount": 0,
            "closedPositionCount": 0,
            "positions": [],
            "recentTrades": [],
            "closedPositions": [],
            "errors": [],
        }
        if not account_address:
            return jsonify(payload)

        account_client = PolymarketAccountClient(
            AccountClientConfig(
                clob_base_url=account_settings.clob_base_url,
                private_key=account_settings.polymarket_private_key,
                api_key=account_settings.polymarket_api_key,
                api_secret=account_settings.polymarket_api_secret,
                api_passphrase=account_settings.polymarket_api_passphrase,
                signature_type=account_settings.polymarket_signature_type,
                funder_address=account_settings.polymarket_funder_address,
            )
        )
        authenticated_snapshot = account_client.get_authenticated_snapshot()
        payload.update(
            {
                "authenticatedConfigured": authenticated_snapshot["authenticatedConfigured"],
                "authenticatedConnected": authenticated_snapshot["authenticatedConnected"],
                "signerAddress": authenticated_snapshot["signerAddress"],
                "balanceAllowance": authenticated_snapshot["balanceAllowance"],
                "collateralBalanceUsdc": clob_collateral_amount(
                    (authenticated_snapshot["balanceAllowance"] or {}).get("balance")
                    if isinstance(authenticated_snapshot["balanceAllowance"], dict)
                    else None
                ),
                "collateralAllowanceUsdc": clob_collateral_allowance(
                    (
                        (authenticated_snapshot["balanceAllowance"] or {}).get("allowance")
                        or (authenticated_snapshot["balanceAllowance"] or {}).get("allowances")
                    )
                    if isinstance(authenticated_snapshot["balanceAllowance"], dict)
                    else None
                ),
                "openOrders": authenticated_snapshot["openOrders"],
                "authenticatedTrades": authenticated_snapshot["authenticatedTrades"],
            }
        )
        payload["errors"].extend(authenticated_snapshot["errors"])

        client = PolymarketClient(
            gamma_base_url=account_settings.gamma_base_url,
            clob_base_url=account_settings.clob_base_url,
            data_base_url=account_settings.data_base_url,
            timeout_seconds=account_settings.request_timeout_seconds,
        )
        public_users = []
        for user in [account_settings.polymarket_funder_address, account_address]:
            clean = str(user or "").strip()
            if clean and clean.lower() not in {item.lower() for item in public_users}:
                public_users.append(clean)
        try:
            positions = []
            for user in public_users:
                positions.extend(client.get_user_positions_raw(user, limit=100))
            payload["positions"] = positions[:50]
            payload["openPositionCount"] = len(positions)
        except Exception as error:  # pragma: no cover - external API
            LOGGER.exception("Could not load account positions")
            payload["errors"].append(f"positions: {error}")
        try:
            trades = []
            for user in public_users:
                trades.extend(client.get_user_trade_activity(user, limit=50))
            trades.sort(key=lambda item: item.timestamp, reverse=True)
            payload["recentTrades"] = decimal_to_json([asdict(item) for item in trades])
            payload["recentTradeCount"] = len(trades)
        except Exception as error:  # pragma: no cover - external API
            LOGGER.exception("Could not load account trades")
            payload["errors"].append(f"trades: {error}")
        try:
            closed_positions = []
            for user in public_users:
                closed_positions.extend(client.get_user_closed_positions(user, limit=100))
            closed_positions.sort(key=lambda item: item.timestamp, reverse=True)
            payload["closedPositions"] = decimal_to_json([asdict(item) for item in closed_positions])
            payload["closedPositionCount"] = len(closed_positions)
        except Exception as error:  # pragma: no cover - external API
            LOGGER.exception("Could not load account closed positions")
            payload["errors"].append(f"closed positions: {error}")
        return jsonify(payload)

    @app.get("/api/account/connection")
    def account_connection():
        return jsonify(account_connection_payload(load_settings()))

    @app.post("/api/account/connection")
    def set_account_connection():
        payload = request.get_json(force=True, silent=True) or {}
        return jsonify(save_account_connection(payload))

    @app.post("/api/account/derive-credentials")
    def derive_account_credentials():
        payload = request.get_json(force=True, silent=True) or {}
        save_account_connection(payload)
        account_settings = load_settings()
        if not account_settings.polymarket_private_key:
            return jsonify({"error": "Private key is required to derive CLOB API credentials."}), 400

        try:
            from py_clob_client_v2.client import ClobClient
            from py_clob_client_v2.constants import POLYGON
        except Exception as error:  # pragma: no cover - optional dependency guard
            return jsonify({"error": f"py-clob-client-v2 unavailable: {error}"}), 500

        try:
            client = ClobClient(
                host=account_settings.clob_base_url,
                chain_id=POLYGON,
                key=account_settings.polymarket_private_key,
            )
            creds = client.create_or_derive_api_key()
        except Exception as error:  # pragma: no cover - external API/auth
            LOGGER.exception("Could not derive Polymarket API credentials")
            return jsonify({"error": f"Could not derive API credentials: {error}"}), 400

        connection = save_account_connection(
            {
                "apiKey": creds.api_key,
                "apiSecret": creds.api_secret,
                "apiPassphrase": creds.api_passphrase,
            }
        )
        connection["derived"] = True
        return jsonify(connection)

    @app.get("/api/scan")
    def scan():
        limit = int(request.args.get("limit", settings.scan_limit))
        max_markets_raw = request.args.get("maxMarkets")
        max_markets = int(max_markets_raw) if max_markets_raw else None
        min_profit_bps = Decimal(request.args.get("minProfitBps", str(settings.min_profit_bps)))

        limit = max(1, min(limit, 500))
        if max_markets is not None:
            max_markets = max(1, min(max_markets, limit))

        started_at = datetime.now(UTC)
        opportunities = build_scanner().scan_binary_markets(
            limit=limit,
            max_markets=max_markets,
            min_profit_bps=min_profit_bps,
        )
        finished_at = datetime.now(UTC)

        opportunity_payload = [decimal_to_json(asdict(item)) for item in opportunities]
        return jsonify(
            {
                "startedAt": started_at.isoformat(),
                "finishedAt": finished_at.isoformat(),
                "durationSeconds": round((finished_at - started_at).total_seconds(), 3),
                "requestedMarketLimit": limit,
                "scannedMarketCap": max_markets,
                "minProfitBps": float(min_profit_bps),
                "opportunityCount": len(opportunity_payload),
                "opportunities": opportunity_payload,
            }
        )

    @app.get("/api/traders")
    def traders():
        category = request.args.get("category", "OVERALL").upper()
        time_period = request.args.get("timePeriod", "DAY").upper()
        order_by = request.args.get("orderBy", "PNL").upper()
        limit = max(1, min(int(request.args.get("limit", 10)), 50))
        trades_per_trader = max(0, min(int(request.args.get("tradesPerTrader", 5)), 25))
        closed_positions_per_trader = max(1, min(int(request.args.get("closedPositionsPerTrader", 50)), 50))
        min_closed_positions = max(0, min(int(request.args.get("minClosedPositions", 10)), 50))
        min_win_rate = Decimal(request.args.get("minWinRate", "0"))
        min_recent_trades = max(0, min(int(request.args.get("minRecentTrades", 0)), 25))
        rank_by_consistency = request.args.get("rankBy", "").upper() == "CONSISTENCY"

        started_at = datetime.now(UTC)
        trader_profiles = build_trader_tracker().get_top_traders_with_recent_trades(
            category=category,
            time_period=time_period,
            order_by=order_by,
            limit=limit,
            trades_per_trader=trades_per_trader,
            closed_positions_per_trader=closed_positions_per_trader,
            min_closed_positions=min_closed_positions,
            min_win_rate=min_win_rate,
            min_recent_trades=min_recent_trades,
            rank_by_consistency=rank_by_consistency,
        )
        finished_at = datetime.now(UTC)

        return jsonify(
            {
                "startedAt": started_at.isoformat(),
                "finishedAt": finished_at.isoformat(),
                "durationSeconds": round((finished_at - started_at).total_seconds(), 3),
                "category": category,
                "timePeriod": time_period,
                "orderBy": order_by,
                "traderCount": len(trader_profiles),
                "tradesPerTrader": trades_per_trader,
                "closedPositionsPerTrader": closed_positions_per_trader,
                "minClosedPositions": min_closed_positions,
                "minWinRate": float(min_win_rate),
                "minRecentTrades": min_recent_trades,
                "rankBy": "CONSISTENCY" if rank_by_consistency else order_by,
                "traders": [decimal_to_json(asdict(item)) for item in trader_profiles],
            }
        )

    @app.post("/api/smart-wallets/ingest")
    def ingest_smart_wallets():
        payload = request.get_json(silent=True) or {}
        category = str(payload.get("category", "OVERALL")).upper()
        time_period = str(payload.get("timePeriod", "MONTH")).upper()
        order_by = str(payload.get("orderBy", "PNL")).upper()
        candidate_limit = max(1, min(int(payload.get("candidateLimit", 25)), 50))
        trades_per_wallet = max(1, min(int(payload.get("tradesPerWallet", 25)), 100))
        closed_positions_per_wallet = max(1, min(int(payload.get("closedPositionsPerWallet", 50)), 100))
        markout_trades_per_wallet = max(0, min(int(payload.get("markoutTradesPerWallet", 5)), 20))

        result = build_smart_wallet_tracker().ingest_candidates(
            category=category,
            time_period=time_period,
            order_by=order_by,
            candidate_limit=candidate_limit,
            trades_per_wallet=trades_per_wallet,
            closed_positions_per_wallet=closed_positions_per_wallet,
            markout_trades_per_wallet=markout_trades_per_wallet,
        )
        return jsonify(result)

    @app.get("/api/smart-wallets")
    def smart_wallets():
        category = request.args.get("category", "").upper() or None
        time_period = request.args.get("timePeriod", "").upper() or None
        limit = max(1, min(int(request.args.get("limit", 25)), 100))
        min_trades = max(0, min(int(request.args.get("minTrades", 10)), 500))
        min_closed_positions = max(0, min(int(request.args.get("minClosedPositions", 10)), 500))
        min_win_rate = Decimal(request.args.get("minWinRate", "0.55"))
        min_average_markout = Decimal(request.args.get("minAverageMarkout", "-1"))

        started_at = datetime.now(UTC)
        wallets = build_smart_wallet_tracker().get_ranked_wallets(
            limit=limit,
            min_trades=min_trades,
            min_closed_positions=min_closed_positions,
            min_win_rate=min_win_rate,
            min_average_markout=min_average_markout,
            category=category,
            time_period=time_period,
        )
        finished_at = datetime.now(UTC)

        return jsonify(
            {
                "startedAt": started_at.isoformat(),
                "finishedAt": finished_at.isoformat(),
                "durationSeconds": round((finished_at - started_at).total_seconds(), 3),
                "category": category,
                "timePeriod": time_period,
                "walletCount": len(wallets),
                "wallets": [decimal_to_json(asdict(item)) for item in wallets],
            }
        )

    @app.get("/api/watchlist")
    def watchlist():
        saved_wallets = build_watchlist().list_wallets(build_smart_wallet_tracker())
        return jsonify({"walletCount": len(saved_wallets), "wallets": decimal_to_json(saved_wallets)})

    @app.post("/api/watchlist")
    def save_watchlist_wallet():
        payload = request.get_json(silent=True) or {}
        proxy_wallet = str(payload.get("proxyWallet") or payload.get("proxy_wallet") or "").strip()
        if not proxy_wallet:
            return jsonify({"error": "proxyWallet is required"}), 400

        result = build_watchlist().save_wallet(
            proxy_wallet=proxy_wallet,
            label=str(payload.get("label") or ""),
            notes=str(payload.get("notes") or ""),
            username=str(payload.get("username") or ""),
            x_username=str(payload.get("xUsername") or payload.get("x_username") or ""),
            profile_image=str(payload.get("profileImage") or payload.get("profile_image") or ""),
            verified_badge=bool(payload.get("verifiedBadge") or payload.get("verified_badge") or False),
        )
        return jsonify(result)

    @app.delete("/api/watchlist/<proxy_wallet>")
    def remove_watchlist_wallet(proxy_wallet: str):
        return jsonify(build_watchlist().remove_wallet(proxy_wallet))

    @app.post("/api/watchlist/<proxy_wallet>/alerts")
    def set_watchlist_alerts(proxy_wallet: str):
        payload = request.get_json(silent=True) or {}
        enabled = bool(payload.get("enabled"))
        return jsonify(build_watchlist().set_alerts_enabled(proxy_wallet, enabled))

    @app.post("/api/watchlist/refresh")
    def refresh_watchlist():
        payload = request.get_json(silent=True) or {}
        trades_per_wallet = max(1, min(int(payload.get("tradesPerWallet", 20)), 100))
        return jsonify(refresh_watchlist_trades(trades_per_wallet=trades_per_wallet))

    @app.get("/api/watchlist/monitor")
    def watchlist_monitor():
        return jsonify(_watchlist_monitor_state)

    @app.get("/api/watchlist/alerts")
    def watchlist_alerts():
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
        alerts = build_watchlist().list_alerts(limit=limit)
        return jsonify({"alertCount": len(alerts), "alerts": alerts})

    @app.post("/api/alerts/arbitrage/check")
    def check_arbitrage_alerts():
        payload = request.get_json(silent=True) or {}
        limit = max(1, min(int(payload.get("limit", settings.scan_limit)), 500))
        max_markets_raw = payload.get("maxMarkets")
        max_markets = int(max_markets_raw) if max_markets_raw else None
        min_profit_bps = Decimal(str(payload.get("minProfitBps", settings.min_profit_bps)))

        opportunities = build_scanner().scan_binary_markets(
            limit=limit,
            max_markets=max_markets,
            min_profit_bps=min_profit_bps,
        )
        new_alerts = build_alert_store().save_arbitrage_opportunities(opportunities)
        paper_trading = build_paper_trading()
        paper_orders = [
            order
            for opportunity in opportunities
            if (order := paper_trading.maybe_create_arbitrage_order(opportunity)) is not None
        ]
        return jsonify(
            {
                "checkedAt": datetime.now(UTC).isoformat(),
                "opportunityCount": len(opportunities),
                "newAlertCount": len(new_alerts),
                "newAlerts": new_alerts,
                "paperOrdersCreated": len(paper_orders),
                "paperOrders": paper_orders,
            }
        )

    @app.get("/api/alerts/arbitrage")
    def arbitrage_alerts():
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
        alerts = build_alert_store().list_arbitrage_alerts(limit=limit)
        return jsonify({"alertCount": len(alerts), "alerts": alerts})

    @app.post("/api/paper/copytrade/<proxy_wallet>")
    def set_copytrade(proxy_wallet: str):
        payload = request.get_json(silent=True) or {}
        result = build_paper_trading().set_copytrade_settings(
            proxy_wallet=proxy_wallet,
            enabled=bool(payload.get("enabled")),
            sizing_mode=str(payload.get("sizingMode") or payload.get("sizing_mode") or "PERCENT"),
            size_value=Decimal(str(payload.get("sizeValue") or payload.get("size_value") or "10")),
            max_usdc=Decimal(str(payload.get("maxUsdc") or payload.get("max_usdc") or "100")),
        )
        return jsonify(result)

    @app.get("/api/paper/copytrade")
    def copytrade_settings():
        return jsonify({"settings": decimal_to_json(build_paper_trading().get_copytrade_settings())})

    @app.get("/api/live/settings")
    def live_settings():
        live_trading = build_live_trading()
        reconciliation = reconcile_live_trading(live_trading)
        account_positions, position_errors = live_account_positions()
        account = live_trading.account_summary(live_markets_for_open_positions(live_trading), account_positions)
        if position_errors:
            reconciliation["errors"] = list(reconciliation.get("errors", [])) + position_errors
        live_trading.save_account_snapshot(account)
        return jsonify({"settings": live_trading.get_settings(), "account": account, "reconciliation": reconciliation})

    @app.get("/api/live/copytraders")
    def live_copytraders():
        wallets = build_watchlist().list_wallets_basic()
        copy_settings = build_live_trading().get_copytrade_settings()
        rows = []
        for wallet in wallets:
            setting = copy_settings.get(str(wallet["proxy_wallet"]).lower(), {})
            rows.append(
                {
                    **wallet,
                    "copytrade": decimal_to_json(setting),
                }
            )
        return jsonify({"copytraders": rows})

    @app.post("/api/live/copytrade/<proxy_wallet>")
    def set_live_copytrade(proxy_wallet: str):
        payload = request.get_json(silent=True) or {}
        result = build_live_trading().set_copytrade_settings(
            proxy_wallet=proxy_wallet,
            enabled=bool(payload.get("enabled")),
            sizing_mode=str(payload.get("sizingMode") or payload.get("sizing_mode") or "PERCENT"),
            size_value=Decimal(str(payload.get("sizeValue") or payload.get("size_value") or "10")),
            max_usdc=Decimal(str(payload.get("maxUsdc") or payload.get("max_usdc") or "100")),
        )
        return jsonify(result)

    @app.post("/api/live/settings")
    def set_live_settings():
        payload = request.get_json(force=True, silent=True) or {}
        live_trading = build_live_trading()
        try:
            if "enabled" in payload:
                settings_payload = live_trading.set_enabled(bool(payload.get("enabled", False)))
            else:
                settings_payload = live_trading.set_execution_settings(
                    entry_slippage_bps=Decimal(str(payload.get("entrySlippageBps", "25"))),
                    exit_slippage_bps=Decimal(str(payload.get("exitSlippageBps", "25"))),
                max_chase_bps=Decimal(str(payload.get("maxChaseBps", "100"))),
                copytrade_capital_mode=str(payload.get("copytradeCapitalMode", "CONSERVATIVE")),
                min_cash_reserve_usdc=Decimal(str(payload.get("minCashReserveUsdc", "0"))),
                min_trade_usdc=Decimal(str(payload.get("minTradeUsdc", "1"))),
            )
            account_positions, _position_errors = live_account_positions()
            account = live_trading.account_summary(live_markets_for_open_positions(live_trading), account_positions)
            return jsonify({"settings": settings_payload, "account": account})
        except Exception as error:
            LOGGER.exception("Could not update live settings")
            return jsonify({"error": str(error)}), 400

    @app.post("/api/live/kill-switch")
    def live_kill_switch():
        live_trading = build_live_trading()
        settings_payload = live_trading.emergency_stop()
        account_positions, _position_errors = live_account_positions()
        return jsonify(
            {
                "settings": settings_payload,
                "account": live_trading.account_summary(live_markets_for_open_positions(live_trading), account_positions),
            }
        )

    @app.get("/api/live/orders")
    def live_orders():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        return jsonify({"orders": build_live_trading().list_orders(limit=limit)})

    @app.get("/api/live/linked-closed-positions")
    def live_linked_closed_positions():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        closed_positions = []
        errors = []
        for user in live_account_user_ids():
            try:
                closed_positions.extend(client.get_user_closed_positions(user, limit=limit))
            except Exception as error:  # pragma: no cover - external API
                LOGGER.exception("Could not load linked closed positions")
                errors.append(f"closed positions {user[:6]}...: {error}")
        closed_positions.sort(key=lambda item: item.timestamp, reverse=True)
        return jsonify(
            {
                "positions": decimal_to_json([asdict(item) for item in closed_positions[:limit]]),
                "positionCount": len(closed_positions),
                "realizedPnl": float(sum((item.realized_pnl for item in closed_positions), Decimal("0"))),
                "errors": errors,
            }
        )

    @app.get("/api/live/account/history")
    def live_account_history():
        limit = max(1, min(int(request.args.get("limit", 500)), 5000))
        return jsonify({"snapshots": build_live_trading().list_account_snapshots(limit=limit)})

    @app.get("/api/live/positions")
    def live_positions():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        status = request.args.get("status")
        live_trading = build_live_trading()
        reconciliation = reconcile_live_trading(live_trading)
        positions = live_trading.list_positions(status=status, limit=limit)
        account_positions, position_errors = live_account_positions()
        if position_errors:
            reconciliation["errors"] = list(reconciliation.get("errors", [])) + position_errors
        markets = live_markets_for_open_positions(live_trading) if str(status or "").upper() == "OPEN" else {}
        if markets:
            positions = live_trading.mark_positions(positions, markets, account_positions)
        return jsonify({"positions": positions, "reconciliation": reconciliation})

    @app.get("/api/paper/orders")
    def paper_orders():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        orders = build_paper_trading().list_orders(limit=limit)
        return jsonify({"orderCount": len(orders), "orders": orders})

    @app.get("/api/paper/account")
    def paper_account():
        paper_trading = build_paper_trading()
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        markets = client.get_markets_by_condition_ids(paper_trading.list_open_condition_ids())
        return jsonify(paper_trading.get_marked_account(markets, save_snapshot=True))

    @app.get("/api/paper/account/history")
    def paper_account_history():
        limit = max(1, min(int(request.args.get("limit", 500)), 5000))
        snapshots = build_paper_trading().list_account_snapshots(limit=limit)
        return jsonify({"snapshotCount": len(snapshots), "snapshots": snapshots})

    @app.get("/api/paper/execution-settings")
    def paper_execution_settings():
        return jsonify(build_paper_trading().get_execution_settings())

    @app.post("/api/paper/execution-settings")
    def set_paper_execution_settings():
        payload = request.get_json(silent=True) or {}
        try:
            with _watchlist_refresh_lock:
                paper_trading = build_paper_trading()
                settings_payload = paper_trading.set_execution_settings(
                    entry_slippage_bps=Decimal(str(payload.get("entrySlippageBps", "25"))),
                    exit_slippage_bps=Decimal(str(payload.get("exitSlippageBps", "25"))),
                    fee_bps=Decimal(str(payload.get("feeBps", "0"))),
                    max_chase_bps=Decimal(str(payload.get("maxChaseBps", "100"))),
                    copytrade_capital_mode=str(payload.get("copytradeCapitalMode", "CONSERVATIVE")),
                    min_cash_reserve_usdc=Decimal(str(payload.get("minCashReserveUsdc", "0"))),
                )
                client = PolymarketClient(
                    gamma_base_url=settings.gamma_base_url,
                    clob_base_url=settings.clob_base_url,
                    data_base_url=settings.data_base_url,
                    timeout_seconds=settings.request_timeout_seconds,
                )
                try:
                    markets = client.get_markets_by_condition_ids(paper_trading.list_open_condition_ids())
                except Exception:  # pragma: no cover - reserve enforcement can fall back to entry prices
                    LOGGER.exception("Could not fetch markets for cash reserve enforcement")
                    markets = {}
                reserve_result = paper_trading.enforce_cash_reserve(markets)
            settings_payload["cashReserveEnforcement"] = reserve_result
            return jsonify(settings_payload)
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/account/balance")
    def set_paper_balance():
        payload = request.get_json(silent=True) or {}
        try:
            balance = Decimal(str(payload.get("balance", "1000")))
            return jsonify(build_paper_trading().set_balance(balance))
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/reset")
    def reset_paper_account():
        with _watchlist_refresh_lock:
            return jsonify(build_paper_trading().reset_account())

    @app.get("/api/paper/positions")
    def paper_positions():
        status = request.args.get("status", "OPEN").upper()
        max_limit = 5000 if status == "CLOSED" else 500
        limit = max(1, min(int(request.args.get("limit", 100)), max_limit))
        paper_trading = build_paper_trading()
        positions = paper_trading.list_positions(status=status, limit=limit)
        if status == "OPEN":
            client = PolymarketClient(
                gamma_base_url=settings.gamma_base_url,
                clob_base_url=settings.clob_base_url,
                data_base_url=settings.data_base_url,
                timeout_seconds=settings.request_timeout_seconds,
            )
            markets = client.get_markets_by_condition_ids([str(position["condition_id"]) for position in positions])
            positions = paper_trading.mark_positions(positions, markets, save_snapshots=True)
            positions = paper_trading.attach_mark_history(positions)
        else:
            positions = paper_trading.attach_mark_history(positions)
        return jsonify({"positionCount": len(positions), "positions": positions})

    @app.get("/api/paper/events")
    def paper_events():
        limit = max(1, min(int(request.args.get("limit", 50)), 500))
        events = build_paper_trading().list_paper_events(limit=limit)
        return jsonify({"eventCount": len(events), "events": events})

    @app.post("/api/paper/positions/<int:position_id>/close")
    def close_paper_position(position_id: int):
        payload = request.get_json(silent=True) or {}
        try:
            exit_price = Decimal(str(payload.get("exitPrice", "1")))
            reason = str(payload.get("reason", "Manual close"))
            return jsonify(build_paper_trading().close_position(position_id, exit_price, reason))
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/reconcile")
    def reconcile_paper_positions():
        return jsonify(reconcile_paper_trading())

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
