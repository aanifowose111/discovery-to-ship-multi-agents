#!/usr/bin/env bash
# preflight.sh — verify all dependencies and workspace state for
# discovery-to-ship-multi-agents. Runnable outside Claude Code; surfaces a
# colored punch list of what's installed / missing / misconfigured.
#
# Pure verification — never modifies anything. Safe to run repeatedly.
#
# Usage: bash scripts/preflight.sh [--no-color] [--quiet]
#
# Exit codes:
#   0  all required checks pass (warnings allowed)
#   1  one or more required checks fail

set -uo pipefail

USE_COLOR=1
QUIET=0
for arg in "$@"; do
    case "$arg" in
        --no-color) USE_COLOR=0 ;;
        --quiet)    QUIET=1 ;;
        -h|--help)
            echo "Usage: bash scripts/preflight.sh [--no-color] [--quiet]"
            exit 0
            ;;
    esac
done

if [ "$USE_COLOR" -eq 1 ] && [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RED=$'\e[31m'; CYAN=$'\e[36m'
    BOLD=$'\e[1m';   DIM=$'\e[2m';    RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; RED=""; CYAN=""; BOLD=""; DIM=""; RESET=""
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

pass=0
warn=0
fail=0

check() {
    local label="$1"
    local result="$2"   # "pass" | "warn" | "fail"
    local detail="${3:-}"
    local fix="${4:-}"

    case "$result" in
        pass)
            printf "  ${GREEN}✓${RESET} %-40s %s\n" "$label" "$detail"
            pass=$((pass + 1))
            ;;
        warn)
            printf "  ${YELLOW}⚠${RESET} %-40s %s\n" "$label" "$detail"
            [ -n "$fix" ] && printf "    ${DIM}→ %s${RESET}\n" "$fix"
            warn=$((warn + 1))
            ;;
        fail)
            printf "  ${RED}✗${RESET} %-40s %s\n" "$label" "$detail"
            [ -n "$fix" ] && printf "    ${DIM}→ %s${RESET}\n" "$fix"
            fail=$((fail + 1))
            ;;
    esac
}

print_header() {
    [ "$QUIET" -eq 1 ] && return
    echo
    printf "${BOLD}${CYAN}=== %s ===${RESET}\n" "$1"
}

# ─── Detect OS for install commands ──────────────────────────────────────
case "$(uname -s)" in
    Darwin) OS="macos"; INSTALL="brew install" ;;
    Linux)  OS="linux"; INSTALL="sudo apt install" ;;
    *)      OS="other"; INSTALL="(see README for install)" ;;
esac

# ─── Tools ───────────────────────────────────────────────────────────────
print_header "Required tools"

if command -v git >/dev/null 2>&1; then
    check "git" pass "$(git --version | head -1)"
else
    check "git" fail "not found" \
          "macOS: xcode-select --install | Linux: $INSTALL git"
fi

if command -v gh >/dev/null 2>&1; then
    check "GitHub CLI (gh)" pass "$(gh --version | head -1)"
else
    check "GitHub CLI (gh)" fail "not found" "$INSTALL gh"
fi

if command -v pandoc >/dev/null 2>&1; then
    check "pandoc" pass "$(pandoc --version | head -1)"
else
    check "pandoc" fail "not found" "$INSTALL pandoc"
fi

if command -v typst >/dev/null 2>&1; then
    check "typst" pass "$(typst --version 2>&1 | head -1)"
else
    check "typst" warn "not found (PDF export will fail)" "$INSTALL typst"
fi

if command -v python3 >/dev/null 2>&1; then
    check "python3" pass "$(python3 --version 2>&1)"
else
    check "python3" fail "not found" "$INSTALL python3"
fi

if command -v node >/dev/null 2>&1; then
    check "node" pass "$(node --version) (mobile-only)"
else
    check "node" warn "not found (only needed for mobile work)" "$INSTALL node@20"
fi

if command -v claude >/dev/null 2>&1; then
    check "Claude Code CLI" pass "available"
else
    check "Claude Code CLI" warn "not in PATH" \
          "https://docs.claude.com/en/docs/claude-code/installation"
fi

# ─── Git identity ────────────────────────────────────────────────────────
print_header "Git identity"

git_email="$(git config user.email 2>/dev/null || true)"
git_name="$(git config user.name 2>/dev/null || true)"

if [ -n "$git_email" ]; then
    check "user.email" pass "$git_email"
else
    check "user.email" fail "not set" \
          'git config --global user.email "you@example.com"'
fi

if [ -n "$git_name" ]; then
    check "user.name" pass "$git_name"
else
    check "user.name" fail "not set" \
          'git config --global user.name "Your Name"'
fi

# ─── GitHub auth ─────────────────────────────────────────────────────────
print_header "GitHub authentication"

if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        gh_account="$(gh api user --jq '.login' 2>/dev/null || echo unknown)"
        check "gh auth" pass "logged in as $gh_account"
    else
        check "gh auth" fail "not authenticated" "gh auth login"
    fi
else
    check "gh auth" warn "gh not installed; skipping"
fi

# ─── Repo state ──────────────────────────────────────────────────────────
print_header "Repository state"

if [ -f external/agent-skills/agents/code-reviewer.md ]; then
    check "agent-skills submodule" pass "initialized"
else
    check "agent-skills submodule" fail "not initialized" \
          "git submodule update --init --recursive"
fi

for persona in code-reviewer security-auditor test-engineer; do
    target=".claude/agents/${persona}.md"
    if [ -f "$target" ] && [ -s "$target" ]; then
        check "${persona}.md file copy" pass "present"
    else
        check "${persona}.md file copy" fail "missing or empty" \
              "Run: bash scripts/update-agent-skills.sh (re-copies personas + skills from submodule)"
    fi
done

if [ -f .claude-acknowledged ]; then
    ack_email="$(grep '^acknowledged-by:' .claude-acknowledged 2>/dev/null | cut -d: -f2- | xargs || echo unknown)"
    check ".claude-acknowledged" pass "on file (by: $ack_email)"
else
    owner_email="aanifowose111@gmail.com"
    if [ "$git_email" = "$owner_email" ]; then
        check ".claude-acknowledged" pass "you are the repo owner — acknowledgment waived"
    else
        check ".claude-acknowledged" warn "not on file" \
              "In Claude Code: /acknowledge-contributing"
    fi
fi

# ─── Summary ─────────────────────────────────────────────────────────────
echo
printf "${BOLD}=== Summary ===${RESET}\n"
printf "  ${GREEN}✓ %d passed${RESET}    ${YELLOW}⚠ %d warnings${RESET}    ${RED}✗ %d failed${RESET}\n" \
       "$pass" "$warn" "$fail"

if [ "$fail" -eq 0 ] && [ "$warn" -eq 0 ]; then
    printf "\n  ${GREEN}${BOLD}All checks passed.${RESET} Try ${CYAN}/discover${RESET} or ${CYAN}/help${RESET} in Claude Code.\n"
    exit 0
elif [ "$fail" -eq 0 ]; then
    printf "\n  ${YELLOW}Workspace usable but with warnings.${RESET} See above for context.\n"
    exit 0
else
    printf "\n  ${RED}Required tools or repo state missing.${RESET} Resolve and re-run.\n"
    exit 1
fi
