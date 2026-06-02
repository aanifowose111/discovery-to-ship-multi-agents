---
description: Kick off the build phase for a green-lit-to-build product. Invokes senior-software-engineer to ask the orientation questions (web/mobile/desktop/hybrid order, MVP vs. fully-featured, build-first subsystem), then routes work to the right senior-engineer persona. Use after /scope-mvp returns green-lit-to-build, or at any point in the build when you want a fresh "where do I start" prompt.
argument-hint: <product-slug>
---

You are about to kick off the build phase for a product. This command does not implement anything itself — it routes the user through orientation questions and then to the right specialist persona for the chosen first subsystem.

The orchestration is owned by the `senior-software-engineer` persona; you invoke that persona and let it drive.

**Arguments:** $ARGUMENTS — the product slug. The brief must exist at `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, or `desktop-apps/<slug>/MVP.md` with `status: green-lit-to-build`.

### Pre-flight

1. **Verify the brief exists.** Check `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, and `desktop-apps/<slug>/MVP.md`. If none exists, stop and tell the user: "No MVP brief at any of `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, or `desktop-apps/<slug>/MVP.md`. Run `/scope-mvp <slug>` first."

2. **Verify the brief's status.** Read frontmatter. If `status` is not `green-lit-to-build`, surface:

   > Brief status is `<current-status>`, not `green-lit-to-build`. The build orchestration assumes the brief has been finalized and approved. Continue anyway?

   Wait for confirmation if not green-lit.

3. **Check pre-build decisions.** Read frontmatter for `design-path` and `build-support`. If either is missing, surface:

   > The pre-build decisions checkpoint from `/scope-mvp` wasn't recorded:
   > - design-path: <missing | recorded>
   > - build-support: <missing | recorded>
   >
   > Want to set them now before continuing?

   If user wants to set them, ask the two questions from `.claude/commands/scope-mvp.md` checkpoint #2 and record the answers in the brief's frontmatter.

### Do

Invoke the `senior-software-engineer` subagent using the custom-subagent invocation pattern in `CLAUDE.md`:

```
Agent({
  subagent_type: "general-purpose",
  description: "Build orchestration for <slug>",
  prompt: "You are about to act as the senior-software-engineer for the build phase of <slug>. Read .claude/agents/senior-software-engineer.md in full and treat its body as your role and process. Read the brief at <path-to-MVP.md>, the design research and brief at <path-to-design/> (if they exist), and CLAUDE.md for the workspace conventions and the build-phase skill auto-invocation policy. Then ask the user the three orientation questions from §'Build-order questions you ask' in your persona file (in this order: web/mobile/desktop/hybrid order based on the brief's domain; MVP or fully-featured; first subsystem to tackle). Wait for the user's answers between questions. After all three are answered, propose the next-step specialist persona to invoke and the specific first task, and tell the user to either confirm to proceed or override."
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

### Notes

- This command is the **entry point** to the build phase. After this, individual specialists are invoked as the build proceeds — `senior-software-engineer` routes them in based on what's done and what's next.
- The user can re-run `/start-build <slug>` at any point if they want a fresh "where am I" + "what's next" prompt from the senior software engineer.
- The senior personas all live in `.claude/agents/senior-*.md` and are invoked via the custom-subagent invocation pattern in `CLAUDE.md`.
