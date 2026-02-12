"""
US Tech Stocks List - User Selected
美股科技股清單 - 用戶指定
"""

US_TECH_STOCKS = [
    'AAPL',   # Apple (corrected from APPL)
    'NVDA',   # NVIDIA
    'MSFT',   # Microsoft
    'GOOGL',  # Alphabet (Google)
    'AMZN',   # Amazon
    'META',   # Meta (Facebook)
    'TSLA',   # Tesla
    'AVGO',   # Broadcom
    'ADBE',   # Adobe
    'CRM',    # Salesforce
    'INTC',   # Intel
    'AMD',    # AMD
    'QCOM',   # Qualcomm
    'TXN',    # Texas Instruments
    'MU'      # Micron Technology
]

if __name__ == "__main__":
    print("\n美股科技股清單 - US Tech Stocks List")
    print("=" * 50)
    for i, ticker in enumerate(US_TECH_STOCKS, 1):
        print(f"{i:2d}. {ticker}")
    print(f"\nTotal: {len(US_TECH_STOCKS)} stocks")
