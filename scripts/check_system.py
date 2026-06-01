#!/usr/bin/env python3
"""Check the host system against this workspace's requirements.

Surfaces a comparison table of:
  - OS, architecture
  - CPU cores
  - Total RAM
  - Free disk space at the workspace location
  - Network connectivity (api.anthropic.com reachable)
  - Required CLI tools (git, gh, python3, node, pandoc, typst)
  - Optional CLI tools (docker — needed for the dockerized Flask default)

Each row shows: required / recommended / your system / status (OK / WARN / FAIL).

USAGE
    python3 scripts/check_system.py
    python3 scripts/check_system.py --json
    python3 scripts/check_system.py --no-color

The script uses only the Python standard library — no `psutil` or other
third-party deps. RAM detection uses platform-specific commands (`sysctl`
on macOS, `/proc/meminfo` on Linux, `wmic` on Windows); if a command is
unavailable, the row falls back to "unable to detect" without failing the
overall run.

Exit code: 0 if all required checks pass (warnings allowed); 1 if any
required check fails. Optional tools never cause a non-zero exit.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ANSI color codes (disabled when output isn't a TTY or --no-color is passed)
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

NO_COLOR = False


# --- detection helpers -----------------------------------------------------


def detect_os():
    sys_name = platform.system()  # 'Darwin', 'Linux', 'Windows'
    arch = platform.machine()
    if sys_name == "Darwin":
        ver = platform.mac_ver()[0] or "?"
        os_str = f"macOS {ver}"
    elif sys_name == "Linux":
        os_str = f"Linux {platform.release()}"
        try:
            for line in Path("/etc/os-release").read_text().splitlines():
                if line.startswith("PRETTY_NAME="):
                    os_str = line.split("=", 1)[1].strip().strip('"')
                    break
        except Exception:
            pass
    elif sys_name == "Windows":
        os_str = f"Windows {platform.release()}"
    else:
        os_str = sys_name
    return {"os": os_str, "system": sys_name, "arch": arch}


def detect_ram_gb():
    """Total RAM in GB. Returns None if detection fails."""
    sys_name = platform.system()
    try:
        if sys_name == "Darwin":
            out = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"], text=True, stderr=subprocess.DEVNULL
            )
            return int(out.strip()) / 1024**3
        if sys_name == "Linux":
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) / 1024 / 1024  # KB → GB
        if sys_name == "Windows":
            out = subprocess.check_output(
                ["wmic", "OS", "get", "TotalVisibleMemorySize", "/value"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.splitlines():
                if line.startswith("TotalVisibleMemorySize="):
                    return int(line.split("=", 1)[1].strip()) / 1024 / 1024
    except Exception:
        return None
    return None


def detect_disk_free_gb():
    return shutil.disk_usage(ROOT).free / 1024**3


def detect_internet():
    """Resolve api.anthropic.com via DNS as a cheap connectivity probe."""
    try:
        socket.setdefaulttimeout(3)
        socket.gethostbyname("api.anthropic.com")
        return True
    except Exception:
        return False


def get_tool_version(name):
    """Best-effort version string for a CLI tool. Returns None if unavailable."""
    try:
        if name == "python3":
            return platform.python_version()
        if name == "node":
            out = subprocess.check_output(
                [name, "--version"], text=True, stderr=subprocess.DEVNULL
            )
            return out.strip().lstrip("v")
        out = subprocess.check_output(
            [name, "--version"], text=True, stderr=subprocess.DEVNULL
        )
        return out.splitlines()[0].strip()
    except Exception:
        return None


# --- check builder ---------------------------------------------------------


def run_checks():
    os_info = detect_os()
    ram_gb = detect_ram_gb()
    free_disk_gb = detect_disk_free_gb()
    has_internet = detect_internet()
    cpu_cores = os.cpu_count() or 0
    py_ver = platform.python_version()
    py_tuple = tuple(int(p) for p in py_ver.split(".")[:2])

    checks = []

    # 1. OS
    if os_info["system"] in {"Darwin", "Linux", "Windows"}:
        checks.append(
            {
                "row": "OS",
                "required": "macOS 12+, Linux, Windows+WSL",
                "recommended": "macOS 13+ or recent Linux",
                "actual": os_info["os"],
                "status": "ok",
            }
        )
    else:
        checks.append(
            {
                "row": "OS",
                "required": "macOS 12+, Linux, Windows+WSL",
                "recommended": "",
                "actual": os_info["os"],
                "status": "fail",
            }
        )

    # 2. CPU architecture
    arch = os_info["arch"]
    arch_status = "ok" if arch in {"x86_64", "arm64", "AMD64", "aarch64"} else "warn"
    checks.append(
        {
            "row": "CPU architecture",
            "required": "x86_64 or arm64",
            "recommended": "arm64 (Apple Silicon) on macOS",
            "actual": arch,
            "status": arch_status,
        }
    )

    # 3. CPU cores
    if cpu_cores >= 8:
        cores_status = "ok"
    elif cpu_cores >= 4:
        cores_status = "warn"
    else:
        cores_status = "fail"
    checks.append(
        {
            "row": "CPU cores (logical)",
            "required": "4",
            "recommended": "8+",
            "actual": str(cpu_cores) if cpu_cores else "(unknown)",
            "status": cores_status,
        }
    )

    # 4. RAM
    if ram_gb is None:
        ram_row = {
            "row": "RAM",
            "required": "8 GB",
            "recommended": "16 GB+",
            "actual": "(unable to detect)",
            "status": "warn",
        }
    elif ram_gb >= 16:
        ram_row = {
            "row": "RAM",
            "required": "8 GB",
            "recommended": "16 GB+",
            "actual": f"{ram_gb:.1f} GB",
            "status": "ok",
        }
    elif ram_gb >= 8:
        ram_row = {
            "row": "RAM",
            "required": "8 GB",
            "recommended": "16 GB+",
            "actual": f"{ram_gb:.1f} GB",
            "status": "warn",
        }
    else:
        ram_row = {
            "row": "RAM",
            "required": "8 GB",
            "recommended": "16 GB+",
            "actual": f"{ram_gb:.1f} GB",
            "status": "fail",
        }
    checks.append(ram_row)

    # 5. Disk
    if free_disk_gb >= 25:
        disk_status = "ok"
    elif free_disk_gb >= 10:
        disk_status = "warn"
    else:
        disk_status = "fail"
    checks.append(
        {
            "row": "Free disk (at workspace)",
            "required": "10 GB",
            "recommended": "25 GB+",
            "actual": f"{free_disk_gb:.1f} GB",
            "status": disk_status,
        }
    )

    # 6. Internet
    checks.append(
        {
            "row": "Internet (api.anthropic.com)",
            "required": "yes",
            "recommended": "stable broadband",
            "actual": "reachable" if has_internet else "NOT reachable",
            "status": "ok" if has_internet else "fail",
        }
    )

    # 7. Python
    if py_tuple >= (3, 10):
        py_status = "ok"
    else:
        py_status = "fail"
    checks.append(
        {
            "row": "Python",
            "required": "3.10+",
            "recommended": "3.11+",
            "actual": py_ver,
            "status": py_status,
        }
    )

    # 8. Node
    node_ver = get_tool_version("node")
    if node_ver:
        try:
            node_major = int(node_ver.split(".")[0])
            if node_major >= 20:
                node_status = "ok"
            elif node_major >= 18:
                node_status = "warn"
            else:
                node_status = "fail"
        except Exception:
            node_status = "warn"
        node_actual = node_ver
    else:
        node_status = "fail"
        node_actual = "(not installed)"
    checks.append(
        {
            "row": "Node.js",
            "required": "20+",
            "recommended": "20 LTS",
            "actual": node_actual,
            "status": node_status,
        }
    )

    # 9-12. Required tools (git, gh, pandoc, typst)
    for tool in ["git", "gh", "pandoc", "typst"]:
        ver = get_tool_version(tool)
        if ver:
            checks.append(
                {
                    "row": tool,
                    "required": "yes",
                    "recommended": "latest",
                    "actual": ver if len(ver) < 50 else ver[:47] + "...",
                    "status": "ok",
                }
            )
        else:
            checks.append(
                {
                    "row": tool,
                    "required": "yes",
                    "recommended": "latest",
                    "actual": "(not installed)",
                    "status": "fail",
                }
            )

    # 13. Optional: docker (needed for the dockerized Flask default)
    ver = get_tool_version("docker")
    if ver:
        checks.append(
            {
                "row": "docker (optional)",
                "required": "for Flask MVPs",
                "recommended": "Docker Desktop or Engine",
                "actual": ver if len(ver) < 50 else ver[:47] + "...",
                "status": "ok",
            }
        )
    else:
        checks.append(
            {
                "row": "docker (optional)",
                "required": "for Flask MVPs",
                "recommended": "Docker Desktop or Engine",
                "actual": "(not installed)",
                "status": "warn",
            }
        )

    return checks


# --- output ---------------------------------------------------------------


def color(text, code):
    return text if NO_COLOR else f"{code}{text}{RESET}"


STATUS_SYMBOL = {"ok": "✓", "warn": "⚠", "fail": "✗"}
STATUS_COLOR = {"ok": GREEN, "warn": YELLOW, "fail": RED}


def print_table(checks):
    headers = ["Component", "Required", "Recommended", "Your system", "Status"]

    # Markdown table — renders cleanly in Claude Code's TUI and on GitHub,
    # and still reads fine as raw text in a plain terminal (pipe-delimited
    # rows wrap predictably instead of breaking mid-column-header).
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")

    for c in checks:
        # Status emoji stays uncolored inside the table cell because some
        # markdown renderers strip ANSI codes from table cells; the colored
        # summary line below preserves the visual signal.
        cells = [
            c["row"],
            c["required"],
            c["recommended"],
            c["actual"],
            STATUS_SYMBOL[c["status"]],
        ]
        print("| " + " | ".join(cells) + " |")

    # Summary
    passed = sum(1 for c in checks if c["status"] == "ok")
    warned = sum(1 for c in checks if c["status"] == "warn")
    failed = sum(1 for c in checks if c["status"] == "fail")
    print()
    print(
        color("Summary:", BOLD),
        color(f"{passed} passed", GREEN),
        " ",
        color(f"{warned} warning(s)", YELLOW),
        " ",
        color(f"{failed} failed", RED),
    )
    print()
    if failed == 0 and warned == 0:
        print(
            color(
                "Your system meets every requirement and recommendation. You're ready to use the workspace.",
                GREEN,
            )
        )
    elif failed == 0:
        print(
            color(
                "Your system meets the requirements but some recommendations are unmet. "
                "The workspace will work; you may hit limits on heavier tasks (Docker + RN bundler + browser).",
                YELLOW,
            )
        )
    else:
        print(
            color(
                f"Your system is missing required prerequisites ({failed} failure(s)). "
                "Address those before running the pipeline; see README.md \"System requirements\" for guidance.",
                RED,
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description="Check the host system against this workspace's requirements."
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    args = parser.parse_args()

    global NO_COLOR
    NO_COLOR = args.no_color or not sys.stdout.isatty()

    checks = run_checks()

    if args.json:
        print(json.dumps(checks, indent=2))
    else:
        print_table(checks)

    return 1 if any(c["status"] == "fail" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
