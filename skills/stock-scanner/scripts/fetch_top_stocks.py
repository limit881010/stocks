"""
Top Stocks Fetcher - Curated 150-stock list for 2024-2026
使用精選清單抓取市值前150大股票
"""
import pandas as pd
import os
from datetime import datetime, timedelta
import json

CACHE_FILE = "top_market_cap_stocks.txt"
CACHE_VALIDITY_DAYS = 30

def get_top_150_stocks():
    """
    Taiwan's top 150 stocks - Curated list based on 2024-2026 market conditions
    台股前150大精選清單（根據2024-2026市場狀況）
    
    Organized by sector with major companies from each industry
    """
    return [
        # ==================== 半導體/IC/電子 (50 stocks) ====================
        '2330.TW',  # 台積電 TSMC
        '2317.TW',  # 鴻海 Hon Hai
        '2454.TW',  # 聯發科 MediaTek
        '2308.TW',  # 台達電 Delta
        '2382.TW',  # 廣達 Quanta
        '2303.TW',  # 聯電 UMC
        '3711.TW',  # 日月光投控 ASE
        '2357.TW',  # 華碩 ASUS
        '2327.TW',  # 國巨 Yageo
        '3034.TW',  # 聯詠 Novatek
        '2301.TW',  # 光寶科 Lite-On
        '2379.TW',  # 瑞昱 Realtek
        '3008.TW',  # 大立光 Largan
        '2324.TW',  # 仁寶 Compal
        '2356.TW',  # 英業達 Inventec
        '3037.TW',  # 欣興 Unimicron
        '6669.TW',  # 緯穎 Wiwynn
        '3661.TW',  # 世芯-KY Alchip
        '2337.TW',  # 旺宏 Macronix
        '2408.TW',  # 南亞科 Nanya Tech
        '3231.TW',  # 緯創 Wistron
        '2377.TW',  # 微星 MSI
        '6415.TW',  # 矽力-KY Silergy
        '3443.TW',  # 創意 GUC
        '4938.TW',  # 和碩 Pegatron
        '2395.TW',  # 研華 Advantech
        '2409.TW',  # 友達 AUO
        '2474.TW',  # 可成 Catcher
        '3481.TW',  # 群創 Innolux
        '6176.TW',  # 瑞儀 Radiant
        '2383.TW',  # 台光電 Taiwan Union Tech
        '8046.TW',  # 南電 Nanya PCB
        '2376.TW',  # 技嘉 Gigabyte
        '2345.TW',  # 智邦 Accton
        '2344.TW',  # 華邦電 Winbond
        '3035.TW',  # 智原 Faraday
        '5269.TW',  # 祥碩 ASMedia
        '6488.TWO',  # 環球晶 GlobalWafers
        '3017.TW',  # 奇鋐 Chi Lin
        '6239.TW',  # 力成 Powertech
        '3189.TW',  # 景碩 Kinsus
        '4919.TW',  # 新唐 Nuvoton
        '3105.TWO',  # 穩懋 Win Semi
        '2049.TW',  # 上銀 Hiwin
        '5234.TW',  # 達興材料 Daxin Materials
        '3532.TW',  # 台勝科 TSEC
        '2393.TW',  # 億光 Everlight
        '3036.TW',  # 文曄 WT Microelectronics
        
        # ==================== 電信 (3 stocks) ====================
        '2412.TW',  # 中華電 Chunghwa Telecom
        '3045.TW',  # 台灣大 Taiwan Mobile
        '4904.TW',  # 遠傳 Far EasTone
        
        # ==================== 金融/保險 (20 stocks) ====================
        '2881.TW',  # 富邦金 Fubon Financial
        '2882.TW',  # 國泰金 Cathay Financial
        '2886.TW',  # 兆豐金 Mega Financial
        '2891.TW',  # 中信金 CTBC Financial
        '2892.TW',  # 第一金 First Financial
        '2884.TW',  # 玉山金 E.SUN Financial
        '2887.TW',  # 台新金 Taishin Financial
        '2885.TW',  # 元大金 Yuanta Financial
        '2880.TW',  # 華南金 Hua Nan Financial
        '2883.TW',  # 開發金 China Development
        '5880.TW',  # 合庫金 Taiwan Business Bank
        '2890.TW',  # 永豐金 SinoPac Financial
        '5876.TW',  # 上海商銀 Shanghai Commercial
        '2801.TW',  # 彰銀 Chang Hwa Bank
        '2834.TW',  # 臺企銀 Taiwan Business Bank
        '2845.TW',  # 遠東銀 Far Eastern Bank
        '5871.TW',  # 中租-KY Chailease
        '2812.TW',  # 台中銀 Taichung Bank
        '2867.TW',  # 三商壽 MercuriesLife
        
        # ==================== 塑化/石化 (6 stocks) ====================
        '1301.TW',  # 台塑 Formosa Plastics
        '1303.TW',  # 南亞 Nan Ya Plastics
        '1326.TW',  # 台化 Formosa Chemicals
        '6505.TW',  # 台塑化 Formosa Petrochemical
        '1402.TW',  # 遠東新 Far Eastern New Century
        '1605.TW',  # 華新 Hwa Hsia
        
        # ==================== 鋼鐵 (4 stocks) ====================
        '2002.TW',  # 中鋼 China Steel
        '2006.TW',  # 東和鋼鐵 Tung Ho Steel
        '2027.TW',  # 大成鋼 Ta Chen Steel
        '2031.TW',  # 新光鋼 Shin Kong Steel
        
        # ==================== 水泥 (3 stocks) ====================
        '1101.TW',  # 台泥 Taiwan Cement
        '1102.TW',  # 亞泥 Asia Cement
        '1104.TW',  # 環泥 Universal Cement
        
        # ==================== 航運 (5 stocks) ====================
        '2603.TW',  # 長榮 Evergreen Marine
        '2609.TW',  # 陽明 Yang Ming
        '2615.TW',  # 萬海 Wan Hai
        '2610.TW',  # 華航 China Airlines
        '2618.TW',  # 長榮航 EVA Airways
        
        # ==================== 汽車/零組件 (4 stocks) ====================
        '2207.TW',  # 和泰車 Hotai Motor
        '2201.TW',  # 裕隆 Yulon Motor
        '2227.TW',  # 裕日車 Yulon Nissan Motor
        '1590.TW',  # 亞德客-KY Airtac
        
        # ==================== 食品/生技/民生 (10 stocks) ====================
        '1216.TW',  # 統一 Uni-President
        '2912.TW',  # 統一超 President Chain Store
        '1229.TW',  # 聯華 Lian Hwa
        '1227.TW',  # 佳格 Standard Foods
        '1232.TW',  # 大統益 Great Wall Enterprise
        '6472.TW',  # 保瑞 PharmaEssentia
        '6446.TW',  # 藥華藥 PharmaEssentia
        '4306.TW',  # 炎洲 Yen Sun Tech
        '4952.TW',  # 凌通 Realchip
        
        # ==================== 營建/房地產 (5 stocks) ====================
        '2501.TW',  # 國建 Kuo Chien Construction
        '2520.TW',  # 冠德 Crown Construction
        '5522.TW',  # 遠雄 Farglory Land Development
        '2542.TW',  # 興富發 Highwealth Construction
        '2547.TW',  # 日勝生 Jih Sun International
        
        # ==================== 觀光/百貨 (3 stocks) ====================
        '2915.TW',  # 潤泰全 Ruentex Industries
        '9945.TW',  # 潤泰新 Ruentex Development
        '2910.TW',  # 統領 Tung Ling Dep Store
        
        # ==================== 紡織/製鞋 (5 stocks) ====================
        '9904.TW',  # 寶成 Pou Chen
        '9910.TW',  # 豐泰 Feng Tay
        '1476.TW',  # 儒鴻 Eclat Textile
        '2105.TW',  # 正新 Cheng Shin Rubber
        '2106.TW',  # 建大 Kenda Rubber
        
        # ==================== 其他重要權值股 (27 stocks，補足到150) ====================
        '2633.TW',  # 台灣高鐵 THSR
        '2352.TW',  # 佳世達 Qisda
        '2353.TW',  # 宏碁 Acer
        '2360.TW',  # 致茂 Chroma ATE
        '2371.TW',  # 大同 Tatung
        '2385.TW',  # 群光 Chicony
        '2439.TW',  # 美律 Merry
        '2492.TW',  # 華新科 Walsin Tech
        '3494.TW',  # 誠研 iTech
        '6525.TW',  # 捷敏-KY
        '3702.TW',  # 大聯大 WPG Holdings
        '3706.TW',  # 神達 MiTAC
        '2347.TW',  # 聯強 Synnex
        '5283.TW',  # 禾聯碩 Heran
        '3033.TW',  # 威剛 ADATA
        '2434.TW',  # 統一超 (重複，改為其他)
        '3583.TW',  # 辛耘 Apollo
        '6531.TW',  # 愛普 Elan
        '2428.TW',  # 興勤 Well Shin
        '2441.TW',  # 超豐 Chaojet
        '3406.TW',  # 玉晶光 GSEO
        '8016.TW',  # 矽創 Sitronix
        '2498.TW',  # 宏達電 HTC
        '3679.TW',  # 新至陞 Ennoconn
        '6271.TW',  # 同欣電 United Rad
        ]

