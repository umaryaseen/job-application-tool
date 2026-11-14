"""Draft TASK-012 classification bound to a verified TASK-011 extraction.

Rules are deterministic and source-bound. Output stays draft; review/correction
versions belong to TASK-014 and nothing here becomes an approved requirement.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

from pydantic import ValidationError

from ..domain.job import JobRevision
from ..domain.requirement import (
    MAX_CONDITION_DEPTH,
    ClassifiedCandidate,
    Condition,
    ConditionGroup,
    DuplicateGroup,
    Negation,
    PriorityCue,
    RequirementCandidate,
    RequirementClassification,
    RequirementExtraction,
    ReviewReason,
    SourceSpan,
)
from ..verification.support import model_digest
from .groups import analyze_structure
from .priority import (
    Cue,
    decide_priority,
    find_cues,
    heading_level,
    marker_level,
    stray_negations,
)
from .rules import extract_requirements, load_saved_source, validate_extraction
from .spans import ExtractionError, verify_span

MAX_ANNOTATIONS = 16_384
MAX_ROW_ANNOTATIONS = 4096
_NON_REQUIREMENT = {"responsibility", "context"}


class _Budget:
    """Fail the whole analysis (never truncate) when annotations exceed fixed limits."""

    def __init__(self) -> None:
        self.total = 0

    def spend(self, *groups: list[object]) -> None:
        if any(len(group) > MAX_ROW_ANNOTATIONS for group in groups):
            raise ExtractionError("a JD clause exceeds 4096 annotations; review the source")
        self.total += sum(len(group) for group in groups)
        if self.total > MAX_ANNOTATIONS:
            raise ExtractionError("JD classification exceeds 16384 annotations; review the source")


def _cue_models(cues: list[Cue], origin: str, origin_id: str) -> list[PriorityCue]:
    return [
        PriorityCue(level=c.level, origin=origin, origin_id=origin_id, span=c.span)  # type: ignore[arg-type]
        for c in cues
    ]


def _row(candidate: RequirementCandidate, **values: object) -> ClassifiedCandidate:
    reasons = sorted(set(values.pop("review_reasons", [])))  # type: ignore[call-overload]
    return ClassifiedCandidate(
        candidate_id=candidate.candidate_id,
        kind=candidate.kind,
        span=candidate.span,
        review_reasons=reasons,
        needs_review=bool(reasons),
        **values,  # type: ignore[arg-type]
    )


def _condition_key(node: Condition | None) -> object:
    if node is None:
        return None
    if isinstance(node, ConditionGroup):
        return (node.node, tuple(_condition_key(child) for child in node.children))
    return ("term", node.term_kind, " ".join(node.span.quote.split()).casefold())


def _equivalence_key(row: ClassifiedCandidate) -> object:
    thresholds = tuple(
        (
            t.measure,
            t.operator,
            t.value,
            t.upper,
            t.level,
            t.upper_level,
            t.unit,
            " ".join(t.scope.quote.split()).casefold() if t.scope else None,
        )
        for t in row.thresholds
    )
    return (
        " ".join(row.span.quote.split()).casefold(),
        row.kind,
        row.priority,
        row.basis,
        row.negation,
        _condition_key(row.condition),
        thresholds,
        tuple(row.review_reasons),
    )


def _duplicates(
    rows: list[ClassifiedCandidate], job: JobRevision, scopes: dict[str, object]
) -> list[DuplicateGroup]:
    """Group repeats only within the same heading and marker scope (README rule 11)."""
    groups: dict[object, list[str]] = defaultdict(list)
    for row in rows:
        if row.role == "requirement":
            key = (scopes[row.candidate_id], _equivalence_key(row))
            groups[key].append(row.candidate_id)
    result = []
    for members in groups.values():
        if len(members) > 1:
            digest = hashlib.sha256(f"{job.record_digest}:{':'.join(members)}".encode())
            result.append(
                DuplicateGroup(duplicate_id="dup-" + digest.hexdigest()[:24], candidate_ids=members)
            )
    order = {row.candidate_id: index for index, row in enumerate(rows)}
    return sorted(result, key=lambda group: order[group.candidate_ids[0]])


def _classify(
    extraction: RequirementExtraction, source: str, job: JobRevision
) -> RequirementClassification:
    headings = {
        heading.heading_id: _cue_models(
            find_cues(source, heading.span, heading=True), "heading", heading.heading_id
        )
        for heading in extraction.sections
    }
    rows: list[ClassifiedCandidate] = []
    marker: list[PriorityCue] = []
    scopes: dict[str, object] = {}
    budget = _Budget()
    section: str | None = None
    for candidate in extraction.candidates:
        if candidate.section_id != section:
            marker, section = [], candidate.section_id
        clause = find_cues(source, candidate.span)
        budget.spend(clause)  # type: ignore[arg-type]
        clause_models = _cue_models(clause, "clause", candidate.candidate_id)
        if candidate.kind in _NON_REQUIREMENT:
            rows.append(
                _row(
                    candidate,
                    role="non_requirement",
                    priority="unspecified",
                    basis="not_a_requirement_kind",
                    cues=clause_models,
                    negation="none",
                    review_reasons=["cue_outside_requirement_section"] if clause else [],
                )
            )
            continue
        level = (
            marker_level(candidate.span.quote)
            if candidate.kind == "ambiguous" and not candidate.signals
            else None
        )
        if level is not None:
            marker = [
                PriorityCue(
                    level=level,
                    origin="marker",
                    origin_id=candidate.candidate_id,
                    span=candidate.span,
                )
            ]
            rows.append(
                _row(
                    candidate,
                    role="priority_marker",
                    priority="unspecified",
                    basis="priority_marker",
                    cues=marker,
                    negation="none",
                )
            )
            continue
        scopes[candidate.candidate_id] = (
            candidate.section_id,
            marker[0].origin_id if marker else None,
        )
        inherited = marker or headings.get(candidate.section_id or "", [])
        heading, heading_conflict = heading_level([Cue(cue.level, cue.span) for cue in inherited])
        priority, basis, reasons = decide_priority(clause, heading)
        review: set[ReviewReason] = set(reasons)
        if heading_conflict:
            review.add("conflicting_heading_cues")
        stray = stray_negations(source, candidate.span, clause)
        budget.spend(stray)  # type: ignore[arg-type]
        negated = [cue.span for cue in clause if cue.level == "not_required"]
        negation: Negation = (
            "unsupported" if stray else ("requirement_negated" if negated else "none")
        )
        if stray:
            review.add("unsupported_negation")
        structure = analyze_structure(
            source,
            candidate.span,
            candidate.signals,
            [cue.span for cue in clause] + stray,
        )
        budget.spend(structure.thresholds)  # type: ignore[arg-type]
        review |= structure.reasons
        rows.append(
            _row(
                candidate,
                role="requirement",
                priority=priority,
                basis=basis,
                cues=sorted([*inherited, *clause_models], key=lambda c: (c.span.start, c.span.end))
                if heading is not None or heading_conflict
                else clause_models,
                negation=negation,
                negation_spans=sorted([*negated, *stray], key=lambda s: (s.start, s.end)),
                condition=structure.condition,
                thresholds=structure.thresholds,
                review_reasons=sorted(review),
            )
        )
    result = RequirementClassification(
        job_id=job.job_id,
        job_revision=job.revision,
        job_record_digest=job.record_digest,
        raw_sha256=job.raw_sha256,
        extraction_digest=extraction.analysis_digest,
        locale=job.locale,
        candidates=rows,
        duplicates=_duplicates(rows, job, scopes),
        classification_digest="0" * 64,
    )
    return result.model_copy(
        update={"classification_digest": model_digest(result, exclude={"classification_digest"})}
    )


def _condition_spans(node: Condition, depth: int = 1) -> list[SourceSpan]:
    if depth > MAX_CONDITION_DEPTH:
        raise ExtractionError("condition nesting exceeds the supported depth")
    if not isinstance(node, ConditionGroup):
        return [node.span]
    spans = [node.span, *node.connectives]
    previous = node.span.start
    for child in node.children:
        if child.span.start < previous or child.span.end > node.span.end:
            raise ExtractionError("condition members are outside their group or out of order")
        previous = child.span.end
        spans.extend(_condition_spans(child, depth + 1))
    return spans


def _validate_structure(
    classification: RequirementClassification,
    extraction: RequirementExtraction,
    source: str,
    job: JobRevision,
) -> None:
    validate_extraction(extraction, source, job)
    if (
        classification.job_id,
        classification.job_revision,
        classification.job_record_digest,
        classification.raw_sha256,
        classification.locale,
        classification.extraction_digest,
    ) != (
        job.job_id,
        job.revision,
        job.record_digest,
        job.raw_sha256,
        job.locale,
        extraction.analysis_digest,
    ) or model_digest(
        classification, exclude={"classification_digest"}
    ) != classification.classification_digest:
        raise ExtractionError("classification revision or checksum does not match")
    if [(r.candidate_id, r.kind, r.span) for r in classification.candidates] != [
        (c.candidate_id, c.kind, c.span) for c in extraction.candidates
    ]:
        raise ExtractionError("classification rows do not match the extraction candidates")
    headings = {h.heading_id: h.span for h in extraction.sections}
    candidates = {c.candidate_id: c for c in extraction.candidates}
    rows = {r.candidate_id: r for r in classification.candidates}
    for row in classification.candidates:
        candidate = candidates[row.candidate_id]
        own = [cue.span for cue in row.cues if cue.origin == "clause"]
        own += list(row.negation_spans)
        if row.condition is not None:
            own += _condition_spans(row.condition)
        for threshold in row.thresholds:
            own += [threshold.span, *([threshold.scope] if threshold.scope else [])]
        for span in own:
            verify_span(source, span)
            if span.start < row.span.start or span.end > row.span.end:
                raise ExtractionError("classification span is outside its source clause")
        for cue in row.cues:
            verify_span(source, cue.span)
            if cue.origin == "heading":
                bound = headings.get(cue.origin_id)
                valid = cue.origin_id == candidate.section_id and bound is not None
            elif cue.origin == "marker":
                origin = rows.get(cue.origin_id)
                valid = origin is not None and origin.role == "priority_marker"
                bound = origin.span if origin else None
                valid = valid and candidates[cue.origin_id].section_id == candidate.section_id
            else:
                bound, valid = row.span, cue.origin_id == row.candidate_id
            if (
                not valid
                or bound is None
                or cue.span.start < bound.start
                or cue.span.end > bound.end
            ):
                raise ExtractionError("priority cue origin or placement is invalid")
    seen: set[str] = set()
    for group in classification.duplicates:
        members = [rows.get(member) for member in group.candidate_ids]
        if (
            any(m is None or m.role != "requirement" for m in members)
            or seen & set(group.candidate_ids)
            or len(set(group.candidate_ids)) != len(group.candidate_ids)
        ):
            raise ExtractionError("duplicate group membership is invalid")
        seen |= set(group.candidate_ids)


def validate_classification(
    classification: RequirementClassification,
    extraction: RequirementExtraction,
    source: str,
    job: JobRevision,
) -> None:
    """Check structure and that every label equals the deterministic rule output."""
    try:
        checked = RequirementClassification.model_validate_json(classification.model_dump_json())
    except ValueError:
        raise ExtractionError("classification structure is invalid") from None
    _validate_structure(checked, extraction, source, job)
    try:
        expected = _classify(extraction, source, job)
    except ValidationError:
        raise ExtractionError("JD classification produced an invalid annotation") from None
    if expected != checked:
        raise ExtractionError("classification does not match the deterministic source rules")


def classify_requirements(
    extraction: RequirementExtraction, source: str, *, job: JobRevision
) -> RequirementClassification:
    validate_extraction(extraction, source, job)
    try:
        result = _classify(extraction, source, job)
    except ValidationError:
        # Defence in depth: rule gaps must never leak raw model details or JD text.
        raise ExtractionError("JD classification produced an invalid annotation") from None
    _validate_structure(result, extraction, source, job)
    return result


def classify_saved_job(
    job_id: str, *, revision: int | None = None, data_root: str | Path | None = None
) -> RequirementClassification:
    source, job = load_saved_source(job_id, revision=revision, data_root=data_root)
    return classify_requirements(extract_requirements(source, job=job), source, job=job)
