"""
Portfolio Monitor - Monitor tracked stocks for sell signals
監控追蹤清單中的股票，檢測賣出訊號
"""

import sys
import os
import csv
import time
from datetime import datetime

# Add strategy directory to path
strategy_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'strategy')
sys.path.insert(0, os.path.abspath(strategy_dir))

from bb_volume_strategy import (
    fetch_data, add_indicators,
    strategy_volatility_breakout, strategy_volume_reversal, strategy_w_bottom,
    strategy_bb_squeeze_momentum, strategy_ichimoku_cloud, strategy_mean_reversion,
    strategy_dbb_trend, strategy_percent_b_mfi
)

# Strategy map
STRATEGIES = {
    "Vol Breakout": strategy_volatility_breakout,
    "Low Vol Reversal": strategy_volume_reversal,
    "W-Bottom": strategy_w_bottom,
    "BB Squeeze+Mom": strategy_bb_squeeze_momentum,
    "Ichimoku Cloud": strategy_ichimoku_cloud,
    "Mean Reversion": strategy_mean_reversion,
    "DBB Trend Entry": strategy_dbb_trend,
    "%B+MFI Reversal": strategy_percent_b_mfi
}


def monitor_portfolio(watchlist_path='watchlist.csv'):
    """
    Monitor watchlist for sell signals
    """
    if not os.path.exists(watchlist_path):
        print("📋 追蹤清單是空的，請先掃描並加入股票")
        return
    
    # Load watchlist
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        watchlist = list(reader)
    
    if not watchlist:
        print("📋 追蹤清單是空的")
        return
    
    print("="*100)
    print(f" 開始監控 {len(watchlist)} 個部位...")
    print("="*100)
    print()
    
    results = []
    sell_signals = []
    
    for item in watchlist:
        ticker = item['Ticker']
        strategy_name = item['Strategy']
        entry_price = float(item['EntryPrice'])
        entry_date = item['EntryDate']
        
        try:
            print(f"檢查 {ticker} ({strategy_name})...", end='\r')
            time.sleep(1)
            
            # Fetch data
            df = fetch_data(ticker, start='2024-01-01')
            
            if len(df) < 50:
                continue
                
            df = add_indicators(df)
            df = df.dropna()
            
            # Get strategy function
            strategy_func = STRATEGIES.get(strategy_name)
            if not strategy_func:
                continue
            
            # Check for sell signal
            signal_series = strategy_func(df)
            current_price = df['Close'].iloc[-1]
            current_date = df.index[-1]
            
            # Calculate P&L
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Check if sell signal
            has_sell_signal = signal_series.iloc[-1] == -1
            
            # Calculate holding period
            days_held = (datetime.now() - datetime.strptime(entry_date, '%Y-%m-%d')).days
            
            results.append({
                'Ticker': ticker,
                'Strategy': strategy_name,
                'EntryPrice': entry_price,
                'CurrentPrice': current_price,
                'PnL%': pnl_pct,
                'DaysHeld': days_held,
                'SellSignal': '🔴 SELL' if has_sell_signal else '🟢 HOLD'
            })
            
            if has_sell_signal:
                sell_signals.append({
                    'ticker': ticker,
                    'strategy': strategy_name,
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl_pct': pnl_pct,
                    'days_held': days_held,
                    'df': df
                })
                
        except Exception as e:
            print(f"[Error] {ticker}: {e}")
            continue
    
    # Display results
    print("="*100)
    print(" 持倉狀態總覽")
    print("="*100)
    print(f"{'股票':<10} | {'策略':<18} | {'狀態':<12} | {'買入':<10} | {'現價':<10} | {'損益%':<10} | {'持有天數':<8}")
    print("-"*100)
    
    for r in results:
        pnl_emoji = '📈' if r['PnL%'] > 0 else '📉'
        print(f"{r['Ticker']:<10} | {r['Strategy']:<18} | {r['SellSignal']:<12} | ${r['EntryPrice']:<9.2f} | ${r['CurrentPrice']:<9.2f} | {pnl_emoji} {r['PnL%']:>6.1f}% | {r['DaysHeld']:>7}天")
    
    print("="*100)
    
    # Show sell signals
    if sell_signals:
        print()
        print("="*100)
        print(" 🔴 賣出訊號警報 🔴")
        print("="*100)
        print()
        
        for sig in sell_signals:
            pnl_status = '✅ 獲利' if sig['pnl_pct'] > 0 else '❌ 虧損'
            print(f"[{sig['ticker']}] - {sig['strategy']}")
            print(f"  買入: {sig['entry_date']} @ ${sig['entry_price']:.2f}")
            print(f"  現在: {sig['df'].index[-1].strftime('%Y-%m-%d')} @ ${sig['current_price']:.2f}")
            print(f"  損益: {pnl_status} {sig['pnl_pct']:+.2f}% (持有 {sig['days_held']} 天)")
            print(f"  關鍵價位:")
            print(f"    • 20 日均線: ${sig['df']['SMA'].iloc[-1]:.2f}")
            print(f"    • 下軌支撐: ${sig['df']['Lower_Band'].iloc[-1]:.2f}")
            if 'Chandelier_Long' in sig['df'].columns:
                print(f"    • Chandelier 止損: ${sig['df']['Chandelier_Long'].iloc[-1]:.2f}")
            print()
        
        print("="*100)
        print(f"⚠️  {len(sell_signals)} 個部位觸發賣出訊號！")
        print("="*100)
    
    # Summary
    print()
    print("="*100)
    print(" 投資組合摘要")
    print("="*100)
    winning = [r for r in results if r['PnL%'] > 0]
    print(f"總部位數: {len(results)}")
    print(f"獲利部位: {len(winning)} ({len(winning)/len(results)*100 if results else 0:.1f}%)")
    print(f"平均損益: {sum(r['PnL%'] for r in results)/len(results) if results else 0:.2f}%")
    print(f"賣出訊號: {len(sell_signals)} 個")
    print("="*100)


if __name__ == "__main__":
    monitor_portfolio()
