"""Draft source annotations; none are reviewed requirements or career facts."""

from __future__ import annotations

from typing import Annotated, Literal

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


# TASK-012: deterministic draft classification of the TASK-011 candidates.
# Labels are rule outputs bound to literal source spans, not reviewed requirements.
Priority = Literal["mandatory", "preferred", "unspecified"]
CueLevel = Literal["mandatory", "preferred", "not_required"]
ClassificationRole = Literal["requirement", "priority_marker", "non_requirement"]
PriorityBasis = Literal[
    "explicit_mandatory_cue",
    "explicit_preferred_cue",
    "explicitly_not_required",
    "heading_mandatory_cue",
    "heading_preferred_cue",
    "conflicting_clause_cues",
    "clause_conflicts_with_heading",
    "no_priority_cue",
    "priority_marker",
    "not_a_requirement_kind",
]
Negation = Literal["none", "requirement_negated", "unsupported"]
ReviewReason = Literal[
    "conflicting_priority_cues",
    "heading_clause_conflict",
    "conflicting_heading_cues",
    "unsupported_negation",
    "unparsed_alternative",
    "unparsed_conjunction",
    "unsupported_grouping",
    "no_supported_condition",
    "vague_quantity",
    "unsupported_number",
    "threshold_scope_unclear",
    "multiple_thresholds",
    "cue_outside_requirement_section",
]
TermKind = Literal[
    "technology", "language", "education", "equivalent_experience", "equivalent_qualification"
]
CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
MAX_CONDITION_DEPTH = 3
MAX_CONDITION_TERMS = 128


class PriorityCue(StrictModel):
    level: CueLevel
    origin: Literal["clause", "heading", "marker"]
    origin_id: StableId
    span: SourceSpan


class ConditionTerm(StrictModel):
    node: Literal["term"] = "term"
    term_kind: TermKind
    span: SourceSpan


class ConditionGroup(StrictModel):
    node: Literal["all", "any"]
    span: SourceSpan
    connectives: list[SourceSpan] = Field(min_length=1, max_length=MAX_CONDITION_TERMS)
    children: list[Condition] = Field(min_length=2, max_length=MAX_CONDITION_TERMS)


Condition = Annotated[ConditionTerm | ConditionGroup, Field(discriminator="node")]
ConditionGroup.model_rebuild()


class Threshold(StrictModel):
    measure: Literal["duration", "language_level"]
    operator: Literal["gte", "gt", "range", "unqualified"]
    value: int | None = Field(default=None, strict=True, ge=0, le=99)
    upper: int | None = Field(default=None, strict=True, ge=1, le=99)
    level: CefrLevel | None = None
    upper_level: CefrLevel | None = None
    unit: Literal["years", "months", "cefr"]
    span: SourceSpan
    scope: SourceSpan | None = None

    @model_validator(mode="after")
    def consistent_measure(self) -> Threshold:
        ranged = self.operator == "range"
        if self.measure == "duration":
            valid = (
                self.unit in {"years", "months"}
                and self.value is not None
                and self.level is None
                and self.upper_level is None
                and (self.upper is not None) == ranged
                and (not ranged or (self.upper or 0) > self.value)
            )
        else:
            valid = (
                self.unit == "cefr"
                and self.level is not None
                and self.value is None
                and self.upper is None
                and self.operator != "gt"
                and (self.upper_level is not None) == ranged
                and (not ranged or (self.upper_level or "") > self.level)
            )
        if not valid:
            raise ValueError("threshold fields are inconsistent with its measure")
        return self


class ClassifiedCandidate(StrictModel):
    candidate_id: StableId
    kind: CandidateKind
    span: SourceSpan
    role: ClassificationRole
    priority: Priority
    basis: PriorityBasis
    cues: list[PriorityCue] = Field(default_factory=list, max_length=4096)
    negation: Negation
    negation_spans: list[SourceSpan] = Field(default_factory=list, max_length=4096)
    condition: Condition | None = None
    thresholds: list[Threshold] = Field(default_factory=list, max_length=4096)
    review_reasons: list[ReviewReason] = Field(default_factory=list, max_length=13)
    needs_review: bool
    review_state: Literal["draft"] = "draft"

    @model_validator(mode="after")
    def consistent_labels(self) -> ClassifiedCandidate:
        if self.review_reasons != sorted(set(self.review_reasons)) or self.needs_review != bool(
            self.review_reasons
        ):
            raise ValueError("review reasons must be sorted, unique and match needs_review")
        levels = {cue.level for cue in self.cues}
        expected = {
            "explicit_mandatory_cue": "mandatory",
            "heading_mandatory_cue": "mandatory",
            "explicit_preferred_cue": "preferred",
            "heading_preferred_cue": "preferred",
        }.get(self.basis, "unspecified")
        if self.priority != expected or (
            self.priority != "unspecified" and self.priority not in levels
        ):
            raise ValueError("priority is not supported by its basis and cues")
        role_basis = {
            "priority_marker": "priority_marker",
            "non_requirement": "not_a_requirement_kind",
        }
        if self.role != "requirement" and (
            self.condition is not None
            or self.thresholds
            or self.negation != "none"
            or self.basis != role_basis[self.role]
        ):
            raise ValueError("only requirement rows can carry conditions or negation")
        if self.role == "requirement" and self.basis in set(role_basis.values()):
            raise ValueError("requirement rows need a priority basis")
        return self


class DuplicateGroup(StrictModel):
    duplicate_id: StableId
    candidate_ids: list[StableId] = Field(min_length=2, max_length=2048)


class RequirementClassification(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    rules_version: Literal["priority-groups-v1"] = "priority-groups-v1"
    extraction_rules_version: Literal["source-candidates-v1"] = "source-candidates-v1"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    job_record_digest: Sha256
    raw_sha256: Sha256
    extraction_digest: Sha256
    locale: Literal["en", "de", "unknown"]
    quote_source: Literal["job_description.raw.txt"] = "job_description.raw.txt"
    state: Literal["draft"] = "draft"
    candidates: list[ClassifiedCandidate] = Field(default_factory=list, max_length=2048)
    duplicates: list[DuplicateGroup] = Field(default_factory=list, max_length=1024)
    classification_digest: Sha256
