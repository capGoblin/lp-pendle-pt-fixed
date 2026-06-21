# TRACK 2: CMC × LP Farming Strategy Skills — Deep Dive

**Hackathon:** BNB Hack: AI Trading Agent Edition — CoinMarketCap × Trust Wallet × BNB Chain
**Track:** 2 — Strategy Skills (CMC Skill format, backtestable spec)
**Prize pool this track:** $6,000 ($3K / $2K / $1K)
**Submission lock:** 2026-06-21 12:00 UTC
**Generated:** 2026-06-20 13:05 UTC
**Author:** Sambar (subagent — Track 2 LP-farming deep research)
**Companion file:** `TRACK2_LP_FARMING_QUICKSTART.md` (operator 1-pager)

---

## 0. What this document is

This is a deep, technical, **LP-farming-specific** Track 2 research doc. The previous `BUILD_IDEAS.md` failed on this exact lane — it produced 4 Track 2 ideas that were all Track 1 trading strategies in disguise. This document does not do that. It treats Track 2 as a CMC Skill that takes market data and produces a **backtestable LP-farming strategy spec**. It maps the real BSC LP universe, decomposes LP strategy archetypes with the actual math, and writes 5-8 complete Skill specs that someone could literally drop into the `coinmarketcap-official/skills-for-ai-agents-by-CoinMarketCap` repo.

The author is explicit about a scope shift: the wedge for Track 2 in this hackathon is **not** "another momentum+RSI+MACD+Fear&Greed Skill." It is **LP-farming strategy generation as a primitive other agents consume**. LP farming is the lane where (a) the spec says "Quantopian-style strategy generation, adapted to crypto" most literally, (b) almost no Track 2 entrant will compete because the LP mechanics are harder to reason about, and (c) the backtest story is clean (real fees, real IL, real APY decomposition) — which judges love.

---

## 1. Executive Summary

### The strategic insight

Track 2 wants a backtestable **strategy spec**, not a live trader. The spec's own example ("a momentum Skill that blends RSI, MACD, and Fear & Greed into entry and exit rules") is the dead-end — that lane is going to be flooded with low-effort entries.

The lane that almost no one will touch — but where the demo, the originality, and the technical depth are all inherently higher — is **LP farming strategy generation**. The reason is structural:

1. **LP farming IS already a strategy generation problem.** You compose (i) a pool universe, (ii) a range/rebalance policy, (iii) a hedge overlay, (iv) a signal-driven trigger — and the output is a quant-style spec with measurable Sharpe. That's Quantopian-style by definition.
2. **CMC's data layer is uniquely suited to it.** The CMC DEX API (18 endpoints) gives you pool snapshots, OHLCV, token security, liquidity-change events, and gainers/losers — exactly the inputs a sophisticated LP strategy needs. CEX-only agents can't build these.
3. **The x402 path means no API-key tax.** Each CMC MCP call costs $0.01 USDC on Base — for a Track 2 Skill that *generates* specs, the data is cheap enough to wire as a backtest driver.
4. **BSC's LP universe is mature and varied.** PancakeSwap v3 (concentrated), Uniswap v3 on BSC, Thena Fusion (ve(3,3) on Algebra), Curve, Pendle (PT/YT/Boros on BSC), Beefy auto-compounders, Aave v3 supply. Multiple non-overlapping LP archetypes — enough to ship a *library* of 5-7 skills, not just one.
5. **The demo narrative is naturally strong.** "I take a market question, look up the pool, the token, the volatility regime, the funding market — and output a backtestable LP strategy with Sharpe, IL profile, and rebalance rules." That maps 1:1 to the four discretionary criteria (technical execution, originality, real-world relevance, demo).

### 5 wedge strategies that have real edge

These are the five LP-farming primitives that (a) ship as a backtestable spec, (b) are original in the context of Track 2, (c) have measurable edge, and (d) can be authored as a CMC Skill. Section 5 contains the full spec for each.

| # | Skill | Underlying primitive | Real edge | Edge from CMC data |
|---|---|---|---|---|
| 1 | `lp-concentrated-stable` | Concentrated stable LP on PancakeSwap v3 / Curve | Tight spread capture + low IL | Liquidity snapshots, pool age, 24h vol |
| 2 | `lp-vol-range-ema` | Volatile-pair concentrated LP with volatility-driven range | Range efficiency | Token technical analysis (ATR, realized vol) |
| 3 | `lp-pendle-pt-fixed` | Pendle PT buy-and-hold | Fixed yield, no IL | PT/YT price curves, sUSDe funding snapshots |
| 4 | `lp-delta-neutral` | Long LP + short perp carry | Funding harvest | Funding rates, OHLCV for hedge sizing |
| 5 | `lp-emissions-rotation` | Liquidity-mining rotation across PancakeSwap/Thena/Aerodrome | Capture > IL | DEX pool metrics, emissions tracker, sentiment |

Bonus wedge (6): `lp-pendle-boros` — Pendle's Boros market for funding-rate swap exposure. A pure fixed-income play on perp funding, fully on-chain, no IL.

### Submission shape: one polished Skill + a small library, or a library of 5+?

**Recommendation: ship ONE flagship Skill (`lp-pendle-pt-fixed` or `lp-delta-neutral`) PLUS a thin library of 3-4 others as a "Track 2 Strategy Library" wrapper.**

Rationale:
- The flagship carries the originality / technical-execution weight.
- The library signals "this is a primitive other agents consume" — it picks up the "Best Use of Agent Hub" special-prize vibe and positions the operator post-hackathon as a builder of Strategy-as-a-Service infra.
- A library of 5 thin Skills is a weaker demo than 1 deep Skill + 3 thin ones. Quality > quantity.
- The library wrapper itself can be a CMC Skill (MCP-exposed) that other Track 1 entries can subscribe to. This is the cross-track wedge.

Alternative if time-constrained: ship only the flagship Skill. A single, deeply-technical, fully-backtested LP strategy Skill beats a shallow library. The library is a power move, not a fallback.

---

## 2. Track 2 Mechanics & The CMC × LP Farming Intersection

### 2.1 What a CMC Skill actually is (the format)

A CMC Skill is a directory containing a `SKILL.md` file with YAML frontmatter. The structure is the standard agentskills.io / Claude Code skills spec:

```yaml
---
name: skill-name
description: |
  One-paragraph description of what the skill does.
  Trigger phrases that should activate it.
  Be specific — the LLM uses this to decide whether to load the skill.
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_global_metrics_latest
  - Read
  - Bash
---

# Skill Title

## What this skill does
...

## Inputs
...

## Logic
...

## Output
...

## Examples
...
```

**Key observations from the official catalog** (`github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap`):

- `cmc-mcp/SKILL.md` uses `allowed-tools: [mcp__cmc-mcp__*]` to whitelist the MCP tools the LLM can call. Skills are instruction sets, not standalone executables.
- `cmc-api-dex/SKILL.md` uses `allowed-tools: [Bash, Read]` — meaning the agent shells out to CMC REST via curl. The skill is *guide text*, the execution is whatever the host agent does.
- `cmc-x402/SKILL.md` references `@x402/axios @x402/evm viem` for pay-per-request. The skill describes the workflow; the integration is up to the agent.
- The `description` field is the **discovery surface**. The LLM scans the YAML frontmatter of every skill at session start and decides what to load. The description must include concrete trigger phrases.

**Implication for Track 2:** A CMC Skill is fundamentally an *instruction set* that an LLM agent loads. It defines inputs (CMC endpoints + on-chain reads), logic (the decision tree), and outputs (the strategy spec, formatted as JSON/YAML the agent can hand to a backtester). It is not a Python program. It is a prompt-engineering artifact with API references.

