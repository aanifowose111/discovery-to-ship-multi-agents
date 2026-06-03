---
description: Renders a condensed in-terminal walkthrough of the workspace end-to-end — covering the pipeline phases, slash commands, scripts, helper skills, conventions, and the reviewer-decision model. Uses the user's current pipeline state as concrete examples where possible. Always points the user to the permanent DOCUMENTATION.md at the repo root for the deeper full reference. **This command bypasses the first-launch onboarding interrupt** (the only command that does — forcing onboarding before letting users read about it would be circular).
argument-hint: (no arguments)
---

You are about to render the workspace's end-to-end documentation in the terminal. This is the **only command that bypasses the first-launch onboarding interrupt** described in CLAUDE.md §Session continuity → Rule A. If `user-context/INTERESTS.md` is missing, do NOT trigger onboarding for this command — render the documentation directly. The documentation itself explains the onboarding workflow and why it matters.

### Inputs to read before rendering

1. **`DOCUMENTATION.md` at the repo root** — this is the source of truth for content. Your job is to render a condensed in-terminal version that:
   - Covers the same 15-section structure
   - Uses tables and "what to do" blocks generously, in the same style as DOCUMENTATION.md
   - References the user's *actual current state* as concrete examples (see step 2)
   - Closes with a clear pointer to `DOCUMENTATION.md` for the full reference
2. **Survey the user's current state** — use these commands so you can inject the user's real artifacts as examples in the relevant sections:
   - `ls market-research/` and per-run-folder listings to see active scans, triages, validations, scopings, trends
   - `ls ideas/` and `ls ideas/killed/` to see active and killed cards
   - `ls web-apps/ mobile-apps/ desktop-apps/` to see in-flight builds
   - `ls user-context/INTERESTS.md user-context/IDEAS.md user-context/POLICY.md 2>/dev/null` to see whether user-context is populated
3. **Read `CLAUDE.md`** (auto-loaded) for pipeline orchestration conventions you may need to reference.

### Do

Render the documentation in the terminal as a structured markdown response. Target ~300–450 lines. Use the same headings as DOCUMENTATION.md so users can cross-reference, but be more concise. The structure to follow:

1. **Top of response** — a short header noting that the same content (more thorough) is at `DOCUMENTATION.md` and that this is the condensed version personalized to the user's current state.
2. **§1 Welcome** — one paragraph summary
3. **§2 60-second workflow** — keep the ASCII flow diagram from DOCUMENTATION.md but trim narrative
4. **§3 User-context onboarding** — explain INTERESTS.md / IDEAS.md / POLICY.md; cite whether the *user's* live files exist or are missing (concrete personalization)
5. **§4 System requirements + setup** — table of `/system-check` + `/setup` + `/acknowledge-contributing`
6. **§5 Phase 1 — Discovery & Validation** — one subsection per command. For each:
   - Brief "what it does"
   - "What you input" code block
   - "What comes out" path
   - One or two status meanings + when to stop
   - **If the user has real artifacts at this phase, reference them as the example**. E.g., when describing `/validate-card`, if the user has `market-research/<run-id>/validation-bench-watch.md`, name it and use it as the concrete example. If the user has no artifacts at this phase yet, use a placeholder slug and note that.
7. **§6 Phase 2 — Initial MVP Build** — this is the heaviest section. Cover:
   - 6.1 What "build" means in plain English (1 paragraph + 1 table)
   - 6.2 Stack choices (compact table: web/mobile/desktop defaults + when to pick each)
   - 6.3 `/start-build` walkthrough (steps 1-5 condensed)
   - 6.4 The senior-engineer personas (table)
   - 6.5 Following along when you don't code (signs going well / badly tables + practical tips)
   - 6.6 When Fijara makes sense (when-to-pick list)
   - 6.7 `BUILD_STATUS.md` (one paragraph + checklist of what's in it)
   - 6.8 `/preview-product` (table per stack)
8. **§7-9 Phases 3-5** — compact summaries, table-driven
9. **§10 Trend monitoring** — short
10. **§11 Reviewer-decision model** — IMPORTANT: cover this in detail (it's the most-asked-about concept). Include the verdict-pattern table. If the user has real validation reports with mixed verdicts, use them as concrete examples in the verdict-pattern section.
11. **§12 Workspace conventions** — compact bullets covering slug uniqueness, run-id grouping, personal vs shared, status frontmatter
12. **§13-14 Utility commands + scripts + helper skills** — tables
13. **§15 Common scenarios + troubleshooting + going deeper** — pick the 3-4 most useful scenarios; the troubleshooting table from DOCUMENTATION.md; the methodology guides table

### Important — use the user's actual state for personalization

When you survey the user's current state in step 2 above, look for these concrete personalization opportunities and weave them into the rendered documentation:

| User state to look for | Where to use it as an example |
|---|---|
| Active idea cards in `ideas/<run-id>/` | §5.2 (`/discover`) and §11 (when describing what cards look like) |
| Validation reports in `market-research/<run-id>/validation-*.md` | §5.3 (`/validate-card`) — name specific cards (e.g., "your bench-watch validation"), and §11 if their verdict patterns illustrate the model |
| Scoping reports in `market-research/<run-id>/scoping-*.md` | §5.4 (`/scope-mvp`) |
| Scan reports in `market-research/<run-id>/scan.md` | §5.1 (`/scan`) |
| In-flight briefs in `web-apps/<slug>/MVP.md` etc. | §6 (`/start-build`) — but only if they exist |
| Killed cards in `ideas/killed/<run-id>/` | §11 (kill examples) |
| Missing `user-context/INTERESTS.md` | §3 — directly note "your INTERESTS.md is missing — this affects /scan and /discover quality" |

**If the user has no current state** (fresh repo), use placeholder slugs (`<your-slug>`) and add a one-line note in §5.2 like "you haven't run /discover yet — once you have idea cards, this section will reference them by name in future runs of /documentation."

### Stop here

After rendering the documentation, end with a closing block:

> The condensed version above lives in this terminal session only. The full version with deeper coverage of every phase, troubleshooting, common scenarios, and going-deeper pointers is at **`DOCUMENTATION.md`** at the repo root — open it in any markdown viewer or read it directly. You can re-run `/documentation` anytime to refresh the condensed view with your latest state as the examples.

Then propose 2-3 reasonable next actions based on the user's current state (e.g., "Populate `user-context/INTERESTS.md` to unblock targeted discovery" if missing, or "`/scope-mvp bench-watch` to advance your strongest validated card" if validations exist).

### Important — no auto-actions

- **NEVER** advance any artifact status as a side effect of this command.
- **NEVER** auto-invoke other slash commands.
- This command is read-only — it produces text in the terminal; it does not modify any file.
