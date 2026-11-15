"""Apply explicit reviewed corrections to the deterministic draft (TASK-014).

Corrections never alter raw posting text: every corrected condition or
threshold span is re-verified against the exact raw JD and must lie inside its
row's clause. A row becomes reviewed only through an explicit ``accept`` that
names every draft uncertainty; any later edit returns it to draft. Ambiguous or
unreviewed rows therefore stay visible and can never become hard gates.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..domain.job import JobRevision
from ..domain.requirement import (
    MAX_CONDITION_TERMS,
    Condition,
    ConditionGroup,
    RequirementClassification,
    SourceSpan,
    Threshold,
)
from ..domain.requirement_review import (
    AcceptRow,
    EditedField,
    ReopenRow,
    RequirementReviewView,
    ReviewedRequirement,
    ReviewOperation,
    SetCondition,
    SetPriority,
    SetRole,
    SetThresholds,
    gate_status,
)
from ..verification.support import model_digest
from .classification import condition_spans
from .spans import ExtractionError, verify_span


class ReviewError(ExtractionError):
    """A sanitized invalid-correction or review-history failure."""


class StaleReviewError(ReviewError):
    """The correction or stored review belongs to other JD text or rules output."""


class ConcurrentReviewError(ReviewError):
    """The review state changed after the correction was prepared."""


def _rebuild(row: ReviewedRequirement, **changes: object) -> ReviewedRequirement:
    updated = row.model_copy(update=changes)
    updated = updated.model_copy(update={"gate": gate_status(updated)})
    # Re-validate the complete row, including nested condition and thresholds.
    return ReviewedRequirement.model_validate_json(updated.model_dump_json())


def draft_rows(classification: RequirementClassification) -> list[ReviewedRequirement]:
    """The unreviewed starting point: every draft label, nothing reviewed."""

    rows = []
    for candidate in classification.candidates:
        row = ReviewedRequirement.model_construct(
            candidate_id=candidate.candidate_id,
            kind=candidate.kind,
            span=candidate.span,
            role=candidate.role,
            priority=candidate.priority,
            condition=candidate.condition,
            thresholds=list(candidate.thresholds),
            negation=candidate.negation,
            negation_spans=list(candidate.negation_spans),
            review_reasons=list(candidate.review_reasons),
            needs_review=candidate.needs_review,
            edited_fields=[],
            review_state="draft",
            reviewed_by=None,
            reviewed_in=None,
            gate="unreviewed",
        )
        rows.append(_rebuild(row))
    return rows


def build_view(
    job: JobRevision,
    classification: RequirementClassification,
    rows: Sequence[ReviewedRequirement],
    *,
    review_revision: int,
    latest_revision_digest: str | None,
) -> RequirementReviewView:
    view = RequirementReviewView(
        job_id=job.job_id,
        job_revision=job.revision,
        job_record_digest=job.record_digest,
        raw_sha256=job.raw_sha256,
        classification_digest=classification.classification_digest,
        duplicates=list(classification.duplicates),
        review_revision=review_revision,
        latest_revision_digest=latest_revision_digest,
        rows=list(rows),
        view_digest="0" * 64,
    )
    # The head digest is excluded: a revision records the view it produces
    # before its own digest exists. The chain is linked by base digests.
    digest = model_digest(view, exclude={"view_digest", "latest_revision_digest"})
    return view.model_copy(update={"view_digest": digest})


def _within(source: str, outer: SourceSpan, spans: Sequence[SourceSpan]) -> None:
    for span in spans:
        try:
            verify_span(source, span)
        except ExtractionError:
            raise ReviewError("corrected quote or offsets do not match the raw JD") from None
        if span.start < outer.start or span.end > outer.end:
            raise ReviewError("corrected span is outside its requirement clause")


def _term_count(node: Condition) -> int:
    if isinstance(node, ConditionGroup):
        for connective in node.connectives:
            if connective.start < node.span.start or connective.end > node.span.end:
                raise ReviewError("corrected connective is outside its group")
        return sum(_term_count(child) for child in node.children)
    return 1


def _check_condition(source: str, row: ReviewedRequirement, condition: Condition) -> None:
    try:
        spans = condition_spans(condition)
    except ExtractionError:
        raise ReviewError("corrected condition is nested too deeply or out of order") from None
    if _term_count(condition) > MAX_CONDITION_TERMS:
        raise ReviewError("corrected condition has too many terms")
    _within(source, row.span, spans)


def _check_thresholds(source: str, row: ReviewedRequirement, thresholds: list[Threshold]) -> None:
    spans = [span for t in thresholds for span in (t.span, *([t.scope] if t.scope else []))]
    _within(source, row.span, spans)


def _edited(row: ReviewedRequirement, *fields: EditedField) -> list[EditedField]:
    return sorted({*row.edited_fields, *fields})


def apply_operations(
    rows: Sequence[ReviewedRequirement],
    operations: Sequence[ReviewOperation],
    source: str,
    *,
    reviewer_id: str,
    review_revision: int,
) -> list[ReviewedRequirement]:
    """Apply operations in order; any invalid operation rejects the whole patch."""

    result = list(rows)
    index = {row.candidate_id: position for position, row in enumerate(result)}
    draft = {"review_state": "draft", "reviewed_by": None, "reviewed_in": None}
    for operation in operations:
        position = index.get(operation.candidate_id)
        if position is None:
            raise ReviewError("correction names an unknown requirement row")
        row = result[position]
        if isinstance(operation, AcceptRow):
            if operation.acknowledged_reasons != row.review_reasons:
                raise ReviewError("accept must acknowledge exactly the row's review reasons")
            row = _rebuild(
                row,
                review_state="reviewed",
                reviewed_by=reviewer_id,
                reviewed_in=review_revision,
            )
        elif isinstance(operation, ReopenRow):
            row = _rebuild(row, **draft)
        elif row.role == "priority_marker":
            raise ReviewError("priority marker rows can only be accepted or reopened")
        elif isinstance(operation, SetRole):
            if operation.role == row.role:
                raise ReviewError("row already has this role")
            # A role change starts the row's labels over; nothing carries across.
            row = _rebuild(
                row,
                role=operation.role,
                priority="unspecified",
                condition=None,
                thresholds=[],
                edited_fields=_edited(row, "role"),
                **draft,
            )
        elif row.role != "requirement":
            raise ReviewError("only requirement rows carry priority, conditions or thresholds")
        elif isinstance(operation, SetPriority):
            row = _rebuild(
                row, priority=operation.priority, edited_fields=_edited(row, "priority"), **draft
            )
        elif isinstance(operation, SetCondition):
            if operation.condition is not None:
                _check_condition(source, row, operation.condition)
            row = _rebuild(
                row,
                condition=operation.condition,
                edited_fields=_edited(row, "condition"),
                **draft,
            )
        elif isinstance(operation, SetThresholds):
            _check_thresholds(source, row, operation.thresholds)
            row = _rebuild(
                row,
                thresholds=operation.thresholds,
                edited_fields=_edited(row, "thresholds"),
                **draft,
            )
        else:  # pragma: no cover - the discriminated union is exhaustive
            raise ReviewError("unsupported review operation")
        result[position] = row
    return result


def hard_gates(view: RequirementReviewView) -> list[ReviewedRequirement]:
    """Rows that may exclude an application: reviewed, structured, mandatory, unnegated."""

    return [row for row in view.rows if row.gate == "hard_gate"]
