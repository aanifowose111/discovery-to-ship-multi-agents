# Action Required methodology

How `ACTION_REQUIRED.md` works — the per-product tracker for external, gating, third-party items the USER must obtain (API keys, OAuth apps, image-asset URLs, etc.) before the relevant build subsystem can proceed.

This guide is the contract `/check-actions <slug>`, `/draft-design-spec` Step 5, and the orchestrator's append behavior all run against.

---

## 1. Purpose

Some things only the user can do — get a Stripe API key from the Stripe dashboard, create an OAuth app on Google Cloud Console, generate images on ChatGPT/Midjourney and upload them somewhere. Claude can't do these for you. **`ACTION_REQUIRED.md` is the single canonical list of those items per product**, so nothing falls through the cracks.

It's distinct from `CHECKLIST.md` (build deliverables Claude will produce) and `BUILD_STATUS.md` (subsystem state):

| File | Tracks | Who does the work |
|---|---|---|
| `BUILD_STATUS.md` | Coarse subsystems | Orchestrator + specialists |
| `CHECKLIST.md` | Fine deliverables | Orchestrator + specialists |
| `ACTION_REQUIRED.md` | External / third-party items | **User** (only) |

---

## 2. What goes in (and what doesn't)

**Include:**
- API keys / tokens the user must obtain from external services (Stripe, SendGrid, Twilio, etc.)
- OAuth apps that need provisioning (Google Cloud Console, GitHub OAuth, etc.)
- Service accounts (Firebase service account JSON, GCP service accounts)
- Image-asset URLs the user must generate + upload (`IMG_*_URL` env-var slots from `DESIGN_SPEC.md §4`)
- Webhook URLs / domain DNS records the user must configure
- App Store / Play Store accounts the user must register
- Domain-name purchase + DNS configuration
- Any other gating item where Claude is blocked until the user does something external

**Even non-blocking items go in** — if a `SENDGRID_API_KEY` is needed eventually but the email subsystem can use console-print fallback in the meantime, list it anyway so the user has a single place to track pending third-party items.

**DO NOT include:**
- Judgment calls ("should this button be red or blue?") — those are design decisions, not actions
- Decisions about scope ("should we add a settings page?") — those go in `/rework` or scope conversations
- Things Claude can do for the user ("write the email template") — those are build deliverables, belong in `CHECKLIST.md`
- Things that should be in `BUILD_STATUS.md` (subsystem state)

---

## 3. Format

Lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/ACTION_REQUIRED.md`.

The format follows the **summary-table-plus-detail** pattern: a quick-scan summary table at the top so the user can see status across all items at a glance + flip the status symbol from the copy-paste block; then a detailed per-item section with full instructions.

```markdown
# Action Required — <Product Name>

Third-party items the build needs from outside the editor: API keys, OAuth credentials, DNS / domain setup, console-side scope grants. Items live here whether they're blocking right now or just coming up — so you can knock them out in parallel.

**What's NOT here:** judgment-call decisions, software questions, or anything Claude can ask you directly. Those stay in the chat.

**How to use:**
- Claude cannot read your `.env` values (only key names + emptiness, when `env-scan-enabled`). For each item below, check whether the env var is set; if so, mark it done.
- Items are sorted by **when they become blocking** — earliest first.
- For each item: env var name, what it powers, when it blocks, and step-by-step to get + add.
- Mark items done by replacing `[ ]` with `[x]` in the Status column. Copy from the samples below.

**Status symbols — copy from here:**

```
[ ]   pending
[x]   done
[~]   in progress / partial
[!]   blocked / needs attention
[-]   skipped / not applicable
```

**Last updated:** YYYY-MM-DD

---

## Summary table

