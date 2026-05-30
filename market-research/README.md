# market-research/

Reports produced by the pipeline commands. **This folder is gitignored** (except this README) — your research outputs are personal and never enter git.

## File types

| Pattern | Produced by | Defined in |
|---|---|---|
| `scan-<date>.md` | `/scan` | `guides/market/market-scan-methodology.md` |
| `triage-<date>.md` | `/discover` | `guides/product/idea-discovery-methodology.md` §6 |
| `validation-<slug>-<date>.md` | `/validate-card <slug>` | `guides/product/idea-validation-methodology.md` §7 |
| `scoping-<slug>-<date>.md` | `/scope-mvp <slug>` | `guides/product/mvp-scoping-methodology.md` §9 |
| `trends-<date>.md` | `/trend-check` | `guides/market/trend-monitoring.md` §6 |

All reports are date-stamped. Multiple of the same type accumulate over time.

## Lifecycle

Reports use a `status` frontmatter field that varies by report type. Common values:

- `draft` — produced by the command, awaiting user sign-off.
- `active` (scan reports) — signed off; feeds the next discovery cycle.
- `acted-on` (trend reports) — recommended actions are queued or executed.
- `reviewed` — read by the user, no further action expected.

## Commands

See `CLAUDE.md`'s "Pipeline orchestration & checkpoints" for which command produces and reads each report type.
