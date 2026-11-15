"""Immutable private storage and replay of requirement review revisions (TASK-014).

Layout: ``jobs/<job_id>/requirement-reviews/r<job revision>/v<review revision>.json``.
Each file is written once (exclusive hard link from a private temporary file)
and never rewritten. Loading re-verifies the saved JD, recomputes the
deterministic classification and replays the whole hash-linked chain; any
gap, tampering, foreign file, other JD text or other rules output fails.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import secrets
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..config import private_data_root, safe_private_path
from ..domain.job import JobRevision
from ..domain.requirement import RequirementClassification
from ..domain.requirement_review import (
    RequirementCorrection,
    RequirementReviewHead,
    RequirementReviewRevision,
    RequirementReviewView,
)
from ..extraction.classification import classify_requirements
from ..extraction.review import (
    ConcurrentReviewError,
    ReviewError,
    StaleReviewError,
    apply_operations,
    build_view,
    draft_rows,
)
from ..extraction.rules import extract_requirements, load_saved_source
from ..ingestion.text import load_job_revision
from ..verification.support import canonical_json, model_digest

REVIEW_FOLDER = "requirement-reviews"
HEAD_NAME = "head.json"
MAX_REVISION_BYTES = 2_000_000
MAX_CORRECTION_BYTES = 2_000_000
_REVISION_NAME = re.compile(r"v([0-9]{6})\.json")
# An interrupted write can leave only such a private temporary file; it is
# never part of the chain because publication is the exclusive link.
_TEMPORARY_PREFIX = ".review-"


@dataclass(frozen=True)
class ReviewState:
    source: str
    job: JobRevision
    classification: RequirementClassification
    view: RequirementReviewView
    revisions: tuple[RequirementReviewRevision, ...]
    latest_job_revision: int


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewError("review JSON contains duplicate keys")
        result[key] = value
    return result


def _bounded_json(path: Path, limit: int) -> str:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ReviewError("review JSON exceeds its size limit")
    try:
        text = data.decode("utf-8")
        json.loads(text, object_pairs_hook=_unique_keys)
    except (UnicodeError, ValueError) as error:
        if isinstance(error, ReviewError):
            raise
        raise ReviewError("review JSON is not valid UTF-8 JSON") from None
    return text


def read_correction(path: Path, *, data_root: str | Path | None = None) -> RequirementCorrection:
    """Read a reviewer's correction file from inside the private data root."""

    root = private_data_root(data_root)
    target = safe_private_path(path.as_posix(), root=root)
    try:
        return RequirementCorrection.model_validate_json(
            _bounded_json(target, MAX_CORRECTION_BYTES)
        )
    except ValueError as error:
        if isinstance(error, ReviewError):
            raise
        raise ReviewError("requirement correction is invalid") from None


def _folder(root: Path, job_id: str, job_revision: int) -> Path:
    relative = Path("jobs") / job_id / REVIEW_FOLDER / f"r{job_revision:06d}"
    return safe_private_path(relative, root)


