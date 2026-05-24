from __future__ import annotations

from decimal import Decimal
from typing import Any


def decimal_to_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: decimal_to_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_to_json(item) for item in value]
    if isinstance(value, tuple):
        return [decimal_to_json(item) for item in value]
    return value
