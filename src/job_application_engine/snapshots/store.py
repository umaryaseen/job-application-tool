"""Atomic private snapshot publication with no overwrite."""

from __future__ import annotations

import os
import secrets
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from ..config import ConfigurationError, private_data_root, safe_private_path
from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..profile.validation import ProvenanceValidationError, validate_profile
from ..verification.document import document_plan_digest, profile_digest, validate_document_plan
from ..verification.support import EvidenceKey, canonical_json, verify_support_captures
from .manifest import SnapshotManifest, canonical_manifest_bytes, file_record

OWNER_MARKER = ".jae-snapshot-owner-v1"
SNAPSHOT_ID_PATTERN = r"^[a-z0-9][a-z0-9._-]{0,99}$"


class SnapshotError(ValueError):
    """Raised when a snapshot cannot be safely built or read."""


@dataclass(frozen=True)
class SnapshotBuild:
    snapshot_id: str
    profile: ProfileRevision
    plan: DocumentPlan
    reviews: Sequence[LocalReviewReceipt]
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path]
    source_slice: bytes
    pdf: bytes
    text: bytes
    qa_report: bytes
    configuration: Mapping[str, str]
    tool_versions: Mapping[str, str]
    as_of: date


@dataclass(frozen=True)
class SnapshotResult:
    snapshot_id: str
    path: Path
    manifest_sha256: str


def _safe_id(value: str) -> None:
    import re

    if not re.fullmatch(SNAPSHOT_ID_PATTERN, value):
        raise SnapshotError("snapshot ID must be a bounded lowercase local identifier")


def _json_bytes(value: Any) -> bytes:
    return (canonical_json(value) + "\n").encode("utf-8")


def _read_capture(value: bytes | bytearray | Path) -> bytes:
    if isinstance(value, Path):
        try:
            return value.read_bytes()
        except OSError as error:
            raise SnapshotError("required support capture cannot be read") from error
    return bytes(value)


def _snapshot_root(root: Path) -> Path:
    try:
        base = private_data_root(root)
        snapshots = safe_private_path("snapshots", root=base)
    except ConfigurationError as error:
        raise SnapshotError(str(error)) from error
    snapshots.mkdir(mode=0o700, parents=True, exist_ok=True)
    return snapshots


def _write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _validate_qa(pdf: bytes, qa_report: bytes, profile: ProfileRevision) -> None:
    from ..ats_qa.report import QAReport

    try:
        report = QAReport.model_validate_json(qa_report)
    except ValueError as error:
        raise SnapshotError("QA report is not valid") from error
    import hashlib

    pdf_digest = hashlib.sha256(pdf).hexdigest()
    if report.artifact_sha256 != pdf_digest:
        raise SnapshotError("QA report is bound to another PDF")
    from ..verification.document import _required_identity
    from ..verification.support import fact_digest

    try:
        identity = _required_identity(profile)
    except ValueError as error:
        raise SnapshotError("trusted profile identity is invalid") from error
    if (
        report.profile_id != profile.profile_id
        or report.profile_revision != profile.revision
        or report.profile_digest != profile_digest(profile)
        or report.identity_fact_id != identity.fact_id
        or report.identity_revision != identity.revision
        or report.identity_digest != fact_digest(identity)
    ):
        raise SnapshotError("QA report is not bound to the trusted profile identity")
    if report.overall_status != "pass" or report.visual_review.status != "pass":
        raise SnapshotError("mandatory QA and attributed visual review must pass")
    if report.visual_review.artifact_sha256 != pdf_digest or not report.visual_review.reviewer_id:
        raise SnapshotError("visual review is not bound to the PDF and reviewer")
    if any(check.mandatory and check.status != "pass" for check in report.checks):
        raise SnapshotError("a mandatory QA check is absent or not passing")


