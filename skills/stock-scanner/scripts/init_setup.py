"""
Initialize Stock Scanner - Create Required Data Files
初始化股票掃描器 - 創建必要的數據文件
"""
import os
import csv

def init_setup():
    """
    Create empty data files if they don't exist
    如果數據文件不存在則創建空文件
    """
    print("="*60)
    print(" Stock Scanner Setup - 股票掃描器初始化")
    print("="*60)
    print()
    
    created_files = []
    existing_files = []
    
    # 1. Create empty watchlist.csv
    watchlist_path = 'watchlist.csv'
    if not os.path.exists(watchlist_path):
        with open(watchlist_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ticker', 'Strategy', 'EntryDate', 'EntryPrice', 'WinRate', 'Return', 'Trades'])
        created_files.append(watchlist_path)
        print(f"✅ Created: {watchlist_path}")
    else:
        existing_files.append(watchlist_path)
        print(f"ℹ️  Already exists: {watchlist_path}")
    
    # 2. Create empty scan_results_with_stats.csv
    scan_results_path = 'scan_results_with_stats.csv'
    if not os.path.exists(scan_results_path):
        with open(scan_results_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ticker', 'Date', 'Strategy', 'Close', 'WinRate', 'Return', 'Trades'])
        created_files.append(scan_results_path)
        print(f"✅ Created: {scan_results_path}")
    else:
        existing_files.append(scan_results_path)
        print(f"ℹ️  Already exists: {scan_results_path}")
    
    # 3. Create empty us_scan_results_with_stats.csv
    us_scan_results_path = 'us_scan_results_with_stats.csv'
    if not os.path.exists(us_scan_results_path):
        with open(us_scan_results_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ticker', 'Date', 'Strategy', 'Close', 'WinRate', 'Return', 'Trades'])
        created_files.append(us_scan_results_path)
        print(f"✅ Created: {us_scan_results_path}")
    else:
        existing_files.append(us_scan_results_path)
        print(f"ℹ️  Already exists: {us_scan_results_path}")
    
    # 4. Check for top_market_cap_stocks.txt (created by fetch_top_stocks.py)
    cache_path = 'top_market_cap_stocks.txt'
    if not os.path.exists(cache_path):
        print(f"ℹ️  Note: {cache_path} will be created on first Taiwan stock scan")
    else:
        existing_files.append(cache_path)
        print(f"ℹ️  Already exists: {cache_path}")
    
    # Summary
    print()
    print("="*60)
    print(" Setup Summary")
    print("="*60)
    if created_files:
        print(f"✅ Created {len(created_files)} new file(s)")
    if existing_files:
        print(f"ℹ️  Found {len(existing_files)} existing file(s)")
    print()
    print("🎉 Setup complete! You can now:")
    print("   1. Run Taiwan stock scan: python run_scanner.py")
    print("   2. Run US stock scan: python run_us_scanner.py")
    print("   3. Monitor portfolio: python monitor_portfolio.py")
    print("="*60)

if __name__ == "__main__":
    init_setup()
