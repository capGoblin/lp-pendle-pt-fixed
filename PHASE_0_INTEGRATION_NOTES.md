# PHASE_0_INTEGRATION_NOTES.md — Operator Summary

**Phase:** 0 (verification, no code)
**Date:** 2026-06-21 10:00–10:15 UTC
**Operator:** capGoblin
**Author:** Sambar
**Companion files:**
- `PHASE_0_CMC_VERIFICATION.md` — 7 endpoint checks, all citations
- `PHASE_0_PENDLE_VERIFICATION.md` — 6 BSC PT markets, contracts, APYs, backtest path

---

## What the operator needs to know in 60 seconds

1. **The flagship is not sUSDe. It's sUSDat.** The deep-dive spec assumed sUSDe (Ethena's staked USDe) was the lead PT market. **sUSDe isn't on BSC, period.** The lead market by implied APY is **sUSDat at 14.98%** with $2.96M liquidity and a 67-day maturity. **Use sUSDat.**

2. **One of the 7 CMC endpoints in the spec is fake.** `mcp__cmc-mcp__get_crypto_security_detail` doesn't exist in the official openCMC cmc-mcp skill. **Replace it with `get_crypto_info` + `search_crypto_info`** in the SKILL.md.

3. **The plan tier is 15,000 calls/month, not 330.** 45× more headroom than the deep-dive said. No backtest budget concern.

4. **The backtest data path works.** `/v3/56/markets/{address}/historical-data?timeframe=1d` returns 722 hourly observations for sUSDat, with stable implied APY around 13-15%. Clean backtest story.

5. **x402 is real and usable for the demo.** `https://mcp.coinmarketcap.com/x402/mcp` is the MCP variant, $0.01 USDC per request on Base, no API key. This is the agentic-commerce proof the judges will care about.

6. **The 149-token allowlist is unverified.** Dorahacks page is gated by AWS WAF ("Human Verification"). I could not get the allowlist. **For Track 2 (Strategy Skills), this is not a hard blocker** — the spec just needs to be backtestable, not live-tradeable. The allowlist is a Track 1 (Autonomous Trading Agents) constraint.

---

## What to change in the build

### In `lp-pendle-pt-fixed/SKILL.md`

| Old (in deep-dive) | New (verified) | Reason |
|---|---|---|
| `mcp__cmc-mcp__get_crypto_security_detail` | `mcp__cmc-mcp__get_crypto_info` + `mcp__cmc-mcp__search_crypto_info` | The old tool doesn't exist |
| `expected_fixed_apy: 0.142` (sUSDe assumed) | `expected_fixed_apy: 0.1498` (sUSDat) | sUSDe isn't on BSC; sUSDat is |
| `pt_market_address: <sUSDe BSC>` | `pt_market_address: 0x23f9a497a5d4d54eaf5e03d94774f17dc1219745` (sUSDat PT) | Real on-chain contract |
| `underlying_token: sUSDe` | `underlying_token: sUSDat` (Resolv USR yield-bearing) | Live market data |
| `backtest_window: 90d` | `backtest_window: 30d` (max available) | sUSDat launched 2026-05-22 |
| (not in spec) | Add `mcp__cmc-mcp__get_crypto_technical_analysis` | RSI filter on underlying before entry |
| (not in spec) | Add `mcp__cmc-mcp__get_upcoming_macro_events` | Avoid entering right before macro catalysts |
| `derivatives: CMC global derivatives metrics` | (drop) | No per-market funding via public REST; only aggregate volume |

### In the strategy spec