For LP-farming strategies, the Skill's output should be a **JSON strategy spec** like:

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1",
  "venue": "pendle",
  "chain": "bsc",
  "underlying": "sUSDe",
  "maturity": "2026-09-26",
  "action": "buy_pt_hold_to_maturity",
  "expected_fixed_apy": 0.142,
  "capital_required_usd": 1000,
  "il_profile": "zero",
  "rebalance_rules": "none_required",
  "exit_conditions": ["maturity", "yt_price_collapse_to_zero"],
  "risk_score": 0.18,
  "data_inputs": ["cmc.get_dex_pairs_quotes_latest", "cmc.get_global_metrics_latest"]
}
```

That spec is the artifact the backtester consumes. The Skill is the prompt that generates it.

### 2.2 Which CMC endpoints are useful for LP strategies

The CMC Agent Hub exposes 60+ endpoints across four API surfaces (`cmc-api-crypto`, `cmc-api-dex`, `cmc-api-exchange`, `cmc-api-market`). For LP strategy generation, the critical ones are:

| CMC endpoint | What it gives you | Used in |
|---|---|---|
| `/v4/dex/pairs/quotes/latest` | DEX pair price, 24h vol, liquidity, FDV | All LP strategies — pool snapshots |
| `/v1/dex/token/pools` | All pools for a token, with TVL, fee tier | Pool universe selection |
| `/v1/dex/token-liquidity/query` | Historical liquidity over time | Regime detection, de-pegging detection |
| `/v1/dex/security/detail` | Token security/rug score | Hard filter for "is this LP-able" |
| `/v1/dex/liquidity-change/list` | Tokens with significant LP changes | Emissions-rotation triggers |
| `/v1/dex/gainer-loser/list` | Top movers | Volatility-sorted pool selection |
| `/v1/dex/spot-pairs/latest` | All DEX pairs with platform/chain | DEX-pair discovery |
| `/v1/dex/platform/list` | Supported networks and DEXs | Network-scope filter |
| `get_crypto_ohlcv` (cmc-api-crypto) | OHLCV for the underlying token | Volatility calculation, ATR |
| `get_crypto_technical_analysis` | SMA/EMA/RSI/MACD/Fib | Vol-adjusted range, regime |
| `get_crypto_quotes_latest` | Spot price + market cap | Sanity check on chain data |
| `get_crypto_metrics` | Holder concentration | Risk overlay (whale %) |
| `get_global_metrics_latest` | Fear & Greed, dominance, total mcap | Macro regime |
| `get_global_crypto_derivatives_metrics` | Open interest, funding, liquidations | Funding-rate carry, delta-neutral |
| `get_crypto_latest_news` | Token-specific news | Catalyst check (avoid buy-the-dip-into-collapse) |
| `cmc-x402 pay-per-call` | $0.01 USDC on Base, no API key needed | Backtest driver (cheap data) |

The DEX endpoints are the wedge. CEX-only agents can build momentum strategies; DEX-native agents are the ones that can build LP strategies. That is the original wedge for Track 2.

### 2.3 The format a backtestable strategy spec should take

A spec that is genuinely *backtestable* must have:

1. **Venue + chain + contract addresses** — machine-readable, not prose.
2. **Action** — verb: `provide_liquidty`, `buy_pt`, `short_perp`, `deposit_aave`, `rotate_pool`.
3. **Entry rules** — boolean condition(s) on the inputs.
4. **Exit rules** — boolean conditions OR time-based (maturity).
5. **Sizing** — function of inputs (volatility-scaled, Kelly, fixed-fractional, etc.).
6. **Rebalance rules** — when and how to adjust range/position.
7. **Risk constraints** — hard gates (max drawdown, max position, allowlist).
8. **Data inputs (provenance)** — which CMC endpoints + on-chain reads, with link/refs.
9. **Expected metrics** — Sharpe, IL profile, breakeven holding period, max DD.
10. **Backtest signature** — time-window, gas assumption, slippage assumption.

The Skill should produce this spec as JSON or YAML, with the LLM filling in the values from the CMC data. The backtest is then deterministic: feed in historical data, replay the spec, get PnL curve.

This format is **Quantopian-style by definition**: the spec is a quant strategy that another agent or a human can plug into a backtester. The Skill is the LLM's role in the quant loop.

---

## 3. BSC LP Universe Map (June 2026)

This is the actual on-chain LP landscape the Skill will reason about. Numbers are TVL/APY snapshots from DeFiLlama, protocol dashboards, and third-party trackers as of June 2026. Where a number is from a single source and not cross-checked, it's flagged.

### 3.1 PancakeSwap (the dominant BSC DEX)

- **Total TVL:** ~$2.0B (DeFiLlama, June 7, 2026) — PancakeSwap AMM v2 + v3 combined. The $1.5B figure from PistachioFi (early 2026) has grown.
- **PancakeSwap v3 TVL:** ~$273M (pancakeswap.finance info, Jun 6, 2026) — concentrated liquidity.
- **PancakeSwap v3 24h volume:** ~$95.8M (pancakeswap.finance, Jun 6, 2026).
- **CAKE token incentives:** Active across v2 + v3 pools. CAKE emissions to LPs are a major component of APY.
- **Fee tiers:** 0.01%, 0.05%, 0.25%, 1% (the standard Uniswap v3 tier set).
- **Top pools by TVL (typical, June 2026):** BNB/USDT, ETH/USDC, CAKE/BNB, USDT/USDC, BTCB/USDT.
- **Pool depth:** BNB/USDT and ETH/USDC have tens of millions in pool depth even at 0.25% tier.

**Why this matters for the Skill:** PancakeSwap v3 is the largest concentrated-LP venue on BSC. The Skill needs to be able to enumerate pools, identify fee tier, and reason about liquidity per range. CMC's `/v1/dex/token/pools` and `/v4/dex/pairs/quotes/latest` give you that for free.

**Caveat / data validation:** Rebasing tokens are not supported by PancakeSwap v3 (per PancakeSwap developer docs, July 2025). The Skill should filter for non-rebasing tokens when recommending v3 ranges. This is a documented hard constraint.

### 3.2 Uniswap v3 on BSC

- **TVL on BSC:** $8.87M (DeFiLlama, June 7, 2026) — a fraction of PancakeSwap.
- **Reality check:** Uniswap v3 on BSC is a *brand-presence* deployment, not a liquidity hub. Most BSC LPs use PancakeSwap.
- **What it's good for:** Mid-cap pairs that PancakeSwap doesn't list. The Skill should still enumerate it but weight it lower in pool selection.

### 3.3 Thena (ve(3,3) on BSC)

- **Type:** ve(3,3) DEX with concentrated liquidity (Algebra-powered "Fusion" pools, launched May 2025).
- **Token:** THE — vote-escrow model with veTHE.
- **Value add:** vote-directed deep liquidity on specific pairs. Manual CL LPs (Concentrated Liquidity LPs) can provide within a custom range and receive an NFT representing the position.
- **Why it matters:** Thena is the BSC analogue of Aerodrome on Base. The Skill should know about it because the emissions structure (veTHE bribes) creates a different APY composition than PancakeSwap.
- **Caveat:** Specific TVL snapshot for Thena Fusion as of June 2026 not found in this research pass. DeFiLlama tracks THENA FUSION separately (defillama.com/protocol/thena-fusion). Operator should pull the live number before submitting.

### 3.4 Pendle on BSC

- **Type:** Yield tokenization (PT + YT) + Boros funding-rate market.
- **TVL (cross-chain, Q1 2026):** ~$1.5B per DeFiLlama; recent (March 2026) cross-chain figure: $3.5B per defiprime.com.
- **BSC-specific presence:** sUSDe and other BSC yield-bearing assets. PT/YT pairs exist for the supported SY (Standardized Yield, EIP-5115) tokens.
- **PT pricing example:** sUSDe 6-month PT at 0.94 sUSDe → ~12-15% fixed APY at June 2026 (varies with market pricing).
- **Boros (Pendle's funding-rate market):** Allows users to trade funding rate exposure using PT/YT framework. Tradeable funding rate yields via fully on-chain orderbook. Up to 1000x less capital than direct hedge. (Sources: pendle.finance/boros, blockworks.co Aug 2025, alearesearch.substack.com Aug 2025.)
- **Why it matters:** Pendle is the *most important* LP-farming primitive for Track 2 because it gives you **fixed yield with zero IL**. The Skill can recommend a PT buy-and-hold as a "fixed-income LP" spec — that is genuinely novel in the context of an LLM-Skill.
- **Caveat:** PT requires understanding of YT, SY, and the redemption mechanic. The Skill must include the PT math: PT price = SY / (1 + fixed_apy × time_to_maturity). The Skill should pull live PT/YT prices from Pendle's API or compute implied fixed yield from the discount.

### 3.5 Curve on BSC

- **Type:** StableSwap AMM (low-slippage stable-to-stable and BTC-correlated pools).
- **BSC TVL:** Modest vs Ethereum Curve. Curve on BSC exists but is not the primary BSC venue.
- **What it's good for:** Stable-to-stable pools (USDC/USDT, BUSD/USDC, USD1/USDC) with much lower IL than constant-product AMMs.
- **Caveat:** Curve on BSC has lower liquidity depth than PancakeSwap StableSwap. The Skill should prefer PancakeSwap StableSwap for most stable pairs on BSC.

### 3.6 Aave v3 on BSC (LP-adjacent)

- **Type:** Lending market. "Supply-only" is LP-adjacent in the sense that the supplied assets earn variable APY with no IL.
- **Why it matters:** Aave supply is a *baseline* LP-farming strategy: deposit USDC, earn supply APY + AAVE incentives. No IL, no range management. The Skill can use Aave as the risk-off floor of a strategy menu.
- **Caveat:** Aave supply APY on stablecoins is typically 2-6% (low). The Skill should recommend Aave only when risk-off conditions are met (extreme fear, low vol).

### 3.7 Beefy (auto-compounder)

- **Type:** Yield optimizer that auto-compounds LP rewards and re-deposits.
- **TVL (cross-chain, 2026):** Beefy operates across 11+ chains with significant TVL (specific BSC number not captured in this research pass — operator should pull from app.beefy.com before submitting).
- **What it does:** Wraps a PancakeSwap LP token or Aave aToken into a Beefy vault that auto-compounds. Saves gas (vs manual claim + reinvest) and can boost APY by 1-3 percentage points depending on compounding frequency.
- **Why it matters:** The Skill can recommend "deposit into Beefy vault X" as a single-action spec. This is the "give up some yield for convenience" lane.
- **Trade-off:** Beefy takes a 4.5% performance fee on the auto-compounded gains. The Skill should reflect that in net APY.

### 3.8 Aerodrome (Base — for cross-chain context)

- **Type:** ve(3,3) DEX on Base, concentrated liquidity.
- **Why it matters even though it's not BSC:** Aerodrome is the most successful ve(3,3) on a non-Ethereum chain. It processed $177B+ in 2025 volume. The Skill's *library* can include an Aerodrome variant as a sister strategy. But the Hackathon is BNB-focused — Aerodrome is bonus content, not core.
- **Caveat:** Aerodrome is on Base, not BSC. Including it dilutes the BNB focus. Recommend keeping it as an optional sister Skill.

### 3.9 Mapping summary

| DEX | Type | Primary use | Best Skill hook |
|---|---|---|---|
| PancakeSwap v3 | Concentrated LP | Volatile pairs (BNB/ETH, mid-caps) | `lp-vol-range-ema` |
| PancakeSwap StableSwap | Stable LP | Stables, low IL | `lp-concentrated-stable` |
| Thena Fusion | Concentrated + ve(3,3) | Vote-escrow bribed pools | `lp-emissions-rotation` |
| Pendle | PT/YT + Boros | Fixed yield, funding | `lp-pendle-pt-fixed`, `lp-pendle-boros` |
| Aave v3 | Lending | Risk-off supply | Risk overlay + base case |
| Beefy | Auto-compounder | Wrap any of the above | `lp-autocompound` |
| Curve (BSC) | StableSwap | Stable pairs (limited) | Sister to `lp-concentrated-stable` |
| Uniswap v3 (BSC) | Concentrated LP | Long-tail pairs | Optional / edge case |

---

## 4. LP Strategy Archetypes (deep, with math)

Each archetype includes: mechanism, APY decomposition, IL profile, when it works, when it dies, the CMC data inputs, and the backtestable spec format.

### 4.1 Stable-Stable Concentrated Liquidity (USDC/USDT, USD1/USDC)

**Mechanism.** Deposit into a tight range around 1.0 (e.g., 0.998–1.002) on PancakeSwap v3 or Curve. Earn swap fees on stable-to-stable flow.

**APY decomposition (typical BSC, June 2026):**
- Base fees: 5-15% APY on tight stable-stable v3 ranges (PancakeSwap) or Curve's StableSwap. The number is *highly* pool-specific.
- CAKE emissions: variable, can add 2-10% APY.
- Net: 7-25% APY is realistic at the current (June 2026) BSC activity level, with significant variance.

**IL profile.** With a tight range, stable IL is tiny (< 0.5% on a depeg of ±1%) but a *full depeg* (USDC → 0.90) is catastrophic — the position goes 100% into the depreciated asset. A real risk in 2022-23 (USDC depegging) and a tail risk always.

**When it works.** Steady stable-to-stable flow, no major depeg. The Skill should add a depeg-bail trigger: if either asset deviates > 0.5% from 1.0, exit the position.

**When it dies.** Depeg event, volume collapse, CAKE emissions turned off.

**CMC inputs.** `/v4/dex/pairs/quotes/latest` (price + 24h vol), `/v1/dex/token/pools` (TVL + fee tier), `get_global_metrics_latest` (Fear & Greed — bail at < 20).

**Spec format.**
```json
{
  "strategy_id": "lp-concentrated-stable-v1",
  "venue": "pancakeswap_v3",
  "pair": "USDC/USDT",
  "fee_tier": 100,         // 0.01% tier
  "range": [0.998, 1.002],  // ±0.2%
  "entry": "always_on_unless_bail",
  "bail": "any_asset_deviates_>0.5%_from_peg",
  "rebalance": "weekly_close_to_peg",
  "expected_apy": 0.12,
  "il_risk": 0.005,
  "data_inputs": ["cmc.dex.pairs.quotes.latest", "cmc.global.metrics.latest"]
}
```

### 4.2 Volatile-Volatile Concentrated Liquidity (WBNB/ETH, CAKE/BNB, mid-caps)

**Mechanism.** Deposit into a tight range around the current price. Earn swap fees from high volume.

**APY decomposition (typical BSC, June 2026):**
- Base fees: 20-100%+ APY at *very* tight ranges (e.g., ±5%) on high-volume pairs.
- But: the tighter the range, the more capital-efficient, the higher the *fee APY*, and the higher the *IL when out of range*.
- CAKE emissions: 0-30% APY depending on gauge weight.

**IL profile.** Concentrated IL formula (Auditless, Medium):
- For range [p_a, p_b], if price stays in range, IL is amplified vs full-range.
- If price moves *out* of range, position is 100% in the depreciated asset. Catastrophic.

**When it works.** Range-pinned price, high volume, fee APY > IL. **The Skill should size the range based on realized volatility**: range = current_price × exp(±k × daily_vol × sqrt(days_in_range)). The standard k=2.5 (≈95% confidence) is a good default.

**When it dies.** Trending market (price moves out of range), vol spike, range too tight for the vol regime.

**CMC inputs.** `get_crypto_ohlcv` (20-30d for vol calc), `get_crypto_technical_analysis` (ATR), `/v4/dex/pairs/quotes/latest` (current price + 24h vol), `get_crypto_quotes_latest` (sanity check).

**Spec format.**
```json
{
  "strategy_id": "lp-vol-range-ema-v1",
  "venue": "pancakeswap_v3",
  "pair": "WBNB/USDC",
  "fee_tier": 2500,         // 0.25%
  "range_calc": "current_price * exp(±2.5 * daily_vol_20d * sqrt(7))",
  "rebalance": "every_7d_OR_price_outside_range",
  "expected_fee_apy": 0.45,
  "expected_il_apy": -0.15,
  "net_apy": 0.30,
  "data_inputs": ["cmc.crypto.ohlcv", "cmc.crypto.technical_analysis", "cmc.dex.pairs.quotes.latest"]
}
```

### 4.3 Hedged LP (Long spot + Short perp = Delta-Neutral)

**Mechanism.** Provide concentrated LP on a volatile pair. Simultaneously short the underlying on a perp to neutralize delta. The carry comes from: (LP fees + funding received from short perp) − (borrowing cost if any). The Skill's edge is *not* the position itself — anyone can do this manually — but the **auto-rebalance logic** that keeps the hedge ratio in band as price moves.

**APY decomposition:**
- LP fees: 20-80% (concentrated)
- Funding received (perp): variable, can be 5-30% on perps where shorts pay longs (negative funding). On BSC, ASTER, INJ, FIL perps available.
- IL: 0 (hedge cancels it out for small moves; imperfect for large moves due to gamma).
- Borrow cost: 0 if you're not borrowing the underlying; positive if delta-imperfect.

**IL / Gamma risk.** Hedged LP is *short gamma*. After a 10% price move, the LP's value changes by ~2% even hedged (Zelos Research). The fees have to cover that gamma loss. The Skill should set a "funding > 2 × gamma_loss" entry gate.

**When it works.** Funding-rich environment, mid-cap volatile pairs, range-narrow strategy.

**When it dies.** Negative funding (you pay shorts), low vol (fees don't compensate), large dislocations (gamma loss spike).

**CMC inputs.** `get_global_crypto_derivatives_metrics` (funding rate by token), `get_crypto_ohlcv` (vol), `/v4/dex/pairs/quotes/latest` (LP price).

**Spec format.**
```json
{
  "strategy_id": "lp-delta-neutral-v1",
  "venue": "pancakeswap_v3 + perp",
  "pair": "ASTER/USDC",
  "perp_venue": "aster_dex",
  "lp_range": "current_price ± 2σ_daily",
  "hedge_ratio": "delta_computed_daily",
  "entry": "funding_apy > 0.10 AND vol_20d > 0.04",
  "exit": "funding_apy < 0.02 OR vol_20d < 0.02",
  "rebalance": "daily_delta_hedge",
  "expected_net_apy": 0.18,
  "data_inputs": ["cmc.global.derivatives.metrics", "cmc.crypto.ohlcv", "cmc.dex.pairs.quotes.latest"]
}
```

### 4.4 Single-Sided LP via Beefy/Yearn Auto-Compounders

**Mechanism.** Deposit a single token (USDC, BNB, ETH) into a Beefy vault. Beefy wraps it into an LP position and auto-compounds rewards.

**APY decomposition:**
- Base LP: 5-25% (depending on underlying)
- Auto-compound boost: 0.5-3% (depends on compounding frequency and gas)
- Beefy perf fee: 4.5% of gains
- Net: 4-25%

**Trade-off vs manual LP:** Give up some yield (Beefy fee) for hands-off operation. The Skill should surface this trade-off explicitly.

**When it works.** When gas on manual compounding > the 4.5% perf fee, or when the user is not technical.

**When it dies.** Always works at lower APY than manual, but never *blows up* the same way. Lower variance.

**CMC inputs.** `app.beefy.com` API for vault list + APY; CMC for underlying token data.

**Spec format.**
```json
{
  "strategy_id": "lp-autocompound-bnb-vault-v1",
  "vault": "beefy:pancake:BNB-USDT",
  "underlying": "BNB",
  "deposit_token": "BNB",
  "expected_apy": 0.09,
  "fee_impact": 0.005,
  "data_inputs": ["beefy.vaults.list", "cmc.crypto.quotes.latest"]
}
```

### 4.5 Pendle PT (Principal Token) Buy-and-Hold — Fixed Yield, No IL

**Mechanism.** Buy a Pendle PT (e.g., PT-sUSDe-June-2026) at a discount to the underlying. Hold to maturity. Redeem 1:1 for the underlying. The discount = your fixed APY.

**APY = (1 / PT_price) − 1 over (time_to_maturity).**

Example (June 2026): PT-sUSDe-September-2026 at 0.94 sUSDe with 3 months to maturity → 0.06/0.94 × 4 ≈ **25.5% annualized fixed**. Typical PT yields in 2026 range 8-25% depending on underlying and tenor.

**IL profile.** Zero. PT is not a token pair — it is a fixed-income instrument that pays back 1:1.

**When it works.** When the underlying yield is expected to remain stable or rise. If yield collapses, the PT still pays out at maturity — but the mark-to-market price drops. The Skill should compute: "If yield falls to X%, what's the PT price drop?"

**When it dies.** Underlying protocol hack (e.g., Ethena depeg), liquidity crunch (can't exit before maturity), maturity rollover (you have to re-buy next PT at potentially worse rate).

**CMC inputs.** Pendle API for PT/YT prices. CMC for underlying token data + global metrics for risk regime.

**Spec format.**
```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1",
  "venue": "pendle",
  "chain": "bsc",
  "underlying": "sUSDe",
  "pt_address": "0x...",
  "maturity": "2026-09-26",
  "entry": "implied_fixed_apy > 0.10 AND underlying_score > 0.7",
  "exit": "maturity OR pt_price < discount_threshold (early exit)",
  "expected_fixed_apy": 0.142,
  "il_risk": 0.0,
  "data_inputs": ["pendle.pt.yt.prices", "cmc.global.metrics.latest", "cmc.crypto.security.detail"]
}
```

**Why this is the recommended flagship.** PT buy-and-hold is (a) the cleanest spec, (b) the easiest to backtest (PT price is observable, fixed yield is computable), (c) genuinely novel in the LLM-Skill context, (d) has zero IL, and (e) the demo is a single chart: "PT price vs implied fixed yield over time, with the strategy line."

### 4.6 Pendle YT (Yield Token) Speculation

**Mechanism.** Buy a Pendle YT (e.g., YT-sUSDe-June-2026). YT streams the *variable* yield of the underlying. YT price decays to zero at maturity (if no yield, YT worthless; if massive yield, YT captures it).

**APY.** Variable. YT is *long yield* — leveraged exposure to underlying yield changes.

**IL profile.** Not applicable — YT is a single token, not a pair.

**When it works.** When you expect the underlying yield to *increase* from current. YT is a leveraged bet on yield going up.

**When it dies.** Yield collapse (YT goes to zero fast). Maturity decay is relentless — every day you don't earn, you lose time value.

**CMC inputs.** Same as PT but with focus on the underlying protocol's yield trend.

**Spec format.** Similar to PT, with entry condition: "expected_yield_increase > X%."

**Caveat:** YT is the speculative cousin of PT. The Skill should default to PT for risk-controlled specs; YT is the "aggressive" variant.

### 4.7 Pendle LP (PT + YT combined, or SY LP)

**Mechanism.** Provide liquidity to a Pendle pool containing the underlying SY token. Earn swap fees + PENDLE emissions. The "LP" here is on the AMM curve (constant product) but the asset is a yield-bearing token.

**APY decomposition:**
- Base LP: 5-15% (swap fees on the pool)
- PENDLE emissions: 5-30% (gauge weight dependent)
- Underlying yield drift: variable (the LP is exposed to the underlying's yield moves)

**IL profile.** Yes — the LP is on a standard x*y=k curve, so IL applies between the two assets. The Skill should treat this as a hybrid: yield exposure + IL.

**When it works.** High PENDLE emissions to the pool (vote-escrow bribes are sticky to high-volume pools), stable yield from underlying.

**When it dies.** PENDLE emissions end, underlying yield volatile (IL kicks in).

**CMC inputs.** Pendle API for pool TVL + APY. CMC for PENDLE price, underlying token.

**Spec format.** Similar to volatile-volatile concentrated LP, but with the underlying being a Pendle SY token.

### 4.8 Aave Supply with CMC Risk Overlay

**Mechanism.** Deposit USDC/USDT/DAI into Aave v3 on BSC. Earn supply APY. CMC provides the risk overlay (when fear/greed low, deploy more; when high, withdraw).

**APY.** 2-6% on stables (June 2026). Variable with utilization.

**IL profile.** None.

**When it works.** When CMC's risk overlay correctly times bear/bull. The wedge is *the overlay*, not the Aave position itself.

**When it dies.** When the overlay is wrong (entering at top of fear/greed cycle, etc.).

**CMC inputs.** `get_global_metrics_latest` (Fear & Greed), `get_crypto_quotes_latest` (stablecoin prices), Aave subgraph for live rates.

**Spec format.**
```json
{
  "strategy_id": "lp-aave-supply-overlay-v1",
  "venue": "aave_v3",
  "asset": "USDC",
  "entry": "fear_greed < 30 AND stablecoin_deviation < 0.005",
  "exit": "fear_greed > 70 OR stablecoin_deviation > 0.01",
  "expected_apy": 0.04,
  "il_risk": 0.0,
  "data_inputs": ["cmc.global.metrics.latest", "cmc.crypto.quotes.latest"]
}
```

### 4.9 Concentrated Liquidity with Rebalance Triggers

**Mechanism.** Same as 4.2 (volatile-volatile CL) but with explicit rebalance rules driven by CMC signals.

**CMC-driven rebalance triggers:**
- **Volatility regime shift:** If 20d realized vol moves > 30% in 7d, widen range by 1.5×.
- **Sentiment brake:** If Fear & Greed > 80, narrow range (take less risk near euphoria).
- **Catalyst check:** If CMC news shows major negative event for the underlying, withdraw.
- **Funding brake:** If perp funding is heavily negative (longs pay shorts), widen the range or exit — this means retail is heavily long, susceptible to long squeeze.

**When it works.** When the CMC signals are predictive of vol shifts. Backtest is the proof.

**When it dies.** When CMC signals are lagging (fear/greed is reactive, not leading).

**Spec format.** Extends 4.2 with explicit CMC-signal triggers.

### 4.10 Liquidity-Mining Incentive Rotation

**Mechanism.** Scan PancakeSwap v3, Thena, Aerodrome (Base) for pools with high emissions-to-IL ratio. Rotate capital weekly.

**APY.** 30-100%+ in high-emission windows; collapses to 0 when emissions end.

**IL profile.** Standard AMM IL.

**When it works.** New token launches with high emissions, bribe markets active (ve(3,3) on Thena/Aerodrome).

**When it dies.** Always. Emissions are temporary. The Skill's job is to detect when emissions drop below IL cost and exit.

**CMC inputs.** `/v1/dex/liquidity-change/list` (TVL changes), `/v1/dex/token/pools` (pool sizes), `get_crypto_quotes_latest` (token price for IL calc).

**Spec format.**
```json
{
  "strategy_id": "lp-emissions-rotation-v1",
  "venues": ["pancakeswap_v3", "thena_fusion", "aerodrome"],
  "scan_frequency": "daily",
  "entry": "emissions_apy > 0.30 AND projected_il_30d < 0.05",
  "exit": "emissions_apy < 0.10 OR tvl_drop_7d > 0.30",
  "expected_apy": 0.45,
  "il_risk": 0.10,
  "data_inputs": ["cmc.dex.liquidity.change.list", "cmc.dex.token.pools", "cmc.crypto.quotes.latest"]
}
```

### 4.11 Bonus: Pendle Boros (Funding-Rate Swaps)

**Mechanism.** Trade funding rate exposure using Pendle's Boros market. Buy PT-BTC-funding to lock in a fixed funding rate for a defined period; YT-BTC-funding is the leveraged bet on funding increasing.

**Why it's a wedge.** Boros is novel (launched Aug 2025) and on-chain-native. The Skill can specify "lock in X% funding on BTC for 30 days" as a fully backtestable spec.

**Spec format.** Similar to 4.5 (PT) but the underlying is funding rate, not yield.

**Caveat:** Boros adoption is still early (Q1 2026). Pool depth on most pairs is thinner than Pendle V2. Operator should check live liquidity before recommending.

---

---

## 5. CMC × LP Strategy Spec Library (the actual track 2 deliverables)

This is the section that matters. Each of the following is a **complete CMC Skill spec** that someone could literally copy into a `SKILL.md` file and ship. The format follows the official catalog (YAML frontmatter + markdown body), with the addition of a structured **Output Spec** section that the agent emits to the backtester.

### 5.1 Skill: `lp-pendle-pt-fixed` (flagship)

```yaml
---
name: lp-pendle-pt-fixed
description: |
  Generates a backtestable Pendle PT (Principal Token) buy-and-hold strategy spec for
  a given underlying yield-bearing asset and maturity. PT is fixed-income exposure to
  DeFi yield with zero impermanent loss. Use this skill when the user asks for a
  fixed-yield LP strategy, asks about Pendle PT vs YT, wants a low-risk LP alternative,
  or wants to lock in a known yield on a stablecoin or LST for a defined period.
  Triggers: "pendle PT", "fixed yield LP", "no IL strategy", "principal token",
  "stablecoin yield lock-in", "/lp-pendle-pt-fixed"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_metrics
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_crypto_security_detail
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - Bash
  - Read
