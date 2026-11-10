"""Gold price per gram in euros.

    pip install requests
    METALCHARTS_API_KEY=mc_live_... python gold_per_gram_eur.py

/v1/prices quotes in any of 32 currencies (currency=) and six mass units
(unit=toz, g, kg, lb, mt, tola). The conversion uses the ECB reference rate.
"""
import os

import requests

API_KEY = os.environ["METALCHARTS_API_KEY"]

res = requests.get(
    "https://api.metalcharts.org/v1/prices",
    params={"symbols": "XAU", "currency": "EUR", "unit": "g"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=10,
)
# A 401 (bad key) or 429 (rate limit) becomes an exception here.
res.raise_for_status()

quote = res.json()["data"]["XAU"]
print(f"Gold: {quote['price']:.2f} EUR per gram (as of {quote['timestamp']})")
