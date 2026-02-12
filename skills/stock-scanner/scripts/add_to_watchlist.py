"""
Watchlist Manager - Add stocks to watchlist
將選定的股票加入追蹤清單
"""

import sys
import csv
import os
from datetime import datetime

def add_to_watchlist(stock_codes, scan_results_path=None):
    """
    Add selected stocks to watchlist
    
    Args:
        stock_codes: List of stock codes to add (e.g., ['2330.TW', '2454.TW', 'AMZN'])
        scan_results_path: Path to scan results CSV (auto-detects if None)
    """
    # Auto-detect scan results file if not specified
    if scan_results_path is None:
        # Try to determine market from stock codes
        has_us_stocks = any(not code.endswith(('.TW', '.TWO')) for code in stock_codes)
        has_tw_stocks = any(code.endswith(('.TW', '.TWO')) for code in stock_codes)
        
        # Load both files if they exist
        all_results = []
        files_checked = []
        
        if has_tw_stocks or not has_us_stocks:
            tw_file = 'scan_results_with_stats.csv'
            if os.path.exists(tw_file):
                with open(tw_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    all_results.extend(list(reader))
                files_checked.append(tw_file)
        
        if has_us_stocks or not has_tw_stocks:
            us_file = 'us_scan_results_with_stats.csv'
            if os.path.exists(us_file):
                with open(us_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    all_results.extend(list(reader))
                files_checked.append(us_file)
        
        if not all_results:
            print(f"❌ 找不到掃描結果檔案")
            return
        
        print(f"📁 已載入掃描結果: {', '.join(files_checked)}")
    else:
        # Use specified file
        if not os.path.exists(scan_results_path):
            print(f"❌ 找不到掃描結果檔案: {scan_results_path}")
            return
        
        with open(scan_results_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_results = list(reader)
    
    # Filter selected stocks
    selected = []
    for code in stock_codes:
        # Try exact match first
        matches = [r for r in all_results if r['Ticker'] == code]
        
        # If no exact match and input is just numbers, try adding suffix
        if not matches and code.isdigit():
             matches = [r for r in all_results if r['Ticker'].split('.')[0] == code]
             
        if matches:
            selected.extend(matches)
        else:
            print(f"⚠️  未找到 {code} 在掃描結果中")
    
    if not selected:
        print("❌ 沒有符合的股票可加入")
        return
    
    # Show what will be added
    print(f"\n準備加入 {len(selected)} 個部位到追蹤清單：")
    print("-" * 85)
    for item in selected:
        print(f"{item['Ticker']:<10} | {item['Strategy']:<18} | {item['Close']:<10} | {item['WinRate']:>6}% | {item['Return']:>7}%")
    print("-" * 85)
    
    # Append to watchlist (create if doesn't exist)
    watchlist_path = 'watchlist.csv'
    file_exists = os.path.exists(watchlist_path)
    
    with open(watchlist_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Ticker', 'Strategy', 'EntryDate', 'EntryPrice', 'WinRate', 'Return', 'Trades']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for item in selected:
            writer.writerow({
                'Ticker': item['Ticker'],
                'Strategy': item['Strategy'],
                'EntryDate': datetime.now().strftime('%Y-%m-%d'),
                'EntryPrice': item['Close'],
                'WinRate': item['WinRate'],
                'Return': item['Return'],
                'Trades': item['Trades']
            })
    
    print(f"\n✅ 成功加入 {len(selected)} 個部位到追蹤清單！")
    print(f"   檔案位置: {watchlist_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python add_to_watchlist.py <股票代碼1> <股票代碼2> ...")
        print("範例: python add_to_watchlist.py 2330.TW 2454.TW 2317.TW")
        sys.exit(1)
    
    stock_codes = sys.argv[1:]
    add_to_watchlist(stock_codes)