| # | Env var(s) / Action | Vendor | Blocks | Status (you fill) |
|---|---|---|---|---|
| 1 | `STRIPE_SECRET_KEY` | Stripe | Payment subsystem (MH #N) | [ ] |
| 2 | `IMG_HERO_URL` (generate + upload) | DO Spaces / S3 | Public landing render | [ ] |
| 3 | `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` + redirect URI | Google Cloud | Auth subsystem | [ ] |
| ... | | | | |

---

## 1. `STRIPE_SECRET_KEY` — Stripe live secret key for payment processing

**Powers:** Server-side Stripe API calls for the Checkout Sessions subsystem (MH #N).
**Blocking?** Yes — payment subsystem can't build/test without it.

**Steps:**
1. Log into https://dashboard.stripe.com/.
2. **Developers → API keys → Standard keys.** Copy the **Secret key** (`sk_test_*` for test mode).
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   ```
4. Before Cohort 1: swap to `sk_live_*`.

---

## 2. `IMG_HERO_URL` — generate hero image, upload to DO Spaces (or S3), paste URL

**Powers:** Public landing page hero. Template uses a placeholder color block until the URL is set.
**Blocking?** No — non-blocking; templates render with placeholders. Worth doing before first marketing share.

**Steps:**
1. Generate using prompt verbatim from `design/DESIGN_SPEC.md §4 hero slot`: *"<exact prompt>"* — use ChatGPT / Midjourney / DALL-E / Stable Diffusion.
2. Upload to DigitalOcean Spaces bucket (or S3). Make object public-read.
3. Copy the object URL.
4. Add to `.env`:
   ```
   IMG_HERO_URL=https://...
   ```

---

(Continue with one numbered section per item — `## N. <KEY_NAME> — <one-line>`. Use the **Powers / Blocking? / Steps** structure.)

---

## Completed items (history)

- [x] **APP_SECRET_KEY** — Flask session secret (completed 2026-06-10 — generated by `senior-backend-engineer` during setup, value set in `.env`)
- [x] **SENDGRID_API_KEY** — SendGrid for transactional email (completed 2026-06-11 via `.env` scan)

---

## Removed items (no longer needed)

- [-] **TWILIO_AUTH_TOKEN** — SMS via Twilio (removed 2026-06-15 — scope changed; we use Resend email-only for notifications)
```

**Frontmatter** is optional but recommended for `/check-actions` to know the scan mode. Place at the top of the file in standard YAML form:

```yaml
---
slug: <product-slug>
created-at: YYYY-MM-DD HH:MM
last-scanned-at: YYYY-MM-DD HH:MM
env-scan-enabled: true
env-scan-mode: key-name-emptiness
---
```

**Frontmatter fields:**
- `slug` — product slug
- `created-at` — when the file was first created
- `last-scanned-at` — last time `/check-actions` ran a `.env` scan + status refresh
- `env-scan-enabled` — `true` / `false`. When true, `/check-actions` and the orchestrator periodically scan `.env` to auto-cross-out completed items.
- `env-scan-mode` — `key-name-emptiness` (default — see §4) / `full` (reads values, exposes to context) / `manual` (no scan)

If frontmatter is absent, `/check-actions` defaults to `env-scan-enabled: true, env-scan-mode: key-name-emptiness`.

**Per-item structure:**
- **Title line** — `## N. \`KEY_NAME\` — <one-line description>`
- **Powers** — which subsystem/feature uses this; reference MH # or feature name
- **Blocking?** — yes/no/conditional, with the specific subsystem it blocks
- **Steps** — numbered, actionable; URLs verbatim where the user must click; the `.env` snippet as a fenced code block
- **Added** (optional metadata) — date + source (`/draft-design-spec`, `senior-backend-engineer`, etc.)

**Status symbols (the 5 the file documents at the top — also what `/check-actions` and the orchestrator respect):**

| Symbol | Meaning | `/check-actions` behavior |
|---|---|---|
| `[ ]` | Pending | Stay in pending; auto-cross-out to `[x]` when env key is set |
| `[x]` | Done | Move to **Completed items (history)** |
| `[~]` | In progress / partial | Stay in pending with the `[~]` mark preserved; do NOT auto-flip via env scan (the user is mid-step) |
| `[!]` | Blocked / needs attention | Stay in pending with the `[!]` mark preserved; do NOT auto-flip |
| `[-]` | Skipped / not applicable | Move to **Removed items (no longer needed)** |

---

## 4. `.env` scan modes

`/check-actions` and the orchestrator can optionally scan `<product-folder>/.env` to auto-cross-out items whose env keys are now set. Three modes:

### 4.1 `key-name-emptiness` (default — recommended)

Scan extracts only the key NAMES and whether each has a non-empty value. Values never enter Claude's context. Implementation:

```bash
awk -F= '/^[A-Z_]+=/{ key=$1; val=$2; print key, (length(val)>0 ? "set" : "empty") }' <product-folder>/.env
```

Output:
```
STRIPE_SECRET_KEY set
SENDGRID_API_KEY empty
GOOGLE_OAUTH_CLIENT_ID set
APP_SECRET_KEY set
```

For each pending item in ACTION_REQUIRED.md whose env-var name appears in the "set" column, the item is auto-cross-out. Items in the "empty" column stay pending.

**This mode is the default** and the workspace recommendation — automation without secret exposure.

### 4.2 `full` (read values)

Claude reads `.env` directly. Most thorough cross-out — can match values against pattern requirements (e.g., "STRIPE_SECRET_KEY must start with `sk_live_`"). But secret values land in Claude's transcript/context.

Use only when:
- Pattern matching beyond presence/emptiness is needed
- The user has explicitly opted in
- The transcript/context is private to the user

### 4.3 `manual` (no scan)

`/check-actions` and the orchestrator never read `.env`. User marks `[x]` by hand. Most private, least automated.

---

## 5. Lifecycle

### 5.1 Creation (auto, never user-triggered first)

`ACTION_REQUIRED.md` is created at one of two trigger points:

1. **`/draft-design-spec` Step 5 (primary trigger).** After the user signs off on `DESIGN_SPEC.md`, alongside the auto-generation of `CHECKLIST.md`, also create ACTION_REQUIRED.md populated from:
   - `DESIGN_SPEC.md §4 Image assets` → one item per `IMG_*_URL` env-var slot, with the prompt verbatim
   - Any third-party services explicitly named in the spec or brief (Stripe if pricing is set, etc.)
2. **First specialist build step that surfaces a third-party need** — if step 1 was skipped (manual `/generate-checklist` run before spec landed), the orchestrator creates ACTION_REQUIRED.md when the first dependency surfaces.

Frontmatter set with current timestamps + `env-scan-enabled: true` + `env-scan-mode: key-name-emptiness` (defaults).

### 5.2 Append (during build)

Whenever a specialist identifies a third-party dependency the user must obtain (e.g., `senior-backend-engineer` needs Stripe for payment processing, `senior-devops-engineer` needs domain DNS), the orchestrator appends a new item to the **Pending items** section of ACTION_REQUIRED.md.

**Never overwrite existing items.** If the file exists, only append; preserve all existing items + history.

**Always tell the user.** After appending, surface to user: "Added `<KEY_NAME>` to ACTION_REQUIRED.md — you'll need to get the value from `<URL>` and add to `.env` to unblock `<subsystem>`."

### 5.3 Refresh (auto + user-triggered)

- **Auto** — orchestrator runs the refresh inline after every BUILD_STATUS subsystem flip (paired with the existing CHECKLIST refresh).
- **User** — `/check-actions <slug>` runs the refresh explicitly. Useful after the user has just added keys to `.env` and wants the items crossed out immediately.

Refresh logic:
1. Read ACTION_REQUIRED.md frontmatter
2. If `env-scan-enabled: true`, run the scan (per mode in §4)
3. For each pending item, check if its env-var key has a value in `.env`. If yes, move the item from "Pending items" to "Completed items" with a `(completed YYYY-MM-DD via .env scan)` suffix
4. For items marked `[x]` by the user manually, also move them to Completed
5. Update `last-scanned-at` frontmatter

### 5.4 Append-only — never destroy items

The file is **append-only** at the item level. Completed items move to the history section but are never deleted. Pending items can be removed only via explicit user request (e.g., "this is no longer needed because scope changed"); the removal lands in `## Removed items` with a reason + date.

---

## 6. General .env key-name-scan usage (beyond ACTION_REQUIRED)

The `awk -F= '/^[A-Z_]+=/{ ... }'` pattern from §4.1 isn't only for `/check-actions`. Claude can use it **anywhere** it needs to verify a specific env key is set without exposing the value:

- Before writing code that depends on `STRIPE_SECRET_KEY` — check it's set; if not, skip-code-write and surface to user that the key is missing in ACTION_REQUIRED.md
- Before generating a migration that adds OAuth — check `GOOGLE_OAUTH_CLIENT_ID` is set; if not, defer and add to ACTION_REQUIRED.md
- After the user mentions they've added a key — confirm with a key-name scan rather than asking the user to paste the value

The scan is a safe, low-cost, no-context-exposure read of `.env`. Use it generously.

---

## 7. Integration with the rest of the pipeline

| Upstream | How it feeds ACTION_REQUIRED |
|---|---|
| `DESIGN_SPEC.md §4 Image assets` | Primary source of `IMG_*_URL` items at creation |
| Brief (MVP.md / V1.md) | Pricing/payment must-haves → Stripe key; auth must-haves → OAuth keys |
| Specialists during build | Append new dependencies as they surface |
| `.env` file | Source of truth for "is this key set"; scanned on every refresh |

| Downstream | How ACTION_REQUIRED feeds it |
|---|---|
| `/recollect <slug>` | Includes ACTION_REQUIRED summary (pending count, blocking count) |
| `/continue-build <slug>` | Orchestrator checks ACTION_REQUIRED before resuming a subsystem that needs an external key |
| `/ship-app <slug>` | Refuses to deploy if any blocking item is still pending (gate, not block — user can override with explicit ack) |

---

*Last meaningful revision: 2026-06-09 (initial draft).*
