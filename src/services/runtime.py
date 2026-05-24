from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
import logging
import threading
from typing import Any

from src.alert_store import AlertStore
from src.config import Settings
from src.config import load_settings
from src.live_trading import LiveTrading
from src.paper_trading import PaperTrading
from src.polymarket_account_client import AccountClientConfig
from src.polymarket_account_client import PolymarketAccountClient
from src.polymarket_client import PolymarketClient
from src.scanner import ArbitrageScanner
from src.serialization import decimal_to_json
from src.smart_wallet_tracker import SmartWalletTracker
from src.trader_tracker import TraderTracker
from src.watchlist import Watchlist


LOGGER = logging.getLogger(__name__)


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


class RuntimeServices:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.watchlist_refresh_lock = threading.Lock()
        self.live_reconcile_lock = threading.Lock()

    def build_client(self, settings: Settings | None = None) -> PolymarketClient:
        settings = settings or self.settings
        return PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            data_base_url=settings.data_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )

    def build_scanner(self) -> ArbitrageScanner:
        return ArbitrageScanner(self.build_client())

    def build_trader_tracker(self) -> TraderTracker:
        return TraderTracker(self.build_client())

    def build_smart_wallet_tracker(self) -> SmartWalletTracker:
        return SmartWalletTracker(client=self.build_client(), database_path=self.settings.database_path)

    def build_watchlist(self) -> Watchlist:
        return Watchlist(database_path=self.settings.database_path)

    def build_alert_store(self) -> AlertStore:
        return AlertStore(database_path=self.settings.database_path)

    def build_paper_trading(self) -> PaperTrading:
        return PaperTrading(database_path=self.settings.database_path)

    def build_live_trading(self) -> LiveTrading:
        return LiveTrading(database_path=self.settings.database_path)

    def account_status(self) -> dict[str, Any]:
        account_settings = load_settings()
        account_address = account_settings.polymarket_account_address
        live_settings_payload = self.build_live_trading().get_settings()
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
            return payload

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

        client = self.build_client(account_settings)
        public_users = self._public_account_user_ids(account_settings)
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
        return payload

    def live_markets_for_open_positions(self, live_trading: LiveTrading) -> dict[str, dict[str, Any]]:
        condition_ids = live_trading.list_open_condition_ids()
        if not condition_ids:
            return {}
        return self.build_client().get_markets_by_condition_ids(condition_ids)

    def live_account_user_ids(self) -> list[str]:
        account_settings = load_settings()
        return self._public_account_user_ids(account_settings)

    def live_account_positions(self) -> tuple[list[dict[str, Any]], list[str]]:
        client = self.build_client()
        positions = []
        errors = []
        for user in self.live_account_user_ids():
            try:
                positions.extend(client.get_user_positions_raw(user, limit=500))
            except Exception as error:  # pragma: no cover - external API
                LOGGER.exception("Could not load live account positions")
                errors.append(f"positions {user[:6]}...: {error}")
        return positions, errors

    def reconcile_live_trading(self, live_trading: LiveTrading | None = None) -> dict[str, Any]:
        with self.live_reconcile_lock:
            live_trading = live_trading or self.build_live_trading()
            client = self.build_client()
            account_positions = []
            account_trades = []
            account_closed_positions = []
            errors = []
            users = self.live_account_user_ids()
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
            markets = self.live_markets_for_open_positions(live_trading)
            result = live_trading.reconcile_account_positions(
                account_positions,
                account_trades,
                account_closed_positions,
                markets,
            )
            result["errors"] = errors
            result["checkedUsers"] = len(users)
            return result

    def refresh_watchlist_trades(self, trades_per_wallet: int = 20) -> dict[str, Any]:
        with self.watchlist_refresh_lock:
            return self.build_watchlist().refresh_saved_wallet_trades(
                client=self.build_client(),
                trades_per_wallet=trades_per_wallet,
                paper_trading=self.build_paper_trading(),
                live_trading=self.build_live_trading(),
            )

    def record_open_position_marks(self) -> None:
        paper_trading = self.build_paper_trading()
        open_positions = paper_trading.list_positions(status="OPEN", limit=5000)
        if not open_positions:
            live_trading = self.build_live_trading()
            self.reconcile_live_trading(live_trading)
            account_positions, _position_errors = self.live_account_positions()
            live_trading.save_account_snapshot(
                live_trading.account_summary(self.live_markets_for_open_positions(live_trading), account_positions)
            )
            return

        markets = self.build_client().get_markets_by_condition_ids(
            [str(position["condition_id"]) for position in open_positions]
        )
        paper_trading.mark_positions(open_positions, markets, save_snapshots=True)
        paper_trading.get_marked_account(markets, save_snapshot=True)

        live_trading = self.build_live_trading()
        self.reconcile_live_trading(live_trading)
        account_positions, _position_errors = self.live_account_positions()
        live_trading.save_account_snapshot(
            live_trading.account_summary(self.live_markets_for_open_positions(live_trading), account_positions)
        )

    def reconcile_paper_trading(self, client: PolymarketClient | None = None) -> dict[str, Any]:
        paper_trading = self.build_paper_trading()
        client = client or self.build_client()
        condition_ids = paper_trading.list_open_condition_ids()
        markets = client.get_markets_by_condition_ids(condition_ids)
        settlement_result = paper_trading.reconcile_settled_positions(markets)

        closed_positions = []
        for wallet in self.build_watchlist().list_saved_wallet_addresses():
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

    def live_settings_payload(self) -> dict[str, Any]:
        live_trading = self.build_live_trading()
        reconciliation = self.reconcile_live_trading(live_trading)
        account_positions, position_errors = self.live_account_positions()
        account = live_trading.account_summary(self.live_markets_for_open_positions(live_trading), account_positions)
        if position_errors:
            reconciliation["errors"] = list(reconciliation.get("errors", [])) + position_errors
        live_trading.save_account_snapshot(account)
        return {"settings": live_trading.get_settings(), "account": account, "reconciliation": reconciliation}

    def update_live_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        live_trading = self.build_live_trading()
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
        account_positions, _position_errors = self.live_account_positions()
        account = live_trading.account_summary(self.live_markets_for_open_positions(live_trading), account_positions)
        return {"settings": settings_payload, "account": account}

    def live_kill_switch_payload(self) -> dict[str, Any]:
        live_trading = self.build_live_trading()
        settings_payload = live_trading.emergency_stop()
        account_positions, _position_errors = self.live_account_positions()
        return {
            "settings": settings_payload,
            "account": live_trading.account_summary(self.live_markets_for_open_positions(live_trading), account_positions),
        }

    def live_linked_closed_positions_payload(self, limit: int) -> dict[str, Any]:
        client = self.build_client()
        closed_positions = []
        errors = []
        for user in self.live_account_user_ids():
            try:
                closed_positions.extend(client.get_user_closed_positions(user, limit=limit))
            except Exception as error:  # pragma: no cover - external API
                LOGGER.exception("Could not load linked closed positions")
                errors.append(f"closed positions {user[:6]}...: {error}")
        closed_positions.sort(key=lambda item: item.timestamp, reverse=True)
        return {
            "positions": decimal_to_json([asdict(item) for item in closed_positions[:limit]]),
            "positionCount": len(closed_positions),
            "realizedPnl": float(sum((item.realized_pnl for item in closed_positions), Decimal("0"))),
            "errors": errors,
        }

    def live_positions_payload(self, status: str | None, limit: int) -> dict[str, Any]:
        live_trading = self.build_live_trading()
        reconciliation = self.reconcile_live_trading(live_trading)
        positions = live_trading.list_positions(status=status, limit=limit)
        account_positions, position_errors = self.live_account_positions()
        if position_errors:
            reconciliation["errors"] = list(reconciliation.get("errors", [])) + position_errors
        markets = self.live_markets_for_open_positions(live_trading) if str(status or "").upper() == "OPEN" else {}
        if markets:
            positions = live_trading.mark_positions(positions, markets, account_positions)
        return {"positions": positions, "reconciliation": reconciliation}

    def paper_account_payload(self) -> dict[str, Any]:
        paper_trading = self.build_paper_trading()
        markets = self.build_client().get_markets_by_condition_ids(paper_trading.list_open_condition_ids())
        return paper_trading.get_marked_account(markets, save_snapshot=True)

    def update_paper_execution_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.watchlist_refresh_lock:
            paper_trading = self.build_paper_trading()
            settings_payload = paper_trading.set_execution_settings(
                entry_slippage_bps=Decimal(str(payload.get("entrySlippageBps", "25"))),
                exit_slippage_bps=Decimal(str(payload.get("exitSlippageBps", "25"))),
                fee_bps=Decimal(str(payload.get("feeBps", "0"))),
                max_chase_bps=Decimal(str(payload.get("maxChaseBps", "100"))),
                copytrade_capital_mode=str(payload.get("copytradeCapitalMode", "CONSERVATIVE")),
                min_cash_reserve_usdc=Decimal(str(payload.get("minCashReserveUsdc", "0"))),
            )
            try:
                markets = self.build_client().get_markets_by_condition_ids(paper_trading.list_open_condition_ids())
            except Exception:  # pragma: no cover - reserve enforcement can fall back to entry prices
                LOGGER.exception("Could not fetch markets for cash reserve enforcement")
                markets = {}
            reserve_result = paper_trading.enforce_cash_reserve(markets)
        settings_payload["cashReserveEnforcement"] = reserve_result
        return settings_payload

    def paper_positions_payload(self, status: str, limit: int) -> dict[str, Any]:
        paper_trading = self.build_paper_trading()
        positions = paper_trading.list_positions(status=status, limit=limit)
        if status == "OPEN":
            markets = self.build_client().get_markets_by_condition_ids(
                [str(position["condition_id"]) for position in positions]
            )
            positions = paper_trading.mark_positions(positions, markets, save_snapshots=True)
        positions = paper_trading.attach_mark_history(positions)
        return {"positionCount": len(positions), "positions": positions}

    @staticmethod
    def _public_account_user_ids(settings: Settings) -> list[str]:
        unique_users = []
        for user in [settings.polymarket_funder_address, settings.polymarket_account_address]:
            clean = str(user or "").strip()
            if clean and clean.lower() not in {item.lower() for item in unique_users}:
                unique_users.append(clean)
        return unique_users
