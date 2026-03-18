import requests

BASE = "https://www.nseindia.com"
API = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

session = requests.Session()

# Step 1 — get cookies
session.get(BASE, headers=headers)
print(session.cookies)

# Step 2 — call API
response = session.get(API, headers=headers)
print(response.cookies)

data = response.json()


# print("NIFTY VALUE:", data["data"][0]["lastPrice"])

# print("\nStocks:\n")

# for stock in data["data"]:
#     if "symbol" in stock:
#         print(
#             stock["symbol"],
#             stock["lastPrice"],
#             stock["change"],
#             stock["pChange"]
        # )