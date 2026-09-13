"""Compile approved profile records into a deterministic baseline plan."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from ..domain.common import Locale
from ..domain.document import DocumentLine, DocumentPlan, DocumentSection
from ..domain.fact import (
    ContactFact,
    EducationFact,
    EmploymentFact,
    FactRef,
    LanguageFact,
    SkillFact,
)
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..profile.validation import validate_profile
from ..verification.document import document_plan_digest, profile_digest
from ..verification.support import EvidenceKey


def _date_text(point: Any) -> str:
    if point is None:
        return ""
    precision = point.precision
    if precision == "year":
        return str(point.year)
    if precision == "month":
        return f"{point.year:04d}-{point.month:02d}"
    return f"{point.year:04d}-{point.month:02d}-{point.day:02d}"


def format_date_range(period: Any) -> str:
    start = _date_text(period.start)
    end_state = period.end_state
    if end_state == "known":
        end = _date_text(period.end)
        return f"{start} – {end}"
    if end_state == "ongoing":
        return f"{start} – ongoing"
    return f"{start} – end date unknown"


def _entity_name(profile: ProfileRevision, entity_id: str) -> str:
    for entity in profile.entities:
        if entity.entity_id == entity_id:
            return entity.display_name
    raise ValueError(f"missing entity {entity_id}")


def fact_line_text(profile: ProfileRevision, fact: Any) -> str:
    if isinstance(fact, ContactFact):
        return f"{fact.value.kind.title()}: {fact.value.value}"
    if isinstance(fact, EmploymentFact):
        return (
            f"{fact.title} — {_entity_name(profile, fact.employer_id)}"
            f" | {format_date_range(fact.period)}"
        )
    if isinstance(fact, EducationFact):
        degree = fact.degree_name or "Degree not specified"
        status = fact.degree_status
        return (
            f"{degree} — {fact.program}, {_entity_name(profile, fact.institution_id)}"
            f" (status: {status}; {format_date_range(fact.period)})"
        )
    if isinstance(fact, SkillFact):
        return f"{fact.name} (context: {fact.context}; proficiency: {fact.proficiency})"
    if isinstance(fact, LanguageFact):
        assessment = fact.assessment
        if assessment.assessment == "cefr":
            detail = f"CEFR {assessment.level}"
        elif assessment.assessment == "test_score":
            detail = f"{assessment.test_name} score {assessment.score}"
        else:
            detail = f"self-description: {assessment.description}"
        return f"{fact.language} ({detail})"
    raise ValueError(
        f"fact kind is not supported by the baseline plan: {getattr(fact, 'kind', None)}"
    )


def _fact_line(profile: ProfileRevision, fact: Any) -> DocumentLine:
    return DocumentLine(
        text=fact_line_text(profile, fact),
        source="fact",
        fact_ref=FactRef(fact_id=fact.fact_id, revision=fact.revision),
        support_binding_refs=list(fact.support_binding_refs),
    )


def _approved_facts(profile: ProfileRevision, kind: str) -> list[Any]:
    return [fact for fact in profile.facts if fact.status == "approved" and fact.kind == kind]


def _start_key(fact: Any) -> tuple[int, int, int, str]:
    point = fact.period.start
    if point is None:
        return (0, 0, 0, fact.fact_id)
    return (
        point.year,
        getattr(point, "month", 0),
        getattr(point, "day", 0),
        fact.fact_id,
    )


def compile_baseline(
    profile: ProfileRevision,
    *,
    as_of: date,
    reviews: Sequence[LocalReviewReceipt] = (),
    support_captures: Mapping[EvidenceKey, bytes | bytearray] | None = None,
    locale: Locale = "en",
) -> DocumentPlan:
    """Compile only locally reviewed approved records into standard sections."""

    validate_profile(profile, reviews=reviews, support_captures=support_captures)
    sections: list[DocumentSection] = []

    contacts = sorted(
        _approved_facts(profile, "contact"), key=lambda fact: (fact.kind, fact.fact_id)
    )
    if contacts:
        sections.append(
            DocumentSection(
                section_id="contact",
                label="Contact",
                lines=[_fact_line(profile, fact) for fact in contacts],
            )
        )

    variants = sorted(
        [variant for variant in profile.variants if variant.status == "approved"],
        key=lambda variant: (variant.variant_id, variant.revision),
    )
    if variants:
        sections.append(
            DocumentSection(
                section_id="headline",
                label="Professional Summary",
                lines=[
                    DocumentLine(
                        text=variant.text,
                        source="variant",
                        variant_id=variant.variant_id,
                        variant_revision=variant.revision,
                        support_binding_refs=list(variant.support_binding_refs),
                    )
                    for variant in variants
                ],
            )
        )

    employment = sorted(_approved_facts(profile, "employment"), key=_start_key, reverse=True)
    if employment:
        sections.append(
            DocumentSection(
                section_id="experience",
                label="Professional Experience",
                lines=[_fact_line(profile, fact) for fact in employment],
            )
        )

    education = sorted(_approved_facts(profile, "education"), key=_start_key, reverse=True)
    if education:
        sections.append(
            DocumentSection(
                section_id="education",
                label="Education",
                lines=[_fact_line(profile, fact) for fact in education],
            )
        )

    skills = sorted(
        _approved_facts(profile, "skill"), key=lambda fact: (fact.name.casefold(), fact.fact_id)
    )
    if skills:
        sections.append(
            DocumentSection(
                section_id="skills",
                label="Skills",
                lines=[_fact_line(profile, fact) for fact in skills],
            )
        )

    languages = sorted(
        _approved_facts(profile, "language"),
        key=lambda fact: (fact.language.casefold(), fact.fact_id),
    )
    if languages:
        sections.append(
            DocumentSection(
                section_id="languages",
                label="Languages",
                lines=[_fact_line(profile, fact) for fact in languages],
            )
        )

    draft = DocumentPlan(
        plan_version="1.0",
        profile_id=profile.profile_id,
        profile_revision=profile.revision,
        profile_digest=profile_digest(profile),
        as_of=as_of,
        locale=locale,
        sections=sections,
        plan_sha256="0" * 64,
    )
    return draft.model_copy(update={"plan_sha256": document_plan_digest(draft)})
