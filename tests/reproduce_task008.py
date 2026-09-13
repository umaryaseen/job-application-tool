"""Run the complete synthetic TASK-008 build, review and export workflow."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from job_application_engine.snapshots.export import export_snapshot
from job_application_engine.snapshots.review import approve_snapshot
from job_application_engine.snapshots.store import build_snapshot
from tests.test_snapshots import NOW, build_inputs


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="jae-task008-") as directory:
        root = Path(directory)
        request, profile, reviews, capture = build_inputs(root)
        built = build_snapshot(request, root=root)
        approval = approve_snapshot(
            request.snapshot_id,
            reviewer_id="synthetic-final-reviewer",
            approved_at=NOW,
            root=root,
        )
        exported = export_snapshot(
            request.snapshot_id,
            destination=root / "exports" / "synthetic-one",
            profile=profile,
            reviews=reviews,
            support_captures={("attestation-one", 1): capture},
            now=NOW,
            root=root,
        )
        print(f"snapshot={built.path}")
        print(f"manifest_sha256={built.manifest_sha256}")
        print(f"approval_manifest_sha256={approval.manifest_sha256}")
        print(f"export={exported}; pdf_bytes={(exported / 'output.pdf').stat().st_size}")


if __name__ == "__main__":
    main()
