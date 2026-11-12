# n8n templates

Two workflows for [n8n](https://n8n.io) that use the MetalCharts API with built-in nodes only.

| File | What it does | Requests a month |
|---|---|---|
| [`daily-gold-silver-to-google-sheets.json`](daily-gold-silver-to-google-sheets.json) | Appends the gold and silver price, their 24-hour change and the gold/silver ratio to a Google Sheet once a day | about 31 |
| [`gold-move-alert.json`](gold-move-alert.json) | Checks gold every 6 hours and posts to a Slack, Discord or other webhook when the 24-hour change reaches 2% up or down | about 124 |

Both fit inside the free plan's 200 requests a month, together as well as on their own.

## Import

1. Download the JSON file (open it on GitHub, click **Raw**, save the page).
2. In n8n, open **Workflows**, click **Create Workflow**, then use the **...** menu and pick **Import from File**. You can also copy the file's contents and paste them straight onto an empty canvas.

## Set the API key

The HTTP Request nodes send the key in a header, using n8n's **Header Auth** credential:

1. Get a free key at [metalcharts.org/metals-api](https://metalcharts.org/metals-api).
2. Open the **Get gold and silver prices** (or **Get gold price**) node.
3. Under **Credential for Header Auth**, choose **Create new credential**.
4. Set **Name** to `Authorization` and **Value** to `Bearer mc_live_your_key_here`, with your real key after `Bearer `.
5. Save. Both templates can share the same credential.

n8n stores the key encrypted, and it is not included when you export or share the workflow.

## Daily price to Google Sheets

1. Create a Google Sheet with these headers in row 1: `date`, `gold_usd_oz`, `gold_change_pct`, `silver_usd_oz`, `silver_change_pct`, `gold_silver_ratio`.
2. In the **Append row** node, connect your Google account and pick the spreadsheet and the tab.
3. Activate the workflow. It runs at 21:00 in the workflow's time zone (set it under **Settings**).

Prices are US dollars per troy ounce. For another currency or unit, add `currency` (for example `EUR`) and `unit` (`g`, `kg`, `toz`, `tola`) to the query parameters of the HTTP Request node and rename the columns to match.

## Gold move alert

1. In the **Send alert** node, replace the URL with your webhook. A Slack incoming webhook reads the `text` field and a Discord webhook reads `content`; the node sends both.
2. Activate the workflow.

The threshold is `THRESHOLD` at the top of the **Check the move** Code node. It alerts at most once per direction per day. That memory is kept in the workflow's static data, which n8n only saves for runs started by the trigger, so a manual test run alerts every time it crosses the threshold.

On a paid plan you can check more often: hourly is about 730 requests a month and every 15 minutes about 2,900, both within Starter's 10,000. For email instead of a webhook, replace **Send alert** with a **Send Email** node and use `{{ $json.message }}` as the text.

## Attribution

On the free plan, anything public that shows the data (a shared sheet, a website, a public channel) needs a visible "Metal prices by MetalCharts" link to https://metalcharts.org. Paid plans don't need it.
