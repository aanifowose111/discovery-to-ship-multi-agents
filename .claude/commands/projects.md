---
description: List all discovery-cycle projects in the workspace (by run-id), then offer actions on a chosen one — primarily delete, with destructive-action multi-confirm safety.
argument-hint: (no arguments)
---

You are surfacing the project-management interface. This is a maintenance command for cleaning up discovery work the user no longer needs.

A **project** = the full set of artifacts keyed by a single run-id (`<8-alphanumeric>-<MMDDYY>`). The helper script `scripts/delete_project.py` knows how to enumerate and (with `--force`) delete those artifacts; this command wraps it with a safe interactive flow.

### Do

1. **Inventory:** `python3 scripts/delete_project.py list --json` to get the structured list of projects.
   - If empty (no projects yet): tell the user "No projects found in this workspace yet — run `/discover` to start one," then stop.
2. **Present the list** to the user in human-readable form (project run-id + date + summary like "12 cards, 3 validations, 0 builds"), then use `AskUserQuestion` to pick one:
   - One option per project: label = `<run-id> (<date>) — <summary>`, description = a fuller breakdown
   - Plus a **Cancel** option at the end
   - If only 1-3 projects exist, all fit comfortably; if more than 4, AskUserQuestion's 4-option cap means you'll need to ask the user to type the run-id directly via "Other" — or do the picker in pages of 4 (show first 4, with the 4th option being "show more"). Pick whichever is cleaner; default to direct-list when ≤4 projects, paged when >4.
3. **Action picker** for the chosen project — `AskUserQuestion`:
   - **View artifacts** — run `python3 scripts/delete_project.py show <run-id>`, show the output, then loop back to this action picker
   - **Delete project (irreversible)** — go to the delete flow (next step)
   - **Cancel** — exit
4. **Delete flow — Step 1 of 2 (first confirmation):**
   - Run `python3 scripts/delete_project.py show <run-id>` to list everything that will be deleted.
   - Display the output with a warning header:
     > **⚠ This will permanently delete the following.** Files bypass the Trash and are removed from disk. The action **CANNOT be undone**. Make sure you have anything you want to keep saved elsewhere first.
   - Use `AskUserQuestion` with two options:
     - **Continue to final confirmation** — proceeds to step 2
     - **Cancel — keep this project** — exits without deleting
5. **Delete flow — Step 2 of 2 (final confirmation):**
   - Show a shorter, blunter header:
     > **FINAL CONFIRMATION**. About to permanently delete **\<N\> file(s)** across **\<M\> director(ies)** for project **\<run-id\>**. There is no undo. Choose carefully.
   - Use `AskUserQuestion` with two options:
     - **YES, DELETE PERMANENTLY** — proceeds to actual deletion
     - **Cancel — do not delete** — exits without deleting
6. **Execute deletion:**
   - Run `python3 scripts/delete_project.py delete <run-id> --force`.
   - Surface the script's success line to the user (`Deleted project <run-id>: N file(s) removed.`).
   - Suggest 2-3 reasonable next actions (e.g., `/discover` to start fresh, `/menu` for state, `/run-tests` to confirm health).

### Important — no auto-actions

- **NEVER** run `delete --force` without BOTH confirmations passing.
- **NEVER** chain automatically into other commands after deletion.
- If the user's pick is ambiguous on any step, **default to the safer option** (cancel / keep).
- Don't bypass the confirmations even if the user says "just delete it" — explain that this is a safety guard and walk them through the two confirms quickly.

### What gets deleted (per the script)

For the given run-id:
- `ideas/<run-id>/` — entire folder (active cards + any platform metadata files like `.DS_Store`)
- `ideas/killed/<run-id>/` — entire folder (killed cards from this cycle)
- `market-research/<run-id>/` — entire folder (triage, scan, trends, validations, scopings)
- For each slug found in those folders:
  - `web-apps/<slug>/` — entire folder (if the slug was scoped to a web app)
  - `mobile-apps/<slug>/` — entire folder (if scoped to a mobile app)
  - `generated/**/*<slug>*` — every exported file referencing the slug

The script handles all path discovery — don't manually compose paths.
