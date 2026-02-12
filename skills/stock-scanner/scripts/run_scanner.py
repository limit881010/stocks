"""
Taiwan Stock Scanner - Run Scan
執行台股掃描，找出符合技術指標的買入訊號
"""
print("DEBUG: Executing run_scanner.py from current directory...")

import sys
import os

# Add strategy directory to path
# strategy_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'strategy')
# sys.path.insert(0, os.path.abspath(strategy_dir))

# Import scanner
from bb_scanner import scan_stocks, POSSIBLE_TICKERS

if __name__ == "__main__":
    print("="*100)
    print(" 台股技術分析掃描器 - Taiwan Stock Scanner")
    print("="*100)
    print()
    
    # Run scanner
    scan_stocks(POSSIBLE_TICKERS)
