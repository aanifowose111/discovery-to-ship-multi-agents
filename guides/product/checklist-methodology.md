# Checklist methodology

How `CHECKLIST.md` works — the fine-grained companion to `BUILD_STATUS.md` for tracking individual deliverables within a product build.

This guide is the contract `/generate-checklist <slug>`, `/read-checklist <slug>`, and the orchestrator's auto-refresh behavior run against.

---

## 1. Purpose

`BUILD_STATUS.md` tracks **coarse subsystems**: database, auth, API contract, frontend skeleton, etc. It's the orchestrator's map for who-does-what-next at the subsystem layer.

`CHECKLIST.md` tracks **fine deliverables** within those subsystems: "Email verification template (`app/templates/emails/verify.html`)", "`/verify-email/<token>` handler", "Tests for expired-token path". This is the granularity the user (and Claude) actually looks at when asking "what's left to do?"

The two files are **complementary, not redundant**:

| File | Granularity | Examples | Owner |
|---|---|---|---|
| `BUILD_STATUS.md` | Coarse subsystems | "Auth subsystem [x]", "API contract [x]", "Frontend skeleton [>]" | `senior-software-engineer` orchestrator |
| `CHECKLIST.md` | Fine deliverables | "Signup form [x]", "Verification email template [x]", "Resend-verification UI [ ]", "Tests for expired-token path [ ]" | `senior-software-engineer` orchestrator (auto-refresh) + user (additions via `/read-checklist` or direct edit) |

---

## 2. The CHECKLIST.md format

Lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/CHECKLIST.md`.

```markdown
---
slug: <product-slug>
brief-version: mvp | v1
design-artifact-source: design/DESIGN_SPEC.md | design/handoff/ | design/DESIGN_RESEARCH.md | none
generated-at: YYYY-MM-DD HH:MM
last-scanned-at: YYYY-MM-DD HH:MM
last-scanned-mtime: <epoch seconds>
status: in-progress | complete
---

# Checklist: <product name>

<one-line product description copied from brief>

## How this file works

- `[ ]` Pending  ·  `[x]` Done  ·  `[~]` Deferred / removed from scope
- Items auto-cross-out when matching files / patterns appear in the source tree
- Items can be added by the orchestrator (when scope discovers new work) or by the user (manually or via `/read-checklist`)
- Items can be removed by the user when scope changes
- Run `/read-checklist <slug>` to refresh statuses + scan for new work
- Auto-refreshed by the orchestrator after every `BUILD_STATUS.md` subsystem flip to `[x]`

## Must-haves from MVP.md

### <Must-have 1: short noun-phrase title>

*Why: <single sentence — links back to riskiest assumption or user-signal>*

- [x] <deliverable 1> — *`app/routes/auth.py:login_handler`*
- [x] <deliverable 2> — *`app/templates/login.html`*
- [ ] <deliverable 3> — *needs: email-template integration*
- [ ] <deliverable 4>

### <Must-have 2: short title>

*Why: <single sentence>*

- [ ] ...

## Must-haves from V1.md (only if V1 brief is green-lit-to-build)

### <V1 must-have>

*Why: <one sentence>*

- [ ] ...

## Could-haves (tracked, not in MVP scope)

- [~] <could-have 1> — *deferred to v2 per MVP.md*
- [~] <could-have 2>

## Scope changes log

Every addition, removal, or status flip the orchestrator (or user) makes to this file lands here for auditability.

| Date | Change | Reason | Triggered by |
|---|---|---|---|
| YYYY-MM-DD | Added "<item>" under "<must-have>" | Discovered during build — required by <subsystem> | orchestrator after `<subsystem>` flip |
| YYYY-MM-DD | Removed "<item>" | Scope cut at `/rework` (audit: <id>) | user via `/rework` |
| YYYY-MM-DD | Marked done "<item>" | File `<path>` shipped at commit `<hash>` | `/read-checklist` mtime scan |
```

---

## 3. Decomposition granularity

For each must-have in MVP.md (or V1.md), produce **3-8 deliverables**. Fewer than 3 means the must-have is itself bite-size enough; more than 8 means the must-have is two separate concerns and should be split first.

Rules of thumb for picking deliverables:

- **Each deliverable is independently completable** — a working test, a working endpoint, a working template, a working migration. Not "half of X".
- **Each deliverable is observable** — when it's done, you can point at a file or a passing test that proves it. This is what allows mtime-based auto-cross-out.
- **Group by user-visible feature first, by technical concern second.** Example: prefer ("Email verification → template + handler + email-send + tests") over ("Templates → email verification template; Routes → email verification handler; Tests → email verification tests"). The first reads as a feature; the second reads as a CRUD split.
- **One line per deliverable.** Sub-bullets only when a deliverable genuinely has nested parts (e.g., "Tests" with sub-items "happy path", "expired token", "invalid token").
- **Include the file/path hint when known.** `*\`app/routes/auth.py:login_handler\`*` in italics after the deliverable. Helps both Claude (mtime matching) and the user (jumping to code).

