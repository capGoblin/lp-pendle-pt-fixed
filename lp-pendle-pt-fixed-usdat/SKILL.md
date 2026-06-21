---
name: lp-pendle-pt-fixed-usdat
description: |
  Conservative variant of lp-pendle-pt-fixed, targeting the USDat PT market on BSC.
  Lower yield (8.35%) but longer-tenor and lower mark-to-market volatility than sUSDat.
  Use when a user prefers a more boring, lower-risk PT position or wants to diversify away
  from sUSDat concentration.

  Trigger: "conservative PT", "USDat position", "diversify away from sUSDat",
  "lower-volatility fixed yield", "/lp-pendle-pt-fixed-usdat"

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_info
  - mcp__cmc-mcp__get_crypto_technical_analysis
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_global_metrics_latest
---

# lp-pendle-pt-fixed-usdat

Conservative sister of `lp-pendle-pt-fixed`. Targets the USDat PT market on BSC.

## When to use

- User wants a lower-risk PT position than sUSDat.
- User wants to diversify the PT book across two underlyings.
- The risk overlay suggests sUSDat is overbought (RSI > 80) but USDat is not.

## Spec (live, 2026-06-21)

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1-usdat",
  "venue": "pendle",
  "chain": "bsc",
  "chain_id": 56,
  "instrument": "PT-USDat-2026-08-27",
  "underlying_token": "USDat",
  "pt_address": "0x3519f72144daae5ae933fac1bf91f8da57664d24",
  "yt_address": "0xb977399b1e25d5885831af34769ff47f94d391a6",
  "sy_address": "0x81a77db87618d51bc12c9eabe08cc298764b8277",
  "market_address": "0x9757834d0b31aa820b85f68705117691207152d9",
  "expiry": "2026-08-27T00:00:00Z",
  "time_to_maturity_days": 67,
  "expected_fixed_apy": 0.0835,
  "liquidity_usd": 2776399,
  "il_profile": "zero",
  "rebalance_rule": "buy-and-hold to maturity"
}
```

## Risk profile vs flagship

| | sUSDat (flagship) | USDat (conservative) |
|---|---|---|
| Implied APY | 14.98% | 8.35% |
| Liquidity | $2.96M | $2.78M |
| Time to maturity | 67d | 67d |
| Underlying risk | medium (RWA yield-bearing) | low (USD-pegged) |
| Mark-to-market vol | medium | low |
| Best for | aggressive yield | conservative / diversification |

## Workflow

Same as `lp-pendle-pt-fixed` but with USDat as the fixed target. Reuse the same risk filters
and CMC integration. The CMC ID for USDat is whatever the agent resolves via `search_cryptos`.
