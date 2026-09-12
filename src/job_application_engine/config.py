"""Safe configuration for private runtime data."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when private-data configuration is missing or unsafe."""


def _repository_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(result.stdout.strip()).resolve()


def private_data_root(value: str | os.PathLike[str] | None = None) -> Path:
    """Return an existing, non-symlink private root outside the repository."""

    raw = value if value is not None else os.environ.get("JAE_DATA_DIR")
    if not raw:
        raise ConfigurationError("JAE_DATA_DIR is required and must point outside the repository")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise ConfigurationError("JAE_DATA_DIR must be an absolute path")
    if path.is_symlink():
        raise ConfigurationError("JAE_DATA_DIR may not be a symlink")
    if not path.exists() or not path.is_dir():
        raise ConfigurationError("JAE_DATA_DIR must be an existing directory")
    resolved = path.resolve()
    repo = _repository_root()
    if repo is not None and (resolved == repo or repo in resolved.parents):
        raise ConfigurationError("JAE_DATA_DIR must be outside the repository")
    return resolved


def safe_private_path(relative: str | os.PathLike[str], root: Path | None = None) -> Path:
    """Resolve a relative path under the private root, rejecting escapes and symlinks."""

    base = private_data_root() if root is None else root.resolve()
    candidate = Path(relative)
    if candidate.is_absolute() or candidate == Path("."):
        raise ConfigurationError("private paths must be non-empty relative paths")
    destination = base.joinpath(candidate)
    current = base
    for part in candidate.parts:
        current /= part
        if current.is_symlink():
            raise ConfigurationError("private path may not traverse a symlink")
    resolved = destination.resolve(strict=False)
    if resolved != base and base not in resolved.parents:
        raise ConfigurationError("private path escapes JAE_DATA_DIR")
    return resolved