Example decomposition for the must-have **"Email signup with verification"**:

```markdown
### Email signup with verification

*Why: riskiest assumption — users will hand over an email for trial access only if the signup feels low-friction and trustworthy*

- [ ] Signup form (template + handler) — *`app/templates/signup.html`, `app/routes/auth.py:signup`*
- [ ] User model + DB migration — *`app/models/user.py`, `migrations/versions/0001_users.py`*
- [ ] Email verification flow — *token generation + email template + `/verify-email/<token>` handler*
  - [ ] Token model + generation — *`app/auth/tokens.py:generate_email_verification_token`*
  - [ ] Verification email template — *`app/templates/emails/verify.html`*
  - [ ] Verification handler with redirect — *`app/routes/auth.py:verify_email`*
- [ ] Tests
  - [ ] Happy path — *`tests/test_signup.py:test_signup_flow`*
  - [ ] Expired token — *`tests/test_signup.py:test_expired_token`*
  - [ ] Invalid token — *`tests/test_signup.py:test_invalid_token`*
- [ ] Resend-verification UI + handler — *for users who lose the original email*
```

5 top-level deliverables. The "Email verification flow" one has 3 sub-items (genuinely nested); "Tests" has 3 (nested by test case). Most other deliverables stay flat.

---

## 4. Auto-cross-out via mtime scan

When `/read-checklist <slug>` runs, it:

1. Reads `last-scanned-mtime` from frontmatter.
2. Lists files in the product folder with `mtime > last-scanned-mtime` (excluding `.git/`, `__pycache__/`, `node_modules/`, `.pytest_cache/`).
3. For each pending (`[ ]`) deliverable that has a file-hint in italics, checks whether the hinted file exists AND is in the recent-files list. If yes, cross out (`[ ]` → `[x]`).
4. For deliverables WITHOUT a file-hint, skip mtime-matching. Instead, look at the deliverable's text — if it describes a test, run `find tests/ -name "test_*<keyword>*" -mmin -<since-last-scan>` to confirm. If it describes a template, do the equivalent for `templates/`. Etc.
5. Updates `last-scanned-mtime` to the current epoch.
6. Appends one row per change to the Scope changes log.

**Token-cost optimization:** the mtime gate is the key. Without it, every `/read-checklist` would have to re-read every file. With it, only files touched since the last scan are inspected. After a long inactive period (week+) where lots changed, the first scan is expensive; subsequent scans are cheap.

---

## 5. Scope discovery (auto-add)

The orchestrator (or `/read-checklist`) can detect new work that should be added to the checklist:

1. **From the design artifact (highest priority):** walk `DESIGN_SPEC.md` (or handoff / DESIGN_RESEARCH.md) for sections the checklist doesn't yet cover — tokens (§2), icon system (§3), image-asset prompts (§4), responsive (§5), per-surface specs (§6), component patterns (§7), a11y floor (§8). UI / design coverage is the most-often-missed dimension; surface these gaps first.
2. **From new BUILD_STATUS subsystem flips:** if a new subsystem appeared in `BUILD_STATUS.md` since the last scan that has no corresponding section in CHECKLIST, propose adding it.
3. **From source-tree growth:** if a new top-level directory appeared (e.g., `app/integrations/`) without any matching checklist deliverable, propose adding "Integrations layer" with its known sub-files.
4. **From `/rework` audit-log entries:** if a rework added a must-have, that must-have needs decomposing into checklist items. The rework audit-log entry's description hints at what.

