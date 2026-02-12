"""
US Stock Scanner - Run Scan
執行美股掃描，找出符合技術指標的買入訊號
"""
print("DEBUG: Executing us_scanner.py for US tech stocks...")

import sys
import os

# Import scanner with US stocks
from bb_scanner import scan_stocks
from us_stocks_list import US_TECH_STOCKS

if __name__ == "__main__":
    print("="*100)
    print(" 美股技術分析掃描器 - US Tech Stock Scanner")
    print("="*100)
    print(f" Scanning {len(US_TECH_STOCKS)} US tech stocks for buy signals...")
    print()
    
    # Run scanner with US stocks
    scan_stocks(US_TECH_STOCKS, output_file='us_scan_results_with_stats.csv')
