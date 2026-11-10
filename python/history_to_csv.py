"""Save daily prices as a CSV file.

    pip install requests
    METALCHARTS_API_KEY=mc_live_... python history_to_csv.py XAU
    METALCHARTS_API_KEY=mc_live_... python history_to_csv.py XAU 2025-01-01 2025-12-31

With just a symbol it saves the last 30 days, which every plan can read.
Give a start and end date (YYYY-MM-DD) for any other range; the free tier
reads 30 days back and paid plans further.

format=csv returns the same rows as the JSON response, one per line, with a
header row. It works on any endpoint whose response is a list.
"""
import os
import sys
from datetime import date, timedelta

import requests

API_KEY = os.environ["METALCHARTS_API_KEY"]
symbol = sys.argv[1] if len(sys.argv) > 1 else "XAU"
if len(sys.argv) > 3:
    start, end = sys.argv[2], sys.argv[3]
else:
    end = date.today().isoformat()
    start = (date.today() - timedelta(days=29)).isoformat()

res = requests.get(
    f"https://api.metalcharts.org/v1/history/{symbol}",
    params={"start": start, "end": end, "interval": "1d", "format": "csv"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=30,
)
# A 403 here means the range reaches past your plan's history.
res.raise_for_status()

filename = f"{symbol}-{start}-{end}.csv"
with open(filename, "w", encoding="utf-8", newline="") as f:
    f.write(res.text)
print(f"Wrote {filename} ({len(res.text.splitlines()) - 1} rows)")
