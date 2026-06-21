---
name: lp-pendle-pt-fixed
description: |
  Recommends Pendle Principal Token (PT) buy-and-hold positions for fixed yield with zero impermanent loss.
  Use when a user asks about fixed-yield DeFi, PT buy-and-hold, Pendle markets, principal-protected yield,
  or "what's the best fixed APY I can lock in on BSC right now."
  Generates a backtestable strategy spec (JSON) the agent can hand to a backtester, an LP allocation engine,
  or a Trust Wallet Agent Kit (TWAK) execution layer. Designed for the BNB Hack Track 2 (Strategy Skills)
  submission, but the spec format generalises to any EVM chain Pendle supports.

  Trigger: "fixed yield", "PT buy-and-hold", "pendle principal token", "zero IL yield",
  "best fixed APY BSC", "/lp-pendle-pt-fixed"

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_info
  - mcp__cmc-mcp__get_crypto_metrics
  - mcp__cmc-mcp__get_crypto_technical_analysis
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_upcoming_macro_events
---

# lp-pendle-pt-fixed

Generate a Pendle Principal Token (PT) buy-and-hold strategy spec. The output is a backtestable JSON spec
that captures the recommended market, the fixed yield locked in, the entry/exit rules, the risk guardrails,
and the data sources. Zero impermanent loss (IL) by design — PT is a fixed-income instrument, not a pair.

## When to use this skill

Use this skill when a user asks any of:

- "What's the best fixed yield I can lock in on BSC right now?"
- "Recommend a Pendle PT position for $X capital."
- "Show me a fixed-income DeFi spec for next 30/60/90 days."
- "Backtest a buy-and-hold PT strategy."
- "I want zero IL — what PT should I buy?"
- "What's the implied APY on sUSDat / USDat / [Pendle market]?"

Do NOT use this skill for:

- Live execution (this is a spec generator, not an execution layer — pair with TWAK for that).
- Variable yield speculation (use YT instead).
- LP positions on Pendle pools (constant-product IL applies).
- Chains Pendle doesn't support (BSC, Ethereum, Arbitrum, Base, Optimism, Mantle, Sonic, Berachain, Monad, Plasma, Hyperliquid).

## What the skill produces

A JSON strategy spec. Example:

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1",
  "venue": "pendle",
  "chain": "bsc",
  "chain_id": 56,
  "instrument": "PT-sUSDat-2026-08-27",
  "underlying_token": "sUSDat",
  "pt_address": "0x23f9a497a5d4d54eaf5e03d94774f17dc1219745",
  "yt_address": "0x11550114dc4c572e6c1eddfbcdbed9480f4847da",
  "sy_address": "0x68930887e1318ef30653a4b7942ab07544ebed4d",
  "market_address": "0x1017e73ce9c219164ce841a980136eb023c55387",
  "expiry": "2026-08-27T00:00:00Z",
  "time_to_maturity_days": 67,
  "expected_fixed_apy": 0.1498,
  "liquidity_usd": 2961210,
  "il_profile": "zero",
  "data_inputs": [
    "pendle.v3.markets.historical-data",
    "cmc.mcp.crypto.quotes.latest",
    "cmc.mcp.crypto.info",
    "cmc.mcp.global.metrics.latest",
    "cmc.mcp.crypto.technical.analysis",
    "cmc.mcp.upcoming.macro.events"
  ],
  "x402_alternative": {
    "endpoint": "https://pro.coinmarketcap.com/x402/v3/cryptocurrency/quotes/latest",
    "mcp_endpoint": "https://mcp.coinmarketcap.com/x402/mcp",
    "cost_per_call_usd": 0.01,
    "currency": "USDC",
    "network": "base"
  },
  "rebalance_rule": "buy-and-hold to maturity; do not roll early unless implied_apy > 0.20 across all open PTs in the market",
  "risk_guardrails": {
    "min_liquidity_usd": 500000,
    "min_time_to_maturity_days": 14,
    "max_position_pct_of_liquidity": 0.02,
    "yield_floor_apy": 0.08,
    "exclude_underlyings_with_24h_drawdown_gt_pct": 0.15
  }
}
```

## Workflow

### Step 1: Pull live Pendle markets on BSC

```bash
curl -s "https://api-v2.pendle.finance/core/v1/56/markets/active" | jq '.results[] | {
  name, address, expiry,
  impliedApy: .details.impliedApy,
  liquidity: .details.liquidity,
  pendleApy: .details.pendleApy,
  pt, yt, sy, underlyingAsset
}'
```

The endpoint returns all currently-active PT markets on BSC. Each market object has:

- `name` — human-readable (e.g. "sUSDat")
- `address` — Pendle market contract
- `expiry` — ISO timestamp of PT maturity
- `details.impliedApy` — the **fixed yield** the PT buyer locks in
- `details.liquidity` — current TVL in USD
- `details.pendleApy` — extra PENDLE token emissions (often near zero)
- `details.aggregatedApy` — combined (implied + pendle emissions)
- `pt` / `yt` / `sy` — chain-prefixed contract addresses (`{chainId}-{address}`)
- `underlyingAsset` — chain-prefixed contract address

### Step 2: Apply the safety filter

Reject any market where:

- `liquidity < $500,000` — backtest story breaks with thin liquidity
- `time_to_maturity < 14 days` — too short to be a meaningful position
- `yieldRange.max < 0.08` (8%) — yield floor
- Underlying token has dropped >15% in 24h (per CMC quote) — risk of mark-to-market drawdown
- Underlying token has a security incident in the last 30 days (per CMC news)

### Step 3: Pull CMC context for the underlying

For each surviving candidate, pull:

```bash
# 1. Resolve underlying symbol to CMC ID
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?symbol={UNDERLYING_SYMBOL}" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"

