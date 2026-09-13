"""TASK-007 checks run against real PDF bytes, with independent expectations."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from job_application_engine.ats_qa import pdf
from job_application_engine.ats_qa.report import QAReport, record_visual_observation
from job_application_engine.ats_qa.text import normalize_extracted_text
from tests.rendering.fixtures import ORACLES, adversarial_pdf, expected, production_pdf


def measure(path: Path, oracle: str = "adversarial") -> QAReport:
    return pdf.run_pdf_qa(
        path,
        expected(oracle),
        report_path=path.parent / "qa.json",
        raster_dir=path.parent / "rasters",
    )


def statuses(report: QAReport) -> dict[str, str]:
    return {check.check_id: check.status for check in report.checks}


@pytest.mark.parametrize("two_pages", [False, True])
def test_real_production_pdf_complete_content_and_geometry(tmp_path: Path, two_pages: bool) -> None:
    path = production_pdf(tmp_path, two_pages=two_pages)
    report = measure(path, "two-page" if two_pages else "one-page")
    assert all(check.status == "pass" for check in report.checks), report.model_dump_json(indent=2)
    assert report.overall_status == "not_checked"  # Raster generation cannot approve visuals.
    assert report.visual_review.reviewer_id is None
    assert len(list((path.parent / "rasters").glob("*.png"))) == (2 if two_pages else 1)
    for engine in ("poppler", "pypdf"):
        critical = next(c for c in report.checks if c.check_id == f"critical_fields_{engine}")
        assert critical.measured == {"found": 19, "total": 19, "fraction": 1.0}
    saved = QAReport.model_validate_json((path.parent / "qa.json").read_text())
    assert saved.model_dump(mode="json") == report.model_dump(mode="json")
    assert "synthetic@example.com" not in saved.model_dump_json()


@pytest.mark.parametrize(
    "mutation,check_ids",
    [
        (
            "wrong_order",
            [
                "complete_text_poppler",
                "complete_text_pypdf",
                "entry_claim_sequence_poppler",
                "entry_claim_sequence_pypdf",
            ],
        ),
        ("duplicate", ["complete_text_poppler", "complete_text_pypdf"]),
        ("missing", ["complete_text_poppler", "complete_text_pypdf", "critical_fields_poppler"]),
        ("suffix_loss", ["complete_text_poppler", "complete_text_pypdf"]),
        (
            "qualification",
            ["complete_text_poppler", "complete_text_pypdf", "critical_fields_pypdf"],
        ),
        (
            "numeric_punctuation",
            ["quantitative_punctuation_poppler", "quantitative_punctuation_pypdf"],
        ),
        ("lost_date", ["critical_fields_poppler", "critical_fields_pypdf"]),
        ("wrong_scope", ["critical_fields_poppler", "critical_fields_pypdf"]),
        ("unexpected", ["complete_text_poppler", "complete_text_pypdf"]),
        ("heading", ["standard_headings_poppler", "standard_headings_pypdf"]),
        ("hidden", ["visibility_operators"]),
        ("clip", ["visibility_operators"]),
        ("overflow", ["complete_text_poppler", "text_geometry"]),
        ("dimensions", ["a4_dimensions"]),
        ("empty", ["complete_text_poppler", "complete_text_pypdf", "text_geometry"]),
        ("image_only", ["complete_text_poppler", "complete_text_pypdf", "text_geometry"]),
    ],
)
def test_actual_negative_pdf_fails_for_intended_reason(
    tmp_path: Path, mutation: str, check_ids: list[str]
) -> None:
    report = measure(adversarial_pdf(tmp_path / "negative.pdf", mutation))
    result = statuses(report)
    assert report.overall_status == "fail"
    assert {key: result[key] for key in check_ids} == dict.fromkeys(check_ids, "fail")
    if mutation == "hidden":
        assert result["complete_text_pypdf"] == "pass"  # Extraction alone misses invisibility.
    if mutation == "wrong_scope":
        assert (
            result["quantitative_punctuation_pypdf"] == "pass"
        )  # Global presence is insufficient.


def test_adversarial_control_is_valid_and_empty_denominators_are_null(tmp_path: Path) -> None:
    report = measure(adversarial_pdf(tmp_path / "control.pdf"))
    assert all(c.status == "pass" for c in report.checks), report.model_dump_json(indent=2)
    assert (
        next(c for c in report.checks if c.check_id == "unicode_pypdf").measured["fraction"] is None
    )


@pytest.mark.parametrize("tool", ["pdftotext", "pdftoppm", "sandbox-exec", "pypdf"])
def test_missing_tool_is_not_a_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tool: str
) -> None:
    path = adversarial_pdf(tmp_path / "control.pdf")
    original = pdf.shutil.which
    monkeypatch.setattr(pdf.shutil, "which", lambda name: None if name == tool else original(name))
    if tool == "pypdf":

        def absent(_: str) -> str:
            raise pdf.PackageNotFoundError

        monkeypatch.setattr(pdf, "version", absent)
    report = measure(path)
    assert report.overall_status == "not_checked"
    assert any(c.mandatory and c.status == "not_checked" for c in report.checks)
    observed = record_visual_observation(
        report,
        path,
        reviewer_id="synthetic-test",
        status="pass",
        notes="Test of aggregation only; not a real visual review.",
    )
    assert observed.overall_status == "not_checked"


@pytest.mark.parametrize("failure", ["timeout", "exit", "invalid_output"])
def test_failed_measurement_process_cannot_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    path = adversarial_pdf(tmp_path / "control.pdf")
    original = pdf.subprocess.run

    def failed(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "-v" in command:
            return original(command, **kwargs)
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 30)
        return subprocess.CompletedProcess(
            command, 5 if failure == "exit" else 0, "not valid output", ""
        )

    monkeypatch.setattr(pdf.subprocess, "run", failed)
    report = measure(path)
    assert report.overall_status == "fail"
    assert statuses(report)["complete_text_pypdf"] == "fail"
    assert list(tmp_path.glob(".qa-*")) == []


def test_visual_observation_is_explicit_and_hash_bound(tmp_path: Path) -> None:
    path = adversarial_pdf(tmp_path / "control.pdf")
    report = measure(path)
    assert report.visual_review.status == "not_checked"
    with pytest.raises(ValueError):
        record_visual_observation(
            report, path, reviewer_id="", status="pass", notes="Invalid identity"
        )
    recorded = record_visual_observation(
        report,
        path,
        reviewer_id="synthetic-test",
        status="warn",
        notes="Test-only observation; manual inspection still pending.",
    )
    assert recorded.overall_status == "warn"
    assert recorded.visual_review.artifact_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    path.write_bytes(path.read_bytes() + b"\n% changed")
    with pytest.raises(ValueError, match="changed"):
        record_visual_observation(
            report, path, reviewer_id="synthetic-test", status="pass", notes="stale"
        )


def test_normalization_is_exact_reviewed_policy() -> None:
    from experiments.renderer.runner.render_experiment import normalize_extracted_text as reviewed

    for value in [
        "Größe\nÄ Ö Ü ß",
        "https:/ /\nexample.invalid",
        "2020\u00ad01",
        "qualifi\u00ad\ncation",
        "1.5 1,5 30% 30 percentage points not",
        "Müller İpek Łukasz François",
    ]:
        assert normalize_extracted_text(value) == reviewed(value)
    assert normalize_extracted_text("1.5") != normalize_extracted_text("15")
    assert normalize_extracted_text("not expert") != normalize_extracted_text("expert")


def test_qa_module_command_records_unchecked_visuals(tmp_path: Path) -> None:
    import os

    adversarial_pdf(tmp_path / "input.pdf")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "job_application_engine.ats_qa",
            "--pdf",
            "input.pdf",
            "--expected",
            str(ORACLES / "adversarial.json"),
            "--output",
            "qa",
        ],
        env={**os.environ, "JAE_DATA_DIR": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    data = json.loads((tmp_path / "qa" / "report.json").read_text())
    assert data["overall_status"] == "not_checked"
