"""Reproduce real TASK-007 reports under the ignored artifacts directory."""

from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from job_application_engine.ats_qa.pdf import run_pdf_qa  # noqa: E402
from tests.rendering.fixtures import expected, production_pdf  # noqa: E402


def main() -> None:
    root = Path("artifacts") / "qa" / f"task-007-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    root.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="jae-task007-") as temporary:
        private = Path(temporary)
        for name, pages in (("one-page", False), ("two-page", True)):
            (private / name).mkdir()
            source = production_pdf(private / name, two_pages=pages)
            destination = root / f"{name}.pdf"
            shutil.copy2(source, destination)
            report = run_pdf_qa(
                destination,
                expected(name),
                report_path=root / f"{name}.json",
                raster_dir=root / f"{name}-raster",
            )
            print(f"{name}: {report.overall_status}; {root / f'{name}.json'}")


if __name__ == "__main__":
    main()
