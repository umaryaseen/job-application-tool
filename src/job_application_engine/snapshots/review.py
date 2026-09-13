"""Explicit final artifact approval, stored outside the content manifest."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path

from pydantic import Field

from ..config import private_data_root
from ..domain.common import Sha256, StableId, StrictModel
from .manifest import SnapshotManifest, digest_file, manifest_digest, verify_manifest_files
from .store import OWNER_MARKER, SnapshotError, _snapshot_root


class FinalApproval(StrictModel):
    approval_version: str = Field(pattern=r"^1\.0$")
    snapshot_id: StableId
    manifest_sha256: Sha256
    pdf_sha256: Sha256
    text_sha256: Sha256
    reviewer_id: StableId
    approved_at: datetime


def _load_manifest(snapshot: Path) -> tuple[SnapshotManifest, str]:
    try:
        manifest_bytes = (snapshot / "manifest.json").read_bytes()
        manifest = SnapshotManifest.model_validate_json(manifest_bytes)
    except (OSError, ValueError) as error:
        raise SnapshotError("snapshot manifest is unreadable") from error
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    if digest != manifest_digest(manifest):
        raise SnapshotError("snapshot manifest canonical bytes are inconsistent")
    try:
        verify_manifest_files(snapshot, manifest)
    except ValueError as error:
        raise SnapshotError(str(error)) from error
    return manifest, digest


def _verify_ready(snapshot: Path) -> tuple[SnapshotManifest, str]:
    if not snapshot.is_dir() or not (snapshot / OWNER_MARKER).is_file():
        raise SnapshotError("snapshot is not a published private snapshot")
    manifest, digest = _load_manifest(snapshot)
    if not (snapshot / "pdf/output.pdf").is_file() or not (snapshot / "text/output.txt").is_file():
        raise SnapshotError("snapshot is incomplete")
    return manifest, digest


def approve_snapshot(
    snapshot_id: str,
    *,
    reviewer_id: str,
    approved_at: datetime,
    root: Path | None = None,
) -> FinalApproval:
    """Record an explicit final review after rechecking the immutable bytes."""

    if not reviewer_id or approved_at.tzinfo is None or approved_at.utcoffset() is None:
        raise SnapshotError("final approval requires a reviewer and aware timestamp")
    snapshots = _snapshot_root(root or private_data_root())
    snapshot = snapshots / snapshot_id
    manifest, manifest_sha = _verify_ready(snapshot)
    pdf_sha = digest_file(snapshot / "pdf/output.pdf")
    text_sha = digest_file(snapshot / "text/output.txt")
    approval = FinalApproval(
        approval_version="1.0",
        snapshot_id=manifest.snapshot_id,
        manifest_sha256=manifest_sha,
        pdf_sha256=pdf_sha,
        text_sha256=text_sha,
        reviewer_id=reviewer_id,
        approved_at=approved_at,
    )
    target = snapshot / "final-approval.json"
    try:
        with target.open("x", encoding="utf-8") as stream:
            stream.write(approval.model_dump_json(indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        target.chmod(0o600)
    except FileExistsError as error:
        raise SnapshotError("final approval already exists; overwrite is forbidden") from error
    except OSError as error:
        raise SnapshotError("final approval could not be recorded") from error
    return approval


def load_final_approval(snapshot: Path) -> FinalApproval:
    try:
        return FinalApproval.model_validate_json((snapshot / "final-approval.json").read_bytes())
    except (OSError, ValueError) as error:
        raise SnapshotError("final approval is missing or invalid") from error
