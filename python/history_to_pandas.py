"""Daily gold prices as a pandas DataFrame.

    pip install requests pandas
    METALCHARTS_API_KEY=mc_live_... python history_to_pandas.py

/v1/history/{symbol} takes range (1M, 6M, 1Y, 5Y, ALL) or start and end
dates, and interval (15m, 30m, 1h, 4h, 1d, 1w, 1M). The free tier reads 30
days of daily bars, which is what RANGE = "1M" asks for. "1Y" needs Starter
or above, longer ranges and intraday intervals a higher plan.
"""
import os

import pandas as pd
import requests

API_KEY = os.environ["METALCHARTS_API_KEY"]
SYMBOL = "XAU"  # XAG silver, XPT platinum, XPD palladium, HG copper
RANGE = "1M"

res = requests.get(
    f"https://api.metalcharts.org/v1/history/{SYMBOL}",
    params={"range": RANGE, "interval": "1d"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=30,
)
# A 403 here means the range reaches past your plan's history.
res.raise_for_status()

df = pd.DataFrame(res.json()["data"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.set_index("timestamp")

print(df[["open", "high", "low", "close"]].tail())
print(f"\n{len(df)} bars, {df.index.min().date()} to {df.index.max().date()}")
