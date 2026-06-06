---
description: List, name, or edit the senior-engineer team members for a product. Per-product team-member names live in `<web-apps|mobile-apps|desktop-apps>/<slug>/team.json` and are used by the build orchestrator in narration (e.g., "Paul (Senior Software Engineer) is invoking Maria (Senior Database Engineer)..."). Members can be named, renamed, or reset to unnamed; they cannot be deleted (the 9 roles are critical to the workflow). Backed by `scripts/team.py`.
argument-hint: <slug>
---

You are about to view / name / edit team members for a product. The team is a fixed roster of **9 senior-engineer personas** (the long-running build-phase collaborators — the orchestrator + 8 specialists). Helper script: `scripts/team.py`.

**Arguments:** `$ARGUMENTS` — the product slug. The product folder must exist at `web-apps/<slug>/`, `mobile-apps/<slug>/`, or `desktop-apps/<slug>/` (created by `/scope-mvp` when the brief is drafted).

### Inputs

1. **Verify the product folder exists** by running `python3 scripts/team.py path <slug>`. If exit code 1, stop and tell the user: "No product folder for `<slug>`. Run `/scope-mvp <slug>` to draft the brief and create the product folder first."
2. **Auto-initialize `team.json` if missing**: `python3 scripts/team.py init <slug>` (this is a no-op if it already exists).

### Do

This is an **interactive command**. After the inputs step, loop:

#### Step 1 — Display the team

Run `python3 scripts/team.py list <slug>` and show the output verbatim in a code block. The table has 9 rows numbered 1-9, one per role, with the human name if set or "(unnamed — uses role label)" otherwise.

#### Step 2 — Offer actions

Use `AskUserQuestion` with these options:

- **Name an unnamed member** — pick a row whose name is currently blank.
- **Edit an existing name** — pick a row whose name is set, replace it.
- **Reset all to unnamed** — clears every name in one shot (the file stays; just the values blank out).
- **Done — exit** — stop the loop.

**Important:** the picker does NOT include a "delete a member" option. The 9 roles are workflow-critical and cannot be deleted. If the user asks for one anyway, surface: "Deletion isn't supported — these 9 roles are wired into the build orchestration. You can reset their names to unnamed (uses the default role label in narration), but the role itself stays."

#### Step 3 — Handle the action

**For "Name an unnamed member" or "Edit an existing name":**

1. Ask the user to identify the role. Prompt:

   > Which member? Reply with either:
   > - the **row number** (1-9) from the table above, or
   > - the **role key** (e.g., `senior-database-engineer`).

   Parse the reply: numeric → look up the role key from `python3 scripts/team.py roles` (1-indexed); string → use as-is.

2. Ask for the new name:

   > Name for **<Role Label>**? (1-30 characters; letters, numbers, spaces, hyphens, apostrophes only.)

3. Validate the reply against the rules. If the reply is too long, too short, or contains forbidden characters, surface the specific issue and re-ask once. If it still fails, return to step 2 (the action picker) without setting anything.

4. On valid input: run `python3 scripts/team.py set <slug> <role-key> "<name>"`. Surface the script's confirmation (`set senior-database-engineer = Maria`).

5. **Return to step 1** (re-display the team and offer actions again).

**For "Reset all to unnamed":**

1. Confirm via `AskUserQuestion`:
   - **Reset all names — proceed** → continue
   - **Cancel — keep names** → return to step 1
2. On confirmation: run `python3 scripts/team.py reset <slug>`.
3. Surface the confirmation.
4. **Return to step 1.**

**For "Done — exit":**

Tell the user where the team file lives:

> Team saved at `<web-apps|mobile-apps|desktop-apps>/<slug>/team.json`. The build orchestrator reads this on every persona invocation and uses the names in narration ("Paul (Senior Software Engineer)…" if named; "Senior Software Engineer…" if unnamed). You can run `/team <slug>` again anytime to rename anyone.

Suggest 2-3 next actions based on context:
- If the slug has an MVP brief but no build yet: "`/start-build <slug>` to begin the build with your named team."
- If the slug has a build in progress: "Next persona invocation will use the names you just set."
- Always: "`/log type build-milestone` to see the build journal so far."

Then **stop the command** — do not loop further.

### Important — no auto-actions

- **NEVER delete a team member.** Deletion isn't supported by the helper script either, but enforce it in the UI: never offer a "delete" option, never write empty roles when refreshing, never run any rm-like operation on `team.json`.
- **NEVER alter team.json outside the helper script.** Always go through `python3 scripts/team.py set|reset|init` to ensure validation runs and `last-updated` is bumped.
- **NEVER name a team member for the user.** Names are personal — even if the user says "pick one for me", surface 2-3 *suggestions* (common short names) and let them choose. Don't write a name to the file without explicit confirmation.

### Notes

- **What gets named:** the 9 build-phase senior-engineer personas (orchestrator + 8 specialists). The validation reviewers (`product-viability-reviewer`, `product-competition-reviewer`, `market-segment-reviewer`, `product-pricing-reviewer`), scoping reviewers (`product-scope-reviewer`, `code-reviewer`), and design personas (`ui-ux-researcher`, `design-brief-reviewer`, `design-fidelity-reviewer`) are **one-shot advisors**, not long-running collaborators — they are not part of the team roster.
- **Where the names show up:** anywhere the build orchestrator narrates a handoff or status update — `/start-build` summaries, `BUILD_STATUS.md` History entries, `build-milestone` audit-log descriptions. The narration format is `<Name> (<Role>) is …` when named, and just `<Role> is …` when unnamed.
- **Per-product, not workspace-wide.** Each product gets its own team. Different products can have different teams — useful if you want different vibes per project, or if you have multiple products in flight and want the names to keep them straight in your head.
