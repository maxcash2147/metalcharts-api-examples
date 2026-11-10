// Live metal prices in Excel with Power Query.
//
// Setup:
//   1. Data > Get Data > From Other Sources > Blank Query.
//   2. Home > Advanced Editor. Paste this, replacing mc_live_YOUR_KEY.
//   3. When Excel asks how to connect, choose Anonymous: the key is
//      already sent in the header below.
//   4. Close & Load. Use Refresh All to update the table.
//
// Add currency = "EUR" or unit = "g" inside Query to change what is quoted.
// WEBSERVICE() cannot be used for this, because it cannot send the header.
let
    Source = Json.Document(
        Web.Contents(
            "https://api.metalcharts.org/v1/prices",
            [
                Query = [symbols = "XAU,XAG,XPT,XPD"],
                Headers = [Authorization = "Bearer mc_live_YOUR_KEY"]
            ]
        )
    ),
    Quotes = Record.ToTable(Source[data]),
    Renamed = Table.RenameColumns(Quotes, {{"Name", "Symbol"}}),
    Expanded = Table.ExpandRecordColumn(
        Renamed,
        "Value",
        {"price", "changePercent24h", "timestamp"},
        {"Price", "Change 24h %", "As of"}
    )
in
    Expanded
