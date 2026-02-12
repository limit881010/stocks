"""
Portfolio Status - Minimal Version
"""
import csv
import yfinance as yf
from datetime import datetime

# Read watchlist
with open('watchlist.csv', 'r') as f:
    reader = csv.DictReader(f)
    positions = list(reader)

print("\n" + "="*90)
print(" PORTFOLIO STATUS")
print("="*90)

for pos in positions:
    ticker = pos['Ticker']
    strategy = pos['Strategy'][:15]
    entry_price = float(pos['EntryPrice'])
    entry_date = pos['EntryDate']
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d')
        
        if not hist.empty:
            current_price = hist['Close'].iloc[0]
            pnl = ((current_price - entry_price) / entry_price) * 100
            days = (datetime.now() - datetime.strptime(entry_date, '%Y-%m-%d')).days
            
            status = "UP" if pnl > 0 else "DOWN"
            print(f"{ticker:8} | {strategy:15} | Entry: ${entry_price:7.2f} | Now: ${current_price:7.2f} | {status:4} {pnl:+6.2f}% | {days}d")
        else:
            print(f"{ticker:8} | {strategy:15} | Entry: ${entry_price:7.2f} | No data available")
            
    except Exception as e:
        print(f"{ticker:8} | ERROR: {str(e)[:40]}")

print("="*90)
