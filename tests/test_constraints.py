"""TASK-015 / A07, A22, A23: scoped constraints and experience intervals.

Expectations come from the independently reviewed synthetic oracle in
``tests/fixtures/matching``; the harness only builds approved facts from it.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from job_application_engine.domain.common import DateRange
from job_application_engine.domain.profile import ProfileRevision
from job_application_engine.domain.requirement import Threshold
from job_application_engine.matching import durations
from job_application_engine.matching.constraints import (
    Constraint,
    ConstraintError,
    evaluate_constraints,
    months_from_threshold,
)
from job_application_engine.profile.review import fact_approval_from_review, record_human_review
from job_application_engine.verification.support import (
    canonical_fact_payload,
    canonical_json,
    evidence_digest,
    fact_digest,
)

FIXTURE = Path(__file__).parent / "fixtures" / "matching" / "constraints.json"
ORACLE = json.loads(FIXTURE.read_text(encoding="utf-8"))
COMPACT = Path(__file__).parent / "fixtures" / "profiles" / "compact.json"
REVIEWED_AT = datetime(2026, 9, 12, 13, 0, tzinfo=UTC)
CONSTRAINT = TypeAdapter(Constraint)


def build_profile(simplified: list[dict]) -> tuple[ProfileRevision, list[object]]:
    """Approved revision-1 facts for ``approved`` entries; others stay unapproved."""

    base = json.loads(COMPACT.read_text(encoding="utf-8"))
    data = {key: base[key] for key in ("schema_version", "profile_id", "revision", "created_at")}
    data["content_sha256"] = base["content_sha256"]
    data["entities"] = [
        *base["entities"],
        {"entity_id": "synthetic-project", "entity_type": "project", "display_name": "Example"},
    ]
    data["evidence"] = base["evidence"]
    facts = []
    approved_ids = []
    for item in simplified:
        fact = copy.deepcopy(item)
        status = fact.pop("status")
        fact.update(
            revision=1,
            subject_id="synthetic-person",
            evidence_refs=[{"evidence_id": "attestation-one", "revision": 1}],
            status="draft" if status == "approved" else status,
        )
        if status == "approved":
            fact["support_binding_refs"] = [f"binding-{fact['fact_id']}"]
            approved_ids.append(fact["fact_id"])
        facts.append(fact)
    data["facts"] = facts
    draft = ProfileRevision.model_validate_json(json.dumps(data))
    source = draft.evidence[0]
    staged = draft.model_copy(
        update={
            "facts": [
                f.model_copy(update={"status": "approved"}) if f.fact_id in approved_ids else f
                for f in draft.facts
            ]
        }
    )
    data["support_bindings"] = [
        {
            "binding_id": f"binding-{fact.fact_id}",
            "fact_id": fact.fact_id,
            "fact_revision": 1,
            "evidence_id": source.evidence_id,
            "evidence_revision": source.revision,
            "fact_sha256": fact_digest(fact),
            "evidence_sha256": evidence_digest(source),
            "reviewed_scope": f"synthetic scope for {fact.fact_id}",
            "reviewed_at": "2026-09-12T12:00:00Z",
            "reviewer_id": "synthetic-reviewer",
        }
        for fact in staged.facts
        if fact.fact_id in approved_ids
    ]
    profile = ProfileRevision.model_validate_json(json.dumps(data))
    profile = profile.model_copy(
        update={
            "facts": [
                f.model_copy(update={"status": "approved"}) if f.fact_id in approved_ids else f
                for f in profile.facts
            ]
        }
    )
    reviews: list[object] = []
    payload = profile.model_dump(mode="json")
    for fact in profile.facts:
        if fact.fact_id not in approved_ids:
            continue
        receipt = record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=1,
            displayed_content=canonical_json(canonical_fact_payload(fact)),
            review_id=f"review-{fact.fact_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=REVIEWED_AT,
        )
        reviews.append(receipt)
        entry = next(item for item in payload["facts"] if item["fact_id"] == fact.fact_id)
        entry["status"] = "approved"
        entry["approval"] = fact_approval_from_review(receipt).model_dump(mode="json")
    return ProfileRevision.model_validate_json(json.dumps(payload)), reviews


def facts_for(case: dict) -> list[dict]:
    removed = set(case.get("remove_fact_ids", []))
    return [f for f in ORACLE["base_facts"] if f["fact_id"] not in removed] + case.get(
        "extra_facts", []
    )


@pytest.mark.parametrize("case", ORACLE["cases"], ids=[c["id"] for c in ORACLE["cases"]])
def test_independently_reviewed_oracle(case: dict) -> None:
    profile, reviews = build_profile(facts_for(case))
    constraint = CONSTRAINT.validate_json(json.dumps(case["constraint"]))
    as_of = date.fromisoformat(case.get("as_of", ORACLE["as_of_default"]))
    [result] = evaluate_constraints(profile, [constraint], as_of=as_of, reviews=reviews)
    expected = case["expected"]
    actual = {
        "state": result.state,
        "rationale": result.rationale,
        "fact_ids": [ref.fact_id for ref in result.fact_refs],
    }
    if case["constraint"]["type"] == "duration":
        actual |= {
            "lower_months": result.lower_months,
            "upper_months": result.upper_months,
            "excluded": result.excluded,
        }
        assert result.basis == "calendar_months_not_fte"
    else:
        assert result.lower_months is None and result.basis is None
    assert actual == expected
    assert result.as_of == as_of


def test_fixture_identity_and_coverage() -> None:
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert digest == FIXTURE_SHA256
    kinds = {c["constraint"]["type"] for c in ORACLE["cases"]}
    assert kinds == {"language", "credential", "degree", "authorization", "duration"}
    states = {c["expected"]["state"] for c in ORACLE["cases"]}
    assert states == {"direct", "explicitly_unmet", "no_evidence", "unknown"}


# Pinned: the reviewed oracle (fixture rounds 1-2 plus follow-ups F-01..F-03).
FIXTURE_SHA256 = "0359c0c6d418ca518e543b32f726a23ea64fb418a73c4259207c17fb1bf3ffd6"


def test_unknown_skill_concept_is_rejected() -> None:
    profile, reviews = build_profile(ORACLE["base_facts"])
    constraint = CONSTRAINT.validate_json(
        json.dumps(
            {"type": "duration", "months": 1, "scope": {"kind": "skill", "concept": "made-up"}}
        )
    )
    with pytest.raises(ConstraintError):
        evaluate_constraints(profile, [constraint], as_of=date(2026, 11, 15), reviews=reviews)


@pytest.mark.parametrize(
    "bad",
    [
        {"type": "language", "language": "German", "min_level": "B3"},
        {"type": "language", "language": "German"},
        {"type": "duration", "months": 0, "scope": {"kind": "overall"}},
        {"type": "duration", "months": 1201, "scope": {"kind": "overall"}},
        {"type": "duration", "months": 12, "scope": {"kind": "fte"}},
        {"type": "authorization", "country": "Germany", "inferred_from": "residence"},
        {"type": "salary", "amount": 1},
    ],
)
def test_unsupported_constraint_shapes_are_rejected(bad: dict) -> None:
    with pytest.raises(ValidationError):
        CONSTRAINT.validate_json(json.dumps(bad))


def test_unapproved_profile_is_refused_before_evaluation() -> None:
    profile, _ = build_profile(ORACLE["base_facts"])
    constraint = CONSTRAINT.validate_json(
        json.dumps({"type": "duration", "months": 1, "scope": {"kind": "overall"}})
    )
    with pytest.raises(ValueError):
        evaluate_constraints(profile, [constraint], as_of=date(2026, 11, 15), reviews=[])


# Implementer adversarial checks (not part of the reviewed oracle).


def test_range_union_equals_brute_force_month_sets() -> None:
    import random

    rng = random.Random(15)
    for _ in range(400):
        ranges = []
        for _ in range(rng.randint(0, 8)):
            start = rng.randint(0, 60)
            ranges.append((start, start + rng.randint(-3, 20)))
        expected = len({m for a, b in ranges for m in range(a, b + 1)})
        assert durations._union_size(ranges) == expected


def _period(start: dict | None, end: dict | None, end_state: str) -> DateRange:
    return DateRange.model_validate_json(
        json.dumps(
            {
                "start": start,
                "start_state": "known" if start else "unknown",
                "end": end,
                "end_state": end_state,
            }
        )
    )


def test_extreme_years_and_many_intervals_stay_bounded() -> None:
    wide = _period({"precision": "year", "year": 1}, {"precision": "year", "year": 9998}, "known")
    bounds = durations.union_bounds([("wide", wide)], date(9999, 12, 31))
    assert bounds.upper_months == 9998 * 12 and bounds.lower_months == 9996 * 12
    many = [
        (
            f"f{i}",
            _period(
                {"precision": "month", "year": 1900 + i % 100, "month": 1 + i % 12},
                {"precision": "month", "year": 2000, "month": 12},
                "known",
            ),
        )
        for i in range(5000)
    ]
    result = durations.union_bounds(many, date(2026, 11, 15))
    assert result.upper_months == (2000 - 1900) * 12 + 12 and len(result.contributing) == 5000


def test_adjacent_ranges_merge_and_gaps_do_not_count() -> None:
    assert durations._union_size([(1, 3), (4, 6)]) == 6
    assert durations._union_size([(1, 3), (5, 6)]) == 5
    assert durations._union_size([(5, 4), (1, 1)]) == 1


def test_same_month_interval_has_no_certain_month() -> None:
    same = _period(
        {"precision": "month", "year": 2020, "month": 5},
        {"precision": "month", "year": 2020, "month": 5},
        "known",
    )
    bounds = durations.union_bounds([("same", same)], date(2026, 1, 1))
    assert (bounds.lower_months, bounds.upper_months, bounds.contributing) == (0, 1, ("same",))


def test_as_of_must_be_a_date_not_a_datetime() -> None:
    profile, reviews = build_profile(ORACLE["base_facts"])
    constraint = CONSTRAINT.validate_json(
        json.dumps({"type": "duration", "months": 1, "scope": {"kind": "overall"}})
    )
    with pytest.raises(ConstraintError):
        evaluate_constraints(
            profile, [constraint], as_of=datetime(2026, 11, 15, tzinfo=UTC), reviews=reviews
        )


def test_unicode_equivalent_names_compare_equal() -> None:
    composed, decomposed = "Zertifikat Ü", "Zertifikat Ü"
    facts = [
        {"fact_id": "cred-u", "kind": "credential", "status": "approved",
         "value": {"name": composed, "status": "awarded"}},
    ]  # fmt: skip
    profile, reviews = build_profile(facts)
    constraint = CONSTRAINT.validate_json(json.dumps({"type": "credential", "name": decomposed}))
    [result] = evaluate_constraints(
        profile, [constraint], as_of=date(2026, 11, 15), reviews=reviews
    )
    assert (result.state, [r.fact_id for r in result.fact_refs]) == ("direct", ["cred-u"])


@pytest.mark.parametrize(
    ("threshold", "months"),
    [
        ({"operator": "gte", "value": 5, "unit": "years"}, 60),
        ({"operator": "unqualified", "value": 3, "unit": "years"}, 36),
        ({"operator": "gt", "value": 3, "unit": "years"}, 37),
        ({"operator": "range", "value": 3, "upper": 5, "unit": "years"}, 36),
        ({"operator": "gte", "value": 6, "unit": "months"}, 6),
    ],
)
def test_task012_duration_thresholds_convert_to_minimum_months(
    threshold: dict, months: int
) -> None:
    parsed = Threshold.model_validate_json(
        json.dumps(
            {"measure": "duration", "span": {"start": 0, "end": 1, "quote": "x"}, **threshold}
        )
    )
    assert months_from_threshold(parsed) == months


def test_cefr_and_out_of_range_thresholds_do_not_convert() -> None:
    cefr = Threshold.model_validate_json(
        json.dumps({"measure": "language_level", "operator": "gte", "level": "B2", "unit": "cefr",
                    "span": {"start": 0, "end": 2, "quote": "B2"}})
    )  # fmt: skip
    zero = Threshold.model_validate_json(
        json.dumps({"measure": "duration", "operator": "gte", "value": 0, "unit": "years",
                    "span": {"start": 0, "end": 1, "quote": "0"}})
    )  # fmt: skip
    for threshold in (cefr, zero):
        with pytest.raises(ConstraintError):
            months_from_threshold(threshold)
