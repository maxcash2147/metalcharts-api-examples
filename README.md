# MetalCharts API examples

Working examples for the [MetalCharts metals price API](https://metalcharts.org/metals-api): live and historical prices for gold, silver, platinum, palladium, copper and base metals as JSON or CSV, plus COMEX warehouse inventory, CFTC Commitments of Traders positioning, and Shanghai (SGE, SHFE), Guangzhou (GFEX), LBMA vault and India data.

- **Base URL:** `https://api.metalcharts.org`
- **Auth:** `Authorization: Bearer mc_live_YOUR_KEY`
- **Free tier:** 200 requests a month and 30 days of daily history, no card. Commercial use is allowed on every plan. A public page or app on the free plan must show a "Metal prices by MetalCharts" link to https://metalcharts.org next to the data; paid plans don't need it.
- **Docs:** [API reference](https://metalcharts.org/metals-api/docs) (every endpoint, parameter and response field), [more examples](https://metalcharts.org/metals-api/examples), [OpenAPI 3.0 document](https://api.metalcharts.org/docs/json)
- **Pricing:** [metalcharts.org/api-pricing](https://metalcharts.org/api-pricing)

[Get a free API key](https://metalcharts.org/metals-api)

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
| [`google-sheets/METALPRICE.gs`](google-sheets/METALPRICE.gs) | `=METALPRICE("XAU")` custom function for Google Sheets |
| [`excel/prices.pq`](excel/prices.pq) | Live prices table in Excel with Power Query |
| [`curl.sh`](curl.sh) | Prices, conversion, history and COMEX inventory with curl |

Every example reads the key from the `METALCHARTS_API_KEY` environment variable, except the spreadsheet ones, which say where the key goes.

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

Exchange data (COMEX, LBMA, Shanghai, India and CFTC positioning) starts on the Pro plan. The [API reference](https://metalcharts.org/metals-api/docs) lists all 59 endpoints with their parameters, response fields and the plan each needs.

## Things worth knowing

- **JSON by default, CSV on request.** Add `format=csv` to any endpoint whose response is a list.
- **No WebSocket.** The API is REST over HTTPS. Spot responses are cached for about 30 seconds, so polling faster than that returns the same quote.
- **One request, every metal.** A backend that polls `/v1/prices` every 10 minutes uses about 4,300 requests a month.
- **Rate limits are in the headers.** Responses carry `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`. A key over its per-minute limit gets a 429 with `Retry-After`.
- **Errors are JSON:** 400 for an invalid parameter, 401 for a missing or invalid key, 403 when the request needs a higher plan or reaches past the plan's history.
- **AI assistants:** a hosted MCP server exposes the same data to Claude, ChatGPT and other MCP clients. See [metalcharts.org/metals-api/mcp](https://metalcharts.org/metals-api/mcp).

## License

MIT. See [LICENSE](LICENSE). The examples are free to copy into your own projects. Use of the API itself is covered by the [API terms](https://metalcharts.org/api-terms).
