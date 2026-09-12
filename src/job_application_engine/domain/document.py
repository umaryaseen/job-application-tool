"""Typed, renderer-independent baseline document plans."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .common import Locale, Sha256, StableId, StrictModel
from .fact import FactRef

SectionId = Literal["contact", "headline", "experience", "education", "skills", "languages"]
LineSource = Literal["fact", "variant"]

PlanText = Annotated[str, Field(min_length=1, max_length=4000)]


class DocumentLine(StrictModel):
    """A visible candidate line with an exact source and support binding."""

    text: PlanText
    source: LineSource
    fact_ref: FactRef | None = None
    variant_id: StableId | None = None
    variant_revision: int | None = Field(default=None, strict=True, ge=1)
    support_binding_refs: list[StableId] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def source_reference_is_exact(self) -> DocumentLine:
        if self.source == "fact" and self.fact_ref is None:
            raise ValueError("fact document lines require an exact fact reference")
        if self.source == "variant" and (self.variant_id is None or self.variant_revision is None):
            raise ValueError("variant document lines require an exact variant reference")
        if self.source == "fact" and (
            self.variant_id is not None or self.variant_revision is not None
        ):
            raise ValueError("fact document lines cannot carry a variant reference")
        if self.source == "variant" and self.fact_ref is not None:
            raise ValueError("variant document lines cannot carry a fact reference")
        return self


class DocumentSection(StrictModel):
    section_id: SectionId
    label: Literal[
        "Contact",
        "Professional Summary",
        "Professional Experience",
        "Education",
        "Skills",
        "Languages",
    ]
    lines: list[DocumentLine] = Field(min_length=1, max_length=500)


class DocumentPlan(StrictModel):
    """An immutable identity-bound plan ready for a text or PDF adapter."""

    plan_version: Literal["1.0"]
    profile_id: StableId
    profile_revision: int = Field(strict=True, ge=1)
    profile_digest: Sha256
    as_of: date
    locale: Locale
    sections: list[DocumentSection] = Field(min_length=1, max_length=6)
    plan_sha256: Sha256
