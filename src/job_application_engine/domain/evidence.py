"""Evidence, support-binding, and approval records used by profile facts."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .common import GitObject, Sha256, ShortText, StableId, StrictModel


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must include a timezone")
    return value


class EvidenceRef(StrictModel):
    evidence_id: StableId
    revision: int = Field(strict=True, ge=1)


class UserAttestationSource(StrictModel):
    kind: Literal["user_attestation"]
    attestation_id: StableId


class DocumentSource(StrictModel):
    kind: Literal["document_reference"]
    document_sha256: Sha256 | None = None
    locator: ShortText | None = None


class RepositorySource(StrictModel):
    kind: Literal["repository_reference"]
    repository: ShortText
    revision: GitObject | None = None
    path: ShortText


class ImportSource(StrictModel):
    kind: Literal["import_reference"]
    import_id: StableId
    source_sha256: Sha256 | None = None
    source_role: Literal["external_source", "generated_output"] = "external_source"


SourceIdentity = Annotated[
    UserAttestationSource | DocumentSource | RepositorySource | ImportSource,
    Field(discriminator="kind"),
]
EvidenceKind = Literal[
    "user_attestation", "document_reference", "repository_reference", "import_reference"
]


class EvidenceApproval(StrictModel):
    evidence_sha256: Sha256
    approved_at: datetime
    reviewer_id: StableId

    @field_validator("approved_at")
    @classmethod
    def approved_at_is_aware(cls, value: datetime) -> datetime:
        return _aware(value)


class EvidenceRecord(StrictModel):
    evidence_id: StableId
    revision: int = Field(strict=True, ge=1)
    kind: EvidenceKind
    source: SourceIdentity
    support_capture_sha256: Sha256
    captured_at: datetime
    sensitivity: Literal["normal", "sensitive"] = "normal"
    status: Literal["draft", "approved", "revoked"] = "draft"
    approval: EvidenceApproval | None = None

    @field_validator("captured_at")
    @classmethod
    def captured_at_is_aware(cls, value: datetime) -> datetime:
        return _aware(value)

    @model_validator(mode="after")
    def source_kind_matches(self) -> EvidenceRecord:
        if self.kind != self.source.kind:
            raise ValueError("evidence kind must match its source identity kind")
        if self.status == "approved" and self.approval is None:
            raise ValueError("approved evidence requires a hash-bound approval")
        if self.status == "approved":
            if isinstance(self.source, DocumentSource) and self.source.document_sha256 is None:
                raise ValueError("approved documentary evidence requires a source-file hash")
            if isinstance(self.source, RepositorySource) and self.source.revision is None:
                raise ValueError("approved repository evidence requires a pinned revision")
            if isinstance(self.source, ImportSource) and self.source.source_sha256 is None:
                raise ValueError("approved imported evidence requires a source hash")
            if (
                isinstance(self.source, ImportSource)
                and self.source.source_role == "generated_output"
            ):
                raise ValueError("generated output cannot be source evidence")
        return self


class SupportBinding(StrictModel):
    binding_id: StableId
    fact_id: StableId
    fact_revision: int = Field(strict=True, ge=1)
    evidence_id: StableId
    evidence_revision: int = Field(strict=True, ge=1)
    fact_sha256: Sha256
    evidence_sha256: Sha256
    reviewed_scope: ShortText
    depends_on_binding_refs: list[StableId] = Field(default_factory=list, max_length=32)
    reviewed_at: datetime
    reviewer_id: StableId

    @field_validator("reviewed_at")
    @classmethod
    def reviewed_at_is_aware(cls, value: datetime) -> datetime:
        return _aware(value)


class FactApproval(StrictModel):
    fact_sha256: Sha256
    evidence_bundle_sha256: Sha256
    approved_at: datetime
    reviewer_id: StableId

    @field_validator("approved_at")
    @classmethod
    def approved_at_is_aware(cls, value: datetime) -> datetime:
        return _aware(value)


class VariantApproval(StrictModel):
    variant_sha256: Sha256
    evidence_bundle_sha256: Sha256
    approved_at: datetime
    reviewer_id: StableId

    @field_validator("approved_at")
    @classmethod
    def approved_at_is_aware(cls, value: datetime) -> datetime:
        return _aware(value)
