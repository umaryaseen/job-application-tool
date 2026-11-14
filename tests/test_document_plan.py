"""Synthetic TASK-004 document-plan and UTF-8 text tests."""

from __future__ import annotations

import copy
import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from job_application_engine.domain.profile import ProfileRevision
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import (
    fact_approval_from_review,
    record_human_review,
    variant_approval_from_review,
)
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.document import (
    DocumentValidationError,
    document_plan_digest,
)
from job_application_engine.verification.support import canonical_json, evidence_digest, fact_digest

PROFILE_FIXTURE = Path(__file__).parent / "fixtures" / "profiles" / "compact.json"
EXPECTED_TEXT = Path(__file__).parent / "fixtures" / "documents" / "baseline.txt"
REVIEWED_AT = datetime(2026, 9, 12, 13, 0, tzinfo=UTC)


def approved_baseline() -> tuple[ProfileRevision, list[object]]:
    data = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
    facts = data["facts"]
    assert isinstance(facts, list)
    facts.append(
        {
            "fact_id": "skill-german",
            "revision": 1,
            "subject_id": "synthetic-person",
            "kind": "skill",
            "evidence_refs": [{"evidence_id": "attestation-one", "revision": 1}],
            "name": "Größe Ä Ö Ü ß",
            "context": "study",
            "proficiency": "unknown",
            "category": "Data processing & analysis",
            "notes": "recent experience",
        }
    )
    facts.append(
        {
            "fact_id": "employment-two",
            "revision": 1,
            "subject_id": "synthetic-person",
            "kind": "employment",
            "evidence_refs": [{"evidence_id": "attestation-one", "revision": 1}],
            "employer_id": "synthetic-employer",
            "title": "Synthetic Analyst",
            "period": {
                "start": {"precision": "month", "year": 2022, "month": 1},
                "start_state": "known",
                "end": {"precision": "month", "year": 2023, "month": 12},
                "end_state": "known",
            },
        }
    )
    selected_ids = [
        "contact-name",
        "contact-email",
        "employment-one",
        "employment-two",
        "education-one",
        "language-one",
        "skill-german",
    ]
    for fact in facts:
        if isinstance(fact, dict) and fact["fact_id"] in selected_ids:
            fact["support_binding_refs"] = [f"binding-{fact['fact_id']}"]

    draft = ProfileRevision.model_validate_json(json.dumps(data))
    source = draft.evidence[0]
    approved_state = draft.model_copy(
        update={
            "facts": [
                fact.model_copy(update={"status": "approved"})
                if fact.fact_id in selected_ids
                else fact
                for fact in draft.facts
            ]
        }
    )
    binding_data = []
    for fact in approved_state.facts:
        if fact.fact_id not in selected_ids:
            continue
        binding_data.append(
            {
                "binding_id": f"binding-{fact.fact_id}",
                "fact_id": fact.fact_id,
                "fact_revision": fact.revision,
                "evidence_id": source.evidence_id,
                "evidence_revision": source.revision,
                "fact_sha256": fact_digest(fact),
                "evidence_sha256": evidence_digest(source),
                "reviewed_scope": f"synthetic scope for {fact.fact_id}",
                "reviewed_at": "2026-09-12T12:00:00Z",
                "reviewer_id": "synthetic-reviewer",
            }
        )
    data["support_bindings"] = binding_data
    data["variants"] = [
        {
            "variant_id": "headline-one",
            "revision": 1,
            "locale": "en",
            "text": "Synthetic Engineer",
            "fact_refs": [{"fact_id": "employment-one", "revision": 1}],
            "support_binding_refs": ["binding-employment-one"],
            "subject_scope": "synthetic-person",
        }
    ]
    profile = ProfileRevision.model_validate_json(json.dumps(data))
    profile = profile.model_copy(
        update={
            "facts": [
                fact.model_copy(update={"status": "approved"})
                if fact.fact_id in selected_ids
                else fact
                for fact in profile.facts
            ]
        }
    )
    reviews: list[object] = []
    profile_data = profile.model_dump(mode="json")
    for fact in profile.facts:
        if fact.fact_id not in selected_ids:
            continue
        displayed = canonical_json(fact.model_dump(mode="json", exclude={"approval"}))
        receipt = record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=fact.revision,
            displayed_content=displayed,
            review_id=f"review-{fact.fact_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=REVIEWED_AT,
        )
        reviews.append(receipt)
        fact_data = next(item for item in profile_data["facts"] if item["fact_id"] == fact.fact_id)
        fact_data["status"] = "approved"
        fact_data["approval"] = fact_approval_from_review(receipt).model_dump(mode="json")
    profile = ProfileRevision.model_validate_json(json.dumps(profile_data))
    displayed_variant = profile.variants[0].text
    variant_receipt = record_human_review(
        profile,
        target_type="variant",
        target_id="headline-one",
        target_revision=1,
        displayed_content=displayed_variant,
        review_id="review-headline-one",
        reviewer_id="synthetic-reviewer",
        reviewed_at=REVIEWED_AT,
    )
    reviews.append(variant_receipt)
    final_data = profile.model_dump(mode="json")
    final_data["variants"][0]["status"] = "approved"
    final_data["variants"][0]["approval"] = variant_approval_from_review(
        variant_receipt
    ).model_dump(mode="json")
    return ProfileRevision.model_validate_json(json.dumps(final_data)), reviews


