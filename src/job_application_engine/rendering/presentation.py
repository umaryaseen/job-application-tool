"""Deterministic applicant-facing projection of a validated document plan."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..domain.document import DocumentPlan
from ..domain.fact import (
    ContactFact,
    ContactName,
    EducationFact,
    EmploymentFact,
    LanguageFact,
    ProjectFact,
    ResponsibilityFact,
    SkillFact,
)
from ..domain.profile import ProfileRevision
from ..profile.baseline import _entity_name

_SKILL_CATEGORIES = (
    "Data processing & analysis",
    "Databases & backend",
    "Visualization & frontend",
    "AI & retrieval",
    "Tools & infrastructure",
)


@dataclass(frozen=True)
class DisplayLine:
    text: str
    style: str = "body"


@dataclass(frozen=True)
class DisplaySection:
    label: str
    lines: tuple[DisplayLine, ...]
    page_break_before: bool = False


def _pretty_date(point: Any) -> str:
    if point is None:
        return ""
    if point.precision == "year":
        return str(point.year)
    if point.precision == "month":
        months = (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )
        return f"{months[point.month - 1]} {point.year}"
    return f"{point.year:04d}-{point.month:02d}-{point.day:02d}"


def _date_range(period: Any) -> str:
    start = _pretty_date(period.start)
    if period.end_state == "known":
        end = _pretty_date(period.end)
        return f"{start} – {end}" if start else (f"End: {end}" if end else "")
    if period.end_state == "ongoing":
        return f"{start} – ongoing" if start else "ongoing"
    if start:
        return f"Start: {start}"
    end = _pretty_date(period.end)
    return f"End: {end}" if end else ""


def _fact_index(profile: ProfileRevision) -> dict[tuple[str, int], Any]:
    return {(fact.fact_id, fact.revision): fact for fact in profile.facts}


def _skill_label(fact: SkillFact) -> str:
    qualifier: list[str] = []
    name_folded = fact.name.casefold()
    if fact.context != "unknown" and fact.context.casefold() not in name_folded:
        qualifier.append(fact.context)
    if fact.proficiency != "unknown":
        qualifier.append(fact.proficiency)
    if fact.notes and fact.notes.casefold() not in name_folded:
        qualifier.append(fact.notes)
    return f"{fact.name} ({', '.join(qualifier)})" if qualifier else fact.name


def _project_lines(profile: ProfileRevision, fact: ProjectFact) -> list[DisplayLine]:
    # A reviewed description that already contains project identity/role/dates
    # is emitted once. Typed metadata is used when no such wording exists.
    description = fact.description or ""
    known_period = _date_range(fact.period)
    metadata = f"{fact.project_name} — {fact.role}"
    if known_period:
        metadata += f" | {known_period}"
    complete_metadata = [fact.project_name, fact.role]
    if known_period:
        complete_metadata.append(known_period)
    complete_metadata.extend(fact.technologies)
    if description and all(value in description for value in complete_metadata):
        return [DisplayLine(f"Project: {description}", style="project")]
    lines = [DisplayLine(f"Project: {metadata}", style="project")]
    if fact.technologies:
        lines.append(DisplayLine("Technologies: " + ", ".join(fact.technologies), style="project"))
    if description:
        lines.append(DisplayLine(description, style="project"))
    return lines


def present_plan(plan: DocumentPlan, profile: ProfileRevision) -> tuple[DisplaySection, ...]:
    """Project validated claim lines into a stable, readable display policy."""

    facts = _fact_index(profile)
    result: list[DisplaySection] = []
    standalone_facts: list[ProjectFact] = []
    for section in plan.sections:
        lines: list[DisplayLine] = []
        if section.section_id == "contact":
            for line in section.lines:
                fact = (
                    facts.get((line.fact_ref.fact_id, line.fact_ref.revision))
                    if line.fact_ref
                    else None
                )
                if isinstance(fact, ContactFact):
                    if isinstance(fact.value, ContactName):
                        lines.append(DisplayLine(fact.value.value, style="name"))
                    else:
                        # Keep each contact scalar on its own compact line so
                        # long URLs remain an indivisible extraction token.
                        lines.append(DisplayLine(f"{fact.value.kind.title()}: {fact.value.value}"))
        elif section.section_id == "experience":
            for line in section.lines:
                fact = (
                    facts.get((line.fact_ref.fact_id, line.fact_ref.revision))
                    if line.fact_ref
                    else None
                )
                if isinstance(fact, EmploymentFact):
                    location = f" | {fact.location}" if fact.location else ""
                    lines.append(
                        DisplayLine(
                            f"{fact.title} — {_entity_name(profile, fact.employer_id)}{location}",
                            style="employment",
                        )
                    )
                    period = _date_range(fact.period)
                    if period:
                        lines.append(DisplayLine(period))
                elif isinstance(fact, ResponsibilityFact):
                    lines.append(DisplayLine(fact.text, style="bullet"))
                elif isinstance(fact, ProjectFact):
                    if fact.employment_ref is not None:
                        lines.extend(_project_lines(profile, fact))
                    else:
                        standalone_facts.append(fact)
        elif section.section_id == "education":
            for line in section.lines:
                fact = (
                    facts.get((line.fact_ref.fact_id, line.fact_ref.revision))
                    if line.fact_ref
                    else None
                )
                if isinstance(fact, EducationFact):
                    text = f"{fact.program}, {_entity_name(profile, fact.institution_id)}"
                    if fact.degree_name:
                        text = f"{fact.degree_name} — {text}"
                    period = _date_range(fact.period)
                    if period:
                        text += f" | {period}"
                    if fact.degree_status not in {"unknown", "ongoing"}:
                        text += f" ({fact.degree_status})"
                    lines.append(DisplayLine(text))
                    if fact.thesis_title:
                        lines.append(DisplayLine(f"Thesis: {fact.thesis_title}"))
                    if fact.thesis_description:
                        lines.append(DisplayLine(fact.thesis_description))
                    if fact.coursework:
                        lines.append(DisplayLine("Coursework: " + " | ".join(fact.coursework)))
        elif section.section_id == "skills":
            by_ref: dict[tuple[str, int], SkillFact] = {}
            for line in section.lines:
                fact = (
                    facts.get((line.fact_ref.fact_id, line.fact_ref.revision))
                    if line.fact_ref
                    else None
                )
                if isinstance(fact, SkillFact):
                    by_ref[(fact.fact_id, fact.revision)] = fact
            grouped: dict[str, list[SkillFact]] = {}
            ungrouped: list[SkillFact] = []
            for fact in by_ref.values():
                if fact.category in _SKILL_CATEGORIES:
                    grouped.setdefault(fact.category, []).append(fact)
                else:
                    ungrouped.append(fact)
            for category in _SKILL_CATEGORIES:
                if category not in grouped:
                    continue
                lines.append(DisplayLine(category, style="subheading"))
                lines.append(
                    DisplayLine(
                        " | ".join(
                            _skill_label(fact)
                            for fact in sorted(
                                grouped[category],
                                key=lambda item: (
                                    item.name.casefold(),
                                    item.fact_id,
                                    item.revision,
                                ),
                            )
                        )
                    )
                )
            lines.extend(
                DisplayLine(_skill_label(fact))
                for fact in sorted(
                    ungrouped, key=lambda item: (item.name.casefold(), item.fact_id, item.revision)
                )
            )
        elif section.section_id == "languages":
            for line in section.lines:
                fact = (
                    facts.get((line.fact_ref.fact_id, line.fact_ref.revision))
                    if line.fact_ref
                    else None
                )
                if isinstance(fact, LanguageFact):
                    assessment = fact.assessment
                    if assessment.assessment == "cefr":
                        detail = f"CEFR {assessment.level}"
                    elif assessment.assessment == "test_score":
                        detail = f"{assessment.test_name} score {assessment.score}"
                    else:
                        detail = assessment.description
                    lines.append(DisplayLine(f"{fact.language} ({detail})"))
        else:
            lines = [DisplayLine(line.text) for line in section.lines]
        if lines:
            result.append(
                DisplaySection(
                    "" if section.section_id == "contact" else section.label,
                    tuple(lines),
                )
            )
    standalone = standalone_facts
    if standalone:
        project_lines = [line for fact in standalone for line in _project_lines(profile, fact)]
        has_prior_content = any(section.label for section in result)
        result.insert(
            next(
                (index for index, section in enumerate(result) if section.label == "Education"),
                len(result),
            ),
            DisplaySection(
                "Selected Projects",
                tuple(project_lines),
                page_break_before=has_prior_content,
            ),
        )
    return tuple(result)
