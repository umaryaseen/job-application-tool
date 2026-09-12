"""Synthetic production RenderCV adapter tests."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from experiments.renderer.prepare_cases import add_approved_variants
from experiments.renderer.runner.render_experiment import normalize_extracted_text
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.rendering import pdf
from job_application_engine.rendering.pdf import PdfRenderError, build_pdf
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.document import (
    DocumentValidationError,
    document_plan_digest,
)
from tests.test_document_plan import approved_baseline


def _build_fixture(
    tmp_path: Path, *, long: bool = False, hostile: bool = False
) -> tuple[Path, str]:
    profile, reviews = approved_baseline()
    if long or hostile:
        text = (
            '<script>synthetic</script> #include "../sentinel" '
            '#read("../sentinel") [synthetic link](https://example.invalid) '
            "${2+2} ../../sentinel"
            if hostile
            else "Synthetic long approved statement " + "with deterministic wrapping " * 24
        )
        additions = (
            [(f"task006-extra-{index}", text) for index in range(1, 7)]
            if long
            else [("task006-extra", text)]
        )
        profile, reviews = add_approved_variants(profile, reviews, additions)
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    output = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    return output, render_text(plan, profile, reviews=reviews)


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_production_pdf_preserves_complete_unicode_content_with_two_extractors(
    tmp_path: Path,
) -> None:
    output, expected = _build_fixture(tmp_path)
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(output), "-"], capture_output=True, text=True, check=True
    ).stdout
    from pypdf import PdfReader

    pypdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)
    assert normalize_extracted_text(poppler) == normalize_extracted_text(expected)
    assert normalize_extracted_text(pypdf_text) == normalize_extracted_text(expected)
    assert "Größe Ä Ö Ü ß" in poppler


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_production_pdf_keeps_hostile_text_literal_and_does_not_read_sentinel(
    tmp_path: Path,
) -> None:
    (tmp_path / "sentinel").write_text("SECRET_SENTINEL_NOT_CLAIM_TEXT", encoding="utf-8")
    output, expected = _build_fixture(tmp_path, hostile=True)
    text = subprocess.run(
        ["pdftotext", "-layout", str(output), "-"], capture_output=True, text=True, check=True
    ).stdout
    from pypdf import PdfReader

    pypdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)
    assert normalize_extracted_text(text) == normalize_extracted_text(expected)
    assert normalize_extracted_text(pypdf_text) == normalize_extracted_text(expected)
    assert "<script>synthetic</script>" in text
    assert "SECRET_SENTINEL_NOT_CLAIM_TEXT" not in text
    assert "example.invalid" in text


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_production_pdf_handles_long_two_page_plan_without_pruning(tmp_path: Path) -> None:
    output, expected = _build_fixture(tmp_path, long=True)
    info = subprocess.run(
        ["pdfinfo", str(output)], capture_output=True, text=True, check=True
    ).stdout
    pages = int(
        next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:"))
    )
    assert pages >= 2
    recovered = subprocess.run(
        ["pdftotext", "-layout", str(output), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert normalize_extracted_text(recovered) == normalize_extracted_text(expected)


def test_tampered_plan_is_rejected_before_private_staging(tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    section = plan.sections[1]
    changed = section.lines[0].model_copy(update={"text": "Invented synthetic claim"})
    changed_plan = plan.model_copy(
        update={
            "sections": [
                item if item is not section else section.model_copy(update={"lines": [changed]})
                for item in plan.sections
            ],
            "plan_sha256": "0" * 64,
        }
    )
    changed_plan = changed_plan.model_copy(
        update={"plan_sha256": document_plan_digest(changed_plan)}
    )
    with pytest.raises(DocumentValidationError):
        build_pdf(changed_plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs").exists()


def test_isolation_unavailable_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    monkeypatch.setattr(pdf.shutil, "which", lambda _: None)
    with pytest.raises(PdfRenderError, match="network isolation"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)


def test_timeout_cleans_private_staging(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)

    original_run = pdf.subprocess.run

    def timeout(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        command = args[0] if args else kwargs.get("args")
        if isinstance(command, list) and command and command[0] == "git":
            return original_run(*args, **kwargs)
        raise subprocess.TimeoutExpired(["sandbox-exec"], 1)

    monkeypatch.setattr(pdf.subprocess, "run", timeout)
    with pytest.raises(PdfRenderError, match="timed out"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path, timeout_seconds=1)
    assert list(tmp_path.glob(".jae-pdf-*")) == []


def test_worker_failure_cleans_staging_and_publishes_no_pdf(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    original_run = pdf.subprocess.run

    def failed_worker(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        command = args[0] if args else kwargs.get("args")
        if isinstance(command, list) and command and command[0] == "git":
            return original_run(*args, **kwargs)
        return subprocess.CompletedProcess(command, 27)

    monkeypatch.setattr(pdf.subprocess, "run", failed_worker)
    with pytest.raises(PdfRenderError, match="worker exit 27"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()
    assert list(tmp_path.glob(".jae-pdf-*")) == []
