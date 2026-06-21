---
name: lp-strategy-menu
description: |
  Allocates a capital pool across a library of fixed-yield and LP-farming strategies on BSC.
  Wraps the lp-pendle-pt-fixed-* skills and lp-concentrated-stable into a single allocation
  decision that respects a user-defined risk profile (conservative / balanced / aggressive).

  Use when a user asks: "Where should I put $X on BSC for fixed yield?",
  "Allocate my BSC capital across the safest yield strategies.",
  "Build me a balanced DeFi portfolio on BSC.", "/lp-strategy-menu".

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_info
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_upcoming_macro_events
---

# lp-strategy-menu

A wrapper skill that allocates a capital pool across the LP-farming library on BSC.
Reads the current state of the underlying skills (lp-pendle-pt-fixed, lp-pendle-pt-fixed-usdat,
lp-concentrated-stable) and produces a single allocation spec that respects the user's
risk profile.

## When to use this skill

- "Allocate $50K across the safest yield strategies on BSC."
- "Build a balanced DeFi portfolio for me on BSC."
- "Show me the menu of BSC LP-farming strategies with risk-adjusted returns."

## What the skill produces

A JSON allocation spec:

```json
{
  "portfolio_id": "lp-strategy-menu-2026-06-21",
  "total_capital_usd": 50000,
  "risk_profile": "balanced",
  "regime": "risk-on",
  "allocations": [
    {
      "skill": "lp-pendle-pt-fixed-susdat",
      "strategy_id": "lp-pendle-pt-fixed-v1",
      "pct_of_capital": 0.40,
      "capital_usd": 20000,
      "expected_apy": 0.1498,
      "expected_horizon_days": 67
    },
    {
      "skill": "lp-pendle-pt-fixed-usdat",
      "strategy_id": "lp-pendle-pt-fixed-v1-usdat",
      "pct_of_capital": 0.30,
      "capital_usd": 15000,
      "expected_apy": 0.0835,
      "expected_horizon_days": 67
    },
    {
      "skill": "lp-concentrated-stable",
      "strategy_id": "lp-concentrated-stable-v1",
      "pct_of_capital": 0.30,
      "capital_usd": 15000,
      "expected_apy": 0.0412,
      "expected_horizon_days": 30
    }
  ],
  "portfolio_expected_apy": 0.0941,
  "portfolio_max_drawdown_estimate": 0.025,
  "generated_at": "2026-06-21T10:00:00Z"
}
```

## Risk profile templates

### Conservative (capital preservation priority)

| Allocation | Skill | Target weight |
|---|---|---|
| 50% | `lp-pendle-pt-fixed-susdat` | 0.50 |
| 30% | `lp-pendle-pt-fixed-usdat` | 0.30 |
| 20% | `lp-concentrated-stable` (USDC/USDT) | 0.20 |
| **Portfolio APY** | | ~10.2% |
| **Max DD estimate** | | -1.5% |

### Balanced (default)

| Allocation | Skill | Target weight |
|---|---|---|
| 40% | `lp-pendle-pt-fixed-susdat` | 0.40 |
| 30% | `lp-pendle-pt-fixed-usdat` | 0.30 |
| 30% | `lp-concentrated-stable` | 0.30 |
| **Portfolio APY** | | ~9.4% |
| **Max DD estimate** | | -2.5% |

### Aggressive (yield maximization)

| Allocation | Skill | Target weight |
|---|---|---|
| 70% | `lp-pendle-pt-fixed-susdat` | 0.70 |
| 30% | `lp-pendle-pt-fixed-usdat` | 0.30 |
| **Portfolio APY** | | ~13.0% |
| **Max DD estimate** | | -4.0% |

## Regime overlay

If the global metrics show "risk-off" (BTC dominance > 60%), shift 10% of capital from the highest-yield
strategy to the most stable. If "stress" (defi volume 24h drop > 30% week-over-week), raise yield
floor to 12% across all PT strategies.

## Workflow

1. Call each underlying skill (`lp-pendle-pt-fixed`, etc.) to get the live spec candidates.
2. Apply the risk guardrails (min liquidity, min time-to-maturity, yield floor, etc.).
3. Pick the top candidate per skill.
4. Apply the risk profile template weights.
5. Apply the regime overlay if needed.
6. Output the portfolio allocation spec.

## What the agent does NOT do

- Execute the allocation (this is a spec, not a TWAK integration).
- Rebalance dynamically (the spec is generated on-demand, not continuously).
- Cross-chain rebalancing (BSC only — the other chains are out of scope for this wrapper).
