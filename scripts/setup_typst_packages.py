#!/usr/bin/env python3
"""Explicitly download pinned public renderer dependencies; never applicant data."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from urllib.request import urlopen

from job_application_engine.rendering.packages import (
    FONT_AWESOME_COMMIT,
    FONT_AWESOME_FILES,
    FONT_AWESOME_VERSION,
    checked_assets,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--download", action="store_true", help="explicit network setup opt-in")
    args = parser.parse_args()
    if not args.destination.is_absolute():
        parser.error("destination must be absolute")
    if not args.download:
        checked_assets(args.destination)
        print("Pinned local Typst assets verified; no network used.")
        return 0
    base = (
        "https://raw.githubusercontent.com/typst/packages/"
        f"{FONT_AWESOME_COMMIT}/packages/preview/fontawesome/{FONT_AWESOME_VERSION}/"
    )
    directory = args.destination / "preview" / "fontawesome" / FONT_AWESOME_VERSION
    directory.mkdir(parents=True, exist_ok=True)
    for name, expected in FONT_AWESOME_FILES.items():
        target = directory / name
        if target.exists():
            if target.is_symlink() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                parser.error("existing asset changed; choose a new setup destination")
            continue
        with urlopen(base + name, timeout=30) as response:
            data = response.read(1_000_001)
        if len(data) > 1_000_000 or hashlib.sha256(data).hexdigest() != expected:
            parser.error("downloaded asset does not match the pinned checksum")
        target.write_bytes(data)
    checked_assets(args.destination)
    print("Pinned public Typst assets installed; set JAE_TYPST_PACKAGE_ROOT to this destination.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
