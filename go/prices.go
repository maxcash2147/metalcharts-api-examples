// Gold price in Go, standard library only.
//
//	METALCHARTS_API_KEY=mc_live_... go run prices.go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

type pricesResponse struct {
	Data map[string]struct {
		Price     float64 `json:"price"`
		Timestamp string  `json:"timestamp"`
	} `json:"data"`
}

func main() {
	key := os.Getenv("METALCHARTS_API_KEY")
	if key == "" {
		fmt.Fprintln(os.Stderr, "Set METALCHARTS_API_KEY")
		os.Exit(1)
	}

	req, err := http.NewRequest(http.MethodGet, "https://api.metalcharts.org/v1/prices?symbols=XAU", nil)
	if err != nil {
		panic(err)
	}
	req.Header.Set("Authorization", "Bearer "+key)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Fprintf(os.Stderr, "MetalCharts API returned %d\n", resp.StatusCode)
		os.Exit(1)
	}

	var out pricesResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		panic(err)
	}
	gold := out.Data["XAU"]
	fmt.Printf("Gold: %.2f USD per troy ounce (as of %s)\n", gold.Price, gold.Timestamp)
}
