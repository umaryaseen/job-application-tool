"""Draft source annotations; none are reviewed requirements or career facts."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .common import Sha256, StableId, StrictModel

SectionKind = Literal["qualifications", "responsibilities", "benefits", "context", "unknown"]
SignalKind = Literal["technology", "education", "language", "years"]
CandidateKind = Literal[
    "technology", "education", "language", "experience", "responsibility", "context", "ambiguous"
]


class SourceSpan(StrictModel):
    start: int = Field(strict=True, ge=0, le=200_000)
    end: int = Field(strict=True, ge=1, le=200_000)
    quote: str = Field(min_length=1, max_length=200_000)

    @model_validator(mode="after")
    def length_matches(self) -> SourceSpan:
        if self.end <= self.start or self.end - self.start != len(self.quote):
            raise ValueError("source span length is inconsistent")
        return self


class SectionHeading(StrictModel):
    heading_id: StableId
    kind: SectionKind
    span: SourceSpan


class LexicalSignal(StrictModel):
    kind: SignalKind
    span: SourceSpan


class RequirementCandidate(StrictModel):
    candidate_id: StableId
    section_id: StableId | None = None
    kind: CandidateKind
    span: SourceSpan
    signals: list[LexicalSignal] = Field(default_factory=list, max_length=4096)
    priority: Literal["unspecified"] = "unspecified"
    review_state: Literal["draft"] = "draft"
    needs_review: Literal[True] = True


class RequirementExtraction(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    rules_version: Literal["source-candidates-v1"] = "source-candidates-v1"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    job_record_digest: Sha256
    raw_sha256: Sha256
    locale: Literal["en", "de", "unknown"]
    quote_source: Literal["job_description.raw.txt"] = "job_description.raw.txt"
    state: Literal["draft"] = "draft"
    sections: list[SectionHeading] = Field(default_factory=list, max_length=2048)
    candidates: list[RequirementCandidate] = Field(default_factory=list, max_length=2048)
    analysis_digest: Sha256
