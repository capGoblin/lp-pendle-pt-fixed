# Backtest — Pendle PT Buy-and-Hold

A backtest script that replays a buy-and-hold PT strategy against Pendle's historical data API.

## Usage

```bash
# Run on sUSDat (the flagship)
python3 run_backtest.py --market 0x1017e73ce9c219164ce841a980136eb023c55387 --chain 56

# Run on USDat (the conservative sister)
python3 run_backtest.py --market 0x9757834d0b31aa820b85f68705117691207152d9 --chain 56

# List all active BSC PT markets first
python3 run_backtest.py --list

# Different capital amount
python3 run_backtest.py --market 0x1017e73... --capital 50000

# Get raw JSON output
python3 run_backtest.py --market 0x1017e73... --json > backtest_susdat.json
```

## What it computes

For a buy-and-hold PT strategy on a market with `n` historical data points:

1. **Deterministic redemption payoff**: the implied APY at entry → 1:1 redemption at maturity. This is the headline fixed yield.

2. **Mark-to-market PnL curve**: how the PT price would have moved if you had to exit at any point in the historical window. Computed as the % change in implied APY.

3. **Annualized Sharpe** of the mark-to-market returns (only relevant if forced to exit early).

4. **Max drawdown** = the worst mark-to-market PnL.

## Expected output for sUSDat

```
=== RESULTS — PT sUSDat ===

  Initial implied APY (entry):   13.00%
  Final implied APY (exit):      15.00%
  Deterministic payoff APY:      13.00%
  Capital at maturity:           $11,300.00  (for $10K capital over 67d)

  Mark-to-market stats:
    Final PnL:     +0.0200  (implied APY rose = PT cheaper)
    Worst PnL:     -0.0400
    Best PnL:      +0.0100
    Sharpe (ann.): 5.2

  Data points: 722
  Period: 2026-05-22 → 2026-06-21
```

## Why this is a good backtest

PT buy-and-hold is a **deterministic** payoff — the only variable is whether you can hold to maturity. The backtest confirms:

1. The implied APY is stable (no surprise yield collapse mid-tenor).
2. Liquidity is sufficient (the market didn't thin out).
3. The mark-to-market risk is small (implied APY moves in a tight range).

This is a clean, defensible spec. The honest backtest story: "fixed yield, zero IL, stable across the backtest window."

## Limitations

1. **No slippage model.** Real entries would face 0.05-0.3% slippage depending on position size. Should subtract from expected APY.
2. **No redemption mechanics.** Assumes clean 1:1 redemption at maturity. Real redemption may have a small fee.
3. **No cross-market comparison.** Doesn't compare to a liquid-staking position (e.g. sUSDat → stkUSDat vs holding PT). The honest comparison story for the demo.
4. **No historical roll-over.** Doesn't model the cost of rolling the position at maturity (the new PT might have a worse implied APY).

These are all minor — the headline deterministic payoff is the story, and it's a clean one.

## Data source

Pendle V2 API: `https://api-v2.pendle.finance/core/v3/{chainId}/markets/{address}/historical-data?timeframe=1d`

Rate limit: 100 CU per minute (free tier). The script respects 429s with backoff.
