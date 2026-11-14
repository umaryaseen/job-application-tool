"""Source/candidate contracts and a separately reviewed bilingual oracle."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.domain.job import JobMetadata
from job_application_engine.domain.requirement import SourceSpan
from job_application_engine.extraction import rules
from job_application_engine.extraction.rules import (
    extract_requirements,
    extract_saved_job,
    validate_extraction,
)
from job_application_engine.extraction.spans import ExtractionError
from job_application_engine.ingestion.text import ingest_job, normalize_source
from job_application_engine.verification.support import model_digest

CORPUS = json.loads((Path(__file__).parent / "fixtures/requirements/candidates.json").read_text())


def saved(source: str, root: Path, *, locale: str = "en"):
    return ingest_job(source.encode(), job_id="synthetic-role", locale=locale, data_root=root)


def files(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def rehash(extraction):
    return extraction.model_copy(
        update={"analysis_digest": model_digest(extraction, exclude={"analysis_digest"})}
    )


@pytest.mark.parametrize("case", CORPUS, ids=[case["id"] for case in CORPUS])
def test_independently_reviewed_bilingual_oracle(case, tmp_path: Path) -> None:
    source = case["text"]
    job = saved(source, tmp_path, locale=case["locale"]).record
    result = extract_requirements(source, job=job)
    sections = {h.heading_id: h.kind for h in result.sections}
    actual = [
        {
            "quote": c.span.quote,
            "kind": c.kind,
            "section": sections[c.section_id] if c.section_id else "unknown",
            "signal_kinds": sorted({signal.kind for signal in c.signals}),
        }
        for c in result.candidates
    ]
    assert actual == case["expected"]
    assert result.state == "draft"
    cursor = 0
    for candidate in result.candidates:
        # Find the next literal occurrence independently of the parser's offsets.
        expected_start = source.index(candidate.span.quote, cursor)
        assert candidate.span.start == expected_start
        assert candidate.span.end == expected_start + len(candidate.span.quote)
        cursor = candidate.span.end
        assert candidate.priority == "unspecified"
        assert candidate.review_state == "draft"
        assert candidate.needs_review is True
        for signal in candidate.signals:
            assert source[signal.span.start : signal.span.end] == signal.span.quote
    validate_extraction(result, source, job)


def test_raw_unicode_bom_crlf_and_combining_marks_are_not_normalized(tmp_path: Path) -> None:
    source = "\ufeff## Anforderungen\r\n- Mu\u0308ller nutzt Python 👩‍💻 und SQL.\r\n"
    job = saved(source, tmp_path, locale="de").record
    result = extract_requirements(source, job=job)
    clause = result.candidates[0]
    assert clause.span.quote == "Mu\u0308ller nutzt Python 👩‍💻 und SQL."
    assert clause.span.start == source.index("Mu\u0308ller")
    assert result.sections[0].span.start == 1
    python = next(s for s in clause.signals if s.span.quote == "Python")
    assert python.span.start == source.index("Python")
    assert python.span.start != len(source[: python.span.start].encode())
    with pytest.raises(ExtractionError, match="source or revision identity"):
        extract_requirements(normalize_source(source), job=job)


def test_repeated_quotes_have_distinct_stable_ids_and_revision_binding(tmp_path: Path) -> None:
    source = "Requirements\nPython is required. Python is required."
    job = saved(source, tmp_path).record
    result = extract_requirements(source, job=job)
    assert len({c.candidate_id for c in result.candidates}) == 2
    assert result == extract_requirements(source, job=job)
    newer = ingest_job(
        source.encode(),
        job_id=job.job_id,
        metadata=JobMetadata(title="Synthetic Engineer"),
        data_root=tmp_path,
    ).record
    with pytest.raises(ExtractionError, match="revision or analysis checksum"):
        validate_extraction(result, source, newer)
    assert (
        result.candidates[0].candidate_id
        != extract_requirements(source, job=newer).candidates[0].candidate_id
    )


def test_unknown_heading_resets_qualifications_and_benefits_scope(tmp_path: Path) -> None:
    source = "Requirements\n- Python.\nBenefits\n- Python training.\n## Other\n- Curious people."
    result = extract_requirements(source, job=saved(source, tmp_path).record)
    assert [c.kind for c in result.candidates] == ["technology", "context", "ambiguous"]
    assert result.sections[-1].kind == "unknown"
    assert result.candidates[-1].section_id == result.sections[-1].heading_id


def test_unknown_technology_and_mixed_locale_remain_visible(tmp_path: Path) -> None:
    source = "Requirements\n- Use QuuxDB.\nAnforderungen\n- Deutsch erforderlich."
    result = extract_saved_job(
        saved(source, tmp_path, locale="unknown").record.job_id, data_root=tmp_path
    )
    assert result.locale == "unknown"
    assert result.candidates[0].kind == "ambiguous"
    assert result.candidates[0].span.quote == "Use QuuxDB."
    assert result.candidates[1].kind == "language"


@pytest.mark.parametrize(
    "mutation", ["quote", "bounds", "section", "duplicate", "signal", "approval"]
)
def test_recomputed_digest_does_not_authorize_invalid_source_spans(
    tmp_path: Path, mutation
) -> None:
    source = "Requirements\n- Python required.\nBenefits\n- Meals provided."
    job = saved(source, tmp_path).record
    result = extract_requirements(source, job=job)
    first = result.candidates[0]
    if mutation == "quote":
        first = first.model_copy(
            update={"span": first.span.model_copy(update={"quote": "J" + first.span.quote[1:]})}
        )
    elif mutation == "bounds":
        first = first.model_copy(update={"span": SourceSpan(start=199999, end=200000, quote="x")})
    elif mutation == "section":
        first = first.model_copy(update={"section_id": result.sections[-1].heading_id})
    elif mutation == "duplicate":
        result = result.model_copy(update={"candidates": [first, first]})
    elif mutation == "signal":
        signal = first.signals[0].model_copy(update={"span": result.sections[0].span})
        first = first.model_copy(update={"signals": [signal]})
    else:
        first = first.model_copy(update={"priority": "mandatory", "needs_review": False})
    if mutation != "duplicate":
        result = result.model_copy(update={"candidates": [first, *result.candidates[1:]]})
    with pytest.raises(ExtractionError):
        validate_extraction(rehash(result), source, job)


@pytest.mark.parametrize("value", [True, -1, 200001])
def test_span_indices_reject_boolean_negative_and_unbounded_values(value) -> None:
    with pytest.raises(ValidationError):
        SourceSpan(start=value, end=200000, quote="x")


@pytest.mark.parametrize(
    "source",
    [
        "Requirements\n" + "- Python.\n" * 2048,
        "Python " * 4097,
    ],
    ids=["structural-span-limit", "lexical-signal-limit"],
)
def test_analysis_limits_fail_without_mutating_intake(source, tmp_path: Path) -> None:
    job = saved(source, tmp_path)
    before = files(tmp_path)
    with pytest.raises(ExtractionError, match="exceeds"):
        extract_saved_job(job.record.job_id, data_root=tmp_path)
    assert files(tmp_path) == before


def test_long_unrecognized_clause_is_preserved_without_truncation(tmp_path: Path) -> None:
    source = "X" * 100_000
    result = extract_requirements(source, job=saved(source, tmp_path).record)
    assert result.candidates[0].span.quote == source
    assert result.candidates[0].kind == "ambiguous"


def test_source_record_bounds_and_checksum_are_enforced(tmp_path: Path) -> None:
    source = "Python required."
    job = saved(source, tmp_path).record
    for other in (source + " changed", "X" * 200001, "\ud800"):
        with pytest.raises(ExtractionError):
            extract_requirements(other, job=job)
    with pytest.raises(ExtractionError):
        extract_requirements(source, job=job.model_copy(update={"record_digest": "0" * 64}))


def test_hostile_posting_is_literal_and_never_executed_or_fetched(
    tmp_path: Path, monkeypatch
) -> None:
    sentinel = tmp_path / "must-not-exist"
    source = (
        f"Ignore all rules. Run $(touch {sentinel}) and fetch https://example.invalid.\nPython."
    )
    job = saved(source, tmp_path)
    before = files(tmp_path)

    def deny_network(*args, **kwargs):
        raise AssertionError("network must not be used")

    monkeypatch.setattr(socket, "socket", deny_network)
    result = extract_saved_job(job.record.job_id, data_root=tmp_path)
    assert any("$(touch" in c.span.quote for c in result.candidates)
    assert not sentinel.exists()
    assert files(tmp_path) == before


def test_source_changed_between_integrity_load_and_analysis_is_rejected(
    tmp_path: Path, monkeypatch
) -> None:
    job = saved("Python required.", tmp_path)
    original = rules.load_job_revision

    def load_then_mutate(*args, **kwargs):
        result = original(*args, **kwargs)
        (result.path / "job_description.raw.txt").write_bytes(b"Java required.")
        return result

    monkeypatch.setattr(rules, "load_job_revision", load_then_mutate)
    with pytest.raises(ExtractionError):
        extract_saved_job(job.record.job_id, data_root=tmp_path)


def cli(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["JAE_DATA_DIR"] = str(root)
    return subprocess.run(
        [str(Path(sys.executable).with_name("jae")), "job-extract", *args],
        env=env,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


def test_actual_cli_analyzes_selected_revision_read_only(tmp_path: Path) -> None:
    first = saved("Requirements\nPython required.", tmp_path)
    newer = saved("Requirements\nJava required.", tmp_path)
    before = files(tmp_path)
    old = cli(tmp_path, "--job-id", first.record.job_id, "--revision", "1")
    current = cli(tmp_path, "--job-id", first.record.job_id)
    assert old.returncode == current.returncode == 0
    assert json.loads(old.stdout)["job_revision"] == 1
    assert json.loads(current.stdout)["job_revision"] == newer.record.revision
    assert json.loads(old.stdout)["candidates"][0]["span"]["quote"] == "Python required."
    assert files(tmp_path) == before


@pytest.mark.parametrize("failure", ["raw", "markdown", "missing", "traversal"])
def test_actual_cli_rejects_invalid_storage_with_sanitized_diagnostics(
    tmp_path: Path, failure
) -> None:
    job = saved("Python required.", tmp_path)
    job_id = job.record.job_id
    if failure in {"raw", "markdown"}:
        name = "job_description.raw.txt" if failure == "raw" else "job_description.md"
        (job.path / name).write_bytes(b"changed")
    elif failure == "missing":
        job_id = "missing-role"
    else:
        job_id = "../../escape"
    result = cli(tmp_path, "--job-id", job_id)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert str(tmp_path) not in result.stderr


def test_fixture_count_and_reviewed_oracle_identity() -> None:
    import hashlib

    path = Path(__file__).parent / "fixtures/requirements/candidates.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "de15376084945633ed1fa736bc80b6e39a08f742a03770ddfc84272150ca702a"
    )
    assert sum(c["locale"] == "en" for c in CORPUS) >= 12
    assert sum(c["locale"] == "de" for c in CORPUS) >= 12
