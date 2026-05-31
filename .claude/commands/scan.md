---
description: Run a market scan to produce candidate territories for the next discovery cycle, per guides/market/market-scan-methodology.md. Defaults to a broad scan; pass "focused" + a topic for a focused scan.
argument-hint: [broad|focused <topic>]
---

You are about to run a market scan. Follow the methodology in @guides/market/market-scan-methodology.md exactly. The user does *not* need to be in the loop for the source sweep itself — proceed without asking permission for web fetches per @CLAUDE.md (Internet access policy).

**Arguments:** $ARGUMENTS — parse as aperture and optional focus. If empty, default to `aperture: broad`. If first word is `focused`, the rest is the focus topic.

### Inputs to read before sweeping
- @CLAUDE.md (user profile, founder fit, working style)
- The most recent scan: search for `market-research/*/scan.md` (one per scan run folder); pick the newest by folder date.
- The most recent trend report: search for `market-research/*/trends.md`; pick the newest by folder date.
- Recent `ideas/killed/` entries — for filter calibration; do not re-surface territories whose ideas have systematically failed

### Do
1. Set the aperture and write it down at the top of the report.
2. Run the source sweep across all families in §5.2 of the methodology guide. Cite URLs inline.
3. Aggregate signals into candidate territories (3-7 in the final list). Each must have: segment, anchor, distribution channel, founder fit, priority.
4. Prioritize each territory on freshness × founder fit × reachability. Lowest dimension wins.
5. **Generate a run-id and create the folder** for this scan: run `RUN_ID=$(python3 scripts/gen_run_id.py); mkdir -p market-research/$RUN_ID`. Then write the report to `market-research/$RUN_ID/scan.md` with `status: draft` and `run-id: $RUN_ID` in the frontmatter.
6. Show the user: the aperture, the source sweep table, the candidate territories with priorities, the recommended 2-3 seeds for the next discovery cycle.

### Stop here — user checkpoint
After showing the summary, **stop**. Do not advance the report status to `active`. Do not start a discovery cycle. Tell the user:

> Scan report at `market-research/<run-id>/scan.md`. Sign off to advance status to `active`. Next step after sign-off: `/discover` to mine the recommended seeds for ideas (or pass specific territories: `/discover <territory-name>[, <territory-name>]`).

Only after the user signs off, update the report's `status` field to `active`.
