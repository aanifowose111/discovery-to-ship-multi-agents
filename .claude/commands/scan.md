---
description: Run a market scan to produce candidate territories for the next discovery cycle, per guides/market/market-scan-methodology.md. Defaults to a broad scan; pass "focused" + a topic for a focused scan.
argument-hint: [broad|focused <topic>]
---

You are about to run a market scan. Follow the methodology in @guides/market/market-scan-methodology.md exactly. The user does *not* need to be in the loop for the source sweep itself — proceed without asking permission for web fetches per @CLAUDE.md (Internet access policy).

**Arguments:** $ARGUMENTS — parse as aperture and optional focus. If empty, default to `aperture: broad`. If first word is `focused`, the rest is the focus topic.

### Inputs to read before sweeping
- @CLAUDE.md (working style and pipeline rules — **NOT** for founder-fit context; see warning in §1 of *Do* below).
- The most recent scan: search for `market-research/*/scan.md` (one per scan run folder); pick the newest by folder date.
- The most recent trend report: search for `market-research/*/trends.md`; pick the newest by folder date.
- Recent `ideas/killed/` entries — for filter calibration; do not re-surface territories whose ideas have systematically failed

### Do
1. **Establish founder-fit context first** — this scopes territory prioritization. In order:
   1. **Check `user-context/INTERESTS.md`** — if it exists, this is the canonical source for the current user's background, strengths, and product interests. Use it as the founder-fit lens.
   2. **If `user-context/INTERESTS.md` does not exist**, surface to the user:
      > No `user-context/INTERESTS.md` found. You have two options:
      > (a) **Open scan** — I sweep without applying any founder-fit filter and produce territories rated only on freshness × reachability. The output is broader and less personally targeted; you can refine later.
      > (b) **Tell me your context now in 1-3 sentences** (your background, interests, the kind of product you'd be excited to build) — I'll use that as the founder-fit lens just for this scan, and you can later populate `user-context/INTERESTS.md` from `user-context/INTERESTS.md.example` to make it persistent.
      >
      > Which would you like? (Default to (a) if no reply within the same turn.)

   **Important — do NOT use the `CLAUDE.md` owner intro (`This directory is ... owned by Abiodun Anifowose ... currently works at Mercor, where he designs and develops advanced algorithms for training AI models...`) as the founder-fit source.** That line is *attribution to the maintainer*, not the current user's context. Forkers will inherit it but it does not apply to them. The canonical source is `user-context/INTERESTS.md`; if absent, ask or fall back to the open-scan mode above. **Never silently pull the maintainer's context into a forker's scan output.**

   Record which source was used at the top of the report's *Aperture* section: e.g., "Founder-fit lens: `user-context/INTERESTS.md`" or "Founder-fit lens: open scan (no user-context found)" or "Founder-fit lens: inline-provided context this run".
2. Set the aperture and write it down at the top of the report.
3. Run the source sweep across all families in §5.2 of the methodology guide. Cite URLs inline.
4. Aggregate signals into candidate territories (3-7 in the final list). Each must have: segment, anchor, distribution channel, founder fit (or "n/a — open scan"), priority.
5. Prioritize each territory on freshness × founder fit × reachability. Lowest dimension wins. **For open-scan mode (no founder-fit lens), prioritize on freshness × reachability only.**
6. **Generate a run-id and create the folder** for this scan: run `RUN_ID=$(python3 scripts/gen_run_id.py); mkdir -p market-research/$RUN_ID`. Then write the report to `market-research/$RUN_ID/scan.md` with `status: draft` and `run-id: $RUN_ID` in the frontmatter.
7. Show the user: the founder-fit source used, the aperture, the source sweep table, the candidate territories with priorities, the recommended 2-3 seeds for the next discovery cycle.

### Stop here — user checkpoint
After showing the summary, **stop**. Do not advance the report status to `active`. Do not start a discovery cycle. Tell the user:

> Scan report at `market-research/<run-id>/scan.md`. Sign off to advance status to `active`. Next step after sign-off: `/discover` to mine the recommended seeds for ideas (or pass specific territories: `/discover <territory-name>[, <territory-name>]`).

Only after the user signs off, update the report's `status` field to `active`.
