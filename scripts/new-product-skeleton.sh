#!/usr/bin/env bash
# new-product-skeleton.sh — scaffold a new product folder under
# web-apps/<slug>/ or mobile-apps/<slug>/ (or both for hybrid).
#
# Creates the expected per-product layout: README.md, .gitignore (for
# build artifacts that should never enter git), design/ subfolder, and
# (for web) a previews/fixtures/ scaffold. Does NOT create MVP.md —
# that's the /scope-mvp command's job.
#
# Usage: bash scripts/new-product-skeleton.sh <slug> <web|mobile|hybrid>

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: bash scripts/new-product-skeleton.sh <slug> <web|mobile|hybrid>"
    echo
    echo "  slug    kebab-case product identifier (e.g., dev-task-tracker)"
    echo "  domain  web | mobile | hybrid"
    exit 1
fi

SLUG="$1"
DOMAIN="$2"

if ! [[ "$SLUG" =~ ^[a-z][a-z0-9-]*$ ]]; then
    echo "✗ Slug must be lowercase kebab-case (letters, digits, hyphens; start with a letter)." >&2
    exit 1
fi

case "$DOMAIN" in
    web|mobile|hybrid) ;;
    *) echo "✗ Domain must be one of: web, mobile, hybrid." >&2; exit 1 ;;
esac

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'
    DIM=$'\e[2m';    RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; CYAN=""; DIM=""; RESET=""
fi

scaffold_web() {
    local dir="web-apps/$SLUG"
    if [ -d "$dir" ]; then
        echo "${YELLOW}⚠ $dir already exists; not overwriting.${RESET}"
        return
    fi
    echo "${CYAN}Creating $dir/...${RESET}"
    mkdir -p "$dir/design" "$dir/previews/fixtures"

    cat > "$dir/README.md" <<EOF
# $SLUG (web)

Per-product overview. Filled in once the product is being actively built.

- **Domain:** web
- **Stack:** _record from MVP.md once the brief picks one_
- **Status:** not-yet-started (no MVP brief)

## Documents

- \`MVP.md\` — the source-of-truth brief (created by \`/scope-mvp $SLUG\`)
- \`design/\` — design research, brief, Figma link, handoff
  (created by \`/research-design\` and \`/draft-design-brief\`)
- \`previews/\` — Jinja preview fixtures for the \`web-preview\` skill
EOF

    cat > "$dir/.gitignore" <<'EOF'
# Build artifacts
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
venv/
instance/

# Env / secrets
.env
.env.local
SECRETS.md

# Previews
previews/_rendered/

# OS
.DS_Store
EOF

    echo "${GREEN}✓ Created $dir/${RESET}"
    echo "${DIM}  Next: /scope-mvp $SLUG in Claude Code to draft the MVP brief.${RESET}"
}

scaffold_mobile() {
    local dir="mobile-apps/$SLUG"
    if [ -d "$dir" ]; then
        echo "${YELLOW}⚠ $dir already exists; not overwriting.${RESET}"
        return
    fi
    echo "${CYAN}Creating $dir/...${RESET}"
    mkdir -p "$dir/design"

    cat > "$dir/README.md" <<EOF
# $SLUG (mobile)

Per-product overview. Filled in once the product is being actively built.

- **Domain:** mobile
- **Stack:** _record from MVP.md once the brief picks one_
- **Status:** not-yet-started (no MVP brief)

## Documents

- \`MVP.md\` — the source-of-truth brief (created by \`/scope-mvp $SLUG\`)
- \`design/\` — design research, brief, Figma link, handoff
EOF

    cat > "$dir/.gitignore" <<'EOF'
node_modules/
.expo/
.expo-shared/
ios/build/
ios/Pods/
ios/DerivedData/
android/app/build/
android/.gradle/
.env
.env.local
SECRETS.md
.DS_Store
*.jks
*.p12
*.mobileprovision
EOF

    echo "${GREEN}✓ Created $dir/${RESET}"
    echo "${DIM}  Next: /scope-mvp $SLUG in Claude Code to draft the MVP brief.${RESET}"
}

case "$DOMAIN" in
    web)    scaffold_web ;;
    mobile) scaffold_mobile ;;
    hybrid) scaffold_web; scaffold_mobile ;;
esac

echo
echo "${GREEN}Done.${RESET}"
