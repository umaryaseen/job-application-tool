from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.domain.fact import CredentialValue, LanguageTestScore, Metric
from job_application_engine.domain.profile import (
    DuplicateJsonKeyError,
    ProfileRevision,
    load_profile_json,
)
from job_application_engine.schema_export import profile_schema

FIXTURES = Path(__file__).parent / "fixtures" / "profiles"


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_compact_and_two_page_synthetic_profiles_validate() -> None:
    compact = load_profile_json(FIXTURES / "compact.json")
    two_page = load_profile_json(FIXTURES / "two-page.json")
    assert compact.profile_id == "synthetic-profile"
    assert two_page.profile_id == "synthetic-two-page"
    assert len(two_page.facts) > len(compact.facts)


def test_unknown_fields_and_python_coercion_are_rejected() -> None:
    unknown = fixture("compact.json")
    unknown["unexpected"] = True
    with pytest.raises(ValidationError, match="unexpected"):
        ProfileRevision.model_validate(unknown)

    coerced = fixture("compact.json")
    coerced["revision"] = "1"
    with pytest.raises(ValidationError):
        ProfileRevision.model_validate(coerced)


def test_bad_dates_and_reversed_ranges_are_rejected() -> None:
    bad_month = fixture("compact.json")
    employment = bad_month["facts"][1]  # type: ignore[index]
    employment["period"]["start"]["month"] = 13  # type: ignore[index]
    with pytest.raises(ValidationError):
        ProfileRevision.model_validate(bad_month)

    reversed_range = fixture("compact.json")
    employment = reversed_range["facts"][1]  # type: ignore[index]
    employment["period"]["end"] = {"precision": "month", "year": 2021, "month": 12}  # type: ignore[index]
    employment["period"]["end_state"] = "known"  # type: ignore[index]
    with pytest.raises(ValidationError, match="reversed"):
        ProfileRevision.model_validate(reversed_range)


def test_unknown_states_and_cefr_test_score_distinction_are_preserved() -> None:
    profile = load_profile_json(FIXTURES / "compact.json")
    education = next(f for f in profile.facts if f.kind == "education")
    assert education.degree_status == "unknown"
    assert education.period.start_state == "unknown"

    with pytest.raises(ValidationError):
        LanguageTestScore.model_validate(
            {"assessment": "test_score", "test_name": "Synthetic Test", "score": 8.0}
        )
    with pytest.raises(ValidationError):
        ProfileRevision.model_validate(
            {
                **fixture("compact.json"),
                "facts": [
                    {
                        **fixture("compact.json")["facts"][3],  # type: ignore[index]
                        "assessment": {"assessment": "cefr", "level": "8.0"},
                    }
                ],
            }
        )


def test_metrics_credentials_and_expiry_are_typed() -> None:
    metric = Metric(value="10.00", unit="currency", currency="EUR")
    assert str(metric.value) == "10.00"
    with pytest.raises(ValidationError):
        Metric(value=10, unit="percent")
    with pytest.raises(ValidationError):
        CredentialValue(name="Synthetic Credential", status="expired")
    with pytest.raises(ValidationError):
        CredentialValue(
            name="Synthetic Credential", status="awarded", expires_at="2027-01-01T00:00:00"
        )


def test_duplicate_json_keys_are_rejected_before_model_validation(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
    with pytest.raises(DuplicateJsonKeyError, match="schema_version"):
        load_profile_json(duplicate)


def test_exported_schema_has_no_drift() -> None:
    checked_in = json.loads(
        (Path(__file__).parents[1] / "schemas" / "profile.schema.json").read_text()
    )
    assert checked_in == profile_schema()
