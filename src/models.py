from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderLevel:
    price: Decimal
    size: Decimal


@dataclass(frozen=True)
class OrderBook:
    token_id: str
    bids: list[OrderLevel]
    asks: list[OrderLevel]
    hash: str | None = None
    timestamp: str | None = None

    @property
    def best_ask(self) -> OrderLevel | None:
        return self.asks[0] if self.asks else None

    @property
    def best_bid(self) -> OrderLevel | None:
        return self.bids[0] if self.bids else None


@dataclass(frozen=True)
class Market:
    id: str
    question: str
    condition_id: str
    slug: str | None
    clob_token_ids: list[str]
    outcomes: list[str]


@dataclass(frozen=True)
class FeeInfo:
    taker_fee_rate: Decimal


@dataclass(frozen=True)
class BinaryArbitrageOpportunity:
    market_id: str
    question: str
    condition_id: str
    yes_token_id: str
    no_token_id: str
    yes_price: Decimal
    no_price: Decimal
    max_size: Decimal
    gross_cost_per_set: Decimal
    estimated_fee_per_set: Decimal
    net_cost_per_set: Decimal
    net_profit_per_set: Decimal
    net_profit_bps: Decimal
    book_hashes: tuple[str | None, str | None]


@dataclass(frozen=True)
class TraderActivity:
    proxy_wallet: str
    timestamp: int
    condition_id: str
    activity_type: str
    side: str
    outcome: str
    title: str
    slug: str
    size: Decimal
    usdc_size: Decimal
    price: Decimal
    transaction_hash: str
    asset: str = ""


@dataclass(frozen=True)
class ClosedPosition:
    proxy_wallet: str
    condition_id: str
    title: str
    slug: str
    outcome: str
    avg_price: Decimal
    total_bought: Decimal
    realized_pnl: Decimal
    timestamp: int
    end_date: str


@dataclass(frozen=True)
class TraderStats:
    closed_positions_sampled: int
    winning_positions: int
    losing_positions: int
    breakeven_positions: int
    win_rate: Decimal
    total_realized_pnl: Decimal
    average_realized_pnl: Decimal
    recent_trade_count: int
    active_days: int
    consistency_score: Decimal


@dataclass(frozen=True)
class TraderProfile:
    rank: str
    proxy_wallet: str
    username: str
    x_username: str
    verified_badge: bool
    volume: Decimal
    pnl: Decimal
    profile_image: str
    recent_trades: list[TraderActivity]
    recent_closed_positions: list[ClosedPosition]
    stats: TraderStats | None = None


@dataclass(frozen=True)
class SmartWallet:
    proxy_wallet: str
    username: str
    x_username: str
    verified_badge: bool
    profile_image: str
    observed_trade_count: int
    closed_position_count: int
    winning_positions: int
    losing_positions: int
    win_rate: Decimal
    total_realized_pnl: Decimal
    average_realized_pnl: Decimal
    active_days: int
    average_markout: Decimal
    positive_markout_rate: Decimal
    latest_trade_timestamp: int
    insider_score: Decimal
    reasons: list[str]
    recent_trades: list[TraderActivity]