# 2. Get coin background
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?id={CMC_ID}" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"

# 3. Get latest quote
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={CMC_ID}&convert=USD" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"

# 4. Get technicals (RSI, MA, MACD) — risk overlay
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/technical_analysis?id={CMC_ID}" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"

# 5. Get latest news — catalyst check
curl -s "https://pro-api.coinmarketcap.com/v1/cryptocurrency/news/latest?id={CMC_ID}" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"
```

**Filters that should make the agent pause:**

- RSI > 80 on the underlying → overbought; PT mark-to-market may already be inflated
- 24h drop > 15% → safety filter rejects
- Negative news in last 24h with "hack", "exploit", "depeg", "rugpull" → reject
- Mcap < $10M → underlying is too illiquid; PT redemption could fail

### Step 4: Pull global market context (regime filter)

```bash
curl -s "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"
```

Use the `btc_dominance`, `total_volume_24h`, and `defi_volume_24h` to set a regime tag:

- BTC dominance > 60% → "risk-off" → prefer higher yields (>12%) to compensate
- BTC dominance < 50% → "risk-on" → can accept lower yields (8%+)
- Defi volume 24h drop > 30% week-over-week → "stress" → shrink position size, raise yield floor to 12%

### Step 5: Pull upcoming macro events (catalyst filter)

```bash
curl -s "https://pro-api.coinmarketcap.com/v1/global-macro/events/upcoming" \
  -H "X-CMC_PRO_API_KEY: ${CMC_API_KEY}"
```

If a major event is within 7 days of the PT expiry (Fed FOMC, regulatory deadline, major unlock), prefer a different market with a longer buffer.

### Step 6: Generate the spec

Pick the top surviving market (highest `impliedApy` after all filters). Construct the JSON spec (example above). Add:

- `position_size_usd` — based on the agent's risk profile (default 1-5% of capital per position)
- `entry_window_days` — how long the agent has to fill the position (default 3)
- `exit_window_days` — how long before maturity to close the position if rolling (default 7)
- `data_as_of` — ISO timestamp of when the spec was generated
- `agent_id` — who generated the spec

### Step 7: Output the spec

Hand the JSON to:
- A backtester (e.g. the script in `backtest/run_backtest.py` in this repo)
- An allocation engine (`lp-strategy-menu` wrapper in this library)
- A Trust Wallet Agent Kit (TWAK) execution layer for live trading

## Backtest

This repo ships a backtest script: `backtest/run_backtest.py`. It pulls the historical data from
`/v3/56/markets/{address}/historical-data?timeframe=1d` and replays a buy-and-hold PT strategy
over the available window. Outputs: PnL curve, Sharpe ratio, max drawdown, redemption-at-maturity
payoff. See `backtest/README.md` for usage.

For sUSDat, the backtest has **722 hourly observations** spanning 2026-05-22 → 2026-06-21
(implied APY stable around 13-15%). Expected output: ~14.98% return over 67 days, ~zero variance
on the deterministic-redeem-at-maturity payoff. The interesting risk story is mark-to-market
drawdown if the underlying yield collapses mid-tenor.

## Error handling

- **Pendle API rate limit (429):** wait `Retry-After` seconds, retry. If still 429, fall back to CMC's `get_global_metrics_latest` for an aggregate risk regime signal and recommend the user wait 10 minutes before re-pulling Pendle.
- **CMC API key missing:** recommend the user set `CMC_API_KEY` env var. The spec is unusable without it.
- **No PT markets pass the safety filter:** output an empty result with a reason: "No PT markets on BSC currently meet the risk guardrails (min liquidity $500K, min time-to-maturity 14d, yield floor 8%). Consider expanding the chain scope to Ethereum or Base where deeper markets exist."
- **Underlying token not in CMC:** still allow the spec with a warning — some Pendle markets have very new underlyings that aren't on CMC yet.

## Demo (x402 agentic-commerce proof)

This skill can also be demonstrated via the **x402 pay-per-request MCP** at `https://mcp.coinmarketcap.com/x402/mcp`.
The agent pays $0.01 USDC per request on Base (chain 8453) for any CMC data call. This is the
agentic-commerce angle the judges will care about for the BNB Hack submission.

Demo flow:

1. User asks: "Find the best fixed-yield PT on BSC for $10K."
2. Agent calls `https://mcp.coinmarketcap.com/x402/mcp` with a BTC quote to check market regime.
3. MCP returns 402 Payment Required with payment instructions.
4. Agent's wallet (Base, USDC) signs the $0.01 payment.
5. MCP returns the data.
6. Agent calls Pendle API directly (no auth).
7. Agent reasons across the 6 active PT markets.
8. Agent outputs the sUSDat PT spec.
9. Agent's response includes the tx hash of the x402 payment as proof of the agentic-commerce flow.

## References

- `references/pendle-api.md` — Pendle API endpoint reference
- `references/cmc-mcp.md` — CoinMarketCap MCP tool reference
- `references/x402-integration.md` — x402 pay-per-request flow
- `examples/susdat-pt-spec.json` — example output spec
- `backtest/run_backtest.py` — backtest script
- `backtest/README.md` — backtest usage
