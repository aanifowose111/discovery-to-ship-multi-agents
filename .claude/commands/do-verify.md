---
description: Append entries to a product's `VERIFIED.md` — the per-product log of features the human user has manually verified at the end-user surface (clicked the UI, saw the JSON, watched the email arrive). Distinct from pytest. Asks one candidate line at a time; user picks Yes (fully verified) / Yes (partial) / Observed (free text) / Not working. Creates `VERIFIED.md` if it doesn't exist. Accepts optional `--hint "<text>"` to bias which features Claude proposes. Per guides/product/verified-features-methodology.md.
argument-hint: <product-slug> [--hint "<text>"]
---

You are about to append verified-feature entries to `VERIFIED.md` for one product. Follow the methodology in @guides/product/verified-features-methodology.md exactly.

**Use this when:**
- You've manually walked through a feature and want to record that you confirmed it works
- You've just hit a `/_dev/*` route and want to record the JSON response as the "presentation" for that check
- An existing project (like `ops-audit-agent`) doesn't have `VERIFIED.md` yet — running this creates it and backfills entries
- You want to flag a feature as confirmed-not-working (`[!]`) so the orchestrator surfaces it at next `/start-build` / `/continue-build`

**Don't use this for:**
- pytest tests / unit tests — `VERIFIED.md` is for human end-user verification only
- A pre-deploy smoke playbook — that's `/smoke <slug>` writing `SMOKE.md`
- External items the user must obtain — that's `ACTION_REQUIRED.md`

**Arguments:** $ARGUMENTS — the product slug, optionally followed by `--hint "<text>"`. The hint biases which candidate features Claude proposes — useful for backfilling ("focus on auth flow + dev routes + dashboard load").

Examples:
```
/do-verify ops-audit-agent
/do-verify ops-audit-agent --hint "auth flow, /_dev/whoami, /_dev/logout, /_dev/run_diagnostic, dashboard load, design tokens applied"
/do-verify fijara --hint "the new sign-up flow we just built"
```

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, stop and tell the user: "No product folder for `<slug>`. Has the brief been scoped? Run `/scope-mvp <slug>` first."

2. **Parse `--hint`** if present. Extract the text between the quotes. This becomes the primary source of candidate-line suggestions.

3. **Read `<product-folder>/VERIFIED.md`** if it exists. Parse the existing entries to know what NOT to re-ask about. If the file doesn't exist, plan to create it with the frontmatter + skeleton sections per `guides/product/verified-features-methodology.md §3`.

4. **Read `<product-folder>/BUILD_STATUS.md`** to know the subsystem names (used for grouping) and to discover which subsystems are `[x]` (likely candidates).

5. **Scan recent activity in the product folder** to find candidate features. Order of precedence:
   1. **`--hint` items** — highest priority; each becomes a candidate.
   2. **Subsystems in `BUILD_STATUS.md` marked `[x]`** since the file's `last-updated` (or all `[x]` if `VERIFIED.md` doesn't exist yet).
   3. **`/_dev/*` routes** registered in `app/blueprints/_dev.py` (Flask) or `src/screens/_dev/` (RN). Each becomes a candidate.
   4. **Last 7 days of git commits** in the product folder (`git log --oneline --since="7 days ago" -- <product-folder>/`). Each commit subject becomes a candidate prompt.
   5. **The current conversation context** — features the user has mentioned trying / checking in this session.

   Build a working list of candidate lines: `[{description, suggested_subsystem, suggested_presentation}]`. Deduplicate against existing `VERIFIED.md` entries.

### Do

1. **If `VERIFIED.md` doesn't exist**, create it with the frontmatter + skeleton from `guides/product/verified-features-methodology.md §3`. Surface to the user: "Creating new `VERIFIED.md` at `<path>`. About to walk through `<N>` candidate features one at a time."