def _revision_files(root: Path, folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    if folder.is_symlink() or not folder.is_dir():
        raise ReviewError("requirement review history is not a directory")
    numbers = []
    for entry in folder.iterdir():
        if entry.name == HEAD_NAME:
            continue
        if entry.name.startswith(_TEMPORARY_PREFIX) and not entry.is_symlink():
            continue
        match = _REVISION_NAME.fullmatch(entry.name)
        if match is None or entry.is_symlink() or not entry.is_file():
            raise ReviewError("requirement review history contains an unexpected entry")
        numbers.append(int(match.group(1)))
    numbers.sort()
    if numbers != list(range(1, len(numbers) + 1)):
        raise ReviewError("requirement review history has a gap")
    return [
        safe_private_path((folder / f"v{number:06d}.json").relative_to(root), root)
        for number in numbers
    ]


def _parse_revision(path: Path) -> RequirementReviewRevision:
    try:
        return RequirementReviewRevision.model_validate_json(
            _bounded_json(path, MAX_REVISION_BYTES)
        )
    except ValueError as error:
        if isinstance(error, ReviewError):
            raise
        raise ReviewError("stored requirement review is invalid") from None


def replay(
    job: JobRevision,
    classification: RequirementClassification,
    source: str,
    revisions: list[RequirementReviewRevision],
) -> RequirementReviewView:
    """Rebuild the view from the deterministic draft and every stored revision."""

    view = build_view(
        job, classification, draft_rows(classification), review_revision=0,
        latest_revision_digest=None,
    )  # fmt: skip
    previous: RequirementReviewRevision | None = None
    for number, record in enumerate(revisions, 1):
        if model_digest(record, exclude={"revision_digest"}) != record.revision_digest:
            raise ReviewError("stored requirement review checksum mismatch")
        if (
            record.job_id,
            record.job_revision,
            record.job_record_digest,
            record.raw_sha256,
            record.classification_digest,
        ) != (
            job.job_id,
            job.revision,
            job.record_digest,
            job.raw_sha256,
            classification.classification_digest,
        ):
            raise StaleReviewError(
                "stored requirement review belongs to other JD text or classification rules"
            )
        if (
            record.review_revision != number
            or record.base_revision_digest
            != (previous.revision_digest if previous is not None else None)
            or record.base_view_digest != view.view_digest
        ):
            raise ReviewError("requirement review chain is broken")
        if previous is not None and record.reviewed_at < previous.reviewed_at:
            raise ReviewError("requirement review revisions are out of time order")
        rows = apply_operations(
            view.rows,
            record.operations,
            source,
            reviewer_id=record.reviewer_id,
            review_revision=number,
        )
        view = build_view(
            job, classification, rows, review_revision=number,
            latest_revision_digest=record.revision_digest,
        )  # fmt: skip
        if view.view_digest != record.result_view_digest:
            raise ReviewError("replayed requirement review does not reproduce its result")
        previous = record
    return view


def _head(job: JobRevision, latest: RequirementReviewRevision | None) -> RequirementReviewHead:
    head = RequirementReviewHead(
        job_id=job.job_id,
        job_revision=job.revision,
        review_revision=latest.review_revision if latest is not None else 0,
        latest=latest,
        head_digest="0" * 64,
    )
    return head.model_copy(update={"head_digest": model_digest(head, exclude={"head_digest"})})


def _read_head(root: Path, folder: Path, job: JobRevision) -> RequirementReviewHead:
    path = safe_private_path((folder / HEAD_NAME).relative_to(root), root)
    if path.is_symlink() or not path.is_file():
        raise ReviewError("requirement review head is missing")
    try:
        head = RequirementReviewHead.model_validate_json(
            _bounded_json(path, MAX_REVISION_BYTES + 4_000)
        )
    except ValueError as error:
        if isinstance(error, ReviewError):
            raise
        raise ReviewError("requirement review head is invalid") from None
    if model_digest(head, exclude={"head_digest"}) != head.head_digest or (
        head.job_id,
        head.job_revision,
    ) != (job.job_id, job.revision):
        raise ReviewError("requirement review head is invalid")
    return head


def _history(root: Path, job: JobRevision) -> list[RequirementReviewRevision]:
    """Stored revisions, reconciled with the head before replay.

    The head is written before each revision file and embeds that revision, so
    files may trail the head by exactly that one revision (a crash between the
    two writes, or a deleted newest file); it is then taken from the head. A
    newest file that differs from the head, files beyond the head, a larger
    shortfall or a missing head fail. A review folder is created together with
    its head. Removing the whole review folder cannot be detected and returns
    the unreviewed draft, which never yields a hard gate.
    """

    folder = _folder(root, job.job_id, job.revision)
    if not folder.exists():
        return []
    revisions = [_parse_revision(path) for path in _revision_files(root, folder)]
    head = _read_head(root, folder, job)
    count, committed = len(revisions), head.review_revision
    if count == committed:
        if committed and revisions[-1] != head.latest:
            raise ReviewError("requirement review history does not match its head")
        return revisions
    if count == committed - 1 and head.latest is not None:
        return [*revisions, head.latest]
    raise ReviewError("requirement review history does not match its head")


def load_review(
    job_id: str, *, revision: int | None = None, data_root: str | Path | None = None
) -> ReviewState:
    """Verified source, draft classification and replayed review of one JD revision."""

    root = private_data_root(data_root)
    source, job = load_saved_source(job_id, revision=revision, data_root=root)
    classification = classify_requirements(extract_requirements(source, job=job), source, job=job)
    revisions = _history(root, job)
    view = replay(job, classification, source, revisions)
    latest = load_job_revision(job.job_id, data_root=root).record.revision
    return ReviewState(source, job, classification, view, tuple(revisions), latest)


def _private_file(folder: Path, data: bytes) -> Path:
    temporary = folder / f"{_TEMPORARY_PREFIX}{secrets.token_hex(8)}"
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return temporary


def _head_bytes(head: RequirementReviewHead) -> bytes:
    return (canonical_json(head) + "\n").encode("utf-8")


def _create_folder(root: Path, job: JobRevision, folder: Path) -> None:
    """Create the review folder and its empty head in one atomic rename."""

    parent = safe_private_path(folder.parent.relative_to(root), root)
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=_TEMPORARY_PREFIX, dir=parent))
    try:
        os.replace(_private_file(stage, _head_bytes(_head(job, None))), stage / HEAD_NAME)
        os.rename(stage, folder)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def _commit_head(folder: Path, head: RequirementReviewHead) -> None:
    """Atomically replace the head; this is the commit point of a revision."""

    temporary = _private_file(folder, _head_bytes(head))
    try:
        os.replace(temporary, folder / HEAD_NAME)
    finally:
        temporary.unlink(missing_ok=True)


