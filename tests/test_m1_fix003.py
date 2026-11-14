"""Synthetic regression coverage for the applicant-facing M1 projection."""

from __future__ import annotations

from datetime import UTC, date, datetime

from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import record_human_review
from job_application_engine.rendering.presentation import present_plan
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.document import profile_digest
from job_application_engine.verification.support import (
    canonical_fact_payload,
    canonical_json,
    fact_digest,
)
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix import supported_project_profile


def test_display_omits_internal_unknown_labels_and_keeps_typed_education_details() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 15), reviews=reviews)
    output = render_text(plan, profile, reviews=reviews)

    assert "Synthetic validation thesis" in output
    assert "Synthetic Algorithms | Synthetic Systems" in output
    assert "status: unknown" not in output
    assert "end date unknown" not in output
    assert "(study, recent experience)" in output


def test_contact_scalars_remain_separate_for_long_url_extraction() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 15), reviews=reviews)
    contact = next(section for section in present_plan(plan, profile) if section.label == "")
    texts = [line.text for line in contact.lines]
    assert texts[0] == "Synthetic Example"
    assert all(" | " not in text for text in texts[1:])


def test_linked_and_standalone_projects_are_distinct_and_not_duplicated() -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile,
        as_of=date(2026, 9, 15),
        reviews=reviews,
        support_captures=captures,
    )
    output = render_text(plan, profile, reviews=reviews, support_captures=captures)
    assert output.count("Project: InSite") == 1
    assert output.count("Project: Cost CLI") == 1
    assert "Selected Projects" in output
    assert "Start: January 2024" in output


def test_explicit_skill_categories_are_grouped_without_inventing_qualifiers() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 15), reviews=reviews)
    category = next(f for f in profile.facts if f.fact_id == "skill-german")
    assert category.category == "Data processing & analysis"
    sections = present_plan(plan, profile)
    skills = next(section for section in sections if section.label == "Skills")
    assert [line.text for line in skills.lines] == [
        "Data processing & analysis",
        "Größe Ä Ö Ü ß (study, recent experience)",
    ]
    assert "expert" not in skills.lines[-1].text


def test_duplicate_skill_names_keep_distinct_fact_qualifiers() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 15), reviews=reviews)
    original = next(f for f in profile.facts if f.fact_id == "skill-german")
    duplicate = original.model_copy(
        update={"fact_id": "skill-second", "notes": "basic exposure", "category": "Other"}
    )
    profile = profile.model_copy(update={"facts": [*profile.facts, duplicate]})
    section = next(s for s in plan.sections if s.section_id == "skills")
    line = section.lines[0]
    replacement = section.model_copy(
        update={
            "lines": [
                *section.lines,
                line.model_copy(
                    update={
                        "fact_ref": line.fact_ref.model_copy(update={"fact_id": "skill-second"})
                    }
                ),
            ]
        }
    )
    plan = plan.model_copy(
        update={"sections": [replacement if s.section_id == "skills" else s for s in plan.sections]}
    )
    skills = next(s for s in present_plan(plan, profile) if s.label == "Skills")
    assert [line.text for line in skills.lines] == [
        "Data processing & analysis",
        "Größe Ä Ö Ü ß (study, recent experience)",
        "Größe Ä Ö Ü ß (study, basic exposure)",
    ]


def test_partial_project_description_does_not_hide_role_dates_or_technologies() -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile, as_of=date(2026, 9, 15), reviews=reviews, support_captures=captures
    )
    project = next(f for f in profile.facts if f.fact_id == "project-one")
    changed = project.model_copy(update={"description": "InSite — Software Engineer"})
    profile = profile.model_copy(
        update={"facts": [changed if f.fact_id == project.fact_id else f for f in profile.facts]}
    )
    experience = next(
        s for s in present_plan(plan, profile) if s.label == "Professional Experience"
    )
    lines = [line.text for line in experience.lines]
    assert "Project: InSite — Software Engineer | Start: January 2024" in lines
    assert "Technologies: YOLO v11, Roboflow" in lines
    assert "InSite — Software Engineer" in lines


def test_unknown_degree_name_is_omitted_without_omitting_program() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 15), reviews=reviews)
    profile = profile.model_copy(
        update={
            "facts": [
                f.model_copy(update={"degree_name": None}) if f.kind == "education" else f
                for f in profile.facts
            ]
        }
    )
    education = next(s for s in present_plan(plan, profile) if s.label == "Education")
    assert education.lines[0].text == "Synthetic Computing, Example University"
    assert "Degree not specified" not in "\n".join(line.text for line in education.lines)


def test_empty_presentation_fields_keep_legacy_fact_payload_and_nonempty_fields_bind() -> None:
    profile, reviews = approved_baseline()
    education = next(f for f in profile.facts if f.kind == "education")
    payload = canonical_fact_payload(education)
    assert "thesis_title" in payload
    legacy = education.model_copy(
        update={"thesis_title": None, "thesis_description": None, "coursework": []}
    )
    legacy_payload = canonical_fact_payload(legacy)
    raw = legacy.model_dump(mode="json", exclude={"approval"})
    for key in ("thesis_title", "thesis_description", "coursework"):
        raw.pop(key, None)
    assert legacy_payload == raw
    assert fact_digest(legacy) == "9bb7dc2ae507218b901b1df3380d77da080222e07b7278654f419c030183c639"
    assert fact_digest(education) != fact_digest(legacy)
    legacy_profile = profile.model_copy(
        update={
            "facts": [
                f.model_copy(
                    update=(
                        {"thesis_title": None, "thesis_description": None, "coursework": []}
                        if f.kind == "education"
                        else {"category": None}
                        if f.kind == "skill"
                        else {}
                    )
                )
                for f in profile.facts
            ]
        }
    )
    assert (
        profile_digest(legacy_profile)
        == "9591263c9ddd2fbac3d5e2471599a12b366c7720d0beaef649082756a4e1d9d0"
    )
    receipt = record_human_review(
        profile,
        target_type="fact",
        target_id=education.fact_id,
        target_revision=education.revision,
        displayed_content=canonical_json(payload),
        review_id="review-education-presentation",
        reviewer_id="synthetic-reviewer",
        reviewed_at=datetime(2026, 9, 15, tzinfo=UTC),
    )
    assert receipt.displayed_content == canonical_json(payload)