---
```

**# Pendle PT Fixed-Yield LP Strategy**

## What this Skill does

Takes a market question about fixed-yield LP exposure and emits a backtestable strategy spec for a Pendle Principal Token (PT) buy-and-hold on a supported underlying (sUSDe, stETH, USDe-wrapped variants, BSC-native stables). The PT is held to maturity, redeemed 1:1 for the underlying, and the *discount at purchase* is the locked-in fixed yield.

This is genuinely zero-impermanent-loss LP. The Skill treats the PT as a fixed-income instrument and selects maturities, underlyings, and entry conditions based on CMC data + live Pendle market data.

## Inputs

| Input | Type | Source |
|---|---|---|
| Underlying asset | string (e.g., "sUSDe", "stETH") | user |
| Chain | enum (bsc / ethereum / arbitrum) | user, default bsc |
| Capital (USD) | number | user |
| Risk tolerance | enum (low / medium / high) | user, default low |

## Logic

1. **Resolve underlying via CMC:**
   - `search_cryptos(query=underlying)` → get CMC id, contract address.
   - `get_crypto_quotes_latest(id=cmc_id)` → spot price + market cap (sanity check vs PT price).
   - `get_crypto_metrics(id=cmc_id)` → holder concentration (reject if top-10 holders > 70%).
   - `get_crypto_security_detail(contract_address=...)` → security score (reject if score < 0.6).
   - `get_crypto_latest_news(id=cmc_id)` → recent catalysts (reject if major negative news in 7d).

2. **Fetch macro regime:**
   - `get_global_metrics_latest` → fear_greed, btc_dominance, total_mcap.
   - `get_global_crypto_derivatives_metrics` → perp funding aggregate (sense of "risk-on/risk-off").

3. **Fetch live Pendle markets** (separate Pendle API or via on-chain reads):
   - Pull all PT markets for the underlying across supported chains.
   - For each PT, compute **implied_fixed_apy** = (1 / pt_price) − 1 over (time_to_maturity in years).
   - Filter: pt_liquidity_usd > 100,000 (avoid illiquid markets); time_to_maturity between 14d and 365d.

4. **Score and rank:**
   - Base score: implied_fixed_apy (higher = better, ceteris paribus).
   - Penalize: time_to_maturity < 30d (too short, less attractive), > 180d (longer lock).
   - Penalize: implied_fixed_apy > 0.40 (too good — likely to mean the underlying is in trouble, e.g., depeg risk; halve score).
   - Boost: underlying security_score > 0.85, holder concentration top-10 < 50%.

5. **Apply entry conditions:**
   - If risk_tolerance == low: require implied_fixed_apy >= 0.08.
   - If risk_tolerance == medium: implied_fixed_apy >= 0.12.
   - If risk_tolerance == high: implied_fixed_apy >= 0.20.
   - Reject if fear_greed > 80 (macro euphoria, may be late).
   - Reject if any major negative news on the underlying in 7d.

6. **Emit spec** in the Output Spec format.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1",
  "venue": "pendle",
  "chain": "bsc",
  "underlying": {
    "symbol": "sUSDe",
    "cmc_id": 29470,
    "contract_address": "0x..."
  },
  "pt": {
    "address": "0x...",
    "maturity": "2026-09-26",
    "current_price": 0.94,
    "implied_fixed_apy": 0.142,
    "liquidity_usd": 2400000
  },
  "action": "buy_pt_hold_to_maturity",
  "entry": {
    "condition": "always_on_above_threshold",
    "max_buy_slippage_bps": 30
  },
  "exit": {
    "primary": "redeem_at_maturity",
    "early_exit_if": [
      "pt_price > 0.99 (take profit early)",
      "underlying_security_score < 0.5 (de-risk)",
      "fear_greed > 90 AND time_to_maturity < 14d"
    ]
  },
  "sizing": {
    "method": "full_capital_at_entry",
    "max_position_usd": null
  },
  "risk": {
    "il": 0.0,
    "smart_contract_risk": "underlying_protocol_dependent",
    "duration_risk_days": 91
  },
  "expected_metrics": {
    "fixed_apy": 0.142,
    "sharpe_estimate": 8.5,
    "max_drawdown_estimate": 0.05
  },
  "data_inputs": [
    "cmc.search.cryptos",
    "cmc.crypto.quotes.latest",
    "cmc.crypto.metrics",
    "cmc.crypto.security.detail",
    "cmc.crypto.latest.news",
    "cmc.global.metrics.latest",
    "pendle.markets.list",
    "pendle.pt.quote"
  ]
}
```

