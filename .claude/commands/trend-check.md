---
description: Run a trend-monitoring sweep across the watchlist derived from active pipeline state, per guides/market/trend-monitoring.md. Categorizes findings as material / notable / background and recommends downstream commands for any material findings.
argument-hint: [optional: "triggered <reason>" for an emergency sweep instead of a scheduled one]
---

You are about to run a trend sweep. Follow @guides/market/trend-monitoring.md exactly. Proceed with web research without asking permission per @CLAUDE.md (Internet access policy).

**Arguments:** $ARGUMENTS — if it starts with `triggered`, this is an emergency sweep; the rest is the trigger reason. Otherwise it is a scheduled sweep.

### Skip-check (do first)
- If the most recent `market-research/*/trends.md` is less than 4 days old AND this is a scheduled (not triggered) sweep, **skip and tell the user** instead of running.
- If no `status: active` scan exists AND no active cards or briefs exist in `ideas/` or the build folders, there is nothing to watch — **skip and tell the user**.

### Inputs to read for watchlist derivation
- The most recent `status: active` market scan at `market-research/*/scan.md` (newest by folder date)
- All cards under `ideas/*/<slug>.md` with `status: green-lit` or `status: in-validation` (active cards)
- All `<web-apps|mobile-apps>/<slug>/MVP.md` with `status` in `{draft, in-scoping, green-lit-to-build}` (active briefs)
- The most recent prior trend report — for the "last checked previously" column and to avoid re-surfacing already-known findings

### Do
1. Derive the watchlist from the active state. Write the categories and what they specifically watch at the top of the report.
2. Sweep all six watchlist categories in §3 of the trend guide. Time-box ~30-60 minutes equivalent of focused web work.
3. Categorize every concrete finding as **material**, **notable**, or **background** per §5.3. When in doubt, call something material only if you can name the affected artifact and the specific recommended action.
4. **Generate a run-id and create the folder:** `RUN_ID=$(python3 scripts/gen_run_id.py); mkdir -p market-research/$RUN_ID`. Then write the report to `market-research/$RUN_ID/trends.md` per §6 (with `run-id: $RUN_ID` in the frontmatter).

### Stop here — user checkpoint
After writing the report, **stop**. Show the user:

> Trend sweep at `market-research/<run-id>/trends.md`. {sweep-type}.
>
> Material findings: {count}
> Notable findings: {count}
> Background findings: {count}
>
> Recommended next commands (if any):
> - <command 1 — for which finding>
> - <command 2>
>
> *(If no material findings: "No actions recommended this sweep — pipeline state is consistent with last sweep.")*

Do not auto-run any of the recommended commands. The user decides which to run.
