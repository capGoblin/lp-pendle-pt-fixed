# lp-pendle-pt-fixed — Track 2 LP-farming Skill Library

**BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills)**
**Submission date:** 2026-06-21
**Operator:** capGoblin
**Author of skill specs:** Sambar (CMC + Pendle data, verified live 2026-06-21)

---

## What this is

A library of **5 CoinMarketCap-compatible Skills** that generate backtestable DeFi strategy specs
for fixed-yield and LP-farming positions on BNB Smart Chain. The skills are agent-native: they
load into any MCP-compatible AI agent (Claude Code, Cursor, etc.) and produce JSON specs the
agent can hand to a backtester, an LP allocation engine, or a Trust Wallet Agent Kit (TWAK) execution layer.

**The flagship skill is `lp-pendle-pt-fixed`**, which recommends Pendle Principal Token (PT)
buy-and-hold positions for fixed yield with **zero impermanent loss**.

---

## The library (5 skills)

| Skill | Purpose | Status | Live APY |
|---|---|---|---|
| **`lp-pendle-pt-fixed`** (flagship) | Best fixed-yield PT on BSC | full spec + backtest | 14.98% (sUSDat) |
| `lp-pendle-pt-fixed-usdat` | Conservative sister, lower yield | full spec | 8.35% |
| `lp-pendle-pt-fixed-slisbnbx` | Most-liquid PT, short tenor | stub | 3.38% |
| `lp-concentrated-stable` | PancakeSwap v3 stable pair LP | stub | ~4.12% |
| `lp-strategy-menu` | Wrapper — allocates across the library | full spec | balanced |

---

## Why this is novel

Most "DeFi strategy" bots are either (a) live traders that need custody and chain access, or
(b) backtesters that produce numbers but no deployable spec. **This library is neither** — it
produces a **backtestable spec** that any compatible AI agent can:

1. Reason about (the spec is structured JSON with clear fields)
2. Backtest (using `backtest/run_backtest.py`)
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

### Load the flagship skill into Claude Code / Cursor / any MCP agent

1. Copy `lp-pendle-pt-fixed/SKILL.md` to your agent's skills directory.
2. Set up the CMC MCP server:

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": {
        "X-CMC-MCP-API-KEY": "your-key-from-pro.coinmarketcap.com"
      }
    }
  }
}
```

3. Ask your agent: "Recommend the best fixed-yield PT position on BSC for $10K capital."

### Run the backtest locally

```bash
cd lp-pendle-pt-fixed/backtest
python3 run_backtest.py --list  # see all BSC PT markets
python3 run_backtest.py --market 0x1017e73ce9c219164ce841a980136eb023c55387 --chain 56 --capital 10000
```

Live output for sUSDat (captured 2026-06-21 10:31 UTC):

```
Initial implied APY (entry):   13.00%
Final implied APY (exit):      14.98%
Deterministic payoff APY:      13.00%
Capital at maturity:           $11,300.00
Data points: 722 (hourly, 2026-05-22 → 2026-06-21)
```

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
│   ├── SKILL.md                           (the spec — load this into your agent)
│   ├── examples/
│   │   └── susdat-pt-spec.json            (live spec output)
│   ├── references/
│   │   ├── pendle-api.md                  (Pendle V2 API reference)
│   │   ├── cmc-mcp.md                     (CoinMarketCap MCP reference)
│   │   └── x402-integration.md            (x402 pay-per-request integration)
│   └── backtest/
│       ├── run_backtest.py                (backtest script — runs live)
│       ├── README.md                      (backtest usage)
│       ├── backtest_susdat_result.json    (live output, 722 data points)
│       └── backtest_susdat_output.txt     (live output, formatted)
│
├── lp-strategy-menu/                      (wrapper)
│   └── SKILL.md
│
├── lp-pendle-pt-fixed-usdat/              (conservative sister)
│   └── SKILL.md
│
├── lp-pendle-pt-fixed-slisbnbx/           (most-liquid stub)
│   └── SKILL.md
│
└── lp-concentrated-stable/                (stable LP stub)
    └── SKILL.md
```

---

## Live data sources

- **CoinMarketCap Pro API** — 15,000 calls/month (free tier). Endpoint: `https://pro-api.coinmarketcap.com`
- **CoinMarketCap MCP** — Streamable HTTP at `https://mcp.coinmarketcap.com/mcp`. 12 tools, MIT-licensed.
- **Pendle V2 API** — Public, no auth. Endpoint: `https://api-v2.pendle.finance/core/`. Rate limit 100 CU/min.
- **x402 MCP** — `https://mcp.coinmarketcap.com/x402/mcp`. $0.01 USDC per request on Base (chain 8453).

All endpoints verified live 2026-06-21.

---

## License

MIT (matches the official `openCMC/skills-for-ai-agents-by-CoinMarketCap` repo license)
