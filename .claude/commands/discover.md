---
description: Run a product discovery cycle against the active market scan, producing idea cards and a triaged candidate list per guides/product/idea-discovery-methodology.md. Optionally restrict to specific territories from the scan.
argument-hint: [comma-separated territory names — defaults to the scan's recommended seeds]
---

You are about to run a discovery cycle. Follow the methodology in @guides/product/idea-discovery-methodology.md exactly. Proceed with web research without asking permission per @CLAUDE.md (Internet access policy).

**Arguments:** $ARGUMENTS — comma-separated territory names from the active scan. If empty, default to the *Recommended seeds* from the most recent `status: active` scan.

### Inputs to read before brainstorming
- @CLAUDE.md (user profile, founder fit)
- The most recent `status: active` market scan at `market-research/*/scan.md` (look across run folders, newest first) — for territories, anchors, and channel notes. **First check the folder is non-empty** (zsh errors on unmatched globs — see CLAUDE.md "Cross-shell safety"), then probe. Cross-shell-safe pattern: `ls market-research/ 2>/dev/null` to confirm run-folders exist, then `python3 -c "import glob; [print(p) for p in glob.glob('market-research/*/scan.md') if 'status: active' in open(p).read()]" | head -1`. If output is empty, fall back to the inline lightweight scan described in step 1.
- The most recent `market-research/*/trends.md` (if any) — fresh capability shifts to fold into ideation. Same guard: `ls market-research/ 2>/dev/null` first, then `python3 -c "import glob; print('\n'.join(sorted(glob.glob('market-research/*/trends.md'), key=lambda p: -__import__('os').path.getmtime(p))))" | head -1`.
- Existing `ideas/*.md` (active and `ideas/killed/`) — do not duplicate, and respect filter signals from past kills

### Do
1. **Determine the seed territories.** In order:
   - If `$ARGUMENTS` is non-empty, parse it as a comma-separated territory list and use those.
   - Else, look for the most recent `market-research/*/scan.md` with `status: active`. If found, use its *Recommended seeds* section.
   - Else (no args, no active scan), do an **inline lightweight scan**. Determine the founder-fit context for *this specific clone of the workspace* in this order:
     1. **Check `user-context/INTERESTS.md`** — if it exists, this is the canonical source for the current user's professional background, hobbies, domain expertise, and prior product ideas. Use it as the primary anchor for territory selection. (Per `user-context/README.md`: that file is gitignored, so forkers populate it for themselves; it is NOT the maintainer's context bleeding through.)
     2. **If `user-context/INTERESTS.md` does not exist**, surface to the user:
        > No `user-context/INTERESTS.md` found. You have two options:
        > (a) **Open discovery** — I brainstorm broadly from current capability shifts + adjacent workflows + competitor weaknesses, with no founder-fit constraint. Less personally relevant but a fine starting point.
        > (b) **Tell me your context now in 1-3 sentences** (your background, interests, the kind of product you'd be excited to build) — I use that as the seed, just for this run. You can later populate `user-context/INTERESTS.md` from the template (`user-context/INTERESTS.md.example`) so this is persistent for the next time.
        >
        > Which would you like? (Default to (a) if no reply within the same turn.)

     Once the founder-fit source is determined, also read the most recent `market-research/*/trends.md` (if any) and any recent kills in `ideas/killed/*/`. Pick 2-3 fresh candidate territories grounded in (a) the user's context per the source above and (b) recent capability/regulatory/funding shifts you can cite.

     Write a note at the top of the triage list explaining which source was used: "No active scan; territories derived inline from `<source>` + recent trends. Consider running `/scan` for a deeper foundation before the next discovery cycle." This makes `/discover` work as a one-command bootstrap when the user has not yet run a scan.

   Write the chosen territories at the top of your scratch notes.

   **Important — do NOT use the `CLAUDE.md` owner intro (`This directory is ... owned by Abiodun Anifowose ... currently works at Mercor, where he designs and develops advanced algorithms for training AI models...`) as the founder-fit source.** That line is *attribution to the maintainer*, not the current user's context. Forkers will inherit it but it does not apply to them. The canonical source for the current user's context is `user-context/INTERESTS.md`; if absent, ask or fall back to open discovery as described above.

1b. **Check `user-context/IDEAS.md` for seed ideas — choose a mode.** If `user-context/IDEAS.md` exists AND is non-empty (the user has populated it beyond the template placeholders), surface a mode choice via `AskUserQuestion`:

   > Your `user-context/IDEAS.md` has seed ideas. How should this discovery cycle handle them?
   >
   > (a) **Promote seeds** — skip the brainstorming step. Convert each seed idea in `IDEAS.md` into a formal card in `ideas/<run-id>/<slug>.md` per the §4 card format, score on the §5 rubric, and triage. The fastest path when you already know what you want to validate. The "≥10 cards" requirement does NOT apply in this mode — you get however many seeds you have.
   >
   > (b) **Full discovery (ignore seeds)** — brainstorm 10+ candidates from territories / trends / capability shifts as usual. Use when seeds feel stale or you want a fresh angle.
   >
   > (c) **Hybrid + compare** — brainstorm 10+ candidates AND include each seed idea as a card. The triage table compares them side-by-side (which territory each came from, score, bucket, recommendation). Best for "I have ideas but want to see how they stack up against what's out there right now." (Recommended default.)

   Record the chosen mode at the top of the triage report as a "Mode:" line and follow the matching path below:

   - **Mode (a) Promote seeds:** read each entry from `IDEAS.md`, draft a card slug for it (verify with `check_slug.py`), and create one `ideas/<run-id>/<slug>.md` per seed. Use the seed text to populate *Problem*, *Current alternatives*, *Solution hypothesis*, and *Distribution hypothesis* — supplement with web research where the seed is thin (cite URLs). Tag `source: user-context/IDEAS.md` in frontmatter (instead of the brainstorm-source tag). Then **skip step 2 below** and go straight to step 3.
   - **Mode (b) Full discovery:** proceed with step 2 as written — ignore IDEAS.md entirely.
   - **Mode (c) Hybrid + compare:** proceed with step 2 to brainstorm 10+ candidates, THEN add one card per seed idea on top (same conversion logic as mode (a), tagged `source: user-context/IDEAS.md`). When you write the triage in step 5, add a "Seeds vs. brainstormed candidates" subsection that compares them on the same rubric and calls out: (i) which seeds rank above any brainstormed candidate, (ii) which brainstormed candidates make a seed look weaker, (iii) which seeds and candidates overlap territory-wise.

   If `IDEAS.md` does not exist or contains only the example placeholders, skip this step silently — the cycle proceeds as full discovery (mode b implicit).
2. Brainstorm idea cards. **At least 10 cards**, drawn from at least three sources in §3 of the discovery guide. Tag each card's source territory in its frontmatter (add a `territory: <name>` field to the card frontmatter, *in addition* to the fields the guide already specifies). **Skipped when mode (a) was chosen in step 1b.**
3. **Generate a single run-id for this discovery cycle** (the same id is shared by the cards in `ideas/<run-id>/` and the triage + downstream validations/scopings in `market-research/<run-id>/`): run `RUN_ID=$(python3 scripts/gen_run_id.py); mkdir -p ideas/$RUN_ID market-research/$RUN_ID`. Write each card to `ideas/$RUN_ID/<slug>.md` per the format in §4 of the discovery guide (with `run-id: $RUN_ID` in the frontmatter). Cite URLs in *Problem*, *Current alternatives*, and *Distribution hypothesis* per §3.1. Before generating each slug, verify availability with `python3 scripts/check_slug.py <proposed-slug>`.
4. Score every card on the §5 rubric. Bucket as green / yellow / red. Apply the hard-kill rules.
5. Write the triage list to `market-research/$RUN_ID/triage.md` (same `$RUN_ID` as the cards folder) with the *Top 3 callout* at the top and `run-id: $RUN_ID` in the frontmatter. For mode (c), include the "Seeds vs. brainstormed candidates" subsection described in step 1b.
6. Move red-bucket cards to `ideas/killed/<run-id>/<slug>.md` with a one-line reason in the card.

### Stop here — user checkpoint
After writing the triage list, **stop**. Do not start validation on any card. Show the user:

> Discovery cycle complete. {N} cards drafted in `ideas/<run-id>/`, triage at `market-research/<run-id>/triage.md` (run-id: `<run-id>`). Top 3:
> 1. <slug — one-line reason>
> 2. <slug — one-line reason>
> 3. <slug — one-line reason>
>
> Sign off on the top 3, then I run `/validate-card <slug>` for each (parallelizable). You can also override the top 3 if you want a different card validated first.

Wait for the user's go-ahead before invoking `/validate-card`.
