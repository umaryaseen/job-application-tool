"""A supplied vacancy snapshot is draft source data, never career evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from .common import Sha256, ShortText, StableId, StrictModel


class JobMetadata(StrictModel):
    company: ShortText | None = None
    title: ShortText | None = None
    external_id: ShortText | None = None
    source_url: str | None = Field(default=None, min_length=1, max_length=2000)


class JobRevision(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    job_id: StableId
    revision: int = Field(strict=True, ge=1, le=999999)
    state: Literal["draft"] = "draft"
    captured_at: datetime
    locale: Literal["en", "de", "unknown"] = "unknown"
    metadata: JobMetadata
    normalization: Literal["nfc-lf-v1"] = "nfc-lf-v1"
    quote_source: Literal["job_description.raw.txt"] = "job_description.raw.txt"
    raw_sha256: Sha256
    normalized_sha256: Sha256
    raw_bytes: int = Field(strict=True, ge=1, le=200000)
    raw_codepoints: int = Field(strict=True, ge=1, le=200000)
    content_digest: Sha256
    record_digest: Sha256

    @field_validator("captured_at")
    @classmethod
    def timestamp_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at requires a timezone")
        return value
