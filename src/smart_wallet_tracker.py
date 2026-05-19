from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import requests

from src.models import ClosedPosition, OrderBook, SmartWallet, TraderActivity, TraderProfile
from src.polymarket_client import PolymarketClient
from src.storage import connect_database


class SmartWalletTracker:
    def __init__(self, client: PolymarketClient, database_path: str) -> None:
        self.client = client
        self.database_path = database_path

    def ingest_candidates(
        self,
        category: str,
        time_period: str,
        order_by: str,
        candidate_limit: int,
        trades_per_wallet: int,
        closed_positions_per_wallet: int,
        markout_trades_per_wallet: int,
    ) -> dict[str, Any]:
        started_at = datetime.now(UTC)
        candidates = self.client.get_leaderboard(
            category=category,
            time_period=time_period,
            order_by=order_by,
            limit=candidate_limit,
        )

        wallets_seen = 0
        trades_seen = 0
        positions_seen = 0
        markouts_seen = 0

        with connect_database(self.database_path) as connection:
            for candidate in candidates:
                wallets_seen += 1
                self._upsert_wallet(connection, candidate, started_at.isoformat())
                self._insert_leaderboard_snapshot(
                    connection=connection,
                    candidate=candidate,
                    category=category,
                    time_period=time_period,
                    order_by=order_by,
                    observed_at=started_at.isoformat(),
                )

                try:
                    trades = self.client.get_user_trade_activity(
                        user=candidate.proxy_wallet,
                        limit=trades_per_wallet,
                    )
                except requests.RequestException:
                    trades = []

                for trade in trades:
                    self._upsert_trade(connection, trade, started_at.isoformat())
                trades_seen += len(trades)

                try:
                    positions = self.client.get_user_closed_positions(
                        user=candidate.proxy_wallet,
                        limit=closed_positions_per_wallet,
                    )
                except requests.RequestException:
                    positions = []

                for position in positions:
                    self._upsert_closed_position(connection, position, started_at.isoformat())
                positions_seen += len(positions)

                for trade in trades[:markout_trades_per_wallet]:
                    markout = self._calculate_trade_markout(trade)
                    if markout is None:
                        continue
                    self._insert_markout(
                        connection=connection,
                        transaction_hash=trade.transaction_hash,
                        observed_at=started_at.isoformat(),
                        current_mid=markout["current_mid"],
                        markout=markout["markout"],
                    )
                    markouts_seen += 1

        finished_at = datetime.now(UTC)
        return {
            "startedAt": started_at.isoformat(),
            "finishedAt": finished_at.isoformat(),
            "durationSeconds": round((finished_at - started_at).total_seconds(), 3),
            "walletsSeen": wallets_seen,
            "tradesSeen": trades_seen,
            "closedPositionsSeen": positions_seen,
            "markoutsSeen": markouts_seen,
        }

    def get_ranked_wallets(
        self,
        limit: int,
        min_trades: int,
        min_closed_positions: int,
        min_win_rate: Decimal,
        min_average_markout: Decimal,
        category: str | None = None,
        time_period: str | None = None,
    ) -> list[SmartWallet]:
        with connect_database(self.database_path) as connection:
            filters = []
            params: list[str] = []
            if category and category != "ALL":
                filters.append("w.proxy_wallet IN (SELECT proxy_wallet FROM leaderboard_snapshots WHERE category = ?)")
                params.append(category)
            if time_period and time_period != "ALL":
                filters.append("w.proxy_wallet IN (SELECT proxy_wallet FROM leaderboard_snapshots WHERE time_period = ?)")
                params.append(time_period)

            where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
            rows = connection.execute(
                f"""
                WITH trade_stats AS (
                    SELECT
                        proxy_wallet,
                        COUNT(DISTINCT transaction_hash) AS observed_trade_count,
                        COUNT(DISTINCT date(timestamp, 'unixepoch')) AS active_days,
                        COALESCE(MAX(timestamp), 0) AS latest_trade_timestamp
                    FROM trades
                    GROUP BY proxy_wallet
                ),
                position_stats AS (
                    SELECT
                        proxy_wallet,
                        COUNT(*) AS closed_position_count,
                        SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) AS winning_positions,
                        SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) AS losing_positions,
                        COALESCE(SUM(realized_pnl), 0) AS total_realized_pnl,
                        COALESCE(AVG(realized_pnl), 0) AS average_realized_pnl
                    FROM closed_positions
                    GROUP BY proxy_wallet
                ),
                markout_stats AS (
                    SELECT
                        t.proxy_wallet,
                        COALESCE(AVG(tm.markout), 0) AS average_markout,
                        COALESCE(AVG(CASE WHEN tm.markout > 0 THEN 1.0 ELSE 0.0 END), 0) AS positive_markout_rate
                    FROM trade_markouts tm
                    JOIN trades t ON t.transaction_hash = tm.transaction_hash
                    GROUP BY t.proxy_wallet
                )
                SELECT
                    w.proxy_wallet,
                    w.username,
                    w.x_username,
                    w.verified_badge,
                    w.profile_image,
                    COALESCE(ts.observed_trade_count, 0) AS observed_trade_count,
                    COALESCE(ps.closed_position_count, 0) AS closed_position_count,
                    COALESCE(ps.winning_positions, 0) AS winning_positions,
                    COALESCE(ps.losing_positions, 0) AS losing_positions,
                    COALESCE(ps.total_realized_pnl, 0) AS total_realized_pnl,
                    COALESCE(ps.average_realized_pnl, 0) AS average_realized_pnl,
                    COALESCE(ts.active_days, 0) AS active_days,
                    COALESCE(ms.average_markout, 0) AS average_markout,
                    COALESCE(ms.positive_markout_rate, 0) AS positive_markout_rate,
                    COALESCE(ts.latest_trade_timestamp, 0) AS latest_trade_timestamp
                FROM wallets w
                LEFT JOIN trade_stats ts ON ts.proxy_wallet = w.proxy_wallet
                LEFT JOIN position_stats ps ON ps.proxy_wallet = w.proxy_wallet
                LEFT JOIN markout_stats ms ON ms.proxy_wallet = w.proxy_wallet
                {where_clause}
                """,
                params,
            ).fetchall()

            ranked: list[SmartWallet] = []
            for row in rows:
                wallet = self._row_to_smart_wallet(connection, row)
                if wallet.observed_trade_count < min_trades:
                    continue
                if wallet.closed_position_count < min_closed_positions:
                    continue
                if wallet.win_rate < min_win_rate:
                    continue
                if wallet.average_markout < min_average_markout:
                    continue
                ranked.append(wallet)

        return sorted(ranked, key=lambda item: item.insider_score, reverse=True)[:limit]

    def _row_to_smart_wallet(self, connection: sqlite3.Connection, row: sqlite3.Row) -> SmartWallet:
        wins = int(row["winning_positions"] or 0)
        losses = int(row["losing_positions"] or 0)
        decisive = wins + losses
        win_rate = Decimal(wins) / Decimal(decisive) if decisive else Decimal("0")
        observed_trade_count = int(row["observed_trade_count"] or 0)
        closed_position_count = int(row["closed_position_count"] or 0)
        active_days = int(row["active_days"] or 0)
        total_realized_pnl = Decimal(str(row["total_realized_pnl"] or 0))
        average_realized_pnl = Decimal(str(row["average_realized_pnl"] or 0))
        average_markout = Decimal(str(row["average_markout"] or 0))
        positive_markout_rate = Decimal(str(row["positive_markout_rate"] or 0))
        score = self._score_wallet(
            win_rate=win_rate,
            closed_position_count=closed_position_count,
            observed_trade_count=observed_trade_count,
            active_days=active_days,
            total_realized_pnl=total_realized_pnl,
            average_markout=average_markout,
            positive_markout_rate=positive_markout_rate,
        )
        reasons = self._build_reasons(
            win_rate=win_rate,
            closed_position_count=closed_position_count,
            observed_trade_count=observed_trade_count,
            active_days=active_days,
            total_realized_pnl=total_realized_pnl,
            average_markout=average_markout,
            positive_markout_rate=positive_markout_rate,
        )

        return SmartWallet(
            proxy_wallet=str(row["proxy_wallet"]),
            username=str(row["username"] or ""),
            x_username=str(row["x_username"] or ""),
            verified_badge=bool(row["verified_badge"]),
            profile_image=str(row["profile_image"] or ""),
            observed_trade_count=observed_trade_count,
            closed_position_count=closed_position_count,
            winning_positions=wins,
            losing_positions=losses,
            win_rate=win_rate,
            total_realized_pnl=total_realized_pnl,
            average_realized_pnl=average_realized_pnl,
            active_days=active_days,
            average_markout=average_markout,
            positive_markout_rate=positive_markout_rate,
            latest_trade_timestamp=int(row["latest_trade_timestamp"] or 0),
            insider_score=score,
            reasons=reasons,
            recent_trades=self._get_recent_trades(connection, str(row["proxy_wallet"]), limit=5),
        )

    def _score_wallet(
        self,
        win_rate: Decimal,
        closed_position_count: int,
        observed_trade_count: int,
        active_days: int,
        total_realized_pnl: Decimal,
        average_markout: Decimal,
        positive_markout_rate: Decimal,
    ) -> Decimal:
        win_points = win_rate * Decimal("30")
        pnl_points = Decimal("15") if total_realized_pnl > 0 else Decimal("0")
        sample_points = min(Decimal(closed_position_count) / Decimal("75"), Decimal("1")) * Decimal("15")
        activity_points = min(Decimal(active_days) / Decimal("14"), Decimal("1")) * Decimal("10")
        trade_points = min(Decimal(observed_trade_count) / Decimal("75"), Decimal("1")) * Decimal("10")
        markout_points = max(min(average_markout * Decimal("200"), Decimal("10")), Decimal("-10"))
        positive_markout_points = positive_markout_rate * Decimal("10")
        return win_points + pnl_points + sample_points + activity_points + trade_points + markout_points + positive_markout_points

    def _build_reasons(
        self,
        win_rate: Decimal,
        closed_position_count: int,
        observed_trade_count: int,
        active_days: int,
        total_realized_pnl: Decimal,
        average_markout: Decimal,
        positive_markout_rate: Decimal,
    ) -> list[str]:
        reasons = [
            f"{float(win_rate * 100):.1f}% closed-position win rate across {closed_position_count} positions",
            f"{observed_trade_count} observed trades across {active_days} active days",
        ]
        if total_realized_pnl > 0:
            reasons.append(f"${float(total_realized_pnl):,.0f} observed realized PnL")
        if average_markout > 0:
            reasons.append(f"{float(average_markout):.3f} average favorable markout after tracked trades")
        if positive_markout_rate > 0:
            reasons.append(f"{float(positive_markout_rate * 100):.1f}% of tracked markouts moved in their favor")
        return reasons

    def _calculate_trade_markout(self, trade: TraderActivity) -> dict[str, Decimal] | None:
        if not trade.asset:
            return None
        try:
            order_book = self.client.get_order_book(trade.asset)
        except requests.RequestException:
            return None

        current_mid = self._current_mid(order_book)
        if current_mid is None:
            return None
        markout = current_mid - trade.price if trade.side.upper() == "BUY" else trade.price - current_mid
        return {"current_mid": current_mid, "markout": markout}

    def _current_mid(self, order_book: OrderBook) -> Decimal | None:
        bid = order_book.best_bid
        ask = order_book.best_ask
        if bid is not None and ask is not None:
            return (bid.price + ask.price) / Decimal("2")
        if bid is not None:
            return bid.price
        if ask is not None:
            return ask.price
        return None

    def _get_recent_trades(self, connection: sqlite3.Connection, wallet: str, limit: int) -> list[TraderActivity]:
        rows = connection.execute(
            """
            SELECT * FROM trades
            WHERE proxy_wallet = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (wallet, limit),
        ).fetchall()
        return [
            TraderActivity(
                proxy_wallet=str(row["proxy_wallet"]),
                timestamp=int(row["timestamp"]),
                condition_id=str(row["condition_id"]),
                activity_type="TRADE",
                side=str(row["side"]),
                outcome=str(row["outcome"]),
                title=str(row["title"]),
                slug=str(row["slug"]),
                asset=str(row["asset"]),
                size=Decimal(str(row["size"])),
                usdc_size=Decimal(str(row["usdc_size"])),
                price=Decimal(str(row["price"])),
                transaction_hash=str(row["transaction_hash"]),
            )
            for row in rows
        ]

    def _upsert_wallet(self, connection: sqlite3.Connection, candidate: TraderProfile, observed_at: str) -> None:
        connection.execute(
            """
            INSERT INTO wallets (
                proxy_wallet, username, x_username, verified_badge, profile_image, first_seen_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(proxy_wallet) DO UPDATE SET
                username = excluded.username,
                x_username = excluded.x_username,
                verified_badge = excluded.verified_badge,
                profile_image = excluded.profile_image,
                last_seen_at = excluded.last_seen_at
            """,
            (
                candidate.proxy_wallet,
                candidate.username,
                candidate.x_username,
                int(candidate.verified_badge),
                candidate.profile_image,
                observed_at,
                observed_at,
            ),
        )

    def _insert_leaderboard_snapshot(
        self,
        connection: sqlite3.Connection,
        candidate: TraderProfile,
        category: str,
        time_period: str,
        order_by: str,
        observed_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO leaderboard_snapshots (
                observed_at, category, time_period, order_by, rank, proxy_wallet, pnl, volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observed_at,
                category,
                time_period,
                order_by,
                candidate.rank,
                candidate.proxy_wallet,
                float(candidate.pnl),
                float(candidate.volume),
            ),
        )

    def _upsert_trade(self, connection: sqlite3.Connection, trade: TraderActivity, observed_at: str) -> None:
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
                observed_at,
            ),
        )

    def _upsert_closed_position(
        self,
        connection: sqlite3.Connection,
        position: ClosedPosition,
        observed_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT OR IGNORE INTO closed_positions (
                proxy_wallet, condition_id, outcome, title, slug, avg_price,
                total_bought, realized_pnl, timestamp, end_date, first_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                position.proxy_wallet,
                position.condition_id,
                position.outcome,
                position.title,
                position.slug,
                float(position.avg_price),
                float(position.total_bought),
                float(position.realized_pnl),
                position.timestamp,
                position.end_date,
                observed_at,
            ),
        )

    def _insert_markout(
        self,
        connection: sqlite3.Connection,
        transaction_hash: str,
        observed_at: str,
        current_mid: Decimal,
        markout: Decimal,
    ) -> None:
        connection.execute(
            """
            INSERT INTO trade_markouts (transaction_hash, observed_at, current_mid, markout)
            VALUES (?, ?, ?, ?)
            """,
            (transaction_hash, observed_at, float(current_mid), float(markout)),
        )
