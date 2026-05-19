from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from decimal import InvalidOperation
from decimal import ROUND_DOWN
import json
from typing import Any

from src.config import load_settings
from src.models import ClosedPosition
from src.models import TraderActivity
from src.storage import connect_database


def clob_collateral_amount(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        raw = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return float(raw / Decimal("1000000"))


class LiveTrading:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def get_settings(self) -> dict[str, Any]:
        with connect_database(self.database_path) as connection:
            row = self._ensure_settings(connection)
        return self._settings_payload(row)

    def set_execution_settings(
        self,
        entry_slippage_bps: Decimal,
        exit_slippage_bps: Decimal,
        max_chase_bps: Decimal,
        copytrade_capital_mode: str,
        min_cash_reserve_usdc: Decimal,
        min_trade_usdc: Decimal,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        copytrade_capital_mode = copytrade_capital_mode.upper()
        if copytrade_capital_mode not in {"CONSERVATIVE", "AGGRESSIVE"}:
            copytrade_capital_mode = "CONSERVATIVE"
        with connect_database(self.database_path) as connection:
            self._ensure_settings(connection)
            connection.execute(
                """
                UPDATE live_execution_settings
                SET entry_slippage_bps = ?,
                    exit_slippage_bps = ?,
                    max_chase_bps = ?,
                    copytrade_capital_mode = ?,
                    min_cash_reserve_usdc = ?,
                    min_trade_usdc = ?,
                    updated_at = ?
                WHERE id = 1
                """,
                (
                    float(max(Decimal("0"), entry_slippage_bps)),
                    float(max(Decimal("0"), exit_slippage_bps)),
                    float(max(Decimal("0"), max_chase_bps)),
                    copytrade_capital_mode,
                    float(max(Decimal("0"), min_cash_reserve_usdc)),
                    float(max(Decimal("0"), min_trade_usdc)),
                    now,
                ),
            )
        return self.get_settings()

    def set_copytrade_settings(
        self,
        proxy_wallet: str,
        enabled: bool,
        sizing_mode: str = "PERCENT",
        size_value: Decimal = Decimal("10"),
        max_usdc: Decimal = Decimal("100"),
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        proxy_wallet = proxy_wallet.strip().lower()
        sizing_mode = sizing_mode.upper()
        if sizing_mode not in {"PERCENT", "FIXED"}:
            sizing_mode = "PERCENT"
        with connect_database(self.database_path) as connection:
            connection.execute("DELETE FROM live_copytrade_settings WHERE lower(proxy_wallet) = lower(?)", (proxy_wallet,))
            connection.execute(
                """
                INSERT INTO live_copytrade_settings (
                    proxy_wallet, enabled, sizing_mode, size_value, max_usdc, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (proxy_wallet, 1 if enabled else 0, sizing_mode, float(size_value), float(max_usdc), now, now),
            )
        return {
            "proxyWallet": proxy_wallet,
            "enabled": enabled,
            "sizingMode": sizing_mode,
            "sizeValue": float(size_value),
            "maxUsdc": float(max_usdc),
        }

    def get_copytrade_settings(self) -> dict[str, dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute("SELECT * FROM live_copytrade_settings").fetchall()
        return {
            str(row["proxy_wallet"]).lower(): {
                "enabled": bool(row["enabled"]),
                "sizing_mode": str(row["sizing_mode"]),
                "size_value": float(row["size_value"]),
                "max_usdc": float(row["max_usdc"]),
                "updated_at": str(row["updated_at"]),
            }
            for row in rows
        }

    def set_enabled(self, enabled: bool) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            current = self._ensure_settings(connection)
            starting_balance = current["starting_balance_usdc"]
            if enabled and starting_balance is None:
                starting_balance = self._current_collateral_balance_usdc()
            connection.execute(
                """
                UPDATE live_execution_settings
                SET enabled = ?, starting_balance_usdc = ?, updated_at = ?
                WHERE id = 1
                """,
                (1 if enabled else 0, float(starting_balance) if starting_balance is not None else None, now),
            )
        return self.get_settings()

    def emergency_stop(self, reason: str = "Manual kill switch") -> dict[str, Any]:
        settings = self.set_enabled(False)
        settings["reason"] = reason
        return settings

    def maybe_create_copy_order(self, trade: TraderActivity) -> dict[str, Any] | None:
        if not trade.asset:
            return None
        side = trade.side.upper()
        if side not in {"BUY", "SELL"}:
            return None

        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            settings = self._ensure_settings(connection)
            if not bool(settings["enabled"]):
                return None
            copy_setting = self._get_enabled_copy_setting(connection, trade.proxy_wallet)
            if copy_setting is None:
                return None

            existing = connection.execute(
                """
                SELECT 1
                FROM live_orders
                WHERE source_type = 'COPYTRADE'
                  AND source_transaction_hash = ?
                  AND strategy = 'COPYTRADE'
                """,
                (trade.transaction_hash,),
            ).fetchone()
            if existing:
                return None

            raw_requested_usdc = self._calculate_copy_size(
                source_usdc=trade.usdc_size,
                sizing_mode=str(copy_setting["sizing_mode"]).upper(),
                size_value=Decimal(str(copy_setting["size_value"])),
                max_usdc=Decimal(str(copy_setting["max_usdc"])),
            )
            live_settings = self._live_execution_settings(connection)
            if side == "BUY":
                requested_usdc = self._clamp_live_entry_size(
                    requested=raw_requested_usdc,
                    min_trade=live_settings["min_trade_usdc"],
                    max_trade=Decimal(str(copy_setting["max_usdc"])),
                )
            else:
                requested_usdc = raw_requested_usdc
            if requested_usdc <= 0 or trade.price <= 0:
                return None

            if side == "BUY":
                limit_price = self._worse_entry_price(trade.price, live_settings)
                if not self._within_max_chase(trade.price, limit_price, live_settings):
                    return self._record_live_order(
                        connection=connection,
                        trade=trade,
                        side=side,
                        requested_usdc=requested_usdc,
                        requested_size=Decimal("0"),
                        limit_price=limit_price,
                        status="REJECTED_CHASE_LIMIT",
                        reason=(
                            f"Observed {float(trade.price):.4f}, limit {float(limit_price):.4f}, "
                            f"max chase {float(live_settings['max_chase_bps']):.1f} bps"
                        ),
                        now=now,
                    )

                requested_size = requested_usdc / limit_price
                requested_size = self._round_order_size(requested_size)
                requested_usdc = self._round_buy_amount(requested_usdc)
                spendable_cash = self._live_spendable_cash(connection, settings, live_settings)
                if requested_usdc > spendable_cash:
                    return self._record_live_order(
                        connection=connection,
                        trade=trade,
                        side=side,
                        requested_usdc=requested_usdc,
                        requested_size=requested_size,
                        limit_price=limit_price,
                        status="REJECTED_LOW_BALANCE",
                        reason=(
                            f"Live copytrade skipped: needed ${float(requested_usdc):.2f}, "
                            f"spendable ${float(spendable_cash):.2f}. Live trading remains armed."
                        ),
                        now=now,
                    )
            else:
                limit_price = self._worse_exit_price(trade.price, live_settings)
                requested_size = self._matching_live_position_size(connection, trade, requested_usdc)
                requested_size = self._round_order_size(requested_size)
                if requested_size <= 0:
                    return self._record_live_order(
                        connection=connection,
                        trade=trade,
                        side=side,
                        requested_usdc=requested_usdc,
                        requested_size=Decimal("0"),
                        limit_price=limit_price,
                        status="NO_POSITION",
                        reason="Copied SELL had no matching live position opened by this bot.",
                        now=now,
                    )

        return self._submit_live_copy_order(
            trade=trade,
            side=side,
            requested_usdc=requested_usdc,
            requested_size=requested_size,
            limit_price=limit_price,
            now=now,
        )

    def list_orders(self, limit: int = 100) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM live_orders ORDER BY created_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_positions(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            if status:
                order_column = "closed_at" if status.upper() == "CLOSED" else "opened_at"
                rows = connection.execute(
                    f"""
                    SELECT *
                    FROM live_positions
                    WHERE status = ?
                    ORDER BY {order_column} DESC, id DESC
                    LIMIT ?
                    """,
                    (status.upper(), limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM live_positions ORDER BY opened_at DESC, id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(row) for row in rows]

    def account_summary(
        self,
        markets_by_condition_id: dict[str, dict[str, Any]] | None = None,
        account_positions: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        balance = self._current_collateral_balance_usdc()
        settings = self.get_settings()
        with connect_database(self.database_path) as connection:
            open_positions = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM live_positions WHERE status = 'OPEN' ORDER BY opened_at DESC, id DESC"
                ).fetchall()
            ]
            open_cost = Decimal(
                str(
                    sum(Decimal(str(position["cost_usdc"])) for position in open_positions)
                )
            )
            realized = Decimal(
                str(
                    connection.execute(
                        "SELECT COALESCE(SUM(pnl_usdc), 0) AS value FROM live_positions WHERE status = 'CLOSED'"
                    ).fetchone()["value"]
                    or 0
                )
            )
            orders = int(connection.execute("SELECT COUNT(*) AS value FROM live_orders").fetchone()["value"] or 0)
        marked_positions = self.mark_positions(open_positions, markets_by_condition_id or {}, account_positions)
        open_market_value = sum(Decimal(str(position["mark_value_usdc"])) for position in marked_positions)
        unrealized = sum(Decimal(str(position["unrealized_pnl_usdc"])) for position in marked_positions)
        running_pnl = realized + unrealized
        return {
            "enabled": settings["enabled"],
            "startingBalanceUsdc": settings["startingBalanceUsdc"],
            "balanceUsdc": float(balance),
            "openCostUsdc": float(open_cost),
            "openMarketValueUsdc": float(open_market_value),
            "realizedPnlUsdc": float(realized),
            "unrealizedPnlUsdc": float(unrealized),
            "runningPnlUsdc": float(running_pnl),
            "equityEstimateUsdc": float(balance + open_market_value),
            "orders": orders,
        }

    def save_account_snapshot(self, account: dict[str, Any] | None = None) -> None:
        account = account or self.account_summary()
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO live_account_snapshots (
                    observed_at, balance_usdc, open_cost_usdc, open_market_value_usdc,
                    realized_pnl_usdc, unrealized_pnl_usdc, running_pnl_usdc, equity_estimate_usdc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    now,
                    float(account.get("balanceUsdc") or 0),
                    float(account.get("openCostUsdc") or 0),
                    float(account.get("openMarketValueUsdc") or account.get("openCostUsdc") or 0),
                    float(account.get("realizedPnlUsdc") or 0),
                    float(account.get("unrealizedPnlUsdc") or 0),
                    float(account.get("runningPnlUsdc") or account.get("realizedPnlUsdc") or 0),
                    float(account.get("equityEstimateUsdc") or 0),
                ),
            )

    def list_account_snapshots(self, limit: int = 500) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM (
                    SELECT *
                    FROM live_account_snapshots
                    ORDER BY observed_at DESC
                    LIMIT ?
                )
                ORDER BY observed_at ASC
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_open_condition_ids(self) -> list[str]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                "SELECT DISTINCT condition_id FROM live_positions WHERE status = 'OPEN' AND condition_id != ''"
            ).fetchall()
        return [str(row["condition_id"]) for row in rows]

    def reconcile_account_positions(
        self,
        account_positions: list[dict[str, Any]],
        account_trades: list[TraderActivity],
        account_closed_positions: list[ClosedPosition] | None = None,
        markets_by_condition_id: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        actual_size_by_asset: dict[str, Decimal] = {}
        for position in account_positions:
            asset = self._position_asset(position)
            if not asset:
                continue
            actual_size_by_asset[asset] = actual_size_by_asset.get(asset, Decimal("0")) + self._position_size(position)

        account_closed_positions = account_closed_positions or []
        markets_by_condition_id = markets_by_condition_id or {}
        closed_positions = 0
        closed_size = Decimal("0")
        realized_pnl = Decimal("0")
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT *
                    FROM live_positions
                    WHERE status = 'OPEN'
                    ORDER BY asset ASC, opened_at ASC, id ASC
                    """
                ).fetchall()
            ]
            rows_by_asset: dict[str, list[dict[str, Any]]] = {}
            for row in rows:
                rows_by_asset.setdefault(str(row["asset"]), []).append(row)

            for asset, asset_rows in rows_by_asset.items():
                local_size = sum(Decimal(str(row["size"])) for row in asset_rows)
                actual_size = actual_size_by_asset.get(asset, Decimal("0"))
                missing_size = local_size - actual_size
                if missing_size <= Decimal("0.00005"):
                    continue

                earliest_opened_at = min(str(row["opened_at"]) for row in asset_rows)
                matching_sell_trades = self._matching_sell_trades(asset, account_trades, earliest_opened_at)
                closed_position = self._matching_closed_position(asset_rows[0], account_closed_positions)
                if closed_position is None and not matching_sell_trades:
                    continue

                exit_price = self._sell_trade_exit_price(asset, account_trades, earliest_opened_at)
                closed_at = self._sell_trade_closed_at(asset, account_trades, earliest_opened_at) or now
                close_reason = "Reconciled from linked account SELL trade."
                if closed_position is not None:
                    exit_price = self._closed_position_exit_price(closed_position)
                    closed_at = datetime.fromtimestamp(closed_position.timestamp, UTC).isoformat()
                    close_reason = "Reconciled from linked account closed-position result."
                if exit_price is None:
                    exit_price = self._market_price_for_position(
                        asset_rows[0],
                        markets_by_condition_id.get(str(asset_rows[0]["condition_id"])),
                    )
                    close_reason = "Externally closed on linked account; using latest market mark."
                if exit_price is None:
                    close_reason = "Externally closed on linked account; exit price unavailable, using each entry price."

                result = self._close_live_rows(
                    connection=connection,
                    rows=asset_rows,
                    sell_size=missing_size,
                    exit_price=exit_price,
                    closed_at=closed_at,
                    close_reason=close_reason,
                )
                closed_positions += result["closed_positions"]
                closed_size += result["closed_size"]
                realized_pnl += result["realized_pnl"]

        return {
            "closedPositions": closed_positions,
            "closedSize": float(closed_size),
            "realizedPnlUsdc": float(realized_pnl),
        }

    def repair_closed_positions_from_account_results(self, account_closed_positions: list[ClosedPosition]) -> dict[str, Any]:
        repaired = 0
        realized_delta = Decimal("0")
        with connect_database(self.database_path) as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT *
                    FROM live_positions
                    WHERE status = 'CLOSED'
                      AND close_reason LIKE 'Externally closed on linked account;%'
                    """
                ).fetchall()
            ]
            for row in rows:
                closed_position = self._matching_closed_position(row, account_closed_positions)
                if closed_position is None:
                    continue
                exit_price = self._closed_position_exit_price(closed_position)
                if exit_price is None:
                    continue
                size = Decimal(str(row["size"]))
                cost = Decimal(str(row["cost_usdc"]))
                exit_value = size * exit_price
                pnl = exit_value - cost
                old_pnl = Decimal(str(row["pnl_usdc"] or 0))
                connection.execute(
                    """
                    UPDATE live_positions
                    SET closed_at = ?, exit_price = ?, exit_value_usdc = ?,
                        pnl_usdc = ?, close_reason = ?
                    WHERE id = ?
                    """,
                    (
                        datetime.fromtimestamp(closed_position.timestamp, UTC).isoformat(),
                        float(exit_price),
                        float(exit_value),
                        float(pnl),
                        "Repaired from linked account closed-position result.",
                        int(row["id"]),
                    ),
                )
                repaired += 1
                realized_delta += pnl - old_pnl
        return {"repairedPositions": repaired, "realizedPnlDeltaUsdc": float(realized_delta)}

    def reopen_false_closed_positions(
        self,
        account_positions: list[dict[str, Any]],
        account_trades: list[TraderActivity],
        account_closed_positions: list[ClosedPosition],
    ) -> dict[str, Any]:
        actual_size_by_asset: dict[str, Decimal] = {}
        for position in account_positions:
            asset = self._position_asset(position)
            if not asset:
                continue
            actual_size_by_asset[asset] = actual_size_by_asset.get(asset, Decimal("0")) + self._position_size(position)

        reopened = 0
        with connect_database(self.database_path) as connection:
            open_rows = [
                dict(row)
                for row in connection.execute("SELECT asset, size FROM live_positions WHERE status = 'OPEN'").fetchall()
            ]
            local_open_by_asset: dict[str, Decimal] = {}
            for row in open_rows:
                asset = str(row["asset"])
                local_open_by_asset[asset] = local_open_by_asset.get(asset, Decimal("0")) + Decimal(str(row["size"]))

            closed_rows = [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT *
                    FROM live_positions
                    WHERE status = 'CLOSED'
                      AND (
                        close_reason LIKE 'Externally closed on linked account;%'
                        OR close_reason = 'Reconciled from linked account position size.'
                      )
                    ORDER BY closed_at DESC, id DESC
                    """
                ).fetchall()
            ]
            for row in closed_rows:
                asset = str(row["asset"])
                actual_size = actual_size_by_asset.get(asset, Decimal("0"))
                local_open = local_open_by_asset.get(asset, Decimal("0"))
                if actual_size <= local_open + Decimal("0.00005"):
                    continue
                if self._matching_closed_position(row, account_closed_positions) is not None:
                    continue
                if self._matching_sell_trades(asset, account_trades, str(row["opened_at"])):
                    continue
                row_size = Decimal(str(row["size"]))
                if row_size > actual_size - local_open + Decimal("0.00005"):
                    continue
                connection.execute(
                    """
                    UPDATE live_positions
                    SET status = 'OPEN',
                        closed_at = NULL,
                        exit_price = NULL,
                        exit_value_usdc = NULL,
                        pnl_usdc = NULL,
                        exit_fee_usdc = 0,
                        close_reason = ''
                    WHERE id = ?
                    """,
                    (int(row["id"]),),
                )
                local_open_by_asset[asset] = local_open + row_size
                reopened += 1
        return {"reopenedPositions": reopened}

    def mark_positions(
        self,
        positions: list[dict[str, Any]],
        markets_by_condition_id: dict[str, dict[str, Any]],
        account_positions: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        account_marks = self._account_position_marks(account_positions or [])
        marked_positions = []
        for position in positions:
            asset = str(position.get("asset") or "")
            mark_value = None
            mark_price = None
            if asset in account_marks and account_marks[asset]["size"] > 0:
                mark_price = account_marks[asset]["current_value"] / account_marks[asset]["size"]
                mark_value = Decimal(str(position["size"])) * mark_price
            else:
                mark_price = self._market_price_for_position(
                    position=position,
                    market=markets_by_condition_id.get(str(position["condition_id"])),
                )
                if mark_price is not None:
                    mark_value = Decimal(str(position["size"])) * mark_price

            if mark_value is None:
                mark_value = Decimal(str(position["cost_usdc"]))
                unrealized_pnl = Decimal("0")
            else:
                unrealized_pnl = mark_value - Decimal(str(position["cost_usdc"]))
            item = dict(position)
            item.update(
                {
                    "mark_price": float(mark_price) if mark_price is not None else None,
                    "mark_value_usdc": float(mark_value),
                    "unrealized_pnl_usdc": float(unrealized_pnl),
                }
            )
            marked_positions.append(item)
        return marked_positions

    @staticmethod
    def _account_position_marks(account_positions: list[dict[str, Any]]) -> dict[str, dict[str, Decimal]]:
        marks: dict[str, dict[str, Decimal]] = {}
        for position in account_positions:
            asset = LiveTrading._position_asset(position)
            if not asset:
                continue
            size = LiveTrading._position_size(position)
            current_value = LiveTrading._position_current_value(position)
            if size <= 0 or current_value is None:
                continue
            item = marks.setdefault(asset, {"size": Decimal("0"), "current_value": Decimal("0")})
            item["size"] += size
            item["current_value"] += current_value
        return marks

    def _submit_live_copy_order(
        self,
        trade: TraderActivity,
        side: str,
        requested_usdc: Decimal,
        requested_size: Decimal,
        limit_price: Decimal,
        now: str,
    ) -> dict[str, Any]:
        try:
            client = self._build_clob_client()
            if side == "BUY":
                order_args = self._market_order_args(
                    token_id=trade.asset,
                    amount=float(requested_usdc),
                    price=float(limit_price),
                    side=side,
                    order_type=self._order_type().FOK,
                )
                signed_order = client.create_market_order(order_args)
            else:
                order_args = self._order_args(
                    token_id=trade.asset,
                    price=float(limit_price),
                    size=float(requested_size),
                    side=side,
                )
                signed_order = client.create_order(order_args)
            response = client.post_order(signed_order, order_type=self._order_type().FOK)
            success = self._response_success(response)
            status = "SUBMITTED_LIVE" if success else "REJECTED_BY_CLOB"
            reason = "Live FOK copy order submitted." if success else "CLOB did not accept the live order."
        except Exception as error:
            response = {"error": str(error)}
            success = False
            status, reason = self._live_order_error_status(error)

        with connect_database(self.database_path) as connection:
            result = self._record_live_order(
                connection=connection,
                trade=trade,
                side=side,
                requested_usdc=requested_usdc,
                requested_size=requested_size,
                limit_price=limit_price,
                status=status,
                reason=reason,
                now=now,
                raw_response=response,
            )
            order_id = int(result["id"])
            if success and side == "BUY":
                connection.execute(
                    """
                    INSERT INTO live_positions (
                        order_id, source_wallet, title, outcome, asset, condition_id,
                        entry_price, size, cost_usdc, entry_fee_usdc, status, opened_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'OPEN', ?)
                    """,
                    (
                        order_id,
                        trade.proxy_wallet,
                        trade.title,
                        trade.outcome,
                        trade.asset,
                        trade.condition_id,
                        float(limit_price),
                        float(requested_size),
                        float(requested_usdc),
                        now,
                    ),
                )
            elif success and side == "SELL":
                self._close_live_positions(connection, trade, requested_size, limit_price, now)
        return result

    def _record_live_order(
        self,
        connection,
        trade: TraderActivity,
        side: str,
        requested_usdc: Decimal,
        requested_size: Decimal,
        limit_price: Decimal,
        status: str,
        reason: str,
        now: str,
        raw_response: Any | None = None,
    ) -> dict[str, Any]:
        raw_response = raw_response or {}
        clob_order_id = self._extract_order_id(raw_response)
        connection.execute(
            """
            INSERT OR IGNORE INTO live_orders (
                source_type, source_wallet, source_transaction_hash, strategy, side,
                title, outcome, asset, condition_id, requested_usdc, requested_size,
                limit_price, status, reason, clob_order_id, raw_response, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "COPYTRADE",
                trade.proxy_wallet,
                trade.transaction_hash,
                "COPYTRADE",
                side,
                trade.title,
                trade.outcome,
                trade.asset,
                trade.condition_id,
                float(requested_usdc),
                float(requested_size),
                float(limit_price),
                status,
                reason,
                clob_order_id,
                json.dumps(raw_response, default=str),
                now,
            ),
        )
        order_id = int(connection.execute("SELECT last_insert_rowid() AS id").fetchone()["id"] or 0)
        return {
            "id": order_id,
            "sourceWallet": trade.proxy_wallet,
            "sourceTransactionHash": trade.transaction_hash,
            "requestedUsdc": float(requested_usdc),
            "requestedSize": float(requested_size),
            "limitPrice": float(limit_price),
            "side": side,
            "status": status,
            "reason": reason,
            "title": trade.title,
            "outcome": trade.outcome,
        }

    def _close_live_positions(self, connection, trade: TraderActivity, sell_size: Decimal, exit_price: Decimal, now: str) -> None:
        rows = connection.execute(
            """
            SELECT *
            FROM live_positions
            WHERE status = 'OPEN'
              AND source_wallet = ?
              AND asset = ?
              AND condition_id = ?
              AND outcome = ?
            ORDER BY opened_at ASC, id ASC
            """,
            (trade.proxy_wallet, trade.asset, trade.condition_id, trade.outcome),
        ).fetchall()
        self._close_live_rows(
            connection=connection,
            rows=[dict(row) for row in rows],
            sell_size=sell_size,
            exit_price=exit_price,
            closed_at=now,
            close_reason="Copied live SELL",
            partial_close_reason="Copied live SELL partial close",
        )

    @staticmethod
    def _close_live_rows(
        connection,
        rows: list[dict[str, Any]],
        sell_size: Decimal,
        exit_price: Decimal | None,
        closed_at: str,
        close_reason: str,
        partial_close_reason: str | None = None,
    ) -> dict[str, Any]:
        partial_close_reason = partial_close_reason or close_reason
        remaining = sell_size
        closed_positions = 0
        closed_size_total = Decimal("0")
        realized_pnl_total = Decimal("0")
        for row in rows:
            if remaining <= 0:
                break
            size = Decimal(str(row["size"]))
            close_size = min(size, remaining)
            ratio = close_size / size
            cost = Decimal(str(row["cost_usdc"])) * ratio
            entry_fee = Decimal(str(row.get("entry_fee_usdc") or 0)) * ratio
            row_exit_price = exit_price if exit_price is not None else Decimal(str(row["entry_price"]))
            exit_value = close_size * row_exit_price
            pnl = exit_value - cost
            if close_size == size:
                connection.execute(
                    """
                    UPDATE live_positions
                    SET status = 'CLOSED', closed_at = ?, exit_price = ?, exit_value_usdc = ?,
                        pnl_usdc = ?, exit_fee_usdc = ?, close_reason = ?
                    WHERE id = ?
                    """,
                    (closed_at, float(row_exit_price), float(exit_value), float(pnl), 0.0, close_reason, int(row["id"])),
                )
                closed_positions += 1
            else:
                connection.execute(
                    "UPDATE live_positions SET size = ?, cost_usdc = ?, entry_fee_usdc = ? WHERE id = ?",
                    (
                        float(size - close_size),
                        float(Decimal(str(row["cost_usdc"])) - cost),
                        float(Decimal(str(row.get("entry_fee_usdc") or 0)) - entry_fee),
                        int(row["id"]),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO live_positions (
                        order_id, source_wallet, title, outcome, asset, condition_id, entry_price,
                        size, cost_usdc, entry_fee_usdc, status, opened_at, closed_at, exit_price,
                        exit_value_usdc, pnl_usdc, exit_fee_usdc, close_reason
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CLOSED', ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(row["order_id"]),
                        str(row["source_wallet"]),
                        str(row["title"]),
                        str(row["outcome"]),
                        str(row["asset"]),
                        str(row["condition_id"]),
                        float(row["entry_price"]),
                        float(close_size),
                        float(cost),
                        float(entry_fee),
                        str(row["opened_at"]),
                        closed_at,
                        float(row_exit_price),
                        float(exit_value),
                        float(pnl),
                        0.0,
                        partial_close_reason,
                    ),
                )
                closed_positions += 1
            remaining -= close_size
            closed_size_total += close_size
            realized_pnl_total += pnl
        return {
            "closed_positions": closed_positions,
            "closed_size": closed_size_total,
            "realized_pnl": realized_pnl_total,
        }

    def _live_spendable_cash(self, connection, _settings: dict[str, Any], live_settings: dict[str, Decimal]) -> Decimal:
        balance = self._current_collateral_balance_usdc()
        after_reserve = max(Decimal("0"), balance - live_settings["min_cash_reserve_usdc"])
        if live_settings["copytrade_capital_mode"] == "AGGRESSIVE":
            return after_reserve

        open_cost = self._live_open_cost(connection)
        realized_pnl = self._live_realized_pnl(connection)
        protected_profit = max(Decimal("0"), realized_pnl)
        conservative_capital = max(Decimal("0"), balance + open_cost - protected_profit)
        remaining_conservative_capital = max(Decimal("0"), conservative_capital - open_cost)
        return min(after_reserve, remaining_conservative_capital)

    @staticmethod
    def _live_open_cost(connection) -> Decimal:
        return Decimal(
            str(
                connection.execute(
                    "SELECT COALESCE(SUM(cost_usdc), 0) AS value FROM live_positions WHERE status = 'OPEN'"
                ).fetchone()["value"]
                or 0
            )
        )

    @staticmethod
    def _live_realized_pnl(connection) -> Decimal:
        return Decimal(
            str(
                connection.execute(
                    "SELECT COALESCE(SUM(pnl_usdc), 0) AS value FROM live_positions WHERE status = 'CLOSED'"
                ).fetchone()["value"]
                or 0
            )
        )

    def _current_collateral_balance_usdc(self) -> Decimal:
        settings = load_settings()
        client = self._build_clob_client()
        from py_clob_client_v2.clob_types import AssetType, BalanceAllowanceParams

        data = client.get_balance_allowance(
            BalanceAllowanceParams(asset_type=AssetType.COLLATERAL, signature_type=int(settings.polymarket_signature_type or "3"))
        )
        balance = clob_collateral_amount(data.get("balance") if isinstance(data, dict) else None)
        return Decimal(str(balance or 0))

    def _build_clob_client(self):
        settings = load_settings()
        from py_clob_client_v2.client import ClobClient
        from py_clob_client_v2.clob_types import ApiCreds
        from py_clob_client_v2.constants import POLYGON

        return ClobClient(
            host=settings.clob_base_url,
            chain_id=POLYGON,
            key=settings.polymarket_private_key,
            creds=ApiCreds(
                api_key=settings.polymarket_api_key,
                api_secret=settings.polymarket_api_secret,
                api_passphrase=settings.polymarket_api_passphrase,
            ),
            signature_type=int(settings.polymarket_signature_type or "3"),
            funder=settings.polymarket_funder_address or None,
        )

    @staticmethod
    def _order_args(**kwargs):
        from py_clob_client_v2.clob_types import OrderArgs

        return OrderArgs(**kwargs)

    @staticmethod
    def _market_order_args(**kwargs):
        from py_clob_client_v2.clob_types import MarketOrderArgs

        return MarketOrderArgs(**kwargs)

    @staticmethod
    def _order_type():
        from py_clob_client_v2.clob_types import OrderType

        return OrderType

    @staticmethod
    def _ensure_settings(connection) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        connection.execute(
            """
            INSERT OR IGNORE INTO live_execution_settings (
                id, enabled, starting_balance_usdc, entry_slippage_bps, exit_slippage_bps,
                max_chase_bps, copytrade_capital_mode, min_cash_reserve_usdc, min_trade_usdc, updated_at
            )
            VALUES (1, 0, NULL, 25, 25, 100, 'CONSERVATIVE', 0, 1, ?)
            """,
            (now,),
        )
        return dict(connection.execute("SELECT * FROM live_execution_settings WHERE id = 1").fetchone())

    @staticmethod
    def _settings_payload(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "enabled": bool(row["enabled"]),
            "startingBalanceUsdc": row["starting_balance_usdc"],
            "entrySlippageBps": float(row["entry_slippage_bps"]),
            "exitSlippageBps": float(row["exit_slippage_bps"]),
            "maxChaseBps": float(row["max_chase_bps"]),
            "copytradeCapitalMode": str(row["copytrade_capital_mode"]),
            "minCashReserveUsdc": float(row["min_cash_reserve_usdc"]),
            "minTradeUsdc": float(row["min_trade_usdc"]),
            "updatedAt": row["updated_at"],
        }

    @staticmethod
    def _get_enabled_copy_setting(connection, proxy_wallet: str) -> dict[str, Any] | None:
        row = connection.execute(
            """
            SELECT *
            FROM live_copytrade_settings
            WHERE lower(proxy_wallet) = lower(?) AND enabled = 1
            LIMIT 1
            """,
            (proxy_wallet,),
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def _live_execution_settings(connection) -> dict[str, Decimal]:
        row = LiveTrading._ensure_settings(connection)
        return {
            "entry_slippage_bps": Decimal(str(row["entry_slippage_bps"])),
            "exit_slippage_bps": Decimal(str(row["exit_slippage_bps"])),
            "max_chase_bps": Decimal(str(row["max_chase_bps"])),
            "copytrade_capital_mode": str(row["copytrade_capital_mode"]).upper(),
            "min_cash_reserve_usdc": Decimal(str(row["min_cash_reserve_usdc"])),
            "min_trade_usdc": Decimal(str(row["min_trade_usdc"])),
        }

    @staticmethod
    def _calculate_copy_size(source_usdc: Decimal, sizing_mode: str, size_value: Decimal, max_usdc: Decimal) -> Decimal:
        requested = size_value if sizing_mode == "FIXED" else source_usdc * (size_value / Decimal("100"))
        return min(requested, max_usdc)

    @staticmethod
    def _clamp_live_entry_size(requested: Decimal, min_trade: Decimal, max_trade: Decimal) -> Decimal:
        if max_trade <= 0:
            return Decimal("0")
        return min(max(requested, min_trade), max_trade)

    @staticmethod
    def _round_buy_amount(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    @staticmethod
    def _round_order_size(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

    @staticmethod
    def _worse_entry_price(observed_price: Decimal, settings: dict[str, Decimal]) -> Decimal:
        return min(Decimal("0.9999"), observed_price * (Decimal("1") + settings["entry_slippage_bps"] / Decimal("10000")))

    @staticmethod
    def _worse_exit_price(observed_price: Decimal, settings: dict[str, Decimal]) -> Decimal:
        return max(Decimal("0.0001"), observed_price * (Decimal("1") - settings["exit_slippage_bps"] / Decimal("10000")))

    @staticmethod
    def _within_max_chase(observed_price: Decimal, entry_price: Decimal, settings: dict[str, Decimal]) -> bool:
        chase_bps = ((entry_price - observed_price) / observed_price) * Decimal("10000")
        return chase_bps <= settings["max_chase_bps"]

    @staticmethod
    def _response_success(response: Any) -> bool:
        if isinstance(response, dict):
            if response.get("error"):
                return False
            if response.get("success") is True:
                return True
            status = str(response.get("status") or response.get("orderStatus") or "").lower()
            if status in {"matched", "live", "delayed", "submitted"}:
                return True
            if response.get("orderID") or response.get("orderId") or response.get("id"):
                return True
        return False

    @staticmethod
    def _extract_order_id(response: Any) -> str:
        if not isinstance(response, dict):
            return ""
        return str(response.get("orderID") or response.get("orderId") or response.get("id") or "")

    @staticmethod
    def _live_order_error_status(error: Exception) -> tuple[str, str]:
        message = str(error)
        normalized = message.lower()
        if "fok orders are fully filled or killed" in normalized or "couldn't be fully filled" in normalized:
            return (
                "REJECTED_NOT_FILLED",
                "Live FOK copy order was not filled immediately at the protected price. Live trading remains armed.",
            )
        if "not enough balance" in normalized or "insufficient" in normalized:
            return (
                "REJECTED_LOW_BALANCE",
                "Live copy order was rejected for insufficient available balance. Live trading remains armed.",
            )
        return ("ERROR", message)

    @staticmethod
    def _matching_live_position_size(connection, trade: TraderActivity, requested_usdc: Decimal) -> Decimal:
        target_size = requested_usdc / trade.price
        row = connection.execute(
            """
            SELECT COALESCE(SUM(size), 0) AS value
            FROM live_positions
            WHERE status = 'OPEN'
              AND source_wallet = ?
              AND asset = ?
              AND condition_id = ?
              AND outcome = ?
            """,
            (trade.proxy_wallet, trade.asset, trade.condition_id, trade.outcome),
        ).fetchone()
        available = Decimal(str(row["value"] or 0))
        return min(target_size, available)

    @staticmethod
    def _position_asset(position: dict[str, Any]) -> str:
        return str(
            position.get("asset")
            or position.get("tokenId")
            or position.get("token_id")
            or position.get("assetTokenId")
            or position.get("clobTokenId")
            or ""
        )

    @staticmethod
    def _position_size(position: dict[str, Any]) -> Decimal:
        for key in ("size", "shares", "amount"):
            value = position.get(key)
            if value not in (None, ""):
                return max(Decimal("0"), Decimal(str(value)))
        return Decimal("0")

    @staticmethod
    def _position_current_value(position: dict[str, Any]) -> Decimal | None:
        for key in ("currentValue", "current_value", "value", "usdcValue"):
            value = position.get(key)
            if value not in (None, ""):
                return max(Decimal("0"), Decimal(str(value)))
        price = position.get("curPrice") or position.get("price")
        size = LiveTrading._position_size(position)
        if price not in (None, "") and size > 0:
            return size * Decimal(str(price))
        return None

    @staticmethod
    def _sell_trade_exit_price(asset: str, trades: list[TraderActivity], opened_at: str) -> Decimal | None:
        candidates = LiveTrading._matching_sell_trades(asset, trades, opened_at)
        total_size = sum((trade.size for trade in candidates if trade.size > 0), Decimal("0"))
        if total_size <= 0:
            return None
        total_value = sum((trade.usdc_size for trade in candidates if trade.size > 0), Decimal("0"))
        if total_value <= 0:
            return candidates[0].price if candidates else None
        return total_value / total_size

    @staticmethod
    def _sell_trade_closed_at(asset: str, trades: list[TraderActivity], opened_at: str) -> str | None:
        candidates = LiveTrading._matching_sell_trades(asset, trades, opened_at)
        if not candidates:
            return None
        latest = max(trade.timestamp for trade in candidates)
        return datetime.fromtimestamp(latest, UTC).isoformat()

    @staticmethod
    def _matching_closed_position(
        position: dict[str, Any],
        closed_positions: list[ClosedPosition],
    ) -> ClosedPosition | None:
        condition_id = str(position.get("condition_id") or "")
        outcome = str(position.get("outcome") or "").lower()
        matches = [
            item
            for item in closed_positions
            if item.condition_id == condition_id and item.outcome.lower() == outcome
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.timestamp)

    @staticmethod
    def _closed_position_exit_price(position: ClosedPosition) -> Decimal | None:
        if position.total_bought <= 0:
            return None
        total_cost = position.avg_price * position.total_bought
        return (total_cost + position.realized_pnl) / position.total_bought

    @staticmethod
    def _matching_sell_trades(asset: str, trades: list[TraderActivity], opened_at: str) -> list[TraderActivity]:
        opened_timestamp = LiveTrading._iso_timestamp(opened_at)
        return [
            trade
            for trade in trades
            if str(trade.asset) == asset
            and str(trade.side).upper() == "SELL"
            and trade.timestamp >= opened_timestamp - 60
        ]

    @staticmethod
    def _iso_timestamp(value: str) -> int:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return 0
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return int(parsed.timestamp())

    @staticmethod
    def _market_price_for_position(position: dict[str, Any], market: dict[str, Any] | None) -> Decimal | None:
        if not market:
            return None
        outcome_prices = [Decimal(str(item)) for item in LiveTrading._parse_json_list(market.get("outcomePrices"))]
        token_ids = LiveTrading._parse_json_list(market.get("clobTokenIds"))
        outcomes = LiveTrading._parse_json_list(market.get("outcomes"))
        asset = str(position.get("asset") or "")
        outcome = str(position.get("outcome") or "")
        if asset in token_ids and len(outcome_prices) == len(token_ids):
            return outcome_prices[token_ids.index(asset)]
        if outcome in outcomes and len(outcome_prices) == len(outcomes):
            return outcome_prices[outcomes.index(outcome)]
        return None

    @staticmethod
    def _parse_json_list(raw: Any) -> list[str]:
        if raw is None:
            return []
        if isinstance(raw, list):
            return [str(item) for item in raw]
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return []
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        return []