2. **For each candidate line in the working list**, run one round of the per-line confirmation protocol per `guides/product/verified-features-methodology.md §4`:

   a. Show the user the candidate: "**Candidate:** `<description>` — proposed subsystem: `<subsystem>`. Proposed presentation: `<short description or JSON snippet>`."

   b. Use `AskUserQuestion` with exactly these 4 options (and the "Other" slot reserved for "Skip this candidate / I haven't checked this"):
      - **Yes — fully verified** — "Append as `[x]` with the proposed presentation."
      - **Yes — partial** — "Append as `[~]`; I'll ask which part you confirmed."
      - **Let me describe what I saw** — "Append as `[?]` with your own observation text."
      - **Not working as intended** — "Append as `[!]`; I'll ask what's broken. Orchestrator will surface this at next `/start-build` / `/continue-build`."

   c. Per the user's answer:
      - **Yes — fully verified** → append the line as `[x]` with the proposed presentation. Stamp `Verified on: <today>`.
      - **Yes — partial** → ask a free-text follow-up: "Which part of this did you confirm?" — append the line as `[~]` with the user's reply as an `Observation:` field.
      - **Let me describe what I saw** → ask a free-text follow-up: "What did you see when you checked this?" — append as `[?]` with the user's reply verbatim as `Observation:`.
      - **Not working as intended** → ask a free-text follow-up: "What's the symptom?" — append as `[!]` with the user's reply as `Observation:`. Bump frontmatter `[!]-count` so the orchestrator sees it.
      - **Other / Skip** → don't append; move on.

   d. Append the line to the right subsystem section in `VERIFIED.md`. Create the subsystem `## <name>` header if it doesn't exist yet (use the subsystem name from `BUILD_STATUS.md`; fall back to `## Misc` if the candidate doesn't map to a known subsystem).

   e. Bump frontmatter `last-updated: <today>`.

   f. **Move on to the next candidate** — do NOT batch confirmations.

3. **After all candidates are processed**, append a line to the "Version log" section: `- <today> — <N> entries added via /do-verify (X [x], Y [~], Z [?], W [!]).`

### Stop here — user checkpoint

After all candidates are processed, show the user:

> ✅ VERIFIED.md updated at `<product-folder>/VERIFIED.md`.
>
> **This pass:**
> - Fully verified (`[x]`): `<count>`
> - Partial (`[~]`): `<count>`
> - Observed with notes (`[?]`): `<count>`
> - Not working as intended (`[!]`): `<count>`
> - Skipped: `<count>` (you said "haven't checked these")
>
> **🚨 Flagged not-working** (orchestrator will surface at next `/start-build` / `/continue-build`):
> 1. `<description>` — `<observation>`
> 2. ...
>
> **Subsystem coverage:**
> - `<subsystem 1>`: `<N>` entries
> - `<subsystem 2>`: `<N>` entries
> - ...
>
> **Subsystems with zero verified entries** (consider walking through these next):
> - `<subsystem name>`
> - ...
>
> Run `/do-verify <slug>` again any time to add more entries. The file persists across sessions.

### Notes

- **Never auto-append.** Every entry comes from a per-line user confirmation. If the user says "skip" or picks "Other", that candidate is dropped silently.
- **Deduplicate against existing entries.** Match by one-line description — fuzzy match is fine. If a candidate is already in the file, skip it silently.
- **JSON snippets as presentation.** For `/_dev/*` routes, encourage the user to paste the actual JSON response as the presentation field — that's the highest-value record. Claude can render a prompt like "Paste the JSON you saw (or 'skip' to use a description)."
- **No audit-log entry.** `/do-verify` is incremental, not a milestone. The file itself is the record.
- **Stack-agnostic.** Works for web / mobile / desktop equally. The candidate-finding heuristics adjust per stack (web: `app/blueprints/_dev.py`; mobile: `src/screens/_dev/`; desktop: dev menu items).
- **For backfill on existing projects** (like `ops-audit-agent`) the `--hint` carries the user's list of features to walk through. Claude treats each comma-separated item as a candidate.
