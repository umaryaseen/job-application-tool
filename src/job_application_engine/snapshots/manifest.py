"""Hash-only manifest for an immutable snapshot (approval stays separate)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from pydantic import Field

from ..domain.common import Sha256, StableId, StrictModel
from ..verification.support import canonical_json


class ManifestFile(StrictModel):
    path: str = Field(min_length=1, max_length=300, pattern=r"^[a-zA-Z0-9_./-]+$")
    sha256: Sha256
    size: int = Field(strict=True, ge=0)


class SnapshotManifest(StrictModel):
    manifest_version: str = Field(pattern=r"^1\.0$")
    snapshot_id: StableId
    profile_id: StableId
    profile_revision: int = Field(strict=True, ge=1)
    profile_digest: Sha256
    plan_digest: Sha256
    as_of: str = Field(min_length=1, max_length=50)
    files: list[ManifestFile] = Field(min_length=1, max_length=1000)
    tool_versions: dict[str, str] = Field(max_length=100)
    configuration: dict[str, str] = Field(max_length=100)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_manifest_bytes(manifest: SnapshotManifest) -> bytes:
    return (canonical_json(manifest) + "\n").encode("utf-8")


def manifest_digest(manifest: SnapshotManifest) -> str:
    return digest_bytes(canonical_manifest_bytes(manifest))


def file_record(path: str, data: bytes) -> ManifestFile:
    return ManifestFile(path=path, sha256=digest_bytes(data), size=len(data))


def verify_manifest_files(root: Path, manifest: SnapshotManifest) -> None:
    for item in manifest.files:
        path = root / item.path
        try:
            relative = path.resolve(strict=False).relative_to(root.resolve())
        except ValueError as error:
            raise ValueError(f"manifest path escapes snapshot: {item.path}") from error
        if str(relative) != item.path or not path.is_file():
            raise ValueError(f"manifest artifact is missing: {item.path}")
        if path.stat().st_size != item.size or digest_file(path) != item.sha256:
            raise ValueError(f"manifest hash mismatch: {item.path}")


def manifest_payload(manifest: SnapshotManifest) -> dict[str, Any]:
    return manifest.model_dump(mode="json")
