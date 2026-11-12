/**
 * Live metal prices in Google Sheets.
 *
 *   =METALPRICE("XAU")              gold, US dollars per troy ounce
 *   =METALPRICE("XAU", "EUR", "g")  gold, euros per gram
 *   =METALPRICE("XAG", "INR", "kg") silver, rupees per kilogram
 *
 * Setup:
 *   1. In your sheet: Extensions > Apps Script. Paste this file and save.
 *   2. In the Apps Script editor: Project Settings > Script Properties.
 *      Add a property named METALCHARTS_KEY with your key (mc_live_...).
 *   3. Use =METALPRICE("XAU") in any cell.
 *
 * Why a script and not IMPORTDATA: the key stays in Script Properties, where
 * people you share the sheet with can't read it. An IMPORTDATA formula has to
 * carry the key in its URL. See README.md in this folder for that option.
 *
 * Results are cached for six hours (the longest Apps Script allows), so
 * each distinct combination of symbol, currency and unit costs at most four
 * requests a day. That keeps a small sheet inside the free tier of 200
 * requests a month.
 *
 * @param {string} symbol   XAU, XAG, XPT, XPD, HG and the other metal codes.
 * @param {string} currency Optional ISO code, e.g. "EUR". Default USD.
 * @param {string} unit     Optional: toz, g, kg, lb, mt or tola.
 * @return {number} The latest price.
 * @customfunction
 */
function METALPRICE(symbol, currency, unit) {
  var key = PropertiesService.getScriptProperties().getProperty("METALCHARTS_KEY");
  if (!key) throw new Error("Add a script property named METALCHARTS_KEY");

  symbol = String(symbol).toUpperCase();
  var query = "?symbols=" + encodeURIComponent(symbol) +
    (currency ? "&currency=" + encodeURIComponent(currency) : "") +
    (unit ? "&unit=" + encodeURIComponent(unit) : "");

  var cache = CacheService.getScriptCache();
  var hit = cache.get(query);
  if (hit) return Number(hit);

  var res = UrlFetchApp.fetch("https://api.metalcharts.org/v1/prices" + query, {
    headers: { Authorization: "Bearer " + key },
    muteHttpExceptions: true,
  });
  if (res.getResponseCode() !== 200) {
    throw new Error("MetalCharts API returned " + res.getResponseCode());
  }

  var quote = JSON.parse(res.getContentText()).data[symbol];
  if (!quote) throw new Error("No price for " + symbol);

  cache.put(query, String(quote.price), 21600);
  return quote.price;
}
