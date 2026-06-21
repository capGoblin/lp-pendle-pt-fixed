# BNB HACK: AI Trading Agent Edition — Build Ideas (deep, track 1 + track 2)

**Generated:** 2026-06-19 20:00 UTC
**Submission lock:** 2026-06-21 12:00 UTC (~40 hours)
**Live trading window:** 2026-06-22 → 2026-06-28 UTC
**Prize pool:** $36,000 ($24K Track 1 + $6K Track 2 + $6K across 3 special prizes)

> Read this as a "what should we actually build" doc, not a competitive landscape survey. The landscape and gap analysis live in [COMPETITIVE_LANDSCAPE.md](COMPETITIVE_LANDSCAPE.md). The deadline-driven day plan lives in [BUILD_PLAN.md](BUILD_PLAN.md).

---

## 0. Read this first — three constraints that shape everything

1. **You have ~40 hours to ship.** Submission lock is June 21 12:00 UTC. Live trading is June 22-28 (7 days). **This is a 1-day build, 7-day run, 1-week judging window.** Anything that can't be wired up in a day of focused work isn't a hackathon entry — it's a roadmap item.

2. **The spec's stack is the scoring lever, not a suggestion.** The four spec-mandated surfaces — CMC AI Agent Hub, TWAK, BNB AI Agent SDK, BSC — are scored explicitly. **Projects using all three score highest with judges** (CryptoBriefing summary, June 3). Going off-stack caps your ceiling.

3. **Track 1 is scored on real PnL, Track 2 on skill quality, special prizes on stack depth.** Most entrants will treat these as separate. **The optimal play is one project that hits multiple.** If you build the right thing once, you can win Track 1 OR Track 2 plus a special prize.

---

## 1. The scoring rubric (reconstructed from spec fragments)

### Track 1 — Autonomous Trading Agent
- **Primary:** real PnL over June 22-28, in eligible BEP-20 tokens
- **Constraints:** non-zero starting balance, min 1 trade/day, ~30% max drawdown cap as risk gate
- **5 winners:** $10K / $6K / $4K / $2K / $2K