def _validate_inputs(request: SnapshotBuild) -> dict[str, bytes]:
    _safe_id(request.snapshot_id)
    if not request.source_slice:
        raise SnapshotError("selected source slice is required")
    try:
        request.source_slice.decode("utf-8")
        request.text.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SnapshotError("source slice and text must be UTF-8") from error
    if not request.pdf or len(request.pdf) >= 2_000_000:
        raise SnapshotError("PDF is empty or exceeds the snapshot size limit")
    if not request.reviews:
        raise SnapshotError("local fact/variant review records are required")
    try:
        validate_profile(
            request.profile,
            support_captures=request.support_captures,
            reviews=request.reviews,
        )
        validate_document_plan(
            request.plan,
            request.profile,
            reviews=request.reviews,
            support_captures=request.support_captures,
        )
        verify_support_captures(request.profile.evidence, request.support_captures)
    except (ProvenanceValidationError, ValueError) as error:
        raise SnapshotError(f"current profile or plan is not eligible: {error}") from error
    _validate_qa(request.pdf, request.qa_report, request.profile)
    approval_bytes = _json_bytes([review.model_dump(mode="json") for review in request.reviews])
    captures: dict[str, bytes] = {}
    for key, value in request.support_captures.items():
        captures[f"captures/{key[0]}-r{key[1]}.bin"] = _read_capture(value)
    return {
        "profile.json": _json_bytes(request.profile),
        "plan.json": _json_bytes(request.plan),
        "reviews.json": approval_bytes,
        "source-slice.json": request.source_slice,
        "pdf/output.pdf": request.pdf,
        "text/output.txt": request.text,
        "qa/report.json": request.qa_report,
        "config.json": _json_bytes(dict(request.configuration)),
        "tools.json": _json_bytes(dict(request.tool_versions)),
        **captures,
    }


def build_snapshot(request: SnapshotBuild, *, root: Path | None = None) -> SnapshotResult:
    """Validate and atomically publish one immutable snapshot directory."""

    files = _validate_inputs(request)
    snapshots = _snapshot_root(root or private_data_root())
    final = snapshots / request.snapshot_id
    if final.exists():
        raise SnapshotError("snapshot ID already exists; overwrite is forbidden")
    stage = Path(tempfile.mkdtemp(prefix=f".staging-{request.snapshot_id}-", dir=snapshots))
    try:
        _write_private(stage / OWNER_MARKER, secrets.token_hex(16).encode("ascii"))
        for relative, data in files.items():
            _write_private(stage / relative, data)
        manifest = SnapshotManifest(
            manifest_version="1.0",
            snapshot_id=request.snapshot_id,
            profile_id=request.profile.profile_id,
            profile_revision=request.profile.revision,
            profile_digest=profile_digest(request.profile),
            plan_digest=document_plan_digest(request.plan),
            as_of=request.as_of.isoformat(),
            files=[file_record(relative, data) for relative, data in files.items()],
            tool_versions=dict(request.tool_versions),
            configuration=dict(request.configuration),
        )
        manifest_data = canonical_manifest_bytes(manifest)
        _write_private(stage / "manifest.json", manifest_data)
        directory_fd = os.open(stage, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        try:
            os.replace(stage, final)
        except FileExistsError as error:
            raise SnapshotError("snapshot ID already exists; overwrite is forbidden") from error
        return SnapshotResult(
            request.snapshot_id,
            final,
            __import__("hashlib").sha256(manifest_data).hexdigest(),
        )
    except SnapshotError:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    except (OSError, ValueError) as error:
        shutil.rmtree(stage, ignore_errors=True)
        raise SnapshotError("snapshot publication failed") from error


def clean_owned_staging(*, root: Path | None = None) -> list[Path]:
    """Remove only staging directories carrying this implementation's marker."""

    snapshots = _snapshot_root(root or private_data_root())
    removed: list[Path] = []
    for candidate in snapshots.glob(".staging-*"):
        marker = candidate / OWNER_MARKER
        if candidate.is_dir() and marker.is_file():
            shutil.rmtree(candidate)
            removed.append(candidate)
    return removed
