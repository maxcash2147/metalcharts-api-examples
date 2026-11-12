"""Rebuild MetalCharts.postman_collection.json from the live OpenAPI document.

    python postman/generate_collection.py

Standard library only. Pass a local OpenAPI file as the first argument to
build from that instead.
"""
import json
import sys
import urllib.request
import uuid
from pathlib import Path

SPEC_URL = "https://api.metalcharts.org/docs/json"
OUT = Path(__file__).with_name("MetalCharts.postman_collection.json")

if len(sys.argv) > 1:
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
else:
    # Cloudflare refuses urllib's default User-Agent, so send our own.
    request = urllib.request.Request(SPEC_URL, headers={"User-Agent": "metalcharts-postman-generator"})
    with urllib.request.urlopen(request, timeout=30) as res:
        spec = json.load(res)

DOCS = "https://metalcharts.org/metals-api/docs"

# Values for parameters the spec gives no example for. Keyed by (path, name)
# or by name alone.
VALUES = {
    ("/v1/prices", "symbols"): "XAU,XAG",
    ("/v1/history/{symbol}", "range"): "1M",
    ("/v1/history/{symbol}", "interval"): "1d",
    ("/v1/history/{symbol}", "start"): "2026-01-01",
    ("/v1/history/{symbol}", "end"): "2026-06-30",
    ("/v1/currency/history", "currency"): "EUR",
    ("/v1/currency/history", "range"): "1M",
    ("/v1/convert", "from"): "XAU",
    ("/v1/convert", "to"): "EUR",
    ("/v1/convert", "amount"): "10",
    ("/v1/convert", "unit"): "g",
    ("/v1/shfe/settlement", "symbol"): "au",
    ("/v1/shfe/inventory", "symbol"): "cu",
    ("/v1/comex/inventory", "symbol"): "XAG",
    ("/v1/comex/depositories", "symbol"): "XAU",
    ("/v1/comex/depositories", "depository"): "brink",
    ("/v1/comex/volume-oi", "symbol"): "XAU",
    ("/v1/comex/delivery-notices", "symbol"): "XAU",
    ("/v1/sge/trading", "contract"): "Au99.99",
    ("/v1/sge/benchmark", "metal"): "gold",
    ("/v1/gfex/settlement", "symbol"): "pt",
    ("/v1/gfex/premium", "symbol"): "pt",
    ("/v1/lbma/vault", "metal"): "gold",
    ("/v1/lbma/clearing", "metal"): "gold",
    ("/v1/cot", "metal"): "XAU",
    ("/v1/supply", "metal"): "XAG",
    ("/v1/news/search", "q"): "central bank gold",
    ("/v1/news/feed", "limit"): "10",
    ("/v1/news/feed", "symbols"): "XAU",
    ("/v1/news/{symbol}", "limit"): "10",
    ("/v1/india/history", "symbol"): "XAU",
    ("/v1/indices", "symbols"): "DXY",
    ("/v1/indices/history/{symbol}", "range"): "1M",
    ("/v1/commodities/{symbol}/history", "range"): "1M",
    ("/v1/crypto/{symbol}/history", "range"): "1M",
    ("/v1/etfs/{symbol}/history", "range"): "1M",
    ("/v1/markets/{symbol}/history", "range"): "1M",
    ("/v1/news/sentiment/candles/{symbol}", "range"): "1M",
    ("/v1/economic-calendar", "days"): "7",
    "currency": "EUR",
    "unit": "g",
    "karat": "22",
    "range": "1Y",
    "sort": "symbol",
    "order": "asc",
    "limit": "50",
}

# Optional parameters switched on by default, so each request returns
# something useful as it stands. Everything else is listed but disabled.
ENABLED = {
    ("/v1/prices", "symbols"),
    ("/v1/history/{symbol}", "range"),
    ("/v1/history/{symbol}", "interval"),
    ("/v1/currency/history", "range"),
    ("/v1/convert", "amount"),
    ("/v1/convert", "unit"),
    ("/v1/news/search", "q"),
    ("/v1/news/feed", "limit"),
    ("/v1/instruments", "search"),
}

# Short descriptions for parameters the spec leaves undocumented.
PARAM_NOTES = {
    "symbols": "Comma-separated symbols.",
    "range": "Window such as 1M, 6M, 1Y, 5Y or ALL.",
    "interval": "Candle size: 15m, 30m, 45m, 1h, 2h, 4h, 8h, 1d, 1w or 1M. Intraday needs a paid plan.",
    "start": "YYYY-MM-DD. Overrides range.",
    "end": "YYYY-MM-DD, used with start. Defaults to now.",
    "sort": "Field to sort by.",
    "order": "asc or desc.",
    "limit": "Maximum rows to return.",
}

PLAN_NOTE = (
    "\n\nPlans, limits and the full field list: " + DOCS
)


def clean_path(path: str) -> str:
    return path[:-1] if path.endswith("/") and path != "/" else path


def example(path, param):
    schema = param.get("schema", {})
    examples = schema.get("examples")
    if (path, param["name"]) in VALUES:
        return VALUES[(path, param["name"])]
    if examples:
        return str(examples[0])
    return VALUES.get(param["name"], "")


def describe(param):
    schema = param.get("schema", {})
    text = schema.get("description") or param.get("description") or PARAM_NOTES.get(param["name"], "")
    if param.get("required"):
        text = ("Required. " + text).strip() if not text.startswith("Required") else text
    return text


