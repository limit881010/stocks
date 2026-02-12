---
name: stock-scanner
description: Taiwan and US stock technical analysis scanner with portfolio tracking. Use when the user wants to (1) scan Taiwan or US stocks for buy signals ("掃描股票", "scan"), (2) track selected stocks in a watchlist, (3) monitor positions for sell signals ("追蹤"), or (4) manage their stock watchlist (add/remove positions). Scans top 150 Taiwan stocks by market cap OR user-specified US stocks using 8 technical strategies, presents results for user selection, and monitors tracked positions for exit signals.
---

# Taiwan & US Stock Scanner + Portfolio Tracker

Scan Taiwan and US stocks for technical buy signals and track selected positions for sell signals.

## When to Use This Skill

Use this skill when the user:
- Wants to scan Taiwan stocks: "掃描股票", "尋找買入機會", "find buy signals"
- Wants to track/monitor positions: "追蹤", "monitor my stocks", "check my positions"
- Wants to manage their watchlist: "add to watchlist", "remove from watchlist"

## First Time Setup

**For new users**, follow these steps to set up the stock scanner:

### Step 1: Install Required Packages

```bash
cd .agent/skills/stock-scanner
pip install -r requirements.txt
```

Required packages:
- `yfinance` - Fetch stock data from Yahoo Finance
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `matplotlib` - Plotting and visualization (for backtesting charts)

### Step 2: Initialize Data Files

Run the initialization script to create required data files:

```bash
cd scripts
python init_setup.py
```

This will create empty data files if they don't exist:
- `watchlist.csv` - Empty watchlist (will be populated when you add stocks)
- `scan_results_with_stats.csv` - Taiwan scan results (populated by scanner)
- `us_scan_results_with_stats.csv` - US scan results (populated by scanner)

**Note**: The `top_market_cap_stocks.txt` cache file will be automatically created on your first Taiwan stock scan.

## Core Workflow

### 1. Scan for Buy Signals

Execute the scanner to find stocks with technical buy signals:

```bash
cd .agent/skills/stock-scanner/scripts
python run_scanner.py
```

The scanner:
- Scans top 150 Taiwan stocks by market cap
- Tests 8 technical strategies per stock
- Backtests each signal to verify win rate
- Saves results to `strategy/scan_results_with_stats.csv`
- Automatically retries OTC stocks with `.TWO` suffix if `.TW` fails

**Output**: Table of stocks with buy signals, sorted by win rate.

### 1b. Scan US Stocks for Buy Signals

Execute the US stock scanner to find buy signals among specified tech stocks:

```bash
cd .agent/skills/stock-scanner/scripts
python run_us_scanner.py
```

The scanner:
- Scans 15 US tech stocks (AAPL, NVDA, MSFT, GOOGL, AMZN, META, TSLA, AVGO, ADBE, CRM, INTC, AMD, QCOM, TXN, MU)
- Tests 8 technical strategies per stock
- Backtests each signal to verify win rate
- Saves results to `us_scan_results_with_stats.csv`

**Customizing US Stock List**: Edit `us_stocks_list.py` to change the stocks to scan.

**Output**: Table of US stocks with buy signals, sorted by win rate.

### 2. Select Stocks for Tracking

After scanning, help the user select stocks to track. Present the scan results and ask which stocks they want to add to their watchlist.

**Example conversation:**
```
ASSISTANT: "掃描完成！找到 26 個買入訊號。以下是勝率最高的前 10 個：
1. 2886.TW - W-Bottom (勝率 100%, 回報 9.7%)
2. 2606.TW - %B+MFI Reversal (勝率 66.7%, 回報 12.1%)
...

你想追蹤哪些股票？請提供股票代碼，例如：2886.TW 2606.TW"

USER: "2886.TW 2606.TW 3034.TW"
```

**Note**: The add_to_watchlist script automatically detects whether you're adding Taiwan stocks (ending in .TW/.TWO) or US stocks, and searches the appropriate scan results files.

