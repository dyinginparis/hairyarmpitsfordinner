from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import requests

from src.models import ClosedPosition, TraderActivity, TraderProfile, TraderStats
from src.polymarket_client import PolymarketClient


class TraderTracker:
    def __init__(self, client: PolymarketClient) -> None:
        self.client = client

    def get_top_traders_with_recent_trades(
        self,
        category: str,
        time_period: str,
        order_by: str,
        limit: int,
        trades_per_trader: int,
        closed_positions_per_trader: int = 50,
        min_closed_positions: int = 10,
        min_win_rate: Decimal = Decimal("0"),
        min_recent_trades: int = 0,
        rank_by_consistency: bool = False,
    ) -> list[TraderProfile]:
        traders = self.client.get_leaderboard(
            category=category,
            time_period=time_period,
            order_by=order_by,
            limit=limit,
        )
        tracked: list[TraderProfile] = []

        for trader in traders:
            try:
                recent_trades = self.client.get_user_trade_activity(
                    user=trader.proxy_wallet,
                    limit=trades_per_trader,
                )
            except requests.RequestException:
                recent_trades = []

            try:
                recent_closed_positions = self.client.get_user_closed_positions(
                    user=trader.proxy_wallet,
                    limit=closed_positions_per_trader,
                )
            except requests.RequestException:
                recent_closed_positions = []

            stats = self._calculate_stats(
                recent_trades=recent_trades,
                closed_positions=recent_closed_positions,
            )
            if stats.closed_positions_sampled < min_closed_positions:
                continue
            if stats.win_rate < min_win_rate:
                continue
            if stats.recent_trade_count < min_recent_trades:
                continue

            tracked.append(
                TraderProfile(
                    rank=trader.rank,
                    proxy_wallet=trader.proxy_wallet,
                    username=trader.username,
                    x_username=trader.x_username,
                    verified_badge=trader.verified_badge,
                    volume=trader.volume,
                    pnl=trader.pnl,
                    profile_image=trader.profile_image,
                    recent_trades=recent_trades,
                    recent_closed_positions=recent_closed_positions[:5],
                    stats=stats,
                )
            )

        if rank_by_consistency:
            tracked.sort(key=lambda item: item.stats.consistency_score if item.stats else Decimal("0"), reverse=True)

        return tracked

    def _calculate_stats(
        self,
        recent_trades: list[TraderActivity],
        closed_positions: list[ClosedPosition],
    ) -> TraderStats:
        wins = sum(1 for item in closed_positions if item.realized_pnl > 0)
        losses = sum(1 for item in closed_positions if item.realized_pnl < 0)
        breakeven = sum(1 for item in closed_positions if item.realized_pnl == 0)
        decisive_positions = wins + losses
        closed_count = len(closed_positions)
        win_rate = Decimal(wins) / Decimal(decisive_positions) if decisive_positions else Decimal("0")
        total_pnl = sum((item.realized_pnl for item in closed_positions), Decimal("0"))
        average_pnl = total_pnl / Decimal(closed_count) if closed_count else Decimal("0")
        active_days = self._count_active_days(recent_trades)
        score = self._score_trader(
            win_rate=win_rate,
            closed_count=closed_count,
            active_days=active_days,
            total_pnl=total_pnl,
            recent_trade_count=len(recent_trades),
        )

        return TraderStats(
            closed_positions_sampled=closed_count,
            winning_positions=wins,
            losing_positions=losses,
            breakeven_positions=breakeven,
            win_rate=win_rate,
            total_realized_pnl=total_pnl,
            average_realized_pnl=average_pnl,
            recent_trade_count=len(recent_trades),
            active_days=active_days,
            consistency_score=score,
        )

    def _count_active_days(self, recent_trades: list[TraderActivity]) -> int:
        days = set()
        for trade in recent_trades:
            if trade.timestamp > 0:
                days.add(datetime.fromtimestamp(trade.timestamp, tz=UTC).date())
        return len(days)

    def _score_trader(
        self,
        win_rate: Decimal,
        closed_count: int,
        active_days: int,
        total_pnl: Decimal,
        recent_trade_count: int,
    ) -> Decimal:
        win_rate_points = win_rate * Decimal("60")
        sample_points = min(Decimal(closed_count) / Decimal("30"), Decimal("1")) * Decimal("20")
        activity_points = min(Decimal(active_days) / Decimal("7"), Decimal("1")) * Decimal("10")
        trade_points = min(Decimal(recent_trade_count) / Decimal("10"), Decimal("1")) * Decimal("5")
        pnl_points = Decimal("5") if total_pnl > 0 else Decimal("0")
        return win_rate_points + sample_points + activity_points + trade_points + pnl_points
