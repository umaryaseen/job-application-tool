"""Command-line entry point for the project bootstrap."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import ConfigurationError, private_data_root
from .domain.document import DocumentPlan
from .domain.profile import ProfileRevision
from .profile.load import DuplicateJsonKeyError
from .profile.review import LocalReviewReceipt
from .rendering.pdf import PdfRenderError, build_pdf


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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    return 0 if handler is None else handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