def _publish(folder: Path, number: int, record: RequirementReviewRevision) -> Path:
    """Write a committed revision's file once; an existing file is never replaced."""

    final = folder / f"v{number:06d}.json"
    temporary = _private_file(folder, (canonical_json(record) + "\n").encode("utf-8"))
    try:
        os.link(temporary, final)
    except FileExistsError:
        raise ReviewError("requirement review history is inconsistent") from None
    finally:
        temporary.unlink(missing_ok=True)
    return final


@contextmanager
def _writer_lock(root: Path, job_id: str, job_revision: int) -> Iterator[None]:
    """One writer per review history; the OS releases the lock if a writer dies."""

    parent = safe_private_path(Path("jobs") / job_id / REVIEW_FOLDER, root)
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = safe_private_path((parent / f"r{job_revision:06d}.lock").relative_to(root), root)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ConcurrentReviewError(
                "another requirement review is being stored; reload and retry"
            ) from None
        yield
    finally:
        os.close(descriptor)


def apply_correction(
    correction: RequirementCorrection,
    *,
    reviewer_id: str,
    reviewed_at: datetime,
    data_root: str | Path | None = None,
) -> tuple[RequirementReviewRevision, Path]:
    """Validate and store one explicit correction as the next immutable revision."""

    root = private_data_root(data_root)
    with _writer_lock(root, correction.job_id, correction.job_revision):
        return _apply_locked(root, correction, reviewer_id=reviewer_id, reviewed_at=reviewed_at)


def _apply_locked(
    root: Path,
    correction: RequirementCorrection,
    *,
    reviewer_id: str,
    reviewed_at: datetime,
) -> tuple[RequirementReviewRevision, Path]:
    state = load_review(correction.job_id, revision=correction.job_revision, data_root=root)
    if state.latest_job_revision != state.job.revision:
        raise StaleReviewError("the JD has a newer revision; review the latest revision")
    if (correction.job_record_digest, correction.raw_sha256) != (
        state.job.record_digest,
        state.job.raw_sha256,
    ):
        raise StaleReviewError("correction was prepared for a different JD text or record")
    view = state.view
    if (correction.base_review_revision, correction.base_view_digest) != (
        view.review_revision,
        view.view_digest,
    ):
        raise ConcurrentReviewError(
            "requirement review changed since this correction was prepared; reload and retry"
        )
    history = state.revisions
    number = view.review_revision + 1
    rows = apply_operations(
        view.rows,
        correction.operations,
        state.source,
        reviewer_id=reviewer_id,
        review_revision=number,
    )
    # The head digest is not part of the view digest; a placeholder stands in
    # until the revision record (which carries this result digest) is hashed.
    result = build_view(
        state.job,
        state.classification,
        rows,
        review_revision=number,
        latest_revision_digest="0" * 64,
    )  # fmt: skip
    try:
        record = RequirementReviewRevision(
            job_id=state.job.job_id,
            job_revision=state.job.revision,
            job_record_digest=state.job.record_digest,
            raw_sha256=state.job.raw_sha256,
            classification_digest=state.classification.classification_digest,
            review_revision=number,
            base_revision_digest=history[-1].revision_digest if history else None,
            base_view_digest=view.view_digest,
            reviewer_id=reviewer_id,
            reviewed_at=reviewed_at,
            operations=correction.operations,
            result_view_digest=result.view_digest,
            revision_digest="0" * 64,
        )
    except ValueError:
        raise ReviewError("reviewer identity or review time is invalid") from None
    if history and record.reviewed_at < history[-1].reviewed_at:
        raise ReviewError("review time precedes the previous review revision")
    record = record.model_copy(
        update={"revision_digest": model_digest(record, exclude={"revision_digest"})}
    )
    folder = _folder(root, state.job.job_id, state.job.revision)
    if not folder.exists():
        _create_folder(root, state.job, folder)
    if history and not (folder / f"v{len(history):06d}.json").exists():
        # A committed revision whose file was not written yet (crash) or was removed.
        _publish(folder, len(history), history[-1])
    _commit_head(folder, _head(state.job, record))
    path = _publish(folder, number, record)
    stored = load_review(state.job.job_id, revision=state.job.revision, data_root=root)
    if stored.view.view_digest != result.view_digest:
        raise ReviewError("stored requirement review does not reproduce its result")
    return record, path
