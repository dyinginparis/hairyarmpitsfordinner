from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from src.models import BinaryArbitrageOpportunity
from src.storage import connect_database


class AlertStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def save_arbitrage_opportunities(
        self,
        opportunities: list[BinaryArbitrageOpportunity],
    ) -> list[dict[str, Any]]:
        now = datetime.now(UTC).isoformat()
        new_alerts: list[dict[str, Any]] = []

        with connect_database(self.database_path) as connection:
            for opportunity in opportunities:
                signature = self._arbitrage_signature(opportunity)
                inserted = connection.execute(
                    """
                    INSERT OR IGNORE INTO arbitrage_alerts (
                        signature, market_id, question, condition_id, yes_price, no_price,
                        net_profit_bps, max_size, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        signature,
                        opportunity.market_id,
                        opportunity.question,
                        opportunity.condition_id,
                        float(opportunity.yes_price),
                        float(opportunity.no_price),
                        float(opportunity.net_profit_bps),
                        float(opportunity.max_size),
                        now,
                    ),
                ).rowcount
                if inserted:
                    payload = asdict(opportunity)
                    payload["signature"] = signature
                    payload["created_at"] = now
                    new_alerts.append(self._decimal_to_float(payload))

        return new_alerts

    def list_arbitrage_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        with connect_database(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM arbitrage_alerts
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _arbitrage_signature(self, opportunity: BinaryArbitrageOpportunity) -> str:
        # Bucket prices to cents so the same opportunity does not spam alerts on tiny book updates.
        yes_bucket = int((opportunity.yes_price * Decimal("100")).to_integral_value())
        no_bucket = int((opportunity.no_price * Decimal("100")).to_integral_value())
        return f"{opportunity.condition_id}:{yes_bucket}:{no_bucket}"

    def _decimal_to_float(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {key: self._decimal_to_float(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._decimal_to_float(item) for item in value]
        if isinstance(value, tuple):
            return [self._decimal_to_float(item) for item in value]
        return value
