from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import re

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    gamma_base_url: str = "https://gamma-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"
    data_base_url: str = "https://data-api.polymarket.com"
    scan_limit: int = 50
    min_profit_bps: float = 10.0
    request_timeout_seconds: float = 10.0
    database_path: str = "data/smart_wallets.sqlite3"
    polymarket_account_address: str = ""
    polymarket_funder_address: str = ""
    polymarket_signature_type: str = ""
    polymarket_api_key: str = ""
    polymarket_api_secret: str = ""
    polymarket_api_passphrase: str = ""
    polymarket_private_key: str = ""


ACCOUNT_ENV_KEYS = {
    "accountAddress": "POLYMARKET_ACCOUNT_ADDRESS",
    "funderAddress": "POLYMARKET_FUNDER_ADDRESS",
    "signatureType": "POLYMARKET_SIGNATURE_TYPE",
    "apiKey": "POLYMARKET_API_KEY",
    "apiSecret": "POLYMARKET_API_SECRET",
    "apiPassphrase": "POLYMARKET_API_PASSPHRASE",
    "privateKey": "POLYMARKET_PRIVATE_KEY",
}

SECRET_ACCOUNT_KEYS = {"apiKey", "apiSecret", "apiPassphrase", "privateKey"}


def load_settings() -> Settings:
    load_dotenv(override=True)

    return Settings(
        gamma_base_url=os.getenv("POLYMARKET_GAMMA_BASE_URL", Settings.gamma_base_url).rstrip("/"),
        clob_base_url=os.getenv("POLYMARKET_CLOB_BASE_URL", Settings.clob_base_url).rstrip("/"),
        data_base_url=os.getenv("POLYMARKET_DATA_BASE_URL", Settings.data_base_url).rstrip("/"),
        scan_limit=int(os.getenv("SCAN_LIMIT", Settings.scan_limit)),
        min_profit_bps=float(os.getenv("MIN_PROFIT_BPS", Settings.min_profit_bps)),
        request_timeout_seconds=float(
            os.getenv("REQUEST_TIMEOUT_SECONDS", Settings.request_timeout_seconds)
        ),
        database_path=os.getenv("DATABASE_PATH", Settings.database_path),
        polymarket_account_address=os.getenv("POLYMARKET_ACCOUNT_ADDRESS", "").strip(),
        polymarket_funder_address=os.getenv("POLYMARKET_FUNDER_ADDRESS", "").strip(),
        polymarket_signature_type=os.getenv("POLYMARKET_SIGNATURE_TYPE", "").strip(),
        polymarket_api_key=os.getenv("POLYMARKET_API_KEY", "").strip(),
        polymarket_api_secret=os.getenv("POLYMARKET_API_SECRET", "").strip(),
        polymarket_api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE", "").strip(),
        polymarket_private_key=os.getenv("POLYMARKET_PRIVATE_KEY", "").strip(),
    )


def account_connection_payload(settings: Settings | None = None) -> dict[str, str | bool]:
    settings = settings or load_settings()
    values = {
        "accountAddress": settings.polymarket_account_address,
        "funderAddress": settings.polymarket_funder_address,
        "signatureType": settings.polymarket_signature_type,
        "apiKey": settings.polymarket_api_key,
        "apiSecret": settings.polymarket_api_secret,
        "apiPassphrase": settings.polymarket_api_passphrase,
        "privateKey": settings.polymarket_private_key,
    }
    payload: dict[str, str | bool] = {}
    for key, value in values.items():
        payload[key] = value if key not in SECRET_ACCOUNT_KEYS else ""
        payload[f"{key}Configured"] = bool(value)
        payload[f"{key}Masked"] = mask_secret(value) if key in SECRET_ACCOUNT_KEYS else value
    return payload


def save_account_connection(payload: dict[str, object], env_path: str | Path = ".env") -> dict[str, str | bool]:
    clean_values: dict[str, str] = {}
    for key, env_key in ACCOUNT_ENV_KEYS.items():
        raw_value = payload.get(key)
        if raw_value is None:
            continue
        value = str(raw_value).strip()
        if key in SECRET_ACCOUNT_KEYS and value == "":
            continue
        clean_values[env_key] = value
        os.environ[env_key] = value

    if clean_values:
        _write_env_values(Path(env_path), clean_values)
    return account_connection_payload(load_settings())


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 10:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _write_env_values(path: Path, values: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    updated_lines: list[str] = []
    key_pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")

    for line in lines:
        match = key_pattern.match(line)
        if match and match.group(1) in values:
            key = match.group(1)
            updated_lines.append(f"{key}={_format_env_value(values[key])}")
            seen.add(key)
        else:
            updated_lines.append(line)

    if updated_lines and updated_lines[-1].strip():
        updated_lines.append("")
    for key, value in values.items():
        if key not in seen:
            updated_lines.append(f"{key}={_format_env_value(value)}")

    path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")


def _format_env_value(value: str) -> str:
    if value == "":
        return ""
    if re.search(r"\s|#|\"|'", value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value
