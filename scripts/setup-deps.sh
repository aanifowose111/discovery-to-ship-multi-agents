#!/usr/bin/env bash
# setup-deps.sh — install all required tools for the workspace in one go.
# Idempotent: detects already-installed tools and skips them.
# Detects macOS vs Linux and uses the appropriate package manager.
#
# Required:  git, GitHub CLI (gh), pandoc, typst, python3
# Optional:  node@20 (only needed for mobile work)
#
# Usage: bash scripts/setup-deps.sh [--no-optional]

set -euo pipefail

INSTALL_OPTIONAL=1
for arg in "$@"; do
    case "$arg" in
        --no-optional) INSTALL_OPTIONAL=0 ;;
        -h|--help)
            echo "Usage: bash scripts/setup-deps.sh [--no-optional]"
            echo
            echo "  --no-optional    skip node@20 (only needed for mobile work)"
            exit 0
            ;;
    esac
done

if [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'
    BOLD=$'\e[1m';   DIM=$'\e[2m';    RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; CYAN=""; BOLD=""; DIM=""; RESET=""
fi

case "$(uname -s)" in
    Darwin) OS="macos" ;;
    Linux)  OS="linux" ;;
    *) echo "Unsupported OS: $(uname -s). Install manually per README.md." >&2; exit 1 ;;
esac

echo "${BOLD}${CYAN}Setting up dependencies for: $OS${RESET}"
echo

ensure_homebrew() {
    if ! command -v brew >/dev/null 2>&1; then
        echo "${YELLOW}Homebrew not found. Installing...${RESET}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "${DIM}Homebrew already installed.${RESET}"
    fi
}

install_macos() {
    ensure_homebrew

    local tools=(git gh pandoc typst python@3.12)
    [ "$INSTALL_OPTIONAL" -eq 1 ] && tools+=(node@20)

    for tool in "${tools[@]}"; do
        printf "${BOLD}%-20s${RESET} " "$tool:"
        if brew list "$tool" >/dev/null 2>&1; then
            echo "${GREEN}already installed${RESET}"
        else
            echo "${YELLOW}installing...${RESET}"
            brew install "$tool"
        fi
    done
}

install_linux() {
    if ! command -v apt >/dev/null 2>&1; then
        echo "${YELLOW}This script supports apt-based distros (Ubuntu/Debian/WSL).${RESET}"
        echo "${YELLOW}For other distros, install: git, gh, pandoc, python3, node, typst manually.${RESET}"
        exit 1
    fi

    echo "${CYAN}Running apt update...${RESET}"
    sudo apt update -qq

    local apt_tools=(git gh pandoc python3 python3-pip)
    for tool in "${apt_tools[@]}"; do
        printf "${BOLD}%-20s${RESET} " "$tool:"
        if dpkg -s "$tool" >/dev/null 2>&1; then
            echo "${GREEN}already installed${RESET}"
        else
            echo "${YELLOW}installing...${RESET}"
            sudo apt install -y "$tool"
        fi
    done

    # typst is not in apt; install via cargo if available, else direct download
    if command -v typst >/dev/null 2>&1; then
        echo "${BOLD}typst:${RESET}               ${GREEN}already installed${RESET}"
    elif command -v cargo >/dev/null 2>&1; then
        echo "${BOLD}typst:${RESET}               ${YELLOW}installing via cargo...${RESET}"
        cargo install --locked typst-cli
    else
        echo "${BOLD}typst:${RESET}               ${YELLOW}not installed${RESET}"
        echo "    ${DIM}Install via cargo (cargo install typst-cli) or download from"
        echo "    https://github.com/typst/typst/releases${RESET}"
    fi

    # Node 20 via NodeSource if optional + missing
    if [ "$INSTALL_OPTIONAL" -eq 1 ]; then
        if command -v node >/dev/null 2>&1; then
            echo "${BOLD}node:${RESET}                ${GREEN}already installed${RESET}"
        else
            echo "${BOLD}node:${RESET}                ${YELLOW}installing Node 20 via NodeSource...${RESET}"
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt install -y nodejs
        fi
    fi
}

case "$OS" in
    macos) install_macos ;;
    linux) install_linux ;;
esac

echo
echo "${GREEN}${BOLD}Dependency setup complete.${RESET}"
echo "${DIM}Verify with: bash scripts/preflight.sh${RESET}"
echo "${DIM}If GitHub auth not done:    gh auth login${RESET}"
echo "${DIM}Then open Claude Code:      claude${RESET}"
