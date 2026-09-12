"""Command-line entry point for the project bootstrap."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import ConfigurationError, private_data_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jae",
        description="Local job application tooling (TASK-001 bootstrap).",
    )
    parser.add_argument("--version", action="version", version=f"jae {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    check = subparsers.add_parser("config-check", help="validate the configured private data root")
    check.set_defaults(handler=_config_check)
    return parser


def _config_check(_: argparse.Namespace) -> int:
    try:
        print(private_data_root())
    except ConfigurationError as error:
        print(f"jae: {error}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    return 0 if handler is None else handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
