from __future__ import annotations

from contextlib import contextmanager
import sqlite3
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS wallets (
    proxy_wallet TEXT PRIMARY KEY,
    username TEXT NOT NULL DEFAULT '',
    x_username TEXT NOT NULL DEFAULT '',
    verified_badge INTEGER NOT NULL DEFAULT 0,
    profile_image TEXT NOT NULL DEFAULT '',
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leaderboard_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observed_at TEXT NOT NULL,
    category TEXT NOT NULL,
    time_period TEXT NOT NULL,
    order_by TEXT NOT NULL,
    rank TEXT NOT NULL,
    proxy_wallet TEXT NOT NULL,
    pnl REAL NOT NULL,
    volume REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS trades (
    transaction_hash TEXT PRIMARY KEY,
    proxy_wallet TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    condition_id TEXT NOT NULL,
    side TEXT NOT NULL,
    outcome TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    asset TEXT NOT NULL DEFAULT '',
    size REAL NOT NULL,
    usdc_size REAL NOT NULL,
    price REAL NOT NULL,
    first_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS closed_positions (
    proxy_wallet TEXT NOT NULL,
    condition_id TEXT NOT NULL,
    outcome TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    avg_price REAL NOT NULL,
    total_bought REAL NOT NULL,
    realized_pnl REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    end_date TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    PRIMARY KEY (proxy_wallet, condition_id, outcome, timestamp)
);

CREATE TABLE IF NOT EXISTS trade_markouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_hash TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    current_mid REAL,
    markout REAL
);

CREATE TABLE IF NOT EXISTS watchlist (
    proxy_wallet TEXT PRIMARY KEY,
    label TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    added_at TEXT NOT NULL,
    alerts_enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS copytrade_settings (
    proxy_wallet TEXT PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    sizing_mode TEXT NOT NULL DEFAULT 'PERCENT',
    size_value REAL NOT NULL DEFAULT 10,
    max_usdc REAL NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_wallet TEXT NOT NULL DEFAULT '',
    source_transaction_hash TEXT NOT NULL DEFAULT '',
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    asset TEXT NOT NULL DEFAULT '',
    condition_id TEXT NOT NULL DEFAULT '',
    requested_usdc REAL NOT NULL,
    simulated_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    status TEXT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE(source_type, source_transaction_hash, strategy)
);

CREATE TABLE IF NOT EXISTS paper_account (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    starting_balance REAL NOT NULL DEFAULT 1000,
    cash_balance REAL NOT NULL DEFAULT 1000,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_wallet TEXT NOT NULL DEFAULT '',
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    asset TEXT NOT NULL DEFAULT '',
    condition_id TEXT NOT NULL DEFAULT '',
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    cost_usdc REAL NOT NULL,
    entry_fee_usdc REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    exit_price REAL,
    exit_value_usdc REAL,
    pnl_usdc REAL,
    exit_fee_usdc REAL NOT NULL DEFAULT 0,
    close_reason TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS paper_execution_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    entry_slippage_bps REAL NOT NULL DEFAULT 25,
    exit_slippage_bps REAL NOT NULL DEFAULT 25,
    fee_bps REAL NOT NULL DEFAULT 0,
    max_chase_bps REAL NOT NULL DEFAULT 100,
    copytrade_capital_mode TEXT NOT NULL DEFAULT 'CONSERVATIVE',
    min_cash_reserve_usdc REAL NOT NULL DEFAULT 0,
    min_trade_usdc REAL NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_mark_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    observed_at TEXT NOT NULL,
    mark_price REAL,
    mark_value_usdc REAL NOT NULL,
    unrealized_pnl_usdc REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    proxy_wallet TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    seen INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS paper_account_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observed_at TEXT NOT NULL,
    cash_balance REAL NOT NULL,
    active_cost REAL NOT NULL,
    open_market_value REAL NOT NULL,
    realized_pnl REAL NOT NULL,
    unrealized_pnl REAL NOT NULL,
    running_pnl REAL NOT NULL,
    equity_estimate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS live_execution_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    enabled INTEGER NOT NULL DEFAULT 0,
    starting_balance_usdc REAL,
    entry_slippage_bps REAL NOT NULL DEFAULT 25,
    exit_slippage_bps REAL NOT NULL DEFAULT 25,
    max_chase_bps REAL NOT NULL DEFAULT 100,
    copytrade_capital_mode TEXT NOT NULL DEFAULT 'CONSERVATIVE',
    min_cash_reserve_usdc REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS live_copytrade_settings (
    proxy_wallet TEXT PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    sizing_mode TEXT NOT NULL DEFAULT 'PERCENT',
    size_value REAL NOT NULL DEFAULT 10,
    max_usdc REAL NOT NULL DEFAULT 100,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS live_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_wallet TEXT NOT NULL DEFAULT '',
    source_transaction_hash TEXT NOT NULL DEFAULT '',
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    asset TEXT NOT NULL DEFAULT '',
    condition_id TEXT NOT NULL DEFAULT '',
    requested_usdc REAL NOT NULL,
    requested_size REAL NOT NULL,
    limit_price REAL NOT NULL,
    status TEXT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    clob_order_id TEXT NOT NULL DEFAULT '',
    raw_response TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE(source_type, source_transaction_hash, strategy)
);

CREATE TABLE IF NOT EXISTS live_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    source_wallet TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    asset TEXT NOT NULL DEFAULT '',
    condition_id TEXT NOT NULL DEFAULT '',
    entry_price REAL NOT NULL,
    size REAL NOT NULL,
    cost_usdc REAL NOT NULL,
    status TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    exit_price REAL,
    exit_value_usdc REAL,
    pnl_usdc REAL,
    close_reason TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS live_account_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observed_at TEXT NOT NULL,
    balance_usdc REAL NOT NULL,
    open_cost_usdc REAL NOT NULL,
    open_market_value_usdc REAL NOT NULL DEFAULT 0,
    realized_pnl_usdc REAL NOT NULL,
    unrealized_pnl_usdc REAL NOT NULL DEFAULT 0,
    running_pnl_usdc REAL NOT NULL DEFAULT 0,
    equity_estimate_usdc REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS watchlist_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proxy_wallet TEXT NOT NULL,
    transaction_hash TEXT NOT NULL UNIQUE,
    alert_type TEXT NOT NULL,
    title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    usdc_size REAL NOT NULL,
    trade_timestamp INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    seen INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS arbitrage_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signature TEXT NOT NULL UNIQUE,
    market_id TEXT NOT NULL,
    question TEXT NOT NULL,
    condition_id TEXT NOT NULL,
    yes_price REAL NOT NULL,
    no_price REAL NOT NULL,
    net_profit_bps REAL NOT NULL,
    max_size REAL NOT NULL,
    created_at TEXT NOT NULL,
    seen INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_trades_wallet_time ON trades(proxy_wallet, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_positions_wallet_time ON closed_positions(proxy_wallet, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_markouts_tx ON trade_markouts(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_watchlist_alerts_created ON watchlist_alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_arbitrage_alerts_created ON arbitrage_alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_paper_orders_created ON paper_orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_paper_positions_status ON paper_positions(status, opened_at DESC);
CREATE INDEX IF NOT EXISTS idx_paper_mark_snapshots_position ON paper_mark_snapshots(position_id, observed_at ASC);
CREATE INDEX IF NOT EXISTS idx_paper_events_created ON paper_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_paper_account_snapshots_observed ON paper_account_snapshots(observed_at ASC);
CREATE INDEX IF NOT EXISTS idx_live_account_snapshots_observed ON live_account_snapshots(observed_at ASC);
"""


@contextmanager
def connect_database(database_path: str) -> Iterator[sqlite3.Connection]:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.executescript(SCHEMA)
        _run_migrations(connection)
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _run_migrations(connection: sqlite3.Connection) -> None:
    watchlist_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(watchlist)").fetchall()
    }
    if "alerts_enabled" not in watchlist_columns:
        connection.execute("ALTER TABLE watchlist ADD COLUMN alerts_enabled INTEGER NOT NULL DEFAULT 1")

    position_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(paper_positions)").fetchall()
    }
    if "observed_entry_price" not in position_columns:
        connection.execute("ALTER TABLE paper_positions ADD COLUMN observed_entry_price REAL")
    if "entry_fee_usdc" not in position_columns:
        connection.execute("ALTER TABLE paper_positions ADD COLUMN entry_fee_usdc REAL NOT NULL DEFAULT 0")
    if "observed_exit_price" not in position_columns:
        connection.execute("ALTER TABLE paper_positions ADD COLUMN observed_exit_price REAL")
    if "exit_fee_usdc" not in position_columns:
        connection.execute("ALTER TABLE paper_positions ADD COLUMN exit_fee_usdc REAL NOT NULL DEFAULT 0")

    execution_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(paper_execution_settings)").fetchall()
    }
    if "copytrade_capital_mode" not in execution_columns:
        connection.execute(
            "ALTER TABLE paper_execution_settings ADD COLUMN copytrade_capital_mode TEXT NOT NULL DEFAULT 'CONSERVATIVE'"
        )
    if "min_cash_reserve_usdc" not in execution_columns:
        connection.execute(
            "ALTER TABLE paper_execution_settings ADD COLUMN min_cash_reserve_usdc REAL NOT NULL DEFAULT 0"
        )

    live_execution_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(live_execution_settings)").fetchall()
    }
    live_execution_defaults = {
        "entry_slippage_bps": "REAL NOT NULL DEFAULT 25",
        "exit_slippage_bps": "REAL NOT NULL DEFAULT 25",
        "max_chase_bps": "REAL NOT NULL DEFAULT 100",
        "copytrade_capital_mode": "TEXT NOT NULL DEFAULT 'CONSERVATIVE'",
        "min_cash_reserve_usdc": "REAL NOT NULL DEFAULT 0",
        "min_trade_usdc": "REAL NOT NULL DEFAULT 1",
    }
    for column, definition in live_execution_defaults.items():
        if column not in live_execution_columns:
            connection.execute(f"ALTER TABLE live_execution_settings ADD COLUMN {column} {definition}")

    live_snapshot_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(live_account_snapshots)").fetchall()
    }
    live_snapshot_defaults = {
        "open_market_value_usdc": "REAL NOT NULL DEFAULT 0",
        "unrealized_pnl_usdc": "REAL NOT NULL DEFAULT 0",
        "running_pnl_usdc": "REAL NOT NULL DEFAULT 0",
    }
    for column, definition in live_snapshot_defaults.items():
        if column not in live_snapshot_columns:
            connection.execute(f"ALTER TABLE live_account_snapshots ADD COLUMN {column} {definition}")

    live_position_columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(live_positions)").fetchall()
    }
    live_position_defaults = {
        "entry_fee_usdc": "REAL NOT NULL DEFAULT 0",
        "exit_fee_usdc": "REAL NOT NULL DEFAULT 0",
    }
    for column, definition in live_position_defaults.items():
        if column not in live_position_columns:
            connection.execute(f"ALTER TABLE live_positions ADD COLUMN {column} {definition}")

    setting_rows = connection.execute(
        """
        SELECT *
        FROM copytrade_settings
        ORDER BY lower(proxy_wallet), updated_at DESC, created_at DESC
        """
    ).fetchall()
    latest_by_wallet = {}
    for row in setting_rows:
        key = str(row["proxy_wallet"]).lower()
        if key not in latest_by_wallet:
            latest_by_wallet[key] = row
    if len(latest_by_wallet) != len(setting_rows):
        connection.execute("DELETE FROM copytrade_settings")
        for key, row in latest_by_wallet.items():
            connection.execute(
                """
                INSERT INTO copytrade_settings (
                    proxy_wallet, enabled, sizing_mode, size_value, max_usdc, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    int(row["enabled"]),
                    str(row["sizing_mode"]),
                    float(row["size_value"]),
                    float(row["max_usdc"]),
                    str(row["created_at"]),
                    str(row["updated_at"]),
                ),
            )
