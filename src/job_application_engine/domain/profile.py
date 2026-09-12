"""Versioned profile revision and duplicate-safe JSON loading."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator

from .common import Sha256, StableId, StrictModel
from .evidence import EvidenceRecord, SupportBinding
from .fact import Fact
from .variant import ApprovedVariant


class Entity(StrictModel):
    entity_id: StableId
    entity_type: str = Field(min_length=1, max_length=40, pattern=r"^[a-z][a-z0-9_]*$")
    display_name: str = Field(min_length=1, max_length=300)


class ProfileRevision(StrictModel):
    schema_version: str = Field(pattern=r"^1\.0$")
    profile_id: StableId
    revision: int = Field(strict=True, ge=1)
    created_at: datetime
    content_sha256: Sha256
    entities: list[Entity] = Field(default_factory=list, max_length=500)
    facts: list[Fact] = Field(default_factory=list, max_length=1000)
    evidence: list[EvidenceRecord] = Field(default_factory=list, max_length=1000)
    support_bindings: list[SupportBinding] = Field(default_factory=list, max_length=1000)
    variants: list[ApprovedVariant] = Field(default_factory=list, max_length=1000)

    @field_validator("created_at")
    @classmethod
    def created_at_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        return value

    @model_validator(mode="after")
    def ids_unique_within_collections(self) -> ProfileRevision:
        collections = {
            "entities": [item.entity_id for item in self.entities],
            "facts": [item.fact_id for item in self.facts],
            "evidence": [item.evidence_id for item in self.evidence],
            "support_bindings": [item.binding_id for item in self.support_bindings],
            "variants": [item.variant_id for item in self.variants],
        }
        for collection, ids in collections.items():
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate IDs in {collection}")
        return self


class DuplicateJsonKeyError(ValueError):
    """Raised before validation when JSON contains an ambiguous duplicate key."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_profile_json(path: str | Path) -> ProfileRevision:
    """Load a profile after duplicate-key detection and strict Pydantic validation."""

    raw = Path(path).read_text(encoding="utf-8")
    json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    return ProfileRevision.model_validate_json(raw)
