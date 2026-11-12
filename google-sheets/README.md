# MetalCharts in Google Sheets

Two ways to get metal prices into a sheet. The one-line formula is quicker to set up. The Apps Script function keeps your API key out of the sheet.

## Option 1: one formula with IMPORTDATA

The API accepts the key as an `api_key` query parameter and returns CSV with `format=csv`, so a plain `IMPORTDATA` formula works with no script:

```
=IMPORTDATA("https://api.metalcharts.org/v1/prices?symbols=XAU&format=csv&api_key=YOUR_KEY")
```

This fills a small table: a header row with the field names, then one row per symbol. To put only the price in a cell, look the column up by name:

```
=LET(t, IMPORTDATA("https://api.metalcharts.org/v1/prices?symbols=XAU&format=csv&api_key=YOUR_KEY"), INDEX(t, 2, MATCH("price", INDEX(t, 1, 0), 0)))
```

The usual parameters work in the URL:

```
Gold in euros per gram
=IMPORTDATA("https://api.metalcharts.org/v1/prices?symbols=XAU&currency=EUR&unit=g&format=csv&api_key=YOUR_KEY")

Gold and silver in one table
=IMPORTDATA("https://api.metalcharts.org/v1/prices?symbols=XAU,XAG&format=csv&api_key=YOUR_KEY")

The last 30 days of daily gold bars (timestamp, price, open, high, low, close, volume)
=IMPORTDATA("https://api.metalcharts.org/v1/history/XAU?range=1M&interval=1d&format=csv&api_key=YOUR_KEY")
```

Two things to know before you use it:

- **The key is visible to anyone who can see the sheet.** It sits in the formula, so anyone with view access can read it, and it stays in the version history after you delete it. Use a key you can throw away: on a paid plan, create a separate key for the sheet in the [API console](https://metalcharts.org/api-console). If the sheet is shared and access changes, or the sheet becomes public, revoke that key and create a new one. The free plan has one key, so on the free plan keep the sheet private or use Option 2.
- **Every refresh is a request.** Google re-fetches `IMPORTDATA` on its own schedule, roughly once an hour while the sheet is open, and each fetch counts toward your monthly allowance. A free key (200 requests a month) suits a sheet you open now and then. Put several symbols in one formula rather than one formula per symbol, since `symbols=XAU,XAG,XPT` costs the same single request.

## Option 2: Apps Script custom function (key stays private)

[`METALPRICE.gs`](METALPRICE.gs) adds a `=METALPRICE()` function. The key lives in the script's properties, where people you share the sheet with can't see it, and results are cached for six hours so a sheet uses few requests.

```
=METALPRICE("XAU")              gold, US dollars per troy ounce
=METALPRICE("XAU", "EUR", "g")  gold, euros per gram
=METALPRICE("XAG", "INR", "kg") silver, rupees per kilogram
```

Setup:

1. In your sheet, open **Extensions > Apps Script**, paste the contents of `METALPRICE.gs` and save.
2. In the Apps Script editor, open **Project Settings > Script Properties** and add a property named `METALCHARTS_KEY` with your key (`mc_live_...`).
3. Use `=METALPRICE("XAU")` in any cell.

Note that people with edit access to the sheet can open the script project, so share edit access only with people you would trust with the key.

## Attribution

On the free plan, a sheet that shows the data publicly (published to the web, or open to anyone with the link) needs a visible "Metal prices by MetalCharts" link to https://metalcharts.org near the data. Paid plans don't need it.
