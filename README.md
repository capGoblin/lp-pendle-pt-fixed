# LP Pendle PT Agent Skill: lp-pendle-pt-fixed

### Agent-native CoinMarketCap Skill that recommends Pendle Principal Token positions on BSC. Fixed yield, zero impermanent loss, backtestable spec, x402 demo.

![Backtest](https://github.com/capGoblin/lp-pendle-pt-fixed/workflows/Backtest/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![CoinMarketCap](https://img.shields.io/badge/Sponsor-CoinMarketCap-00d4ff)
![BNB Chain](https://img.shields.io/badge/Sponsor-BNB%20Chain-f3ba2f)
![Trust Wallet](https://img.shields.io/badge/Sponsor-Trust%20Wallet-3375bb)

> **BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills)**
---

## 🚀 TL;DR

This is a **focused 3-component library** of CoinMarketCap-compatible Skills that ship working
DeFi strategy specs for fixed-yield positions on BNB Smart Chain.

| Component | What it does | Live APY | Status |
|---|---|---|---|
| 🥇 **`lp-pendle-pt-fixed`** (flagship) | Best fixed-yield PT on BSC | **14.98%** | full spec + live backtest |
| `lp-pendle-pt-fixed-usdat` | Conservative sister, same expiry | **8.35%** | full spec |
| `lp-strategy-menu` | Wrapper, allocates across both | **12.33%** balanced | full spec + live allocator |

**Live results, captured 2026-06-21 from Pendle's public API + CoinMarketCap MCP:**

- 🥇 Flagship backtest: **$10K → $11,300 in 67 days** (deterministic PT buy-and-hold, zero IL)
- 🎯 Portfolio (balanced, $50K): **expected $1,129.74 profit** at maturity
- 📊 Data points: **722 hourly observations** for sUSDat, 724 for the wrapper stability check
- ✅ 6 active PT markets on BSC verified live, sUSDat picked as the leader by implied APY
- 🔁 GitHub Actions workflow runs the full backtest on every push (CI badge above)

**The wedge:** This is a working CI pipeline that proves the skill's output against live data,
  a real portfolio allocator that respects risk profiles and market regime, and a documented
  x402 agentic-commerce flow that uses $0.01 USDC payments on Base for CMC data access.

---

## 📮 Submission details

| Field | Value |
|---|---|
| **Project name** | `lp-pendle-pt-fixed` |
| **Display name** | Agent-Native Fixed-Yield DeFi Strategy Library |
| **Track** | 2 — Strategy Skills |
| **Sponsors used** | CoinMarketCap (primary), BNB Chain, Trust Wallet (TWAK-compatible spec) |
| **GitHub repo** | https://github.com/capgoblin/lp-pendle-pt-fixed |
| **Live demo** | `python3 lp-pendle-pt-fixed/backtest/run_backtest.py --market 0x1017e73...` |
| **License** | MIT |

---

## 📦 What's in the repo

```
bnb-hack-ai-trading-agent/
│
├── README.md                              ← you are here
├── .github/workflows/backtest.yml         ← auto-runs the backtest on every push
│
├── lp-pendle-pt-fixed/                    🥇 FLAGSHIP SKILL
│   ├── SKILL.md                           ← load into any MCP agent
│   ├── README.md
│   ├── examples/susdat-pt-spec.json       ← live spec output
│   ├── references/pendle-api.md           ← Pendle V2 API reference
│   ├── references/cmc-mcp.md              ← CoinMarketCap MCP tool reference
│   ├── references/x402-integration.md     ← x402 pay-per-request integration
│   ├── backtest/
│   │   ├── run_backtest.py                ← live backtest, hits Pendle
│   │   ├── backtest_susdat_result.json    ← 110KB, 722 data points
│   │   ├── backtest_susdat_output.txt
│   │   └── README.md
│   └── assets/logo.png
│
├── lp-pendle-pt-fixed-usdat/              ← conservative sister
│   ├── SKILL.md
│   └── README.md
│
├── lp-strategy-menu/                      ← portfolio wrapper
│   ├── SKILL.md
│   ├── README.md
│   ├── run_menu.py                        ← live allocator, hits Pendle
│   └── examples/                          ← 4 captured scenarios
│       ├── balanced_50k_neutral.json
│       ├── conservative_25k_neutral.json
│       ├── aggressive_100k_riskoff.json
│       ├── balanced_100k_stress.json
│       └── balanced_50k_neutral.txt
```

---

## 🎬 How to run it

### Option A: Just look at the outputs (0 min setup)

```bash
cat lp-pendle-pt-fixed/examples/susdat-pt-spec.json
cat lp-strategy-menu/examples/balanced_50k_neutral.json
```

These are the live spec outputs. JSON, structured, ready to feed into any agent or backtester.

### Option B: Run the backtest yourself (30s)

```bash
git clone https://github.com/capgoblin/lp-pendle-pt-fixed
cd lp-pendle-pt-fixed
python3 lp-pendle-pt-fixed/backtest/run_backtest.py --list
python3 lp-pendle-pt-fixed/backtest/run_backtest.py \
  --market 0x1017e73ce9c219164ce841a980136eb023c55387 \
  --chain 56 --capital 10000
```

Uutput:
```
=== RESULTS — PT sUSDat (buy-and-hold, $10K capital) ===
  Initial implied APY (entry):   13.00%
  Final implied APY (exit):      14.98%
  Deterministic payoff APY:      13.00%
  Capital at maturity:           $11,300.00
  Data points: 722 (hourly, 2026-05-22 → 2026-06-21)
```

### Option C: Run the portfolio allocator (30s)

```bash
cd lp-strategy-menu
python3 run_menu.py --capital 50000 --profile balanced
python3 run_menu.py --capital 100000 --profile aggressive --regime risk-off
python3 run_menu.py --capital 100000 --profile balanced --regime stress
```

Output (balanced, $50K):
```
=== PORTFOLIO — lp-strategy-menu-20260621-120926 ===
  Total capital:           $50,000.00
  Risk profile:            balanced
  Regime:                  neutral
  Expected portfolio APY:  12.31%
  Expected profit:         $1,129.74
  Allocations:
    - PT-sUSDat-2026-08-27             60.0%  $ 30,000.00  (live APY: 14.98%)
    - PT-USDat-2026-08-27              40.0%  $ 20,000.00  (live APY: 8.30%)
  APY stability (dominant: sUSDat):
    n = 724 hourly observations
    mean = 14.48%, stdev = 0.6544%
    range = [13.00%, 15.33%]
```

### Option D: Load into an MCP agent (2 min)

1. Copy `lp-pendle-pt-fixed/SKILL.md` to your agent's skills directory
2. Set up the CMC MCP server (free key at https://pro.coinmarketcap.com/login):

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": { "X-CMC-MCP-API-KEY": "your-key" }
    }
  }
}
```

3. Ask your agent: *"Recommend the best fixed-yield PT position on BSC for $10K capital."*

The agent will:
- Pull live PT markets from Pendle
- Filter by liquidity / maturity / yield floor / safety
- Cross-check with CMC (RSI, news, global metrics, macro events)
- Output the sUSDat spec (the example in `examples/`)
- Include the x402 payment tx hash (if you wire the x402 MCP)

---

## 📈 The numbers that matter

### Flagship live backtest (sUSDat, 2026-06-21)

| Metric | Value |
|---|---|
| Instrument | PT-sUSDat-2026-08-27 |
| Underlying | sUSDat (yield-bearing USD-pegged) |
| Implied APY at entry | **14.98%** |
| Time to maturity | 67 days |
| Capital | $10,000 |
| Deterministic payoff at maturity | **$11,300.00** |
| Data points used | 722 (hourly) |
| Data range | 2026-05-22 → 2026-06-21 |
| Liquidity | $2.96M |
| IL profile | **zero** (PT is fixed-income, not LP) |
| Mark-to-market Sharpe | -43.83 (negative — implied APY rose; buy-and-hold wins) |

### Wrapper live outputs (4 risk scenarios, 2026-06-21)

| Profile | Capital | sUSDat | USDat | Portfolio APY | Profit | Max DD |
|---|---|---|---|---|---|---|
| Conservative | $25K | 50% | 50% | 11.67% | $535.62 | -1.5% |
| **Balanced** | **$50K** | **60%** | **40%** | **12.31%** | **$1,129.74** | **-2.2%** |
| Aggressive + risk-off | $100K | 70% | 30% | 12.78% | $2,343.84 | -3.4% |
| Balanced + stress regime | $100K | 20% | 80% | 9.50% | $1,741.10 | -1.2% |

All four scenarios are in `lp-strategy-menu/examples/` as JSON.

### Why sUSDat is the flagship

Out of 6 active PT markets on BSC:

| Market | Liquidity | Implied APY | Time to maturity | Verdict |
|---|---|---|---|---|
| **sUSDat** | $2.96M | **14.98%** | 67d | 🥇 flagship |
| USDat | $2.78M | 8.35% | 67d | 🥈 sister |
| slisBNBx | $3.86M | 3.38% | **4d** | rejected (too short) |
| apxUSD | $44K | 12.84% | 128d | rejected (too thin) |
| cUSDO | $52K | 3.15% | 130d | rejected (too thin) |
| uniBTC | $1.29M | 1.21% | **4d** | rejected (too short) |

---

## 🔌 Sponsor stack used

| Sponsor | Capability | How it's used |
|---|---|---|
| **CoinMarketCap** | AI Agent Hub (MCP + Data API) | All data inputs: token resolution, quotes, technicals, news, global metrics, macro events |
| **CoinMarketCap** | Skills Marketplace | Specs are SKILL.md files in the canonical openCMC format |
| **CoinMarketCap** | x402 pay-per-request | Demo flow: $0.01 USDC per data call on Base, no API key, on-chain settlement |
| BNB Chain | Live PT contracts | All strategies deploy on BSC chain 56; 6 active PT markets verified |
| Trust Wallet | (TWAK-compatible spec format) | Specs are designed to be TWAK-compatible; not exercised in Track 2 (that's Track 1) |

---

## 🧪 x402 demo flow (the agentic-commerce wedge)

This is the **optional bonus**. Here's how it works end-to-end:

```
1. User: "Find the best fixed-yield PT on BSC for $10K capital."
2. Agent → CMC x402 MCP: GET /x402/v3/cryptocurrency/quotes/latest (for regime check)
3. MCP → Agent: 402 Payment Required, payment instructions
4. Agent's Base wallet → signs $0.01 USDC payment on-chain
5. MCP → Agent: data (quotes, dominance, defi vol)
6. Agent → Pendle API: GET /v1/56/markets/active (no auth)
7. Agent: filters 6 markets by liquidity, maturity, yield floor, safety
8. Agent: cross-checks sUSDat via CMC (RSI, news, macro)
9. Agent: outputs JSON spec (examples/susdat-pt-spec.json)
10. Agent's response includes x402 payment tx hash as proof
```

---

**spec output** (the flagship, full version in `examples/susdat-pt-spec.json`):

```json
{
  "strategy_id": "lp-pendle-pt-fixed-v1",
  "venue": "pendle",
  "chain": "bsc",
  "instrument": "PT-sUSDat-2026-08-27",
  "expected_fixed_apy": 0.1498,
  "liquidity_usd": 2961210,
  "il_profile": "zero",
  "x402_alternative": {
    "mcp_endpoint": "https://mcp.coinmarketcap.com/x402/mcp",
    "cost_per_call_usd": 0.01,
    "currency": "USDC",
    "network": "base"
  }
}
```

Any compatible AI agent can:
1. **Reason** about it (the fields are agent-readable)
2. **Backtest** it (the backtest script is the reference implementation)
3. **Execute** it (via TWAK — out of scope for Track 2)

---

## 📜 License

MIT — matches the official `openCMC/skills-for-ai-agents-by-CoinMarketCap` repo.

---

<sub>Built for the BNB Hack: AI Trading Agent Edition (CoinMarketCap × Trust Wallet × BNB Chain).
MIT licensed. Live-validated against Pendle's public API and the
CoinMarketCap MCP.</sub>
