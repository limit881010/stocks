---
name: yahoo-stock
description: Analyzes stock data and generates technical signals using Yahoo Finance. Use when the user asks for analysis of a specific stock ticker using this specific tool, or asks for "yahoo stock analysis" or mentions "get_info" or "signal" scripts. Provides RSI, MACD, MA, and simple trend signals.
---

# Yahoo Stock Analysis Skill

## Overview

This skill uses Yahoo Finance (`yfinance`) to fetch historical stock data and calculates technical indicators to provide a snapshot analysis and trading signals.

## Capabilities

- **Market Data**: Current price, target price, analyst rating.
- **Valuation**: PE, P/B, PEG, EPS.
- **Financials**: Margins (Gross, Operating), ROE, ROA, Debt/Equity.
- **Technical Indicators**: 
    - Moving Averages (MA10, MA20, MA50)
    - MACD (Moving Average Convergence Divergence)
    - RSI (Relative Strength Index)
    - Volume Analysis
- **Signals**: Generates buy/sell/hold signals based on MA crossover, RSI levels, and MACD.

## Usage

Run the `analyze.py` script with a ticker symbol.

### Analyze a Stock

To analyze a stock (e.g., NVIDIA):
```bash
python scripts/analyze.py NVDA
```

To analyze a Taiwan stock (e.g., TSMC):
```bash
python scripts/analyze.py 2330.TW
```

## Output Interpretation

The script outputs two main sections:
1. **Fundamental & Data Overview**: A table of valuation, financial, and basic price data.
2. **Technical Analysis**: 
    - Recent 10 days of price and indicator values.
    - **Trend Analysis**: Bullish/Bearish based on MA alignment.
    - **Signals**: MACD Golden/Death Cross, RSI Overbought/Oversold.
    - **Volume**: Analysis of volume trends relative to 20-day average.

## Requirements

- Python 3.x
- `yfinance`
- `pandas`
- `numpy`

(Note: Ensure these packages are installed in the environment)