**Always propose, never silently add.** Surface the proposed addition to the user (via `/read-checklist`'s output), then add only on confirm. Avoid noise: cap at ~5 proposed additions per scan. **Prioritize design-artifact gaps** over source-tree gaps when triaging which to surface.

---

## 6. Scope changes (user-driven add/remove)

The user can:

- **Add an item manually**: edit CHECKLIST.md directly, or describe it during `/read-checklist`'s interactive prompt.
- **Remove an item**: mark it `[~]` (deferred) or delete the line. `/read-checklist` respects existing `[~]` markers (won't re-add them).
- **Re-prioritize**: re-order the deliverables. The methodology doesn't impose ordering beyond "must-haves first, could-haves last".

Every change appends to the Scope changes log.

---

## 7. Auto-refresh hook in the orchestrator + auto-generation trigger

Two distinct automation points:

### 7.1 Auto-generation — after the design artifact is signed off

`/draft-design-spec` (claude-led path) auto-generates `CHECKLIST.md` immediately after the user signs off on the spec (status flips to `acted-on`). Rationale: the spec is the richest design input the checklist depends on; generating BEFORE the spec produces a backend-heavy checklist that misses UI / icon / image-asset deliverables.

For the other paths:
- **Hired-designer path** (`/draft-design-brief` → designer → handoff) — auto-generation should fire after the handoff is captured (currently a manual flow per `design-handoff-methodology.md`; user runs `/generate-checklist <slug>` manually after handoff lands).
- **Hybrid-light-refresh path** — user runs `/generate-checklist <slug>` manually after `/research-design --light` signs off.
- **Claude-led without a spec yet** — the user can run `/generate-checklist <slug>` manually any time but should expect a backend-heavy checklist; re-running with regenerate-from-scratch after the spec lands is the recommended path.

### 7.2 Auto-refresh — after every BUILD_STATUS subsystem flip

`senior-software-engineer.md` has a § Auto-refresh CHECKLIST section. The rule:

> After flipping any `BUILD_STATUS.md` subsystem to `[x]`, if `<product-folder>/CHECKLIST.md` exists, do an in-line mtime scan and update CHECKLIST. Re-read the design artifact named in `design-artifact-source` if its mtime is newer than `last-scanned-mtime`. Append to the Scope changes log. This is silent — no user prompt; the goal is keeping CHECKLIST current so the user can run `/read-checklist` confidently or just open the file directly.

The orchestrator does NOT auto-generate CHECKLIST on first run if the spec is missing — generation is gated on the design artifact being available.

---

## 8. When NOT to use CHECKLIST.md

- **Single-deliverable MVPs** (rare — a brief with one must-have that decomposes into 2-3 items is fine without CHECKLIST; BUILD_STATUS subsystems are enough).
- **Pre-build phases** (idea card, validation, scoping). CHECKLIST lives at the product folder, which doesn't exist until `/scope-mvp` ships the brief.
- **Post-shipped reflection.** Once a product is `shipped`, CHECKLIST is read-only history. Don't add items; record findings as user notes in `BUILD_STATUS.md` History or a new section in V1.md.

---

## 9. Integration with the rest of the pipeline

| Upstream | How it feeds CHECKLIST |
|---|---|
| MVP.md / V1.md must-haves | Source of every top-level section |
| MVP.md could-haves | Tracked as `[~]` in §Could-haves |
| DESIGN_SPEC.md (if exists) | UI/UX surfaces inform deliverable hints (which template files to expect) |
| `BUILD_STATUS.md` subsystems | Cross-referenced; subsystem flips trigger refresh |
| `/rework` | New must-haves added during rework auto-propose new CHECKLIST items |

| Downstream | How CHECKLIST feeds it |
|---|---|
| `/recollect <slug>` | Recollect includes a CHECKLIST summary (count of done/pending) |
| `/continue-build <slug>` | Orchestrator references CHECKLIST when proposing the next file to write |
| `senior-software-engineer` orchestrator | Auto-refresh on subsystem completion |
| `/ship-app` | Verifies all MVP-scope items are `[x]` before allowing deploy (warning, not block) |

---

*Last meaningful revision: 2026-06-09 (initial draft).*
