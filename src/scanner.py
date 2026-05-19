from __future__ import annotations

from decimal import Decimal

import requests

from src.models import BinaryArbitrageOpportunity
from src.polymarket_client import PolymarketClient
from src.strategies.binary_arb import find_binary_buy_arb


class ArbitrageScanner:
    def __init__(self, client: PolymarketClient) -> None:
        self.client = client

    def scan_binary_markets(
        self,
        limit: int,
        min_profit_bps: Decimal,
        max_markets: int | None = None,
    ) -> list[BinaryArbitrageOpportunity]:
        opportunities: list[BinaryArbitrageOpportunity] = []
        markets = self.client.get_active_markets(limit=limit)
        if max_markets is not None:
            markets = markets[:max_markets]

        for market in markets:
            if not market.condition_id:
                continue

            try:
                yes_book = self.client.get_order_book(market.clob_token_ids[0])
                no_book = self.client.get_order_book(market.clob_token_ids[1])
                fee_info = self.client.get_fee_info(market.condition_id)
            except requests.RequestException:
                continue

            opportunity = find_binary_buy_arb(
                market=market,
                yes_book=yes_book,
                no_book=no_book,
                fee_info=fee_info,
                min_profit_bps=min_profit_bps,
            )
            if opportunity is not None:
                opportunities.append(opportunity)

        return sorted(opportunities, key=lambda item: item.net_profit_bps, reverse=True)
