---
description: Kick off the build phase for a green-lit-to-build product. Invokes senior-software-engineer to ask the orientation questions (web/mobile/desktop/hybrid order, MVP vs. fully-featured, build-first subsystem), then routes work to the right senior-engineer persona. Use after /scope-mvp returns green-lit-to-build, or at any point in the build when you want a fresh "where do I start" prompt.
argument-hint: <product-slug>
---

You are about to kick off the build phase for a product. This command does not implement anything itself — it routes the user through orientation questions and then to the right specialist persona for the chosen first subsystem.

The orchestration is owned by the `senior-software-engineer` persona; you invoke that persona and let it drive.

**Arguments:** $ARGUMENTS — the product slug. A brief must exist at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` OR `<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md` with `status: green-lit-to-build`. The command auto-detects which is current:

- **If both `MVP.md` (status `shipped`) and `V1.md` (status `green-lit-to-build`) exist:** build the v1. The MVP code is the starting point; new features are added on top per `V1.md`.
- **If only `MVP.md` exists:** build the MVP per the standard Phase 2 flow.
- **If only `V1.md` exists with no prior `MVP.md`:** this is an irregular state (Phase 1's MVP scoping was skipped). Surface to the user before proceeding.

### Pre-flight

1. **Detect which brief to build (MVP vs V1).** Check both `MVP.md` and `V1.md` under `web-apps/<slug>/`, `mobile-apps/<slug>/`, and `desktop-apps/<slug>/`. Pick which brief to build:

   | State | Brief to build | Notes |
   |---|---|---|
   | Only `MVP.md` exists with `status: green-lit-to-build` | `MVP.md` | Standard Phase 2 — initial MVP build. |
   | `MVP.md` exists with `status: shipped` AND `V1.md` exists with `status: green-lit-to-build` | `V1.md` | Phase 4 — real v1 build. MVP code is the starting point; new must-haves get added on top. |
   | `BUILD_STATUS.md` exists with `build-status: rework-in-progress` | (the matching brief — MVP.md or V1.md) | **Resume after `/rework`** — `BUILD_STATUS.md` has flipped subsystems (`[>]` that were previously `[x]`) per the rework-trigger History entries. The orchestrator re-engages the relevant specialists to revisit their work against the reworked brief. After all affected subsystems are back to `[x]`, the orchestrator can clear `build-status` back to the prior state (typically `building`). |
   | `MVP.md` exists with `status: shipped` but no `V1.md` | (nothing) | Stop and tell the user: "MVP shipped but no V1.md found. Run `/scope-v1 <slug>` to plan the v1 before re-running `/start-build`." |
   | Only `V1.md` exists with no prior `MVP.md` | `V1.md` (with warning) | Irregular state — MVP scoping was skipped. Surface to the user before proceeding: "No MVP.md found, but V1.md exists. Phase 1 was bypassed; the build will use V1.md but you should double-check this is what you intend." Default to continue. |
   | No brief at all | (nothing) | Stop: "No MVP.md or V1.md found at `<web-apps\|mobile-apps\|desktop-apps>/<slug>/`. Run `/scope-mvp <slug>` first." |

   Resolve `<path-to-brief>` and `<brief-version>` (one of `mvp` or `v1`) before proceeding to step 2.

2. **Verify the chosen brief's status.** Read frontmatter of the brief resolved in step 1. If `status` is not `green-lit-to-build`, surface:

   > Brief status is `<current-status>`, not `green-lit-to-build`. The build orchestration assumes the brief has been finalized and approved. Continue anyway?

   Wait for confirmation if not green-lit.

3. **Check pre-build decisions.** Read frontmatter for `design-path` and `build-support`. If either is missing, surface:

   > The pre-build decisions checkpoint from `/scope-mvp` wasn't recorded:
   > - design-path: <missing | recorded>
   > - build-support: <missing | recorded>
   >
   > Want to set them now before continuing?

   If user wants to set them, ask the two questions from `.claude/commands/scope-mvp.md` checkpoint #2 and record the answers in the brief's frontmatter.

4. **Check design-artifact readiness (gated by `design-path`).** Both design paths now run design research before build:

   | `design-path` | Required artifact | Path | If missing |
   |---|---|---|---|
   | `claude-led` / `claude-led-continued` | `DESIGN_SPEC.md` with `status: acted-on` | `<product-folder>/design/DESIGN_SPEC.md` | Stop and tell the user: "Build cannot start — `design-path` is `<value>` but `DESIGN_SPEC.md` does not exist (or is not signed off). Run `/research-design <slug>` → `/draft-design-spec <slug>` first. The spec is the build's source of truth on the claude-led path." |
   | `hired` / `pro-designer-engaged` | `design/handoff/tokens.json` + `design/handoff/screenshots/` | `<product-folder>/design/handoff/` | Stop and tell the user: "Build cannot start — `design-path` is `<value>` but the designer handoff (tokens.json + screenshots/) does not exist. Run `/research-design <slug>` → `/draft-design-brief <slug>` → engage the designer → capture handoff per `guides/ui-ux/design-handoff-methodology.md` first." |
   | `hybrid-light-refresh` | `DESIGN_RESEARCH.md` with `status: acted-on` (from `--light` run) | `<product-folder>/design/DESIGN_RESEARCH.md` | Stop and tell the user: "Build cannot start — `design-path` is `hybrid-light-refresh` but `DESIGN_RESEARCH.md` does not exist. Run `/research-design <slug> --light` first." |

   **Surface a soft override**: if the user wants to proceed without the design artifact (e.g., truly tossed-off prototype), require them to type "I accept the AI-generic aesthetic risk" before allowing build to continue. Record the override in the brief's frontmatter as `design-artifact-skipped: true` so it's auditable later.

### Do

Invoke the `senior-software-engineer` subagent using the custom-subagent invocation pattern in `CLAUDE.md`:

```
Agent({
  subagent_type: "general-purpose",
  description: "Build orchestration for <slug>",
  prompt: "You are about to act as the senior-software-engineer for the build phase of <slug>. Read .claude/agents/senior-software-engineer.md in full and treat its body as your role and process — pay particular attention to the § Reviewer routing section, which gates subsystem [>] → [x] flips on security + QA reviewer verdicts per guides/product/build-status-methodology.md §6. Read the team file at <product-folder>/team.json — it maps role keys to human names; use the name in narration if set ('<Name> (Senior X Engineer) is...'), otherwise just the role label. Read the brief at <path-to-brief> (resolved per /start-build step 1 — either MVP.md or V1.md), and if V1.md, ALSO read MVP.md and the existing codebase + BUILD_STATUS.md since v1 extends the MVP code rather than starting from scratch. If BUILD_STATUS.md exists with `pending-reviews:` frontmatter entries OR per-subsystem `security-review-required: true` / `qa-review-required: true` flags on subsystems still in `[>]` state, RESOLVE THOSE REVIEWS FIRST before any new implementation work — invoke the relevant reviewer(s) per guides/product/build-status-methodology.md §6 rules. ALSO read <product-folder>/VERIFIED.md if it exists per guides/product/verified-features-methodology.md §5; if it has any `[!]` entries (features the user manually flagged as not-working at the end-user surface), surface them in your orientation summary as a 'verification flags from prior session' section. Do NOT hard-gate on `[!]` — these are warnings, not blockers — but surface them prominently so the user remembers to revisit. Also note any `BUILD_STATUS.md` `[x]` subsystem that has zero entries in VERIFIED.md as a 'verification gap' (soft signal). **Read the design artifact authoritative for this design-path:** if claude-led / claude-led-continued, read <product-folder>/design/DESIGN_SPEC.md — this is the build's source of truth for visual + interaction design, and it SUPERSEDES the frontend-ui-engineering skill's defaults (padding scales, type ramps, color tokens) for this product; if hired / pro-designer-engaged, read <product-folder>/design/handoff/tokens.json + screenshots/; if hybrid-light-refresh, read <product-folder>/design/DESIGN_RESEARCH.md. Also read <product-folder>/design/DESIGN_RESEARCH.md if it exists (for context behind the locked picks). Read CLAUDE.md for the workspace conventions and the build-phase skill auto-invocation policy. Then ask the user the three orientation questions from §'Build-order questions you ask' in your persona file (in this order: web/mobile/desktop/hybrid order based on the brief's domain; MVP-scope or fully-featured-scope — for v1 builds this question takes a different shape; first subsystem to tackle — for v1 builds this is usually one of the new must-haves or a refactor of an MVP layer that the v1 needs to expand). When narrating to the frontend specialist later in the build, remind them that DESIGN_SPEC.md (or the handoff) is the token contract — they do not invent tokens. Wait for the user's answers between questions. After all three are answered, propose the next-step specialist persona to invoke and the specific first task, and tell the user to either confirm to proceed or override."
})
```

### Stop here — user checkpoint

After the `senior-software-engineer` returns its orientation summary, **stop**. Show the user:

> Build orchestration ready. Senior-software-engineer recommends starting with:
>
> **<first subsystem name>** — to be handled by **<senior-X-engineer>**.
>
> Your call:
> - **Confirm** → I invoke `<senior-X-engineer>` to start that subsystem.
> - **Override** → tell me which subsystem or specialist you'd rather start with.
> - **Discuss** → I can have `senior-software-engineer` go deeper on the tradeoffs.

Wait for the user's response before invoking any further specialists.

### Team-naming pre-flight (just-in-time, before each persona invocation)

The build phase uses 9 named senior-engineer personas (orchestrator + 8 specialists). Each product has a per-product `team.json` at the product folder storing the human names the user has chosen for those personas. The build orchestrator and `BUILD_STATUS.md` history use those names in narration ("Paul (Senior Software Engineer) is invoking Maria (Senior Database Engineer)..."); unnamed members fall back to the role label ("Senior Software Engineer is invoking Senior Database Engineer...").

**Initialization step (run once at the start of /start-build, before invoking the orchestrator):**

1. Run `python3 scripts/team.py init <slug>` — no-op if `team.json` already exists; otherwise creates an empty one (all 9 roles unset).

**Just-in-time naming prompt (run before every persona invocation, INCLUDING the orchestrator):**

For the persona that's about to be invoked (role key `<role>`):

1. Check `python3 scripts/team.py get <slug> <role>`. Exit 0 = name already set, skip to step 4. Exit 1 = unnamed.
2. If unnamed, surface to the user via `AskUserQuestion`:

   > This is the first time you're engaging your **<Role Label>** on this product. Would you like to give them a name? Names are used in build narration (e.g., "Paul (<Role Label>) is invoking..."). You can also run `/team <slug>` later to name or rename anyone.
   >
   > - **Yes — name them** → I'll ask for the name next.
   > - **No — use the role label** → "<Role Label>" will appear in narration as-is.

3. If "Yes — name them":
   - Prompt: "What name? (1-30 characters; letters, numbers, spaces, hyphens, apostrophes only.)"
   - Validate the reply (regex `^[A-Za-z0-9][A-Za-z0-9 \-']{0,29}$`). If it fails, surface the specific issue and re-ask once. If it fails a second time, fall back to "use the role label" silently.
   - On valid input, run `python3 scripts/team.py set <slug> <role> "<name>"`. Surface a one-line confirmation: "Saved: <name> (<Role Label>)."

4. Proceed with the invocation. Read the current team.json content (`python3 scripts/team.py list <slug> --json`) and pass it into the agent's prompt so the persona can use the right name in its narration.

**This applies to every persona invocation during /start-build**, both:

- The first call to the orchestrator (`senior-software-engineer`) at /start-build entry.
- Each subsequent call to a specialist that the orchestrator proposes — main Claude does the name-check before each Agent tool call.

### Notes

- This command is the **entry point** to the build phase. After this, individual specialists are invoked as the build proceeds — `senior-software-engineer` routes them in based on what's done and what's next.
- The user can re-run `/start-build <slug>` at any point if they want a fresh "where am I" + "what's next" prompt from the senior software engineer.
- The senior personas all live in `.claude/agents/senior-*.md` and are invoked via the custom-subagent invocation pattern in `CLAUDE.md`.
- For full team-management control (renaming, batch-naming upfront, resetting all to unnamed), use `/team <slug>`.

### Audit-log auto-append (build initialization)

When the user confirms the first subsystem and the senior-software-engineer starts the build (i.e., `BUILD_STATUS.md` is first created or the first subsystem flips to `[>]`), append a `build-milestone` entry per `CLAUDE.md` § Audit log:

```
python3 scripts/audit_log.py add build-milestone "Build milestone for <slug>: project initialized via /start-build (<stack: flask|react-native|pyside6|...>, first subsystem: <subsystem name>)."
```

Subsequent milestones (subsystem completion, ready-to-deploy, shipped) are appended by `senior-software-engineer` and `/ship-app` — see their respective files.
