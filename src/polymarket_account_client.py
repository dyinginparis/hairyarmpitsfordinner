from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountClientConfig:
    clob_base_url: str
    private_key: str
    api_key: str
    api_secret: str
    api_passphrase: str
    signature_type: str
    funder_address: str


class PolymarketAccountClient:
    def __init__(self, config: AccountClientConfig) -> None:
        self.config = config

    def is_configured(self) -> bool:
        return all(
            [
                self.config.private_key,
                self.config.api_key,
                self.config.api_secret,
                self.config.api_passphrase,
            ]
        )

    def get_authenticated_snapshot(self) -> dict[str, Any]:
        if not self.is_configured():
            return {
                "authenticatedConfigured": False,
                "authenticatedConnected": False,
                "balanceAllowance": None,
                "openOrders": [],
                "authenticatedTrades": [],
                "errors": ["Missing private key or API credentials in .env"],
            }

        try:
            from py_clob_client_v2.client import ClobClient
            from py_clob_client_v2.clob_types import (
                ApiCreds,
                AssetType,
                BalanceAllowanceParams,
                OpenOrderParams,
                TradeParams,
            )
            from py_clob_client_v2.constants import POLYGON
        except Exception as error:  # pragma: no cover - optional dependency guard
            return {
                "authenticatedConfigured": True,
                "authenticatedConnected": False,
                "balanceAllowance": None,
                "openOrders": [],
                "authenticatedTrades": [],
                "errors": [f"py-clob-client-v2 unavailable: {error}"],
            }

        errors: list[str] = []
        signature_type = self._signature_type()
        client = ClobClient(
            host=self.config.clob_base_url,
            chain_id=POLYGON,
            key=self.config.private_key,
            creds=ApiCreds(
                api_key=self.config.api_key,
                api_secret=self.config.api_secret,
                api_passphrase=self.config.api_passphrase,
            ),
            signature_type=signature_type,
            funder=self.config.funder_address or None,
        )

        snapshot: dict[str, Any] = {
            "authenticatedConfigured": True,
            "authenticatedConnected": False,
            "signerAddress": "",
            "balanceAllowance": None,
            "openOrders": [],
            "authenticatedTrades": [],
            "errors": errors,
        }
        try:
            snapshot["signerAddress"] = client.get_address()
        except Exception as error:
            errors.append(f"signer address: {error}")

        try:
            snapshot["balanceAllowance"] = client.get_balance_allowance(
                BalanceAllowanceParams(asset_type=AssetType.COLLATERAL, signature_type=signature_type)
            )
        except Exception as error:
            errors.append(f"balance allowance: {error}")

        try:
            snapshot["openOrders"] = client.get_open_orders(OpenOrderParams(), only_first_page=True)
        except Exception as error:
            errors.append(f"open orders: {error}")

        try:
            snapshot["authenticatedTrades"] = client.get_trades(TradeParams(), only_first_page=True)
        except Exception as error:
            errors.append(f"authenticated trades: {error}")

        snapshot["authenticatedConnected"] = snapshot["balanceAllowance"] is not None or snapshot["openOrders"] != []
        return snapshot

    def _signature_type(self) -> int:
        if self.config.signature_type == "":
            return -1
        try:
            return int(self.config.signature_type)
        except ValueError:
            return -1
