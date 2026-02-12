"""
Watchlist Manager - Remove stocks from watchlist
從追蹤清單移除股票
"""

import sys
import csv
import os

def remove_from_watchlist(stock_codes, watchlist_path='watchlist.csv'):
    """
    Remove selected stocks from watchlist
    
    Args:
        stock_codes: List of stock codes to remove (e.g., ['2330.TW', '2454.TW'])
        watchlist_path: Path to watchlist CSV
    """
    if not os.path.exists(watchlist_path):
        print(f"❌ 找不到追蹤清單檔案: {watchlist_path}")
        return
    
    # Read current watchlist
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_items = list(reader)
    
    # Filter out selected stocks
    removed = []
    remaining = []
    
    for item in all_items:
        if item['Ticker'] in stock_codes:
            removed.append(item)
        else:
            remaining.append(item)
    
    if not removed:
        print("⚠️  未找到要移除的股票")
        return
    
    # Show what will be removed
    print(f"\n準備移除 {len(removed)} 個部位：")
    print("-" * 85)
    for item in removed:
        print(f"{item['Ticker']:<10} | {item['Strategy']:<18} | {item['EntryPrice']:<10}")
    print("-" * 85)
    
    # Write back remaining items
    with open(watchlist_path, 'w', newline='', encoding='utf-8') as f:
        if remaining:
            fieldnames = list(remaining[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(remaining)
    
    print(f"\n✅ 成功移除 {len(removed)} 個部位！")
    print(f"   剩餘 {len(remaining)} 個部位在追蹤清單中")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python remove_from_watchlist.py <股票代碼1> <股票代碼2> ...")
        print("範例: python remove_from_watchlist.py 2330.TW 2454.TW")
        sys.exit(1)
    
    stock_codes = sys.argv[1:]
    remove_from_watchlist(stock_codes)