## Backtest outline

1. Pull historical PT prices for the candidate (e.g., PT-sUSDe-June-2026 over Mar-Jun 2026).
2. For each daily timestamp, compute implied_fixed_apy at that snapshot.
3. Apply the entry/exit rules in the spec.
4. Replay the resulting trade log over the period.
5. Output: PnL curve, Sharpe, max drawdown, win rate (most PT positions go to maturity = 100% "win" on the principal).

Expected backtest result (illustrative): a strategy that enters when implied_fixed_apy > 0.10 and holds to maturity should show **~0% drawdown** on principal (PT pays 1:1), **10-20% annualized return**, and a Sharpe of 5-10+ (low vol of returns since principal is fixed).

## Why this wins the panel

- **Originality:** Almost no Track 2 entry will think about Pendle PT. It's the natural extension of "Quantopian-style strategy generation" — fixed-income LP is a strategy class the spec literally calls for.
- **Technical execution:** The spec is fully implementable; the backtest is clean; the IL is literally zero (which is a powerful demo line: "I generated a strategy with zero impermanent loss").
- **Real-world relevance:** PT buy-and-hold is a real product used by real funds. The Skill makes it accessible to LLM agents.
- **Demo:** "I queried 'fixed yield on sUSDe' and got a backtested spec. The chart shows PT price vs implied fixed yield over 6 months. The strategy entered at the right time, held to maturity, and the PnL is on the right."

---

### 5.2 Skill: `lp-delta-neutral`

```yaml
---
name: lp-delta-neutral
description: |
  Generates a backtestable delta-neutral LP strategy spec: concentrated liquidity on a
  volatile pair (PancakeSwap v3 / Thena) hedged with a short perp position. Use this
  skill when the user asks about funding-rate carry, market-neutral LP, hedging LP
  exposure, or harvesting perp funding with LP fees. The spec outputs an LP range,
  a hedge ratio, and a rebalance schedule.
  Triggers: "delta neutral", "hedged LP", "funding carry", "LP hedge",
  "short perp + long LP", "/lp-delta-neutral"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_ohlcv
  - mcp__cmc-mcp__get_crypto_technical_analysis
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - Bash
  - Read
---
```

**# Delta-Neutral LP Strategy**

## What this Skill does

Generates a backtestable delta-neutral LP strategy: provide concentrated liquidity on a volatile BSC pair, short the underlying on a perp venue to neutralize price exposure, and harvest the carry from (LP fees + funding received) − (gamma loss on dislocation). Outputs a spec with the LP range, hedge ratio, rebalance frequency, and entry/exit conditions.

## Inputs

| Input | Type | Source |
|---|---|---|
| Token | string (e.g., "ASTER", "BNB", "WIF") | user |
| Pair | string (e.g., "ASTER/USDC") | user, default "{token}/USDC" |
| Capital (USD) | number | user |
| Risk tolerance | enum (low / medium / high) | user, default medium |
| Hold horizon (days) | int | user, default 30 |

## Logic

1. **Resolve token via CMC:**
   - `search_cryptos` → cmc_id, contract address.
   - `get_crypto_ohlcv(id, days=30, interval=daily)` → 30d OHLCV for vol calc.
   - `get_crypto_technical_analysis(id)` → ATR(14), realized vol.
   - `get_crypto_latest_news(id)` → catalyst check.
   - `get_crypto_quotes_latest(id)` → spot price.

2. **Fetch perp market data:**
   - `get_global_crypto_derivatives_metrics` → funding rate aggregated.
   - For BSC: query perp venues (Aster, INJ, etc.) for the specific token's funding rate. CMC's derivatives metrics is CEX-aggregated; for BSC-native perps, supplement with the perp venue's API or on-chain reads.

3. **Compute LP range:**
   - daily_vol = stdev(log_returns) over 20d (annualize: daily_vol × sqrt(365)).
   - For a 7-day hold, range_width = exp(2.5 × daily_vol × sqrt(7)) − exp(−2.5 × daily_vol × sqrt(7)).
   - range_lower = current_price × exp(−2.5 × daily_vol × sqrt(7)).
   - range_upper = current_price × exp(+2.5 × daily_vol × sqrt(7)).
   - Convert to PancakeSwap v3 tick bounds.

4. **Compute hedge ratio:**
   - For full-range LP: delta ≈ 0.5 × position_value. Hedge 0.5 × position in notional short.
   - For concentrated range [p_a, p_b] with current price p, delta(p) = 0.5 × (sqrt(p × p_b) − sqrt(p_a × p)) / (sqrt(p_b) − sqrt(p_a)) × position_value. (Approximate, see Auditless Medium article for exact formula.)
   - Recompute daily as price moves.

