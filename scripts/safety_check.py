#!/usr/bin/env python3
"""
Safety check. Run before every Freqtrade command (scripts/ft.sh does this).

Stops with an error if:
  1. any config file has dry_run != true (or base.json has no dry_run at all)
  2. any config file contains a non-empty exchange key/secret
  3. any file that git would commit looks like it contains a key, token or password
  4. a .env file is tracked by git

Usage: python scripts/safety_check.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SECRET_PATTERNS = {
    "telegram_bot_token": re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),
    "binance_like_api_key": re.compile(r"\b[A-Za-z0-9]{64}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # KEY=value / "key": "value" style assignments with a non-empty value
    "secret_assignment": re.compile(
        r"""(?ix)
        \b(api[_-]?key|api[_-]?secret|secret[_-]?key|bot[_-]?token|password|passwd|jwt[_-]?secret)\b
        ["']?\s*[:=]\s*["']?
        (?!["']?\s*(?:$|,|\}|<|\$\{|your|xxx|changeme))   # empty / placeholder values are fine
        [^\s"',}]{8,}
        """
    ),
}

# Files that legitimately describe these patterns (this script and its tests).
SCAN_EXCLUDE = {"scripts/safety_check.py", "tests/test_safety_check.py"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".feather", ".parquet", ".pdf", ".ico"}


def git_files() -> list[str]:
    """Files git tracks or would add (respects .gitignore)."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in out.splitlines() if f and (REPO / f).is_file()]


def iter_dry_run_values(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k == "dry_run":
                yield p, v
            yield from iter_dry_run_values(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_dry_run_values(v, f"{path}[{i}]")


def check_configs(errors: list[str]) -> None:
    config_dir = REPO / "config"
    base = config_dir / "base.json"
    if not base.exists():
        errors.append("config/base.json is missing")
    for cfg in sorted(config_dir.rglob("*.json")):
        rel = cfg.relative_to(REPO)
        try:
            data = json.loads(cfg.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON ({e})")
            continue
        found = list(iter_dry_run_values(data))
        if cfg == base and not found:
            errors.append(f"{rel}: dry_run is not set (must be true)")
        for p, v in found:
            if v is not True:
                errors.append(f"{rel}: {p} = {v!r} (must be true)")
        exch = data.get("exchange", {}) if isinstance(data, dict) else {}
        for k in ("key", "secret", "password", "uid"):
            if exch.get(k):
                errors.append(f"{rel}: exchange.{k} is not empty (no API keys allowed)")


def check_secrets(errors: list[str]) -> None:
    files = git_files()
    for f in files:
        if f == ".env" or f.endswith("/.env"):
            errors.append(f"{f}: .env must never be committed")
            continue
        if f in SCAN_EXCLUDE or Path(f).suffix.lower() in BINARY_SUFFIXES:
            continue
        try:
            text = (REPO / f).read_text(errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, pat in SECRET_PATTERNS.items():
                if pat.search(line):
                    errors.append(f"{f}:{lineno}: looks like a secret ({name})")


def main() -> int:
    errors: list[str] = []
    check_configs(errors)
    check_secrets(errors)
    if errors:
        print("SAFETY CHECK FAILED - stopping.")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Safety check OK: dry_run is true everywhere, no secrets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
