"""Bounded UTF-8 intake with exact source bytes and immutable private revisions."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO, Literal

from pydantic import TypeAdapter

from ..config import private_data_root, safe_private_path
from ..domain.common import StableId
from ..domain.job import JobMetadata, JobRevision
from ..verification.support import canonical_json, model_digest, sha256_text

MAX_INPUT_BYTES = 200_000
Locale = Literal["en", "de", "unknown"]
FILES = {"job.json", "job_description.raw.txt", "job_description.md"}


class JobIntakeError(ValueError):
    """Sanitized input, integrity or concurrent-write failure."""


@dataclass(frozen=True)
class IntakeResult:
    record: JobRevision
    path: Path
    duplicate: bool


def read_source(stream: BinaryIO) -> bytes:
    data = stream.read(MAX_INPUT_BYTES + 1)
    decode_source(data)
    return data


def decode_source(data: bytes) -> str:
    if len(data) > MAX_INPUT_BYTES:
        raise JobIntakeError("job text exceeds 200000 bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise JobIntakeError("job text must be valid UTF-8") from error
    if not text.lstrip("\ufeff").strip():
        raise JobIntakeError("job text must not be empty")
    return text


def normalize_source(text: str) -> str:
    # Only the separate Markdown view changes. Quotes/offsets use the raw file.
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


def _id(value: str) -> str:
    try:
        return TypeAdapter(StableId).validate_python(value)
    except ValueError as error:
        raise JobIntakeError("job ID must be a bounded lowercase local identifier") from error


def _fingerprint(raw: str, normalized: str, metadata: JobMetadata, locale: Locale) -> str:
    return sha256_text(
        canonical_json(
            {
                "raw_sha256": raw,
                "normalized_sha256": normalized,
                "metadata": metadata.model_dump(mode="json"),
                "locale": locale,
                "normalization": "nfc-lf-v1",
            }
        )
    )


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise JobIntakeError("job revision contains duplicate JSON keys")
        result[key] = value
    return result


def _bounded_file(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise JobIntakeError("stored job artifact exceeds its size limit")
    return data


def _read_revision(root: Path, folder: Path, job_id: str, revision: int) -> JobRevision:
    if {p.name for p in folder.iterdir()} != FILES:
        raise JobIntakeError("job revision has missing or unexpected files")
    paths = {name: safe_private_path((folder / name).relative_to(root), root) for name in FILES}
    try:
        manifest = _bounded_file(paths["job.json"], 32_000)
        json.loads(manifest, object_pairs_hook=_unique_keys)
        record = JobRevision.model_validate_json(manifest)
        raw = _bounded_file(paths["job_description.raw.txt"], MAX_INPUT_BYTES)
        normalized = _bounded_file(paths["job_description.md"], MAX_INPUT_BYTES * 4)
        source = decode_source(raw)
    except (OSError, UnicodeError, ValueError) as error:
        raise JobIntakeError("stored job revision is invalid or unavailable") from error
    if record.job_id != job_id or record.revision != revision:
        raise JobIntakeError("job revision identity mismatch")
    if model_digest(record, exclude={"record_digest"}) != record.record_digest:
        raise JobIntakeError("job revision record checksum mismatch")
    if (
        hashlib.sha256(raw).hexdigest() != record.raw_sha256
        or hashlib.sha256(normalized).hexdigest() != record.normalized_sha256
        or len(raw) != record.raw_bytes
        or len(source) != record.raw_codepoints
        or normalize_source(source).encode("utf-8") != normalized
        or _fingerprint(record.raw_sha256, record.normalized_sha256, record.metadata, record.locale)
        != record.content_digest
    ):
        raise JobIntakeError("job revision source checksum mismatch")
    return record


def _latest_folder(root: Path, job_id: str) -> tuple[Path, int] | None:
    directory = safe_private_path(Path("jobs") / job_id / "revisions", root)
    if not directory.exists():
        return None
    candidates = [p for p in directory.iterdir() if re.fullmatch(r"r[0-9]{6}", p.name)]
    if not candidates:
        return None
    latest = max(candidates, key=lambda p: p.name)
    safe = safe_private_path(latest.relative_to(root), root)
    if not safe.is_dir():
        raise JobIntakeError("job revision is not a directory")
    return safe, int(latest.name[1:])


def load_job_revision(
    job_id: str, *, revision: int | None = None, data_root: str | Path | None = None
) -> IntakeResult:
    root = private_data_root(data_root)
    job_id = _id(job_id)
    if revision is None:
        found = _latest_folder(root, job_id)
        if found is None:
            raise JobIntakeError("job has no saved revision")
        folder, revision = found
    else:
        if isinstance(revision, bool) or not 1 <= revision <= 999999:
            raise JobIntakeError("revision must be between 1 and 999999")
        folder = safe_private_path(Path("jobs") / job_id / "revisions" / f"r{revision:06d}", root)
    try:
        record = _read_revision(root, folder, job_id, revision)
    except OSError as error:
        raise JobIntakeError("job revision is unavailable") from error
    return IntakeResult(record, folder, False)


def _write_private(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def ingest_job(
    data: bytes,
    *,
    job_id: str | None = None,
    metadata: JobMetadata | None = None,
    locale: Locale | None = None,
    data_root: str | Path | None = None,
) -> IntakeResult:
    source = decode_source(data)
    normalized = normalize_source(source).encode("utf-8")
    raw_hash = hashlib.sha256(data).hexdigest()
    normalized_hash = hashlib.sha256(normalized).hexdigest()
    job_id = _id(job_id if job_id is not None else "job-" + raw_hash[:24])
    root = private_data_root(data_root)
    found = _latest_folder(root, job_id)
    previous = _read_revision(root, found[0], job_id, found[1]) if found else None
    # Omitted source metadata is retained for later revisions of the same job.
    values = previous.metadata.model_dump() if previous else {}
    if metadata is not None:
        values.update(metadata.model_dump(exclude_unset=True))
    merged = JobMetadata.model_validate(values)
    chosen_locale: Locale = (
        locale if locale is not None else (previous.locale if previous else "unknown")
    )
    fingerprint = _fingerprint(raw_hash, normalized_hash, merged, chosen_locale)
    if previous and previous.content_digest == fingerprint:
        assert found is not None
        return IntakeResult(previous, found[0], True)
    revision = previous.revision + 1 if previous else 1
    record = JobRevision(
        job_id=job_id,
        revision=revision,
        captured_at=datetime.now(UTC),
        locale=chosen_locale,
        metadata=merged,
        raw_sha256=raw_hash,
        normalized_sha256=normalized_hash,
        raw_bytes=len(data),
        raw_codepoints=len(source),
        content_digest=fingerprint,
        record_digest="0" * 64,
    )
    record = record.model_copy(
        update={"record_digest": model_digest(record, exclude={"record_digest"})}
    )
    directory = safe_private_path(Path("jobs") / job_id / "revisions", root)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination = safe_private_path(directory.relative_to(root) / f"r{revision:06d}", root)
    if destination.exists():
        raise JobIntakeError("job was updated concurrently; retry intake")
    with tempfile.TemporaryDirectory(prefix=".intake-", dir=directory) as temporary:
        stage = Path(temporary)
        _write_private(stage / "job_description.raw.txt", data)
        _write_private(stage / "job_description.md", normalized)
        _write_private(stage / "job.json", (canonical_json(record) + "\n").encode("utf-8"))
        _read_revision(root, stage, job_id, revision)
        if destination.exists():
            raise JobIntakeError("job was updated concurrently; retry intake")
        try:
            stage.rename(destination)
        except OSError as error:
            raise JobIntakeError("job revision publication failed; retry intake") from error
    return IntakeResult(record, destination, False)
