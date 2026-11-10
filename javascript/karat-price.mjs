// 22 karat gold in Indian rupees per gram.
//
//   METALCHARTS_API_KEY=mc_live_... node karat-price.mjs
//
// Node 18 or later (native fetch). `karat` prices gold at nominal purity,
// the karat divided by 24. Change the three values for 14K in dollars or
// 18K in dirhams.

const API_KEY = process.env.METALCHARTS_API_KEY;
if (!API_KEY) throw new Error("Set METALCHARTS_API_KEY");

const url = new URL("https://api.metalcharts.org/v1/prices");
url.search = new URLSearchParams({ symbols: "XAU", currency: "INR", unit: "g", karat: "22" });

const res = await fetch(url, { headers: { Authorization: `Bearer ${API_KEY}` } });
if (!res.ok) throw new Error(`MetalCharts API returned ${res.status}`);

const { data } = await res.json();
console.log(`22K gold: ${data.XAU.price.toFixed(2)} INR per gram`);
