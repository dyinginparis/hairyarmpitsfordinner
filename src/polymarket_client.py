from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import requests

from src.models import ClosedPosition, FeeInfo, Market, OrderBook, OrderLevel, TraderActivity, TraderProfile


class PolymarketClient:
    def __init__(
        self,
        gamma_base_url: str,
        clob_base_url: str,
        timeout_seconds: float,
        data_base_url: str = "https://data-api.polymarket.com",
    ) -> None:
        self.gamma_base_url = gamma_base_url
        self.clob_base_url = clob_base_url
        self.data_base_url = data_base_url
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "predictionmarket-arbitrage-bot/phase1"})

    def get_active_markets(self, limit: int) -> list[Market]:
        response = self.session.get(
            f"{self.gamma_base_url}/markets",
            params={
                "active": "true",
                "closed": "false",
                "archived": "false",
                "enableOrderBook": "true",
                "limit": limit,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return [self._parse_market(item) for item in payload if self._is_binary_clob_market(item)]

    def get_order_book(self, token_id: str) -> OrderBook:
        response = self.session.get(
            f"{self.clob_base_url}/book",
            params={"token_id": token_id},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return OrderBook(
            token_id=token_id,
            bids=self._parse_levels(payload.get("bids", [])),
            asks=self._parse_levels(payload.get("asks", [])),
            hash=payload.get("hash"),
            timestamp=str(payload.get("timestamp")) if payload.get("timestamp") else None,
        )

    def get_fee_info(self, condition_id: str) -> FeeInfo:
        response = self.session.get(
            f"{self.clob_base_url}/clob-markets/{condition_id}",
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        fee_details = payload.get("fd") or {}
        if "r" in fee_details and fee_details["r"] is not None:
            return FeeInfo(taker_fee_rate=Decimal(str(fee_details["r"])))

        taker_base_fee = payload.get("tbf")
        if taker_base_fee is not None:
            # CLOB V2 exposes market fee parameters. If only the base fee is present,
            # treat it as basis points to avoid underestimating costs.
            return FeeInfo(taker_fee_rate=Decimal(str(taker_base_fee)) / Decimal("10000"))

        return FeeInfo(taker_fee_rate=Decimal("0"))

    def get_leaderboard(
        self,
        category: str,
        time_period: str,
        order_by: str,
        limit: int,
        offset: int = 0,
    ) -> list[TraderProfile]:
        response = self.session.get(
            f"{self.data_base_url}/v1/leaderboard",
            params={
                "category": category,
                "timePeriod": time_period,
                "orderBy": order_by,
                "limit": limit,
                "offset": offset,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return [self._parse_trader(item) for item in response.json()]

    def get_user_trade_activity(self, user: str, limit: int) -> list[TraderActivity]:
        response = self.session.get(
            f"{self.data_base_url}/activity",
            params={
                "user": user,
                "type": "TRADE",
                "limit": limit,
                "sortBy": "TIMESTAMP",
                "sortDirection": "DESC",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return [self._parse_activity(item) for item in response.json()]

    def get_user_closed_positions(self, user: str, limit: int) -> list[ClosedPosition]:
        response = self.session.get(
            f"{self.data_base_url}/closed-positions",
            params={
                "user": user,
                "limit": limit,
                "sortBy": "TIMESTAMP",
                "sortDirection": "DESC",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return [self._parse_closed_position(item) for item in response.json()]

    def get_user_positions_raw(self, user: str, limit: int = 100) -> list[dict[str, Any]]:
        response = self.session.get(
            f"{self.data_base_url}/positions",
            params={"user": user, "limit": limit},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []

    def get_markets_by_condition_ids(self, condition_ids: list[str]) -> dict[str, dict[str, Any]]:
        markets: dict[str, dict[str, Any]] = {}
        for condition_id in dict.fromkeys(condition_ids):
            if not condition_id:
                continue
            response = self.session.get(
                f"{self.gamma_base_url}/markets",
                params={"condition_ids": condition_id},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            for item in response.json():
                item_condition_id = str(item.get("conditionId") or item.get("condition_id") or "")
                if item_condition_id:
                    markets[item_condition_id] = item
        return markets

    def _parse_market(self, payload: dict[str, Any]) -> Market:
        return Market(
            id=str(payload.get("id", "")),
            question=str(payload.get("question", "")),
            condition_id=str(payload.get("conditionId") or payload.get("condition_id") or ""),
            slug=payload.get("slug"),
            clob_token_ids=self._parse_json_list(payload.get("clobTokenIds")),
            outcomes=self._parse_json_list(payload.get("outcomes")),
        )

    def _parse_trader(self, payload: dict[str, Any]) -> TraderProfile:
        return TraderProfile(
            rank=str(payload.get("rank", "")),
            proxy_wallet=str(payload.get("proxyWallet", "")),
            username=str(payload.get("userName") or payload.get("proxyWallet") or ""),
            x_username=str(payload.get("xUsername") or ""),
            verified_badge=bool(payload.get("verifiedBadge", False)),
            volume=Decimal(str(payload.get("vol", 0))),
            pnl=Decimal(str(payload.get("pnl", 0))),
            profile_image=str(payload.get("profileImage") or ""),
            recent_trades=[],
            recent_closed_positions=[],
            stats=None,
        )

    def _parse_activity(self, payload: dict[str, Any]) -> TraderActivity:
        return TraderActivity(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            timestamp=int(payload.get("timestamp") or 0),
            condition_id=str(payload.get("conditionId", "")),
            activity_type=str(payload.get("type", "")),
            side=str(payload.get("side", "")),
            outcome=str(payload.get("outcome", "")),
            title=str(payload.get("title", "")),
            slug=str(payload.get("slug", "")),
            size=Decimal(str(payload.get("size", 0))),
            usdc_size=Decimal(str(payload.get("usdcSize", 0))),
            price=Decimal(str(payload.get("price", 0))),
            transaction_hash=str(payload.get("transactionHash", "")),
            asset=str(payload.get("asset", "")),
        )

    def _parse_closed_position(self, payload: dict[str, Any]) -> ClosedPosition:
        return ClosedPosition(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            condition_id=str(payload.get("conditionId", "")),
            title=str(payload.get("title", "")),
            slug=str(payload.get("slug", "")),
            outcome=str(payload.get("outcome", "")),
            avg_price=Decimal(str(payload.get("avgPrice", 0))),
            total_bought=Decimal(str(payload.get("totalBought", 0))),
            realized_pnl=Decimal(str(payload.get("realizedPnl", 0))),
            timestamp=int(payload.get("timestamp") or 0),
            end_date=str(payload.get("endDate") or ""),
        )

    def _is_binary_clob_market(self, payload: dict[str, Any]) -> bool:
        token_ids = self._parse_json_list(payload.get("clobTokenIds"))
        outcomes = self._parse_json_list(payload.get("outcomes"))
        enabled = payload.get("enableOrderBook") is True or str(payload.get("enableOrderBook")).lower() == "true"
        return enabled and len(token_ids) == 2 and len(outcomes) == 2

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

    def _parse_levels(self, raw_levels: list[dict[str, Any]]) -> list[OrderLevel]:
        return [
            OrderLevel(price=Decimal(str(level["price"])), size=Decimal(str(level["size"])))
            for level in raw_levels
            if "price" in level and "size" in level
        ]
