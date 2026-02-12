import pandas as pd
import yfinance as yf
import time
from bb_volume_strategy import fetch_data, add_indicators, run_backtest
from datetime import datetime, timedelta
from bb_volume_strategy import (
    strategy_volatility_breakout, 
    strategy_volume_reversal, 
    strategy_w_bottom, 
    strategy_bb_squeeze_momentum,
    strategy_ichimoku_cloud,
    strategy_mean_reversion,
    strategy_dbb_trend, 
    strategy_percent_b_mfi
)
from fetch_top_stocks import get_top_market_cap_tickers

# Fetch top 150 stocks by market capitalization (uses cache to save FinLab quota)
print("Loading top 150 Taiwan stocks by market cap...")
POSSIBLE_TICKERS = get_top_market_cap_tickers(150, use_cache=True)

# Fallback to a small list if fetching fails
if not POSSIBLE_TICKERS:
    print("Warning: Failed to load ticker list. Using fallback list.")
    POSSIBLE_TICKERS = [
        '2330.TW', '2454.TW', '2317.TW', '2308.TW', '2382.TW', '2303.TW',
        '2881.TW', '2882.TW', '2886.TW', '2891.TW',
        '1101.TW', '2002.TW', '1301.TW', '1303.TW'
    ]
else:
    print(f"Successfully loaded {len(POSSIBLE_TICKERS)} tickers for scanning.")
    print("💡 Tip: Run 'python fetch_top_stocks.py --refresh' to update the list from FinLab\n")



def fetch_data_local(ticker, start='2025-01-01'):
    import yfinance as yf
    try:
        # Use threads=False to avoid potential threading issues with cache
        # Changed start date to force cache invalidation if any
        df = yf.download(ticker, start=start, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            try: df.columns = df.columns.droplevel(1)
            except: pass
        if len(df) > 0:
            pass # print(f"DEBUG: {ticker} Tail:\n{df.tail(1)}")
        return df

    except Exception as e:
        return pd.DataFrame()

def scan_stocks(tickers, output_file='scan_results_with_stats.csv'):
    results = []
    
    print(f"Scanning {len(tickers)} stocks for Buy Signals + Win Rate Analysis...")
    print("-" * 85)
    
    for ticker in tickers:
        try:
            # print(f"Fetching data for {ticker}...", end='\r')
            time.sleep(0.1) # Rate limit protection
            
            # Fetch data using local function to avoid import issues
            # Use '2025-01-01' to align with new fetch logic
            df = fetch_data_local(ticker, start='2025-01-01')
            
            # If download failed and using .TW suffix, try .TWO (OTC stocks)
            if len(df) < 50 and ticker.endswith('.TW'):
                alternate_ticker = ticker.replace('.TW', '.TWO')
                # print(f"Retrying {ticker} as {alternate_ticker}...", end='\r')
                time.sleep(0.1)
                df = fetch_data_local(alternate_ticker, start='2025-01-01')
                
                # If successful with .TWO, use alternate ticker for results
                if len(df) >= 50:
                    ticker = alternate_ticker
            
            if len(df) < 50: 
                continue
                
            df = add_indicators(df)
            
            # Chikou Span (shifted -26) causes NaNs at the end (current dates).
            # We must drop it or ignore it to avoid dropping the most recent data.
            if 'Chikou' in df.columns:
                df = df.drop(columns=['Chikou'])
                
            df = df.dropna()
            
            # Define Strategies Map
            strategies = {
                "Vol Breakout": strategy_volatility_breakout(df),
                "Low Vol Reversal": strategy_volume_reversal(df),
                "W-Bottom": strategy_w_bottom(df),
                "BB Squeeze+Mom": strategy_bb_squeeze_momentum(df),
                "Ichimoku Cloud": strategy_ichimoku_cloud(df),
                "Mean Reversion": strategy_mean_reversion(df),
                "DBB Trend Entry": strategy_dbb_trend(df),
                "%B+MFI Reversal": strategy_percent_b_mfi(df)
            }
            
            last_idx = df.index[-1]
            last_close = df['Close'].iloc[-1]
            last_date_str = last_idx.strftime('%Y-%m-%d')
            
            # Check for data lag (e.g., > 4 days old)
            days_diff = (datetime.now() - last_idx).days
            if days_diff > 4:
                last_date_str = f"{last_date_str} (⚠️Old)"
            
            for strat_name, signal_series in strategies.items():
                if signal_series.iloc[-1] == 1:
                    # Signal Found! Now Verify it.
                    # Run backtest on this specific strategy
                    _, metrics = run_backtest(df, signal_series, title=strat_name, verbose=False)
                    
                    results.append({
                        'Ticker': ticker,
                        'Date': last_date_str,
                        'Strategy': strat_name,
                        'Close': last_close,
                        'WinRate': metrics['WinRate'], # Keep as float for sorting if needed
                        'Return': metrics['Return'],
                        'Trades': metrics['Trades']
                    })
                    
        except Exception as e:
            print(f"[Error] {ticker}: {e}")
            continue
            
    print("\n" + "-" * 85)
    print("SCAN COMPLETE")
    print(f"{'Ticker':<10} | {'Strategy':<18} | {'Price':<10} | {'WinRate':<7} | {'Return':<8}")
    print("-" * 85)
    
    if results:
        # Sort by WinRate descending
        results.sort(key=lambda x: x['WinRate'], reverse=True)
        
        for res in results:
             print(f"{res['Ticker']:<10} | {res['Strategy']:<18} | {res['Close']:<10.2f} | {res['WinRate']:>6.1f}% | {res['Return']:>7.1f}%")

        res_df = pd.DataFrame(results)
        res_df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
    else:
        print("No buy signals found today.")

if __name__ == "__main__":
    scan_stocks(POSSIBLE_TICKERS)
