# PHASE_0_CMC_VERIFICATION.md — CMC AI Agent Hub Live Check

**Phase:** 0 (verification, no code)
**Date:** 2026-06-21 10:00–10:15 UTC
**Operator:** capGoblin
**Author:** Sambar (live API calls, no subagent)
**CMC API key:** stored at `/root/.openclaw/credentials/cmc-api-key` (chmod 600), plan: 15,000 calls/month, 50 calls/min, **14,977 credits remaining**

---

## TL;DR — what works, what's broken

| # | Spec assumption | Reality | Action |
|---|---|---|---|
| 1 | `mcp__cmc-mcp__search_cryptos` | ✅ Real, in official cmc-mcp skill | keep |
| 2 | `mcp__cmc-mcp__get_crypto_quotes_latest` | ✅ Real, in official cmc-mcp skill | keep |
| 3 | `mcp__cmc-mcp__get_crypto_metrics` | ✅ Real, in official cmc-mcp skill | keep |
| 4 | `mcp__cmc-mcp__get_crypto_security_detail` | ❌ **DOES NOT EXIST** in official cmc-mcp skill | **REMOVE / replace with `get_crypto_info` + `search_crypto_info`** |
| 5 | `mcp__cmc-mcp__get_crypto_latest_news` | ✅ Real, in official cmc-mcp skill | keep |
| 6 | `mcp__cmc-mcp__get_global_metrics_latest` | ✅ Real, in official cmc-mcp skill | keep |
| 7 | `mcp__cmc-mcp__get_global_crypto_derivatives_metrics` | ⚠️ In MCP tool list, but **no public REST equivalent** — the MCP wraps an internal data source. The public REST endpoint `v1/global-metrics/derivatives*` all return 404. Global metrics endpoint *does* have `derivatives_volume_24h` baked in, but no per-market funding rates via public REST | **flag as MCP-only**; demo can use it via the MCP, not the REST API |

### Bonus discoveries (not in the 7)

The **real** official cmc-mcp skill has 12 tools, not 7. The 5 extras the spec is missing:
- `mcp__cmc-mcp__get_crypto_info` — coin background, links, description, launch date, tags
- `mcp__cmc-mcp__get_crypto_technical_analysis` — SMA/EMA, RSI, MACD, Fib, pivots
- `mcp__cmc-mcp__search_crypto_info` — semantic search across whitepapers/FAQs
- `mcp__cmc-mcp__get_crypto_marketcap_technical_analysis` — TA on total crypto mcap
- `mcp__cmc-mcp__trending_crypto_narratives` — hot narratives
- `mcp__cmc-mcp__get_upcoming_macro_events` — Fed meetings, regulatory deadlines

**For the LP-PT-fixed flagship**, the two most valuable additions are:
- `get_crypto_technical_analysis` (RSI gate on the underlying before entry)
- `get_upcoming_macro_events` (avoid entering PT positions right before a Fed meeting or major unlock)

### Plan reality check

The deep-dive said "330 free calls/month." Wrong by 45×. The plan is actually **15,000 calls/month, 50 calls/min**. Backtest + demo + live verification easily fits.

### x402 (the agentic-commerce proof for the demo)

`https://pro.coinmarketcap.com/x402/v3/cryptocurrency/quotes/latest` — $0.01 USDC per request on Base, no API key.
MCP variant: `https://mcp.coinmarketcap.com/x402/mcp`.
The official `cmc-x402` SKILL.md is in `openCMC/skills-for-ai-agents-by-CoinMarketCap` on GitHub. Confirmed live.

---

## Endpoint-by-endpoint live evidence

### 1. `mcp__cmc-mcp__search_cryptos` ✅

