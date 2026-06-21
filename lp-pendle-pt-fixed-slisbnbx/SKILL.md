---
name: lp-pendle-pt-fixed-slisbnbx
description: |
  Low-yield, high-liquidity PT position on the slisBNBx market. Implied APY ~3.4% with $3.86M
  liquidity. Use only when the user explicitly asks for the most-liquid PT on BSC and accepts
  the short tenor (matures 2026-06-25, ~4 days at time of writing). Not recommended as a
  primary position — included for completeness of the BSC PT universe.

  Trigger: "most liquid PT", "slisBNBx position", "ultra-safe fixed yield",
  "/lp-pendle-pt-fixed-slisbnbx"

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_info
  - mcp__cmc-mcp__get_global_metrics_latest
---

# lp-pendle-pt-fixed-slisbnbx

Low-yield, high-liquidity variant. **Not recommended as flagship** — included only for completeness.

## When to use

- User explicitly wants the most-liquid PT on BSC and understands the trade-off (3.38% APY for 4 days).
- As a parking position for capital that needs to be deployed in <7 days.

## Spec (live, 2026-06-21)

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1-slisbnbx",
  "venue": "pendle",
  "chain": "bsc",
  "chain_id": 56,
  "instrument": "PT-slisBNBx-2026-06-25",
  "underlying_token": "slisBNBx",
  "pt_address": "0xe052823b4aefc6e230faf46231a57d0905e30ae0",
  "market_address": "0x3c1a3d6b69a866444fe506f7d38a00a1c2d859c5",
  "expiry": "2026-06-25T00:00:00Z",
  "time_to_maturity_days": 4,
  "expected_fixed_apy": 0.0338,
  "liquidity_usd": 3855232,
  "il_profile": "zero"
}
```

## Why this is not the flagship

- 4 days to maturity is too short for a meaningful backtest.
- 3.38% APY is below the yield floor of 8% used in the flagship's safety filter.
- Only useful as a parking position for very short-term capital.

## Workflow

Same structure as the flagship, but with slisBNBx as the fixed target. Most users should pick
sUSDat or USDat instead.
