<?php
// Every metal's latest price with plain cURL, no dependencies.
//
//   METALCHARTS_API_KEY=mc_live_... php prices.php

$key = getenv("METALCHARTS_API_KEY");
if (!$key) {
    fwrite(STDERR, "Set METALCHARTS_API_KEY\n");
    exit(1);
}

$ch = curl_init("https://api.metalcharts.org/v1/prices");
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ["Authorization: Bearer $key"],
    CURLOPT_TIMEOUT => 10,
]);

$body = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// A failed call still returns a parseable JSON body, so check the status.
if ($code !== 200) {
    fwrite(STDERR, "MetalCharts API returned $code\n");
    exit(1);
}

$data = json_decode($body, true)["data"];
foreach ($data as $symbol => $quote) {
    printf("%-5s %12.4f\n", $symbol, $quote["price"]);
}
