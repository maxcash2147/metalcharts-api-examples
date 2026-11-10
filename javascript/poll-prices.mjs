// Poll every metal on a timer and keep the latest quotes in memory.
//
//   METALCHARTS_API_KEY=mc_live_... node poll-prices.mjs
//
// One /v1/prices request returns every metal, so there is no need for a
// request per symbol. Spot responses are cached for 30 seconds on the
// server, so polling faster than that returns the same quote. Every 10
// minutes is about 4,300 requests a month.

const API_KEY = process.env.METALCHARTS_API_KEY;
if (!API_KEY) throw new Error("Set METALCHARTS_API_KEY");

const INTERVAL_MS = 10 * 60 * 1000;
let latest = {};

async function refresh() {
  const res = await fetch("https://api.metalcharts.org/v1/prices", {
    headers: { Authorization: `Bearer ${API_KEY}` },
  });

  if (res.status === 429) {
    // Over the per-minute limit: wait as long as the API asks.
    const wait = Number(res.headers.get("retry-after") ?? 60);
    console.warn(`Rate limited, retrying in ${wait}s`);
    setTimeout(refresh, wait * 1000);
    return;
  }
  if (!res.ok) {
    // Keep serving the last good quotes rather than failing.
    console.error(`MetalCharts API returned ${res.status}`);
    return;
  }

  latest = (await res.json()).data;
  const remaining = res.headers.get("x-ratelimit-remaining");
  console.log(
    `${new Date().toISOString()} gold ${latest.XAU?.price} silver ${latest.XAG?.price}` +
      (remaining ? ` (${remaining} left this minute)` : ""),
  );
}

await refresh();
setInterval(refresh, INTERVAL_MS);
