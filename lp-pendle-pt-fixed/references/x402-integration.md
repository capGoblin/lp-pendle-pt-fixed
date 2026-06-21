# x402 Pay-Per-Request Integration

Source: https://raw.githubusercontent.com/openCMC/skills-for-ai-agents-by-CoinMarketCap/main/skills/cmc-x402/SKILL.md
Verified live: 2026-06-21 10:02 UTC

## What is x402?

x402 is an open payment protocol from Coinbase that enables automatic stablecoin payments over HTTP.
Instead of managing API keys, the agent pays $0.01 USDC per request on Base.

This is the **agentic-commerce angle** for the BNB Hack Track 2 demo. The agent doesn't just pull data —
it pays for it, on-chain, in real time. That's the differentiator.

## Endpoints

### REST

Base URL: `https://pro.coinmarketcap.com`

| Endpoint | Path | Use For |
|---|---|---|
| Quotes | `/x402/v3/cryptocurrency/quotes/latest` | Current prices for specific coins |
| Listings | `/x402/v3/cryptocurrency/listing/latest` | Top coins by market cap |
| DEX Search | `/x402/v1/dex/search` | Find DEX tokens by keyword |
| DEX Pairs | `/x402/v4/dex/pairs/quotes/latest` | DEX pair trading data |

### MCP (for AI agents)

Connection URL: `https://mcp.coinmarketcap.com/x402/mcp`
Transport: Streamable HTTP (POST)

## Quick start (TypeScript)

```bash
npm install @x402/axios @x402/evm viem
```

```typescript
import { createX402AxiosClient } from "@x402/axios";
import { ExactEvmScheme, toClientEvmSigner } from "@x402/evm";
import { privateKeyToAccount } from "viem/accounts";
import { createPublicClient, http } from "viem";
import { base } from "viem/chains";

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);
const publicClient = createPublicClient({ chain: base, transport: http() });
const signer = toClientEvmSigner(account, publicClient);

const client = createX402AxiosClient({
  schemes: [new ExactEvmScheme(signer)],
});

const response = await client.get(
  "https://pro.coinmarketcap.com/x402/v3/cryptocurrency/quotes/latest",
  { params: { symbol: "BTC,ETH" } }
);

console.log(response.data);
```

## Pricing

- $0.01 USDC per request on Base (chain 8453)
- Payment only on successful data delivery (no charge for failed requests)
- Need: USDC on Base + small amount of ETH on Base for gas

## Demo flow for BNB Hack Track 2

1. User prompt: "Find the best fixed-yield PT on BSC for $10K capital."
2. Agent decides to use `mcp__cmc-mcp__get_global_metrics_latest` for the regime tag.
3. Agent has a USDC balance on Base.
4. Agent calls `https://mcp.coinmarketcap.com/x402/mcp` with the request.
5. MCP returns 402 Payment Required with payment instructions.
6. Agent's wallet signs the $0.01 USDC payment (and a small ETH gas fee).
7. MCP returns the data.
8. Agent continues: calls Pendle API directly (no payment, public).
9. Agent reasons across 6 active PT markets, applies the safety filter, picks sUSDat.
10. Agent outputs the JSON spec.
11. Agent's response includes the x402 payment tx hash as proof.

## Why this matters for the judges

The BNB Hack explicitly calls out x402 as an **optional** capability for Track 2. Most Track 2 entries
will be "I generated a spec, here's the data." The x402 angle says: "My agent autonomously pays for data,
on-chain, in real time, without an API key — this is what AI agent commerce looks like in production."

That's the wedge.
