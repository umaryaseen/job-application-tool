"""Reviewed corrections of draft requirement rows (TASK-014).

A correction is an explicit, actor- and time-stamped patch bound to one exact
JD revision (record and raw-text digests), the deterministic classification of
that text and the review state it was prepared against. Stored review
revisions are immutable; the reviewed view is always rebuilt by replaying them
over the deterministic draft. Nothing here is a career fact or a match.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .common import Sha256, StableId, StrictModel
from .requirement import (
    CandidateKind,
    ClassificationRole,
    Condition,
    DuplicateGroup,
    Negation,
    Priority,
    ReviewReason,
    SourceSpan,
    Threshold,
)

MAX_OPERATIONS = 512
MAX_REVIEW_THRESHOLDS = 16
EditedField = Literal["priority", "condition", "thresholds", "role"]
# How a row may be used downstream. Only "hard_gate" may ever exclude an
# application automatically; every other state stays visible for a person.
GateStatus = Literal[
    "not_a_requirement",
    "unreviewed",
    "manual_check",
    "not_required",
    "unspecified_priority",
    "preferred",
    "hard_gate",
]


class AcceptRow(StrictModel):
    """Confirm a row as currently shown; every draft uncertainty must be named."""

    op: Literal["accept"]
    candidate_id: StableId
    acknowledged_reasons: list[ReviewReason] = Field(default_factory=list, max_length=14)


class ReopenRow(StrictModel):
    op: Literal["reopen"]
    candidate_id: StableId


class SetPriority(StrictModel):
    op: Literal["set_priority"]
    candidate_id: StableId
    priority: Priority


class SetCondition(StrictModel):
    """Replace the ALL/ANY structure; ``None`` leaves the row unstructured."""

    op: Literal["set_condition"]
    candidate_id: StableId
    condition: Condition | None


class SetThresholds(StrictModel):
    op: Literal["set_thresholds"]
    candidate_id: StableId
    thresholds: list[Threshold] = Field(max_length=MAX_REVIEW_THRESHOLDS)


class SetRole(StrictModel):
    op: Literal["set_role"]
    candidate_id: StableId
    role: Literal["requirement", "non_requirement"]


ReviewOperation = Annotated[
    AcceptRow | ReopenRow | SetPriority | SetCondition | SetThresholds | SetRole,
    Field(discriminator="op"),
]


class RequirementCorrection(StrictModel):
    """A reviewer's patch, prepared against an exact displayed review view."""

    schema_version: Literal["1.0"] = "1.0"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    job_record_digest: Sha256
    raw_sha256: Sha256
    base_review_revision: int = Field(strict=True, ge=0, le=999999)
    base_view_digest: Sha256
    operations: list[ReviewOperation] = Field(min_length=1, max_length=MAX_OPERATIONS)


class RequirementReviewRevision(StrictModel):
    """One immutable stored review revision in a hash-linked chain."""

    schema_version: Literal["1.0"] = "1.0"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    job_record_digest: Sha256
    raw_sha256: Sha256
    classification_digest: Sha256
    review_revision: int = Field(strict=True, ge=1, le=999999)
    base_revision_digest: Sha256 | None
    base_view_digest: Sha256
    reviewer_id: StableId
    reviewed_at: datetime
    operations: list[ReviewOperation] = Field(min_length=1, max_length=MAX_OPERATIONS)
    result_view_digest: Sha256
    revision_digest: Sha256

    @field_validator("reviewed_at")
    @classmethod
    def timestamp_is_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("reviewed_at must be a UTC timestamp")
        return value

    @model_validator(mode="after")
    def chain_start(self) -> RequirementReviewRevision:
        if (self.review_revision == 1) != (self.base_revision_digest is None):
            raise ValueError("only the first review revision has no base revision")
        return self


class RequirementReviewHead(StrictModel):
    """The acknowledged end of one review history.

    Revision files are immutable; this small record is replaced (atomically)
    after each publication, so a missing tail, a missing only revision or a
    re-signed last revision no longer matches it. Interior changes already
    break the hash chain.
    """

    schema_version: Literal["1.0"] = "1.0"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    review_revision: int = Field(strict=True, ge=0, le=999999)
    revision_digest: Sha256 | None
    head_digest: Sha256

    @model_validator(mode="after")
    def empty_head(self) -> RequirementReviewHead:
        if (self.review_revision == 0) != (self.revision_digest is None):
            raise ValueError("a head digest exists exactly when revisions exist")
        return self


class ReviewedRequirement(StrictModel):
    """A draft row with any reviewed corrections applied; quotes stay source-bound."""

    candidate_id: StableId
    kind: CandidateKind
    span: SourceSpan
    role: ClassificationRole
    priority: Priority
    condition: Condition | None = None
    thresholds: list[Threshold] = Field(default_factory=list, max_length=4096)
    negation: Negation
    negation_spans: list[SourceSpan] = Field(default_factory=list, max_length=4096)
    review_reasons: list[ReviewReason] = Field(default_factory=list, max_length=14)
    needs_review: bool
    edited_fields: list[EditedField] = Field(default_factory=list, max_length=4)
    review_state: Literal["draft", "reviewed"] = "draft"
    reviewed_by: StableId | None = None
    reviewed_in: int | None = Field(default=None, strict=True, ge=1, le=999999)
    gate: GateStatus

    @model_validator(mode="after")
    def consistent_review(self) -> ReviewedRequirement:
        reviewed = self.review_state == "reviewed"
        if reviewed != (self.reviewed_by is not None) or reviewed != (self.reviewed_in is not None):
            raise ValueError("reviewer and revision are recorded exactly for reviewed rows")
        if self.edited_fields != sorted(set(self.edited_fields)):
            raise ValueError("edited fields must be sorted and unique")
        if self.review_reasons != sorted(set(self.review_reasons)) or self.needs_review != bool(
            self.review_reasons
        ):
            raise ValueError("draft review reasons must be sorted, unique and match needs_review")
        if self.gate != gate_status(self):
            raise ValueError("gate status does not follow from the row")
        return self


def gate_status(row: ReviewedRequirement) -> GateStatus:
    """Derive downstream use; ambiguity or missing review never yields a hard gate."""

    if row.role != "requirement":
        return "not_a_requirement"
    if row.review_state != "reviewed":
        return "unreviewed"
    if row.negation == "requirement_negated":
        return "not_required"
    if row.negation != "none" or (row.condition is None and not row.thresholds):
        return "manual_check"
    if row.priority == "mandatory":
        return "hard_gate"
    if row.priority == "preferred":
        return "preferred"
    return "unspecified_priority"


class RequirementReviewView(StrictModel):
    """The replayed review state of one JD revision."""

    schema_version: Literal["1.0"] = "1.0"
    job_id: StableId
    job_revision: int = Field(strict=True, ge=1, le=999999)
    job_record_digest: Sha256
    raw_sha256: Sha256
    classification_digest: Sha256
    quote_source: Literal["job_description.raw.txt"] = "job_description.raw.txt"
    # Rule-observed repeats, shown for review; corrections never merge rows.
    duplicates: list[DuplicateGroup] = Field(default_factory=list, max_length=1024)
    review_revision: int = Field(strict=True, ge=0, le=999999)
    latest_revision_digest: Sha256 | None
    rows: list[ReviewedRequirement] = Field(default_factory=list, max_length=2048)
    view_digest: Sha256

    @model_validator(mode="after")
    def chain_head(self) -> RequirementReviewView:
        if (self.review_revision == 0) != (self.latest_revision_digest is None):
            raise ValueError("a review head digest exists exactly when revisions exist")
        return self
