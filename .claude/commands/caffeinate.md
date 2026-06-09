---
description: Prevent the display + system from sleeping while Claude Code is working (macOS-only — uses the built-in `caffeinate` command). Spawns `caffeinate -d -i` in the background, captures its PID, and reports back. Pair with /stop-caffeinate to release. Useful during long builds and the design phase.
argument-hint: (no arguments)
---

You are about to spawn a backgrounded `caffeinate` process that prevents the display from sleeping while Claude Code is running. macOS-only.

### Pre-flight

1. **Platform check.** Run `uname -s` via Bash. If the result is NOT `Darwin`, stop and tell the user:
   > `/caffeinate` is macOS-only — it wraps the built-in `caffeinate` command. On Linux, the equivalent is `systemd-inhibit --what=idle:sleep --who=claude-code --why=build`. On Windows, use `powercfg /requestsoverride PROCESS pwsh.exe DISPLAY` or a third-party tool. I can guide you through either if you tell me your OS.

   Then stop. Do not write a pidfile.

2. **Check for existing caffeinate state.** The PID file lives at `~/.claude/caffeinate.pid`. Run:
   ```bash
   if [ -f ~/.claude/caffeinate.pid ]; then
     PID=$(cat ~/.claude/caffeinate.pid)
     if kill -0 "$PID" 2>/dev/null; then
       echo "ALREADY_RUNNING|$PID"
     else
       echo "STALE_PIDFILE|$PID"
       rm ~/.claude/caffeinate.pid
     fi
   else
     echo "FRESH"
   fi
   ```

   - **ALREADY_RUNNING:** stop and report: "Already caffeinated (PID `<pid>`). Display will stay awake until you run `/stop-caffeinate` or kill PID `<pid>` manually."
   - **STALE_PIDFILE:** clean up (the script above already removed it), surface a note: "Cleaned up a stale pidfile for PID `<pid>` (the process was already gone). Continuing fresh."
   - **FRESH:** continue to Step 1.

### Do

1. **Spawn the background process.** Run via Bash:
   ```bash
   nohup caffeinate -d -i </dev/null >/dev/null 2>&1 &
   echo $! > ~/.claude/caffeinate.pid
   cat ~/.claude/caffeinate.pid
   ```

   The flags:
   - `-d` prevents the **display** from sleeping
   - `-i` prevents the **system** from idle-sleeping
   - `nohup ... </dev/null >/dev/null 2>&1 &` detaches it fully from this shell

   The PID is written to `~/.claude/caffeinate.pid` so `/stop-caffeinate` can find it later. Confirm the pidfile was written (the trailing `cat` will print the PID).

2. **Verify the process actually started.** Run `kill -0 <pid>` — if it returns 0, the process is alive. If non-zero, the spawn failed (rare); surface the error and remove the pidfile.

### Report to user

> ☕ Caffeinated. Display + system will stay awake until you run `/stop-caffeinate`, the process is killed manually (`kill <pid>`), or your Mac reboots.
>
> - PID: `<pid>`
> - Started: `<HH:MM:SS>` (local time)
> - Pidfile: `~/.claude/caffeinate.pid`

### Notes

- **Doesn't auto-stop when Claude Code exits.** The `nohup` detaches it from the shell, so closing this session leaves the caffeinate process running. Stop it explicitly when done — that's why `/stop-caffeinate` exists.
- **Only one caffeinate process at a time per user.** If you want multiple (per-project caffeination), this approach would need a per-project pidfile — current scope is one global state.
- **Battery awareness:** the user might be on battery — `caffeinate -d -i` drains power faster than letting the display sleep. Worth mentioning in the confirmation message if the user is clearly on the road (we don't auto-detect battery state).
- **No audit log entry.** This is a UX command, not a build event.
