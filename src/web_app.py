from __future__ import annotations

import atexit
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import logging
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from src.background import WatchlistMonitor
from src.config import account_connection_payload
from src.config import load_settings
from src.config import save_account_connection
from src.serialization import decimal_to_json
from src.services import RuntimeServices
from src.storage import connect_database


STATIC_DIR = Path(__file__).resolve().parent.parent / "web"

LOGGER = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    settings = load_settings()
    services = RuntimeServices(settings)
    background_monitor = WatchlistMonitor(
        services=services,
        interval_seconds=settings.watchlist_monitor_interval_seconds,
    )
    app.extensions["runtime_services"] = services
    app.extensions["watchlist_monitor"] = background_monitor
    if settings.enable_background_monitor:
        background_monitor.start()
        atexit.register(background_monitor.stop)
    else:
        background_monitor.disable()

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
                "appHost": settings.app_host,
                "appPort": settings.app_port,
                "watchlistMonitorIntervalSeconds": settings.watchlist_monitor_interval_seconds,
                "liveRefreshIntervalSeconds": settings.live_refresh_interval_seconds,
                "backgroundMonitorEnabled": settings.enable_background_monitor,
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

    @app.get("/api/health")
    def health():
        database_status = "ok"
        try:
            with connect_database(settings.database_path) as connection:
                connection.execute("SELECT 1").fetchone()
        except Exception as error:  # pragma: no cover - defensive service health
            LOGGER.exception("Database healthcheck failed")
            database_status = f"error: {error}"

        monitor_status = background_monitor.status()
        ok = database_status == "ok" and (
            not settings.enable_background_monitor or bool(monitor_status.get("running"))
        )
        return jsonify(
            {
                "ok": ok,
                "database": database_status,
                "backgroundMonitor": monitor_status,
                "appHost": settings.app_host,
                "appPort": settings.app_port,
            }
        ), 200 if ok else 503

    @app.get("/api/account/status")
    def account_status():
        return jsonify(services.account_status())

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
        opportunities = services.build_scanner().scan_binary_markets(
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
        trader_profiles = services.build_trader_tracker().get_top_traders_with_recent_trades(
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

        result = services.build_smart_wallet_tracker().ingest_candidates(
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
        wallets = services.build_smart_wallet_tracker().get_ranked_wallets(
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
        saved_wallets = services.build_watchlist().list_wallets(services.build_smart_wallet_tracker())
        return jsonify({"walletCount": len(saved_wallets), "wallets": decimal_to_json(saved_wallets)})

    @app.post("/api/watchlist")
    def save_watchlist_wallet():
        payload = request.get_json(silent=True) or {}
        proxy_wallet = str(payload.get("proxyWallet") or payload.get("proxy_wallet") or "").strip()
        if not proxy_wallet:
            return jsonify({"error": "proxyWallet is required"}), 400

        result = services.build_watchlist().save_wallet(
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
        return jsonify(services.build_watchlist().remove_wallet(proxy_wallet))

    @app.post("/api/watchlist/<proxy_wallet>/alerts")
    def set_watchlist_alerts(proxy_wallet: str):
        payload = request.get_json(silent=True) or {}
        enabled = bool(payload.get("enabled"))
        return jsonify(services.build_watchlist().set_alerts_enabled(proxy_wallet, enabled))

    @app.post("/api/watchlist/refresh")
    def refresh_watchlist():
        payload = request.get_json(silent=True) or {}
        trades_per_wallet = max(1, min(int(payload.get("tradesPerWallet", 20)), 100))
        return jsonify(services.refresh_watchlist_trades(trades_per_wallet=trades_per_wallet))

    @app.get("/api/watchlist/monitor")
    def watchlist_monitor():
        return jsonify(background_monitor.status())

    @app.get("/api/watchlist/alerts")
    def watchlist_alerts():
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
        alerts = services.build_watchlist().list_alerts(limit=limit)
        return jsonify({"alertCount": len(alerts), "alerts": alerts})

    @app.post("/api/alerts/arbitrage/check")
    def check_arbitrage_alerts():
        payload = request.get_json(silent=True) or {}
        limit = max(1, min(int(payload.get("limit", settings.scan_limit)), 500))
        max_markets_raw = payload.get("maxMarkets")
        max_markets = int(max_markets_raw) if max_markets_raw else None
        min_profit_bps = Decimal(str(payload.get("minProfitBps", settings.min_profit_bps)))

        opportunities = services.build_scanner().scan_binary_markets(
            limit=limit,
            max_markets=max_markets,
            min_profit_bps=min_profit_bps,
        )
        new_alerts = services.build_alert_store().save_arbitrage_opportunities(opportunities)
        paper_trading = services.build_paper_trading()
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
        alerts = services.build_alert_store().list_arbitrage_alerts(limit=limit)
        return jsonify({"alertCount": len(alerts), "alerts": alerts})

    @app.post("/api/paper/copytrade/<proxy_wallet>")
    def set_copytrade(proxy_wallet: str):
        payload = request.get_json(silent=True) or {}
        result = services.build_paper_trading().set_copytrade_settings(
            proxy_wallet=proxy_wallet,
            enabled=bool(payload.get("enabled")),
            sizing_mode=str(payload.get("sizingMode") or payload.get("sizing_mode") or "PERCENT"),
            size_value=Decimal(str(payload.get("sizeValue") or payload.get("size_value") or "10")),
            max_usdc=Decimal(str(payload.get("maxUsdc") or payload.get("max_usdc") or "100")),
        )
        return jsonify(result)

    @app.get("/api/paper/copytrade")
    def copytrade_settings():
        return jsonify({"settings": decimal_to_json(services.build_paper_trading().get_copytrade_settings())})

    @app.get("/api/live/settings")
    def live_settings():
        return jsonify(services.live_settings_payload())

    @app.get("/api/live/copytraders")
    def live_copytraders():
        wallets = services.build_watchlist().list_wallets_basic()
        copy_settings = services.build_live_trading().get_copytrade_settings()
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
        result = services.build_live_trading().set_copytrade_settings(
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
        try:
            return jsonify(services.update_live_settings(payload))
        except Exception as error:
            LOGGER.exception("Could not update live settings")
            return jsonify({"error": str(error)}), 400

    @app.post("/api/live/kill-switch")
    def live_kill_switch():
        return jsonify(services.live_kill_switch_payload())

    @app.get("/api/live/orders")
    def live_orders():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        return jsonify({"orders": services.build_live_trading().list_orders(limit=limit)})

    @app.get("/api/live/linked-closed-positions")
    def live_linked_closed_positions():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        return jsonify(services.live_linked_closed_positions_payload(limit))

    @app.get("/api/live/account/history")
    def live_account_history():
        limit = max(1, min(int(request.args.get("limit", 500)), 5000))
        return jsonify({"snapshots": services.build_live_trading().list_account_snapshots(limit=limit)})

    @app.get("/api/live/positions")
    def live_positions():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        status = request.args.get("status")
        return jsonify(services.live_positions_payload(status=status, limit=limit))

    @app.get("/api/paper/orders")
    def paper_orders():
        limit = max(1, min(int(request.args.get("limit", 100)), 500))
        orders = services.build_paper_trading().list_orders(limit=limit)
        return jsonify({"orderCount": len(orders), "orders": orders})

    @app.get("/api/paper/account")
    def paper_account():
        return jsonify(services.paper_account_payload())

    @app.get("/api/paper/account/history")
    def paper_account_history():
        limit = max(1, min(int(request.args.get("limit", 500)), 5000))
        snapshots = services.build_paper_trading().list_account_snapshots(limit=limit)
        return jsonify({"snapshotCount": len(snapshots), "snapshots": snapshots})

    @app.get("/api/paper/execution-settings")
    def paper_execution_settings():
        return jsonify(services.build_paper_trading().get_execution_settings())

    @app.post("/api/paper/execution-settings")
    def set_paper_execution_settings():
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify(services.update_paper_execution_settings(payload))
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/account/balance")
    def set_paper_balance():
        payload = request.get_json(silent=True) or {}
        try:
            balance = Decimal(str(payload.get("balance", "1000")))
            return jsonify(services.build_paper_trading().set_balance(balance))
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/reset")
    def reset_paper_account():
        with services.watchlist_refresh_lock:
            return jsonify(services.build_paper_trading().reset_account())

    @app.get("/api/paper/positions")
    def paper_positions():
        status = request.args.get("status", "OPEN").upper()
        max_limit = 5000 if status == "CLOSED" else 500
        limit = max(1, min(int(request.args.get("limit", 100)), max_limit))
        return jsonify(services.paper_positions_payload(status=status, limit=limit))

    @app.get("/api/paper/events")
    def paper_events():
        limit = max(1, min(int(request.args.get("limit", 50)), 500))
        events = services.build_paper_trading().list_paper_events(limit=limit)
        return jsonify({"eventCount": len(events), "events": events})

    @app.post("/api/paper/positions/<int:position_id>/close")
    def close_paper_position(position_id: int):
        payload = request.get_json(silent=True) or {}
        try:
            exit_price = Decimal(str(payload.get("exitPrice", "1")))
            reason = str(payload.get("reason", "Manual close"))
            return jsonify(services.build_paper_trading().close_position(position_id, exit_price, reason))
        except (InvalidOperation, ValueError) as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/paper/reconcile")
    def reconcile_paper_positions():
        return jsonify(services.reconcile_paper_trading())

    return app


app = create_app()


if __name__ == "__main__":
    run_settings = load_settings()
    app.run(host=run_settings.app_host, port=run_settings.app_port, debug=False)