5. **Entry conditions:**
   - Require `funding_apy > 0.05` (positive funding = shorts paid = we earn funding as short).
   - Require `daily_vol > 0.025` (vol too low = fees don't compensate IL).
   - Reject if recent major negative news.
   - For low risk: require `funding_apy > 0.10`.
   - For high risk: allow `funding_apy > 0.03` but with tighter range.

6. **Exit conditions:**
   - funding_apy < 0.01 (carry gone).
   - daily_vol < 0.015 (vol collapsed, fees dried up).
   - Price moved out of range for > 2 consecutive rebalances.
   - Time horizon reached.

7. **Rebalance:**
   - Daily: recompute delta, rebalance hedge via perp.
   - Weekly: recompute range from new vol, withdraw + redeposit LP if range shifted > 20%.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-delta-neutral-v1",
  "venue_lp": "pancakeswap_v3",
  "venue_perp": "aster_dex",
  "chain": "bsc",
  "pair": "ASTER/USDC",
  "fee_tier": 2500,
  "range": [4.85, 5.42],
  "current_price": 5.12,
  "daily_vol_20d": 0.045,
  "hedge": {
    "perp": "ASTER-PERP",
    "side": "short",
    "notional_usd": 510,
    "delta_pct": 0.50
  },
  "entry": {
    "funding_apy_min": 0.10,
    "vol_20d_min": 0.025
  },
  "exit": {
    "funding_apy_max": 0.01,
    "vol_20d_max": 0.015,
    "out_of_range_days": 2
  },
  "rebalance": {
    "hedge_frequency": "daily",
    "range_frequency": "weekly"
  },
  "expected_metrics": {
    "net_carry_apy": 0.18,
    "sharpe_estimate": 3.5,
    "max_drawdown_estimate": 0.08
  },
  "data_inputs": [
    "cmc.crypto.ohlcv",
    "cmc.crypto.technical_analysis",
    "cmc.crypto.quotes.latest",
    "cmc.global.derivatives.metrics",
    "cmc.global.metrics.latest",
    "aster.perp.funding.rate",
    "pancakeswap.pool.snapshot"
  ]
}
```

## Backtest outline

1. Pull 90d of daily OHLCV for ASTER, plus 90d of daily funding rate for ASTER perp.
2. For each day: if entry conditions met, open LP position (mark to mid-range), open short hedge at current price.
3. Daily: mark to market. Recompute delta. Rebalance hedge.
4. Weekly: if vol shifted > 20%, close LP and re-open at new range.
5. Track: cumulative PnL, daily PnL, max drawdown, Sharpe.

Expected backtest result (illustrative): 10-20% net APY with low drawdown (< 10%) when funding is healthy. Worst case: funding flips negative — the position bleeds slowly (funding paid) but doesn't blow up.

## Why this wins

- It's a real market-neutral strategy with measurable Sharpe.
- The hedge-ratio math is *technical execution* in the strongest sense.
- The Skill demonstrates that CMC's data (funding + OHLCV + technical) is sufficient to construct a delta-neutral position without a human in the loop.
- Demo: "I took a 30-day ASTER view, computed vol-adjusted range, hedged with a perp, and the backtest shows positive carry with low drawdown."

---

### 5.3 Skill: `lp-vol-range-ema`

```yaml
---
name: lp-vol-range-ema
description: |
  Generates a backtestable concentrated-liquidity LP strategy with volatility-driven
  range selection. Use this skill for volatile pairs (BNB/ETH, mid-caps) where the LP
  wants to maximize fee capture by tightly concentrating liquidity around the current
  price, with the range rebalanced weekly based on realized volatility.
  Triggers: "concentrated LP", "range order", "tight range LP", "PancakeSwap v3",
  "Uniswap v3 BSC", "/lp-vol-range-ema"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_ohlcv
  - mcp__cmc-mcp__get_crypto_technical_analysis
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_global_metrics_latest
  - Bash
  - Read
---
```

**# Volatility-Adjusted Concentrated LP**

## What this Skill does

Generates a backtestable concentrated-liquidity LP strategy where the price range is computed from realized volatility, rebalanced weekly, and the entry/exit is gated by regime signals (Fear & Greed, vol shift, news catalyst).

## Inputs

| Input | Type | Source |
|---|---|---|
| Pair | string (e.g., "BNB/USDC") | user |
| Capital (USD) | number | user |
| Range multiplier (k) | float | user, default 2.5 (≈95% CI for 7d) |
| Lookback days | int | user, default 20 |

## Logic

1. **Resolve pair via CMC:**
   - For each token in pair, get cmc_id, contract address.
   - `get_crypto_ohlcv` (days=30) for vol calculation.
   - `get_crypto_technical_analysis` for ATR(14).

2. **Compute range:**
   - daily_vol = stdev(log_returns) of token0/token1 ratio over `lookback_days`.
   - annualized_vol = daily_vol × sqrt(365).
   - range_pct = 2 × k × daily_vol × sqrt(7) (7-day expected move).
   - range_lower = current_price × (1 − range_pct).
   - range_upper = current_price × (1 + range_pct).
   - Convert to PancakeSwap v3 tick spacing.

3. **Filter / Score:**
   - 30d average daily volume > $500K (else not enough fees).
   - Token must be on PancakeSwap v3 supported token list (no rebasing tokens).
   - IL: estimate using the Auditless formula for a range [p_a, p_b] given expected move distribution.

4. **Entry conditions:**
   - vol_ratio = (vol_7d) / (vol_30d). If > 1.5, vol is rising — prefer wider range (k=3.0).
   - If < 0.7, vol is compressing — tighter range (k=2.0).
   - Reject if Fear & Greed > 85 (extreme euphoria, likely to revert — wider range or skip).

5. **Exit conditions:**
   - Price exits range for > 48h.
   - Vol regime flips (vol_7d > 2 × vol_30d) — close and re-open with wider range.
   - Major negative news on either token.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-vol-range-ema-v1",
  "venue": "pancakeswap_v3",
  "pair": "BNB/USDC",
  "fee_tier": 500,
  "range": [605, 645],
  "current_price": 624,
  "range_pct": 0.064,
  "annualized_vol_20d": 0.55,
  "k_multiplier": 2.5,
  "rebalance_frequency": "weekly",
  "rebalance_trigger": "vol_7d / vol_30d > 1.5 OR price_outside_range_48h",
  "entry": {
    "min_30d_avg_volume_usd": 500000,
    "max_fear_greed": 85
  },
  "exit": {
    "out_of_range_hours": 48,
    "news_negative": true
  },
  "expected_metrics": {
    "fee_apy_estimate": 0.45,
    "il_apy_estimate": -0.12,
    "net_apy": 0.33,
    "max_drawdown_estimate": 0.18
  },
  "data_inputs": [
    "cmc.crypto.ohlcv",
    "cmc.crypto.technical_analysis",
    "cmc.crypto.quotes.latest",
    "cmc.global.metrics.latest",
    "cmc.crypto.latest.news"
  ]
}
```

## Backtest outline

Use `DefiLab-xyz/uniswap-v3-backtest` (open-source) or `ilyamk/uniswap-v3-lp-strategy-toolkit` for the core. Plug in the CMC-derived range / rebalance rules. Track active liquidity %, fees earned, IL realized, net PnL.

## Why this works as Track 2

- It's a real quant strategy with measurable Sharpe.
- The math is *transparent* — judges can see the range calc.
- CMC's data drives the rebalance — that's the CMC integration point.
- Demo: a chart showing the range tracking the price, with the active liquidity % (the % of position earning fees) over time.

---

### 5.4 Skill: `lp-concentrated-stable`

```yaml
---
name: lp-concentrated-stable
description: |
  Generates a backtestable stable-pair concentrated-liquidity LP strategy with a
  depeg-bail trigger. Use this skill for stable-to-stable pairs (USDC/USDT,
  USD1/USDC, DAI/USDC) on PancakeSwap v3 or Curve. The strategy is range-tight
  around the peg, with a hard exit on depeg.
  Triggers: "stable LP", "stablecoin yield", "USDC/USDT LP", "Curve stable",
  "/lp-concentrated-stable"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_ohlcv
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_crypto_latest_news
  - Bash
  - Read
---
```

**# Stable-Pair Concentrated LP**

## What this Skill does

Generates a backtestable stable-pair concentrated-LP spec with depeg protection. Targets the 0.01% or 0.05% fee tier on PancakeSwap v3 (or Curve StableSwap for non-paired stables). The range is tight (±0.1% to ±0.3% from peg). A bail trigger exits on any stable deviating > 0.5% from peg.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-concentrated-stable-v1",
  "venue": "pancakeswap_v3",
  "pair": "USDC/USDT",
  "fee_tier": 100,
  "range": [0.998, 1.002],
  "current_price": 1.0001,
  "entry": "always_on_unless_bail",
  "bail": "any_asset_deviates_>0.5%_from_peg",
  "rebalance": "weekly_close_to_peg",
  "expected_metrics": {
    "fee_apy_estimate": 0.12,
    "il_risk": 0.005,
    "depeg_loss_risk": 0.95
  },
  "data_inputs": [
    "cmc.crypto.quotes.latest",
    "cmc.crypto.ohlcv",
    "cmc.global.metrics.latest"
  ]
}
```

## Why this works

- Simpler than volatile LP; tighter range capture.
- The depeg-bail is the wedge — most stable LP strategies ignore the tail risk.
- The skill demonstrates CMC's ability to do real-time price monitoring for safety.

---

### 5.5 Skill: `lp-emissions-rotation`

```yaml
---
name: lp-emissions-rotation
description: |
  Generates a backtestable emissions-rotation strategy: scan PancakeSwap v3, Thena,
  and Aerodrome pools for high emissions-to-IL ratios and rotate capital weekly. Use
  this skill when the user asks about maximizing LP yield via incentive capture, or
  wants a strategy that automatically enters and exits high-emission pools.
  Triggers: "liquidity mining", "emissions", "incentive rotation", "yield farming",
  "ve(3,3)", "/lp-emissions-rotation"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_ohlcv
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_crypto_latest_news
  - Bash
  - Read
---
```

**# Liquidity-Mining Emissions Rotation**

## What this Skill does

Generates a backtestable rotation strategy that scans BSC + cross-chain DEX pools for high emissions, scores them by (emissions_apy − projected_il_30d), and outputs a weekly rebalance schedule with entry/exit conditions per pool.

## Logic

1. **Pool universe scan** (CMC `/v1/dex/liquidity-change/list`, `/v1/dex/token/pools`):
   - For each token in the eligible-149 list (the hackathon's allowlist), find all DEX pools with TVL > $50K.
   - Compute 7d TVL change (proxy for emissions activity).

2. **APY estimation per pool:**
   - emissions_apy = (token_per_day × price) / pool_tvl × 365.
   - Source: protocol's emission schedule (PancakeSwap gauge, Thena bribe, Aerodrome gauge).

3. **IL estimation per pool:**
   - Use 30d realized vol of the underlying.
   - IL_30d = (2 × sqrt(price_ratio) / (1 + price_ratio)) − 1, where price_ratio is the expected move over 30d.

4. **Score = (emissions_apy − IL_30d) × (TVL_stability_score) × (token_security_score).**

5. **Entry:** Top 5 pools by score, weighted by inverse-vol (lower vol = more weight).
6. **Exit:** Pool drops out of top 10; emissions_apy < 0.10; TVL drops > 30% in 7d.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-emissions-rotation-v1",
  "venues": ["pancakeswap_v3", "thena_fusion", "aerodrome"],
  "top_pools": [
    {
      "venue": "pancakeswap_v3",
      "pair": "CAKE/BNB",
      "fee_tier": 2500,
      "emissions_apy": 0.45,
      "il_30d_estimate": 0.08,
      "score": 0.82,
      "weight": 0.25
    }
  ],
  "rebalance_frequency": "weekly",
  "entry": "score > 0.5",
  "exit": ["score < 0.2", "tvl_drop_7d > 0.30", "emissions_apy < 0.10"],
  "data_inputs": [
    "cmc.dex.liquidity.change.list",
    "cmc.dex.token.pools",
    "cmc.crypto.quotes.latest",
    "cmc.crypto.ohlcv",
    "protocol.emissions.schedule"
  ]
}
```

