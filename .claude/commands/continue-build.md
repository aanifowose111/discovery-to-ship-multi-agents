---
description: Resume an in-flight build for a specific product. Disambiguates between multiple products in the workspace by requiring an explicit slug. Reads BUILD_STATUS.md to find subsystem state, scans the source tree for the most recently modified files (so it knows what was last touched), and accepts an optional --hint "<text>" arg for explicit disambiguation. Invokes senior-software-engineer with the resumption context. Distinct from /start-build (initial orientation) and /recollect (read-only synthesis).
argument-hint: <product-slug> [--hint "<text>"] [--from <file-or-subsystem>]
---

You are about to resume an in-flight build for one product. This command is the canonical way to say "continue building X" when multiple products are mid-build in the workspace — `please continue` alone is ambiguous; this command names the product.

**Use this when:**
- A build was interrupted (you closed the session, hit a `please continue`-ambiguous state, took a break) and you want the orchestrator to pick up exactly where it left off.
- After `/rework` flipped some `[x]` subsystems back to `[>]` and you want them revisited against the reworked brief.
- After `/research-design` + `/draft-design-spec` landed mid-build (e.g., you skipped design at MVP time, then added it retroactively) and the frontend needs to revisit work against the new spec.

**Do NOT use this when:**
- The build has never started (no `BUILD_STATUS.md` exists) → use `/start-build <slug>` instead.
- You want a read-only synthesis of where the product is at without invoking the orchestrator → use `/recollect <slug>` instead.
- All subsystems are `[x]` → use `/ship-app <slug>` instead.

**Arguments:** $ARGUMENTS — the product slug, optionally followed by:
- `--hint "<text>"` — free-text user note about what was happening when work stopped ("we were mid-auth, JWT middleware was broken", "just finished tokens.css and was starting components.css"). Helps the orchestrator pick the right resumption point when subsystem-level state is ambiguous.
- `--from <file-or-subsystem>` — explicit override: continue from a specific file (e.g., `--from app/routes/auth.py`) or subsystem name (e.g., `--from "auth"`). Overrides the orchestrator's mtime-based guess.

Examples:
```
/continue-build ops-audit-agent
/continue-build ops-audit-agent --hint "we just finished the tokens and were starting per-surface CSS"
/continue-build ops-audit-agent --from app/static/css/components.css
```

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, stop: "No product folder for `<slug>`. Has the brief been scoped? Run `/scope-mvp <slug>` first." Resolve `<product-folder>` and `<stack>` (web/mobile/desktop).

2. **Locate the active brief.** Check `MVP.md` and `V1.md` in `<product-folder>`. Pick which is current per the same logic as `/start-build` step 1:

   | State | Brief in flight |
   |---|---|
   | Only `MVP.md` | `MVP.md` |
   | `MVP.md` `shipped` + `V1.md` `green-lit-to-build` or `in-v1-building` | `V1.md` |
   | `MVP.md` `shipped`, no `V1.md` | Stop: "MVP shipped, no v1 brief. If you want to continue past MVP, run `/scope-v1 <slug>` first." |
   | Neither | Stop: "No brief found. Run `/scope-mvp <slug>` first." |

3. **Verify `BUILD_STATUS.md` exists** at `<product-folder>/BUILD_STATUS.md`. If not, stop and tell the user: "No `BUILD_STATUS.md` found — build hasn't started yet. Run `/start-build <slug>` to begin (it'll ask the orientation questions and create the file). `/continue-build` resumes an existing build; it does not initiate one."

4. **Read `BUILD_STATUS.md`** and parse the subsystem checklist + frontmatter. Identify:
   - **`build-status` frontmatter value** (one of `building` / `rework-in-progress` / `ready-to-deploy` / `shipped` / unset).
   - **Subsystems in `[>]` state** — currently in-flight, the natural resumption point.
   - **Subsystems in `[ ]` state** — pending, ordered as the orchestrator scheduled them.
   - **Subsystems in `[x]` state** — completed (informational, not actionable).
   - **Rework-trigger subsystems** — any `[>]` whose most recent history entry is annotated `(audit: <id>)` meaning it was flipped back from `[x]` by `/rework`. These get priority resumption.

