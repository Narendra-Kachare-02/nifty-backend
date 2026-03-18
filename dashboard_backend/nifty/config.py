from datetime import time

# Market hours in IST (no holidays handling here).
MARKET_OPEN_IST = time(9, 15)
MARKET_CLOSE_IST = time(15, 15)

# Fetch cadence (Celery beat schedule also limits the window).
NIFTY_FETCH_INTERVAL_SECONDS = 60
OPTION_CHAIN_FETCH_INTERVAL_SECONDS = 60
CHART_FETCH_INTERVAL_SECONDS = 60

# NSE endpoints
NSE_BASE_URL = "https://www.nseindia.com"

# Index tracker (NextApi)
NSE_INDEX_TRACKER_PATH = "/api/NextApi/apiClient/indexTrackerApi"
NSE_INDEX_NAME = "NIFTY 50"
NSE_INDEX_TRACKER_FUNCTION_INDEX = "getIndexData"
NSE_INDEX_TRACKER_FUNCTION_CHART = "getIndexChart"

# Chart flags supported
NSE_CHART_FLAGS = ["1D", "1M", "3M", "6M", "1Y"]

# Option chain v3 + contract info
NSE_OPTION_CHAIN_V3_PATH = "/api/option-chain-v3"
NSE_OPTION_CHAIN_CONTRACT_INFO_PATH = "/api/option-chain-contract-info"
NSE_OPTION_CHAIN_TYPE = "Indices"
NSE_OPTION_CHAIN_SYMBOL = "NIFTY"

# NSE often blocks non-browser clients; keep headers stable + minimal.
NSE_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

