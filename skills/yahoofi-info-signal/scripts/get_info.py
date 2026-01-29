import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    # 使用 EWM 計算 (Wilder's Smoothing)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def get_stock_analysis(ticker_symbol):
    print(f"正在取得 {ticker_symbol} 的資料中...")
    
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # 抓取歷史股價 (為了計算均線與其他指標，至少抓 3 個月)
        hist = stock.history(period="6mo") # 抓6個月確保有足夠資料算 50MA
        
        if hist.empty:
            print("無法取得歷史股價")
        
        # 檢查資料是否足夠
        if len(hist) > 0:
            current_close = hist['Close'].iloc[-1]
        else:
            current_close = info.get("currentPrice")

        # 1. 補算本益比 (Trailing PE)
        trailing_pe = info.get("trailingPE")
        trailing_eps = info.get("trailingEps")
        
        if trailing_pe is None and current_close and trailing_eps:
            try:
                calculated_pe = current_close / trailing_eps
                trailing_pe = f"{calculated_pe:.2f} (估算)"
            except ZeroDivisionError:
                trailing_pe = "N/A"
        
        # 取得最新資料日期
        data_date = "N/A"
        if not hist.empty:
            data_date = hist.index[-1].strftime('%Y-%m-%d')

        # 定義要抓取的欄位與對應的 Info Key
        data = {
            "股價資訊": {
                "資料日期 (Date)": data_date,
                "目前股價 (Price)": info.get("currentPrice") if info.get("currentPrice") else (f"{current_close:.2f}" if len(hist) > 0 else "N/A"),
                "目標價 (Target Price)": info.get("targetMeanPrice"),
                "分析師評級 (Rating)": info.get("recommendationKey", "N/A").upper() if info.get("recommendationKey") else "N/A"
            },
            "估值指標": {
                "本益比 (Trailing PE)": trailing_pe,
                "預估本益比 (Forward PE)": info.get("forwardPE"),
                "股價淨值比 (P/B)": info.get("priceToBook"),
                "PEG (PEG Ratio)": info.get("pegRatio")
            },
            "獲利能力 (Margins)": {
                "毛利率 (Gross Margin)": info.get("grossMargins"),
                "營業利益率 (Operating Margin)": info.get("operatingMargins"),
                "股東權益報酬率 (ROE)": info.get("returnOnEquity"),
                "資產報酬率 (ROA)": info.get("returnOnAssets")
            },
            "每股盈餘 (EPS)": {
                "近12月 EPS (Trailing EPS)": info.get("trailingEps"),
                "預估 EPS (Forward EPS)": info.get("forwardEps")
            },
            "財務結構": {
                "負債權益比 (Debt/Equity)": info.get("debtToEquity")
            }
        }

        # 將數據整理成 DataFrame
        rows = []
        for category, metrics in data.items():
            for metric_name, value in metrics.items():
                formatted_value = value
                
                if isinstance(value, (int, float)):
                    if "Margin" in metric_name or "ROE" in metric_name or "ROA" in metric_name:
                         formatted_value = f"{value:.2%}"
                    elif "Price" in metric_name or "EPS" in metric_name or "PEG" in metric_name or "P/B" in metric_name:
                        formatted_value = f"{value:.2f}"
                    elif "PE" in metric_name and not isinstance(value, str): # PE 可能是字串 "(估算)"
                        formatted_value = f"{value:.2f}"
                    elif "Debt" in metric_name:
                        formatted_value = f"{value:.2f}%"
                
                if value is None:
                    formatted_value = "N/A"

                rows.append({"類別": category, "指標": metric_name, "數值": formatted_value})

        df_basic = pd.DataFrame(rows)
        
        # --- 技術指標計算 ---
        tech_rows = []
        
        if not hist.empty:
            # 計算移動平均線
            hist['MA10'] = hist['Close'].rolling(window=10).mean()
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            
            # 計算成交量均線
            if 'Volume' in hist.columns:
                hist['VolMA20'] = hist['Volume'].rolling(window=20).mean()

            # 計算 MACD
            hist['MACD'], hist['Signal'] = calculate_macd(hist['Close'])
            
            # 計算 RSI
            hist['RSI'] = calculate_rsi(hist['Close'])
            
            # 取得最新一天的數據
            latest = hist.iloc[-1]
            
            tech_indicators = {
                "10日均價 (MA10)": latest['MA10'],
                "20日均價 (MA20)": latest['MA20'],
                "50日均線 (MA50)": latest['MA50'],
                "MACD": latest['MACD'],
                "MACD Signal": latest['Signal'],
                "RSI (14)": latest['RSI']
            }
            
            for k, v in tech_indicators.items():
                 rows.append({"類別": "技術指標", "指標": k, "數值": f"{v:.2f}" if pd.notna(v) else "N/A"})
        
        df_final = pd.DataFrame(rows)

        return df_final, hist

    except Exception as e:
        print(f"發生錯誤: {e}")
        return None, None

# --- 主程式 ---
if __name__ == "__main__":
    symbol = input("請輸入股票代號 (美股如 NVDA, 台股如 2330.TW): ").strip()
    
    if symbol:
        result_df, history_df = get_stock_analysis(symbol)
        
        if result_df is not None:
            print("\n" + "="*50)
            print(f"  {symbol.upper()} 股票分析數據")
            print("="*50)
            print(result_df.to_string(index=False))
            
            if history_df is not None and not history_df.empty:
                print("\n" + "="*50)
                print("  前 10 日股價與指標")
                print("="*50)
                
                # 準備顯示欄位 (加入成交量)
                display_cols = ['Close', 'MA10', 'MA20', 'MA50', 'MACD', 'RSI']
                if 'Volume' in history_df.columns:
                    display_cols.insert(1, 'Volume') # 插入在 Close 後面
                
                # 取最後 10 筆並格式化
                last_10 = history_df.tail(10)[display_cols].copy()
                
                # 格式化設定: 成交量顯示逗號，其餘顯示小數點
                formatters = {}
                for col in display_cols:
                    if col == 'Volume':
                        formatters[col] = '{:,.0f}'.format
                    else:
                        formatters[col] = '{:,.2f}'.format
                
                print(last_10.to_string(formatters=formatters))

        else:
            print("無法取得資料，請檢查代號是否正確。")
