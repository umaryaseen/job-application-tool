"""Command-line entry point for the project bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

from . import __version__
from .config import ConfigurationError, private_data_root
from .domain.document import DocumentPlan
from .domain.profile import ProfileRevision
from .profile.load import DuplicateJsonKeyError
from .profile.review import LocalReviewReceipt
from .rendering.pdf import PdfRenderError, build_pdf
from .snapshots.export import ExportError, export_snapshot
from .snapshots.review import approve_snapshot
from .snapshots.store import SnapshotBuild, SnapshotError, build_snapshot
from .verification.support import EvidenceKey


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jae",
        description="Local evidence-aware job application tooling.",
    )
    parser.add_argument("--version", action="version", version=f"jae {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    check = subparsers.add_parser("config-check", help="validate the configured private data root")
    check.set_defaults(handler=_config_check)
    build = subparsers.add_parser(
        "build-cv",
        help="build a baseline PDF from an explicitly reviewed plan and profile",
    )
    build.add_argument("--profile", required=True, type=Path, help="profile JSON")
    build.add_argument("--plan", required=True, type=Path, help="validated document plan JSON")
    build.add_argument(
        "--reviews", required=True, type=Path, help="local human review receipts JSON"
    )
    build.add_argument("--output-name", default="baseline.pdf", help="private output filename")
    build.set_defaults(handler=_build_cv)
    snapshot = subparsers.add_parser(
        "snapshot-build", help="atomically publish a private immutable snapshot"
    )
    for name in ("profile", "plan", "reviews", "pdf", "text", "qa", "source-slice"):
        snapshot.add_argument(f"--{name}", required=True, type=Path)
    snapshot.add_argument("--captures-dir", required=True, type=Path)
    snapshot.add_argument("--snapshot-id", required=True)
    snapshot.add_argument("--as-of", required=True, type=date.fromisoformat)
    snapshot.set_defaults(handler=_snapshot_build)
    final = subparsers.add_parser(
        "snapshot-approve", help="record explicit final artifact approval"
    )
    final.add_argument("--snapshot-id", required=True)
    final.add_argument("--reviewer-id", required=True)
    final.set_defaults(handler=_snapshot_approve)
    export = subparsers.add_parser(
        "snapshot-export", help="revalidate and export approved PDF/TXT bytes"
    )
    export.add_argument("--snapshot-id", required=True)
    export.add_argument("--destination", required=True, type=Path)
    export.add_argument("--profile", required=True, type=Path)
    export.add_argument("--reviews", required=True, type=Path)
    export.add_argument("--captures-dir", required=True, type=Path)
    export.set_defaults(handler=_snapshot_export)
    return parser


def _config_check(_: argparse.Namespace) -> int:
    try:
        print(private_data_root())
    except ConfigurationError as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    return 0


def _read_json_without_duplicate_keys(path: Path) -> tuple[str, object]:
    def reject(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateJsonKeyError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    raw = path.read_text(encoding="utf-8")
    return raw, json.loads(raw, object_pairs_hook=reject)


def _build_cv(args: argparse.Namespace) -> int:
    try:
        profile_raw, _ = _read_json_without_duplicate_keys(args.profile)
        plan_raw, _ = _read_json_without_duplicate_keys(args.plan)
        _, reviews_data = _read_json_without_duplicate_keys(args.reviews)
        profile = ProfileRevision.model_validate_json(profile_raw)
        plan = DocumentPlan.model_validate_json(plan_raw)
        if not isinstance(reviews_data, list):
            raise ValueError("review receipts JSON must be an array")
        reviews = [
            LocalReviewReceipt.model_validate_json(json.dumps(item, ensure_ascii=False))
            for item in reviews_data
        ]
        output = build_pdf(plan, profile, reviews=reviews, output_name=args.output_name)
    except (OSError, ValueError, TypeError, PdfRenderError) as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


def _private_input(path: Path) -> Path:
    from .config import private_data_root, safe_private_path

    return safe_private_path(path.as_posix(), root=private_data_root())


def _reviews(path: Path) -> list[LocalReviewReceipt]:
    _, data = _read_json_without_duplicate_keys(_private_input(path))
    if not isinstance(data, list):
        raise ValueError("review receipts JSON must be an array")
    # Validate the JSON representation so Pydantic can parse its ISO timestamps
    # while retaining the duplicate-key rejection above.
    return [
        LocalReviewReceipt.model_validate_json(json.dumps(item, ensure_ascii=False))
        for item in data
    ]


def _capture_map(directory: Path, profile: ProfileRevision) -> dict[EvidenceKey, Path]:
    base = _private_input(directory)
    result: dict[EvidenceKey, Path] = {}
    for evidence in profile.evidence:
        filename = f"{evidence.evidence_id}-r{evidence.revision}.bin"
        path = base / filename
        if not path.is_file():
            raise ValueError(f"missing capture: {filename}")
        result[(evidence.evidence_id, evidence.revision)] = path
    return result


def _snapshot_build(args: argparse.Namespace) -> int:
    try:
        profile = ProfileRevision.model_validate_json(_private_input(args.profile).read_bytes())
        plan = DocumentPlan.model_validate_json(_private_input(args.plan).read_bytes())
        reviews = _reviews(args.reviews)
        captures = _capture_map(args.captures_dir, profile)
        result = build_snapshot(
            SnapshotBuild(
                snapshot_id=args.snapshot_id,
                profile=profile,
                plan=plan,
                reviews=reviews,
                support_captures=captures,
                source_slice=_private_input(args.source_slice).read_bytes(),
                pdf=_private_input(args.pdf).read_bytes(),
                text=_private_input(args.text).read_bytes(),
                qa_report=_private_input(args.qa).read_bytes(),
                configuration={"locale": plan.locale, "template": "baseline-v1"},
                tool_versions={"python": sys.version.split()[0]},
                as_of=args.as_of,
            )
        )
    except (OSError, ValueError, SnapshotError) as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    print(f"snapshot {result.snapshot_id}: {result.path}")
    return 0


def _snapshot_approve(args: argparse.Namespace) -> int:
    try:
        result = approve_snapshot(
            args.snapshot_id,
            reviewer_id=args.reviewer_id,
            approved_at=datetime.now(UTC),
        )
    except (OSError, ValueError, SnapshotError) as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    print(f"final approval recorded for {result.snapshot_id}")
    return 0


def _snapshot_export(args: argparse.Namespace) -> int:
    try:
        profile = ProfileRevision.model_validate_json(_private_input(args.profile).read_bytes())
        result = export_snapshot(
            args.snapshot_id,
            destination=_private_input(args.destination),
            profile=profile,
            reviews=_reviews(args.reviews),
            support_captures=_capture_map(args.captures_dir, profile),
            now=datetime.now(UTC),
        )
    except (OSError, ValueError, ExportError) as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    print(f"exported approved bytes: {result}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    return 0 if handler is None else handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