## Why this works

- The rotation is the *strategy*. Static LP is not.
- CMC's liquidity-change endpoints are uniquely suited — they expose pool-level TVL dynamics that traditional CEX APIs don't.
- High Sharpes are possible during emissions windows; the exit logic prevents post-emissions blowups.

---

### 5.6 Skill: `lp-pendle-boros` (advanced / bonus)

```yaml
---
name: lp-pendle-boros
description: |
  Generates a backtestable Pendle Boros funding-rate swap strategy. Use this skill
  when the user wants to lock in a fixed funding rate, or speculate on funding
  rate changes, on BTC or ETH. Boros is a fully on-chain funding-rate market.
  Triggers: "Boros", "funding rate swap", "fixed funding", "Pendle funding",
  "/lp-pendle-boros"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - mcp__cmc-mcp__get_crypto_ohlcv
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_global_metrics_latest
  - Bash
  - Read
---
```

**# Pendle Boros Funding-Rate Strategy**

## What this Skill does

Generates a backtestable spec for a Pendle Boros funding-rate swap. Boros (launched Aug 2025) is a fully on-chain orderbook for funding rate exposure. Buy PT-funding to lock in a fixed funding rate; buy YT-funding to speculate on funding increasing.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-pendle-boros-v1",
  "venue": "pendle_boros",
  "chain": "ethereum_or_bsc",
  "underlying_funding": "BTC",
  "instrument": "PT",
  "tenor_days": 30,
  "implied_fixed_funding_apy": 0.18,
  "current_market_funding_apy": 0.22,
  "edge": 0.04,
  "action": "buy_pt",
  "expected_pnl_if_held": 0.18,
  "data_inputs": [
    "cmc.global.derivatives.metrics",
    "boros.markets.list",
    "boros.pt.quote"
  ]
}
```

## Caveat for the Skill author

Boros adoption is still early. The Skill should include a liquidity-depth check (`boros.open_interest > $100K`) before recommending. If depth is insufficient, fall back to a Pendle V2 PT spec on a yield-bearing asset.

---

### 5.7 Skill: `lp-pendle-yt-long` (the aggressive cousin)

Similar to `lp-pendle-pt-fixed` but for YT (Yield Token). YT is leveraged yield exposure. Use when the user expects the underlying yield to *rise*.

```yaml
---
name: lp-pendle-yt-long
description: |
  Generates a backtestable Pendle YT (Yield Token) long-yield strategy. Use this
  skill when the user expects the underlying yield to increase and wants leveraged
  exposure to that yield. YT decays to zero at maturity — this is a directional bet.
  Triggers: "Pendle YT", "long yield", "leveraged yield", "yield speculation",
  "/lp-pendle-yt-long"
---
```

The output spec is identical in structure to 5.1, with these key differences:
- `instrument: "YT"`
- `expected_apy: variable` (not fixed)
- `entry.condition: "expected_yield_increase > 2%"`
- Higher `max_drawdown_estimate` (~30-50%, because YT is leveraged)
- Higher `sharpe_estimate` if the yield call is right, negative if wrong

This is a "high risk variant" the Skill can offer as an alternative to PT.

---

### 5.8 Skill: `lp-aave-supply-overlay` (the risk-off base case)

```yaml
---
name: lp-aave-supply-overlay
description: |
  Generates a backtestable Aave supply strategy with a CMC-driven risk overlay
  (Fear & Greed, stablecoin deviation, BTC dominance). Use this skill when the user
  wants a low-risk, low-yield baseline that scales into risk-on conditions.
  Triggers: "Aave supply", "stablecoin yield", "low risk LP", "risk-off yield",
  "/lp-aave-supply-overlay"
---
```

```json
{
  "strategy_id": "lp-aave-supply-overlay-v1",
  "venue": "aave_v3",
  "asset": "USDC",
  "expected_apy": 0.04,
  "entry": {
    "fear_greed_max": 35,
    "btc_dominance_min": 0.50,
    "stablecoin_deviation_max": 0.005
  },
  "exit": {
    "fear_greed_min": 70,
    "stablecoin_deviation_min": 0.01
  },
  "il_risk": 0.0,
  "data_inputs": [
    "cmc.global.metrics.latest",
    "cmc.crypto.quotes.latest"
  ]
}
```

This is the *floor* of a strategy menu. The Skill library's wrapper can recommend Aave supply when the macro regime is risk-off, and switch to one of the higher-yield LP strategies when the regime is risk-on. That's a meta-strategy — see 5.9.

---

### 5.9 Wrapper Skill: `lp-strategy-menu` (the library)

A wrapper that takes the user's risk tolerance and macro view, and recommends a *combination* of strategies from the library. This is what makes the Skill feel like a "Strategy-as-a-Service" primitive.

```yaml
---
name: lp-strategy-menu
description: |
  Wrapper that takes a user's risk tolerance, capital, and macro view, and
  recommends a portfolio of LP strategies from the lp-* family. Use this skill
  when the user asks for an LP portfolio, a yield strategy allocation, or wants
  to compare multiple LP strategies side-by-side.
  Triggers: "LP portfolio", "yield strategy menu", "compare LP strategies",
  "strategy allocation", "/lp-strategy-menu"
allowed-tools:
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - mcp__cmc-mcp__get_crypto_latest_news
  - Bash
  - Read
---
```

## What this Skill does

Loads all 5-7 underlying LP Skills, runs each in turn, and produces an *allocation* spec that distributes capital across them based on the user's risk profile and the current macro regime.

## Output Spec (JSON)

```json
{
  "strategy_id": "lp-strategy-menu-v1",
  "user_risk": "medium",
  "macro_regime": "risk_on",
  "fear_greed": 65,
  "allocations": [
    {
      "skill": "lp-pendle-pt-fixed",
      "underlying": "sUSDe",
      "weight": 0.40,
      "expected_apy": 0.142,
      "rationale": "risk_on + fixed-income floor"
    },
    {
      "skill": "lp-vol-range-ema",
      "pair": "BNB/USDC",
      "weight": 0.30,
      "expected_apy": 0.33,
      "rationale": "moderate vol, BNB has deep liquidity"
    },
    {
      "skill": "lp-concentrated-stable",
      "pair": "USDC/USDT",
      "weight": 0.20,
      "expected_apy": 0.10,
      "rationale": "stable yield + low vol ballast"
    },
    {
      "skill": "lp-aave-supply-overlay",
      "asset": "USDC",
      "weight": 0.10,
      "expected_apy": 0.04,
      "rationale": "dry powder for rebalance opportunities"
    }
  ],
  "blended_expected_apy": 0.19,
  "blended_max_drawdown_estimate": 0.10,
  "rebalance_frequency": "weekly"
}
```

This wrapper turns the library into a single artifact: a portfolio of LP strategies. It's the cleanest expression of the "Quantopian-style strategy generation, adapted to crypto" the spec calls for.

---

## 6. The "Originality" Wedge — what almost no other entrant will do

### 6.1 What's over-saturated in Track 2

Based on the spec's own example and the typical agent-skill landscape, these will dominate the Track 2 entry pool:

- **Momentum + RSI/MACD + Fear & Greed blend** — the spec literally calls this out. Expect 20+ entries.
- **Sentiment divergence** (social heat vs price) — popular on Twitter, easy to demo.
- **Regime detection** (above/below 200d MA, vol regime) — straightforward Quantopian-style.
- **Generic "best entry point" skill** — vague, not strategy-specific.
- **News-catalyst detection** — easy, low-edge, demoable but not impressive.

**What they all share:** They are *directional trading* strategies expressed as a Skill. They ignore the LP universe entirely.

### 6.2 What LP farming is under-served in agent skills

**Almost no one is building LP strategy generation as a Skill.** The reasons are real but not impossible:

- LP mechanics are harder to reason about (IL, ranges, gamma).
- The data sources are DEX-native (CMC DEX API, on-chain reads), not CEX-only.
- The backtest is more complex (active liquidity, range tracking, fee accumulation).

But these are *technical moats*, not disqualifications. A 40-hour builder with CMC access and a solid grasp of LP math can ship a credible LP Strategy Skill. That's the operator's edge.

### 6.3 The 1-2 ideas that score 9-10/10 on originality

**Idea 1: `lp-pendle-pt-fixed` (the flagship).** A Skill that turns a "fixed yield" question into a backtestable Pendle PT buy-and-hold spec. Genuinely novel — Pendle is not in the typical agent's toolkit. The demo is a single chart: PT price vs implied fixed yield over 6 months, with the strategy line.

**Idea 2: `lp-strategy-menu` (the library wrapper).** A Skill that composes 5-7 underlying LP strategies into a portfolio allocation. This is the "Strategy-as-a-Service" wedge — it's not just a Skill, it's a *primitive* other agents consume. The demo is the JSON allocation spec, with the rationale text explaining each weight.

These two together score:
- **Originality 9-10/10** — almost no other entrant will touch LP or Pendle.
- **Technical execution 9/10** — the math is real, the spec is backtestable, the integration with CMC is non-trivial.
- **Real-world relevance 8-9/10** — fixed-income LP is a real product, and LLM agents consuming strategy specs is a real pattern.
- **Demo 8-9/10** — the chart and the allocation spec are both visually clean.

### 6.4 The demo narrative that lands

**Opening (15s):** "I built a CMC Skill library for LP-farming strategy generation. The flagship is `lp-pendle-pt-fixed` — it takes a fixed-yield question and outputs a backtestable Pendle PT buy-and-hold spec."

**Live demo 1 (45s):** Query the Skill: "Give me a fixed-yield LP strategy for sUSDe on BSC, $5K capital, low risk." Show the JSON spec output. Highlight `expected_fixed_apy: 0.142`, `il_risk: 0.0`, `maturity: 2026-09-26`.

**Backtest chart (45s):** Show the backtest — implied fixed APY over 6 months, the strategy's entry/exit points, the resulting PnL. Sharpe, max DD, win rate.

**Library (30s):** Show the `lp-strategy-menu` allocation spec — 4 strategies weighted, expected blended APY 19%, max DD 10%. The rationale text is LLM-generated and explains the regime.

**CMC integration proof (30s):** Open the dev console. Show the x402 pay-per-call to CMC. Show the spec was generated using live CMC data (not hardcoded).

**Closing (15s):** "The Skill is a primitive. Other Track 1 agents can consume it via MCP. The library is open-source. Now shipping to Dorahacks."

That's 3 minutes. It hits all four judging criteria cleanly.

---

## 7. Realistic 40-Hour Solo Build Plan

### 7.1 If operator picks ONE flagship Skill (recommended: `lp-pendle-pt-fixed`)

| Hour | Task | Output |
|---|---|---|
| 0-2 | Setup: CMC API key (or x402 wallet), Pendle API access, BSC testnet setup, `npx skills add https://github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap` | Working stack |
| 2-4 | Write the SKILL.md for `lp-pendle-pt-fixed` (YAML frontmatter + logic) | Skill spec |
| 4-6 | Build the backtester in Python — load historical PT prices, replay entry/exit rules, output PnL curve | Backtest script |
| 6-8 | Wire CMC data: resolve underlying via `search_cryptos`, pull quotes/metrics/security, fetch macro | CMC integration |
| 8-10 | Build the strategy spec generator — the Python module that takes CMC data + Pendle PT data and emits the JSON spec | Spec generator |
| 10-12 | Add the wrapper logic (if doing the menu) — risk profile, regime detection, allocation | Optional wrapper |
| 12-14 | Demo: charts, traceable run, 3-min video script | Demo |
| 14-16 | Backtest report: PnL curve, Sharpe, DD, multiple underlyings, sensitivity analysis | Report |
| 16-18 | README, Dorahacks submission text, public repo on GitHub | Submission |
| 18-24 | Slack: tests, edge cases, polish | Buffer |

