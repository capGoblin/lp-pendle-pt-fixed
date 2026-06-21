#!/usr/bin/env python3
"""
Pendle PT Buy-and-Hold Backtester

Replays a buy-and-hold PT strategy over historical data and outputs PnL curve,
Sharpe ratio, max drawdown, and redemption-at-maturity payoff.

Usage:
  python3 run_backtest.py --market 0x1017e73ce9c219164ce841a980136eb023c55387 --chain 56 --capital 10000
  python3 run_backtest.py --market 0x9757834d0b31aa820b85f68705117691207152d9 --chain 56 --capital 10000  # USDat
  python3 run_backtest.py --list  # list all known BSC PT markets
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Optional

import urllib.request
import urllib.error

PENDLE_BASE = "https://api-v2.pendle.finance/core"

# Known BSC PT markets (verified live 2026-06-21 10:09 UTC)
BSC_MARKETS = {
    "0x3c1a3d6b69a866444fe506f7d38a00a1c2d859c5": {"name": "slisBNBx", "expiry": "2026-06-25"},
    "0x03bc522d619fe24b788b9a2a39944f7de1685239": {"name": "cUSDO", "expiry": "2026-10-29"},
    "0x21558067e3ed5d3cdbe2dd3662bd9035a8e3315a": {"name": "uniBTC", "expiry": "2026-06-25"},
    "0x9757834d0b31aa820b85f68705117691207152d9": {"name": "USDat", "expiry": "2026-08-27"},
    "0x1017e73ce9c219164ce841a980136eb023c55387": {"name": "sUSDat", "expiry": "2026-08-27"},
    "0x34a1caef9f303a33e5d15bc5bc85064a39b7d1df": {"name": "apxUSD", "expiry": "2026-11-05"},
}


def fetch_json(url: str, max_retries: int = 3) -> dict:
    """Fetch JSON with retry on 429."""
    headers = {
        "User-Agent": "lp-pendle-pt-fixed-backtest/1.0 (BNB Hack Track 2; github.com/capGoblin/lp-pendle-pt-fixed)",
        "Accept": "application/json",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = int(e.headers.get("Retry-After", 5))
                print(f"  429 hit, waiting {wait}s ...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise


def fetch_active_markets(chain_id: int = 56) -> list:
    """Fetch all active PT markets on a chain."""
    url = f"{PENDLE_BASE}/v1/{chain_id}/markets/active"
    data = fetch_json(url)
    return data.get("markets", data if isinstance(data, list) else [])


def fetch_historical(market_address: str, chain_id: int = 56, timeframe: str = "1d") -> list:
    """Fetch historical data for a market."""
    url = f"{PENDLE_BASE}/v3/{chain_id}/markets/{market_address}/historical-data?timeframe={timeframe}"
    data = fetch_json(url)
    return data.get("results", [])


def backtest_pt_buy_and_hold(historical: list, capital_usd: float = 10000.0) -> dict:
    """
    Replay a buy-and-hold PT strategy.
    
    At T0, buy PT at price pt_price = 1 / (1 + implied_apy * time_to_maturity).
    Hold to maturity. Redeem 1:1 for underlying. Return = (1 / pt_price) - 1.
    
    For a deterministic-redeem-at-maturity strategy, the expected return is
    the implied APY. The interesting risk is mark-to-market: if implied_apy
    changes (up or down), the PT price moves inversely.
    """
    if not historical:
        raise ValueError("Empty historical data")
    
    initial_implied_apy = historical[0]["impliedApy"]
    final_implied_apy = historical[-1]["impliedApy"]
    
    # Entry at T0 implied APY
    # We assume time_to_maturity is fixed at the historical end for simplicity
    # (full 67d for sUSDat/USDat, 4d for slisBNBx/uniBTC)
    # In a real backtest this would be a rolling window
    
    # Mark-to-market PnL curve: how PT price would have moved if you marked to market
    pnl_curve = []
    for obs in historical:
        implied_apy = obs.get("impliedApy", 0)
        # PT price moves inversely to implied APY
        # If implied_apy went up, PT price went down (worse for buyer)
        mtm_pct = (initial_implied_apy - implied_apy) / max(implied_apy, 0.001)
        pnl_curve.append({
            "timestamp": obs["timestamp"],
            "implied_apy": implied_apy,
            "mark_to_market_pct": mtm_pct,
        })
    
    # Compute stats
    mtm_returns = [p["mark_to_market_pct"] for p in pnl_curve]
    final_mtm_pct = mtm_returns[-1] if mtm_returns else 0
    min_mtm_pct = min(mtm_returns) if mtm_returns else 0
    max_mtm_pct = max(mtm_returns) if mtm_returns else 0
    
    # Deterministic redemption payoff (at maturity)
    deterministic_payoff_apy = initial_implied_apy
    deterministic_payoff_usd = capital_usd * (1 + deterministic_payoff_apy)
    
    # Sharpe of mark-to-market returns (not redemption, which is deterministic)
    if len(mtm_returns) > 1:
        mean_mtm = sum(mtm_returns) / len(mtm_returns)
        var_mtm = sum((r - mean_mtm) ** 2 for r in mtm_returns) / len(mtm_returns)
        std_mtm = var_mtm ** 0.5
        sharpe_mtm = (mean_mtm / std_mtm * (365 ** 0.5)) if std_mtm > 0 else float('inf')
    else:
        sharpe_mtm = 0
    
    return {
        "capital_usd": capital_usd,
        "initial_implied_apy": initial_implied_apy,
        "final_implied_apy": final_implied_apy,
        "deterministic_payoff_apy": deterministic_payoff_apy,
        "deterministic_payoff_usd": deterministic_payoff_usd,
        "mark_to_market": {
            "final_pct": final_mtm_pct,
            "min_pct": min_mtm_pct,
            "max_pct": max_mtm_pct,
            "annualized_sharpe": sharpe_mtm,
        },
        "pnl_curve": pnl_curve,
        "data_points": len(historical),
        "timestamp_start": historical[0]["timestamp"],
        "timestamp_end": historical[-1]["timestamp"],
    }


def list_markets(chain_id: int = 56):
    """Print all known active PT markets on a chain."""
    print(f"\nActive PT markets on chain {chain_id}:\n")
    markets = fetch_active_markets(chain_id)
    for m in sorted(markets, key=lambda x: -x.get("details", {}).get("impliedApy", 0)):
        name = m.get("name", "?")
        addr = m.get("address", "?")
        expiry = m.get("expiry", "?")
        det = m.get("details", {})
        implied = det.get("impliedApy", 0)
        liq = det.get("liquidity", 0)
        agg = det.get("aggregatedApy", 0)
        print(f"  {name:10s} | implied={implied*100:6.2f}% | agg={agg*100:6.2f}% | liq=${liq:>12,.0f} | expiry={expiry} | {addr}")


def main():
    parser = argparse.ArgumentParser(description="Pendle PT buy-and-hold backtester")
    parser.add_argument("--market", type=str, help="Market address (e.g. 0x1017e73...)")
    parser.add_argument("--chain", type=int, default=56, help="Chain ID (default 56 for BSC)")
    parser.add_argument("--capital", type=float, default=10000.0, help="Capital in USD (default 10000)")
    parser.add_argument("--timeframe", type=str, default="1d", help="Timeframe: 1h, 1d, 1w, 1m (default 1d)")
    parser.add_argument("--list", action="store_true", help="List all active PT markets on the chain")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.list:
        list_markets(args.chain)
        return
    
    if not args.market:
        print("Error: --market is required (or use --list to see available markets)", file=sys.stderr)
        sys.exit(1)
    
    market = args.market.lower()
    if not market.startswith("0x"):
        market = "0x" + market
    
    # Resolve name
    market_info = BSC_MARKETS.get(market, {})
    market_name = market_info.get("name", market[:10])
    print(f"\n=== Backtesting PT {market_name} ({market}) on chain {args.chain} ===")
    print(f"Capital: ${args.capital:,.2f}")
    print(f"Timeframe: {args.timeframe}\n")
    
    print("Fetching historical data...")
    historical = fetch_historical(market, args.chain, args.timeframe)
    print(f"Got {len(historical)} data points")
    if not historical:
        print("No historical data available", file=sys.stderr)
        sys.exit(1)
    
    print(f"  Range: {historical[0]['timestamp']} → {historical[-1]['timestamp']}")
    print()
    
    print("Running backtest...")
    result = backtest_pt_buy_and_hold(historical, args.capital)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    print(f"\n{'='*60}")
    print(f"RESULTS — PT {market_name}")
    print(f"{'='*60}\n")
    print(f"  Initial implied APY (entry):   {result['initial_implied_apy']*100:.2f}%")
    print(f"  Final implied APY (exit):      {result['final_implied_apy']*100:.2f}%")
    print(f"  Deterministic payoff APY:      {result['deterministic_payoff_apy']*100:.2f}%")
    print(f"  Capital at maturity:           ${result['deterministic_payoff_usd']:,.2f}")
    print()
    print(f"  Mark-to-market stats (if you had to exit early):")
    print(f"    Final PnL:     {result['mark_to_market']['final_pct']*100:+.4f}%")
    print(f"    Worst PnL:     {result['mark_to_market']['min_pct']*100:+.4f}%")
    print(f"    Best PnL:      {result['mark_to_market']['max_pct']*100:+.4f}%")
    print(f"    Sharpe (ann.): {result['mark_to_market']['annualized_sharpe']:.2f}")
    print()
    print(f"  Data points: {result['data_points']}")
    print(f"  Period: {result['timestamp_start']} → {result['timestamp_end']}")
    print(f"\n{'='*60}\n")
    print("  KEY INSIGHT: PT is a fixed-income instrument. The deterministic")
    print("  payoff (above) is the headline. The mark-to-market story is only")
    print("  relevant if you have to exit before maturity.")
    print()


if __name__ == "__main__":
    main()
