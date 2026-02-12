import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_data(ticker, start='2024-01-01', end=None):
    print(f"Fetching data for {ticker}...")
    df = yf.download(ticker, start=start, end=end, progress=False)
    
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        try:
             df.columns = df.columns.droplevel(1)
        except:
             pass
    
    # Ensure essentials exist
    if 'Close' not in df.columns or 'Volume' not in df.columns:
        raise ValueError("Close price or Volume not found")
        
    
    if len(df) > 0:
        print(f"DEBUG: Fetched {len(df)} rows. Last: {df.index[-1]}")
    else:
        print("DEBUG: Fetched EMPTY dataframe")
        
    return df

def plot_combined_signals(df, signals_dict, filename):
    plt.figure(figsize=(16, 8))
    
    # Plot Price and Bands
    plt.plot(df.index, df['Close'], label='Close Price', alpha=0.5, color='gray')
    plt.plot(df.index, df['Upper_Band'], label='Upper Band', color='green', alpha=0.1)
    plt.plot(df.index, df['Lower_Band'], label='Lower Band', color='red', alpha=0.1)
    plt.fill_between(df.index, df['Upper_Band'], df['Lower_Band'], color='gray', alpha=0.05)
    
    # Define styles for each strategy
    styles = {
        'Vol Breakout': {'color': 'purple', 'marker': '^', 'offset': 0},
        'Low Vol Reversal': {'color': 'blue', 'marker': 'o', 'offset': 0},
        'W-Bottom': {'color': 'orange', 'marker': 's', 'offset': 0},
        'BB Squeeze+Mom': {'color': 'red', 'marker': 'D', 'offset': 0},
        'Ichimoku Cloud': {'color': 'green', 'marker': 'v', 'offset': 0},
        'Mean Reversion': {'color': 'brown', 'marker': 'p', 'offset': 0},
        'DBB Trend': {'color': 'cyan', 'marker': 'P', 'offset': 0},
        '%B+MFI': {'color': 'magenta', 'marker': '*', 'offset': 0}
    }
    
    for name, signals in signals_dict.items():
        style = styles.get(name, {'color': 'black', 'marker': 'x'})
        
        buys = df[signals == 1]
        sells = df[signals == -1]
        
        plt.scatter(buys.index, buys['Close'], label=f'{name} Buy', 
                   marker=style['marker'], color=style['color'], s=80, zorder=5)
                   
        # Optional: Plot sells if needed, or just buys to reduce clutter
        # plt.scatter(sells.index, sells['Close'], label=f'{name} Sell', 
        #            marker='v', color=style['color'], s=60, alpha=0.5)

    plt.title(f'Combined Strategy Signals - {filename.replace(".png", "")}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(filename)
    print(f"Saved combined plot: {filename}")

def add_indicators(df, window=20, num_std=2):
    df = df.copy()
    prices = df['Close']
    volume = df['Volume']
    
    # Basic BB
    df['SMA'] = prices.rolling(window=window).mean()
    df['StdDev'] = prices.rolling(window=window).std()
    df['Upper_Band'] = df['SMA'] + (df['StdDev'] * num_std)
    df['Lower_Band'] = df['SMA'] - (df['StdDev'] * num_std)
    
    # Bandwidth & %B (useful for Squeeze)
    df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['SMA']
    df['Percent_B'] = (prices - df['Lower_Band']) / (df['Upper_Band'] - df['Lower_Band'])
    
    # +1 Sigma Band (for Aggressive Trend Stop)
    df['Upper_1std'] = df['SMA'] + df['StdDev']
    
    # ATR Calculation (for Chandelier Exit)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=20).mean() # Changed to 20 period to match KC
    
    # -----------------------------------------------------
    # Keltner Channels (KC) for TTM Squeeze
    # KC Middle = 20 EMA
    # KC Upper = 20 EMA + 1.5 * ATR (using 20 period for consistency)
    # Typically TTM uses 20 SMA or EMA. Let's use 20 SMA for middle to match BB, but strict definition often uses EMA.
    # Let's use standard: Period 20.
    
    # Re-calc ATR for KC if needed (KC often uses SMA of TR). Use 'ATR' column as proxy.
    df['KC_Middle'] = prices.rolling(window=20).mean() # Using SMA for alignment with BB center
    df['KC_Upper'] = df['KC_Middle'] + (1.5 * df['ATR'])
    df['KC_Lower'] = df['KC_Middle'] - (1.5 * df['ATR'])
    
    # -----------------------------------------------------
    # Money Flow Index (MFI) for %B Strategy
    # Formula: 100 - 100 / (1 + Money Ratio)
    # Money Flow = Typical Price * Volume
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    raw_money_flow = typical_price * volume
    
    positive_flow = pd.Series(0.0, index=df.index)
    negative_flow = pd.Series(0.0, index=df.index)
    
    # Compare Typical Price with previous day
    tp_change = typical_price.diff()
    
    positive_flow[tp_change > 0] = raw_money_flow[tp_change > 0]
    negative_flow[tp_change < 0] = raw_money_flow[tp_change < 0]
    
    mfi_period = 14
    pos_mf_sum = positive_flow.rolling(window=mfi_period).sum()
    neg_mf_sum = negative_flow.rolling(window=mfi_period).sum()
    
    # Handle division by zero
    # If neg_mf_sum is 0, money_ratio diverges.
    # Use where to replace 0 with a small epsilon
    money_ratio = pos_mf_sum / neg_mf_sum.where(neg_mf_sum != 0, 1e-10)
    df['MFI'] = 100 - (100 / (1 + money_ratio))
    
    # Relative Volume (RVOL)
    # RVOL = Current Volume / SMA20 Volume
    df['Vol_SMA'] = volume.rolling(window=window).mean()
    # Handle division by zero
    df['RVOL'] = np.where(df['Vol_SMA'] > 0, volume / df['Vol_SMA'], 0)
    
    # -----------------------------------------------------
    # MACD (Moving Average Convergence Divergence) for Momentum Filter
    # MACD Line = 12 EMA - 26 EMA
    # Signal Line = 9 EMA of MACD
    # Histogram = MACD - Signal
    ema_12 = prices.ewm(span=12, adjust=False).mean()
    ema_26 = prices.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # -----------------------------------------------------
    # RSI (Relative Strength Index) for Momentum Filter
    # RSI = 100 - (100 / (1 + RS))
    # RS = Average Gain / Average Loss
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    rs = avg_gain / avg_loss.where(avg_loss != 0, 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # -----------------------------------------------------
    # Ichimoku Cloud Components
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Tenkan'] = (high_9 + low_9) / 2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Kijun'] = (high_26 + low_26) / 2
    
    # Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2, shifted forward +26
    df['Senkou_A'] = ((df['Tenkan'] + df['Kijun']) / 2).shift(26)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, shifted forward +26
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Senkou_B'] = ((high_52 + low_52) / 2).shift(26)
    
    # Chikou Span (Lagging Span): Close price shifted backward -26
    df['Chikou'] = prices.shift(-26)
    
    # Cloud boundaries (for easier logic)
    df['Cloud_Top'] = df[['Senkou_A', 'Senkou_B']].max(axis=1)
    df['Cloud_Bottom'] = df[['Senkou_A', 'Senkou_B']].min(axis=1)
    
    return df

def strategy_volatility_breakout(df, rvol_threshold=1.5, squeeze_percentile=0.20):
    """
    1. Squeeze: Bandwidth is low (in lowest 20th percentile of history).
    2. Breakout: Price closes > Upper Band.
    3. Volume Confirmation: RVOL > Threshold.
    """
    df = df.copy()
    signals = pd.Series(0, index=df.index) # 0: None, 1: Buy, -1: Sell
    
    # Calculate dynamic squeeze threshold (rolling or static history? let's use rolling 6-month percentile for adaptiveness or static)
    # For simplicity, using rolling percentile to define "relative low volatility"
    # Squeeze is when Bandwidth < Rolling Quantile(20%)
    # Use fillna with global quantile to handle short history
    global_low_bw = df['Bandwidth'].quantile(squeeze_percentile)
    rolling_low_bandwidth = df['Bandwidth'].rolling(window=120).quantile(squeeze_percentile).fillna(global_low_bw)
    
    is_squeeze = df['Bandwidth'] < rolling_low_bandwidth
    breakout_up = df['Close'] > df['Upper_Band']
    breakout_down = df['Close'] < df['Lower_Band'] # Optional: Short logic
    high_volume = df['RVOL'] > rvol_threshold
    
    # Buy Signal
    buy_condition = is_squeeze & breakout_up & high_volume
    signals[buy_condition] = 1
    
    # Exit Rule (Simple): Close < SMA (Trend reversal)
    exit_condition = df['Close'] < df['SMA']
    signals[exit_condition] = -1 # Force exit
    
    return signals

def strategy_volume_reversal(df):
    """
    A twist on Divergence:
    Sell if Price > Upper Band AND RVOL < 0.8 (Weak Volume High) -> Mean Reversion Short
    Buy if Price < Lower Band AND RVOL < 0.8 (Weak Volume Low) -> Mean Reversion Long
    
    Note: "Divergence" often requires comparing peaks, which is complex. 
    This is a simplified "Low Volume Extremum" strategy.
    """
    signals = pd.Series(0, index=df.index)
    
    # Bearish Reversal (Short/Exit)
    # Price makes a high (above Upper) but Volume is weak relative to average
    sell_cond = (df['Close'] > df['Upper_Band']) & (df['RVOL'] < 0.8)
    signals[sell_cond] = -1
    
    # Bullish Reversal (Long)
    buy_cond = (df['Close'] < df['Lower_Band']) & (df['RVOL'] < 0.8)
    signals[buy_cond] = 1
    
    # Exit: Touch SMA
    # For backtest engine, we'll handle state. Here we just mark entry intent?
    # Actually, let's keep signals simple: 1 = Buy Entry, -1 = Sell Entry/Exit
    
    return signals

def strategy_bb_squeeze_momentum(df):
    """
    BB Squeeze + Momentum Filter:
    1. Squeeze ON: BB is inside KC (Low Volatility)
    2. Squeeze OFF (Fire): BB expands outside KC (Volatility Explosion)
    3. Entry: Squeeze ends + MACD Histogram > 0 + RSI > 50
    4. Exit: MACD bear cross OR price < SMA
    """
    signals = pd.Series(0, index=df.index)
    
    # Squeeze Condition: BB completely inside KC
    squeeze_on = (df['Upper_Band'] < df['KC_Upper']) & (df['Lower_Band'] > df['KC_Lower'])
    
    # Detect when squeeze turns OFF (Fires)
    squeeze_off = (~squeeze_on) & (squeeze_on.shift(1))
    
    # Momentum Filters
    macd_positive = df['MACD_Hist'] > 0
    rsi_bullish = df['RSI'] > 50
    
    # Buy Signal: Squeeze fires + MACD histogram positive + RSI > 50
    buy_cond = squeeze_off & macd_positive & rsi_bullish
    signals[buy_cond] = 1
    
    # Exit Conditions:
    # 1. MACD bear cross (MACD < Signal)
    # 2. Price < SMA (trend reversal)
    macd_bear_cross = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
    price_below_sma = df['Close'] < df['SMA']
    
    exit_cond = macd_bear_cross | price_below_sma
    signals[exit_cond] = -1
    
    return signals

def strategy_dbb_trend(df):
    """
    Double Bollinger Bands (DBB) Trend Following (Kathy Lien):
    - Buy Zone: Price between +1 Std and +2 Std (Upper Band).
    - Neutral: Price between -1 and +1.
    - Sell Zone: Price between -1 and -2.
    
    Signal: 
    - Buy (Enter/Hold) when Price > +1 StdDev. 
    - Exit when Price Close < +1 StdDev.
    """
    signals = pd.Series(0, index=df.index)
    
    # DBB Logic is a "State". 
    # If Close > Upper_1std -> Long State
    # If Close < Upper_1std -> Neutral/Short State -> Exit Long
    
    # We generate entry signal when crossing into Buy Zone
    enter_buy_zone = (df['Close'] > df['Upper_1std']) & (df['Close'].shift(1) <= df['Upper_1std'].shift(1))
    signals[enter_buy_zone] = 1
    
    # Exit when falling out of Buy Zone
    exit_buy_zone = (df['Close'] < df['Upper_1std'])
    signals[exit_buy_zone] = -1
    
    return signals

def strategy_percent_b_mfi(df):
    """
    %B + MFI Reversal:
    - Buy: %B < 0 (Price < Lower Band) AND MFI > 20 (Not super weak) OR MFI divergence (simplified to MFI rising).
    - Simplified: %B < 0 AND MFI < 30 (Oversold but look for turn?) 
      Standard logic: Price makes low (%B < 0), MFI > 20 or MFI rising.
      Let's use: Close < Lower Band (%B < 0) AND MFI > 25 (Money Flow not dead).
    """
    signals = pd.Series(0, index=df.index)
    
    # Oversold but Money Flowing in?
    # Or just extreme reversion: %B < 0 is rare. 
    # Condition: Close < Lower Band AND MFI > 20 (Kathy Lien often suggests MFI > 80 for top, < 20 for bottom, but here we want divergence)
    # Let's try: Price < Lower Band AND MFI is NOT < 20 (meaning accumulation?) 
    # Or simply: Price < Lower Band. MFI direction?
    
    # Implementation:
    # Buy: %B < 0 (Price < Lower) 
    # Check extra filter: Trend filter? No, this is reversion.
    # Filter: MFI > 30 (Money is actually supporting)
    
    buy_cond = (df['Percent_B'] < 0) & (df['MFI'] > 30)
    signals[buy_cond] = 1
    
    # Exit: %B > 0.8 or MFI > 80
    exit_cond = (df['Percent_B'] > 0.8)
    signals[exit_cond] = -1
    
    return signals

def strategy_ichimoku_cloud(df):
    """
    Ichimoku Cloud (一目均衡表):
    Entry: Price > Cloud (bullish) + Tenkan crosses above Kijun (bullish TK cross)
    Exit: Price < Cloud OR Tenkan crosses below Kijun (bear TK cross)
    """
    signals = pd.Series(0, index=df.index)
    
    # Price above/below cloud
    price_above_cloud = df['Close'] > df['Cloud_Top']
    price_below_cloud = df['Close'] < df['Cloud_Bottom']
    
    # TK Cross (Tenkan-Kijun cross)
    tk_bull_cross = (df['Tenkan'] > df['Kijun']) & (df['Tenkan'].shift(1) <= df['Kijun'].shift(1))
    tk_bear_cross = (df['Tenkan'] < df['Kijun']) & (df['Tenkan'].shift(1) >= df['Kijun'].shift(1))
    
    # Entry: Price above cloud + TK bullish cross
    buy_cond = price_above_cloud & tk_bull_cross
    signals[buy_cond] = 1
    
    # Exit: Price drops below cloud OR TK bearish cross
    exit_cond = price_below_cloud | tk_bear_cross
    signals[exit_cond] = -1
    
    return signals

def strategy_mean_reversion(df):
    """
    Mean Reversion with Standard Deviation:
    Entry: Price deviates > 2.5 StdDev from 20-day SMA (oversold)
    Exit: Price returns to within 0.5 StdDev of SMA
    Special: Designed for high-volatility mean-reverting assets (e.g., crypto)
    """
    signals = pd.Series(0, index=df.index)
    
    # Calculate standard deviation
    # We already have Bandwidth which is (Upper - Lower) / SMA = 4 * StdDev / SMA
    # So StdDev = (Upper - Lower) / 4
    std_dev = (df['Upper_Band'] - df['Lower_Band']) / 4
    
    # Distance from SMA in terms of standard deviations
    distance_from_sma = (df['Close'] - df['SMA']) / std_dev
    
    # Entry: Price < SMA - 2.5 * StdDev (extreme oversold)
    buy_cond = distance_from_sma < -2.5
    signals[buy_cond] = 1
    
    # Exit: Price returns to SMA ± 0.5 StdDev (mean reversion complete)
    exit_cond = (distance_from_sma > -0.5) & (distance_from_sma < 0.5)
    signals[exit_cond] = -1
    
    return signals

def strategy_w_bottom(df):
    """
    Pattern: W-Bottom (Double Bottom)
    1. First Low (L1): Price makes a low (often below Lower Band).
    2. Bounce: Price rises.
    3. Second Low (L2): Price makes a new local low, which is HIGHER than L1 (Higher Low).
       Crucially, L2 should NOT be below the Lower Band (or at least stronger than L1).
    4. Volume Confirmation: Volume at L2 < Volume at L1 (Selling dries up).
    """
    signals = pd.Series(0, index=df.index)
    
    # Use localized minima detection to allow loops only on candidates
    # Find local minima (Low < prev, Low < next)
    # Using shift to find local extrema
    
    lows = df['Low']
    is_local_min = (lows < lows.shift(1)) & (lows < lows.shift(-1))
    
    # Get indices of local minima
    minima_indices = df.index[is_local_min]
    
    # We need position integer indices to look back easily
    minima_ilocs = [df.index.get_loc(idx) for idx in minima_indices]
    
    last_signal_idx = -999 # Debounce tracker
    
    # Loop only through local minima (Efficiency Improvement)
    # We need at least 2 minima to compare
    for current_idx in minima_ilocs:
        # Debounce check
        if current_idx - last_signal_idx < 10:
             continue
             
        if current_idx < 50: # Need history
            continue
            
        # This 'current_idx' is a candidate for the Second Low (Right leg of W)
        current_low_price = df['Low'].iloc[current_idx]
        current_vol = df['Volume'].iloc[current_idx]
        current_lower_band = df['Lower_Band'].iloc[current_idx]
        
        # Second Low Condition:
        # 1. Ideally > Lower Band (Indicates strength relative to bands) - optional but good for W
        # User requested strict check: L2 must NOT be below Lower Band.
        if current_low_price <= current_lower_band:
            continue
            
        # 2. Must be a clear local low (already satisfied by is_local_min)
        
        # Look back for the First Low (Left leg)
        # Search window: e.g., 5 to 50 days ago (Widened)
        window_start = max(0, current_idx - 50)
        window_end = max(0, current_idx - 5)
        
        # We need to find the absolute minimum in this lookback window to be the "First Low"
        
        lookback_window = df.iloc[window_start:window_end]
        if lookback_window.empty:
            continue
            
        first_low_price = lookback_window['Low'].min()
        
        # Condition 3: Regular W-Bottom -> Second Low > First Low
        if current_low_price <= first_low_price:
            continue
            
        # Find exactly when that first low happened to check volume/bands
        # idxmin returns the index (Datetime), we need iloc
        try:
            first_low_dt_idx = lookback_window['Low'].idxmin()
            first_low_loc = df.index.get_loc(first_low_dt_idx)
        except:
             continue
             
        first_low_vol = df['Volume'].iloc[first_low_loc]
        first_lower_band = df['Lower_Band'].iloc[first_low_loc]
        
        # Condition 1: First Low was "Deep" (e.g. < Lower Band or very close)
        # Strict Check: Must be < Lower Band (or at least <=). 
        # User requested: strict check.
        if first_low_price >= first_lower_band: 
            continue
            
        # Condition 2: Second Low is Higher than First Low (Verified above)
        
        # Condition 4: Volume confirmation (Second Low Vol < First Low Vol)
        if current_vol >= first_low_vol:
             continue
             
        # If all pass, we have a W-Bottom Candidate at 'current_idx'.
        # Signal is usually taken on the "Bounce" from the second low.
        # But here we are at the exact low day (or 1 day after since we use shift(-1) to know it's a low?)
        # Since we use shift(-1), we can't know it's a local min until the NEXT day.
        # So the signal should be placed at current_idx + 1 (Today)
        
        signal_day = current_idx + 1
        if signal_day < len(df):
            # Confirmation: Close > Open (Green candle)
            if df['Close'].iloc[signal_day] > df['Open'].iloc[signal_day]:
                signals.iloc[signal_day] = 1
                last_signal_idx = signal_day
                
    # Exit condition: "Trend Reversal"
    # Original: Close > SMA. 
    # New: Hold longer for reversal play. Exit when price hits Upper Band (Target).
    exit_cond = df['Close'] > df['Upper_Band']
    signals[exit_cond] = -1
    
    return signals

def run_backtest(df, signal_series, title="Strategy", stop_loss_type=None, verbose=True):
    """
    Backtest with Stop Loss support.
    Returns equity curve and metrics dict.
    """
    capital = 1_000_000
    cash = capital
    position = 0
    
    prices = df['Close']
    atr = df['ATR'] if 'ATR' in df.columns else pd.Series(0, index=df.index)
    upper_1std = df['Upper_1std']
    sma = df['SMA']
    
    equity = []
    trades = [] # List of (Entry, Exit, PnL%)
    
    entry_price = 0
    highest_high = 0 # For Chandelier
    
    for i in range(len(df)):
        price = prices.iloc[i]
        sig = signal_series.iloc[i]
        curr_atr = atr.iloc[i]
        
        # Check Stop Loss first (if in position)
        if position > 0:
            # Update Highest High for Chandelier
            if price > highest_high:
                highest_high = price
                
            exit_signal = False
            exit_reason = "Signal"
            
            if stop_loss_type == 'chandelier':
                stop_price = highest_high - (3.0 * curr_atr)
                if price < stop_price:
                    exit_signal = True
                    exit_reason = "SL_Chandelier"
            
            elif stop_loss_type == 'bb_trend_1std':
                if price < upper_1std.iloc[i]:
                    exit_signal = True
                    exit_reason = "SL_1Std"
                    
            elif stop_loss_type == 'bb_trend_sma':
                if price < sma.iloc[i]:
                    exit_signal = True
                    exit_reason = "SL_SMA"
            
            if exit_signal:
                pnl = (price - entry_price) / entry_price
                trades.append(pnl)
                cash += position * price
                position = 0
                # if verbose: print(f"  [Exit] {df.index[i].date()} {exit_reason} @ {price:.2f} PnL: {pnl*100:.2f}%")
        
        # Entry Logic
        if sig == 1 and position == 0:
            position = int(cash / price)
            cash -= position * price
            entry_price = price
            highest_high = price # Reset for Chandelier
            # if verbose: print(f"  [Buy]  {df.index[i].date()} @ {price:.2f}")
            
        # Normal Exit Logic (Signal -1)
        # Note: If Stop Loss already exited, position is 0, so this won't trigger
        elif sig == -1 and position > 0:
            pnl = (price - entry_price) / entry_price
            trades.append(pnl)
            cash += position * price
            position = 0
            # if verbose: print(f"  [Sell] {df.index[i].date()} @ {price:.2f} PnL: {pnl*100:.2f}%")
            
        equity.append(cash + position * price)
    
    # Close final position
    if position > 0:
        pnl = (prices.iloc[-1] - entry_price) / entry_price
        trades.append(pnl)
        cash += position * prices.iloc[-1]
        
    final_val = equity[-1] if len(equity) > 0 else capital
    ret = (final_val - capital) / capital * 100
    
    # Metrics
    win_count = len([t for t in trades if t > 0])
    total_trades = len(trades)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
    
    if verbose:
        print(f"[{title}] Return: {ret:.2f}% | Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
        
    return equity, {'Return': ret, 'WinRate': win_rate, 'Trades': total_trades}

def plot_comparison(df, equity_curves, ticker):
    plt.figure(figsize=(12, 6))
    
    for name, equity in equity_curves.items():
        plt.plot(df.index, equity, label=name)
        
    plt.title(f'Strategy Comparison - {ticker}')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid()
    plt.savefig('bb_volume_comparison.png')
    print("Comparison plot saved.")

def plot_strategy_signals(df, signals, title, filename):
    plt.figure(figsize=(14, 7))
    
    # Plot Price and Bands
    plt.plot(df.index, df['Close'], label='Close Price', alpha=0.5, color='black')
    plt.plot(df.index, df['Upper_Band'], label='Upper Band', color='green', alpha=0.3)
    plt.plot(df.index, df['Lower_Band'], label='Lower Band', color='red', alpha=0.3)
    plt.fill_between(df.index, df['Upper_Band'], df['Lower_Band'], color='gray', alpha=0.1)
    
    # Extract Buy/Sell points
    # Signal 1 = Buy, -1 = Sell
    buys = df[signals == 1]
    sells = df[signals == -1]
    
    plt.scatter(buys.index, buys['Close'], label='Buy', marker='^', color='green', lw=3, zorder=5, s=100)
    plt.scatter(sells.index, sells['Close'], label='Sell', marker='v', color='red', lw=3, zorder=5, s=100)
    
    plt.title(f'{title} - Trade Signals')
    plt.legend()
    plt.grid()
    plt.savefig(filename)
    print(f"Saved signal plot: {filename}")

if __name__ == "__main__":
    ticker = '2330.TW'
    df = fetch_data(ticker)
    df = add_indicators(df)
    df = df.dropna()
    
    print(f"--- Backtesting {ticker} ---")
    
    # Strategy 1: Volatility Breakout
    sig_breakout = strategy_volatility_breakout(df)
    eq_breakout, _ = run_backtest(df, sig_breakout, "Vol Breakout")
    # eq_breakout_sma, _ = run_backtest(df, sig_breakout, "Breakout + SMA", stop_loss_type='bb_trend_sma')
    
    # Strategy 2: Volume Reversal (Low Vol at Bands)
    sig_reversal = strategy_volume_reversal(df)
    eq_reversal, _ = run_backtest(df, sig_reversal, "Low Vol Reversal")
    # eq_reversal_chan, _ = run_backtest(df, sig_reversal, "Reversal + Chandelier", stop_loss_type='chandelier')
    # eq_reversal_sma, _ = run_backtest(df, sig_reversal, "Reversal + SMA", stop_loss_type='bb_trend_sma')
    
    # Strategy 3: W-Bottom (Original)
    sig_w_bottom = strategy_w_bottom(df)
    eq_w_bottom, _ = run_backtest(df, sig_w_bottom, "W-Bottom")
    # eq_w_bottom_sma, _ = run_backtest(df, sig_w_bottom, "W-Bottom + SMA", stop_loss_type='bb_trend_sma')
    
    # --- Advanced Strategies ---
    # 4. TTM Squeeze
    sig_ttm = strategy_ttm_squeeze(df)
    eq_ttm, _ = run_backtest(df, sig_ttm, "TTM Squeeze")
    
    # 5. DBB Trend
    sig_dbb = strategy_dbb_trend(df)
    eq_dbb, _ = run_backtest(df, sig_dbb, "DBB Trend (Hold > 1std)")
    
    # 6. %B + MFI
    sig_pbmfi = strategy_percent_b_mfi(df)
    eq_pbmfi, _ = run_backtest(df, sig_pbmfi, "%B + MFI Rev")

    # Compare with Buy & Hold
    eq_bh = (df['Close'] / df['Close'].iloc[0]) * 1_000_000
    # print(f"[Buy & Hold] Final: ${eq_bh.iloc[-1]:,.0f} | Return: {(eq_bh.iloc[-1]-1000000)/1000000*100:.2f}%")
    
    plot_comparison(df, {
        'Vol Breakout': eq_breakout,
        'Low Vol Rev': eq_reversal,
        'W-Bottom': eq_w_bottom,
        'TTM Squeeze': eq_ttm,
        'DBB Trend': eq_dbb,
        '%B+MFI': eq_pbmfi,
        'Buy & Hold': eq_bh
    }, ticker)
    
    # Generate individual signal plots
    plot_strategy_signals(df, sig_breakout, f"Volatility Breakout ({ticker})", "signal_breakout.png")
    plot_strategy_signals(df, sig_reversal, f"Volume Reversal ({ticker})", "signal_reversal.png")
    plot_strategy_signals(df, sig_w_bottom, f"W-Bottom ({ticker})", "signal_w_bottom.png")
    plot_strategy_signals(df, sig_ttm, f"TTM Squeeze ({ticker})", "signal_ttm.png")
    plot_strategy_signals(df, sig_dbb, f"DBB Trend ({ticker})", "signal_dbb.png")
    plot_strategy_signals(df, sig_pbmfi, f"%B + MFI ({ticker})", "signal_pbmfi.png")
    
    # Generate Combined Plot
    plot_combined_signals(df, {
        'Vol Breakout': sig_breakout,
        'Low Vol Reversal': sig_reversal,
        'W-Bottom': sig_w_bottom,
        'TTM Squeeze': sig_ttm,
        'DBB Trend': sig_dbb,
        '%B+MFI': sig_pbmfi
    }, "signal_combined.png")
