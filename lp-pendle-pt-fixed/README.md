# lp-pendle-pt-fixed

**BNB Hack Track 2 — CoinMarketCap Strategy Skill**
**Live APY: 14.98% (sUSDat) · Zero IL · 67 days to expiry**

A CoinMarketCap-compatible Skill that recommends Pendle Principal Token (PT) buy-and-hold positions on BSC for **fixed yield with zero impermanent loss**. Loads into any MCP-compatible AI agent (Claude Code, Cursor, etc.) and outputs a backtestable JSON strategy spec.

## What it does

When a user asks "What's the best fixed-yield PT on BSC right now?", this skill:

1. Pulls live PT markets from Pendle's public API
2. Filters by liquidity (≥$500K), time-to-maturity (≥14d), yield floor (≥8%), and underlying safety
3. Pulls CMC context for each candidate (price, RSI, news, macro events)
4. Picks the top candidate and outputs a structured JSON spec
5. Hands the spec to a backtester, an allocation engine, or a TWAK execution layer

## Live flagship (verified 2026-06-21)

| Field | Value |
|---|---|
| Instrument | PT-sUSDat-2026-08-27 |
| Underlying | sUSDat (Resolv USR yield-bearing) |
| Implied APY | **14.98%** |
| Liquidity | $2.96M |
| Time to maturity | 67 days |
| IL profile | zero |
| PT contract | `0x23f9a497a5d4d54eaf5e03d94774f17dc1219745` |
| Market | `0x1017e73ce9c219164ce841a980136eb023c55387` |

**Backtest result** (live, 722 hourly observations):
- Deterministic payoff: **$10K → $11,300 in 67 days** (13% APY at entry)
- Mark-to-market Sharpe: negative (implied APY rose — buy-and-hold is the right call)
- Data range: 2026-05-22 → 2026-06-21

## Quick start

### Load into Claude Code / Cursor

1. Copy this directory to your agent's skills folder
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

3. Get a free CMC Pro API key at https://pro.coinmarketcap.com/login (15,000 calls/month)
4. Ask your agent: *"Recommend the best fixed-yield PT on BSC for $10K capital."*

### Run the backtest locally

```bash
cd backtest
python3 run_backtest.py --list                              # all 6 active BSC PT markets
python3 run_backtest.py --market 0x1017e73... --capital 10000  # sUSDat backtest
```

## x402 agentic-commerce demo (the wedge)

The skill demonstrates the **x402 pay-per-request protocol**:

1. Agent calls CMC's x402 MCP at `https://mcp.coinmarketcap.com/x402/mcp`
2. MCP returns 402 Payment Required
3. Agent's wallet (Base, USDC) signs $0.01 payment on-chain
4. MCP returns the data
5. Agent reasons across PT markets, outputs the spec
6. Demo includes the on-chain payment tx hash

This is the **agentic-commerce angle** for the BNB Hack — no API keys, agent-to-agent data exchange with cryptographic settlement.

## Files

```
SKILL.md                                ← load this into your MCP agent
examples/susdat-pt-spec.json            ← live spec output
references/pendle-api.md                ← Pendle V2 API reference
references/cmc-mcp.md                   ← CMC MCP tool reference
references/x402-integration.md          ← x402 pay-per-request integration
backtest/run_backtest.py                ← live backtest script
backtest/README.md                      ← backtest usage
backtest/backtest_susdat_output.txt     ← live captured output
backtest/backtest_susdat_result.json    ← full PnL curve (722 points)
```

## License

MIT
