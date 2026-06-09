#!/usr/bin/env bash
# SessionStart hook for Claude Code (matcher: startup).
#
# Resets the break-reminder timer at the start of a fresh Claude Code session.
# Without this, `.session-start` persists from a previous session and the
# break-reminder computes wallclock elapsed time across closes/reopens.
#
# Pairs with .claude/hooks/break-reminder.sh (UserPromptSubmit) which adds
# in-session idle detection (if gap between prompts > 30 min, also reset).

STATE_DIR="${HOME}/.claude"
mkdir -p "${STATE_DIR}"
date +%s > "${STATE_DIR}/.session-start"
rm -f "${STATE_DIR}/.last-prompt" "${STATE_DIR}/.last-break-reminder"
exit 0
