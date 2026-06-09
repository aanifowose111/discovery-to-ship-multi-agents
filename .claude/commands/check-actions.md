---
description: Refresh ACTION_REQUIRED.md for a product — scans `.env` (key-name + emptiness mode by default; no values exposed to context) to auto-cross-out items whose env keys are now set, moves completed items to the history section, and updates last-scanned-at. Idempotent. Pairs with the orchestrator's auto-refresh and the auto-creation from `/draft-design-spec` Step 5. Per guides/product/action-required-methodology.md.
argument-hint: <product-slug>
---

You are about to refresh `ACTION_REQUIRED.md` for one product. Follow the methodology in @guides/product/action-required-methodology.md exactly.

**Use this when:**
- You've just added one or more keys to `.env` and want the pending items crossed out immediately
- You want to see what's still pending (blocking vs. non-blocking) without waiting for the orchestrator's auto-refresh after the next subsystem flip
- You want to verify nothing has drifted (you marked items `[x]` manually but want to confirm Claude's view matches)

**Don't use this for:**
- Creating ACTION_REQUIRED.md from scratch — that's auto-created by `/draft-design-spec` Step 5 (or by the orchestrator on first dependency surface)
- Adding new items by hand — edit the file directly, or let the orchestrator append during build
- Reading `.env` values for any purpose other than presence/emptiness — this command never exposes values

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder + ACTION_REQUIRED.md.** Check `<web-apps|mobile-apps|desktop-apps>/<slug>/ACTION_REQUIRED.md`. If the file doesn't exist, stop and tell the user: "No `ACTION_REQUIRED.md` for `<slug>`. It auto-creates after `/draft-design-spec` sign-off (alongside CHECKLIST.md) or when the build orchestrator surfaces the first third-party dependency. If you want one now, run `/draft-design-spec <slug>` to get the design phase to the auto-create point, or start the build and let the orchestrator create it on first need."

2. **Read frontmatter** for `env-scan-enabled` and `env-scan-mode`.
   - If `env-scan-enabled: false` or `env-scan-mode: manual` → skip the scan; just re-read the file to report current state (pending count, completed count, blocking count) and stop. Tell the user: "env-scan is disabled (mode: `<mode>`). Refresh runs no scan; just reports state. To enable scanning, change the frontmatter to `env-scan-enabled: true` + `env-scan-mode: key-name-emptiness`."

3. **Verify `.env` exists** at `<product-folder>/.env`. If not, tell the user: "No `.env` at `<product-folder>/.env`. Nothing to scan; reporting current ACTION_REQUIRED state only." Then skip the scan and just report.

### Do (scan + cross-out)

1. **Run the key-name + emptiness scan** (the default safe mode — values never enter context):

   ```bash
   awk -F= '/^[A-Z_]+=/{ key=$1; val=$2; print key, (length(val)>0 ? "set" : "empty") }' <product-folder>/.env
   ```

   Capture output. Example:
   ```
   STRIPE_SECRET_KEY set
   SENDGRID_API_KEY empty
   GOOGLE_OAUTH_CLIENT_ID set
   APP_SECRET_KEY set
   ```

   **(For `env-scan-mode: full`** — read the file directly. This is the opt-in mode that exposes values; only do this if frontmatter says so. Pattern-match values against any per-item requirements.)

2. **Read ACTION_REQUIRED.md `## Pending items` section.** For each pending item:
   - Extract the env-var name(s) from the item (e.g., `STRIPE_SECRET_KEY`, or `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` if it's a paired item).
   - Cross-reference against the scan output.
   - **If ALL the item's env keys are in the "set" column** → mark the item complete, move to `## Completed items (history)` with suffix `(completed YYYY-MM-DD via .env scan)`.
   - **If ANY of the item's env keys is "empty" or missing** → leave in pending.

3. **Honor manual `[x]` marks** — for items the user has marked `[x]` directly in the file (without a `.env` value), also move them to Completed with suffix `(completed YYYY-MM-DD via user mark)`.

4. **Update frontmatter** `last-scanned-at: <now>`.

5. **Preserve order + comments.** Don't reorder unchanged pending items. Don't drop user-added items or annotations.

### Stop here — user checkpoint

After applying, **stop**. Show the user:

> ✅ ACTION_REQUIRED refreshed at `<product-folder>/ACTION_REQUIRED.md`.
>
> **This pass:**
> - Auto-crossed-out via `.env` scan: `<count>`
> - Manual `[x]` marks moved to history: `<count>`
> - Still pending: `<count>` (`<blocking-count>` blocking, `<nonblocking-count>` non-blocking)
>
> **Newly completed:**
> - ✓ `<KEY_NAME>` — `<description>`
> - ...
>
> **Still pending — blocking** (need before next build step):
> 1. `<KEY_NAME>` — `<description>` — get from `<URL>`
> 2. ...
>
> **Still pending — non-blocking** (defer-able):
> 1. `<KEY_NAME>` — `<description>` — get from `<URL>`
> 2. ...
>
> Open the file to read the full per-item details. Add new keys to `.env`, then run `/check-actions <slug>` again to auto-cross-out.

### Notes

- **No audit-log entry.** Refresh is a maintenance event, not a milestone.
- **The scan never exposes `.env` values** in the default `key-name-emptiness` mode. The awk output only contains key names and a `set`/`empty` flag.
- **The orchestrator auto-runs this refresh** after every `BUILD_STATUS.md` subsystem flip to `[x]` — paired with the CHECKLIST refresh. Manual `/check-actions` is for the user-driven refresh case (just added keys, want immediate update).
- **Edge case: user added a key not in ACTION_REQUIRED.md.** That's fine — the scan ignores keys not tracked. The user can add new pending items via direct edit, or let the orchestrator surface them.
- **Edge case: pending item references a key name that doesn't appear in the scan at all** (typo, key was removed from .env). Leave pending and surface in the report: "Pending item `<NAME>` references key `<KEY>` which is not in `.env` at all — has the key name been renamed?"
- **For `/check-actions` on a product whose `.env.example` exists but `.env` doesn't** — surface to the user: "Found `.env.example` but no `.env`. Copy it with `cp .env.example .env` first, fill in the values, then re-run `/check-actions`."
