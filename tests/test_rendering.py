"""Synthetic production RenderCV adapter tests."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).parents[1]))

from experiments.renderer.prepare_cases import add_approved_variants
from experiments.renderer.runner.render_experiment import normalize_extracted_text
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import fact_approval_from_review, record_human_review
from job_application_engine.rendering import pdf
from job_application_engine.rendering.pdf import PdfRenderError, build_pdf
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.document import (
    DocumentValidationError,
    document_plan_digest,
)
from job_application_engine.verification.support import (
    canonical_fact_payload,
    canonical_json,
    fact_digest,
)
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix import supported_project_profile


def _revisioned_project_body(
    profile: object, reviews: list[object], description: str
) -> tuple[object, list[object], dict[tuple[str, int], bytes]]:
    """Create a reviewed synthetic project revision with a long body claim."""

    current = profile
    project = next(item for item in current.facts if item.fact_id == "project-two")
    binding = next(item for item in current.support_bindings if item.fact_id == "project-two")
    revised = project.model_copy(
        update={
            "revision": 2,
            "description": description,
            "support_binding_refs": ["binding-project-two-r2"],
            "approval": project.approval,
        }
    )
    revised_binding = binding.model_copy(
        update={
            "binding_id": "binding-project-two-r2",
            "fact_revision": 2,
            "fact_sha256": fact_digest(revised),
        }
    )
    current = current.model_copy(
        update={
            "facts": [revised if item.fact_id == "project-two" else item for item in current.facts],
            "support_bindings": [
                revised_binding if item.fact_id == "project-two" else item
                for item in current.support_bindings
            ],
        }
    )
    receipt = record_human_review(
        current,
        target_type="fact",
        target_id="project-two",
        target_revision=2,
        displayed_content=canonical_json(canonical_fact_payload(revised)),
        review_id="review-project-two-r2",
        reviewer_id="synthetic-reviewer",
        reviewed_at=datetime(2026, 9, 12, 13, tzinfo=UTC),
    )
    current = current.model_copy(
        update={
            "facts": [
                item.model_copy(update={"approval": fact_approval_from_review(receipt)})
                if item.fact_id == "project-two"
                else item
                for item in current.facts
            ]
        }
    )
    return (
        current,
        [*reviews, receipt],
        {("project-document", 1): b"synthetic documentary project capture\n"},
    )


def _extracted_texts(pdf: Path) -> tuple[str, str]:
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    pypdf = "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    return poppler, pypdf


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
            else "Synthetic long approved statement " + "with deterministic wrapping " * 18
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
    assert pages == 2
    recovered = subprocess.run(
        ["pdftotext", "-layout", str(output), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "determin-" not in recovered
    assert normalize_extracted_text(recovered) == normalize_extracted_text(expected)
    from pypdf import PdfReader

    pypdf_recovered = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)
    assert "determin-" not in pypdf_recovered
    assert normalize_extracted_text(pypdf_recovered) == normalize_extracted_text(expected)


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_production_pdf_preserves_url_and_hyphenation_sensitive_words(
    tmp_path: Path,
) -> None:
    profile, reviews = approved_baseline()
    claim = (
        "https://example.invalid/profile/maintainability-and-modularity "
        "validation maintainability modularity"
    )
    profile, reviews = add_approved_variants(profile, reviews, [("url-wrap", claim)])
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    output = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(output), "-"], capture_output=True, text=True, check=True
    ).stdout
    from pypdf import PdfReader

    pypdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)
    for recovered in (poppler, pypdf_text):
        normalized = normalize_extracted_text(recovered)
        assert normalized == normalize_extracted_text(expected)
        assert "https://example.invalid/profile/maintainability-and-modularity" in normalized
        assert "validation maintainability modularity" in normalized


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_literal_hyphen_compounds_are_complete_in_summary_and_project_body(
    tmp_path: Path,
) -> None:
    profile, reviews, captures = supported_project_profile()
    profile, reviews, captures = _revisioned_project_body(
        profile,
        reviews,
        "Synthetic project result for bounded data-processing and operational workflows using "
        + "reliable service " * 5
        + "cost-forensics tool.",
    )
    profile, reviews = add_approved_variants(
        profile,
        reviews,
        [
            (
                "hyphen-summary",
                "Synthetic engineer with 5+ years of experience. Background in backend systems "
                "and full-stack applications.",
            )
        ],
    )
    plan = compile_baseline(
        profile, as_of=date(2026, 9, 12), reviews=reviews, support_captures=captures
    )
    output = build_pdf(
        plan,
        profile,
        reviews=reviews,
        support_captures=captures,
        data_root=tmp_path,
    )
    assert len(PdfReader(output).pages) == 2
    expected = render_text(plan, profile, reviews=reviews, support_captures=captures)
    poppler, pypdf = _extracted_texts(output)
    for recovered in (poppler, pypdf):
        normalized = normalize_extracted_text(recovered)
        assert normalized == normalize_extracted_text(expected)
        assert "full-stack applications" in normalized
        assert "cost-forensics tool" in normalized
        with pytest.raises(AssertionError):
            assert normalized == normalize_extracted_text(
                expected.replace("full-stack", "full stack")
            )
        with pytest.raises(AssertionError):
            assert normalized == normalize_extracted_text(
                expected.replace("cost-forensics", "cost forensics")
            )
        with pytest.raises(AssertionError):
            assert normalized == normalize_extracted_text(
                expected.replace("full-stack applications", "full-stack application")
            )
        with pytest.raises(AssertionError):
            assert normalized == normalize_extracted_text(
                expected.replace("cost-forensics tool", "cost-forensics tooling")
            )


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_unbreakable_hyphenated_compound_fails_before_publication(tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    profile, reviews = add_approved_variants(
        profile,
        reviews,
        [("hyphen-overflow", "synthetic-" * 200 + "end")],
    )
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    with pytest.raises(PdfRenderError, match="hyphenated compound.*fixed A4"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


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
    # Simulate the subprocess failure, including on hosts without macOS isolation.
    # No renderer is executed by this unit test.
    monkeypatch.setattr(pdf, "_sandbox_executable", lambda: "sandbox-exec")
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
    monkeypatch.setattr(pdf, "_sandbox_executable", lambda: "sandbox-exec")
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
