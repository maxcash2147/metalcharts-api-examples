# MetalCharts API examples

Working examples for the [MetalCharts metals price API](https://metalcharts.org/metals-api): live and historical prices for gold, silver, platinum, palladium, copper and base metals as JSON or CSV, plus COMEX warehouse inventory, CFTC Commitments of Traders positioning, and Shanghai (SGE, SHFE), Guangzhou (GFEX), LBMA vault and India data.

- **Base URL:** `https://api.metalcharts.org`
- **Auth:** `Authorization: Bearer mc_live_YOUR_KEY`. For tools that can't set headers (spreadsheet formulas, some no-code tools), GET requests also accept `api_key=mc_live_YOUR_KEY` as a query parameter.
- **Free tier:** 200 requests a month and 30 days of daily history, no card. Commercial use is allowed on every plan. A public page or app on the free plan must show a "Metal prices by MetalCharts" link to https://metalcharts.org next to the data; paid plans don't need it.
- **Docs:** [API reference](https://metalcharts.org/metals-api/docs) (every endpoint, parameter and response field), [more examples](https://metalcharts.org/metals-api/examples), [OpenAPI 3.0 document](https://api.metalcharts.org/docs/json)
- **Pricing:** [metalcharts.org/api-pricing](https://metalcharts.org/api-pricing)

[Get a free API key](https://metalcharts.org/metals-api)

## Client libraries

| Language | Install | Source |
|---|---|---|
| Python 3.9+ | `pip install git+https://github.com/maxcash2147/metalcharts-python` | [metalcharts-python](https://github.com/maxcash2147/metalcharts-python) |
| JavaScript / TypeScript (Node 18+, Bun, Deno, edge) | `npm install github:maxcash2147/metalcharts-js` | [metalcharts-js](https://github.com/maxcash2147/metalcharts-js) |

Both read the key from `METALCHARTS_API_KEY`, raise typed errors for plan and rate limits, and handle the live price stream with reconnects:

```python
from metalcharts import MetalCharts

client = MetalCharts()
print(client.prices("XAU")["data"]["XAU"]["price"])
```

```js
import { MetalCharts } from "metalcharts";

const client = new MetalCharts();
const { data } = await client.prices({ symbols: "XAU" });
console.log(data.XAU.price);
```

## Postman, n8n and spreadsheets

- **Postman:** import [`postman/MetalCharts.postman_collection.json`](postman/MetalCharts.postman_collection.json), set the `apiKey` collection variable, and every endpoint is ready to send, grouped by topic with example parameters.
- **n8n:** [`n8n/`](n8n/) has two importable workflows built from standard nodes: a daily gold and silver price log in Google Sheets, and an alert when gold moves 2% in a day.
- **Google Sheets:** one `IMPORTDATA` formula, or a `=METALPRICE("XAU")` custom function that keeps the key private. See [`google-sheets/`](google-sheets/README.md).
- **Excel:** a Power Query table in [`excel/prices.pq`](excel/prices.pq).

## Quick start

One request returns every metal:

```bash
curl -H "Authorization: Bearer mc_live_YOUR_KEY" \
  "https://api.metalcharts.org/v1/prices"
```

Each quote is under its symbol in `data`: `XAU` gold, `XAG` silver, `XPT` platinum, `XPD` palladium, `HG` copper, and the base metals.

Quote in another currency, mass unit or gold karat with query parameters:

```bash
# Gold in euros per gram
curl -H "Authorization: Bearer mc_live_YOUR_KEY" \
  "https://api.metalcharts.org/v1/prices?symbols=XAU&currency=EUR&unit=g"

# 22 karat gold in Indian rupees per gram
curl -H "Authorization: Bearer mc_live_YOUR_KEY" \
  "https://api.metalcharts.org/v1/prices?symbols=XAU&currency=INR&unit=g&karat=22"
```

- `currency`: any of 32 ISO 4217 codes (USD, EUR, GBP, JPY, INR, CNY, AED and more). Conversion uses ECB reference rates.
- `unit`: `toz` (troy ounce), `g`, `kg`, `lb`, `mt` (metric ton) or `tola`.
- `karat`: 24, 23, 22, 21, 20, 18, 16, 15, 14, 12, 10, 9 or 8. Gold only, at nominal purity (karat divided by 24).

## Examples in this repository

| File | What it does |
|---|---|
| [`python/gold_per_gram_eur.py`](python/gold_per_gram_eur.py) | Gold price per gram in euros |
| [`python/history_to_pandas.py`](python/history_to_pandas.py) | Daily gold bars as a pandas DataFrame |
| [`python/history_to_csv.py`](python/history_to_csv.py) | The last 30 days, or any date range, of daily prices saved as CSV |
| [`javascript/karat-price.mjs`](javascript/karat-price.mjs) | 22K gold in rupees per gram (Node 18+) |
| [`javascript/poll-prices.mjs`](javascript/poll-prices.mjs) | Poll every metal on a timer without wasting quota |
| [`php/prices.php`](php/prices.php) | Every metal's price with plain cURL |
| [`go/prices.go`](go/prices.go) | Gold price in Go, standard library only |
| [`google-sheets/README.md`](google-sheets/README.md) | Prices in Google Sheets with one `IMPORTDATA` formula |
| [`google-sheets/METALPRICE.gs`](google-sheets/METALPRICE.gs) | `=METALPRICE("XAU")` custom function for Google Sheets |
| [`excel/prices.pq`](excel/prices.pq) | Live prices table in Excel with Power Query |
| [`curl.sh`](curl.sh) | Prices, conversion, history and COMEX inventory with curl |
| [`postman/MetalCharts.postman_collection.json`](postman/MetalCharts.postman_collection.json) | Postman collection with every endpoint |
| [`n8n/daily-gold-silver-to-google-sheets.json`](n8n/daily-gold-silver-to-google-sheets.json) | n8n workflow: daily gold and silver prices appended to a Google Sheet |
| [`n8n/gold-move-alert.json`](n8n/gold-move-alert.json) | n8n workflow: webhook alert when gold moves 2% in a day |

Every example reads the key from the `METALCHARTS_API_KEY` environment variable, except the spreadsheet, Postman and n8n ones, which say where the key goes.

## Main endpoints

| Endpoint | Returns | Plan |
|---|---|---|
| `GET /v1/prices` | Latest spot prices for every metal, with 24-hour change, high, low, bid and ask | Free |
| `GET /v1/history/{symbol}` | Price history: daily bars back to October 1966 for gold and silver, intraday from 15 minutes | Free (30 days of daily bars), deeper and intraday on paid plans |
| `GET /v1/convert` | Convert between a metal, a currency and a mass unit | Free |
| `GET /v1/currency` | Exchange rates for the 32 supported currencies | Free |
| `GET /v1/metals` | The list of supported metals | Free |
| `GET /v1/comex/inventory` | COMEX registered, eligible and total warehouse stocks | Pro |
| `GET /v1/cot` | CFTC Commitments of Traders positioning | Pro |
| `GET /v1/bulk/history` | Every daily bar for the requested metals as one CSV | Ultimate |
| `GET /v1/stream/prices` | Live prices pushed as Server-Sent Events, no polling | Pro |
| `GET /v1/usage` | Your plan, limits and usage this month. Costs nothing | Free |

Exchange data (COMEX, LBMA, Shanghai, India and CFTC positioning) starts on the Pro plan. The [API reference](https://metalcharts.org/metals-api/docs) lists all 59 endpoints with their parameters, response fields and the plan each needs.

## Things worth knowing

- **JSON by default, CSV on request.** Add `format=csv` to any endpoint whose response is a list.
- **Streaming or polling.** On Pro and above, `GET /v1/stream/prices` keeps one connection open and sends a `snapshot` event, then a `price` event whenever a quote changes (Server-Sent Events, so any HTTP client can read it). Pro allows 1 connection, Ultimate 10, Enterprise 50. On other plans, poll `/v1/prices`: spot responses are cached for about 30 seconds, so polling faster than that returns the same quote.
- **One request, every metal.** A backend that polls `/v1/prices` every 10 minutes uses about 4,300 requests a month.
- **Rate limits are in the headers.** Responses carry `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`. A key over its per-minute limit gets a 429 with `Retry-After`.
- **Errors are JSON:** 400 for an invalid parameter, 401 for a missing or invalid key, 403 when the request needs a higher plan or reaches past the plan's history (with `required_plan` and `upgrade_url` where they apply), 429 over a limit (with `Retry-After` and `retryAt`).
- **AI assistants:** a hosted MCP server exposes the same data to Claude, ChatGPT and other MCP clients. See [metalcharts.org/metals-api/mcp](https://metalcharts.org/metals-api/mcp).

## License

MIT. See [LICENSE](LICENSE). The examples are free to copy into your own projects. Use of the API itself is covered by the [API terms](https://metalcharts.org/api-terms).
