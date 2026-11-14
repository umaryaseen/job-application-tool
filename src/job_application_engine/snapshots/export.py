"""Current-eligibility export for immutable approved snapshot bytes."""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TypeVar

from ..config import private_data_root
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..profile.validation import ProvenanceValidationError, validate_profile
from ..verification.document import validate_document_plan
from ..verification.support import EvidenceKey, verify_support_captures
from .manifest import digest_file, verify_manifest_files
from .review import _verify_ready, load_final_approval
from .store import SnapshotError, _snapshot_root, _validate_qa

T = TypeVar("T")


class ExportError(ValueError):
    """Raised when immutable approved bytes are no longer currently eligible."""


def _expiry_values(profile: ProfileRevision, plan: object) -> list[datetime | date]:
    # Eligibility is conservative: any time-limited authorization/credential
    # in the current trusted profile blocks after expiry. It never trusts the
    # plan's historical as-of date to move the clock backwards.
    values: list[datetime | date] = []
    for fact in profile.facts:
        value = getattr(fact, "value", None)
        if value is not None:
            expiry = getattr(value, "expires_at", None)
            valid_through = getattr(value, "valid_through", None)
            if expiry is not None:
                values.append(expiry)
            if valid_through is not None and getattr(valid_through, "year", None) is not None:
                values.append(
                    date(valid_through.year, valid_through.month or 1, valid_through.day or 1)
                )
    return values


def _check_expiry(profile: ProfileRevision, plan: object, now: datetime) -> None:
    for expiry in _expiry_values(profile, plan):
        if isinstance(expiry, datetime):
            if expiry <= now:
                raise ExportError("a required authorization or credential has expired")
        elif expiry < now.astimezone(UTC).date():
            raise ExportError("a required authorization or credential is past valid-through")


def _check_current(
    snapshot: Path,
    profile: ProfileRevision,
    reviews: Sequence[LocalReviewReceipt],
    captures: Mapping[EvidenceKey, bytes | bytearray | Path],
    now: datetime,
) -> None:
    import json

    from ..domain.document import DocumentPlan

    manifest, manifest_sha = _verify_ready(snapshot)
    if manifest.profile_id != profile.profile_id or manifest.profile_revision != profile.revision:
        raise ExportError("current profile revision differs from snapshot")
    approval = load_final_approval(snapshot)
    if approval.snapshot_id != manifest.snapshot_id or approval.manifest_sha256 != manifest_sha:
        raise ExportError("final approval does not match this manifest")
    if approval.pdf_sha256 != digest_file(snapshot / "pdf/output.pdf"):
        raise ExportError("final approval does not match the stored PDF")
    if approval.text_sha256 != digest_file(snapshot / "text/output.txt"):
        raise ExportError("final approval does not match the stored text")
    try:
        plan = DocumentPlan.model_validate_json((snapshot / "plan.json").read_bytes())
        report_data = json.loads((snapshot / "qa/report.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ExportError("snapshot plan or QA evidence is unreadable") from error
    try:
        _validate_qa(
            (snapshot / "pdf/output.pdf").read_bytes(),
            (snapshot / "qa/report.json").read_bytes(),
            profile,
        )
    except (OSError, SnapshotError) as error:
        raise ExportError(str(error)) from error
    if report_data.get("overall_status") != "pass":
        raise ExportError("mandatory QA or visual review is not passing")
    try:
        validate_profile(profile, support_captures=captures, reviews=reviews)
        validate_document_plan(plan, profile, reviews=reviews, support_captures=captures)
        verify_support_captures(profile.evidence, captures)
    except (ProvenanceValidationError, ValueError) as error:
        raise ExportError(f"current profile/support eligibility failed: {error}") from error
    from ..verification.document import document_plan_digest, profile_digest

    if manifest.profile_digest != profile_digest(profile):
        raise ExportError("current profile content differs from snapshot")
    if manifest.plan_digest != document_plan_digest(plan):
        raise ExportError("stored plan content differs from snapshot")
    _check_expiry(profile, plan, now.astimezone(UTC))


def export_snapshot(
    snapshot_id: str,
    *,
    destination: Path,
    profile: ProfileRevision,
    reviews: Sequence[LocalReviewReceipt],
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path],
    now: datetime,
    root: Path | None = None,
    profile_loader: Callable[[], ProfileRevision] | None = None,
) -> Path:
    """Revalidate current trust state, then atomically copy exact approved bytes."""

    if now.tzinfo is None or now.utcoffset() is None:
        raise ExportError("export clock must include a timezone")
    snapshots = _snapshot_root(root or private_data_root())
    snapshot = snapshots / snapshot_id
    try:
        _check_current(snapshot, profile, reviews, support_captures, now)
    except SnapshotError as error:
        raise ExportError(str(error)) from error
    current = profile_loader() if profile_loader is not None else profile
    if current is not profile and current.model_dump(mode="json") != profile.model_dump(
        mode="json"
    ):
        raise ExportError("concurrent profile revision changed during export")
    if destination.exists():
        raise ExportError("export destination exists; overwrite is forbidden")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".jae-export-{snapshot_id}-", dir=destination.parent))
    try:
        shutil.copyfile(snapshot / "pdf/output.pdf", stage / "output.pdf")
        shutil.copyfile(snapshot / "text/output.txt", stage / "output.txt")
        manifest, _ = _verify_ready(snapshot)
        verify_manifest_files(snapshot, manifest)
        expected = {item.path: item.sha256 for item in manifest.files}
        if digest_file(stage / "output.pdf") != expected["pdf/output.pdf"]:
            raise ExportError("PDF changed during export")
        if digest_file(stage / "output.txt") != expected["text/output.txt"]:
            raise ExportError("text changed during export")
        # Recheck the bytes and profile immediately before publication.
        if profile_loader is not None:
            latest = profile_loader()
            if latest.model_dump(mode="json") != profile.model_dump(mode="json"):
                raise ExportError("concurrent profile revision changed during export")
        os.replace(stage, destination)
    except ExportError:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    except SnapshotError as error:
        shutil.rmtree(stage, ignore_errors=True)
        raise ExportError(str(error)) from error
    except (OSError, ValueError) as error:
        shutil.rmtree(stage, ignore_errors=True)
        raise ExportError("export publication failed") from error
    return destination
