from decimal import Decimal

from src.models import FeeInfo, Market, OrderBook, OrderLevel
from src.strategies.binary_arb import find_binary_buy_arb


def test_binary_buy_arb_detects_underpriced_pair() -> None:
    market = Market(
        id="1",
        question="Test market?",
        condition_id="0xabc",
        slug="test-market",
        clob_token_ids=["yes", "no"],
        outcomes=["Yes", "No"],
    )
    yes_book = OrderBook(token_id="yes", bids=[], asks=[OrderLevel(Decimal("0.48"), Decimal("20"))])
    no_book = OrderBook(token_id="no", bids=[], asks=[OrderLevel(Decimal("0.49"), Decimal("10"))])

    opportunity = find_binary_buy_arb(
        market=market,
        yes_book=yes_book,
        no_book=no_book,
        fee_info=FeeInfo(taker_fee_rate=Decimal("0")),
        min_profit_bps=Decimal("1"),
    )

    assert opportunity is not None
    assert opportunity.max_size == Decimal("10")
    assert opportunity.net_profit_per_set == Decimal("0.03")


def test_binary_buy_arb_rejects_when_fees_remove_profit() -> None:
    market = Market(
        id="1",
        question="Test market?",
        condition_id="0xabc",
        slug="test-market",
        clob_token_ids=["yes", "no"],
        outcomes=["Yes", "No"],
    )
    yes_book = OrderBook(token_id="yes", bids=[], asks=[OrderLevel(Decimal("0.495"), Decimal("20"))])
    no_book = OrderBook(token_id="no", bids=[], asks=[OrderLevel(Decimal("0.495"), Decimal("20"))])

    opportunity = find_binary_buy_arb(
        market=market,
        yes_book=yes_book,
        no_book=no_book,
        fee_info=FeeInfo(taker_fee_rate=Decimal("0.07")),
        min_profit_bps=Decimal("1"),
    )

    assert opportunity is None
