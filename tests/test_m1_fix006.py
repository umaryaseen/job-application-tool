"""M1-FIX-006: expected degree completion, specialization and skill display headings."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.ats_qa.text import normalize_extracted_text
from job_application_engine.domain.fact import EducationFact
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.rendering.pdf import TEMPLATE_VERSION, build_pdf
from job_application_engine.rendering.presentation import present_plan
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.support import canonical_fact_payload, fact_digest
from tests.test_document_plan import approved_baseline

ONGOING = {
    "degree_status": "ongoing",
    "period": {
        "start": {"precision": "month", "year": 2023, "month": 4},
        "start_state": "known",
        "end": None,
        "end_state": "ongoing",
    },
    "expected_completion_date": {"precision": "month", "year": 2027, "month": 3},
    "specialization": "Synthetic Learning Systems",
    "coursework": [],
}
BASE = {
    "fact_id": "education-x",
    "revision": 1,
    "subject_id": "synthetic-person",
    "kind": "education",
    "evidence_refs": [{"evidence_id": "attestation-one", "revision": 1}],
    "institution_id": "synthetic-school",
    "program": "Synthetic Computing",
}


def education(**values: object) -> EducationFact:
    return EducationFact.model_validate(BASE | ONGOING | values)


def test_valid_ongoing_degree_with_expected_completion_and_specialization() -> None:
    fact = education()
    assert fact.completion_date is None
    assert fact.expected_completion_date is not None


@pytest.mark.parametrize(
    "values",
    [
        {"completion_date": {"precision": "month", "year": 2027, "month": 3}},
        {"degree_status": "completed"},
        {"degree_status": "unknown"},
        {"expected_completion_date": {"precision": "month", "year": 2022, "month": 1}},
        {
            "period": {
                "start": {"precision": "month", "year": 2023, "month": 4},
                "start_state": "known",
                "end": {"precision": "month", "year": 2026, "month": 9},
                "end_state": "known",
            }
        },
    ],
)
def test_expected_completion_never_implies_an_award(values) -> None:
    with pytest.raises(ValidationError):
        education(**values)


def test_ongoing_degree_cannot_carry_an_actual_completion_date() -> None:
    with pytest.raises(ValidationError, match="ongoing degree cannot have an actual completion"):
        education(
            expected_completion_date=None, completion_date={"precision": "year", "year": 2027}
        )


def test_empty_new_fields_leave_canonical_payload_and_digest_unchanged() -> None:
    fact = education(expected_completion_date=None, specialization=None)
    payload = canonical_fact_payload(fact)
    assert "expected_completion_date" not in payload and "specialization" not in payload
    with_fields = education()
    assert canonical_fact_payload(with_fields)["specialization"] == "Synthetic Learning Systems"
    assert fact_digest(with_fields) != fact_digest(fact)


def test_presentation_and_plan_show_expected_completion_and_specialization() -> None:
    profile, reviews = approved_baseline(ONGOING)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    line = next(s for s in plan.sections if s.section_id == "education").lines[0]
    assert "expected completion: 2027-03" in line.text
    assert "specialization: Synthetic Learning Systems" in line.text
    shown = next(s for s in present_plan(plan, profile) if s.label == "Education")
    texts = [item.text for item in shown.lines]
    assert texts[:2] == [
        "Synthetic MSc — Synthetic Computing, Example University"
        " | April 2023 – Expected March 2027",
        "Specialization: Synthetic Learning Systems",
    ]
    assert not any("ongoing" in text or "completed" in text for text in texts)
    assert "April 2023 – Expected March 2027" in render_text(plan, profile, reviews=reviews)


def test_degree_without_new_fields_renders_exactly_as_before() -> None:
    profile, reviews = approved_baseline(
        {
            key: value
            for key, value in ONGOING.items()
            if key not in {"expected_completion_date", "specialization"}
        }
    )
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    line = next(s for s in plan.sections if s.section_id == "education").lines[0]
    assert line.text.endswith("(status: ongoing; 2023-04 – ongoing)")
    shown = next(s for s in present_plan(plan, profile) if s.label == "Education")
    assert shown.lines[0].text.endswith("| April 2023 – ongoing")
    assert not any(item.text.startswith("Specialization") for item in shown.lines)


def test_display_headings_keep_internal_categories_and_order() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    original = next(f for f in profile.facts if f.fact_id == "skill-german")
    internal = [
        "Tools & infrastructure",
        "Visualization & frontend",
        "Databases & backend",
        "AI & retrieval",
        "Unlisted category",
    ]
    extra = [
        original.model_copy(update={"fact_id": f"skill-{i}", "name": f"Skill {i}", "category": c})
        for i, c in enumerate(internal)
    ]
    profile = profile.model_copy(update={"facts": [*profile.facts, *extra]})
    section = next(s for s in plan.sections if s.section_id == "skills")
    template = section.lines[0]
    lines = [
        *section.lines,
        *(
            template.model_copy(
                update={"fact_ref": template.fact_ref.model_copy(update={"fact_id": f.fact_id})}
            )
            for f in extra
        ),
    ]
    plan = plan.model_copy(
        update={
            "sections": [
                s.model_copy(update={"lines": lines}) if s.section_id == "skills" else s
                for s in plan.sections
            ]
        }
    )
    skills = next(s for s in present_plan(plan, profile) if s.label == "Skills")
    headings = [line.text for line in skills.lines if line.style == "subheading"]
    assert headings == [
        "AI & Machine Learning",
        "Data Engineering & Analytics",
        "Backend & Databases",
        "Frontend & Visualization",
        "Cloud & Infrastructure",
    ]
    assert skills.lines[-1].text.startswith("Skill 4")  # unknown category stays ungrouped
    assert {f.category for f in extra} == set(internal)


def test_template_identity_changed() -> None:
    # M1-FIX-006 introduced v4; M1-FIX-007 superseded it with the exact v5 identity.
    assert TEMPLATE_VERSION == "baseline-v5-m1-fix007-slash-compounds"


def test_real_pdf_extracts_expected_completion_specialization_and_headings(tmp_path: Path) -> None:
    from pypdf import PdfReader

    profile, reviews = approved_baseline(ONGOING)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, output_name="m1-fix006.pdf", data_root=tmp_path)
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    pypdf = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
    expected = [
        "April 2023 – Expected March 2027",
        "Specialization: Synthetic Learning Systems",
        "Data Engineering & Analytics",
    ]
    for text in (poppler, pypdf):
        normalized = normalize_extracted_text(text)
        assert all(normalize_extracted_text(item) in normalized for item in expected)
        assert "ongoing" not in normalized.split("Education", 1)[1].split("Skills", 1)[0]


# Regression for independent review round 1 (docs/reviews/M1-FIX-006.md, F-01).
@pytest.mark.parametrize(
    "update",
    [
        {"completion_date": {"precision": "month", "year": 2027, "month": 3}},
        {"expected_completion_date": {"precision": "month", "year": 2022, "month": 1}},
        {
            "period": {
                "start": {"precision": "month", "year": 2023, "month": 4},
                "start_state": "known",
                "end": {"precision": "month", "year": 2025, "month": 9},
                "end_state": "known",
            },
            "expected_completion_date": None,
            "completion_date": {"precision": "month", "year": 2025, "month": 9},
        },
    ],
)
def test_model_copy_cannot_bypass_education_invariants(update) -> None:
    from job_application_engine.domain.common import DateRange, MonthDate
    from job_application_engine.profile.review import fact_approval_from_review, record_human_review
    from job_application_engine.profile.validation import (
        ProvenanceValidationError,
        validate_profile,
    )
    from job_application_engine.verification.support import canonical_json

    profile, reviews = approved_baseline(ONGOING)
    education = next(f for f in profile.facts if f.kind == "education")
    typed = {
        key: (
            DateRange.model_validate_json(json.dumps(value))
            if key == "period"
            else MonthDate.model_validate_json(json.dumps(value))
            if isinstance(value, dict)
            else value
        )
        for key, value in update.items()
    }
    bad = education.model_copy(update={"degree_status": "ongoing", **typed})
    binding = next(b for b in profile.support_bindings if b.fact_id == bad.fact_id)
    bindings = [
        b.model_copy(update={"fact_sha256": fact_digest(bad)}) if b is binding else b
        for b in profile.support_bindings
    ]
    staged = profile.model_copy(
        update={
            "facts": [bad if f.fact_id == bad.fact_id else f for f in profile.facts],
            "support_bindings": bindings,
        }
    )
    with pytest.raises(ProvenanceValidationError, match="invalid_fact_content"):
        record_human_review(
            staged,
            target_type="fact",
            target_id=bad.fact_id,
            target_revision=bad.revision,
            displayed_content=canonical_json(canonical_fact_payload(bad)),
            review_id="review-bad",
            reviewer_id="synthetic-reviewer",
            reviewed_at=education.approval.approved_at,
        )
    with pytest.raises(ProvenanceValidationError, match="invalid_fact_content"):
        validate_profile(staged, reviews=reviews)
    with pytest.raises(ProvenanceValidationError, match="invalid_fact_content"):
        compile_baseline(staged, as_of=date(2026, 11, 15), reviews=reviews)
    assert fact_approval_from_review  # imported API stays available
