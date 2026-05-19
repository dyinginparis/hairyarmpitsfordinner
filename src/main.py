from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from src.config import load_settings
from src.polymarket_client import PolymarketClient
from src.scanner import ArbitrageScanner


def decimal_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Polymarket arbitrage scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan active binary markets")
    scan.add_argument("--limit", type=int, default=None, help="Number of Gamma markets to request")
    scan.add_argument("--max-markets", type=int, default=None, help="Cap markets scanned after filtering")
    scan.add_argument("--min-profit-bps", type=Decimal, default=None, help="Minimum net profit in basis points")
    scan.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main() -> None:
    settings = load_settings()
    args = build_parser().parse_args()

    if args.command == "scan":
        client = PolymarketClient(
            gamma_base_url=settings.gamma_base_url,
            clob_base_url=settings.clob_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        scanner = ArbitrageScanner(client)
        opportunities = scanner.scan_binary_markets(
            limit=args.limit or settings.scan_limit,
            min_profit_bps=args.min_profit_bps or Decimal(str(settings.min_profit_bps)),
            max_markets=args.max_markets,
        )

        if args.json:
            print(json.dumps([asdict(item) for item in opportunities], default=decimal_default, indent=2))
            return

        if not opportunities:
            print("No binary arbitrage opportunities found.")
            return

        for item in opportunities:
            print(f"{item.net_profit_bps:.2f} bps | size {item.max_size} | {item.question}")
            print(
                f"  YES {item.yes_price} + NO {item.no_price} + fee {item.estimated_fee_per_set:.6f}"
                f" = cost {item.net_cost_per_set:.6f}, profit {item.net_profit_per_set:.6f}"
            )
            print(f"  condition: {item.condition_id}")


if __name__ == "__main__":
    main()
