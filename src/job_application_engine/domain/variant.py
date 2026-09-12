"""Exact approved wording variants; graph resolution is deferred to TASK-003."""

from __future__ import annotations

from pydantic import Field, model_validator

from .common import Locale, LongText, RecordStatus, StableId, StrictModel
from .evidence import VariantApproval
from .fact import FactRef


class ApprovedVariant(StrictModel):
    variant_id: StableId
    revision: int = Field(strict=True, ge=1)
    locale: Locale
    text: LongText
    fact_refs: list[FactRef] = Field(min_length=1, max_length=64)
    support_binding_refs: list[StableId] = Field(min_length=1, max_length=64)
    subject_scope: StableId
    status: RecordStatus = "draft"
    approval: VariantApproval | None = None

    @model_validator(mode="after")
    def approved_requires_approval(self) -> ApprovedVariant:
        if self.status == "approved" and self.approval is None:
            raise ValueError("approved variants require a hash-bound approval")
        return self
