from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from src.models import SmartWallet
from src.paper_trading import PaperTrading
from src.live_trading import LiveTrading
from src.polymarket_client import PolymarketClient
from src.smart_wallet_tracker import SmartWalletTracker
from src.storage import connect_database


class Watchlist:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def save_wallet(
        self,
        proxy_wallet: str,
        label: str = "",
        notes: str = "",
        username: str = "",
        x_username: str = "",
        profile_image: str = "",
        verified_badge: bool = False,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with connect_database(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO wallets (
                    proxy_wallet, username, x_username, verified_badge, profile_image, first_seen_at, last_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(proxy_wallet) DO UPDATE SET
                    username = CASE WHEN excluded.username != '' THEN excluded.username ELSE wallets.username END,
                    x_username = CASE WHEN excluded.x_username != '' THEN excluded.x_username ELSE wallets.x_username END,
                    verified_badge = CASE WHEN excluded.verified_badge != 0 THEN excluded.verified_badge ELSE wallets.verified_badge END,
                    profile_image = CASE WHEN excluded.profile_image != '' THEN excluded.profile_image ELSE wallets.profile_image END,
                    last_seen_at = excluded.last_seen_at
                """,
                (
                    proxy_wallet,
                    username,
                    x_username,
                    int(verified_badge),
                    profile_image,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO watchlist (proxy_wallet, label, notes, added_at, alerts_enabled)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(proxy_wallet) DO UPDATE SET
                    label = excluded.label,
                    notes = excluded.notes
                """,
                (proxy_wallet, label, notes, now),
            )

        return {"proxyWallet": proxy_wallet, "saved": True}

    def remove_wallet(self, proxy_wallet: str) -> dict[str, Any]:
        with connect_database(self.database_path) as connection:
            connection.execute("DELETE FROM watchlist WHERE proxy_wallet = ?", (proxy_wallet,))
            connection.execute("DELETE FROM watchlist_alerts WHERE proxy_wallet = ?", (proxy_wallet,))
        return {"proxyWallet": proxy_wallet, "saved": False}

    def set_alerts_enabled(self, proxy_wallet: str, enabled: bool) -> dict[str, Any]:
        with connect_database(self.database_path) as connection:
            connection.execute(
                "UPDATE watchlist SET alerts_enabled = ? WHERE proxy_wallet = ?",
                (1 if enabled else 0, proxy_wallet),
            )
        return {"proxyWallet": proxy_wallet, "alertsEnabled": enabled}

    def list_wallets(self, smart_tracker: SmartWalletTracker) -> list[dict[str, Any]]:
        smart_wallets = {
            wallet.proxy_wallet.lower(): wallet
            for wallet in smart_tracker.get_ranked_wallets(
                limit=500,
                min_trades=0,
                min_closed_positions=0,
                min_win_rate=Decimal("0"),
                min_average_markout=Decimal("-1"),
                category=None,
                time_period=None,
            )
        }

        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    wl.proxy_wallet,
                    wl.label,
                    wl.notes,
                    wl.added_at,
                    wl.alerts_enabled,
                    w.username,
                    w.x_username,
                    w.verified_badge,
                    w.profile_image
                FROM watchlist wl
                LEFT JOIN wallets w ON w.proxy_wallet = wl.proxy_wallet
                ORDER BY wl.added_at DESC
                """
            ).fetchall()

        saved = []
        for row in rows:
            proxy_wallet = str(row["proxy_wallet"])
            smart_wallet = smart_wallets.get(proxy_wallet.lower())
            saved.append(
                {
                    "proxy_wallet": proxy_wallet,
                    "label": str(row["label"] or ""),
                    "notes": str(row["notes"] or ""),
                    "added_at": str(row["added_at"] or ""),
                    "alerts_enabled": bool(row["alerts_enabled"]),
                    "username": str(row["username"] or proxy_wallet),
                    "x_username": str(row["x_username"] or ""),
                    "verified_badge": bool(row["verified_badge"]),
                    "profile_image": str(row["profile_image"] or ""),
                    "smart_wallet": asdict(smart_wallet) if smart_wallet else None,
                }
            )
        return saved

    def list_wallets_basic(self) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    wl.proxy_wallet,
                    wl.label,
                    wl.notes,
                    wl.added_at,
                    wl.alerts_enabled,
                    w.username,
                    w.x_username,
                    w.verified_badge,
                    w.profile_image
                FROM watchlist wl
                LEFT JOIN wallets w ON w.proxy_wallet = wl.proxy_wallet
                ORDER BY wl.added_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def refresh_saved_wallet_trades(
        self,
        client: PolymarketClient,
        trades_per_wallet: int,
        paper_trading: PaperTrading | None = None,
        live_trading: LiveTrading | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        wallets = self._get_alert_enabled_wallets()
        trades_seen = 0
        new_alerts = 0
        paper_orders_created = 0
        copytrade_autostops = 0
        live_orders_created = 0
        live_copytrade_autostops = 0
        copytrade_candidates = []

        with connect_database(self.database_path) as connection:
            for wallet in wallets:
                trades = client.get_user_trade_activity(user=wallet, limit=trades_per_wallet)
                for trade in trades:
                    existed = connection.execute(
                        "SELECT 1 FROM trades WHERE transaction_hash = ?",
                        (trade.transaction_hash,),
                    ).fetchone()
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO trades (
                            transaction_hash, proxy_wallet, timestamp, condition_id, side, outcome, title,
                            slug, asset, size, usdc_size, price, first_seen_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            trade.transaction_hash,
                            trade.proxy_wallet,
                            trade.timestamp,
                            trade.condition_id,
                            trade.side,
                            trade.outcome,
                            trade.title,
                            trade.slug,
                            trade.asset,
                            float(trade.size),
                            float(trade.usdc_size),
                            float(trade.price),
                            now,
                        ),
                    )
                    trades_seen += 1
                    if existed:
                        continue

                    inserted = connection.execute(
                        """
                        INSERT OR IGNORE INTO watchlist_alerts (
                            proxy_wallet, transaction_hash, alert_type, title, outcome, side,
                            price, usdc_size, trade_timestamp, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            trade.proxy_wallet,
                            trade.transaction_hash,
                            "NEW_TRADE",
                            trade.title,
                            trade.outcome,
                            trade.side,
                            float(trade.price),
                            float(trade.usdc_size),
                            trade.timestamp,
                            now,
                        ),
                    ).rowcount
                    new_alerts += inserted
                    if inserted and paper_trading is not None:
                        copytrade_candidates.append(trade)

        if paper_trading is not None:
            for trade in sorted(copytrade_candidates, key=lambda item: (item.timestamp, item.transaction_hash)):
                paper_order = paper_trading.maybe_create_copy_order(trade)
                if paper_order is not None:
                    if paper_order.get("status") == "AUTOSTOPPED_LOW_BALANCE":
                        copytrade_autostops += 1
                    elif paper_order.get("status") == "FILLED_PAPER":
                        paper_orders_created += 1
        if live_trading is not None:
            for trade in sorted(copytrade_candidates, key=lambda item: (item.timestamp, item.transaction_hash)):
                live_order = live_trading.maybe_create_copy_order(trade)
                if live_order is not None:
                    if live_order.get("status") == "AUTOSTOPPED_LOW_BALANCE":
                        live_copytrade_autostops += 1
                    elif live_order.get("status") == "SUBMITTED_LIVE":
                        live_orders_created += 1

        return {
            "walletsChecked": len(wallets),
            "tradesSeen": trades_seen,
            "newAlerts": new_alerts,
            "paperOrdersCreated": paper_orders_created,
            "copytradeAutostops": copytrade_autostops,
            "liveOrdersCreated": live_orders_created,
            "liveCopytradeAutostops": live_copytrade_autostops,
            "refreshedAt": now,
        }

    def list_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    a.*,
                    COALESCE(w.username, a.proxy_wallet) AS username
                FROM watchlist_alerts a
                JOIN watchlist wl ON wl.proxy_wallet = a.proxy_wallet
                LEFT JOIN wallets w ON w.proxy_wallet = a.proxy_wallet
                ORDER BY a.created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_saved_wallet_addresses(self) -> list[str]:
        return self._get_saved_wallets()

    def _get_saved_wallets(self) -> list[str]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute("SELECT proxy_wallet FROM watchlist ORDER BY added_at DESC").fetchall()
        return [str(row["proxy_wallet"]) for row in rows]

    def _get_alert_enabled_wallets(self) -> list[str]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                "SELECT proxy_wallet FROM watchlist WHERE alerts_enabled = 1 ORDER BY added_at DESC"
            ).fetchall()
        return [str(row["proxy_wallet"]) for row in rows]
