# PHASE LOG — Track 2 LP-farming Submission Build

**Hackathon:** BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills)
**Operator:** capGoblin
**Agent:** Sambar (with isolated subagents)
**Started:** 2026-06-20 18:14 UTC
**Submission deadline:** 2026-06-21 12:00 UTC (~18h from start)

---

## Why this log exists

The operator lost an earlier 8h research push when the session context was wiped.
This file is the durable record. Every phase that lands here is on disk and survives
session restarts, channel changes, and context wipes.

---

## Files in this folder (the durable submission bundle)

| File | Purpose |
|---|---|
| `BUILD_IDEAS.md` | Original broad track 1+2 doc (29 KB) — kept as historical reference, NOT the working plan |
| `TRACK2_LP_FARMING_DEEPDIVE.md` | Deep dive — 8 skill specs + 1 wrapper + LP archetypes + math + math + math (85.7 KB) |
| `TRACK2_LP_FARMING_QUICKSTART.md` | 1-page operator quickstart — the call, build plan, demo script, submission checklist (7.8 KB) |
| `PHASE_LOG.md` | THIS FILE. The state-of-the-build record. Read this first. |
| `PHASE_0_CMC_VERIFICATION.md` | ✅ Live verification of the 7 CMC endpoints in the flagship spec. **Found 1 fake endpoint name** (`get_crypto_security_detail` doesn't exist) |
| `PHASE_0_PENDLE_VERIFICATION.md` | ✅ Live BSC PT market data. **Found the flagship is wrong**: sUSDe isn't on BSC, sUSDat at 14.98% APY is the real flagship |
| `PHASE_0_INTEGRATION_NOTES.md` | ✅ Operator-facing summary: what to change in the build, what to keep, what's unverified, time budget |

Files that will be added as phase 1+ lands:

| File (planned) | Purpose |
|---|---|
| `PHASE_1_REPO_SCAFFOLD/` | The actual repo structure for the flagship |
| `PHASE_2_BACKTEST/` | Backtest code + results |

---

## Phase state

- [x] **Phase -1: Deep research** — TRACK2_LP_FARMING_DEEPDIVE.md + QUICKSTART delivered
- [x] **Phase 0: Verification** (DONE 2026-06-21 10:15 UTC, ~15m)
  - [x] CMC AI Agent Hub endpoint verification
  - [x] Pendle live PT market API verification
  - [x] Integration notes (what to change in the build)
- [ ] Phase 1: Repo scaffold + flagship SKILL.md
- [ ] Phase 2: Flagship backtest
- [ ] Phase 3: Wrapper + thin sister
- [ ] Phase 4: Demo + Dorahacks submission

## Phase 0 — key findings (operator 1-liner)

1. **Flagship changes from sUSDe → sUSDat.** sUSDe isn't on BSC. sUSDat: 14.98% implied APY, $2.96M liquidity, 67d to expiry. Real PT contract on BSC: `0x23f9a497a5d4d54eaf5e03d94774f17dc1219745`.
2. **One of 7 CMC endpoints in the deep-dive spec doesn't exist.** `mcp__cmc-mcp__get_crypto_security_detail` → replace with `get_crypto_info` + `search_crypto_info`.
3. **Plan tier is 15K calls/month, not 330.** No backtest budget concern.
4. **Backtest data path works.** `/v3/56/markets/{address}/historical-data` returns 722 hourly observations for sUSDat, stable 13-15% APY.
5. **x402 MCP is the demo differentiator.** `https://mcp.coinmarketcap.com/x402/mcp`, $0.01 USDC per request on Base. The cmc-x402 SKILL.md is in openCMC repo.
6. **149-token allowlist unverified.** Dorahacks gated by AWS WAF. Not a Track 2 hard constraint.
7. **Thin library reduced from 8 skills → 4 skills + 1 wrapper.** Cuts YT spec, Boros, delta-neutral, Beefy (no clean live data path in time budget).

---

## Phase 0 brief (what's being verified right now)

Two parallel research streams. Each delivers a markdown file with cited evidence.

### Stream A — CMC AI Agent Hub verification

The flagship `lp-pendle-pt-fixed` spec uses these CMC endpoints. Each must be confirmed live:

1. `mcp__cmc-mcp__search_cryptos` — resolve underlying (e.g. sUSDe) → cmc_id, contract address
2. `mcp__cmc-mcp__get_crypto_quotes_latest` — spot price + market cap
3. `mcp__cmc-mcp__get_crypto_metrics` — holder concentration
4. `mcp__cmc-mcp__get_crypto_security_detail` — security score
5. `mcp__cmc-mcp__get_crypto_latest_news` — catalyst check
6. `mcp__cmc-mcp__get_global_metrics_latest` — fear/greed, btc dominance, total mcap
7. `mcp__cmc-mcp__get_global_crypto_derivatives_metrics` — perp funding aggregate

For each: confirm endpoint exists in the AI Agent Hub MCP tool list, confirm the response shape matches what the flagship spec assumes, confirm rate limits / auth shape, note any discrepancies.

### Stream B — Pendle live PT market API verification

The flagship depends on Pendle's live PT market data. Verify:

1. Pendle's public API endpoint for listing PT markets (URL + auth shape)
2. Response structure: what fields per PT market
3. Currently-active BSC PT markets (list them)
4. Live implied APYs for the top 5 PT markets on BSC
5. Liquidity depth per market
6. Contract addresses for the top PT markets on BSC (verify on BscScan)
7. Whether the underlying tokens of top PT markets are in the hackathon's 149-token allowlist (this is a hard constraint — only in-allowlist tokens count for the demo)

Deliverable file paths:
- `/root/.openclaw/workspace/research/bnb-hack-ai-trading-agent/PHASE_0_CMC_VERIFICATION.md`
- `/root/.openclaw/workspace/research/bnb-hack-ai-trading-agent/PHASE_0_PENDLE_VERIFICATION.md`
- `/root/.openclaw/workspace/research/bnb-hack-ai-trading-agent/PHASE_0_INTEGRATION_NOTES.md` (operator-facing summary, the "what does this mean for the build" file)

---

## Operating rules

- Phase 0 is **verification only**. No code, no SKILL.md, no scaffold yet.
- Every claim in the verification files must be cited (URL + retrieved-at timestamp).
- If an endpoint doesn't exist or doesn't match, surface that immediately — don't paper over it.
- If Pendle's API doesn't expose what the spec assumes, surface the gap and propose the fix (e.g. on-chain reads via BscScan API instead).
- Operator-facing summary should be plain English: "what works, what's broken, what changes for the build."

---

## Update cadence

Phase 0 expected to land within 1–2h. Will append to this log as each deliverable lands.