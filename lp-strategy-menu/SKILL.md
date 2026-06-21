---
name: lp-strategy-menu
description: |
  Allocates a capital pool across the Pendle PT fixed-yield library on BSC.
  Combines lp-pendle-pt-fixed (sUSDat, 14.98% APY) and lp-pendle-pt-fixed-usdat
  (USDat, 8.35% APY) into a single portfolio spec that respects a user-defined
  risk profile (conservative / balanced / aggressive) and a market regime overlay
  (risk-on / risk-off / stress).

  Use when a user asks: "Allocate $X across fixed-yield PT on BSC.",
  "Build me a balanced DeFi portfolio on BSC.", "What's the best split between
  sUSDat and USDat for a 5% target yield with low risk?", "/lp-strategy-menu".

license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_crypto_quotes_latest
---

# lp-strategy-menu

A wrapper that allocates a capital pool across the Pendle PT fixed-yield library.
Pulls live APYs and liquidity from Pendle, computes portfolio-level stats, and outputs
a single allocation spec.

## When to use

- "Allocate $50K across the safest fixed-yield PT strategies on BSC."
- "Build me a balanced BSC DeFi portfolio."
- "Show me the menu of PT strategies with risk-adjusted returns."

## Quick start

```bash
# Balanced profile (default), $50K capital
python3 run_menu.py --capital 50000 --profile balanced

# Conservative, $25K
python3 run_menu.py --capital 25000 --profile conservative

# Aggressive with risk-off regime overlay
python3 run_menu.py --capital 100000 --profile aggressive --regime risk-off

# Raw JSON output (for piping into other tools)
python3 run_menu.py --capital 50000 --profile balanced --json > portfolio.json
```

## What it produces

A JSON portfolio spec. Example (balanced, $50K, neutral regime, live 2026-06-21):

```json
{
  "portfolio_id": "lp-strategy-menu-20260621-110000",
  "skill": "lp-strategy-menu",
  "version": "1.0",
  "total_capital_usd": 50000.0,
  "risk_profile": "balanced",
  "regime": "neutral",
  "allocations": [
    {
      "skill": "lp-pendle-pt-fixed-susdat",
      "instrument": "PT-sUSDat-2026-08-27",
      "pct_of_capital": 0.6,
      "capital_usd": 30000.0,
      "implied_apy_live": 0.1498,
      "time_to_maturity_days": 67,
      "il_profile": "zero"
    },
    {
      "skill": "lp-pendle-pt-fixed-usdat",
      "instrument": "PT-USDat-2026-08-27",
      "pct_of_capital": 0.4,
      "capital_usd": 20000.0,
      "implied_apy_live": 0.0835,
      "time_to_maturity_days": 67,
      "il_profile": "zero"
    }
  ],
  "portfolio_expected_apy": 0.1233,
  "portfolio_expected_profit_usd": 1130.41,
  "portfolio_avg_maturity_days": 67.0,
  "portfolio_max_drawdown_estimate": 0.022
}
```

## Risk profile templates

| Profile | sUSDat weight | USDat weight | Portfolio APY | Max DD estimate |
|---|---|---|---|---|
| Conservative | 50% | 50% | 11.67% | -1.5% |
| Balanced (default) | 60% | 40% | **12.33%** | -2.2% |
| Aggressive | 80% | 20% | 13.65% | -3.8% |

## Regime overlay

| Regime | Trigger | Action |
|---|---|---|
| neutral | (default) | Apply profile weights as-is |
| risk-on | BTC dominance < 50% | Apply profile weights as-is |
| risk-off | BTC dominance > 60% | Shift 10% from sUSDat → USDat |
| stress | Defi 24h volume drop > 30% WoW | Force 80% USDat / 20% sUSDat |

## Workflow

1. **Pull live PT markets** from Pendle (`/v1/56/markets/active`).
2. **Pull regime tag** from CMC global metrics (`get_global_metrics_latest`).
3. **Apply risk profile** weights to the two PT strategies.
4. **Apply regime overlay** to adjust weights.
5. **Compute portfolio APY** as weighted average of live implied APYs.
6. **Stability check** — pull historical data for the dominant market, compute stdev/min/max.
7. **Output the spec** as JSON.

## What the agent does NOT do

- Execute the allocation (this is a spec, not a TWAK integration).
- Rebalance dynamically (the spec is generated on-demand, not continuously).
- Cross-chain rebalancing (BSC only).
- Auto-detect user risk profile (the user must pick conservative/balanced/aggressive).

## Files

- `SKILL.md` — this file
- `README.md` — quick reference
- `run_menu.py` — the implementation
- `examples/` — sample output specs
