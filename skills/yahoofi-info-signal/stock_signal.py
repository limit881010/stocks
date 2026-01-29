import pandas as pd

def analyze_signals(history_df):
    """
    接收包含 MA10, MA20, MA50, MACD, RSI, Volume, VolMA20 的 DataFrame
    並列印出交易策略訊號分析結果
    """
    if history_df is None or history_df.empty:
        print("無歷史資料，無法進行策略分析。")
        return

    print("\n" + "="*50)
    print("  交易策略訊號檢查")
    print("="*50)

    # 取得最新一筆與前一筆資料
    latest = history_df.iloc[-1]
    prev = history_df.iloc[-2] if len(history_df) > 1 else latest
    current_price = latest['Close']

    # 1. 均線排列 (趨勢)
    if latest['MA10'] > latest['MA20'] > latest['MA50']:
        print("✅ [趨勢] 多頭排列 (MA10 > MA20 > MA50) -> 強勢上漲趨勢")
    elif latest['MA10'] < latest['MA20'] < latest['MA50']:
        print("❌ [趨勢] 空頭排列 (MA10 < MA20 < MA50) -> 弱勢下跌趨勢")
    
    # 2_1. 股價位置 (支撐/壓力) - 長期
    if current_price > latest['MA50']:
        print("✅ [長期] 股價位於季線 (MA50) 之上 -> 長期趨勢偏多")
    else:
        print("❌ [長期] 股價位於季線 (MA50) 之下 -> 長期趨勢偏空")
        
    # 2_2. 股價位置 (支撐/壓力) - 短期
    if current_price > latest['MA10']:
        print("✅ [短期] 股價位於季線 (MA10) 之上 -> 短期趨勢偏多")
    else:
        print("❌ [短期] 股價位於季線 (MA10) 之下 -> 短期趨勢偏空")

    # 3. MACD (動能)
    # 檢查是否剛發生交叉
    if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal']:
        print("🚀 [訊號] MACD 黃金交叉 -> 買進訊號")
    elif latest['MACD'] < latest['Signal'] and prev['MACD'] >= prev['Signal']:
        print("🔻 [訊號] MACD 死亡交叉 -> 賣出訊號")
    else:
         trend = "多方" if latest['MACD'] > latest['Signal'] else "空方"
         print(f"ℹ️ [動能] MACD 維持{trend}控盤 (MACD: {latest['MACD']:.2f}, Signal: {latest['Signal']:.2f})")

    # 4. RSI (過熱/過冷)
    if latest['RSI'] > 70:
        print("⚠️ [風險] RSI 超買 (>70) -> 短線可能回檔")
    elif latest['RSI'] < 30:
        print("⚡ [機會] RSI 超賣 (<30) -> 短線可能反彈")
    else:
        print(f"ℹ️ [區間] RSI 處於中性區域 ({latest['RSI']:.2f})")

    # 5. 成交量策略 (籌碼/動能)
    if 'Volume' in history_df.columns and 'VolMA20' in history_df.columns:
         # 避免除以零
         vol_ma = latest['VolMA20']
         vol_ratio = (latest['Volume'] / vol_ma) if vol_ma > 0 else 0
         
         # 判斷量能位階
         if vol_ratio >= 2.0:
             vol_status = "🔥 爆量 (Explosive)"
         elif vol_ratio >= 1.2:
             vol_status = "↗️ 量增 (Moderate High)"
         elif vol_ratio <= 0.6:
             vol_status = "💤 量縮 (Shrinking)"
         else:
             vol_status = "➡️ 量平 (Normal)"
         
         print(f"📊 [籌碼] 成交量狀態: {vol_status} (今日: {latest['Volume']:,.0f} / 月均: {vol_ma:,.0f})")
         
         # 價量分析 (Price-Volume Analysis)
         price_change = latest['Close'] - prev['Close']
         if price_change > 0:
             if vol_ratio >= 1.2:
                 print("🚀 [價量] 價漲量增 -> 多頭動能強勁 (追價意願高)")
             elif vol_ratio <= 0.6:
                 print("⚠️ [價量] 價漲量縮 -> 上漲無力或籌碼惜售 (需防背離)")
         elif price_change < 0:
             if vol_ratio >= 1.2:
                 print("🔻 [價量] 價跌量增 -> 賣壓沉重 (恐慌性殺盤)")
             elif vol_ratio <= 0.6:
                 print("ℹ️ [價量] 價跌量縮 -> 賣壓減輕 (整理格局)")
