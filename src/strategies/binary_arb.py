from __future__ import annotations

from decimal import Decimal

from src.models import BinaryArbitrageOpportunity, FeeInfo, Market, OrderBook


def estimate_taker_fee_per_share(price: Decimal, fee_info: FeeInfo) -> Decimal:
    return fee_info.taker_fee_rate * price * (Decimal("1") - price)


def find_binary_buy_arb(
    market: Market,
    yes_book: OrderBook,
    no_book: OrderBook,
    fee_info: FeeInfo,
    min_profit_bps: Decimal,
) -> BinaryArbitrageOpportunity | None:
    yes_ask = yes_book.best_ask
    no_ask = no_book.best_ask
    if yes_ask is None or no_ask is None:
        return None

    max_size = min(yes_ask.size, no_ask.size)
    if max_size <= 0:
        return None

    gross_cost = yes_ask.price + no_ask.price
    fee_per_set = estimate_taker_fee_per_share(yes_ask.price, fee_info) + estimate_taker_fee_per_share(
        no_ask.price, fee_info
    )
    net_cost = gross_cost + fee_per_set
    net_profit = Decimal("1") - net_cost
    net_profit_bps = net_profit * Decimal("10000")

    if net_profit_bps < min_profit_bps:
        return None

    return BinaryArbitrageOpportunity(
        market_id=market.id,
        question=market.question,
        condition_id=market.condition_id,
        yes_token_id=market.clob_token_ids[0],
        no_token_id=market.clob_token_ids[1],
        yes_price=yes_ask.price,
        no_price=no_ask.price,
        max_size=max_size,
        gross_cost_per_set=gross_cost,
        estimated_fee_per_set=fee_per_set,
        net_cost_per_set=net_cost,
        net_profit_per_set=net_profit,
        net_profit_bps=net_profit_bps,
        book_hashes=(yes_book.hash, no_book.hash),
    )
