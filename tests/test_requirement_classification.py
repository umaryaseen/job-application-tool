"""TASK-012 priority/negation/alternative labels against a separately reviewed oracle."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.domain.job import JobMetadata
from job_application_engine.domain.requirement import (
    ClassifiedCandidate,
    ConditionGroup,
    SourceSpan,
    Threshold,
)
from job_application_engine.extraction.classification import (
    classify_requirements,
    classify_saved_job,
    validate_classification,
)
from job_application_engine.extraction.rules import extract_requirements
from job_application_engine.extraction.spans import ExtractionError
from job_application_engine.ingestion.text import ingest_job
from job_application_engine.verification.support import model_digest

FIXTURE = Path(__file__).parent / "fixtures/requirements/classification.json"
CORPUS = json.loads(FIXTURE.read_text(encoding="utf-8"))


def saved(source: str, root: Path, *, locale: str = "en"):
    return ingest_job(source.encode(), job_id="synthetic-role", locale=locale, data_root=root)


def analyze(source: str, root: Path, *, locale: str = "en"):
    job = saved(source, root, locale=locale).record
    extraction = extract_requirements(source, job=job)
    return job, extraction, classify_requirements(extraction, source, job=job)


def files(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def condition(node):
    if node is None:
        return None
    if isinstance(node, ConditionGroup):
        return {node.node: [condition(child) for child in node.children]}
    return node.span.quote


def threshold(item: Threshold) -> dict[str, object]:
    result: dict[str, object] = {"measure": item.measure, "operator": item.operator}
    if item.measure == "duration":
        result |= {"value": item.value, "unit": item.unit}
        if item.upper is not None:
            result["upper"] = item.upper
    else:
        result |= {"level": item.level, "unit": item.unit}
        if item.upper_level is not None:
            result["upper_level"] = item.upper_level
    result["scope"] = item.scope.quote if item.scope else None
    return result


def rehash(classification):
    return classification.model_copy(
        update={
            "classification_digest": model_digest(classification, exclude={"classification_digest"})
        }
    )


def all_spans(row: ClassifiedCandidate) -> list[SourceSpan]:
    spans = [cue.span for cue in row.cues] + list(row.negation_spans)
    stack = [row.condition] if row.condition else []
    while stack:
        node = stack.pop()
        spans.append(node.span)
        if isinstance(node, ConditionGroup):
            spans.extend(node.connectives)
            stack.extend(node.children)
    for item in row.thresholds:
        spans.extend([item.span, *([item.scope] if item.scope else [])])
    return spans


@pytest.mark.parametrize("case", CORPUS, ids=[case["id"] for case in CORPUS])
def test_independently_reviewed_bilingual_oracle(case, tmp_path: Path) -> None:
    source = case["text"]
    job, extraction, result = analyze(source, tmp_path, locale=case["locale"])
    actual = [
        {
            "quote": row.span.quote,
            "role": row.role,
            "priority": row.priority,
            "basis": row.basis,
            "negation": row.negation,
            "condition": condition(row.condition),
            "thresholds": [threshold(item) for item in row.thresholds],
            "review_reasons": list(row.review_reasons),
        }
        for row in result.candidates
    ]
    assert actual == case["expected"]
    ids = [row.candidate_id for row in result.candidates]
    assert [[ids.index(m) for m in g.candidate_ids] for g in result.duplicates] == case[
        "duplicates"
    ]
    assert result.state == "draft"
    for row in result.candidates:
        assert row.review_state == "draft"
        assert row.needs_review is bool(row.review_reasons)
        for span in all_spans(row):
            assert source[span.start : span.end] == span.quote
    validate_classification(result, extraction, source, job)


def test_fixture_identity_and_required_coverage() -> None:
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert digest == "16b05e8f0f6f1a8d274de6b06e9eacf08fc3af47d6a802fd564537d4be5b18d1"
    assert sum(c["locale"] == "en" for c in CORPUS) >= 12
    assert sum(c["locale"] == "de" for c in CORPUS) >= 12
    rows = [row for case in CORPUS for row in case["expected"]]
    assert {r["priority"] for r in rows} == {"mandatory", "preferred", "unspecified"}
    assert {r["negation"] for r in rows} == {"none", "requirement_negated", "unsupported"}
    assert {"clause_conflicts_with_heading", "conflicting_clause_cues"} <= {
        r["basis"] for r in rows
    }
    assert any(c["duplicates"] for c in CORPUS)


@pytest.mark.parametrize(
    "source",
    [
        "Requirements\nPython or Go is required.",
        "Requirements\nPython, Java or Rust is required.",
        "Requirements\nPython and Java or Go is required.",
        "Anforderungen\nPython oder Rust ist erforderlich.",
        "Requirements\nPython/Java is required.",
        "Requirements\nA degree in Physics or Chemistry is required.",
        "Requirements\nPython is required, alternatively Java.",
    ],
)
def test_or_is_never_split_into_partial_or_mandatory_conditions(source, tmp_path: Path) -> None:
    _, _, result = analyze(source, tmp_path)
    row = result.candidates[0]
    assert row.condition is None
    assert row.needs_review
    assert {"unparsed_alternative", "unsupported_grouping"} & set(row.review_reasons)


@pytest.mark.parametrize(
    "source",
    [
        "Nice to have:\n- Python is required.\n- Docker.\n- German is not required.",
        "Wünschenswert:\n- Python ist zwingend erforderlich.\n- Docker.",
        "Requirements\nNice to have\n- AWS must be known.\n- Docker.",
        "Preferred qualifications:\n- Must speak German.\n- Kubernetes.",
    ],
)
def test_preferred_scope_never_becomes_mandatory(source, tmp_path: Path) -> None:
    _, _, result = analyze(source, tmp_path)
    assert all(row.priority != "mandatory" for row in result.candidates)
    explicit = [row for row in result.candidates if row.basis == "clause_conflicts_with_heading"]
    assert explicit and all(r.needs_review for r in explicit)


def test_section_cues_are_evidence_not_certainty(tmp_path: Path) -> None:
    source = "Requirements\n- Python.\n## Benefits\n- German lessons are required.\n"
    _, _, result = analyze(source, tmp_path)
    python, benefit = result.candidates
    assert (python.priority, python.basis) == ("unspecified", "no_priority_cue")
    assert (benefit.role, benefit.priority) == ("non_requirement", "unspecified")
    assert benefit.review_reasons == ["cue_outside_requirement_section"]


def test_conflicting_heading_cues_supply_no_priority(tmp_path: Path) -> None:
    source = "Must have or nice to have:\n- Docker."
    _, _, result = analyze(source, tmp_path)
    row = result.candidates[0]
    assert row.priority == "unspecified"
    assert "conflicting_heading_cues" in row.review_reasons


def test_marker_scope_ends_at_next_heading(tmp_path: Path) -> None:
    source = "Requirements\nNice to have\n- Docker.\nQualifications\n- Kubernetes."
    _, _, result = analyze(source, tmp_path)
    priorities = [(r.span.quote, r.priority) for r in result.candidates]
    assert priorities == [
        ("Nice to have", "unspecified"),
        ("Docker.", "preferred"),
        ("Kubernetes.", "unspecified"),
    ]


@pytest.mark.parametrize(
    ("source", "reason"),
    [
        ("Requirements\nMore than 3+ years of Python experience.", "unsupported_number"),
        ("Requirements\nAt least 3-5 years of experience.", "unsupported_number"),
        ("Requirements\n5-3 years of experience.", "unsupported_number"),
        ("Requirements\nGerman B2-C1 or higher.", "unsupported_number"),
        ("Requirements\nMany years of Python experience.", "vague_quantity"),
        ("Requirements\nGerman C1 and English C1.", "threshold_scope_unclear"),
    ],
)
def test_unsupported_numeric_grammar_needs_review(source, reason, tmp_path: Path) -> None:
    _, _, result = analyze(source, tmp_path)
    assert reason in result.candidates[0].review_reasons


def test_supported_numeric_operators(tmp_path: Path) -> None:
    source = (
        "Requirements\n- More than 2 years of SQL experience.\n- 6+ months of AWS experience.\n"
        "- German B1-B2.\n- English C1+."
    )
    _, _, result = analyze(source, tmp_path)
    found = [threshold(t) for row in result.candidates for t in row.thresholds]
    assert found == [
        {"measure": "duration", "operator": "gt", "value": 2, "unit": "years",
         "scope": "SQL experience"},
        {"measure": "duration", "operator": "gte", "value": 6, "unit": "months",
         "scope": "AWS experience"},
        {"measure": "language_level", "operator": "range", "level": "B1", "unit": "cefr",
         "upper_level": "B2", "scope": "German"},
        {"measure": "language_level", "operator": "gte", "level": "C1", "unit": "cefr",
         "scope": "English"},
    ]  # fmt: skip


def test_parenthesized_and_both_groups(tmp_path: Path) -> None:
    source = "Requirements\n- Python and (Django or Flask).\n- Both Docker and Kubernetes."
    _, _, result = analyze(source, tmp_path)
    assert [condition(r.condition) for r in result.candidates] == [
        {"all": ["Python", {"any": ["Django", "Flask"]}]},
        {"all": ["Docker", "Kubernetes"]},
    ]


def test_relabelled_or_invented_classification_fails_even_with_new_digest(
    tmp_path: Path,
) -> None:
    source = "Nice to have:\n- Python or Java.\n- Docker."
    job, extraction, result = analyze(source, tmp_path)
    validate_classification(result, extraction, source, job)
    first = result.candidates[0]
    forged_priority = first.model_copy(
        update={
            "priority": "mandatory",
            "basis": "explicit_mandatory_cue",
            "cues": [
                first.cues[0].model_copy(update={"level": "mandatory"}),
            ],
        }
    )
    assert first.condition is not None and isinstance(first.condition, ConditionGroup)
    split = first.model_copy(update={"condition": first.condition.children[0]})
    invented = SourceSpan(start=first.span.start, end=first.span.start + 6, quote="Golang")
    bad_span = first.model_copy(
        update={"negation_spans": [invented], "negation": "unsupported",
                "review_reasons": ["unsupported_negation"], "needs_review": True}
    )  # fmt: skip
    for row in (forged_priority, split, bad_span):
        forged = rehash(result.model_copy(update={"candidates": [row, *result.candidates[1:]]}))
        with pytest.raises(ExtractionError):
            validate_classification(forged, extraction, source, job)


def test_classification_is_bound_to_revision_and_extraction(tmp_path: Path) -> None:
    source = "Requirements\nPython is required."
    job, extraction, result = analyze(source, tmp_path)
    assert result == classify_requirements(extraction, source, job=job)
    newer = ingest_job(
        source.encode(),
        job_id=job.job_id,
        metadata=JobMetadata(title="Synthetic Engineer"),
        data_root=tmp_path,
    ).record
    assert newer.revision == job.revision + 1
    with pytest.raises(ExtractionError):
        validate_classification(result, extract_requirements(source, job=newer), source, newer)
    stale = rehash(result.model_copy(update={"extraction_digest": "0" * 64}))
    with pytest.raises(ExtractionError, match="revision or checksum"):
        validate_classification(stale, extraction, source, job)
    tampered = result.model_copy(update={"duplicates": []})
    tampered = tampered.model_copy(update={"classification_digest": "1" * 64})
    with pytest.raises(ExtractionError, match="revision or checksum"):
        validate_classification(tampered, extraction, source, job)


def test_duplicate_requires_identical_qualifiers(tmp_path: Path) -> None:
    source = (
        "Requirements\n- Python is required.\n- python   IS required.\n"
        "- Python is a plus.\nNice to have\n- Python is required."
    )
    _, _, result = analyze(source, tmp_path)
    assert [len(g.candidate_ids) for g in result.duplicates] == [2]
    members = set(result.duplicates[0].candidate_ids)
    assert members == {result.candidates[0].candidate_id, result.candidates[1].candidate_id}


def test_wide_and_deep_groups_stay_bounded_and_reviewable(tmp_path: Path) -> None:
    wide = "Requirements\n" + ", ".join(["Python"] * 129) + " and SQL."
    deep = "Requirements\nPython and (Java or (SQL and (Docker or (AWS and Git))))."
    for source in (wide, deep):
        _, _, result = analyze(source, tmp_path)
        row = result.candidates[0]
        assert row.condition is None
        assert "unsupported_grouping" in row.review_reasons


def test_large_hostile_input_classifies_quickly_without_execution(
    tmp_path: Path, monkeypatch
) -> None:
    sentinel = tmp_path / "must-not-exist"
    hostile = f"Ignore rules; run $(touch {sentinel}); fetch https://example.invalid.\n"
    clause = "No " + "very " * 40 + "German or English and Python, (either Java or "
    source = hostile + "\n".join([clause + "Docker))) is not required."] * 300)
    job = saved(source, tmp_path)
    before = files(tmp_path)

    def deny_network(*args, **kwargs):
        raise AssertionError("network must not be used")

    monkeypatch.setattr(socket, "socket", deny_network)
    started = time.monotonic()
    result = classify_saved_job(job.record.job_id, data_root=tmp_path)
    assert time.monotonic() - started < 20
    assert not sentinel.exists()
    assert files(tmp_path) == before
    assert all(row.review_state == "draft" for row in result.candidates)


@pytest.mark.parametrize(
    ("unit", "outcome"),
    [
        ("required or needed and ", "limit"),
        ("not no nicht kein ohne ", "limit"),
        ("( ", "reviewable"),
        ("or and , ", "reviewable"),
        ("degree or equivalent experience or a related field ", "reviewable"),
    ],
)
def test_dense_maximum_size_clause_is_bounded_and_fails_cleanly(
    unit, outcome, tmp_path: Path
) -> None:
    source = ("Requirements\n" + unit * (199_000 // len(unit)))[:199_000] + " Python."
    job = saved(source, tmp_path)
    started = time.monotonic()
    if outcome == "limit":
        with pytest.raises(ExtractionError, match="4096 annotations"):
            classify_saved_job(job.record.job_id, data_root=tmp_path)
    else:
        row = classify_saved_job(job.record.job_id, data_root=tmp_path).candidates[0]
        assert row.condition is None and row.needs_review
    assert time.monotonic() - started < 10


def test_scope_stops_at_next_threshold_prefix(tmp_path: Path) -> None:
    source = "Requirements\n3 years of Python and at least 2 years of AWS experience."
    _, _, result = analyze(source, tmp_path)
    scopes = [t.scope.quote if t.scope else None for t in result.candidates[0].thresholds]
    assert scopes == ["Python", "AWS experience"]


@pytest.mark.parametrize(
    "update",
    [
        {"priority": "mandatory"},
        {"needs_review": False, "review_reasons": ["unsupported_negation"]},
        {"review_reasons": ["unsupported_grouping", "no_supported_condition"]},
        {"basis": "priority_marker"},
        {"role": "non_requirement", "basis": "priority_marker"},
        {"role": "priority_marker", "basis": "priority_marker", "negation": "unsupported"},
    ],
)
def test_row_labels_must_be_internally_consistent(update) -> None:
    base = {
        "candidate_id": "req-abc",
        "kind": "technology",
        "span": {"start": 0, "end": 6, "quote": "Python"},
        "role": "requirement",
        "priority": "unspecified",
        "basis": "no_priority_cue",
        "negation": "none",
        "needs_review": True,
        "review_reasons": ["no_supported_condition"],
    }
    ClassifiedCandidate.model_validate(base)
    with pytest.raises(ValidationError):
        ClassifiedCandidate.model_validate(base | update)


@pytest.mark.parametrize(
    "values",
    [
        {"measure": "duration", "operator": "range", "value": 5, "upper": 3, "unit": "years"},
        {"measure": "duration", "operator": "gte", "unit": "years"},
        {"measure": "language_level", "operator": "gt", "level": "B2", "unit": "cefr"},
        {"measure": "language_level", "operator": "gte", "level": "B2", "unit": "years"},
        {"measure": "duration", "operator": "gte", "value": True, "unit": "years"},
    ],
)
def test_inconsistent_thresholds_are_rejected(values) -> None:
    span = {"span": {"start": 0, "end": 1, "quote": "x"}}
    with pytest.raises(ValidationError):
        Threshold.model_validate(values | span)


def cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["JAE_DATA_DIR"] = str(root)
    return subprocess.run(
        [str(Path(sys.executable).with_name("jae")), "job-classify", *args],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


def test_actual_cli_classifies_selected_revision_read_only(tmp_path: Path) -> None:
    first = saved("Requirements\nPython or Java is required.", tmp_path)
    saved("Nice to have:\n- Docker.", tmp_path)
    before = files(tmp_path)
    old = cli(tmp_path, "--job-id", first.record.job_id, "--revision", "1")
    current = cli(tmp_path, "--job-id", first.record.job_id)
    assert old.returncode == current.returncode == 0
    old_row = json.loads(old.stdout)["candidates"][0]
    assert (old_row["priority"], old_row["condition"]["node"]) == ("mandatory", "any")
    assert json.loads(current.stdout)["candidates"][0]["priority"] == "preferred"
    assert files(tmp_path) == before


@pytest.mark.parametrize("failure", ["raw", "missing", "traversal", "revision"])
def test_actual_cli_rejects_invalid_storage_with_sanitized_diagnostics(
    tmp_path: Path, failure
) -> None:
    job = saved("Python required.", tmp_path)
    args = ["--job-id", job.record.job_id]
    if failure == "raw":
        (job.path / "job_description.raw.txt").write_bytes(b"Java required.")
    elif failure == "missing":
        args = ["--job-id", "missing-role"]
    elif failure == "traversal":
        args = ["--job-id", "../../escape"]
    else:
        args += ["--revision", "7"]
    result = cli(tmp_path, *args)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert str(tmp_path) not in result.stderr


# Regressions for independent review round 1 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    ("source", "reason"),
    [
        ("Requirements\nPython / Rust is required.", "unparsed_alternative"),
        ("Requirements\nPython / QuuxDB is required.", "unparsed_alternative"),
        ("Requirements\nPython/QuuxDB.", "unparsed_alternative"),
        ("Requirements\nPython, QuuxDB is required.", "unsupported_grouping"),
        ("Requirements\nQuuxDB, Python is required.", "unsupported_grouping"),
        ("Anforderungen\nPython, QuuxDB ist erforderlich.", "unsupported_grouping"),
    ],
)
def test_f01_slash_or_comma_to_unrecognized_operand_is_not_partial(
    source, reason, tmp_path: Path
) -> None:
    row = analyze(source, tmp_path)[2].candidates[0]
    assert row.condition is None
    assert reason in row.review_reasons and row.needs_review


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Requirements\nCI/CD is required.", "CI/CD"),
        ("Requirements\nIdeally, Python.", "Python"),
        ("Requirements\nPython, preferably.", "Python"),
        ("Requirements\nExperience with Docker, Kubernetes, and AWS.", None),
    ],
)
def test_f01_controls_keep_supported_conditions(source, expected, tmp_path: Path) -> None:
    row = analyze(source, tmp_path)[2].candidates[0]
    assert row.condition is not None
    if expected is not None:
        assert condition(row.condition) == expected
    assert not {"unparsed_alternative", "unsupported_grouping"} & set(row.review_reasons)


@pytest.mark.parametrize(
    "source",
    [
        "Requirements\nA degree or equivalent experience or a related field.",
        "Requirements\nA degree or equivalent experience or similar field.",
        "Anforderungen\nStudium oder vergleichbare Qualifikation oder einem verwandten Fach.",
    ],
)
def test_f02_trailing_alternative_after_equivalent_is_not_dropped(source, tmp_path: Path) -> None:
    row = analyze(source, tmp_path)[2].candidates[0]
    assert row.condition is None
    assert "unparsed_alternative" in row.review_reasons


@pytest.mark.parametrize(
    "amount", ["999 years", "100 months", "1000 years", "10,000 years", "3yrs", "5 yrs"]
)
def test_f03_out_of_range_or_uncaptured_durations_need_review(amount, tmp_path: Path) -> None:
    source = f"Requirements\n{amount} of Python experience."
    row = analyze(source, tmp_path)[2].candidates[0]
    assert row.thresholds == []
    assert "unsupported_number" in row.review_reasons


def test_f03_cli_reports_review_instead_of_raw_validation_error(tmp_path: Path) -> None:
    job = saved("Requirements\n999 years of Python experience.", tmp_path)
    result = cli(tmp_path, "--job-id", job.record.job_id)
    assert result.returncode == 0, result.stderr
    assert "pydantic" not in result.stderr.casefold()
    row = json.loads(result.stdout)["candidates"][0]
    assert "unsupported_number" in row["review_reasons"]


@pytest.mark.parametrize(
    ("source", "groups"),
    [
        ("Requirements\n- Python is required.\nQualifications\n- Python is required.", 0),
        ("Requirements\n- Python is required.\n- Python is required.", 1),
        ("Requirements\n- Python is required.\nRequired\n- Python is required.", 0),
    ],
)
def test_f04_duplicates_stay_within_one_heading_scope(source, groups, tmp_path: Path) -> None:
    assert len(analyze(source, tmp_path)[2].duplicates) == groups


@pytest.mark.parametrize(
    "source",
    [
        "Requirements\nPython; QuuxDB is required.",
        "Requirements\nPython & QuuxDB is required.",
        "Requirements\nPython + QuuxDB is required.",
        "Requirements\nPython | QuuxDB is required.",
    ],
)
def test_f01_other_symbol_separators_are_not_partial(source, tmp_path: Path) -> None:
    row = analyze(source, tmp_path)[2].candidates[0]
    assert row.condition is None and row.needs_review


def test_numeric_amounts_end_scopes_and_leading_zeros_need_review(tmp_path: Path) -> None:
    source = (
        "Requirements\n- 3 years of Python experience and 1000 months of AWS.\n"
        "- 000 years of Python experience."
    )
    first, second = analyze(source, tmp_path)[2].candidates
    assert [t.scope.quote if t.scope else None for t in first.thresholds] == ["Python experience"]
    assert "unsupported_number" in first.review_reasons
    assert second.thresholds == [] and "unsupported_number" in second.review_reasons


# Regressions for independent review round 2 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    "line",
    [
        "six years of Python experience.",
        "1000-year Python experience.",
        "3-year Python experience.",
        "3 years minimum of Python experience.",
        "Up to 3 years of Python experience.",
        "About 5 years of Python experience.",
        "3 years or more of Python experience.",
        "English C2 minimum.",
        "Etwa 3 Jahre Erfahrung mit Python.",
    ],
)
def test_f05_uninterpreted_numeric_text_needs_review(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.thresholds == []
    assert row.needs_review
    assert {"unsupported_number", "unparsed_alternative"} & set(row.review_reasons)


def test_f05_scope_without_words_is_unclear(tmp_path: Path) -> None:
    row = analyze("Requirements\n3 years of.", tmp_path)[2].candidates[0]
    assert [t.scope for t in row.thresholds] == [None]
    assert "threshold_scope_unclear" in row.review_reasons


@pytest.mark.parametrize(
    "line",
    [
        "A degree; QuuxDB is required.",
        "A degree or a related field; QuuxDB is required.",
        "Bachelor's degree or equivalent experience; QuuxDB is required.",
        "Python plus QuuxDB is required.",
        "Python with QuuxDB is required.",
        "Python but QuuxDB is required.",
        "Python: QuuxDB is required.",
        "Python, preferably; QuuxDB.",
        "QuuxDB with at least 3 years of experience.",
        "Erfahrung mit Python und QuuxDB.",
    ],
)
def test_f06_f07_unrecognized_operands_never_leave_partial_conditions(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.condition is None and row.needs_review


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Strong Python skills.", "Python"),
        ("Solid knowledge of SQL is required.", "SQL"),
        ("Hands-on experience with Docker.", "Docker"),
        ("Fluent German.", "German"),
        ("Sehr gute Englischkenntnisse.", "Englischkenntnisse"),
        ("Fundierte Kenntnisse in Python sind erforderlich.", "Python"),
        ("You have good experience with Kubernetes.", "Kubernetes"),
    ],
)
def test_coverage_rule_keeps_conditions_with_only_filler(line, expected, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert condition(row.condition) == expected
    assert "uninterpreted_text" not in row.review_reasons


def test_threshold_only_scope_counts_as_interpretation(tmp_path: Path) -> None:
    row = analyze("Requirements\nAt least 3 years of QuuxDB experience.", tmp_path)[2]
    first = row.candidates[0]
    assert [t.scope.quote if t.scope else None for t in first.thresholds] == ["QuuxDB experience"]
    assert first.review_reasons == []


# Regressions for independent review round 3 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    "line",
    [
        "3 years of Python experience minimum.",
        "English B2 level minimum.",
        "About at least 3 years of Python experience.",
        "3 years of Python or Java minimum.",
        "QuuxDB with at least 3 years of experience.",
        "Mindestens 3 Jahre Erfahrung mit Python, etwa im Backend.",
    ],
)
def test_f09_stray_operators_or_unplaced_words_withhold_thresholds(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.thresholds == []
    assert row.needs_review


@pytest.mark.parametrize(
    ("line", "operator"),
    [
        ("At least 3 years of experience with Python is required.", "gte"),
        ("German at C1 level or higher is required.", "gte"),
        ("More than 2 years of SQL experience.", "gt"),
    ],
)
def test_f09_controls_keep_accepted_operator_thresholds(line, operator, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert [t.operator for t in row.thresholds] == [operator]
    assert row.review_reasons == []


# Regressions for independent review round 4 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    "line",
    [
        "A degree in Computer Science with Rust experience.",
        "A degree in Computer Science plus QuuxML.",
        "A degree, QuuxML.",
        "A degree or a related field plus QuuxML.",
        "A degree in Computer Science with Rust experience or equivalent practical experience.",
        "A degree with QuuxML or equivalent experience.",
        "Studium der Informatik mit Schwerpunkt QuuxML.",
        "Abgeschlossenes Studium der Informatik, QuuxML.",
    ],
)
def test_f11_text_after_degree_term_is_not_hidden(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.condition is None and row.needs_review


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("A completed degree in Computer Science is required.", "degree in Computer Science"),
        (
            "University degree in Business Information Systems.",
            "degree in Business Information Systems",
        ),
        (
            "Hochschulabschluss in Wirtschaftsinformatik.",
            "Hochschulabschluss in Wirtschaftsinformatik",
        ),
        (
            "Master's degree in Data Science or a related field.",
            "Master's degree in Data Science or a related field",
        ),
    ],
)
def test_f11_controls_keep_explicit_degree_terms(line, expected, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert condition(row.condition) == expected
    assert row.review_reasons == []


# Regressions for independent review round 5 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "A degree in formal language or equivalent experience.",
            {"any": ["degree in formal language", "equivalent experience"]},
        ),
        ("A degree in formal language.", "degree in formal language"),
        ("A degree in technical language.", "degree in technical language"),
        ("Studium der technischen Informatik.", "Studium der technischen Informatik"),
    ],
)
def test_f12_descriptive_field_words_stay_in_the_degree_term(
    line, expected, tmp_path: Path
) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert condition(row.condition) == expected
    assert row.review_reasons == []


@pytest.mark.parametrize(
    "line",
    [
        "A degree in the field of formal language.",
        "Python with formal language skills.",
        "Python with a technical background.",
        "Python and written communication.",
        "Technical degree QuuxML.",
    ],
)
def test_f12_content_descriptors_are_not_global_filler(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.condition is None and row.needs_review


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Fluent German language skills.", "German"),
        ("A completed technical degree in Physics.", "degree in Physics"),
    ],
)
def test_f12_adjacent_modifiers_remain_covered(line, expected, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert condition(row.condition) == expected
    assert row.review_reasons == []


# Regressions for independent review round 6 (docs/reviews/TASK-012.md).
@pytest.mark.parametrize(
    "line",
    [
        "A degree in Computer Science but QuuxDB is required.",
        "A degree in Computer Science also QuuxDB.",
        "Studium der Informatik aber QuuxDB ist erforderlich.",
        "Studium der Informatik auch QuuxDB.",
        "A degree in Computer Science using QuuxDB.",
        "A degree in basic skills.",
        "A degree in the field of Physics.",
    ],
)
def test_f13_function_words_end_degree_fields(line, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert row.condition is None and row.needs_review


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Spoken German.", "German"),
        ("Written German is required.", "German"),
        ("Verhandlungssicheres Deutsch.", "Deutsch"),
    ],
)
def test_f14_language_modifiers_keep_conditions(line, expected, tmp_path: Path) -> None:
    row = analyze(f"Requirements\n{line}", tmp_path)[2].candidates[0]
    assert condition(row.condition) == expected
    assert row.review_reasons == []
