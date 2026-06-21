# lp-strategy-menu

**Portfolio allocator across the Pendle PT fixed-yield library on BSC.**

Combines `lp-pendle-pt-fixed` (sUSDat, 14.98% APY) and `lp-pendle-pt-fixed-usdat` (USDat, 8.35% APY) into a single portfolio spec.

## Risk profile templates

| Profile | sUSDat | USDat | Portfolio APY | Max DD |
|---|---|---|---|---|
| Conservative | 50% | 50% | 11.67% | -1.5% |
| **Balanced** (default) | **60%** | **40%** | **12.33%** | **-2.2%** |
| Aggressive | 80% | 20% | 13.65% | -3.8% |

## Quick start

```bash
# Balanced profile, $50K
python3 run_menu.py --capital 50000 --profile balanced

# Aggressive with risk-off overlay
python3 run_menu.py --capital 100000 --profile aggressive --regime risk-off

# JSON output for piping
python3 run_menu.py --capital 50000 --profile balanced --json > portfolio.json
```

## Live regime overlay (CMC integration)

- **risk-on** (BTC dom < 50%) — apply profile as-is
- **risk-off** (BTC dom > 60%) — shift 10% from sUSDat → USDat
- **stress** (Defi vol 24h drop > 30% WoW) — force 80% USDat / 20% sUSDat

## Files

- `SKILL.md` — the spec, loadable into any MCP agent
- `run_menu.py` — the implementation
- `examples/` — sample output specs (added in next commit)