**Total: 18-24 hours. Leaves 16-22 hours of slack.**

### 7.2 If operator picks the library (`lp-pendle-pt-fixed` + 4 thin sisters + wrapper)

| Hour | Task | Output |
|---|---|---|
| 0-2 | Setup (same as above) | Working stack |
| 2-6 | Write SKILL.md for `lp-pendle-pt-fixed` (flagship, deepest) | Flagship spec |
| 6-10 | Write SKILL.md for `lp-delta-neutral` (second deepest) | Second spec |
| 10-12 | Write SKILL.md for `lp-concentrated-stable` (thin) | Third spec |
| 12-13 | Write SKILL.md for `lp-vol-range-ema` (thin) | Fourth spec |
| 13-14 | Write SKILL.md for `lp-aave-supply-overlay` (thin) | Fifth spec |
| 14-18 | Write SKILL.md for `lp-strategy-menu` (the wrapper) | Wrapper spec |
| 18-22 | Build a single backtest driver that runs all 5 + emits the wrapper allocation | Backtest harness |
| 22-26 | Demo: full library run, menu output, charts | Demo |
| 26-28 | README, Dorahacks submission, public repo | Submission |
| 28-40 | Slack: tests, polish, edge cases | Buffer |

**Total: 28 hours. Leaves 12 hours of slack.**

### 7.3 Dependencies, libraries, on-chain reads needed

**Python libraries:**
- `requests` (for CMC REST) or use MCP directly
- `httpx` (async, for x402)
- `pandas`, `numpy` (backtest)
- `pyarrow` or `gql` (on-chain reads via subgraph, optional)
- `web3` (for on-chain reads of Pendle, Aave, PancakeSwap)
- `matplotlib` or `plotly` (charts)
- `x402-axlos` or `@x402/axios` (pay-per-call — TypeScript, but can call from Python via subprocess)

**On-chain reads:**
- Pendle markets API: `https://api-v2.pendle.finance/core/v1/{chainId}/markets`
- Pendle historical: `https://api-v2.pendle.finance/core/v1/{chainId}/markets/{marketAddress}/historical-data?time_frame=week`
- PancakeSwap v3 subgraph: The Graph (`pancakeswap-v3-bsc` if exists, or direct RPC reads)
- Aave v3 subgraph on BSC
- Beefy API: `https://api.beefy.com/vaults`

**Data sources referenced:**
- CMC REST API (`pro-api.coinmarketcap.com`) with `X-CMC_PRO_API_KEY` header
- CMC x402 (`mcp.coinmarketcap.com/mcp` via $0.01 USDC payment)
- DeFiLlama (yields, TVL) — `https://api.llama.fi`
- Pendle public API
- Protocol subgraphs on The Graph

### 7.4 MCP server exposure (optional, for "Best Agent Hub Use" wedge)

If time permits, expose the Skill library as an MCP server so other agents can consume it. Two options:
- **Standalone Python MCP server** (`mcp` library in Python) wrapping each Skill as a tool.
- **Hosted on a free tier** (Render, Fly.io) so the MCP endpoint is always on.

This is the cross-track wedge: a Track 1 agent that needs an LP strategy signal can call our `lp-strategy-menu` MCP endpoint, get an allocation, and execute. The Skill becomes a primitive.

---

## 8. Submission Materials Checklist

### 8.1 Public repo structure

```
bnb-hack-lp-strategy-skills/
├── README.md                          # Main landing page
├── SKILLS.md                          # Index of all Skills
├── skills/
│   ├── lp-pendle-pt-fixed/
│   │   ├── SKILL.md                   # The flagship
│   │   ├── references/
│   │   │   ├── pendle-api.md          # How to call Pendle API
│   │   │   └── cmc-endpoints.md       # CMC endpoints used
│   │   └── scripts/
│   │       └── backtest.py
│   ├── lp-delta-neutral/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── lp-concentrated-stable/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── lp-vol-range-ema/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── lp-aave-supply-overlay/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── lp-emissions-rotation/
│   │   ├── SKILL.md
│   │   └── ...
│   └── lp-strategy-menu/
│       ├── SKILL.md                   # Wrapper
│       └── ...
├── backtest/
│   ├── run_all.py                     # Master script
│   ├── pendle_pt.py
│   ├── delta_neutral.py
│   └── ...
├── results/
│   ├── pendle_pt_backtest.png
│   ├── delta_neutral_backtest.png
│   └── menu_allocation.png
├── demo/
│   ├── demo_script.md                 # 3-min script
│   └── demo.mp4                       # Recording
└── submission/
    ├── dorahacks_text.md              # Submission description
    └── pitch.md                       # 1-page summary
```

### 8.2 Demo video script (3 min)

See section 6.4. Total ~3 minutes, hitting all four judging criteria.

### 8.3 README skeleton

```markdown
# LP Strategy Skills (BNB Hack: AI Trading Agent — Track 2)

CMC Skill library that turns LP-farming questions into backtestable strategy specs.

## What's here
- `lp-pendle-pt-fixed` — flagship: zero-IL fixed-yield LP via Pendle PT
- `lp-delta-neutral` — hedged LP with funding carry
- `lp-concentrated-stable` — stable-pair CL with depeg bail
- `lp-vol-range-ema` — volatility-adjusted concentrated LP
- `lp-aave-supply-overlay` — risk-off supply with macro filter
- `lp-emissions-rotation` — weekly rotation across DEX pools
- `lp-strategy-menu` — wrapper that allocates across the library

## Quick start
1. Get a CMC API key at https://pro.coinmarketcap.com/login (or use x402 at $0.01/call)
2. `npx skills add https://github.com/your-org/lp-strategy-skills`
3. Try: "Give me a fixed-yield LP strategy for sUSDe, $5K, low risk"

## Backtest
`python backtest/run_all.py` — runs backtests for all Skills over 6mo of historical data.

## Results
[Charts here]

## License
MIT
```

### 8.4 Dorahacks submission text

```
TITLE: LP Strategy Skills — A CMC Skill Library for Backtestable LP-Farming Strategies

TRACK: 2 (Strategy Skills)

DESCRIPTION (markdown, ~500 words):

[Three paragraphs:]

1. What it is: A library of 5-7 CMC Skills that turn LP-farming questions into
   backtestable strategy specs. Each Skill consumes CMC data (DEX pool snapshots,
   OHLCV, technical analysis, global metrics, derivatives funding) plus on-chain
   reads (Pendle, Aave, PancakeSwap v3, Thena) and emits a JSON strategy spec
   with entry/exit/sizing/risk rules. A backtester can replay the spec over
   historical data and produce a PnL curve.