**Replace the sUSDe-PT JSON spec with sUSDat-PT:**

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
  "expected_fixed_apy": 0.1498,
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
    "cost_per_call": 0.01,
    "currency": "USDC",
    "network": "base"
  },
  "il_profile": "zero",
  "best_case_apy": 0.19,
  "worst_case_apy": 0.08,
  "yield_floor": 0.08,
  "rebalance_rule": "buy-and-hold to maturity; do not roll early unless implied_apy > 0.20 across all open PTs in the market"
}
```

### In the thin library (4 skills instead of 8)

The deep-dive proposed 8 LP-farming skills. After verification, the realistic deliverable is **4 skills that match the live Pendle BSC universe + 1 wrapper**:

1. `lp-pendle-pt-fixed-susdat` — flagship, sUSDat, 14.98% APY
2. `lp-pendle-pt-fixed-usdat` — conservative sister, USDat, 8.35% APY
3. `lp-pendle-pt-fixed-slisbnbx` — footnote skill for the 4-day-to-expiry slisBNBx market (low priority, can be a stub)
4. `lp-concentrated-stable` — PancakeSwap v3 stable pair skill, complement to fixed-yield
5. `lp-strategy-menu` — wrapper that allocates across the library based on risk profile

The other 4 (delta-neutral, YT speculation, Boros, Beefy auto-compound) get cut because they don't have a clean live data path in the time budget. The library-of-4 is more credible than a library-of-8 where half the specs are speculative.

### In the demo script

**30 seconds on the live x402 call.** Show the agent:
1. Receiving a prompt: "Find the best fixed-yield PT position on BSC for $10K capital."
2. Calling `https://mcp.coinmarketcap.com/x402/mcp` with the request.
3. The MCP responds with a 402 Payment Required.
4. The agent's wallet signs the USDC payment on Base ($0.01).
5. The MCP returns the data.
6. The agent reasons across the 6 active PT markets and picks sUSDat.
7. The agent outputs the spec (the JSON above).

That's the agentic-commerce proof. **The x402 MCP endpoint is the demo differentiator.** It uses the cmc-x402 SKILL.md from the official openCMC repo.

---

## What I am NOT confident about

1. **The 149-token allowlist.** Could not retrieve from Dorahacks (WAF-gated). The hackathon page text says "a fixed list of BEP-20 tokens listed on CoinMarketCap (149 tokens)" but I don't have the actual list. For Track 2, this is not a hard constraint — Track 2 just needs a backtestable spec.

2. **Whether the spec will be judged "complete" without a Dorahacks live submission.** The deadline is **2026-06-21 12:00 UTC** (about 2 hours from now at time of writing). The submission requires a registered Dorahacks project + a GitHub repo + a writeup. I can scaffold the repo and writeup, but the Dorahacks registration and final submission has to come from you (I don't have your account).

3. **The deep-dive's "track 1 strategies in disguise" concern.** The deep-dive worried that the track 2 entry would actually be a track 1 strategy. After this verification, I'm confident the **sUSDat PT-fixed strategy is a clean track 2 spec**: it's a backtestable strategy recommendation, not a live execution. But the spec needs to be careful to NOT include TWAK execution logic — track 2 is "pre-computed indicators + Skills Marketplace + x402 (optional)."

---

## Time budget

| Phase | Wall-clock | Status |
|---|---|---|
| Phase 0 verification | ~15m | ✅ done (this file + the two companion files) |
| Phase 1 repo scaffold + flagship SKILL.md | 1-2h | not started |
| Phase 2 flagship backtest | 2-3h | not started |
| Phase 3 wrapper + thin sister | 1-2h | not started |
| Phase 4 demo + Dorahacks submission | 1-2h | not started |
| **Total remaining** | **5-9h** | before 12:00 UTC submission lock |

**It's tight.** The 4-skill thin library is the right scope. The flagship sUSDat SKILL.md + a single backtest + the x402 demo is the minimum viable submission. If the timeline slips, the wrapper and thin sisters can ship as a "v1.1" update post-submission.

---

## What's next — do you want me to start phase 1?

The next move is:
1. Scaffold the repo at `/root/.openclaw/workspace/research/bnb-hack-ai-trading-agent/lp-pendle-pt-fixed/`
2. Write the flagship SKILL.md using the verified sUSDat spec above
3. Write the 4-skill thin-library spec stubs
4. Write the Dorahacks submission text

All of this is in this channel, public, on disk. I can start now. **Say "go" or "phase 1" and I'll fire.**

If you want to override anything — different flagship, different thin library composition, different demo angle — say so before I start. Once I scaffold, edits are cheap but context switches cost time.