5. **Edge-case stops**:
   - **All subsystems are `[x]` AND `build-status: ready-to-deploy` or `shipped`:** stop and tell the user: "Build is complete (all subsystems `[x]`, `build-status: <value>`). Next step is `/ship-app <slug>`."
   - **No subsystems checked off (`[ ]` for all)** AND no `[>]`: this means `/start-build` was run but the first subsystem never started. Tell the user: "Build is initialized but no subsystem has started. Re-running `/start-build <slug>` will resurface the orientation + first subsystem suggestion."
   - **`build-status: rework-in-progress`** AND multiple `[>]` from rework flips: this is the expected post-`/rework` state. Continue normally — the orchestrator handles re-engaging specialists per the flipped subsystems.

6. **Scan for most-recently-modified files in the product folder.** Use `find <product-folder> -type f -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/.pytest_cache/*" -newer ... | sort -rn` — or `ls -lt` — to identify the **top 5-10 most recently modified files** by mtime. Capture: file path, mtime (relative — "3 minutes ago" / "47 minutes ago" / "2 hours ago" / "1 day ago"). This gives the orchestrator concrete signal of *what code was last touched*, not just which subsystem was last marked. Example output:
   ```
   Most recent files (mtime-sorted):
   - app/static/css/components.css  (3 min ago)
   - app/static/css/tokens.css       (12 min ago)
   - app/templates/dashboard.html    (47 min ago)
   - app/routes/dashboard.py         (2 hr ago)
   - tests/test_dashboard.py         (2 hr ago)
   ```
   Pass this list to the orchestrator in step 7.

7. **Parse args**: extract `--hint "<text>"` and/or `--from <path>` if present. Both are optional. If both are provided, `--from` is the authoritative resumption point; `--hint` is supplementary context.

### Do

Invoke the `senior-software-engineer` subagent in **resumption mode** using the custom-subagent invocation pattern in `CLAUDE.md`:

```
Agent({
  subagent_type: "general-purpose",
  description: "Resume build for <slug>",
  prompt: "You are about to act as the senior-software-engineer RESUMING the build of <slug>. Read .claude/agents/senior-software-engineer.md in full and treat its body as your role — pay particular attention to the § Reviewer routing section, which gates subsystem [>] → [x] flips on security + QA reviewer verdicts per guides/product/build-status-methodology.md §6. Read the team file at <product-folder>/team.json — use named members in narration when set, role labels otherwise. Read the active brief at <path-to-brief> (resolved per pre-flight step 2 — MVP.md or V1.md). Read <product-folder>/BUILD_STATUS.md in full — its subsystem checklist + History is your map of what's done and what's next. **PENDING REVIEWS GATE:** Before resuming any new implementation work, check BUILD_STATUS.md `pending-reviews:` frontmatter AND per-subsystem `security-review-required: true` / `qa-review-required: true` flags. If any subsystem is in `[>]` state waiting on a reviewer verdict, resolve those reviews FIRST per guides/product/build-status-methodology.md §6 — invoke the relevant reviewer(s) in build-phase review mode before moving the build forward. Surface this to the user explicitly in your summary: 'Found N pending reviews from prior session: <list>. Resolving these first before resuming <next-subsystem>.' **VERIFIED.md SOFT CHECK:** read <product-folder>/VERIFIED.md if it exists per guides/product/verified-features-methodology.md §5; surface any `[!]` (verified-not-working) entries in your resumption summary as 'verification flags from prior session.' Do NOT hard-gate on `[!]` — these are warnings, not blockers. Also surface 'verification gaps' (any BUILD_STATUS.md `[x]` subsystem with zero VERIFIED.md entries) as a soft signal — the user may want to walk through those with `/do-verify <slug>`. Read the design artifact authoritative for the brief's design-path: claude-led → <product-folder>/design/DESIGN_SPEC.md (this is the build's source of truth for visual + interaction design, SUPERSEDES frontend-ui-engineering defaults); hired → <product-folder>/design/handoff/tokens.json + screenshots/; hybrid-light-refresh → <product-folder>/design/DESIGN_RESEARCH.md. Read CLAUDE.md for workspace conventions. **Recent file activity (mtime-sorted, captured pre-flight)**: <paste the list from pre-flight step 6 here verbatim — this tells you what code was actually being touched most recently>. **User hint (optional)**: <if --hint was provided, paste the text; else 'none'>. **User --from override (optional)**: <if --from was provided, paste the value; else 'none'>. Do NOT ask the orientation questions from /start-build — those were answered at build initialization and the answers live in BUILD_STATUS.md. Instead: (1) Summarize in 5-7 lines what has been done so far (completed subsystems with brief outcomes), what is currently mid-flight ([>] subsystems), what is next ([ ] subsystems in scheduled order), AND name the 2-3 most recently modified files so the user sees you've located the exact resumption point. (2) Identify which specialist persona should resume immediately — the one(s) owning the [>] subsystems if any, OR the one owning the next [ ] subsystem if none are mid-flight, biased by which file was most recently touched (e.g., if `app/static/css/components.css` was last touched 3 min ago, frontend specialist is mid-flight on CSS). (3) Honor the user's --from override if provided: the proposed resumption point IS that file/subsystem, not what your inference would otherwise suggest. (4) If --hint was provided, bake it into your interpretation ('per your hint, you were starting per-surface CSS — components.css is next on the spec's per-surface block for the dashboard surface'). (5) If build-status is rework-in-progress, name the subsystems flipped back from [x] (per History entries annotated with `(audit: <id>)`) and the order in which they should be revisited. (6) If a new DESIGN_SPEC.md landed mid-build (mtime after the last successful subsystem completion), explicitly call out that frontend subsystems may need to be revisited against the new spec. (7) Propose the immediate next action — name the file (or files) to touch next, the specialist persona to invoke, and a one-line rationale. (8) Wait for the user to confirm or override before invoking any further specialist."
})
```

