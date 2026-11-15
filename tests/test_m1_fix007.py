"""M1-FIX-007: slash-joined compounds stay atomic so extraction is unchanged."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pypdf import PdfReader

from experiments.renderer.prepare_cases import add_approved_variants
from job_application_engine.ats_qa.text import normalize_extracted_text
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.rendering.pdf import (
    TEMPLATE_VERSION,
    PdfRenderError,
    _literal_text_expression,
    build_pdf,
)
from job_application_engine.rendering.text import render_text
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix004 import _extracted_texts


def test_slash_and_hyphen_tokens_are_emitted_atomically() -> None:
    expression = _literal_text_expression("Use ISO/DIN, CI/CD and full-stack work.")
    assert '#box[#text("ISO/DIN,")]' in expression
    assert '#box[#text("CI/CD")]' in expression
    assert '#box[#text("full-stack")]' in expression
    assert '#text(" and ")' in expression


def test_real_pdf_keeps_slash_compounds_complete_in_both_extractors(tmp_path: Path) -> None:
    # Padding grows one word per paragraph, so some slash token must reach the
    # line end; without atomic compounds Typst breaks after the slash there.
    profile, reviews = approved_baseline()
    variants = [
        (f"slash-{k}", "ab " * k + "ISO/DIN rust/corrosion CI/CD PDF/CSV Python/Apache end")
        for k in range(10, 50)
    ]
    profile, reviews = add_approved_variants(profile, reviews, variants)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    output = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = normalize_extracted_text(render_text(plan, profile, reviews=reviews))
    for recovered in _extracted_texts(output):
        normalized = normalize_extracted_text(recovered)
        assert normalized == expected
        for token in ("ISO/DIN", "rust/corrosion", "CI/CD", "PDF/CSV", "Python/Apache"):
            assert normalized.count(token) == len(variants)
            assert token.replace("/", "/ ") not in normalized
    assert len(PdfReader(output).pages) >= 1


def test_unbreakable_slash_compound_fails_before_publication(tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    profile, reviews = add_approved_variants(
        profile, reviews, [("slash-overflow", "a/" * 200 + "z")]
    )
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    with pytest.raises(PdfRenderError, match="slash-joined compound.*fixed A4"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


def test_template_identity_changed_for_slash_compounds() -> None:
    assert TEMPLATE_VERSION == "baseline-v5-m1-fix007-slash-compounds"
