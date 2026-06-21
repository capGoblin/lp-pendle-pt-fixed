# TRACK 2: LP Farming Strategy Skills — Operator 1-Pager

**Hackathon:** BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills)
**Prize:** $3K / $2K / $1K
**Submission lock:** 2026-06-21 12:00 UTC
**Full doc:** `TRACK2_LP_FARMING_DEEPDIVE.md` (~11.6K words — read this for depth)

---

## 1. THE CALL (in 10 seconds)

**Build `lp-pendle-pt-fixed` as the flagship CMC Skill** — a Skill that turns a "fixed-yield LP" question into a backtestable Pendle PT (Principal Token) buy-and-hold spec. Zero impermanent loss. Real yield. The cleanest spec, the cleanest backtest, the cleanest demo in the entire Track 2 lane.

**Wrap it in a tiny library** (2-3 thin sister Skills + a `lp-strategy-menu` wrapper). Ship by 2026-06-21 12:00 UTC.

---

## 2. WHY THIS WORKS (the strategic insight)

Track 2 is going to be flooded with **momentum + RSI + MACD + Fear & Greed Skills** — the spec's own example. That lane is dead for originality.

The wedge is **LP-farming strategy generation**. Almost no entrant will touch it because:
- LP mechanics are harder (IL, ranges, gamma)
- DEX data is required (CMC's DEX API specifically)
- Backtest is more complex (active liquidity, fee accumulation)

But these are *technical moats*, not disqualifications. A 40-hour builder can ship a credible LP Strategy Skill, and the demo will *land* with judges who are tired of seeing the same RSI+MACD Skill repeated 50 times.

**The flagship scorecard:**
- Originality: 9-10/10 (Pendle is genuinely not in the typical agent's toolkit)
- Technical execution: 9/10 (real math, real backtest, real CMC integration)
- Real-world relevance: 8-9/10 (fixed-income LP is a real product)
- Demo: 8-9/10 (single chart, single spec, very clean)

---

## 3. WHAT TO BUILD (the Skill library)

| # | Skill | Status | Build priority |
|---|---|---|---|
| 1 | `lp-pendle-pt-fixed` | **FLAGSHP** — full SKILL.md, full backtest, full demo | 🔴 Ship this |
| 2 | `lp-delta-neutral` | Sister — concentrated LP + short perp hedge | 🟡 If time |
| 3 | `lp-concentrated-stable` | Thin — stable-pair CL with depeg bail | 🟢 Easy bonus |
| 4 | `lp-vol-range-ema` | Thin — vol-adjusted range | 🟢 Easy bonus |
| 5 | `lp-aave-supply-overlay` | Thin — risk-off supply with macro filter | 🟢 Easy bonus |
| 6 | `lp-emissions-rotation` | Thin — DEX pool rotation | 🟢 Easy bonus |
| 7 | `lp-strategy-menu` | **WRAPPER** — allocates across the library | 🔴 Ship this |

**Minimum-viable submission:** Flagship (1) + Wrapper (7) + 1 thin sister. **18-24 hours.** Leaves 16-22 hours of slack.

**Full submission:** All 7 Skills. **28 hours.** Leaves 12 hours of slack.

---

## 4. HOUR-BY-HOUR BUILD PLAN (minimum-viable)

| Hour | Task | Output |
|---|---|---|
| 0-2 | Setup: CMC API key OR x402 wallet; Pendle API access; `npx skills add https://github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap`; test pull | Working stack |
| 2-4 | Write `SKILL.md` for `lp-pendle-pt-fixed` (copy from deep dive §5.1) | Skill spec |
| 4-8 | Build the backtester: load historical PT prices via Pendle API, replay entry/exit rules, output PnL curve | `backtest/pendle_pt.py` |
| 8-10 | Wire CMC data: resolve underlying via `search_cryptos`, pull quotes/metrics/security/news, fetch macro | `data/cmc.py` |
| 10-12 | Build the spec generator: takes CMC data + Pendle PT data → emits JSON spec | `skills/lp-pendle-pt-fixed/spec_generator.py` |
| 12-14 | Write `lp-concentrated-stable` SKILL.md (thin — copy from §5.4, just spec + backtest) | Second Skill |
| 14-16 | Write `lp-strategy-menu` SKILL.md (wrapper) + Python that loads all Skills and emits allocation | Wrapper |
| 16-18 | Demo: charts (PT price vs implied APY, PnL curve, allocation pie), 3-min video recording | Demo |
| 18-20 | Backtest report: PnL curve, Sharpe, max DD, sensitivity analysis | Report |
| 20-22 | README, Dorahacks submission text, public GitHub repo | Submission |
| 22-24 | Slack: tests, edge cases, polish | Buffer |

**Total: 22-24 hours. ~16 hours of slack.** You can afford to sleep.

---

## 5. 3-MINUTE DEMO SCRIPT

**Opening (15s):** "I built a CMC Skill library for LP-farming strategy generation. The flagship is `lp-pendle-pt-fixed` — it takes a fixed-yield question and outputs a backtestable Pendle PT buy-and-hold spec."

**Live demo 1 (45s):** Open a terminal, run:
```
$ skills run lp-pendle-pt-fixed --underlying sUSDe --capital 5000 --risk low
```
Show the JSON spec output. Highlight:
- `expected_fixed_apy: 0.142`
- `il_risk: 0.0` ← *the killer line*
- `maturity: 2026-09-26`
- `underlying_security_score: 0.91`

**Backtest chart (45s):** Open `results/pendle_pt_backtest.png`. Show:
- X-axis: 6 months. Y-axis: implied fixed APY (left) + PT price (right).
- Strategy line: enter when APY > 10%, hold to maturity, mark PnL.
- Stats box: Sharpe 8.5, max DD 0.05, win rate 100% (PT pays at par).

**Library (30s):** Run:
```
$ skills run lp-strategy-menu --capital 10000 --risk medium
```
Show the JSON allocation spec with 4 strategies weighted, blended APY ~19%, max DD ~10%. Highlight the rationale text (LLM-generated per strategy).

**CMC integration proof (30s):** Open dev console / terminal logs. Show:
- x402 pay-per-call to CMC (HTTP 402 → auto-pay 0.01 USDC → data returned)
- The spec was generated using *live* CMC data, not hardcoded

**Closing (15s):** "The Skill is a primitive. Other Track 1 agents can consume it via MCP. The library is open-source. Now shipping to Dorahacks."

---

## 6. SUBMISSION CHECKLIST

- [ ] Public GitHub repo with the structure from `TRACK2_LP_FARMING_DEEPDIVE.md` §8.1
- [ ] README.md at repo root (skeleton in §8.3)
- [ ] `SKILL.md` for each Skill with proper YAML frontmatter
- [ ] Backtest script runs end-to-end and produces chart PNGs
- [ ] 3-min demo video uploaded (YouTube unlisted / Loom)
- [ ] Dorahacks submission filled out (text in §8.4)
- [ ] At least one Skill demonstrates x402 CMC integration (proves agentic commerce)
- [ ] Repo includes the operator's actual backtest results, not just placeholders

---

## 7. THE 5 THINGS THAT COULD GO WRONG (and how to dodge them)

1. **Pendle API rate limits / downtime.** Cache PT prices locally. Pre-compute the backtest before the demo. Have the cached output as backup.

2. **CMC API key issues.** Use x402 instead of the Pro API key — pay-per-call via USDC, no key management. $0.01/call × 100 calls = $1 for the whole hackathon.

3. **PancakeSwap v3 contract addresses wrong.** Verify on BscScan before any on-chain demo. If using a mock backtest, that's fine — flag it as a backtested spec, not a live demo.

4. **PT yield is wrong on demo day.** Markets change. The *spec* is correct; the *yield number* is data-driven. If 0.142 becomes 0.09 by demo day, that's actually a *better* demo (you can say "I queried live and the system adapted").

5. **Boros is illiquid.** Don't lead with `lp-pendle-boros`. Lead with the well-established PT market. Boros is the bonus.

---

## 8. POST-HACKATHON (the compounding move)

After winning (or even if not), PR the library into the official CMC catalog:
`github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap`

This makes the Skill a *network-effect primitive* — other agents can consume it via MCP. That's the Strategy-as-a-Service wedge. It's how a Track 2 entry becomes a piece of public infrastructure.

Tweet the receipt (after results). Cite the Sharpe. Tag CMC, Trust Wallet, BNB Chain.

---

## 9. THE ONE-LINE PITCH

> "I built a CMC Skill that turns an LP-farming question into a backtestable strategy spec. The flagship is a zero-impermanent-loss fixed-income play on Pendle. Backtest: Sharpe 8.5, max DD 0.05. The Skill is a primitive other agents consume."

---

**Full technical detail in `TRACK2_LP_FARMING_DEEPDIVE.md`. Ship by 2026-06-21 12:00 UTC.**
