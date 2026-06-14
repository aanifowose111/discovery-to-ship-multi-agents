# VERIFIED.md — manual end-user verification log methodology

`VERIFIED.md` is the **per-product log of features the human user has manually verified as an end user would** — clicked the button, saw the dashboard update, hit the `/_dev/whoami` route and saw the JSON, watched the email actually arrive. It is distinct from pytest / unit tests / integration tests; those check correctness at the code level. `VERIFIED.md` checks that the *feature works for a person using it*.

It pairs with `BUILD_STATUS.md` (subsystem progress), `CHECKLIST.md` (granular deliverables), and `ACTION_REQUIRED.md` (external items only the user can obtain). It is the **fourth artifact** in the per-product root.

---

## 1. Purpose

A subsystem can be `[x]` in `BUILD_STATUS.md` and pass every pytest test and still be subtly broken at the end-user surface — a button shows but does nothing, a redirect targets the wrong URL, an empty state shows the wrong copy, the JSON return shape from a `/_dev/*` route doesn't match what the dashboard reads. `VERIFIED.md` is the **deliberate record of what a human actually walked through and saw**, captured per-line with the user's own confirmation.

What it is NOT:

- Not a substitute for pytest. Pytest catches regressions; `VERIFIED.md` records human acceptance at a moment in time.
- Not a release checklist (that's `SMOKE.md` — the standing playbook of pre-deploy checks).
- Not an exhaustive QA matrix. It's a record of what the *user* has eyeballed, not what *should* be eyeballed.

---

## 2. When the file is created

| Trigger | Behavior |
|---|---|
| **After `/draft-design-spec` Step 5b finishes** (auto) | Empty stub is created alongside `CHECKLIST.md` and `ACTION_REQUIRED.md`. Headers + frontmatter; no entries yet. |
| **`/do-verify <slug>` invoked when file doesn't exist** (manual) | Created on the fly. Claude proceeds to scan for candidate lines and ask per-line. |
| **Pre-existing project that pre-dates this methodology** | User runs `/do-verify <slug> --hint "<candidates>"` to backfill. |

The file lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/VERIFIED.md`. It is **gitignored** (lives in the per-product folder, which is gitignored as personal data). Each forker maintains their own.

---

## 3. Format

```markdown
---
project: <slug>
created: 2026-06-13
last-updated: 2026-06-13
schema: verified-v1
---

# VERIFIED — manual end-user checks for <slug>

This file records features that have been **manually verified by a human end-user**.
Distinct from pytest — these are "I clicked it, I saw it work."

## Status symbols (copy from here)

- `[x]` — Fully verified
- `[~]` — Partially verified (some parts checked, some not)
- `[?]` — Observed with notes (user described what they saw)
- `[!]` — Verified not working as intended (the orchestrator surfaces this)
- `[ ]` — Proposed, not yet confirmed (rare — usually `/do-verify` resolves these)

## Verified features

### Auth

- `[x]` Login form accepts a valid email + password and redirects to dashboard.
  - **Verified on**: 2026-06-13
  - **Presentation**: After clicking Submit, redirected to `/dashboard`; header shows user email.

- `[x]` `/_dev/whoami` returns the current user's identity JSON.
  - **Verified on**: 2026-06-13
  - **Presentation**:
    ```json
    {"user_id": "uuid-...", "email": "founder@example.com", "tenant_slug": "ops-audit"}
    ```

### Dashboard

- `[!]` Pagination on the audit-entries table did not trigger past 100 rows; the page kept appending instead.
  - **Observed on**: 2026-06-13
  - **Observation**: "Scrolled to row 120 and the table just kept growing. Expected a 'next page' link or virtual scroll."
  - **Orchestrator note**: surface this at next `/continue-build`.

## Version log

- 2026-06-13 — initial entries via `/do-verify` (3 features confirmed, 1 not-working flagged).
```

### Grouping

**Group by subsystem** (mirrors `BUILD_STATUS.md` subsystem names). This makes the file double as a coverage map — at a glance the user can see "Auth has 4 verified entries, Dashboard has 0, Billing has 1 not-working flag."

### Per-line fields

Every verified entry records:

1. **Status symbol** (`[x]` / `[~]` / `[?]` / `[!]` / `[ ]`)
2. **One-line description** of the feature/behavior the user checked
3. **Verified on** (or **Observed on** for `[?]` / `[!]`) — the date
4. **Presentation** — what the user actually saw, in the form best matching the surface:
   - For UI surfaces: a brief description ("Header shows user name, dashboard table loads with N rows")
   - For JSON/API surfaces: an actual JSON snippet
   - For email: subject line + a couple of words of body
   - For files/exports: the path or filename + relevant fields
5. **Observation** (only for `[?]` / `[!]`) — the user's free-text note about what was different from expected

---

## 4. The per-line confirmation protocol

`/do-verify <slug> [--hint "<text>"]` runs Claude through a loop that proposes one candidate line at a time and asks the user to confirm. **Never batch.** The user reviews and approves each line individually.

For each candidate line:

1. Claude proposes the feature: "I believe you've verified `<one-line description>`. Should I record this as verified?"
2. Claude uses `AskUserQuestion` with these **four options**:
   - **Yes — fully verified** → append as `[x]` with Claude's proposed presentation.
   - **Yes — partially verified** → append as `[~]`; then ask "Which part did you confirm?" via a free-text follow-up.
   - **Let me type what I observed** → append as `[?]`; then ask "What did you see?" via a free-text follow-up; the verbatim user reply becomes the **Observation** field.
   - **It still does not work as intended** → append as `[!]`; then ask "What's the symptom?" via free-text; the verbatim reply becomes **Observation**.
3. Append to the appropriate subsystem section. If the subsystem section doesn't exist yet, create it (use the subsystem name from `BUILD_STATUS.md`; fall back to `## Misc` if Claude can't infer the subsystem).
4. Bump `last-updated` in frontmatter.
5. Move to the next candidate.

After all candidates are processed, Claude shows a summary: count of `[x]` / `[~]` / `[?]` / `[!]` added this pass, plus the running totals.

### Where candidate lines come from

- **Conversation context** in the current session (Claude knows what the user said they tried).
- **`--hint "<text>"`** — the user's free-text list of things to ask about. Highest priority.
- **`BUILD_STATUS.md` History entries** — completed subsystems are likely candidates ("you completed the auth subsystem — did you verify login?").
- **Recent git commits** in the product folder (last 7 days).
- **`/_dev/*` routes registered** in the project — each is a strong candidate to ask about.

Claude prioritizes the `--hint` items first, then conversation context, then BUILD_STATUS.md history, then git commits.

### Never auto-add

Claude does **not** unilaterally add entries to `VERIFIED.md`. Every line comes from a user confirmation. The only thing Claude does without asking is **create the empty stub** (auto-create after `/draft-design-spec` Step 5).

### Already-recorded entries

If Claude proposes a line that's already in `VERIFIED.md` (deduplicate by one-line description), it skips that candidate silently. The user shouldn't have to re-confirm something already recorded.

---

## 5. How the orchestrator uses VERIFIED.md

During `/start-build` and `/continue-build`, the orchestrator reads `VERIFIED.md` (if it exists) and:

- **Counts the `[!]` entries.** If any exist, surface them in the build summary: "`VERIFIED.md` has N items flagged as not-working: `<list>`. These represent confirmed user-facing failures — consider revisiting before new work."
- **Does NOT hard-gate.** Forward build progress continues; `[!]` items are surfaced as a warning, not a block. Reason: the user may have intentionally deferred the fix; the orchestrator's job is to make sure these stay visible, not to override the user.
- **Notes coverage gaps.** If a subsystem in `BUILD_STATUS.md` is `[x]` but has zero entries in `VERIFIED.md`, the orchestrator notes this in the build summary as "verification gap." Soft signal, not a block.

The `[!]` surfacing is per-session — once the user has seen the warning, the orchestrator does not re-warn within the same session.

---

## 6. Relationship to other artifacts

| Artifact | Records | Source of truth for |
|---|---|---|
| `BUILD_STATUS.md` | Subsystem-level progress (`[ ]` / `[>]` / `[x]`) | What has been *built* |
| `CHECKLIST.md` | Fine-grained deliverables Claude produces | What has been *deliverably completed* |
| `ACTION_REQUIRED.md` | External/third-party items only the user can obtain | What is *blocked* on user action |
| `VERIFIED.md` | Features the user has manually checked at the end-user surface | What has been *eyeballed* and confirmed |
| `SMOKE.md` (if present) | Standing manual smoke-test playbook to run before each deploy | What to *re-verify* before shipping |

`VERIFIED.md` is the only artifact whose entries always come from explicit user confirmation. Every other artifact has some Claude-driven append path; this one is per-line user-driven.

---

## 7. Pipeline integration

- **`/draft-design-spec` Step 5c** auto-creates the empty stub (alongside `CHECKLIST.md` Step 5a + `ACTION_REQUIRED.md` Step 5b).
- **`/do-verify <slug> [--hint "<text>"]`** is the only command that appends entries.
- **Orchestrator (`senior-software-engineer.md`)** reads it during build to surface `[!]` items and coverage gaps. Does NOT write to it.
- **`/ship-app`** reads it during release-readiness; surfaces any `[!]` items as a release blocker question ("These features were flagged as not-working. Confirm they're fixed before shipping?").

---

## 8. Edge cases

- **User says "yes" to a partial entry but doesn't specify which part:** record as `[~]` with `Observation: "Partial confirmation; specifics not given."` so the partial state is honest.
- **User says "no" to a proposed entry:** skip it; don't add. If Claude was wrong about the user having tried this, the candidate just disappears.
- **Multiple candidates for the same feature** (e.g., login via password AND login via Google OAuth): treat as separate entries — each is its own user-facing surface.
- **A line in `VERIFIED.md` becomes stale** (the underlying code was reworked): the user runs `/do-verify <slug> --hint "re-check auth after the password-hash rework"` and re-confirms; old entries can be hand-edited or flipped to `[!]` until re-verified.
- **Web app vs. mobile app:** the methodology is identical. Mobile entries may reference a screen name + app build (e.g., "iOS dev build, login screen v2026-06-13") instead of a URL.
- **Desktop app:** same — entries reference the window / screen / dialog.

---

## 9. Privacy + gitignore

`VERIFIED.md` is in a gitignored per-product folder. It never enters git history. The presentation snippets may include identifying info (user IDs, email addresses, tenant slugs) — that stays on the user's machine.

When sharing a project for handoff (e.g., to Fijara), the user can choose whether to include `VERIFIED.md` — it's useful as documentation but contains personal-data snippets.

---

## 10. Anti-patterns

- **Bulk-confirming without reading:** the per-line ask is intentional. If the user reflexively picks "Yes — fully verified" without thinking, the artifact loses its meaning. Claude should ask each one as a deliberate question, not "shall I record these 14 features?" all at once.
- **Treating `[!]` as a `BUILD_STATUS.md` rollback:** flipping a feature to `[!]` does NOT flip its subsystem in `BUILD_STATUS.md` back to `[>]`. The two artifacts track different things — the subsystem can be implementation-done while the end-user experience has a flaw. Use `/rework <slug>` to formally re-open a subsystem.
- **Using `VERIFIED.md` as a backlog:** it's a log, not a planning document. Don't add `[ ]` "things to verify someday" — those belong in your notes or a separate todo.
- **Skipping the presentation field:** "It works" is not enough. The whole point is to record *what the user saw* so a future session can compare.

---

## 11. Auto-update hooks (none)

`VERIFIED.md` has no automatic update path other than `/do-verify`. Every entry requires explicit user confirmation. This is the safety-critical design — verification claims should always trace back to a deliberate human act.

---

*Last updated: 2026-06-13.*