**REST analog:** `GET /v1/cryptocurrency/map?symbol={SYMBOL}` (the spec's `v1/cryptocurrency/search` is **wrong** — 404. Use `map` instead.)

**Live test:**
```bash
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?symbol=sUSDe" \
  -H "X-CMC_PRO_API_KEY: $KEY"
# → {"data":[{"id":29471,"name":"Ethena Staked USDe","symbol":"sUSDe",
#         "slug":"ethena-staked-usde","rank":7905,"is_active":1,
#         "platform":{"id":1,"name":"Ethereum","symbol":"ETH",
#                     "token_address":"0x9d39a5de30e57443bff2a8307a4256c8797a3497"}}]}
```

**Response shape:** `{id, name, symbol, slug, rank, is_active, first_historical_data, last_historical_data, platform{id, name, symbol, slug, token_address}}`. **Spec compatible.**

### 2. `mcp__cmc-mcp__get_crypto_quotes_latest` ✅

**REST analog:** `GET /v1/cryptocurrency/quotes/latest?symbol={SYM}&convert=USD` (or `?id={ID}`)

**Live test:**
```bash
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id=29471&convert=USD" \
  -H "X-CMC_PRO_API_KEY: $KEY"
# → returns full quote object: price, mcap, vol_24h, %_change_1h/24h/7d/30d/90d/1y,
#   circulating_supply, total_supply, max_supply, cmc_rank, dominance, etc.
```

For sUSDe (id 29471): price=$1.2346, mcap=$1.71B, 24h vol=$2.12M. **Live, working.**

### 3. `mcp__cmc-mcp__get_crypto_metrics` ✅

**REST analog:** `GET /v1/cryptocurrency/holders` (or `v2/cryptocurrency/holders/latest` — need to confirm exact route. The MCP tool may wrap a private endpoint.)

**Not tested via REST** — the MCP tool is documented in the official cmc-mcp skill but the public REST endpoint shape is behind CMC's typical holder API. For the flagship, this is a "nice to have" for the optional holder-concentration gate, not a blocker.

### 4. `mcp__cmc-mcp__get_crypto_security_detail` ❌ **DOES NOT EXIST**

This tool is in the **deep-dive spec** but **NOT in the official cmc-mcp skill list**. Searched the official `cmc-mcp/SKILL.md` from `openCMC/skills-for-ai-agents-by-CoinMarketCap` — the `allowed-tools` list has 12 tools and `get_crypto_security_detail` is not one of them.

**Source:** https://raw.githubusercontent.com/openCMC/skills-for-ai-agents-by-CoinMarketCap/main/skills/cmc-mcp/SKILL.md (retrieved 2026-06-21 10:00 UTC)

**The closest equivalent is `mcp__cmc-mcp__get_crypto_info`** which returns:
- description, category, website, social links, explorer URLs
- tags (e.g. "defi", "stablecoin", "asset-backed-stablecoin")
- launch date
- notice (warnings)

**Action:** In the flagship `lp-pendle-pt-fixed` SKILL.md, replace the `get_crypto_security_detail` call with `get_crypto_info` and add `search_crypto_info` for any project-specific security questions (e.g. "is the PT audited?", "what oracle does the SY use?").

### 5. `mcp__cmc-mcp__get_crypto_latest_news` ✅

In the official cmc-mcp skill's `allowed-tools` list. Not directly tested via REST in this verification pass, but the route is documented: `GET /v1/cryptocurrency/news/latest` (or similar). No concerns for the spec.

### 6. `mcp__cmc-mcp__get_global_metrics_latest` ✅

**REST analog:** `GET /v1/global-metrics/quotes/latest` (not `v1/global-metrics/latest` — that 404s.)

**Live test:**
```bash
curl -s "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest" \
  -H "X-CMC_PRO_API_KEY: $KEY"
# → returns total_market_cap, total_volume_24h, altcoin_volume_24h,
#   defi_volume_24h, defi_market_cap, stablecoin_volume_24h,
#   btc_dominance, eth_dominance, derivatives_volume_24h, etc.
```

The `derivatives_volume_24h` field is in here (currently $444.9B, -9.84% 24h) but it's an aggregate, not per-market. **Spec assumption that this gives per-market funding data is wrong — the global metrics endpoint is aggregate only.**

### 7. `mcp__cmc-mcp__get_global_crypto_derivatives_metrics` ⚠️ **MCP-only**

Documented in the official cmc-mcp skill (`get_global_crypto_derivatives_metrics` returns "open interest, funding rates, liquidations, futures vs perpetuals breakdown").

**However:** I cannot find a public REST equivalent. Tested:
- `v1/global-metrics/derivatives` → 404
- `v2/global-metrics/derivatives/quotes/latest` → 404
- `v1/derivatives/quotes/latest` → 404
- `v1/derivatives/global-metrics/quotes/latest` → 404
- `v1/futures/positions` → 404

The MCP tool wraps an internal data source. **For the demo, this is fine** — the agent calls the MCP tool directly, no REST equivalent needed. **For the spec writeup, flag it as MCP-only and avoid claiming REST parity.**

---

## What's wrong with the deep-dive spec (and how to fix it)

1. **Endpoint URL for search:** spec says `v1/cryptocurrency/search` — doesn't exist. Use `v1/cryptocurrency/map?symbol=...`.
2. **Endpoint URL for global metrics:** spec says `v1/global-metrics/latest` — doesn't exist. Use `v1/global-metrics/quotes/latest`.
3. **Tool name wrong:** `get_crypto_security_detail` → not a real tool. Replace with `get_crypto_info` + `search_crypto_info`.
4. **Derivatives REST assumption:** `get_global_crypto_derivatives_metrics` is MCP-only. Demo should call it via the MCP transport, not REST.
5. **Plan tier wrong:** "330 free calls/month" → 15,000/month, 50/min. No backtest budget concern.
6. **5 missing tools:** the real cmc-mcp skill has 12 tools, not 7. Most useful add: `get_crypto_technical_analysis` (RSI filter on the underlying before PT entry).

---

## Sources

- Official cmc-mcp skill (tool list): https://raw.githubusercontent.com/openCMC/skills-for-ai-agents-by-CoinMarketCap/main/skills/cmc-mcp/SKILL.md
- Official openCMC skills repo: https://github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap
- CoinMarketCap AI Agent Hub docs: https://pro.coinmarketcap.com/api/documentation/ai-agent-hub/skills/overview
- x402 SKILL.md: https://raw.githubusercontent.com/openCMC/skills-for-ai-agents-by-CoinMarketCap/main/skills/cmc-x402/SKILL.md
- All curl commands above were run live at the timestamps in the file.
