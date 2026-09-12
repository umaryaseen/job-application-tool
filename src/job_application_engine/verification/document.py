"""Validation boundary for renderer-independent document plans."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..domain.document import DocumentLine, DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..profile.validation import ProvenanceValidationError, validate_profile
from .support import canonical_json, sha256_text


class DocumentValidationError(ValueError):
    """Raised when a plan is stale, altered, or contains an unauthorized claim."""


SECTION_ORDER = ("contact", "headline", "experience", "education", "skills", "languages")
SECTION_LABELS = {
    "contact": "Contact",
    "headline": "Professional Summary",
    "experience": "Professional Experience",
    "education": "Education",
    "skills": "Skills",
    "languages": "Languages",
}


def profile_digest(profile: ProfileRevision) -> str:
    payload = profile.model_dump(mode="json", exclude={"content_sha256"})
    return sha256_text(canonical_json(payload))


def document_plan_digest(plan: DocumentPlan) -> str:
    payload = plan.model_dump(mode="json", exclude={"plan_sha256"})
    return sha256_text(canonical_json(payload))


def _line_error(message: str) -> DocumentValidationError:
    return DocumentValidationError(message)


def _fact_index(profile: ProfileRevision) -> dict[tuple[str, int], Any]:
    return {(fact.fact_id, fact.revision): fact for fact in profile.facts}


def _variant_index(profile: ProfileRevision) -> dict[tuple[str, int], Any]:
    return {(variant.variant_id, variant.revision): variant for variant in profile.variants}


def validate_document_plan(
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
) -> None:
    """Reject altered plans and any line not authorized by current reviewed data."""

    if plan.profile_id != profile.profile_id or plan.profile_revision != profile.revision:
        raise _line_error("plan profile identity is stale")
    if plan.profile_digest != profile_digest(profile):
        raise _line_error("plan profile digest is stale")
    if plan.plan_sha256 != document_plan_digest(plan):
        raise _line_error("document plan content was altered")
    try:
        validate_profile(profile, reviews=reviews)
    except ProvenanceValidationError as error:
        raise _line_error(str(error)) from error

    fact_index = _fact_index(profile)
    variant_index = _variant_index(profile)
    previous = -1
    seen: set[str] = set()
    for section in plan.sections:
        if section.section_id in seen:
            raise _line_error(f"duplicate document section {section.section_id}")
        seen.add(section.section_id)
        position = SECTION_ORDER.index(section.section_id)
        if position <= previous:
            raise _line_error("document sections are out of standard order")
        previous = position
        if section.label != SECTION_LABELS[section.section_id]:
            raise _line_error("document section label is not allowlisted")
        for line in section.lines:
            _validate_line(line, section.section_id, profile, fact_index, variant_index)


def _validate_line(
    line: DocumentLine,
    section_id: str,
    profile: ProfileRevision,
    fact_index: dict[tuple[str, int], Any],
    variant_index: dict[tuple[str, int], Any],
) -> None:
    if line.source == "fact":
        assert line.fact_ref is not None
        fact = fact_index.get((line.fact_ref.fact_id, line.fact_ref.revision))
        if fact is None or fact.status != "approved":
            raise _line_error("document line references a missing or unapproved fact revision")
        if line.support_binding_refs != fact.support_binding_refs:
            raise _line_error("document line support bindings do not match the fact")
        from ..profile.baseline import fact_line_text

        if line.text != fact_line_text(profile, fact):
            raise _line_error("document fact wording is not the approved typed rendering")
        expected_section = {
            "contact": "contact",
            "employment": "experience",
            "education": "education",
            "skill": "skills",
            "language": "languages",
        }.get(fact.kind)
        if expected_section != section_id:
            raise _line_error("fact appears in the wrong document section")
        return

    if line.variant_id is None or line.variant_revision is None:
        raise _line_error("variant line lacks an exact variant reference")
    variant = variant_index.get((line.variant_id, line.variant_revision))
    if variant is None or variant.status != "approved":
        raise _line_error("document line references a missing or unapproved variant revision")
    if line.support_binding_refs != variant.support_binding_refs:
        raise _line_error("document line support bindings do not match the variant")
    if line.text != variant.text or section_id != "headline":
        raise _line_error("document variant wording or section is unauthorized")