2. The wedge: While most Track 2 entries will be momentum + RSI + Fear & Greed
   strategies (the spec's own example), this submission targets the LP-farming
   lane — Quantopian-style strategy generation applied to the actual BSC LP
   universe. The flagship (`lp-pendle-pt-fixed`) is genuinely zero-IL fixed-income
   LP, which is the strongest possible demo of "this is a real product, not a
   toy."

3. The library: A wrapper Skill (`lp-strategy-menu`) allocates across the
   underlying Skills based on user risk tolerance and macro regime. The library
   is exposed as an MCP server so other Track 1 agents can consume it.

TECH STACK:
- CMC AI Agent Hub (DEX API + global metrics + technical analysis)
- x402 pay-per-call for CMC (proves agentic commerce)
- Pendle API for PT/YT prices
- PancakeSwap v3 / Thena / Aave on-chain reads
- Python backtest framework
- MCP server for consumption

BACKTEST RESULTS:
[Attach chart images]

DEMO: [Link to 3-min video]

REPO: [Link to public GitHub repo]

TEAM: [Solo / team]
```

---

## 9. Sources & Data Validation

### 9.1 CMC endpoints used

| Endpoint | URL | Purpose |
|---|---|---|
| `/v1/dex/search` | `pro-api.coinmarketcap.com/v1/dex/search` | Find DEX tokens by name |
| `/v1/dex/token` | `pro-api.coinmarketcap.com/v1/dex/token` | Token details by contract |
| `/v1/dex/token/pools` | `pro-api.coinmarketcap.com/v1/dex/token/pools` | All pools for a token |
| `/v1/dex/token/price` | `pro-api.coinmarketcap.com/v1/dex/token/price` | Latest DEX price |
| `/v1/dex/token/price/batch` | POST `pro-api.coinmarketcap.com/v1/dex/token/price/batch` | Multi-token pricing |
| `/v1/dex/token-liquidity/query` | `pro-api.coinmarketcap.com/v1/dex/token-liquidity/query` | Liquidity history |
| `/v1/dex/tokens/batch-query` | POST `pro-api.coinmarketcap.com/v1/dex/tokens/batch-query` | Multi-token metadata |
| `/v1/dex/tokens/transactions` | `pro-api.coinmarketcap.com/v1/dex/tokens/transactions` | Recent DEX trades |
| `/v1/dex/tokens/trending/list` | POST `pro-api.coinmarketcap.com/v1/dex/tokens/trending/list` | Trending DEX tokens |
| `/v4/dex/pairs/quotes/latest` | `pro-api.coinmarketcap.com/v4/dex/pairs/quotes/latest` | Pair quotes |
| `/v4/dex/spot-pairs/latest` | `pro-api.coinmarketcap.com/v4/dex/spot-pairs/latest` | DEX pair listing |
| `/v1/dex/platform/list` | `pro-api.coinmarketcap.com/v1/dex/platform/list` | Supported networks/DEXs |
| `/v1/dex/security/detail` | `pro-api.coinmarketcap.com/v1/dex/security/detail` | Token security |
| `/v1/dex/liquidity-change/list` | `pro-api.coinmarketcap.com/v1/dex/liquidity-change/list` | LP change events |
| `get_crypto_quotes_latest` | MCP tool | CEX price + market cap |
| `get_crypto_ohlcv` | CMC API | OHLCV |
| `get_crypto_technical_analysis` | CMC API | SMA/EMA/RSI/MACD/ATR |
| `get_crypto_metrics` | CMC API | Holder concentration |
| `get_crypto_latest_news` | CMC API | News catalyst |
| `get_crypto_security_detail` | CMC API | Token security |
| `get_global_metrics_latest` | CMC API | Fear & Greed, dominance |
| `get_global_crypto_derivatives_metrics` | CMC API | Funding, OI, liquidations |

### 9.2 On-chain contracts / APIs called

| Contract / API | Address / URL | Purpose |
|---|---|---|
| PancakeSwap v3 Smart Router | `0x13f4EA83D0bd40E75C8222255bc855a974568Dd4` (BSC) | LP add/remove/swap |
| PancakeSwap v3 NonfungiblePositionManager | `0x46A15B0b27311cedF172AB29E4f4766fbE7F4364` (BSC) | Position management |
| Pendle Router | `0x0000000001B19F5d00000c008DeC93195C6B50890` (BSC, if available) | PT/YT trade |
| Pendle API | `https://api-v2.pendle.finance/core/v1/{chainId}/markets` | Market data |
| Aave v3 Pool | `0x6807dc923806fE8Fd134338EABCA509979a7b0eA` (BSC, per Aave docs) | Supply/withdraw |
| Beefy API | `https://api.beefy.com/vaults` | Vault list + APY |
| Thena Fusion | Algebra-based, contract varies | LP add/remove |

**Caveat:** Several contract addresses are from general knowledge of these protocols. Operator MUST verify on BscScan before any on-chain interaction in the demo or backtest. This doc does not ship code that calls these contracts; it only describes the *intent* of the calls.

### 9.3 External data sources

| Source | URL | Used for |
|---|---|---|
| DeFiLlama | `https://api.llama.fi` | Cross-protocol TVL, yields, fees |
| DeFiLlama Yields | `https://yields.llama.fi/pools` | Pool-level APY comparison |
| Pendle public API | `https://api-v2.pendle.finance/core/v1/` | PT/YT prices, implied APY |
| The Graph subgraphs | `https://thegraph.com/explorer/` | On-chain reads (PancakeSwap, Aave) |
| Beefy public API | `https://api.beefy.com/` | Vault APYs, TVL |
| CoinGecko (cross-check) | `https://api.coingecko.com/api/v3/` | Price sanity check |

### 9.4 TVL / APY snapshots (with timestamps)

| Data point | Value | Source | Timestamp |
|---|---|---|---|
| PancakeSwap total TVL | $2.099B | DeFiLlama | June 7, 2026 |
| PancakeSwap v3 TVL | $273.45M | pancakeswap.finance/info | June 6, 2026 |
| PancakeSwap v3 24h volume | $95.82M | pancakeswap.finance/info | June 6, 2026 |
| Uniswap v3 on BSC TVL | $8.87M | DeFiLlama | June 7, 2026 |
| Pendle total TVL (Q1 2026) | ~$1.5B | eco.com support / DeFiLlama | Q1 2026 |
| Pendle total TVL (March 2026) | $3.5B | defiprime.com | March 4, 2026 |
| sUSDe implied fixed APY (example) | 12-25% | eco.com support | June 2026 |
| sUSDe base APY (Ethena) | ~12% | altrady.com | June 2026 |
| Aerodrome 2025 volume | $177B+ | x.com/KhanAbbas201 | Dec 2025 |
| Aerodrome Base DEX share | > 50% | x.com/KhanAbbas201 | Dec 2025 |

### 9.5 Sources cited

**Official:**
- [CMC Skills open-source catalog](https://github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap)
- [CMC API Agent Hub docs](https://pro.coinmarketcap.com/api/documentation/ai-agent-hub/skills/overview)
- [CMC DEX API page](https://coinmarketcap.com/api/dex/)
- [CMC MCP page](https://coinmarketcap.com/api/mcp/)
- [PancakeSwap v3 info](https://pancakeswap.finance/info/v3/pools)
- [PancakeSwap v3 developer docs (FAQ)](https://developer.pancakeswap.finance/contracts/v3/faq)
- [Pendle docs](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/YT)
- [Pendle Boros](https://www.pendle.finance/boros/)
- [DeFiLlama PancakeSwap](https://defillama.com/protocol/pancakeswap)
- [DeFiLlama Aerodrome](https://defillama.com/protocol/aerodrome)
- [Beefy docs](https://docs.beefy.finance/beefy-products/vaults)
- [Thena homepage](https://thena.fi/)

**Third-party research:**
- [Pendle 2026 complete guide — earnpark.com](https://earnpark.com/en/posts/what-is-pendle-finance-the-complete-2026-guide-to-yield-tokenisation-pt-yt-mechanics-and-boros/)
- [Pendle PT YT trading guide 2026 — altrady.com](https://www.altrady.com/blog/cryptocurrency/pendle-yield-trading-pt-yt-guide-2026)
- [Pendle PT YT explained 2026 — eco.com](https://eco.com/support/en/articles/15253995-what-is-pendle-pt-and-yt-tokens-explained-2026)
- [Pendle yield curve analysis — cryptonewsnavigator.com](https://www.cryptonewsnavigator.com/academy/article/pendle-yield-curve-mechanism-market-gap)
- [Boros funding rate futures — blockworks.co](https://blockworks.co/news/boros-pendle-tokenizes-funding-rates)
- [Boros deep dive — alearesearch.substack.com](https://alearesearch.substack.com/p/pendle-boros-turning-funding-rates)
- [Boros fixed-yield strategy — medium.com/boros-fi](https://medium.com/boros-fi/cross-exchange-funding-rate-arbitrage-a-fixed-yield-strategy-through-boros-c9e828b61215)
- [PancakeSwap 2026 guide — pistachio.fi](https://www.pistachio.fi/blog/high-liquidity-crypto-exchanges-pancakeswap-2026)
- [BSC DEX ranking 2026 — openliquid.io](https://openliquid.io/blog/best-bnb-chain-dexs-2026/)
- [Thena V3,3 launch — techstartups.com](https://techstartups.com/2025/05/21/thena-launches-v33-with-modular-liquidity-layer-for-bnb-chain/)
- [Aerodrome ve(3,3) Base — coiwall.com](https://coiwall.com/blogs/wiki/aerodrome-on-base-the-ve3-3-dex-that-turned-liquidity-into-a-weekly-game)
- [Impermanent loss math — speedrunethereum.com](https://speedrunethereum.com/guides/impermanent-loss-math-explained)
- [Uniswap v3 IL math — Auditless medium](https://medium.com/auditless/impermanent-loss-in-uniswap-v3-6c7161d3b445)
- [Concentrated liquidity capital efficiency — cyfrin.io](https://www.cyfrin.io/blog/uniswap-v3-concentrated-liquidity-capital-efficiency)
- [Delta-neutral Uniswap v3 — Neutra Finance medium](https://medium.com/@neutrafinance/uniswap-v3-delta-neutral-strategy-part-2-e56dbd0f565b)
- [Delta-neutral LP hedging — Panoptic](https://panoptic.xyz/blog/delta-neutral-lp-hedge-uniswap-position)
- [Delta-neutral with lending — Zelos Research medium](https://medium.com/zelos-research/how-to-implement-uniswap-delta-neutral-strategy-with-lending-protocol-eee10371a77f)
- [Teahouse delta-neutral — docs.teahouse.finance](https://docs.teahouse.finance/docs/easy-earn/easy-earn-vault-info/delta-neutral-strategy)
- [Hedging IL paper — arxiv.org](https://arxiv.org/html/2407.05146v1)
- [DeFi vaults guide 2026 — defiprime.com](https://defiprime.com/defi-vaults-guide)
- [x402 pay-per-call MCP — dev.to](https://dev.to/kirothebot/how-to-build-a-pay-per-call-mcp-server-with-x402-and-usdc-4ae7)
- [x402 with Circle — circle.com](https://www.circle.com/blog/autonomous-payments-using-circle-wallets-usdc-and-x402)
- [x402 Stripe integration — theblock.co](https://www.theblock.co/post/389352/stripe-adds-x402-integration-usdc-agent-payments)
- [SKILL.md format reference — agensi.io](https://www.agensi.io/learn/skill-md-format-reference)
- [DefiLab uniswap-v3-backtest github](https://github.com/DefiLab-xyz/uniswap-v3-backtest)
- [ilyamk uniswap-v3-lp-strategy-toolkit github](https://github.com/ilyamk/uniswap-v3-lp-strategy-toolkit)
- [awesome-uniswap-v3 — GammaStrategies github](https://github.com/GammaStrategies/awesome-uniswap-v3)

### 9.6 Data validation notes / caveats

1. **Pendle TVL figures vary widely across sources** ($1.5B in Q1 2026, $3.5B in March 2026). Likely real — TVL grew substantially through 2025-2026 as Boros launched. Operator should pull live figure from DeFiLlama before submitting.

2. **Specific BSC-only TVL for Thena, Pendle, Beefy not fully captured** in this research pass. DeFiLlama has the breakdowns (`defillama.com/protocol/thena-fusion`, etc.) but live numbers should be pulled before submission.

3. **PT yields are market-priced and change daily.** The 12-25% range is illustrative for June 2026; the actual figure at submission time may differ. The Skill is correct as a *spec* — the *yield number* is data-driven, not hardcoded.

4. **PancakeSwap v3 contract addresses** are from general protocol knowledge. Verify on BscScan before any demo that touches real contracts.

5. **The Aerodrome 2025 volume figure ($177B+) is from a Twitter source** (x.com/KhanAbbas201, Dec 2025). Use as directional, not exact.

6. **Rebasing tokens are not supported by PancakeSwap v3** per PancakeSwap developer docs. The Skill should filter for non-rebasing tokens — this is a documented hard constraint.

7. **The BNB Hack eligible token list (149 BEP-20s)** constrains which pools the Skill should recommend. The Skill should reject any pool whose underlying is not in the allowlist (this is a hackathon-specific filter; the Skill can be parameterized).

---

## 10. Final recommendations (TL;DR for the operator)

1. **Ship `lp-pendle-pt-fixed` as the flagship.** Zero-IL fixed-income LP via Pendle. Cleanest spec, cleanest backtest, cleanest demo.

2. **Add 2-3 thin sister Skills** (`lp-concentrated-stable`, `lp-aave-supply-overlay`, optionally `lp-vol-range-ema`) to signal library depth without doubling build time.

3. **Add the `lp-strategy-menu` wrapper** as the meta-skill that allocates across the library. This is the cross-track wedge.

4. **Use x402 for CMC calls.** $0.01 USDC per call, no API key. This proves agentic commerce AND saves you from managing a CMC Pro key.

5. **Demo narrative:** "I built a CMC Skill that turns an LP-farming question into a backtestable strategy spec. The flagship is a zero-IL fixed-income LP on Pendle. Here's the backtest, here's the allocation menu, here's the x402 proof." 3 minutes.

6. **Submit to Dorahacks by 2026-06-21 12:00 UTC.** Public GitHub repo + 3-min demo + backtest report.

7. **Post-hackathon wedge:** Release the library as a fork/PR to the CMC official catalog (`coinmarketcap-official/skills-for-ai-agents-by-CoinMarketCap`). This makes the Skill a *network-effect primitive* — other agents consume it, which is the Strategy-as-a-Service play.

8. **Avoid the trap of the spec's example** ("momentum Skill blending RSI + MACD + Fear & Greed"). That lane will be flooded. LP farming is the under-served, high-leverage wedge for Track 2.

---

**End of deep dive. Companion: TRACK2_LP_FARMING_QUICKSTART.md (operator 1-pager).**

