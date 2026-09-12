"""Export and compare the checked-in profile JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .domain.profile import ProfileRevision


def profile_schema() -> dict[str, Any]:
    return ProfileRevision.model_json_schema()


def export_profile_schema(destination: str | Path) -> None:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile_schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m job_application_engine.schema_export PATH")
    export_profile_schema(sys.argv[1])