Then add selected stocks (works for both Taiwan and US stocks):

```bash
cd .agent/skills/stock-scanner/scripts
python add_to_watchlist.py 2886.TW 2606.TW 3034.TW
# or for US stocks:
python add_to_watchlist.py AMZN NVDA AAPL
```

### 3. Monitor Portfolio

Check tracked positions for sell signals:

```bash
cd .agent/skills/stock-scanner/scripts
python monitor_portfolio.py
```

The monitor:
- Loads watchlist from `watchlist.csv` (supports both Taiwan and US stocks)
- Fetches current prices for all positions
- Checks each position's strategy for sell signal (-1)
- Calculates P&L and holding period
- Highlights positions with sell signals

**Quick Status Check**: For a simple price update without full technical analysis:
```bash
python status.py
```

**Output**: Portfolio status table + sell signal alerts.

### 4. Manage Watchlist

**Show current watchlist:**
```bash
cd .agent/skills/stock-scanner/scripts
python show_watchlist.py
```

**Remove positions:**
```bash
cd .agent/skills/stock-scanner/scripts
python remove_from_watchlist.py 2330.TW 2454.TW
```

## Technical Strategies

The scanner tests 8 strategies per stock:

1. **Vol Breakout** - Volume surge with price breakout
2. **Low Vol Reversal** - Oversold reversal with volume spike
3. **W-Bottom** - W pattern base with volume confirmation
4. **BB Squeeze+Mom** - Bollinger squeeze with momentum
5. **Ichimoku Cloud** - Cloud breakout signal
6. **Mean Reversion** - Price stretched from mean
7. **DBB Trend Entry** - Donchian breakout
8. **%B+MFI Reversal** - %B oversold + MFI divergence

Each signal is backtested to verify win rate and expected return.

## Data Files

- `scan_results_with_stats.csv` - Latest Taiwan stock scan results
- `us_scan_results_with_stats.csv` - Latest US stock scan results
- `watchlist.csv` - User's tracked positions (supports both TW and US stocks)
- `top_market_cap_stocks.txt` - Cached top 150 Taiwan stocks (30-day validity)
- `us_stocks_list.py` - List of US stocks to scan (customizable)

## Important Notes

- **First Time Setup**: Run `python init_setup.py` to create required data files if they don't exist
- **Cache**: Stock list cached for 30 days. Refresh with `python strategy/fetch_top_stocks.py --refresh`
- **OTC Stocks**: Scanner automatically retries with `.TWO` suffix if `.TW` fails
- **Watchlist**: Adding stocks appends to existing watchlist (not replace)
- **API Quota**: Scanning uses 0 MB FinLab quota (relies on cache), monitoring uses yfinance (free)
- **Missing Data Files**: If you encounter "file not found" errors, run `init_setup.py` first

## Example Usage Sessions

### Taiwan Stock Scanning
```
USER: "掃描股票"

ASSISTANT: [Runs run_scanner.py]
         [Presents results]
         "找到 26 個買入訊號。你想追蹤哪些股票？"

USER: "2886.TW 2606.TW"

ASSISTANT: [Runs add_to_watchlist.py 2886.TW 2606.TW]
         "已加入 2 個部位到追蹤清單！"

USER: "追蹤"

ASSISTANT: [Runs monitor_portfolio.py]
         [Shows portfolio status with sell signals]
```

### US Stock Scanning
```
USER: "scan"

ASSISTANT: [Runs run_us_scanner.py]
         [Presents US stock results]
         "Found 4 buy signals. Which stocks do you want to track?"

USER: "加入觀察清單 AMZN"

ASSISTANT: [Runs add_to_watchlist.py AMZN]
         "✅ Successfully added AMZN to watchlist!"

USER: "追蹤"

ASSISTANT: [Runs monitor_portfolio.py]
         [Shows mixed TW/US portfolio status]
```