### Stop here — user checkpoint

After the orchestrator returns its resumption summary, **stop**. Show the user:

> Build resumed for **<slug>** (stack: <web|mobile|desktop>).
>
> **Current state:**
> - Completed: <list completed subsystems, ~5 max — fold rest as "+ N more">
> - In progress (`[>]`): <list>
> - Next pending (`[ ]`): <first 2-3>
>
> **Most recent file activity:**
> - <file 1>  (<relative mtime>)
> - <file 2>  (<relative mtime>)
> - <file 3>  (<relative mtime>)
>
> **Build status:** `<frontmatter value or "building">`
> <if --hint was provided:> **Your hint:** "<text>"
> <if --from was provided:> **Your --from override:** `<path or subsystem>` (used as authoritative resumption point)
>
> **Orchestrator recommends resuming with:**
> <specialist persona> on <subsystem> — next file: `<path>` — <one-line rationale>
>
> Your call:
> - **Confirm** → I invoke `<specialist>` to resume from `<path>`.
> - **Override** → tell me which file / subsystem / specialist you'd rather resume with. (You can also re-run with `--from <path>` for the same effect.)
> - **Discuss** → I can have `senior-software-engineer` go deeper on the tradeoffs.

Wait for the user's response before invoking any further specialists.

### Notes

- **No team-naming pre-flight on resume.** Team members were named (or skipped) at `/start-build` time. If a previously-unnamed member is about to be engaged for the first time on this resume, the just-in-time naming prompt fires per `/start-build`'s team-naming section.
- **No audit-log append.** Resumes are not milestones — they're continuations. Subsystem completions and ready-to-deploy state still emit `build-milestone` entries (per `CLAUDE.md` § Audit log) when they happen.
- **For mobile or desktop builds**, this command works the same way — `BUILD_STATUS.md` is the per-product source of truth regardless of stack.
- **If `/continue-build` is invoked while a previous `please continue` was actively in flight** (a tool call was running when the user closed the session, say), the orchestrator surfaces this in its summary and the user can confirm whether to redo the interrupted work or skip past it.
