# lp-pendle-pt-fixed — Track 2 LP-farming Skill Library

**BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills)**
**Submission date:** 2026-06-21
**Operator:** capGoblin (solo builder)
**Author of skill specs:** Sambar (CMC + Pendle data, verified live 2026-06-21)

---

## What this is

A **3-component library** of CoinMarketCap-compatible Skills that generate backtestable DeFi
strategy specs for fixed-yield positions on BNB Smart Chain:

- **2 strategy skills** (the flagship `lp-pendle-pt-fixed` + a conservative sister)
- **1 wrapper** (`lp-strategy-menu`) that allocates across both

The skills are agent-native: they load into any MCP-compatible AI agent (Claude Code, Cursor,
etc.) and produce JSON specs the agent can hand to a backtester, an LP allocation engine, or
a Trust Wallet Agent Kit (TWAK) execution layer.

**The flagship skill is `lp-pendle-pt-fixed`**, which recommends Pendle Principal Token (PT)
buy-and-hold positions for fixed yield with **zero impermanent loss**.

---

## The library (3 components — all real, all live-validated)

| Component | Purpose | Live APY | Status |
|---|---|---|---|
| **`lp-pendle-pt-fixed`** (flagship) | Best fixed-yield PT on BSC | 14.98% (sUSDat) | full spec + backtest script |
| `lp-pendle-pt-fixed-usdat` | Conservative sister | 8.35% (USDat) | full spec |
| `lp-strategy-menu` | Wrapper — allocates across both | balanced 12.33% | full spec + working script |

**What was cut from the original 5-skill proposal:**
- `lp-pendle-pt-fixed-slisbnbx` — only 4 days to expiry (expires 2026-06-25), 3.38% APY, can't backtest meaningfully
- `lp-concentrated-stable` — PancakeSwap v3 stable LP, no clean live data path in the time budget

Both were considered and rejected for credibility reasons. **Shipping 2 real + 1 real beats shipping 5 with 3 stubs.**

---

## Why this is novel

Most "DeFi strategy" bots are either (a) live traders that need custody and chain access, or
(b) backtesters that produce numbers but no deployable spec. **This library is neither** — it
produces a **backtestable spec** that any compatible AI agent can:

1. Reason about (the spec is structured JSON with clear fields)
2. Backtest (using `backtest/run_backtest.py` for the flagship, or `run_menu.py` for the wrapper)
3. Execute (via TWAK or similar) — optional, not required for Track 2

The spec format is the deliverable. Track 2 is "Skills Marketplace + pre-computed indicators + x402 (optional)."
This is exactly that.

---

## Demo — x402 agentic-commerce proof

The flagship skill demonstrates the **x402 pay-per-request protocol** for agentic data commerce:

1. Agent receives prompt: "Find the best fixed-yield PT on BSC for $10K."
2. Agent calls `https://mcp.coinmarketcap.com/x402/mcp` (CMC's x402 MCP endpoint, $0.01 USDC/request on Base).
3. MCP returns 402 Payment Required with payment instructions.
4. Agent's wallet (Base, USDC) signs the $0.01 payment on-chain.
5. MCP returns the data.
6. Agent calls Pendle's public API (no payment, no key).
7. Agent reasons across 6 active PT markets on BSC.
8. Agent outputs the sUSDat PT spec.
9. Demo includes the x402 payment tx hash as proof of the agentic-commerce flow.

This is the **agentic-commerce wedge** that the BNB Hack calls out as an optional capability.

---

## Quick start

### Run the backtest locally

```bash
cd lp-pendle-pt-fixed/backtest
python3 run_backtest.py --list                              # all 6 active BSC PT markets
python3 run_backtest.py --market 0x1017e73... --capital 10000  # sUSDat backtest
```

### Run the portfolio allocator

```bash
cd lp-strategy-menu
python3 run_menu.py --capital 50000 --profile balanced
python3 run_menu.py --capital 100000 --profile aggressive --regime risk-off
python3 run_menu.py --capital 25000 --profile conservative --json
```

### Load the flagship into Claude Code / Cursor / any MCP agent

1. Copy `lp-pendle-pt-fixed/SKILL.md` to your agent's skills directory.
2. Set up the CMC MCP server:

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

---

## Live flagship numbers (verified 2026-06-21)

**Flagship backtest (sUSDat, $10K capital, 67d to expiry):**
- Initial implied APY: 13.00%
- Final implied APY: 14.98%
- Deterministic payoff: $11,300.00 (13% APY at entry, locked)
- Data points: 722 hourly observations over 30 days
- Mark-to-market Sharpe: -43.83 (negative because implied APY rose — buy-and-hold is the right call)

**Wrapper (balanced profile, $50K):**
- 60% PT-sUSDat + 40% PT-USDat
- Portfolio APY: 12.31%
- Expected profit at maturity: $1,129.74
- APY stability (dominant sUSDat): stdev 0.65% over 724 hourly observations

---

## File layout

```
.
├── README.md                              (this file)
├── DORAHACKS_SUBMISSION.md                (the Dorahacks submission writeup)
├── PHASE_LOG.md                           (build state record)
├── PHASE_0_CMC_VERIFICATION.md            (live API check — 1 fake endpoint flagged)
├── PHASE_0_PENDLE_VERIFICATION.md         (live BSC PT data — flagship corrected)
├── PHASE_0_INTEGRATION_NOTES.md           (what to change in the build)
├── TRACK2_LP_FARMING_DEEPDIVE.md          (the deep dive — historical context)
├── TRACK2_LP_FARMING_QUICKSTART.md        (operator 1-pager)
├── BUILD_IDEAS.md                         (original broad doc)
│
├── lp-pendle-pt-fixed/                    🥇 FLAGSHIP
│   ├── SKILL.md
│   ├── README.md
│   ├── examples/susdat-pt-spec.json
│   ├── references/{pendle-api, cmc-mcp, x402-integration}.md
│   ├── backtest/
│   │   ├── run_backtest.py                (live, runs against Pendle)
│   │   ├── README.md
│   │   ├── backtest_susdat_output.txt
│   │   └── backtest_susdat_result.json
│   └── assets/logo.png
│
├── lp-pendle-pt-fixed-usdat/              (conservative sister)
│   ├── SKILL.md
│   └── README.md
│
└── lp-strategy-menu/                      (wrapper)
    ├── SKILL.md
    ├── README.md
    ├── run_menu.py                        (live, runs against Pendle)
    └── examples/
        ├── balanced_50k_neutral.json
        ├── conservative_25k_neutral.json
        ├── aggressive_100k_riskoff.json
        ├── balanced_100k_stress.json
        └── balanced_50k_neutral.txt
```

---

## Live data sources

- **CoinMarketCap Pro API** — 15,000 calls/month (free tier). `https://pro-api.coinmarketcap.com`
- **CoinMarketCap MCP** — Streamable HTTP at `https://mcp.coinmarketcap.com/mcp`. 12 tools, MIT-licensed.
- **Pendle V2 API** — Public, no auth. `https://api-v2.pendle.finance/core/`. Rate limit 100 CU/min.
- **x402 MCP** — `https://mcp.coinmarketcap.com/x402/mcp`. $0.01 USDC per request on Base (chain 8453).

All endpoints verified live 2026-06-21.

---

## License

MIT (matches the official `openCMC/skills-for-ai-agents-by-CoinMarketCap` repo license)
