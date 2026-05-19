# Prediction Market Arbitrage Bot

Phase 1 is a read-only Polymarket scanner. It fetches active markets, reads live CLOB order books, and reports theoretical binary arbitrage opportunities before any trading code exists.

## What Phase 1 Does

- Finds active, open Polymarket markets with CLOB token IDs.
- Fetches YES and NO order books.
- Calculates whether buying both sides costs less than the guaranteed $1 payout.
- Estimates taker fees when fee data is available.
- Prints opportunities above a configurable minimum net profit.

No wallet, private key, signing, or live order placement is used in this phase.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run

### Web Interface

```powershell
python -m src.web_app
```

Then open:

```text
http://127.0.0.1:5050
```

The web interface is still read-only. It runs the Phase 1 scanner from a local dashboard and does not place trades.

### Desktop App

The desktop app is an editable Electron wrapper around the same local Flask interface. It starts the local server automatically and opens the bot in a native window.

```powershell
npm install
npm run desktop
```

Or double-click:

```text
Start Desktop App.bat
```

To create a Windows portable build:

```powershell
npm run package:win
```

Or double-click:

```text
Build Desktop App.bat
```

The wrapper is intentionally editable: it still uses the project files in `src/`, `web/`, and `data/`. The portable build expects Python and the packages from `requirements.txt` to be available on the machine running it.

Tabs:

- Scanner: finds theoretical binary YES + NO arbitrage.
- Traders: loads the Polymarket leaderboard and recent public trades for top wallets.
- Smart Wallets: stores wallet observations locally and ranks wallets by repeatable signal quality.

The Traders tab can rank by a consistency score. It samples each wallet's recent closed positions, calculates win rate as profitable closed positions divided by winning plus losing closed positions, and filters for minimum recent activity.

The Smart Wallets tab is the start of a historical behavior engine. Click **Update Memory** to ingest current leaderboard candidates, their recent trades, closed positions, and short-term markout observations into a local SQLite database. Click **Rank Wallets** to score wallets using accumulated history:

- closed-position win rate
- observed realized PnL
- observed trade count and active days
- sample size
- average post-trade markout
- percentage of markouts moving in the trader's favor

This does not prove anyone has private information. It flags wallets whose public behavior looks information-advantaged enough to investigate.

Changing filters in the UI automatically refreshes the visible list after the tab has loaded. In Smart Wallets, changing candidate category or period also updates local memory for that slice before ranking it.

## Alerts

- Scanner tab: **Start Arb Alerts** checks for new arbitrage opportunities every 30 seconds.
- Watchlist trade alerts run automatically while the bot server is running, checking saved alert-enabled wallets every 30 seconds.
- The Watchlist UI also refreshes every 30 seconds while open so new saved-trader alerts and paper copytrades show up quickly.
- Alerts are stored locally and shown in-app. Browser notifications are used when the browser grants notification permission.

## Phase 2 Paper Trading

Paper Trading simulates orders only. No wallet, private key, signing, or live order placement is used.

- Arbitrage signals can create simulated binary YES+NO set orders.
- Saved traders can be enabled for paper copytrading.
- Copytrade sizing supports percent-of-source-trade or fixed USDC with a max-USDC cap.
- Copytrade entries are rejected if the requested paper size is larger than available paper cash.
- Low-cash copytrade rejections automatically turn copytrade off for that trader and create a paper risk event.
- Copied BUY trades open paper positions; copied SELL trades close matching open paper positions FIFO.
- The Paper Trading tab shows and edits the paper account balance.
- Running PnL marks open positions to current Polymarket outcome prices when available, then adds realized PnL.
- Account snapshots are stored so the Paper Trading tab can chart cash and equity over time.
- Open-position mark snapshots are stored over time so expanded trade charts can show the path, not only entry and current value.
- Simulated fills reserve paper cash and appear as active trades.
- Active paper trades can be manually closed with an exit price.
- **Settle Ended** reconciles old open paper positions from resolved market data and saved-trader closed-position history.
- Finished trades show realized PnL, win/loss count, and win rate.

## Guarded Live Copytrading

The Execution tab includes a guarded live copytrading panel. It is stopped by default and only submits real orders after pressing **Give Go** and confirming the browser prompt.

- Uses the same saved-trader Copytrade switches and sizing settings as Paper Trading.
- Uses the same execution assumptions for entry chase, capital mode, and minimum cash reserve.
- Submits fill-or-kill limit copy orders, not unlimited market orders.
- The **Kill Switch** immediately disables future live order submission.
- Live order attempts and bot-opened live positions are logged locally.

### Command Line

```powershell
python -m src.main scan --limit 25
```

Useful options:

```powershell
python -m src.main scan --limit 100 --min-profit-bps 15 --max-markets 50
python -m src.main scan --limit 50 --json
```

## Notes

This scanner reports theoretical top-of-book opportunities. Real execution can fail because order books move, available size is small, fees differ by market, or partial fills occur. Treat Phase 1 as discovery and measurement, not a trading system.
