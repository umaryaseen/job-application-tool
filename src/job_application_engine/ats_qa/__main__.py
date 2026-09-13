"""Standalone TASK-007 measurement command; no approval/export workflow."""

import argparse
import sys
from pathlib import Path

from ..cli import _read_json_without_duplicate_keys
from ..config import private_data_root, safe_private_path
from .expected import ExpectedDocument
from .pdf import run_pdf_qa


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure a local PDF against curated QA expectations"
    )
    parser.add_argument("--pdf", required=True, help="PDF path relative to JAE_PRIVATE_DATA_ROOT")
    parser.add_argument("--expected", required=True, type=Path, help="independent expected JSON")
    parser.add_argument("--output", required=True, help="new QA directory relative to private root")
    args = parser.parse_args()
    try:
        root = private_data_root()
        pdf = safe_private_path(args.pdf, root=root)
        destination = safe_private_path(args.output, root=root)
        if destination.exists():
            raise ValueError("QA output directory must be new")
        if args.expected.stat().st_size > 2_000_000:
            raise ValueError("expected JSON exceeds 2 MB")
        raw, _ = _read_json_without_duplicate_keys(args.expected)
        expected = ExpectedDocument.model_validate_json(raw)
        report = run_pdf_qa(
            pdf,
            expected,
            report_path=destination / "report.json",
            raster_dir=destination / "rasters",
        )
    except (OSError, ValueError):
        print(
            "PDF QA could not run; verify local input, expectations and private output paths.",
            file=sys.stderr,
        )
        return 2
    print(f"PDF QA: {report.overall_status}; {destination / 'report.json'}")
    return 0 if report.overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
