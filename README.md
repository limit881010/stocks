#  Stock Analysis & Scanner AI Agent Skills

本專案是一套專為 AI Agent 打造的股票分析工具集（Skills），旨在讓 Agent 具備掃描台美股買入訊號、追蹤投資組合、以及執行深度個股財務診斷的能力。

## 🧠 Agent 核心能力 (Capabilities)
### 1. 市場動態 (Market news) 
> **使用skills：** `market-news-analyst`
Agent 可以自動搜尋過去一周的全球股市與大宗商品市場產生重大影響的財經新聞：

* **全方位掃描**：自動蒐集 FOMC 決策、關鍵經濟數據 (CPI/非農)、科技巨頭財報及地緣政治等重大事件。
* **量化影響力**：透過 Impact Score 演算法評估新聞對股、債、匯、原物料的實際衝擊，並進行影響力排名。
* **深度分析報告**：產出繁體中文週報，解析市場反應、跨資產連動性 (Correlation) 及未來趨勢展望。

### 2. 市場掃描 (Market Scanning) 
> **使用skills：** `stock-scanner`

Agent 可以調用掃描器在數百檔股票中自動篩選符合技術形態的標的：

* **台股掃描**：分析市值前 150 大的權值股。
* **美股掃描**：分析指定的科技領頭股（如 NVDA, AAPL, TSLA 等）。
* **策略回測**：每一筆訊號都會附帶歷史勝率（Win Rate）與預期報酬，供 Agent 進行優先級排序。

### 3. 持倉監控 (Portfolio Monitoring)
> **使用skills：** `stock-scanner`

Agent 具備自動化管理追蹤清單的能力：

* **賣出警報**：監控 `watchlist.csv` 中的股票，當技術指標轉弱時產出 `🔴 SELL` 訊號。
* **損益追蹤**：計算持有天數與即時損益百分比。

### 4. 技術與財務診斷 (Technical & Fundamental Diagnosis)
> **使用skills：** `yahoofi-info-signal`

Agent 能針對指定的股票代號執行深度檢查，產出結構化數據：

* **財務面**：本益比 (PE)、股價淨值比 (P/B)、ROE、毛利率及負債比。
* **技術面**：均線多空排列、MACD 趨勢控盤、RSI 強弱區間及價量背離分析。

---

## 🛠 Agent 指令集 (Tool Usage)

Agent 應根據用戶需求執行對應的 Python 腳本：

| 目標 | 執行指令 | 關鍵輸出內容 |
| --- | --- | --- |
| **掃描台股買點** | `python run_scanner.py` | 策略名稱、收盤價、勝率、預期回報 |
| **掃描美股買點** | `python run_us_scanner.py` | 美股科技股的買入建議清單 |
| **加入追蹤清單** | `python add_to_watchlist.py <TICKER>` | 將股票鎖定至 `watchlist.csv` |
| **檢查賣出訊號** | `python monitor_portfolio.py` | 損益統計、觸發賣出的警報詳情 |
| **深度診斷個股** | `python analyze.py <TICKER>` | 詳細財務表格、近10日指標、多空趨勢判別 |
---

## 📈 內建 AI 策略邏輯

本工具集提供 8 種策略供 Agent 分析，每種策略皆有明確的觸發條件：

1. **Vol Breakout**：布林帶擠壓後的量能突破。
2. **W-Bottom**：標準雙底形態且成交量遞減（籌碼惜售）。
3. **BB Squeeze+Mom**：結合 TTM Squeeze 與 MACD 動能的爆發點。
4. **Ichimoku Cloud**：一目均衡表雲層突破（趨勢轉向）。
5. **Mean Reversion**：極端乖離修正（超賣反彈）。
6. **DBB Trend Entry**：雙重布林帶趨勢區間追蹤。
7. **%B+MFI Reversal**：結合資金流向指標的超賣反轉。
8. **Low Vol Reversal**：支撐區間的低量回測。

---

## 📂 數據結構規範

Agent 應維護並讀取以下 CSV 文件：

* **`watchlist.csv`**：存儲追蹤中的股票。包含欄位：`Ticker`, `Strategy`, `EntryDate`, `EntryPrice`, `WinRate`, `Return`, `Trades`。
* **`scan_results_with_stats.csv`**：存儲最新的台股掃描結果，供 Agent 進行二次過濾。
* **`us_scan_results_with_stats.csv`**：存儲最新的美股掃描結果。

---

## ⚙️ 環境與權限

* **Python 版本**：建議 3.10+。
* **必要套件**：依據 `requirements.txt` 安裝 `yfinance`, `pandas`, `numpy`, `matplotlib`。
* **初始化指令**：Agent 首次部署需執行 `python init_setup.py` 以建立數據架構。

---