def request_item(path, op):
    path = clean_path(path)
    segments = [s for s in path.split("/") if s]
    postman_path = [":" + s[1:-1] if s.startswith("{") else s for s in segments]

    query, variables = [], []
    for param in op.get("parameters", []):
        value = example(path, param)
        if param["in"] == "path":
            variables.append({"key": param["name"], "value": value, "description": describe(param)})
        elif param["in"] == "query":
            entry = {"key": param["name"], "value": value, "description": describe(param)}
            if not param.get("required") and (path, param["name"]) not in ENABLED:
                entry["disabled"] = True
            query.append(entry)

    if path in ("/v1/prices", "/v1/history/{symbol}"):
        query.append({
            "key": "format",
            "value": "csv",
            "description": "csv returns the same data as text/csv.",
            "disabled": True,
        })

    return build_item(op["summary"], postman_path, query, variables, op.get("description", ""))


def build_item(name, postman_path, query, variables, description, headers=None):
    raw = "{{baseUrl}}/" + "/".join(postman_path)
    enabled = [q for q in query if not q.get("disabled")]
    if enabled:
        raw += "?" + "&".join(f"{q['key']}={q['value']}" for q in enabled)
    url = {"raw": raw, "host": ["{{baseUrl}}"], "path": postman_path}
    if query:
        url["query"] = query
    if variables:
        url["variable"] = variables
    return {
        "name": name,
        "request": {
            "method": "GET",
            "header": headers or [{"key": "Accept", "value": "application/json"}],
            "url": url,
            "description": (description or "").strip() + PLAN_NOTE,
        },
        "response": [],
    }


folders = {}
for path, ops in spec["paths"].items():
    op = ops.get("get")
    if not op:
        continue
    tag = (op.get("tags") or ["Other"])[0]
    folders.setdefault(tag, []).append(request_item(path, op))

# Endpoints the OpenAPI document does not list yet.
usage = build_item(
    "Your usage and limits",
    ["v1", "usage"],
    [],
    [],
    "Your plan, its per-minute and monthly limits, and what you have used this month, "
    "with a 30-day daily history. Costs no weight, so checking it never uses quota.",
)
stream = build_item(
    "Stream live prices (Server-Sent Events)",
    ["v1", "stream", "prices"],
    [
        {"key": "symbols", "value": "XAU,XAG", "description": "Comma-separated symbols. Omit for every metal."},
        {"key": "currency", "value": "EUR", "description": "ISO 4217 code. Default USD.", "disabled": True},
        {"key": "unit", "value": "g", "description": "toz, g, kg, lb, mt or tola.", "disabled": True},
    ],
    [],
    "Holds the connection open and sends text/event-stream. The first event is `snapshot` "
    "with every requested symbol (`data: {\"data\": {\"XAU\": {...}}, \"timestamp\": \"...\"}`), "
    "then a `price` event (`data: {\"symbol\": \"XAU\", ...quote}`) each time a quote changes. "
    "A `: ping` comment arrives about every 15 seconds. The server may close the stream at any "
    "time, so clients should reconnect with backoff.\n\n"
    "Concurrent connections: Pro 1, Ultimate 10, Enterprise 50. Other plans get a 403 with "
    "`required_plan`, and one connection too many gets a 429.",
    headers=[{"key": "Accept", "value": "text/event-stream"}],
)
folders.setdefault("Prices", []).append(stream)

tag_descriptions = {t["name"]: t.get("description", "") for t in spec.get("tags", [])}
order = [t["name"] for t in spec.get("tags", [])]
items = [{
    "name": "Account",
    "description": "Your plan and usage. Free to call.",
    "item": [usage],
}]
for tag in order + sorted(set(folders) - set(order)):
    if tag not in folders:
        continue
    items.append({"name": tag, "description": tag_descriptions.get(tag, ""), "item": folders[tag]})

collection = {
    "info": {
        "_postman_id": str(uuid.uuid5(uuid.NAMESPACE_URL, "https://api.metalcharts.org/postman")),
        "name": "MetalCharts API",
        "description": (
            spec["info"]["description"]
            + "\n\n## Setup\n\n"
            "1. Get a free API key at https://metalcharts.org/metals-api (200 requests a month, no card).\n"
            "2. Open the collection's Variables tab and set `apiKey` to your key (`mc_live_...`). "
            "Put it in the Current value column so it stays on your machine and is not synced or shared.\n"
            "3. Send any request. Auth is set once on the collection: `Authorization: Bearer {{apiKey}}`.\n\n"
            "Optional parameters are listed on each request but switched off; tick them to use them.\n\n"
            "- API reference: " + DOCS + "\n"
            "- Pricing: https://metalcharts.org/api-pricing\n"
            "- OpenAPI 3.0 document: https://api.metalcharts.org/docs/json\n"
            "- Code examples: https://github.com/maxcash2147/metalcharts-api-examples"
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "auth": {
        "type": "bearer",
        "bearer": [{"key": "token", "value": "{{apiKey}}", "type": "string"}],
    },
    "variable": [
        {"key": "baseUrl", "value": spec["servers"][0]["url"], "type": "string"},
        {"key": "apiKey", "value": "mc_live_your_key_here", "type": "string"},
    ],
    "item": items,
}

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(collection, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

count = sum(len(f["item"]) for f in items)
print(f"{count} requests in {len(items)} folders -> {OUT}")
