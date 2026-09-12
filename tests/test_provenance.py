"""Synthetic adversarial tests for TASK-003 provenance validation."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.domain.profile import ProfileRevision, load_profile_json
from job_application_engine.profile.review import record_human_review
from job_application_engine.profile.validation import ProvenanceValidationError, validate_profile
from job_application_engine.verification.support import (
    SupportIntegrityError,
    evidence_digest,
    fact_digest,
    verify_support_captures,
)

FIXTURE = Path(__file__).parent / "fixtures" / "profiles" / "compact.json"
REVIEWED_AT = datetime(2026, 9, 12, 12, 30, tzinfo=UTC)


def profile_data() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def profile_with(data: dict[str, object]) -> ProfileRevision:
    return ProfileRevision.model_validate_json(json.dumps(data))


def issue_codes(error: ProvenanceValidationError) -> set[str]:
    return {issue.code for issue in error.issues}


def test_exact_revision_resolution_rejects_dangling_and_revoked_evidence() -> None:
    dangling = profile_data()
    facts = dangling["facts"]
    assert isinstance(facts, list)
    assert isinstance(facts[0], dict)
    facts[0]["evidence_refs"] = [{"evidence_id": "attestation-one", "revision": 2}]
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(dangling))
    assert "dangling_evidence" in issue_codes(error.value)

    revoked = profile_data()
    evidence = revoked["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0]["status"] = "revoked"
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(revoked))
    assert "revoked_evidence" in issue_codes(error.value)


def test_binding_scope_and_cycles_are_checked() -> None:
    data = profile_data()
    facts = data["facts"]
    assert isinstance(facts, list)
    contact = facts[0]
    education = facts[2]
    assert isinstance(contact, dict) and isinstance(education, dict)
    evidence = profile_with(data).evidence[0]
    education_fact = profile_with(data).facts[2]
    binding_data = {
        "binding_id": "binding-one",
        "fact_id": education_fact.fact_id,
        "fact_revision": education_fact.revision,
        "evidence_id": evidence.evidence_id,
        "evidence_revision": evidence.revision,
        "fact_sha256": fact_digest(education_fact),
        "evidence_sha256": evidence_digest(evidence),
        "reviewed_scope": "synthetic education scope",
        "reviewed_at": "2026-09-12T12:00:00Z",
        "reviewer_id": "synthetic-reviewer",
    }
    contact["support_binding_refs"] = ["binding-one"]
    data["support_bindings"] = [binding_data]
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(data))
    assert "wrong_fact_scope" in issue_codes(error.value)

    cycle = profile_data()
    cycle_profile = profile_with(cycle)
    fact = cycle_profile.facts[0]
    source = cycle_profile.evidence[0]
    common = {
        "fact_id": fact.fact_id,
        "fact_revision": fact.revision,
        "evidence_id": source.evidence_id,
        "evidence_revision": source.revision,
        "fact_sha256": fact_digest(fact),
        "evidence_sha256": evidence_digest(source),
        "reviewed_scope": "synthetic contact scope",
        "reviewed_at": "2026-09-12T12:00:00Z",
        "reviewer_id": "synthetic-reviewer",
    }
    cycle["support_bindings"] = [
        {**common, "binding_id": "binding-a", "depends_on_binding_refs": ["binding-b"]},
        {**common, "binding_id": "binding-b", "depends_on_binding_refs": ["binding-a"]},
    ]
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(cycle))
    assert "cyclic_binding" in issue_codes(error.value)


def test_unpinned_documentary_reference_must_remain_draft() -> None:
    data = profile_data()
    evidence = data["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0] = {
        "evidence_id": "attestation-one",
        "revision": 1,
        "kind": "document_reference",
        "source": {"kind": "document_reference", "locator": "synthetic.pdf"},
        "support_capture_sha256": (
            "1111111111111111111111111111111111111111111111111111111111111111"
        ),
        "captured_at": "2026-09-12T12:00:00Z",
        "status": "draft",
    }
    assert validate_profile(profile_with(data)).evidence[0].status == "draft"
    evidence[0]["status"] = "approved"
    evidence[0]["approval"] = {
        "evidence_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
        "approved_at": "2026-09-12T12:00:00Z",
        "reviewer_id": "synthetic-reviewer",
    }
    with pytest.raises(ValidationError, match="source-file hash"):
        profile_with(data)


def test_support_capture_missing_and_changed_are_rejected() -> None:
    evidence = load_profile_json(FIXTURE).evidence
    with pytest.raises(SupportIntegrityError, match="missing support capture"):
        verify_support_captures(evidence, required={("attestation-one", 1)})
    with pytest.raises(SupportIntegrityError, match="hash mismatch"):
        verify_support_captures(
            evidence,
            {("attestation-one", 1): b"changed synthetic capture"},
            required={("attestation-one", 1)},
        )


def test_human_review_records_exact_payload_and_rejects_changed_wording() -> None:
    profile = load_profile_json(FIXTURE)
    fact = profile.facts[0]
    displayed = json.dumps(
        fact.model_dump(mode="json", exclude={"approval"}),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    receipt = record_human_review(
        profile,
        target_type="fact",
        target_id=fact.fact_id,
        target_revision=fact.revision,
        displayed_content=displayed,
        review_id="review-one",
        reviewer_id="synthetic-reviewer",
        reviewed_at=REVIEWED_AT,
    )
    assert receipt.issuer == "local_human"
    assert receipt.displayed_content == displayed
    assert receipt.displayed_content_sha256 == fact_digest(fact)
    with pytest.raises(ProvenanceValidationError, match="display_changed"):
        record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=fact.revision,
            displayed_content=displayed.replace("synthetic@example.com", "false@example.com"),
            review_id="review-two",
            reviewer_id="synthetic-reviewer",
            reviewed_at=REVIEWED_AT,
        )
    assert profile.evidence[0].source.kind == "user_attestation"


def test_generated_output_cannot_be_source_evidence() -> None:
    data = profile_data()
    evidence = data["evidence"]
    assert isinstance(evidence, list) and isinstance(evidence[0], dict)
    evidence[0]["source"] = {
        "kind": "import_reference",
        "import_id": "generated-output-one",
        "source_role": "generated_output",
    }
    evidence[0]["kind"] = "import_reference"
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(data))
    assert "generated_source" in issue_codes(error.value)


def test_variant_resolves_exact_fact_revisions_and_subject_scope() -> None:
    data = profile_data()
    data["variants"] = [
        {
            "variant_id": "variant-one",
            "revision": 1,
            "locale": "en",
            "text": "Synthetic wording",
            "fact_refs": [{"fact_id": "education-one", "revision": 1}],
            "support_binding_refs": ["missing-binding"],
            "subject_scope": "synthetic-person",
        }
    ]
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(data))
    assert "dangling_variant_binding" in issue_codes(error.value)

    altered = copy.deepcopy(data)
    assert isinstance(altered["variants"], list)
    assert isinstance(altered["variants"][0], dict)
    altered["variants"][0]["fact_refs"] = [{"fact_id": "missing-real-id", "revision": 1}]
    with pytest.raises(ProvenanceValidationError) as error:
        validate_profile(profile_with(altered))
    assert "dangling_variant_fact" in issue_codes(error.value)
