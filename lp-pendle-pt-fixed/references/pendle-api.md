# Pendle V2 API Reference

Source: https://docs.pendle.finance/pendle-v2-dev/Backend/ApiOverview
Verified live: 2026-06-21 10:09–10:13 UTC

## Base URL

`https://api-v2.pendle.finance/core/`

## Rate limits (free tier)

- **100 CU per minute**
- **200,000 CU per week**
- Response headers: `X-Computing-Unit`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `X-RateLimit-Weekly-Limit`, `X-RateLimit-Weekly-Remaining`, `X-RateLimit-Weekly-Reset`
- Most REST endpoints cost 1-5 CU. The Hosted SDK (transaction generation) has dynamic costs.
- 429s: exponential backoff recommended.

## Endpoints used by `lp-pendle-pt-fixed`

### GET /v1/{chainId}/markets/active — list all active PT markets on a chain

Chain IDs: 1 (Ethereum), 56 (BSC), 143 (Monad), 999 (Hyperliquid), 8453 (Base), 9745 (Plasma), 42161 (Arbitrum), 10 (Optimism), 146 (Sonic), 5000 (Mantle), 80094 (Berachain).

Response shape (per market):
```json
{
  "name": "sUSDat",
  "address": "0x1017e73ce9c219164ce841a980136eb023c55387",
  "expiry": "2026-08-27T00:00:00Z",
  "pt": "56-0x23f9a497a5d4d54eaf5e03d94774f17dc1219745",
  "yt": "56-0x11550114dc4c572e6c1eddfbcdbed9480f4847da",
  "sy": "56-0x68930887e1318ef30653a4b7942ab07544ebed4d",
  "underlyingAsset": "56-0x9cd57d3685e6868cacaa8bdcaaf52cbdebf4fa25",
  "details": {
    "liquidity": 2961210,
    "pendleApy": 0.0019,
    "impliedApy": 0.1498,
    "feeRate": 0.0029,
    "yieldRange": {"min": 0.08, "max": 0.19},
    "aggregatedApy": 0.1021,
    "maxBoostedApy": 0.105
  },
  "isNew": false,
  "isPrime": false,
  "timestamp": "2026-05-22T09:25:10Z",
  "categoryIds": ["stables"]
}
```

### GET /v3/{chainId}/markets/{address}/historical-data?timeframe=1d — backtest data

Timeframes: `1h`, `1d`, `1w`, `1m`.

Response shape:
```json
{
  "total": 722,
  "timestamp_start": "2026-05-22T09:00:00Z",
  "timestamp_end": "2026-06-21T10:00:00Z",
  "results": [
    {
      "timestamp": "2026-05-22T09:00:00Z",
      "maxApy": 0.0587,
      "baseApy": 0.0587,
      "underlyingApy": 0,
      "impliedApy": 0.13,
      "tvl": 1.186
    }
  ]
}
```

For sUSDat: 722 hourly observations, 30 days. Implied APY stable around 13-15%.

### GET /v2/markets/all — cross-chain markets (paginated)

For cross-chain discovery. `skip` and `limit` (max 100) params. 747 active markets total across all chains.

## Endpoints NOT used (but useful)

- `GET /v1/assets/all` — all assets across chains
- `GET /v1/prices/assets` — asset prices across chains (used for general price monitors)
- `GET /v5/{chainId}/transactions/{address}` — transaction history for an address

## Deprecated

- `GET /v1/markets/all` → use `/v2/markets/all`
- `GET /v1/markets/points-market` → folded into `/v2/markets/all`
- `GET /v2/{chainId}/markets/{address}/data` → use `/v3/{chainId}/markets/{address}/historical-data`
- `GET /v2/sdk/{chainId}/convert` (GET) → use `POST /v3/sdk/{chainId}/convert` (JSON body)

## Hosted SDK (transaction generation)

If the operator wants to wire this skill to a real execution layer, the Hosted SDK generates the
swap / liquidity / mint / redeem payloads. The agent constructs the calldata, the user signs and submits.

For Track 2 of the BNB Hack, **the spec is the deliverable** — the Hosted SDK is optional.
The agentic-commerce proof uses the x402 MCP for the CMC data side, but Pendle's Hosted SDK
is not exercised in the demo (the demo focuses on spec generation + x402 payment flow).
