"""
Watchlist Manager - Show current watchlist
顯示目前的追蹤清單
"""

import csv
import os

def show_watchlist(watchlist_path='watchlist.csv'):
    """
    Display current watchlist
    
    Args:
        watchlist_path: Path to watchlist CSV
    """
    if not os.path.exists(watchlist_path):
        print("📋 追蹤清單是空的")
        print(f"   檔案不存在: {watchlist_path}")
        return
    
    # Read watchlist
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        items = list(reader)
    
    if not items:
        print("📋 追蹤清單是空的")
        return
    
    # Display watchlist
    print("="*100)
    print(f" 目前追蹤清單 - {len(items)} 個部位")
    print("="*100)
    print(f"{'股票':<10} | {'策略':<18} | {'買入日期':<12} | {'買入價':<10} | {'勝率':<7} | {'回報':<8} | {'交易次數':<8}")
    print("-"*100)
    
    for item in items:
        print(f"{item['Ticker']:<10} | {item['Strategy']:<18} | {item['EntryDate']:<12} | ${float(item['EntryPrice']):<9.2f} | {float(item['WinRate']):>6.1f}% | {float(item['Return']):>7.1f}% | {item['Trades']:>8}")
    
    print("="*100)


if __name__ == "__main__":
    show_watchlist()
