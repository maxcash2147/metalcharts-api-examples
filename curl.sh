#!/usr/bin/env bash
# The main requests with curl.
#
#   METALCHARTS_API_KEY=mc_live_... ./curl.sh
set -euo pipefail

: "${METALCHARTS_API_KEY:?Set METALCHARTS_API_KEY}"
API="https://api.metalcharts.org"
AUTH="Authorization: Bearer ${METALCHARTS_API_KEY}"

echo "# Every metal, latest price"
curl -sS -H "$AUTH" "$API/v1/prices"
echo

echo "# Gold in euros per gram"
curl -sS -H "$AUTH" "$API/v1/prices?symbols=XAU&currency=EUR&unit=g"
echo

echo "# What 10 grams of gold costs in euros"
curl -sS -H "$AUTH" "$API/v1/convert?from=XAU&to=EUR&amount=10&unit=g"
echo

echo "# The last month of daily silver bars, as CSV"
curl -sS -H "$AUTH" "$API/v1/history/XAG?range=1M&interval=1d&format=csv"
echo

echo "# COMEX silver inventory, newest report (Pro plan or higher)"
curl -sS -H "$AUTH" "$API/v1/comex/inventory?symbol=XAG&type=latest"
echo
