import sys
import os
import pandas as pd

# Ensure local imports work by adding script directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from get_info import get_stock_analysis
    # Renamed from signal.py to stock_signal.py to avoid conflict with stdlib signal
    from stock_signal import analyze_signals
except ImportError:
    # Fallback if imports fail normally
    try:
        from .get_info import get_stock_analysis
        from .stock_signal import analyze_signals
    except ImportError as e:
        print(f"Error importing modules: {e}")
        # Note: If stock_signal.py is missing, ensure it was renamed from signal.py
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <TICKER>")
        sys.exit(1)
        
    symbol = sys.argv[1].strip()
    
    if not symbol:
        print("Error: Empty ticker symbol")
        sys.exit(1)
        
    try:
        result_df, history_df = get_stock_analysis(symbol)
        
        if result_df is not None:
            print("\n" + "="*50)
            print(f"  {symbol.upper()} Stock Analysis Data")
            print("="*50)
            # Use to_string to print the entire dataframe
            print(result_df.to_string(index=False))
            
            if history_df is not None and not history_df.empty:
                print("\n" + "="*50)
                print("  Last 10 Days Price & Indicators")
                print("="*50)
                
                display_cols = ['Close', 'MA10', 'MA20', 'MA50', 'MACD', 'RSI']
                if 'Volume' in history_df.columns:
                    display_cols.insert(1, 'Volume')
                
                # Check which columns actually exist
                available_cols = [c for c in display_cols if c in history_df.columns]
                last_10 = history_df.tail(10)[available_cols].copy()
                
                formatters = {}
                for col in available_cols:
                    if col == 'Volume':
                        formatters[col] = '{:,.0f}'.format
                    else:
                        formatters[col] = '{:,.2f}'.format
                
                print(last_10.to_string(formatters=formatters))

                # Call signal analysis
                analyze_signals(history_df)
        else:
            print("Could not fetch data.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
