from datetime import time

# Market hours in IST (no holidays handling here).
MARKET_OPEN_IST = time(9, 15)
MARKET_CLOSE_IST = time(15, 30)

# Fetch cadence (Celery beat schedule also limits the window).
NIFTY_FETCH_INTERVAL_SECONDS = 60

# NSE endpoints
NSE_BASE_URL = "https://www.nseindia.com"
NSE_NIFTY_50_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

# NSE often blocks non-browser clients; keep headers stable + minimal.
NSE_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

