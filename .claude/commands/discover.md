---
description: Run a product discovery cycle against the active market scan, producing idea cards and a triaged candidate list per guides/product/idea-discovery-methodology.md. Optionally restrict to specific territories from the scan.
argument-hint: [comma-separated territory names — defaults to the scan's recommended seeds]
---

You are about to run a discovery cycle. Follow the methodology in @guides/product/idea-discovery-methodology.md exactly. Proceed with web research without asking permission per @CLAUDE.md (Internet access policy).

**Arguments:** $ARGUMENTS — comma-separated territory names from the active scan. If empty, default to the *Recommended seeds* from the most recent `status: active` scan.

### Inputs to read before brainstorming
- @CLAUDE.md (user profile, founder fit)
- The most recent `status: active` market scan at `market-research/scan-*.md` — for territories, anchors, and channel notes
- The most recent `market-research/trends-*.md` (if any) — fresh capability shifts to fold into ideation
- Existing `ideas/*.md` (active and `ideas/killed/`) — do not duplicate, and respect filter signals from past kills

### Do
1. **Determine the seed territories.** In order:
   - If `$ARGUMENTS` is non-empty, parse it as a comma-separated territory list and use those.
   - Else, look for the most recent `market-research/scan-*.md` with `status: active`. If found, use its *Recommended seeds* section.
   - Else (no args, no active scan), do an **inline lightweight scan**. Determine the founder-fit context for *this specific clone of the workspace* in this order:
     1. **Check `user-context/INTERESTS.md`** — if it exists, this is the canonical source for the current user's professional background, hobbies, domain expertise, and prior product ideas. Use it as the primary anchor for territory selection. (Per `user-context/README.md`: that file is gitignored, so forkers populate it for themselves; it is NOT the maintainer's context bleeding through.)
     2. **If `user-context/INTERESTS.md` does not exist**, surface to the user:
        > No `user-context/INTERESTS.md` found. You have two options:
        > (a) **Open discovery** — I brainstorm broadly from current capability shifts + adjacent workflows + competitor weaknesses, with no founder-fit constraint. Less personally relevant but a fine starting point.
        > (b) **Tell me your context now in 1-3 sentences** (your background, interests, the kind of product you'd be excited to build) — I use that as the seed, just for this run. You can later populate `user-context/INTERESTS.md` from the template (`user-context/INTERESTS.md.example`) so this is persistent for the next time.
        >
        > Which would you like? (Default to (a) if no reply within the same turn.)

     Once the founder-fit source is determined, also read the most recent `market-research/trends-*.md` (if any) and any recent kills in `ideas/killed/`. Pick 2-3 fresh candidate territories grounded in (a) the user's context per the source above and (b) recent capability/regulatory/funding shifts you can cite.

     Write a note at the top of the triage list explaining which source was used: "No active scan; territories derived inline from `<source>` + recent trends. Consider running `/scan` for a deeper foundation before the next discovery cycle." This makes `/discover` work as a one-command bootstrap when the user has not yet run a scan.

   Write the chosen territories at the top of your scratch notes.

   **Important — do NOT use the `CLAUDE.md` owner intro (`This directory is ... owned by Abiodun Anifowose ... currently does chemistry-reasoning eval work at Mercor`) as the founder-fit source.** That line is *attribution to the maintainer*, not the current user's context. Forkers will inherit it but it does not apply to them. The canonical source for the current user's context is `user-context/INTERESTS.md`; if absent, ask or fall back to open discovery as described above.
2. Brainstorm idea cards. **At least 10 cards**, drawn from at least three sources in §3 of the discovery guide. Tag each card's source territory in its frontmatter (add a `territory: <name>` field to the card frontmatter, *in addition* to the fields the guide already specifies).
3. Write each card to `ideas/<slug>.md` per the format in §4 of the discovery guide. Cite URLs in *Problem*, *Current alternatives*, and *Distribution hypothesis* per §3.1.
4. Score every card on the §5 rubric. Bucket as green / yellow / red. Apply the hard-kill rules.
5. Write the triage list to `market-research/triage-<YYYY-MM-DD>.md` with the *Top 3 callout* at the top.
6. Move red-bucket cards to `ideas/killed/<slug>.md` with a one-line reason in the card.

### Stop here — user checkpoint
After writing the triage list, **stop**. Do not start validation on any card. Show the user:

> Discovery cycle complete. {N} cards drafted in `ideas/`, triage at `market-research/triage-<YYYY-MM-DD>.md`. Top 3:
> 1. <slug — one-line reason>
> 2. <slug — one-line reason>
> 3. <slug — one-line reason>
>
> Sign off on the top 3, then I run `/validate-card <slug>` for each (parallelizable). You can also override the top 3 if you want a different card validated first.

Wait for the user's go-ahead before invoking `/validate-card`.
