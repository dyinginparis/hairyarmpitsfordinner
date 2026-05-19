from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import json
from typing import Any

from src.models import ClosedPosition
from src.models import TraderActivity
from src.models import BinaryArbitrageOpportunity
from src.storage import connect_database


DEFAULT_EXECUTION_SETTINGS = {
    "entry_slippage_bps": Decimal("25"),
    "exit_slippage_bps": Decimal("25"),
    "fee_bps": Decimal("0"),
    "max_chase_bps": Decimal("100"),
    "copytrade_capital_mode": "CONSERVATIVE",
    "min_cash_reserve_usdc": Decimal("0"),
}


class PaperTrading:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

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
            connection.execute("DELETE FROM copytrade_settings WHERE lower(proxy_wallet) = lower(?)", (proxy_wallet,))
            connection.execute(
                """
                INSERT INTO copytrade_settings (
                    proxy_wallet, enabled, sizing_mode, size_value, max_usdc, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proxy_wallet,
                    1 if enabled else 0,
                    sizing_mode,
                    float(size_value),
                    float(max_usdc),
                    now,
                    now,
                ),
            )
        return {
            "proxyWallet": proxy_wallet,
            "enabled": enabled,
            "sizingMode": sizing_mode,
            "sizeValue": float(size_value),
            "maxUsdc": float(max_usdc),
        }

    def get_account(self) -> dict[str, Any]:
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            row = connection.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
            active_cost = connection.execute(
                "SELECT COALESCE(SUM(cost_usdc), 0) AS value FROM paper_positions WHERE status = 'OPEN'"
            ).fetchone()["value"]
            closed = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN pnl_usdc > 0 THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN pnl_usdc < 0 THEN 1 ELSE 0 END) AS losses,
                    COALESCE(SUM(pnl_usdc), 0) AS realized_pnl
                FROM paper_positions
                WHERE status = 'CLOSED'
                """
            ).fetchone()

        wins = int(closed["wins"] or 0)
        losses = int(closed["losses"] or 0)
        decisive = wins + losses
        win_loss_ratio = float(wins / losses) if losses else float(wins) if wins else 0.0
        win_rate = float(wins / decisive) if decisive else 0.0
        return {
            "startingBalance": float(row["starting_balance"]),
            "cashBalance": float(row["cash_balance"]),
            "activeCost": float(active_cost or 0),
            "equityEstimate": float(row["cash_balance"] + (active_cost or 0)),
            "closedTrades": int(closed["total"] or 0),
            "wins": wins,
            "losses": losses,
            "winLossRatio": win_loss_ratio,
            "winRate": win_rate,
            "realizedPnl": float(closed["realized_pnl"] or 0),
        }

    def get_marked_account(
        self,
        markets_by_condition_id: dict[str, dict[str, Any]],
        save_snapshot: bool = False,
    ) -> dict[str, Any]:
        account = self.get_account()
        open_positions = self.mark_positions(self.list_positions(status="OPEN", limit=5000), markets_by_condition_id)
        open_market_value = sum(Decimal(str(position["mark_value_usdc"])) for position in open_positions)
        unrealized_pnl = sum(Decimal(str(position["unrealized_pnl_usdc"])) for position in open_positions)
        realized_pnl = Decimal(str(account["realizedPnl"]))
        account.update(
            {
                "openMarketValue": float(open_market_value),
                "unrealizedPnl": float(unrealized_pnl),
                "runningPnl": float(realized_pnl + unrealized_pnl),
                "equityEstimate": float(Decimal(str(account["cashBalance"])) + open_market_value),
                "markedOpenPositions": sum(1 for position in open_positions if position["mark_price"] is not None),
                "unpricedOpenPositions": sum(1 for position in open_positions if position["mark_price"] is None),
            }
        )
        if save_snapshot:
            self.save_account_snapshot(account)
        return account

    def set_balance(self, balance: Decimal) -> dict[str, Any]:
        if balance < 0:
            raise ValueError("Paper balance cannot be negative")

        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            active_cost = Decimal(
                str(
                    connection.execute(
                        "SELECT COALESCE(SUM(cost_usdc), 0) AS value FROM paper_positions WHERE status = 'OPEN'"
                    ).fetchone()["value"]
                    or 0
                )
            )
            cash_balance = max(Decimal("0"), balance - active_cost)
            connection.execute(
                """
                INSERT INTO paper_account (id, starting_balance, cash_balance, updated_at)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    starting_balance = excluded.starting_balance,
                    cash_balance = excluded.cash_balance,
                    updated_at = excluded.updated_at
                """,
                (float(balance), float(cash_balance), now),
            )
        return self.get_account()

    def reset_account(self) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            account = connection.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
            starting_balance = Decimal(str(account["starting_balance"]))
            open_positions = int(
                connection.execute(
                    "SELECT COUNT(*) AS value FROM paper_positions WHERE status = 'OPEN'"
                ).fetchone()["value"]
                or 0
            )
            position_count = int(
                connection.execute("SELECT COUNT(*) AS value FROM paper_positions").fetchone()["value"] or 0
            )
            order_count = int(connection.execute("SELECT COUNT(*) AS value FROM paper_orders").fetchone()["value"] or 0)

            connection.execute("DELETE FROM paper_mark_snapshots")
            connection.execute("DELETE FROM paper_account_snapshots")
            connection.execute("DELETE FROM paper_positions")
            connection.execute("DELETE FROM paper_orders")
            connection.execute("DELETE FROM paper_events")
            connection.execute(
                """
                UPDATE paper_account
                SET cash_balance = starting_balance,
                    updated_at = ?
                WHERE id = 1
                """,
                (now,),
            )
            connection.execute(
                """
                UPDATE copytrade_settings
                SET enabled = 0,
                    updated_at = ?
                """,
                (now,),
            )
            disabled_copytraders = connection.execute("SELECT changes() AS value").fetchone()["value"]
            connection.execute(
                """
                INSERT INTO paper_events (event_type, message, created_at)
                VALUES ('PAPER_ACCOUNT_RESET', ?, ?)
                """,
                (
                    "Paper account reset: positions and orders cleared, balance restored, copytrading disabled.",
                    now,
                ),
            )

        return {
            "reset": True,
            "startingBalance": float(starting_balance),
            "cashBalance": float(starting_balance),
            "positionsCleared": position_count,
            "openPositionsCleared": open_positions,
            "ordersCleared": order_count,
            "copytradersDisabled": int(disabled_copytraders or 0),
            "resetAt": now,
        }

    def get_copytrade_settings(self) -> dict[str, dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute("SELECT * FROM copytrade_settings").fetchall()
        return {
            str(row["proxy_wallet"]).lower(): {
                "proxy_wallet": str(row["proxy_wallet"]),
                "enabled": bool(row["enabled"]),
                "sizing_mode": str(row["sizing_mode"]),
                "size_value": float(row["size_value"]),
                "max_usdc": float(row["max_usdc"]),
            }
            for row in rows
        }

    def get_execution_settings(self) -> dict[str, Any]:
        with connect_database(self.database_path) as connection:
            settings = self._ensure_execution_settings(connection)
            return self._execution_settings_payload(settings)

    def set_execution_settings(
        self,
        entry_slippage_bps: Decimal,
        exit_slippage_bps: Decimal,
        fee_bps: Decimal,
        max_chase_bps: Decimal,
        copytrade_capital_mode: str = "CONSERVATIVE",
        min_cash_reserve_usdc: Decimal = Decimal("0"),
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        copytrade_capital_mode = copytrade_capital_mode.upper()
        if copytrade_capital_mode not in {"CONSERVATIVE", "AGGRESSIVE"}:
            copytrade_capital_mode = "CONSERVATIVE"
        values = {
            "entry_slippage_bps": self._clamp_bps(entry_slippage_bps),
            "exit_slippage_bps": self._clamp_bps(exit_slippage_bps),
            "fee_bps": self._clamp_bps(fee_bps),
            "max_chase_bps": self._clamp_bps(max_chase_bps),
            "copytrade_capital_mode": copytrade_capital_mode,
            "min_cash_reserve_usdc": max(Decimal("0"), min_cash_reserve_usdc),
        }
        with connect_database(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO paper_execution_settings (
                    id, entry_slippage_bps, exit_slippage_bps, fee_bps, max_chase_bps,
                    copytrade_capital_mode, min_cash_reserve_usdc, updated_at
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    entry_slippage_bps = excluded.entry_slippage_bps,
                    exit_slippage_bps = excluded.exit_slippage_bps,
                    fee_bps = excluded.fee_bps,
                    max_chase_bps = excluded.max_chase_bps,
                    copytrade_capital_mode = excluded.copytrade_capital_mode,
                    min_cash_reserve_usdc = excluded.min_cash_reserve_usdc,
                    updated_at = excluded.updated_at
                """,
                (
                    float(values["entry_slippage_bps"]),
                    float(values["exit_slippage_bps"]),
                    float(values["fee_bps"]),
                    float(values["max_chase_bps"]),
                    str(values["copytrade_capital_mode"]),
                    float(values["min_cash_reserve_usdc"]),
                    now,
                ),
            )
        return self.get_execution_settings()

    def maybe_create_copy_order(self, trade: TraderActivity) -> dict[str, Any] | None:
        side = trade.side.upper()
        setting = self._get_enabled_setting(trade.proxy_wallet)
        if setting is None and side == "SELL":
            setting = self._get_setting(trade.proxy_wallet)
        if setting is None:
            return None

        requested_usdc = self._calculate_copy_size(
            source_usdc=trade.usdc_size,
            sizing_mode=str(setting["sizing_mode"]),
            size_value=Decimal(str(setting["size_value"])),
            max_usdc=Decimal(str(setting["max_usdc"])),
        )
        if requested_usdc <= 0 or trade.price <= 0:
            return None

        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            execution_settings = self._ensure_execution_settings(connection)
            entry_price = self._worse_entry_price(trade.price, execution_settings)
            simulated_size = requested_usdc / (entry_price if side != "SELL" else trade.price)
            entry_fee = self._fee_for_notional(requested_usdc, execution_settings)
            total_entry_cost = requested_usdc + entry_fee
            account = connection.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
            cash = Decimal(str(account["cash_balance"]))
            starting_balance = Decimal(str(account["starting_balance"]))
            active_cost = Decimal(
                str(
                    connection.execute(
                        "SELECT COALESCE(SUM(cost_usdc), 0) AS value FROM paper_positions WHERE status = 'OPEN'"
                    ).fetchone()["value"]
                    or 0
                )
            )
            if side != "SELL" and not self._within_max_chase(trade.price, entry_price, execution_settings):
                inserted = connection.execute(
                    """
                    INSERT OR IGNORE INTO paper_orders (
                        source_type, source_wallet, source_transaction_hash, strategy, side,
                        title, outcome, asset, condition_id, requested_usdc, simulated_size,
                        entry_price, status, reason, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        0,
                        float(entry_price),
                        "REJECTED_CHASE_LIMIT",
                        f"Observed {float(trade.price):.4f}, simulated entry {float(entry_price):.4f}, max chase {float(execution_settings['max_chase_bps']):.1f} bps",
                        now,
                    ),
                ).rowcount
                if not inserted:
                    return None
                return {
                    "sourceWallet": trade.proxy_wallet,
                    "sourceTransactionHash": trade.transaction_hash,
                    "requestedUsdc": float(requested_usdc),
                    "entryPrice": float(entry_price),
                    "observedPrice": float(trade.price),
                    "side": side,
                    "status": "REJECTED_CHASE_LIMIT",
                    "title": trade.title,
                    "outcome": trade.outcome,
                }

            if side != "SELL":
                spendable_cash = self._copytrade_spendable_cash(
                    cash=cash,
                    starting_balance=starting_balance,
                    active_cost=active_cost,
                    execution_settings=execution_settings,
                )
            else:
                spendable_cash = cash

            if side != "SELL" and total_entry_cost > spendable_cash:
                reason = self._copytrade_capital_rejection_reason(
                    requested_total=total_entry_cost,
                    spendable_cash=spendable_cash,
                    cash=cash,
                    starting_balance=starting_balance,
                    active_cost=active_cost,
                    execution_settings=execution_settings,
                )
                inserted = connection.execute(
                    """
                    INSERT OR IGNORE INTO paper_orders (
                        source_type, source_wallet, source_transaction_hash, strategy, side,
                        title, outcome, asset, condition_id, requested_usdc, simulated_size,
                        entry_price, status, reason, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        float(simulated_size),
                        float(entry_price),
                        "AUTOSTOPPED_LOW_BALANCE",
                        reason,
                        now,
                    ),
                ).rowcount
                self._disable_copytrade_for_low_balance(
                    connection=connection,
                    proxy_wallet=trade.proxy_wallet,
                    title=trade.title,
                    requested_usdc=total_entry_cost,
                    cash_balance=spendable_cash,
                    now=now,
                    reason=reason,
                )
                if not inserted:
                    return None
                return {
                    "sourceWallet": trade.proxy_wallet,
                    "sourceTransactionHash": trade.transaction_hash,
                    "requestedUsdc": float(total_entry_cost),
                    "availableCash": float(cash),
                    "side": side,
                    "status": "AUTOSTOPPED_LOW_BALANCE",
                    "title": trade.title,
                    "outcome": trade.outcome,
                }

            inserted = connection.execute(
                """
                INSERT OR IGNORE INTO paper_orders (
                    source_type, source_wallet, source_transaction_hash, strategy, side,
                    title, outcome, asset, condition_id, requested_usdc, simulated_size,
                    entry_price, status, reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    float(simulated_size),
                    float(entry_price),
                    "FILLED_PAPER",
                    f"Copied from saved trader public trade; observed {float(trade.price):.4f}, execution assumptions applied",
                    now,
                ),
            ).rowcount
            if inserted:
                order_id = connection.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
                if side == "SELL":
                    closed = self._close_copy_positions(
                        connection=connection,
                        source_wallet=trade.proxy_wallet,
                        asset=trade.asset,
                        condition_id=trade.condition_id,
                        outcome=trade.outcome,
                        observed_exit_price=trade.price,
                        exit_size=simulated_size,
                        closed_at=now,
                        close_reason=f"Copied SELL from saved trader tx {trade.transaction_hash}",
                        execution_settings=execution_settings,
                    )
                    if not closed["closedPositions"]:
                        connection.execute(
                            "UPDATE paper_orders SET status = 'NO_POSITION', reason = ? WHERE id = ?",
                            ("Copied SELL had no matching open paper position", order_id),
                        )
                else:
                    self._open_position(
                        connection=connection,
                        order_id=int(order_id),
                        source_type="COPYTRADE",
                        source_wallet=trade.proxy_wallet,
                        strategy="COPYTRADE",
                        side=side,
                        title=trade.title,
                        outcome=trade.outcome,
                        asset=trade.asset,
                        condition_id=trade.condition_id,
                        entry_price=entry_price,
                        observed_entry_price=trade.price,
                        size=simulated_size,
                        cost_usdc=total_entry_cost,
                        entry_fee_usdc=entry_fee,
                        opened_at=now,
                    )

        if not inserted:
            return None
        return {
            "sourceWallet": trade.proxy_wallet,
            "sourceTransactionHash": trade.transaction_hash,
            "requestedUsdc": float(total_entry_cost if side != "SELL" else requested_usdc),
            "simulatedSize": float(simulated_size),
            "entryPrice": float(entry_price),
            "observedPrice": float(trade.price),
            "entryFeeUsdc": float(entry_fee if side != "SELL" else Decimal("0")),
            "side": side,
            "status": "FILLED_PAPER",
            "title": trade.title,
            "outcome": trade.outcome,
        }

    def maybe_create_arbitrage_order(
        self,
        opportunity: BinaryArbitrageOpportunity,
        requested_usdc: Decimal = Decimal("10"),
    ) -> dict[str, Any] | None:
        if opportunity.net_profit_bps <= 0:
            return None

        entry_price = opportunity.net_cost_per_set
        if entry_price <= 0:
            return None

        simulated_sets = min(requested_usdc / entry_price, opportunity.max_size)
        if simulated_sets <= 0:
            return None

        source_hash = f"{opportunity.condition_id}:{opportunity.yes_price}:{opportunity.no_price}"
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            inserted = connection.execute(
                """
                INSERT OR IGNORE INTO paper_orders (
                    source_type, source_wallet, source_transaction_hash, strategy, side,
                    title, outcome, asset, condition_id, requested_usdc, simulated_size,
                    entry_price, status, reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "ARBITRAGE",
                    "",
                    source_hash,
                    "BINARY_ARB",
                    "BUY_SET",
                    opportunity.question,
                    "YES+NO",
                    "",
                    opportunity.condition_id,
                    float(requested_usdc),
                    float(simulated_sets),
                    float(entry_price),
                    "FILLED_PAPER",
                    "Paper-filled theoretical binary arbitrage set",
                    now,
                ),
            ).rowcount
            if inserted:
                order_id = connection.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
                self._open_position(
                    connection=connection,
                    order_id=int(order_id),
                    source_type="ARBITRAGE",
                    source_wallet="",
                    strategy="BINARY_ARB",
                    side="BUY_SET",
                    title=opportunity.question,
                    outcome="YES+NO",
                    asset="",
                    condition_id=opportunity.condition_id,
                    entry_price=entry_price,
                    observed_entry_price=entry_price,
                    size=simulated_sets,
                    cost_usdc=requested_usdc,
                    entry_fee_usdc=Decimal("0"),
                    opened_at=now,
                )

        if not inserted:
            return None
        return {
            "conditionId": opportunity.condition_id,
            "requestedUsdc": float(requested_usdc),
            "simulatedSets": float(simulated_sets),
            "entryPrice": float(entry_price),
            "netProfitBps": float(opportunity.net_profit_bps),
            "title": opportunity.question,
        }

    def list_orders(self, limit: int = 100) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM paper_orders
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_positions(self, status: str = "OPEN", limit: int = 100) -> list[dict[str, Any]]:
        status = status.upper()
        order_column = "closed_at" if status == "CLOSED" else "opened_at"
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM paper_positions
                WHERE status = ?
                ORDER BY {order_column} DESC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_positions(
        self,
        positions: list[dict[str, Any]],
        markets_by_condition_id: dict[str, dict[str, Any]],
        save_snapshots: bool = False,
    ) -> list[dict[str, Any]]:
        observed_at = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            execution_settings = self._ensure_execution_settings(connection)
        marked_positions = []
        for position in positions:
            marked = dict(position)
            mark_price = self._market_price_for_position(position=position, market=markets_by_condition_id.get(str(position["condition_id"])))
            if mark_price is None:
                mark_value = Decimal(str(position["cost_usdc"]))
                unrealized_pnl = Decimal("0")
            else:
                liquidation_price = self._worse_exit_price(mark_price, execution_settings)
                gross_mark_value = Decimal(str(position["size"])) * liquidation_price
                mark_value = max(Decimal("0"), gross_mark_value - self._fee_for_notional(gross_mark_value, execution_settings))
                unrealized_pnl = mark_value - Decimal(str(position["cost_usdc"]))

            marked.update(
                {
                    "mark_price": float(mark_price) if mark_price is not None else None,
                    "mark_value_usdc": float(mark_value),
                    "unrealized_pnl_usdc": float(unrealized_pnl),
                }
            )
            marked_positions.append(marked)
        if save_snapshots:
            self.save_mark_snapshots(marked_positions, observed_at=observed_at)
        return marked_positions

    def save_mark_snapshots(self, positions: list[dict[str, Any]], observed_at: str | None = None) -> None:
        if not positions:
            return
        observed_at = observed_at or datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            for position in positions:
                connection.execute(
                    """
                    INSERT INTO paper_mark_snapshots (
                        position_id, observed_at, mark_price, mark_value_usdc, unrealized_pnl_usdc
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        int(position["id"]),
                        observed_at,
                        position.get("mark_price"),
                        float(position.get("mark_value_usdc") or 0),
                        float(position.get("unrealized_pnl_usdc") or 0),
                    ),
                )

    def attach_mark_history(self, positions: list[dict[str, Any]], limit_per_position: int = 200) -> list[dict[str, Any]]:
        if not positions:
            return positions
        ids = [int(position["id"]) for position in positions]
        placeholders = ",".join("?" for _ in ids)
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM paper_mark_snapshots
                WHERE position_id IN ({placeholders})
                ORDER BY observed_at ASC
                """,
                ids,
            ).fetchall()

        history_by_id: dict[int, list[dict[str, Any]]] = {}
        for row in rows:
            position_id = int(row["position_id"])
            history_by_id.setdefault(position_id, []).append(dict(row))

        enriched = []
        for position in positions:
            history = history_by_id.get(int(position["id"]), [])
            if limit_per_position > 0:
                history = history[-limit_per_position:]
            item = dict(position)
            item["mark_history"] = history
            enriched.append(item)
        return enriched

    def list_paper_events(self, limit: int = 50) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM paper_events
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_account_snapshot(self, account: dict[str, Any], observed_at: str | None = None) -> None:
        observed_at = observed_at or datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO paper_account_snapshots (
                    observed_at, cash_balance, active_cost, open_market_value,
                    realized_pnl, unrealized_pnl, running_pnl, equity_estimate
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observed_at,
                    float(account.get("cashBalance") or 0),
                    float(account.get("activeCost") or 0),
                    float(account.get("openMarketValue") or account.get("activeCost") or 0),
                    float(account.get("realizedPnl") or 0),
                    float(account.get("unrealizedPnl") or 0),
                    float(account.get("runningPnl") or account.get("realizedPnl") or 0),
                    float(account.get("equityEstimate") or 0),
                ),
            )

    def list_account_snapshots(self, limit: int = 500) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM (
                    SELECT *
                    FROM paper_account_snapshots
                    ORDER BY observed_at DESC
                    LIMIT ?
                )
                ORDER BY observed_at ASC
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _disable_copytrade_for_low_balance(
        self,
        connection,
        proxy_wallet: str,
        title: str,
        requested_usdc: Decimal,
        cash_balance: Decimal,
        now: str,
        reason: str | None = None,
    ) -> None:
        connection.execute(
            """
            UPDATE copytrade_settings
            SET enabled = 0,
                updated_at = ?
            WHERE lower(proxy_wallet) = lower(?)
            """,
            (now, proxy_wallet),
        )
        message = reason or (
            f"Copytrade autostopped for {proxy_wallet}: needed ${float(requested_usdc):.2f}, "
            f"available ${float(cash_balance):.2f}."
        )
        connection.execute(
            """
            INSERT INTO paper_events (event_type, proxy_wallet, title, message, created_at)
            VALUES ('COPYTRADE_AUTOSTOP_LOW_BALANCE', ?, ?, ?, ?)
            """,
            (proxy_wallet, title, message, now),
        )

    def list_open_condition_ids(self) -> list[str]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT condition_id
                FROM paper_positions
                WHERE status = 'OPEN' AND condition_id != ''
                ORDER BY condition_id
                """
            ).fetchall()
        return [str(row["condition_id"]) for row in rows]

    def enforce_cash_reserve(self, markets_by_condition_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        closed_positions = []
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            execution_settings = self._ensure_execution_settings(connection)
            reserve = execution_settings["min_cash_reserve_usdc"]
            account = connection.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
            cash = Decimal(str(account["cash_balance"]))
            if cash >= reserve:
                return {
                    "enforced": True,
                    "closedPositions": [],
                    "closedPositionCount": 0,
                    "cashBalance": float(cash),
                    "minCashReserveUsdc": float(reserve),
                    "remainingShortfall": 0.0,
                    "enforcedAt": now,
                }

            rows = connection.execute(
                """
                SELECT *
                FROM paper_positions
                WHERE status = 'OPEN'
                ORDER BY opened_at ASC, id ASC
                """
            ).fetchall()
            candidates = []
            for row in rows:
                position = dict(row)
                mark_price = self._market_price_for_position(
                    position=position,
                    market=markets_by_condition_id.get(str(position["condition_id"])),
                )
                exit_price = mark_price if mark_price is not None else Decimal(str(position["entry_price"]))
                liquidation_price = self._worse_exit_price(exit_price, execution_settings)
                gross_exit_value = Decimal(str(position["size"])) * liquidation_price
                exit_value = max(Decimal("0"), gross_exit_value - self._fee_for_notional(gross_exit_value, execution_settings))
                unrealized_pnl = exit_value - Decimal(str(position["cost_usdc"]))
                candidates.append((unrealized_pnl, str(position["opened_at"]), int(position["id"]), position, exit_price, exit_value))

            candidates.sort(key=lambda item: (item[0], item[1], item[2]))
            for _, _, _, position, exit_price, expected_exit_value in candidates:
                if cash >= reserve:
                    break
                if expected_exit_value <= 0:
                    continue
                pnl = self._close_full_position(
                    connection=connection,
                    position=position,
                    observed_exit_price=exit_price,
                    closed_at=now,
                    close_reason="Auto-closed to restore minimum paper cash reserve",
                    apply_execution_settings=True,
                )
                cash += expected_exit_value
                closed_positions.append(
                    {
                        "positionId": int(position["id"]),
                        "title": str(position["title"]),
                        "outcome": str(position["outcome"]),
                        "exitPrice": float(exit_price),
                        "exitValueUsdc": float(expected_exit_value),
                        "pnlUsdc": float(pnl),
                    }
                )

            if closed_positions:
                connection.execute(
                    """
                    INSERT INTO paper_events (event_type, message, created_at)
                    VALUES ('CASH_RESERVE_AUTO_CLOSE', ?, ?)
                    """,
                    (
                        f"Auto-closed {len(closed_positions)} paper position(s) to restore minimum cash reserve ${float(reserve):.2f}.",
                        now,
                    ),
                )

        remaining_shortfall = max(Decimal("0"), reserve - cash)
        return {
            "enforced": True,
            "closedPositions": closed_positions,
            "closedPositionCount": len(closed_positions),
            "cashBalance": float(cash),
            "minCashReserveUsdc": float(reserve),
            "remainingShortfall": float(remaining_shortfall),
            "enforcedAt": now,
        }

    def reconcile_settled_positions(self, markets_by_condition_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        settled_positions = 0
        skipped_positions = 0
        realized_pnl = Decimal("0")

        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            rows = connection.execute(
                """
                SELECT *
                FROM paper_positions
                WHERE status = 'OPEN' AND condition_id != ''
                ORDER BY opened_at ASC, id ASC
                """
            ).fetchall()

            for position in rows:
                market = markets_by_condition_id.get(str(position["condition_id"]))
                settlement_price = self._settlement_price_for_position(position=dict(position), market=market)
                if settlement_price is None:
                    skipped_positions += 1
                    continue

                pnl = self._close_full_position(
                    connection=connection,
                    position=dict(position),
                    observed_exit_price=settlement_price,
                    closed_at=now,
                    close_reason="Settled from resolved Polymarket market",
                    apply_execution_settings=False,
                )
                realized_pnl += pnl
                settled_positions += 1

        return {
            "settledPositions": settled_positions,
            "skippedPositions": skipped_positions,
            "realizedPnl": float(realized_pnl),
            "checkedMarkets": len(markets_by_condition_id),
            "reconciledAt": now,
        }

    def reconcile_closed_copy_positions(self, closed_positions: list[ClosedPosition]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        closed_by_key = {
            (item.proxy_wallet.lower(), item.condition_id, item.outcome): item
            for item in closed_positions
            if item.total_bought > 0
        }
        closed_count = 0
        skipped_count = 0
        realized_pnl = Decimal("0")

        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            rows = connection.execute(
                """
                SELECT *
                FROM paper_positions
                WHERE status = 'OPEN'
                  AND source_type = 'COPYTRADE'
                  AND condition_id != ''
                ORDER BY opened_at ASC, id ASC
                """
            ).fetchall()

            for position in rows:
                key = (
                    str(position["source_wallet"]).lower(),
                    str(position["condition_id"]),
                    str(position["outcome"]),
                )
                closed_position = closed_by_key.get(key)
                if closed_position is None:
                    skipped_count += 1
                    continue

                exit_price = closed_position.avg_price + (closed_position.realized_pnl / closed_position.total_bought)
                exit_price = min(Decimal("1"), max(Decimal("0"), exit_price))
                pnl = self._close_full_position(
                    connection=connection,
                    position=dict(position),
                    observed_exit_price=exit_price,
                    closed_at=now,
                    close_reason="Reconciled from saved trader closed position",
                    apply_execution_settings=True,
                )
                realized_pnl += pnl
                closed_count += 1

        return {
            "closedCopyPositions": closed_count,
            "skippedCopyPositions": skipped_count,
            "realizedPnl": float(realized_pnl),
            "closedPositionSignals": len(closed_by_key),
            "reconciledAt": now,
        }

    def close_position(
        self,
        position_id: int,
        exit_price: Decimal,
        close_reason: str = "Manual close",
    ) -> dict[str, Any]:
        if exit_price < 0:
            raise ValueError("Exit price cannot be negative")

        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            self._ensure_account(connection)
            position = connection.execute(
                "SELECT * FROM paper_positions WHERE id = ? AND status = 'OPEN'",
                (position_id,),
            ).fetchone()
            if position is None:
                return {"closed": False, "reason": "Position not found or already closed"}

            pnl = self._close_full_position(
                connection=connection,
                position=dict(position),
                observed_exit_price=exit_price,
                closed_at=now,
                close_reason=close_reason,
                apply_execution_settings=True,
            )
            execution_settings = self._ensure_execution_settings(connection)
            gross_exit_value = Decimal(str(position["size"])) * self._worse_exit_price(exit_price, execution_settings)
            exit_value = max(Decimal("0"), gross_exit_value - self._fee_for_notional(gross_exit_value, execution_settings))
        return {"closed": True, "positionId": position_id, "exitValueUsdc": float(exit_value), "pnlUsdc": float(pnl)}

    def _get_enabled_setting(self, proxy_wallet: str) -> dict[str, Any] | None:
        with connect_database(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM copytrade_settings
                WHERE lower(proxy_wallet) = lower(?) AND enabled = 1
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (proxy_wallet,),
            ).fetchone()
        return dict(row) if row else None

    def _get_setting(self, proxy_wallet: str) -> dict[str, Any] | None:
        with connect_database(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM copytrade_settings
                WHERE lower(proxy_wallet) = lower(?)
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (proxy_wallet,),
            ).fetchone()
        return dict(row) if row else None

    def _calculate_copy_size(
        self,
        source_usdc: Decimal,
        sizing_mode: str,
        size_value: Decimal,
        max_usdc: Decimal,
    ) -> Decimal:
        if sizing_mode == "FIXED":
            requested = size_value
        else:
            requested = source_usdc * (size_value / Decimal("100"))
        return min(requested, max_usdc)

    def _close_copy_positions(
        self,
        connection,
        source_wallet: str,
        asset: str,
        condition_id: str,
        outcome: str,
        observed_exit_price: Decimal,
        exit_size: Decimal,
        closed_at: str,
        close_reason: str,
        execution_settings: dict[str, Decimal],
    ) -> dict[str, Any]:
        remaining_size = exit_size
        closed_positions = []
        exit_price = self._worse_exit_price(observed_exit_price, execution_settings)
        rows = connection.execute(
            """
            SELECT *
            FROM paper_positions
            WHERE status = 'OPEN'
              AND source_type = 'COPYTRADE'
              AND source_wallet = ?
              AND asset = ?
              AND condition_id = ?
              AND outcome = ?
            ORDER BY opened_at ASC, id ASC
            """,
            (source_wallet, asset, condition_id, outcome),
        ).fetchall()

        for position in rows:
            if remaining_size <= 0:
                break

            position_size = Decimal(str(position["size"]))
            position_cost = Decimal(str(position["cost_usdc"]))
            close_size = min(position_size, remaining_size)
            close_ratio = close_size / position_size
            close_cost = position_cost * close_ratio
            gross_exit_value = close_size * exit_price
            exit_fee = self._fee_for_notional(gross_exit_value, execution_settings)
            exit_value = max(Decimal("0"), gross_exit_value - exit_fee)
            pnl = exit_value - close_cost

            if close_size == position_size:
                connection.execute(
                    """
                    UPDATE paper_positions
                    SET status = 'CLOSED',
                        closed_at = ?,
                        exit_price = ?,
                        observed_exit_price = ?,
                        exit_value_usdc = ?,
                        pnl_usdc = ?,
                        exit_fee_usdc = ?,
                        close_reason = ?
                    WHERE id = ?
                    """,
                    (
                        closed_at,
                        float(exit_price),
                        float(observed_exit_price),
                        float(exit_value),
                        float(pnl),
                        float(exit_fee),
                        close_reason,
                        int(position["id"]),
                    ),
                )
                closed_id = int(position["id"])
            else:
                remaining_position_size = position_size - close_size
                remaining_cost = position_cost - close_cost
                connection.execute(
                    """
                    UPDATE paper_positions
                    SET size = ?,
                        cost_usdc = ?
                    WHERE id = ?
                    """,
                    (float(remaining_position_size), float(remaining_cost), int(position["id"])),
                )
                closed_id = connection.execute(
                    """
                    INSERT INTO paper_positions (
                        order_id, source_type, source_wallet, strategy, side, title, outcome, asset,
                        condition_id, entry_price, size, cost_usdc, status, opened_at,
                        closed_at, exit_price, observed_exit_price, exit_value_usdc,
                        pnl_usdc, exit_fee_usdc, close_reason
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CLOSED', ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(position["order_id"]),
                        str(position["source_type"]),
                        str(position["source_wallet"]),
                        str(position["strategy"]),
                        str(position["side"]),
                        str(position["title"]),
                        str(position["outcome"]),
                        str(position["asset"]),
                        str(position["condition_id"]),
                        float(position["entry_price"]),
                        float(close_size),
                        float(close_cost),
                        str(position["opened_at"]),
                        closed_at,
                        float(exit_price),
                        float(observed_exit_price),
                        float(exit_value),
                        float(pnl),
                        float(exit_fee),
                        close_reason,
                    ),
                ).lastrowid

            connection.execute(
                """
                UPDATE paper_account
                SET cash_balance = cash_balance + ?,
                    updated_at = ?
                WHERE id = 1
                """,
                (float(exit_value), closed_at),
            )
            closed_positions.append(
                {
                    "positionId": closed_id,
                    "closedSize": float(close_size),
                    "exitValueUsdc": float(exit_value),
                    "pnlUsdc": float(pnl),
                }
            )
            remaining_size -= close_size

        return {
            "closedPositions": closed_positions,
            "unmatchedSize": float(max(Decimal("0"), remaining_size)),
        }

    def _close_full_position(
        self,
        connection,
        position: dict[str, Any],
        observed_exit_price: Decimal,
        closed_at: str,
        close_reason: str,
        apply_execution_settings: bool = True,
    ) -> Decimal:
        size = Decimal(str(position["size"]))
        cost = Decimal(str(position["cost_usdc"]))
        if apply_execution_settings:
            execution_settings = self._ensure_execution_settings(connection)
            exit_price = self._worse_exit_price(observed_exit_price, execution_settings)
            gross_exit_value = size * exit_price
            exit_fee = self._fee_for_notional(gross_exit_value, execution_settings)
            exit_value = max(Decimal("0"), gross_exit_value - exit_fee)
        else:
            exit_price = observed_exit_price
            exit_fee = Decimal("0")
            exit_value = size * exit_price
        pnl = exit_value - cost
        connection.execute(
            """
            UPDATE paper_positions
            SET status = 'CLOSED',
                closed_at = ?,
                exit_price = ?,
                observed_exit_price = ?,
                exit_value_usdc = ?,
                pnl_usdc = ?,
                exit_fee_usdc = ?,
                close_reason = ?
            WHERE id = ?
            """,
            (
                closed_at,
                float(exit_price),
                float(observed_exit_price),
                float(exit_value),
                float(pnl),
                float(exit_fee),
                close_reason,
                int(position["id"]),
            ),
        )
        connection.execute(
            """
            UPDATE paper_account
            SET cash_balance = cash_balance + ?,
                updated_at = ?
            WHERE id = 1
            """,
            (float(exit_value), closed_at),
        )
        return pnl

    def _settlement_price_for_position(
        self,
        position: dict[str, Any],
        market: dict[str, Any] | None,
    ) -> Decimal | None:
        if not market or market.get("closed") is not True:
            return None

        outcomes = self._parse_json_list(market.get("outcomes"))
        outcome_prices = [Decimal(str(item)) for item in self._parse_json_list(market.get("outcomePrices"))]
        token_ids = self._parse_json_list(market.get("clobTokenIds"))
        if not outcome_prices or len(outcome_prices) != len(token_ids):
            return None

        asset = str(position.get("asset") or "")
        outcome = str(position.get("outcome") or "")
        settlement_price: Decimal | None = None
        if asset in token_ids:
            settlement_price = outcome_prices[token_ids.index(asset)]
        elif outcome in outcomes and len(outcomes) == len(outcome_prices):
            settlement_price = outcome_prices[outcomes.index(outcome)]

        if settlement_price is None:
            return None
        if settlement_price >= Decimal("0.99"):
            return Decimal("1")
        if settlement_price <= Decimal("0.01"):
            return Decimal("0")
        return None

    def _market_price_for_position(
        self,
        position: dict[str, Any],
        market: dict[str, Any] | None,
    ) -> Decimal | None:
        if not market:
            return None

        outcomes = self._parse_json_list(market.get("outcomes"))
        outcome_prices = [Decimal(str(item)) for item in self._parse_json_list(market.get("outcomePrices"))]
        token_ids = self._parse_json_list(market.get("clobTokenIds"))
        if not outcome_prices:
            return None

        asset = str(position.get("asset") or "")
        outcome = str(position.get("outcome") or "")
        if asset in token_ids and len(outcome_prices) == len(token_ids):
            return outcome_prices[token_ids.index(asset)]
        if outcome in outcomes and len(outcome_prices) == len(outcomes):
            return outcome_prices[outcomes.index(outcome)]
        return None

    def _parse_json_list(self, raw: Any) -> list[str]:
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

    @staticmethod
    def _clamp_bps(value: Decimal) -> Decimal:
        return min(Decimal("10000"), max(Decimal("0"), value))

    @staticmethod
    def _execution_settings_payload(settings: dict[str, Decimal]) -> dict[str, Any]:
        return {
            "entrySlippageBps": float(settings["entry_slippage_bps"]),
            "exitSlippageBps": float(settings["exit_slippage_bps"]),
            "feeBps": float(settings["fee_bps"]),
            "maxChaseBps": float(settings["max_chase_bps"]),
            "copytradeCapitalMode": str(settings["copytrade_capital_mode"]),
            "minCashReserveUsdc": float(settings["min_cash_reserve_usdc"]),
        }

    def _ensure_execution_settings(self, connection) -> dict[str, Decimal]:
        now = datetime.now(UTC).isoformat()
        connection.execute(
            """
            INSERT OR IGNORE INTO paper_execution_settings (
                id, entry_slippage_bps, exit_slippage_bps, fee_bps, max_chase_bps,
                copytrade_capital_mode, min_cash_reserve_usdc, updated_at
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                float(DEFAULT_EXECUTION_SETTINGS["entry_slippage_bps"]),
                float(DEFAULT_EXECUTION_SETTINGS["exit_slippage_bps"]),
                float(DEFAULT_EXECUTION_SETTINGS["fee_bps"]),
                float(DEFAULT_EXECUTION_SETTINGS["max_chase_bps"]),
                str(DEFAULT_EXECUTION_SETTINGS["copytrade_capital_mode"]),
                float(DEFAULT_EXECUTION_SETTINGS["min_cash_reserve_usdc"]),
                now,
            ),
        )
        row = connection.execute("SELECT * FROM paper_execution_settings WHERE id = 1").fetchone()
        return {
            "entry_slippage_bps": Decimal(str(row["entry_slippage_bps"])),
            "exit_slippage_bps": Decimal(str(row["exit_slippage_bps"])),
            "fee_bps": Decimal(str(row["fee_bps"])),
            "max_chase_bps": Decimal(str(row["max_chase_bps"])),
            "copytrade_capital_mode": str(row["copytrade_capital_mode"] or "CONSERVATIVE").upper(),
            "min_cash_reserve_usdc": Decimal(str(row["min_cash_reserve_usdc"] or 0)),
        }

    @staticmethod
    def _worse_entry_price(observed_price: Decimal, execution_settings: dict[str, Decimal]) -> Decimal:
        multiplier = Decimal("1") + (execution_settings["entry_slippage_bps"] / Decimal("10000"))
        return min(Decimal("1"), max(Decimal("0"), observed_price * multiplier))

    @staticmethod
    def _worse_exit_price(observed_price: Decimal, execution_settings: dict[str, Decimal]) -> Decimal:
        multiplier = Decimal("1") - (execution_settings["exit_slippage_bps"] / Decimal("10000"))
        return min(Decimal("1"), max(Decimal("0"), observed_price * multiplier))

    @staticmethod
    def _fee_for_notional(notional: Decimal, execution_settings: dict[str, Decimal]) -> Decimal:
        return max(Decimal("0"), notional) * (execution_settings["fee_bps"] / Decimal("10000"))

    @staticmethod
    def _within_max_chase(
        observed_price: Decimal,
        entry_price: Decimal,
        execution_settings: dict[str, Decimal],
    ) -> bool:
        if observed_price <= 0:
            return False
        chase_bps = ((entry_price - observed_price) / observed_price) * Decimal("10000")
        return chase_bps <= execution_settings["max_chase_bps"]

    @staticmethod
    def _copytrade_spendable_cash(
        cash: Decimal,
        starting_balance: Decimal,
        active_cost: Decimal,
        execution_settings: dict[str, Decimal],
    ) -> Decimal:
        after_reserve_cash = max(Decimal("0"), cash - execution_settings["min_cash_reserve_usdc"])
        if execution_settings["copytrade_capital_mode"] == "AGGRESSIVE":
            return after_reserve_cash
        remaining_starting_capital = max(Decimal("0"), starting_balance - active_cost)
        return min(after_reserve_cash, remaining_starting_capital)

    @staticmethod
    def _copytrade_capital_rejection_reason(
        requested_total: Decimal,
        spendable_cash: Decimal,
        cash: Decimal,
        starting_balance: Decimal,
        active_cost: Decimal,
        execution_settings: dict[str, Decimal],
    ) -> str:
        mode = str(execution_settings["copytrade_capital_mode"]).lower()
        reserve = execution_settings["min_cash_reserve_usdc"]
        return (
            f"Copytrade autostopped: needed ${float(requested_total):.2f}, "
            f"spendable ${float(spendable_cash):.2f}. Mode {mode}, "
            f"cash ${float(cash):.2f}, reserve ${float(reserve):.2f}, "
            f"starting balance ${float(starting_balance):.2f}, active cost ${float(active_cost):.2f}."
        )

    def _ensure_account(self, connection) -> None:
        now = datetime.now(UTC).isoformat()
        connection.execute(
            """
            INSERT OR IGNORE INTO paper_account (id, starting_balance, cash_balance, updated_at)
            VALUES (1, 1000, 1000, ?)
            """,
            (now,),
        )

    def _open_position(
        self,
        connection,
        order_id: int,
        source_type: str,
        source_wallet: str,
        strategy: str,
        side: str,
        title: str,
        outcome: str,
        asset: str,
        condition_id: str,
        entry_price: Decimal,
        observed_entry_price: Decimal,
        size: Decimal,
        cost_usdc: Decimal,
        entry_fee_usdc: Decimal,
        opened_at: str,
    ) -> None:
        cash = Decimal(str(connection.execute("SELECT cash_balance FROM paper_account WHERE id = 1").fetchone()[0]))
        if cash < cost_usdc:
            connection.execute(
                "UPDATE paper_orders SET status = 'REJECTED_PAPER', reason = ? WHERE id = ?",
                ("Insufficient paper cash balance", order_id),
            )
            return

        connection.execute(
            """
            UPDATE paper_account
            SET cash_balance = cash_balance - ?,
                updated_at = ?
            WHERE id = 1
            """,
            (float(cost_usdc), opened_at),
        )
        connection.execute(
            """
            INSERT INTO paper_positions (
                order_id, source_type, source_wallet, strategy, side, title, outcome, asset,
                condition_id, entry_price, observed_entry_price, size, cost_usdc,
                entry_fee_usdc, status, opened_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
            """,
            (
                order_id,
                source_type,
                source_wallet,
                strategy,
                side,
                title,
                outcome,
                asset,
                condition_id,
                float(entry_price),
                float(observed_entry_price),
                float(size),
                float(cost_usdc),
                float(entry_fee_usdc),
                opened_at,
            ),
        )
