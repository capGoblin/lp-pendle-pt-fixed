# CoinMarketCap MCP Reference (cmc-mcp)

Source: https://raw.githubusercontent.com/openCMC/skills-for-ai-agents-by-CoinMarketCap/main/skills/cmc-mcp/SKILL.md
Verified live: 2026-06-21 10:00–10:08 UTC

## MCP setup

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": {
        "X-CMC-MCP-API-KEY": "your-api-key"
      }
    }
  }
}
```

Get your API key: https://pro.coinmarketcap.com/login

## Plan tier (verified live 2026-06-21)

- 15,000 API calls per month
- 50 calls per minute
- 14,977 calls remaining at time of verification (had used 23)

## All 12 tools in the official cmc-mcp skill

| Tool | Purpose | Used by `lp-pendle-pt-fixed`? |
|---|---|---|
| `mcp__cmc-mcp__search_cryptos` | Resolve symbol/name → CMC id | ✅ yes |
| `mcp__cmc-mcp__get_crypto_quotes_latest` | Spot price, mcap, 24h change | ✅ yes |
| `mcp__cmc-mcp__get_crypto_info` | Project background, tags, links | ✅ yes (replaces non-existent `get_crypto_security_detail`) |
| `mcp__cmc-mcp__get_crypto_metrics` | Holder distribution, whales | optional |
| `mcp__cmc-mcp__get_crypto_technical_analysis` | RSI, MA, MACD, Fib, pivots | ✅ yes (RSI filter) |
| `mcp__cmc-mcp__get_crypto_latest_news` | Headlines, catalyst check | ✅ yes (security incident check) |
| `mcp__cmc-mcp__search_crypto_info` | Semantic search on whitepapers | ✅ yes (fallback for `get_crypto_security_detail`) |
| `mcp__cmc-mcp__get_global_metrics_latest` | Total mcap, fear/greed, dominance, defi volume | ✅ yes (regime tag) |
| `mcp__cmc-mcp__get_global_crypto_derivatives_metrics` | Aggregate derivatives volume | not used (per-market funding not available via REST) |
| `mcp__cmc-mcp__get_crypto_marketcap_technical_analysis` | TA on total crypto mcap | not used |
| `mcp__cmc-mcp__trending_crypto_narratives` | Hot narratives | not used |
| `mcp__cmc-mcp__get_upcoming_macro_events` | Fed, regulatory, unlocks | ✅ yes (catalyst filter) |

## Tool spec details

### search_cryptos

Returns: id, name, symbol, slug, rank, is_active, first_historical_data, last_historical_data, platform{id, name, symbol, slug, token_address}.

Most tools require the numeric CMC id (not the name or symbol). **Always search first, then call other tools with the id.**

### get_crypto_quotes_latest

Returns: price, market_cap, volume_24h, percent_change_1h, percent_change_24h, percent_change_7d, percent_change_30d, percent_change_90d, percent_change_1y, circulating_supply, total_supply, max_supply, cmc_rank, dominance, etc.

Batch-friendly: pass `id=1,1027,5426` for multiple coins.

### get_crypto_info

Returns: description, category, website, social links, explorer URLs, tags, launch date, notice (warnings).

### get_crypto_technical_analysis

Returns: SMA (7d, 30d, 200d), EMA (7d, 30d, 200d), RSI, MACD, signal, Fib levels, pivot points.

### get_crypto_latest_news

Returns: headlines, descriptions, content, URLs, publish dates. Filter by coin id.

### get_global_metrics_latest

Returns: total_market_cap, total_volume_24h, altcoin_volume_24h, defi_volume_24h, defi_market_cap, stablecoin_volume_24h, btc_dominance, eth_dominance, derivatives_volume_24h (aggregate only).

### get_upcoming_macro_events

Returns: scheduled events (Fed FOMC, regulatory deadlines, major unlocks, etc.) with timestamps.

## REST endpoint URL patterns (for direct calls bypassing MCP)

| Tool | REST URL |
|---|---|
| search_cryptos | `GET /v1/cryptocurrency/map?symbol={SYM}` (NOT `/v1/cryptocurrency/search` — that 404s) |
| get_crypto_quotes_latest | `GET /v1/cryptocurrency/quotes/latest?id={ID}&convert=USD` |
| get_crypto_info | `GET /v1/cryptocurrency/info?id={ID}` |
| get_global_metrics_latest | `GET /v1/global-metrics/quotes/latest` (NOT `/v1/global-metrics/latest` — that 404s) |

Auth header: `X-CMC_PRO_API_KEY: {key}`.

## Error handling

- **404 on a URL:** the URL pattern is wrong. Refer to the table above.
- **429 rate limited:** wait `Retry-After` seconds, retry with backoff. Drop non-essential calls first.
- **Tool fails (transient):** retry once. If still failing, note the data gap and continue with other data.
- **Coin not found in search:** ask the user to verify spelling, or try the contract address.