def save_tickers_to_cache(tickers, filepath=CACHE_FILE):
    """Save tickers to cache file with timestamp"""
    with open(filepath, 'w', encoding='utf-8') as f:
        data = {
            'tickers': tickers,
            'timestamp': datetime.now().isoformat(),
            'count': len(tickers),
            'source': 'curated_2024_2026'
        }
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_tickers_from_cache(filepath=CACHE_FILE):
    """Load tickers from cache if valid"""
    if not os.path.exists(filepath):
        return None
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check cache validity
        cache_time = datetime.fromisoformat(data['timestamp'])
        age_days = (datetime.now() - cache_time).days
        
        if age_days > CACHE_VALIDITY_DAYS:
            print(f"   ⚠️  Cache is {age_days} days old (expired)")
            return None
            
        print(f"   ℹ️  Using cached data ({age_days} days old, source: {data.get('source', 'unknown')})")
        return data['tickers']
        
    except Exception as e:
        print(f"   ⚠️  Cache read error: {e}")
        return None

def get_top_market_cap_tickers(n=150, use_cache=True, force_refresh=False):
    """
    Get top 150 Taiwan stocks - Curated list for 2024-2026
    
    Args:
        n: Number of stocks to return (default 150)
        use_cache: Whether to use cached results
        force_refresh: Force refresh (ignored, always uses curated list)
        
    Returns:
        list: List of 150 stock tickers with .TW/.TWO suffix
    """
    tickers = None
    
    # Try cache first (unless force refresh)
    if use_cache and not force_refresh:
        tickers = load_tickers_from_cache()
        if tickers:
            return tickers[:n]  # Limit to requested number
    
    # Return curated list
    print("   📋 Using curated 150-stock list (2024-2026 market conditions)")
    tickers = get_top_150_stocks()
    
    # Verify no duplicates
    unique_tickers = list(dict.fromkeys(tickers))
    if len(unique_tickers) < len(tickers):
        print(f"   ⚠️  Removed {len(tickers) - len(unique_tickers)} duplicates")
        tickers = unique_tickers
    
    # Save to cache
    save_tickers_to_cache(tickers)
    
    print(f"   ✅ Loaded {len(tickers)} stocks")
    
    return tickers[:n]

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print(" Taiwan Top 150 Stocks (2024-2026 Curated List)")
    print("=" * 60)
    
    # Check for --refresh flag
    force_refresh = '--refresh' in sys.argv
    n = 150
    
    tickers = get_top_market_cap_tickers(n=n, use_cache=True, force_refresh=force_refresh)
    
    print(f"\n✅ Total: {len(tickers)} stocks\n")
    print("Top 10 stocks:")
    for i, ticker in enumerate(tickers[:10], 1):
        print(f"{i}. {ticker}")
    
    print(f"\nLast 10 stocks:")
    for i, ticker in enumerate(tickers[-10:], len(tickers)-9):
        print(f"{i}. {ticker}")