def test_complete_synthetic_plan_matches_independent_expected_utf8_fixture() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    output = render_text(plan, profile, reviews=reviews)
    assert output == EXPECTED_TEXT.read_text(encoding="utf-8")
    assert "Größe Ä Ö Ü ß" in output
    assert "Present" not in output


def test_plan_claims_cannot_inject_headline_or_skill_text() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    summary = next(section for section in plan.sections if section.section_id == "headline")
    altered_line = summary.lines[0].model_copy(update={"text": "Invented leadership claim"})
    altered_section = summary.model_copy(update={"lines": [altered_line]})
    altered = plan.model_copy(update={"sections": [altered_section], "plan_sha256": "0" * 64})
    altered = altered.model_copy(update={"plan_sha256": document_plan_digest(altered)})
    with pytest.raises(DocumentValidationError, match="wording"):
        render_text(altered, profile, reviews=reviews)

    skill = next(section for section in plan.sections if section.section_id == "skills")
    altered_skill = skill.lines[0].model_copy(update={"text": "Unsupported Python expertise"})
    altered = plan.model_copy(
        update={
            "sections": [
                section
                if section is not skill
                else skill.model_copy(update={"lines": [altered_skill]})
                for section in plan.sections
            ],
            "plan_sha256": "0" * 64,
        }
    )
    altered = altered.model_copy(update={"plan_sha256": document_plan_digest(altered)})
    with pytest.raises(DocumentValidationError, match="wording"):
        render_text(altered, profile, reviews=reviews)


def test_plan_digest_and_profile_bindings_are_stale_after_mutation() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    changed_data = copy.deepcopy(profile.model_dump(mode="json"))
    changed_fact = next(
        item for item in changed_data["facts"] if item["fact_id"] == "employment-one"
    )
    changed_fact["title"] = "Changed Synthetic Engineer"
    changed_profile = ProfileRevision.model_validate_json(json.dumps(changed_data))
    with pytest.raises(DocumentValidationError, match="profile digest"):
        render_text(plan, changed_profile, reviews=reviews)


def test_optional_sections_are_omitted_and_tied_dates_are_deterministic() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    assert [section.section_id for section in plan.sections] == [
        "contact",
        "headline",
        "experience",
        "education",
        "skills",
        "languages",
    ]
    assert plan.as_of == date(2026, 9, 12)
    output = render_text(plan, profile, reviews=reviews)
    experience_text = output.split("Professional Experience\n", 1)[1].split("\n\n", 1)[0]
    assert experience_text.index("Synthetic Analyst") < experience_text.index("Synthetic Engineer")

    without_language = profile.model_copy(
        update={
            "facts": [
                fact.model_copy(
                    update={"status": "draft", "approval": None, "support_binding_refs": []}
                )
                if fact.fact_id == "language-one"
                else fact
                for fact in profile.facts
            ],
            "support_bindings": [
                binding for binding in profile.support_bindings if binding.fact_id != "language-one"
            ],
        }
    )
    omitted = compile_baseline(without_language, as_of=date(2026, 9, 12), reviews=reviews)
    assert "languages" not in [section.section_id for section in omitted.sections]
