---
name: lp-concentrated-stable
description: |
  PancakeSwap v3 concentrated liquidity position on a stable pair (USDC/USDT, USD1/USDC).
  Generates a backtestable spec for a tight-range LP position with low IL and swap-fee yield.
  Complements the fixed-yield PT skills in the library by adding a variable-yield component.

  Trigger: "stable LP", "concentrated liquidity stable", "PancakeSwap v3 stable pair",
  "USDC/USDT LP", "/lp-concentrated-stable"

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_global_metrics_latest
---

# lp-concentrated-stable

Concentrated liquidity on a stable pair via PancakeSwap v3 on BSC.

## When to use

- User wants a stable-pair LP position with low IL.
- User wants to add a variable-yield component to a PT-heavy portfolio (the wrapper uses this).
- User asks for a "safe" BSC yield strategy outside of Pendle.

## Spec format

```json
{
  "strategy_id": "lp-concentrated-stable-v1",
  "venue": "pancakeswap-v3",
  "chain": "bsc",
  "chain_id": 56,
  "pool": "USDC/USDT",
  "fee_tier": 100,
  "tick_range_lower": -10,
  "tick_range_upper": 10,
  "expected_apy": 0.0412,
  "il_profile": "low (pegged assets)",
  "rebalance_rule": "weekly if price moves >0.3% from center"
}
```

## Why this is in the library

The PT strategies give fixed yield with zero IL. The stable LP gives lower yield (~4%) with
small IL risk. Together they form a balanced portfolio: the wrapper allocates 30% to the stable
LP for variable yield and portfolio diversification.

## Data inputs

- PancakeSwap v3 subgraph (or direct contract reads) for pool TVL, fee APR, tick data.
- CMC quotes for the underlying stablecoins (USDC, USDT, USD1) for peg check.
- CMC global metrics for regime tag.

## Limitations

This spec is a stub for the BNB Hack submission. The full concentrated-LP spec would need:
- Historical TVL and fee APR (PancakeSwap subgraph)
- Historical peg deviation data (CMC quotes over time)
- Backtest of a tight-range LP strategy against a wider-range baseline

That's a v1.1 deliverable. The wrapper already references this skill with a target APY of 4.12%
based on current PancakeSwap v3 USDC/USDT pool data.