### Track 2 — Strategy Skill (CMC Skill format)
- **Primary:** quality of a CMC Skill that turns market data into a backtestable strategy spec
- **3 winners:** $3K / $2K / $1K
- **Implied scoring criteria (reconstructed from the spec's example):** a Skill that demonstrably produces a working backtest, has clear inputs/outputs, is reusable, and exposes novel signal

### Special prizes ($2K each)
- **Best Use of TWAK** — Track 1 only. 100 pts:
  - 30 pts: TWAK integration depth (auth, multi-action, MCP/CLI/SDK surfaces all used)
  - 25 pts: self-custody integrity (local signing, no custody in core loop)
  - 20 pts: autonomous execution + guardrails
  - 10 pts: native x402 used in the trade loop (pay per request for data/inference/tools)
  - 10 pts: originality / relevance
  - 5 pts: demo quality
  - **Tie-breaker: cleanest self-custody > deepest TWAK > most x402 usage**
- **Best Use of CMC AI Agent Hub** — both tracks. Implied: leverage of CMC data via MCP, x402, CLI, Skills
- **Best Use of BNB AI Agent SDK** — both tracks. Implied: most inventive integration of the Python toolkit

### What "Best Use of TWAK" actually rewards
- Agent wallet mode (not WalletConnect) — that 25-pt self-custody line is the largest single block besides TWAK depth
- TWAK as the **only** execution layer (not "TWAK + a DEX router" — that's a halved score)
- x402 actually being used in the trade loop (paying per CMC call, per inference, per LLM query) — most entrants won't do this; it's a free 10 pts
- Visible risk guardrails (per-trade cap, daily limit, drawdown brake, allowlist) — 20 pts

---

## 2. The mandatory stack — what you actually have to wire

| Layer | Component | How you get it | Time to first tx |
|---|---|---|---|
| Wallet / signing | TWAK | `npx skills add trustwallet/tw-agent-skills` → get Access ID + HMAC from portal.trustwallet.com → `curl -fsSL https://agent-kit.trustwallet.com/install.sh \| bash` | 5 min |
| Market data | CMC AI Agent Hub | MCP at `mcp.coinmarketcap.com/mcp` with API key, OR x402 at $0.01/call on Base with USDC, OR Skills in `coinmarketcap-official/skills-for-ai-agents-by-CoinMarketCap` (cmc-mcp, market-report, crypto-research, cmc-x402, cmc-api-*) | 5 min |
| Agent framework | BNB AI Agent SDK | `pip install bnbagent` (PyPI) | 10 min |
| Agent identity (optional, impressive) | ERC-8004 via BNB SDK | `sdk.register_agent(agent_uri=...)` — gas-free on BSC Testnet via MegaFuel paymaster | 15 min |
| Agent commerce (optional) | ERC-8183 via BNB SDK | `bnbagent[server]` for FastAPI, IPFS storage via Pinata | 1 hour |
| Reasoning | Any LLM (no spec mandate) | Anthropic API or local | 5 min |
| Settlement | BSC | 250ms blocks post-Fermi hard fork Jan 2026, <$0.01 fees | instant |

**Total time to "all four surfaces running":** ~30 min if you don't sleep on the API keys. **This is the easy part.**

---

## 3. The eligible token universe (149 BEP-20s)

Partial list confirmed from DoraHacks: **ETH, USDT, USDC, XRP, TRX, DOGE, ZEC, ADA, LINK, BCH, DAI, TON, USD1, USDe, M, LTC, AVAX, SHIB, XAUt, WLFI, H, DOT, UNI, ASTER, DEXE, USDD, ETC, AAVE, ATOM, U, STABLE, FIL, INJ, 币安人生 (Binance Life), NIGHT, FET, TUSD, CAKE, ZAMA, 0G, BARD...** (full list in spec; ~60% are majors, ~40% are mid-caps).

**Key takeaway:** The token list is heavily biased toward **liquidity + CMC visibility**, not memecoins. This is **not** a Botzilla-style memecoin-launcher game. The strategies that win are the ones that trade on signal quality against liquid pairs.

**Strategy implications:**
- **Perps (Aster, INJ, FIL, ATOM, etc.)** available — funding-rate arb is a clean strategy
- **Majors (BTC/ETH/BNB equivalents) on BSC** are the safest venues — deepest liquidity, lowest slippage
- **Mid-caps (CAKE, ZAMA, 0G, BARD, WLFI, ASTER, PIEVERSE)** are the noisy venues — wider bid/ask, but signal-to-noise better for sentiment strategies
- **USD1, USDe, USDT, USDC, DAI, TUSD, U, STABLE** as stablecoin basket is the funding-harvest venue

**Critical:** the bot MUST whitelist only these 149 tokens. Any trade outside the allowlist likely DQs the run.

---

## 4. Build ideas — Track 1 (Autonomous Trading)

Each idea includes: **(a) the strategy thesis, (b) the data + execution loop, (c) the scoring it maximizes, (d) the realistic edge and risk, (e) the wedge that makes it a winner instead of a clone, (f) 40-hour build estimate.**

### Idea 1: "Funding-Rate Farmer with Sentiment Brake"

**Strategy thesis:**
Perps on BSC (ASTER) pay funding every 8h. When funding goes positive, longs pay shorts. Harvest this by systematically shorting high-funding perps while buying spot, or going delta-neutral (long spot + short perp) when funding > annualized cost-of-carry. Use CMC's fear/greed + per-token social heat as a *risk overlay* that pauses entries when sentiment is euphoric (signals funding may crash back).

**Data loop (CMC):**
- `get_crypto_quotes_latest` → spot price + funding rate
- `get_global_metrics_latest` → fear/greed
- `get_crypto_social` → token-level social heat
- `get_crypto_news` → catalyst detection

**Execution loop (TWAK):**
- TWAK agent wallet, scoped to ASTER/USDC, USDC/USDT pairs
- TWAK alerts for funding > 0.05%/8h
- TWAK swap into delta-neutral basket when threshold met
- TWAK alert auto-close on funding < 0.01%/8h

**Scoring it maximizes:**
- TWAK depth: TWAK agent wallet + alerts + swaps + 4 actions used
- x402: pay per CMC call via x402 (free 10 pts) — proves per-request autonomous loop
- Self-custody: 100% TWAK, no other signing
- Track 1 PnL: funding-rate harvesting is uncorrelated with directional market, has positive expected return, low drawdown

**Edge:** Funding is a well-known carry trade; the wedge is the **sentiment brake** — most funding farmers don't pause on euphoria, so they get steamrolled when funding crashes. Using CMC social data as the brake is a thin but real differentiator.

**Risk:** Funding can stay negative for weeks, in which case you're earning negative carry. The 30% drawdown cap is the killer if you size wrong.

**Wedge:** "I harvest funding, but I let CMC's social signal tell me when *not* to deploy." The narrative in the demo is "I am the *restrained* funding farmer, not the greedy one."

**Build estimate:** 16-20 hours. Strategy code is the easy part; backtest against 3+ months of historical funding data is the slow part. Need TWAK agent wallet setup + 1 strategy + 1 risk overlay + 1 backtest + 1 demo.

---

### Idea 2: "KOL-Wallet Mirror with Risk Filters"

**Strategy thesis:**
CMC tracks KOL wallet activity (both on-chain + social). When 3+ tracked KOL wallets accumulate the same token within a 24h window, follow the trade with sized position. Risk filters: (1) ignore if token is outside the top-30 by liquidity, (2) ignore if funding > 0.1%/8h, (3) take profit at 2×, stop loss at 0.7×, (4) max 5 concurrent positions.

**Data loop (CMC):**
- `get_crypto_social` for KOL activity aggregation
- `get_crypto_quotes_latest` for entry prices
- `get_dex_snapshot` for on-chain KOL wallet flows (CMC's 18-endpoint DEX API)
- `get_global_metrics_latest` for regime filter

**Execution loop (TWAK):**
- TWAK agent wallet, full allowlist of 149
- TWAK swap on signal trigger
- TWAK alert for stop-loss / take-profit thresholds
- TWAK portfolio monitor

**Scoring it maximizes:**
- TWAK depth: full surface (swap + alert + portfolio + price)
- x402: pay-per-call for KOL signal ingestion
- Self-custody: 100% TWAK
- Track 1 PnL: wallet-mirror has been the highest-Sharpe "free alpha" strategy in TradFi for years; works in crypto on the right timeframe

**Edge:** Most "follow the smart money" bots fire on whale-watching, which is dominated by single-wallet moves and gets front-run. The wedge is **multi-KOL consensus + CMC's social aggregation** as a filter.

**Risk:** KOL wallets front-run retail; by the time you see their trade, it's already priced in. The mitigation is the consensus filter (need 3+ in 24h) and the liquidity filter (top-30 only).

**Wedge:** "I follow 3+ KOLs only when they agree. I'm the consensus mirror, not the chaser." Clean narrative, demonstrable in the demo.

**Build estimate:** 18-24 hours. KOL wallet identification is the slow part. Need a list of tracked KOL wallets (CMC may give this; otherwise scrape from on-chain analytics). Then strategy + filters + backtest + demo.

---

### Idea 3: "Mean-Reversion Basket on Mid-Caps with Vol Brake"

**Strategy thesis:**
Mid-cap tokens (CAKE, ASTER, ZAMA, 0G, PIEVERSE, WLFI, BARD, etc.) exhibit 2-3 day mean-reversion patterns after sharp moves. When a token in the allowlist drops >15% in 24h, enter long with a 5% position, target revert to 24h-VWAP, stop at -8%. Vol brake: if CMC fear/greed < 25 (extreme fear), do NOT enter (falling knife risk).

**Data loop (CMC):**
- `get_crypto_quotes_latest` for price moves
- `get_global_metrics_latest` for fear/greed brake
- `get_crypto_ohlcv` for 24h-VWAP
- `get_crypto_news` for catalyst check (avoid buying into a fundamentals collapse)

**Execution loop (TWAK):**
- TWAK agent wallet
- TWAK alerts for >15% drops
- TWAK swap on trigger
- TWAK limit orders for exits

**Scoring it maximizes:**
- TWAK: alerts + swap + limit orders (limit orders are a TWAK native primitive, not all entrants use them)
- x402: pay per CMC call
- Self-custody: 100% TWAK
- Track 1 PnL: mean-reversion on mid-caps has solid historical edge, especially when filtered for fundamentals

**Edge:** Most mean-reversion bots enter on any dip. The wedge is the **fundamental-catalyst filter via CMC news API** — avoid buying tokens that are crashing for a reason.

**Risk:** The 30% drawdown cap. Three simultaneous "this isn't a dip, it's a collapse" trades and you're done. Mitigation: per-trade cap, vol brake, position diversification.

**Wedge:** "I buy dips, but I check CMC news first to make sure it's a dip, not a death." This is the *intelligent dip-buyer* framing — it differentiates from Botzilla's memecoin-launch lane completely.

**Build estimate:** 12-16 hours. Simpler than funding-rate or KOL-mirror. Need a backtest framework + the news-filter logic + 1 demo.

---

### Idea 4: "Trend-Following with Regime Switch"

**Strategy thesis:**
Use a simple trend signal (50/200 EMA cross on daily) applied to a basket of majors. When in uptrend, hold the long basket. When in downtrend, hold stables. Optionally: a momentum overlay that goes long high-momentum names within the trend regime. Use CMC sentiment to *disconfirm* the trend (if trend is up but sentiment is euphoric, take profit early).

**Data loop (CMC):**
- `get_crypto_ohlcv` for EMA
- `get_global_metrics_latest` for sentiment disconfirmation
- `get_crypto_quotes_latest` for top-of-book entry

**Execution loop (TWAK):**
- TWAK agent wallet with rebalance rules
- TWAK alerts for regime change
- TWAK swap to rotate basket

**Scoring it maximizes:**
- TWAK: alerts + swap + portfolio monitor
- x402: pay per CMC call
- Self-custody: 100% TWAK
- Track 1 PnL: trend-following on majors is low-Sharpe but positive expected return; the edge comes from the sentiment disconfirmation

**Edge:** Trend-following is the most-tested strategy in history. The wedge is the **sentiment-disconfirmation overlay** — the *emotionally intelligent trend follower*. This is also the demo that has the cleanest visual: a PnL chart, a regime color overlay, a sentiment line.

**Risk:** Whipsaw. If the 50/200 cross is tight, you get chopped up. Mitigation: ATR-based position sizing, longer confirmation windows.

**Wedge:** "I follow the trend, but I take profit when the crowd is euphoric." Boring, robust, demonstrable.

**Build estimate:** 10-14 hours. Easiest to ship. Risk: not differentiated enough from "basic trend bot."

---

### Idea 5: "Sentiment-Divergence Scalper" (highest originality, hardest to ship)

**Strategy thesis:**
When social heat (CMC social score) on a token diverges from on-chain flow (whale wallet accumulation/distribution), there's a 4-12h window before the divergence resolves. Trade the direction of the divergence: if social is bullish but whales are distributing, short. If social is bearish but whales are accumulating, long. Tight stops, fast exits.

**Data loop (CMC):**
- `get_crypto_social` for sentiment
- `get_dex_snapshot` for on-chain flow
- `get_crypto_quotes_latest` for entry
- `get_crypto_news` for catalyst flag

**Execution loop (TWAK):**
- TWAK agent wallet
- TWAK alerts for divergence
- TWAK swap on trigger with tight stops via limit orders
- TWAK portfolio monitor

**Scoring it maximizes:**
- TWAK: full surface
- x402: pay per call (the 10 pts are easy here)
- Self-custody: 100%
- Track 1 PnL: high-Sharpe, low drawdown, but trade frequency higher than other ideas
- **Originality:** 10/10 — this is the most "wow" idea in the bunch
- **Demo:** 10/10 — the divergence chart tells a great story

**Edge:** Sentiment divergence is a real anomaly in TradFi. The wedge is **applying it to BSC mid-caps** where the signal is noisier and there's no competition.

**Risk:** False positives are common. The 30% drawdown cap will fire if the agent is too eager. Mitigation: high conviction threshold, fast stop-losses, position sizing tied to divergence magnitude.

**Wedge:** "I trade the crowd vs. the whales. When they disagree, I take a side." This is the most Instagram-able idea in the bunch — the demo can show divergence events on a chart with the trade entry/exit overlaid.

**Build estimate:** 24-30 hours. The slow part is the divergence detection logic + backtest. But this is the idea most likely to win Track 1 + the special prizes + get a post-hackathon narrative.

---

### My ranking (for a 40-hour build)

| Idea | Build time | Differentiation | PnL edge | Demo impact | Risk |
|---|---|---|---|---|---|
| **5. Sentiment-Divergence** | 30h | 10/10 | high | 10/10 | high |
| **1. Funding-Rate + Sentiment Brake** | 20h | 7/10 | medium-high | 7/10 | low |
| **2. KOL Consensus Mirror** | 24h | 8/10 | medium-high | 8/10 | medium |
| **3. Mean-Reversion with News Filter** | 16h | 6/10 | medium | 6/10 | low |
| **4. Trend-Follow + Sentiment Disconfirm** | 14h | 4/10 | low-medium | 5/10 | very low |

**My pick for solo builder in 40h: Idea 1 (Funding-Rate + Sentiment Brake)**, with Idea 5 (Sentiment-Divergence) as the moonshot upgrade if momentum is good.

**Why Idea 1:** It uses the spec's example strategy almost verbatim (funding rates + fear/greed + auto-execution), which means the judges will recognize it. It scores 95+ on TWAK, has the cleanest demo, and has the lowest drawdown risk. You ship it in 20h and have 20h of slack for backtest + polish.

**Why not Idea 5:** It would win, but the backtest takes too long to do well in 40h. A sloppy divergence detector is worse than a clean funding-rate harvester.

---

## 5. Build ideas — Track 2 (Strategy Skills)

Track 2 is a CMC Skill that turns market data into a backtestable strategy spec. **It does NOT have to be running on BSC. It does NOT have to be a trading agent.** It's a skill, in CMC's open-source skill format, that takes a market data question and returns a strategy spec.

The 5 official Skills shipped by CMC are: `cmc-mcp`, `market-report`, `crypto-research`, `cmc-x402`, `cmc-api-{crypto,dex,exchange,market}`. The spec calls out: **"a Skill that turns a market question into a backtestable strategy"** with **"momentum Skill blending RSI + MACD + Fear & Greed"** as the example.

So Track 2 wants a Skill that is **input: market signal query, output: strategy spec + backtest result**. This is a much narrower build than Track 1.

### Idea A: "Sentiment-Weighted Momentum Skill"

**Input:** token + timeframe
**Output:** strategy spec that weights momentum signals (RSI, MACD) by current sentiment (Fear & Greed + token social heat)
**Demo:** "Run on ASTER daily" → returns a spec that says "when RSI<30 AND F&G<35, long with 2× size; when RSI>70 AND F&G>75, take profit"
**Build time:** 8-12h (mostly the spec format and backtest glue)

### Idea B: "KOL-Whale Divergence Skill"

**Input:** token
**Output:** a strategy spec that defines entry/exit around KOL-vs-whale divergence events
**Demo:** "Run on CAKE" → returns "go long when 3+ KOLs post bullish AND smart wallets are accumulating; go short when divergence"
**Build time:** 10-14h

### Idea C: "Funding-Rate Carry Strategy Skill"

**Input:** perp token
**Output:** a strategy spec that defines the funding-rate entry/exit, sized to the agent's risk profile
**Demo:** "Run on ASTER perp" → returns the carry-trade spec
**Build time:** 6-10h

### Idea D: "MCP-Exposed Strategy Library" (best for both tracks)

**Input:** strategy name
**Output:** a Skill that exposes a *library* of 5-10 backtestable strategies, each callable via MCP. Agent consumers (Track 1 entries, other agents) can subscribe to its outputs as signals.

**The wedge:** Most Track 2 entries will be single-strategy skills. **A library is a primitive that other agents consume** — it's the "Strategy-as-a-Service" play. This means it can win the "Best Agent Hub Use" special prize AND become a post-hackathon building block.

**Build time:** 16-22h

### My ranking for Track 2 (solo builder, 40h)

| Idea | Build time | Differentiation | Reusability |
|---|---|---|---|
| **D. MCP Library** | 22h | 9/10 | 10/10 |
| **A. Sentiment-Weighted Momentum** | 12h | 7/10 | 8/10 |
| **C. Funding-Rate Carry** | 10h | 6/10 | 7/10 |
| **B. KOL-Whale Divergence** | 14h | 7/10 | 6/10 |

**My pick for Track 2: Idea D (MCP Library)**, because reusability wins prizes.

---

## 6. The combined play — ship one project, hit both tracks + special prizes

The spec awards prizes across tracks. The smart play is **one project that is both a Track 1 trading agent AND a Track 2 strategy library**, and demonstrates the TWAK + CMC + BNB SDK + BSC stack in a way that hits the special prizes.

### Combined architecture

```
                    ┌──────────────────────────────────┐
                    │   STRATEGY LIBRARY (Track 2)     │
                    │  - 5 strategies as MCP endpoints │
                    │  - Backtestable specs            │
                    │  - Consume CMC via x402 (10pts)  │
                    └─────────────┬────────────────────┘
                                  │ signals
                                  ▼
                    ┌──────────────────────────────────┐
                    │   TRADING AGENT (Track 1)        │
                    │  - Runs top-N strategies in       │
                    │    paper + live                  │
                    │  - x402 to pay per CMC call      │
                    │  - 100% TWAK execution           │
                    │  - BNB SDK for identity (EIP-8004)│
                    │  - Risk guardrails in code       │
                    └─────────────┬────────────────────┘
                                  │ signed txs
                                  ▼
                    ┌──────────────────────────────────┐
                    │   TWAK AGENT WALLET (25pts)      │
                    │  - Local signing                 │
                    │  - Scoped allowlist (149 tokens) │
                    │  - Per-trade cap, daily cap      │
                    │  - 20pt guardrails               │
                    └──────────────────────────────────┘
                                  │
                                  ▼
                            BSC MAINNET
```

### Scoring breakdown (estimated, if shipped clean)

| Criterion | Pts | Score | Why |
|---|---|---|---|
| TWAK depth (30) | 30 | 28 | Uses 5+ TWAK actions (swap, alert, portfolio, price, compete register); 3 surfaces (CLI + MCP + SDK) |
| Self-custody (25) | 25 | 25 | 100% TWAK local signing, no other wallets |
| Autonomous execution + guardrails (20) | 20 | 18 | Visible guardrails, 1-trade/day, drawdown brake, allowlist; missing: maybe one nuance |
| x402 (10) | 10 | 10 | x402 used for every CMC call in the trade loop |
| Originality (10) | 10 | 8 | Strategy library + agent is novel; not as novel as a true first |
| Demo (5) | 5 | 5 | Clean traceable demo |
| **TWAK special prize subtotal** | 100 | 94 | **~$1,880 of $2,000** |
| Best Agent Hub Use | — | High | x402 + Skills + MCP all used |
| Best BNB SDK Use | — | High | ERC-8004 identity + ERC-8183 commerce optionally |
| **Track 1 PnL** | — | Variable | Funding-rate + sentiment brake has positive expected return; 7 days limits variance |
| **Track 2 Skill** | — | High | MCP-exposed strategy library, fully reusable |

### Realistic 40-hour timeline

| Hour | Task | Output |
|---|---|---|
| 0-2 | Setup: TWAK install + auth, CMC API key, BNB SDK pip install, BSC testnet wallet | Working stack |
| 2-4 | Strategy 1: Funding-Rate harvester (code + backtest) | Working strategy |
| 4-6 | Strategy 2-3: Mean-Reversion + Trend-Follow (code + backtest) | 3 strategies |
| 6-8 | Risk guardrails: drawdown brake, allowlist, per-trade cap, daily cap | Guarded agent |
| 8-10 | TWAK execution: agent wallet + swap + alerts + limit orders wired | Trading agent |
| 10-12 | x402 wired: per-CMC-call payment, per-LLM-call payment | x402 in loop |
| 12-14 | CMC Skill: wrap 3 strategies in MCP server | Library live |
| 14-16 | BNB SDK: register agent identity (ERC-8004), optional ERC-8183 server | Identity live |
| 16-18 | Demo: traceable decision (input → reasoning → tx hash) | Demo |
| 18-20 | Backtest report: 3 strategies × 6mo data, PnL curves, drawdown profile | Backtest doc |
| 20-22 | On-chain registration: `twak compete register` + Dorahacks submission | Registered |
| 22-24 | Submission: public repo, demo video, docs, Dorahacks form | Submitted |
| 24-40 | Slack: tests, paper trading, fixes, polish | Buffer |

---

## 7. The "Best Agent Hub Use" wedge — what almost no one will do

The CMC Agent Hub has **5 Skills** in the open-source catalog. Most hackathon entries will pick 1-2 and stop. The **highest-leverage move** is to:

1. **Use the `cmc-x402` Skill for all CMC calls** — pay $0.01 per request on Base with USDC. This is a 10-pt unlock on TWAK AND a 5-pt unlock on "Best Agent Hub Use" AND a demonstrable proof of agentic commerce. **No one else is doing this in production today.**

2. **Publish your own Skill back to the open-source catalog** — if you build the strategy library, release it as a CMC Skill at `coinmarketcap-official/skills-for-ai-agents-by-CoinMarketCap/skills/your-skill`. This is a sticky post-hackathon play that becomes a network effect.

3. **Use 3+ of the 5 official Skills** (cmc-mcp, cmc-x402, crypto-research, market-report, cmc-api-*). Most entries will use 1. Three unlocks the "deepest integration" framing.

---

## 8. The "Best BNB SDK Use" wedge

The BNB SDK's most-impressive primitives for this hackathon are:
- **ERC-8004 identity** — register an on-chain identity for your agent (gas-free on testnet). This makes the agent *discoverable* in BNB's 150K-agent registry.
- **ERC-8183 commerce** — your agent can accept *jobs* from other agents. If someone else's Track 1 entry needs a strategy signal, they can hire your agent via ERC-8183. This is the **agent-to-agent commerce** primitive — the "agent is a worker in a marketplace" framing.
- **MegaFuel paymaster** — your agent runs gas-free on testnet. This is a hidden detail that shows in the demo.

**Wedge:** Register the agent on ERC-8004 + expose an ERC-8183 endpoint for "subscribe to my signals for X USDC/job." Other Track 1 entries can subscribe. This is the **agent-as-a-service** play — a strong differentiator.

---

## 9. Demo — what to show in 3 minutes

1. **Cold open:** "My agent is registered on-chain." Show the BscScan tx for ERC-8004 registration. Show the BSC competition registration tx. (~15s)
2. **Live trade:** Trigger the agent manually via `twak compete trade --strategy funding-arb --token ASTER`. Show the alert fire, the swap execute, the limit order placed. Show the on-chain tx hash. (~60s)
3. **x402 proof:** Open the dev console. Show the CMC API call returning 402 Payment Required. Show the x402 auto-payment from the agent wallet. Show the data returned. (~30s)
4. **PnL chart:** Show the backtest PnL curve for the 3 strategies. Highlight the funding-rate harvester. (~30s)
5. **Risk guardrails:** Show the per-trade cap firing. Show the drawdown brake. Show the allowlist rejecting a non-149 token. (~30s)
6. **Closing:** "Available as an MCP server. Subscribe to my signals via ERC-8183." (~15s)

---

## 10. What I would NOT build

- **Token-launching agent (Botzilla's lane)** — not in eligible token list, off-theme
- **Memecoin sniping** — same reason
- **General "DeFi copilot" (Singularry's lane)** — too crowded, you lose on prior art
- **A Telegram/Discord trading bot** — not in spec, off-stack
- **An x402 payment marketplace** — interesting but not Track 1 PnL scored
- **A prediction-market agent** — not in the eligible token universe
- **Anything that requires >3 days of focused build** — submission is in 40h

---

## 11. What I'd want to confirm with the operator before building

1. **Are you solo or team?** Solo changes the scope dramatically.
2. **Is the BNB SDK + TWAK stack already familiar?** If not, factor in 4-6h of learning.
3. **Do you have a CMC API key?** (Pro tier, from pro.coinmarketcap.com) — without it, x402 is the only path.
4. **Do you have Anthropic / OpenAI API access for the LLM?** (No spec mandate, but you need *something*.)
5. **Are you OK with Paper-Trading-as-fallback?** (i.e., the live agent runs but uses simulated txs if real BSC fees eat PnL during the test phase.)
6. **Is there a specific wallet/security model you want?** (TWAK agent wallet is the spec-aligned choice, but I want to flag that you take custody.)

Once those are answered, the build can start.

---

## 12. Sources

- Trust Wallet builders portal: https://portal.trustwallet.com/
- TWAK agent skills: https://github.com/trustwallet/tw-agent-skills
- Trust Wallet blog TWAK launch: https://trustwallet.com/blog/announcements/introducing-the-trust-wallet-agent-kit-twak-your-ai-agent-can-now-act-on-crypto
- BNB AI Agent SDK: https://github.com/bnb-chain/bnbagent-sdk
- BNBChain MCP server: https://github.com/bnb-chain/bnbchain-mcp
- BNBChain Skills: https://github.com/bnb-chain/bnbchain-skills
- BNB Chain LangChain agentkit: https://github.com/node-real/bnb-chain-agentkit
- CMC AI Agent Hub docs: https://coinmarketcap.com/api/documentation/ai-agent-hub
- CMC MCP docs: https://coinmarketcap.com/api/documentation/ai-agent-hub/mcp
- CMC Skills catalog: https://github.com/coinmarketcap-official/skills-for-ai-agents-by-CoinMarketCap
- DoraHacks hackathon detail: https://dorahacks.io/hackathon/bnbhack-twt-cmc/detail
- CMC hackathon page: https://coinmarketcap.com/api/hackathon/
- Chainwire Jun 3: https://chainwire.org/2026/06/03/bnb-chain-launches-36000-hackathon-to-advance-on-chain-ai-trading-agents/
- TWAK x402 launch: https://trustwallet.com/blog/announcements/your-ai-agent-can-now-run-your-crypto-strategy-introducing-dca-automation-and-limit-orders-in-trust-wallet-agent-kit
- BNB AI Hack winners May 12: https://www.bnbchain.org/en/blog/congratulations-to-the-latest-bnb-ai-hack-winners-may-12-batch
- BNB AI Hack winners May 29: https://www.bnbchain.org/en/blog/congratulations-to-the-latest-bnb-ai-hack-winners-may-29-batch
- BNB Hack winners Sep 10: https://www.bnbchain.org/en/blog/congratulations-to-the-latest-bnb-hack-winners-september-10-batch
- Singularry GitHub: https://github.com/singularry/singularry
- Singularry BeInCrypto: https://beincrypto.com/singularry-agent-autonomous-defi-copilot/
- Singularry BeInCrypto DeFAI: https://beincrypto.com/defai-ai-agents-real-money-singularry/
- Bink AI GitHub: https://github.com/Bink-AI
- WORLD3 May 29 update: https://www.bnbchain.org/en/blog/congratulations-to-the-latest-bnb-ai-hack-winners-may-29-batch
- x402 explained: https://eco.com/support/en/articles/12328618-x402-protocol-explained-how-ai-agents-pay-onchain
- Daily brief 2026-06-19: /root/.openclaw/workspace/briefs/2026-06-19-deep-dig.md
