#!/usr/bin/env python3
"""Reject staged private files and common credential material."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PRIVATE_PARTS = {".env", "private", "local-data", "identity-documents", "browser-profiles"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(?:password|secret|token)\s*[:=]\s*['\"][^'\"]{12,}"),
)


def staged_files(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"],
        check=True,
        capture_output=True,
    )
    return [item for item in result.stdout.decode().split("\0") if item]


def check(repo: Path) -> list[str]:
    failures: list[str] = []
    for name in staged_files(repo):
        path = Path(name)
        if any(part in PRIVATE_PARTS for part in path.parts) or path.name.startswith(".env"):
            failures.append(f"private path staged: {name}")
            continue
        try:
            content = subprocess.run(
                ["git", "-C", str(repo), "show", f":{name}"],
                check=True,
                capture_output=True,
            ).stdout.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError:
            failures.append(f"could not read staged file: {name}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                failures.append(f"credential-like content staged: {name}")
                break
    return failures


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    failures = check(repo)
    if failures:
        print("\n".join(f"commit safeguard: {item}" for item in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
