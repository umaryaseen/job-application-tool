"""Synthetic regressions for the M1-FIX-004 visual presentation policy."""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from pypdf import PdfReader

from experiments.renderer.prepare_cases import add_approved_variants
from job_application_engine.ats_qa.expected import ExpectedEntry, ExpectedSection
from job_application_engine.ats_qa.text import normalize_extracted_text
from job_application_engine.domain.evidence import FactApproval, SupportBinding
from job_application_engine.domain.fact import ContactFact
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import fact_approval_from_review, record_human_review
from job_application_engine.rendering.pdf import PdfRenderError, _template_text, build_pdf
from job_application_engine.rendering.presentation import present_plan
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.support import (
    canonical_fact_payload,
    canonical_json,
    evidence_digest,
    fact_digest,
)
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix import supported_project_profile


def _profile_with_contact_url(url: str):
    """Add one synthetic, locally reviewed URL contact to the compact fixture."""

    profile, reviews = approved_baseline()
    source = profile.evidence[0]
    fact = ContactFact.model_validate(
        {
            "fact_id": "contact-url-long",
            "revision": 1,
            "subject_id": "synthetic-person",
            "kind": "contact",
            "status": "approved",
            # A temporary value lets the strict model represent the reviewed
            # revision before this helper replaces it with the real receipt.
            "approval": FactApproval(
                fact_sha256="0" * 64,
                evidence_bundle_sha256="0" * 64,
                approved_at=datetime(2026, 9, 12, 13, tzinfo=UTC),
                reviewer_id="synthetic-reviewer",
            ),
            "evidence_refs": [{"evidence_id": source.evidence_id, "revision": source.revision}],
            "support_binding_refs": ["binding-contact-url-long"],
            "value": {"kind": "url", "value": url},
        }
    )
    binding = SupportBinding.model_validate(
        {
            "binding_id": "binding-contact-url-long",
            "fact_id": fact.fact_id,
            "fact_revision": fact.revision,
            "evidence_id": source.evidence_id,
            "evidence_revision": source.revision,
            "fact_sha256": fact_digest(fact),
            "evidence_sha256": evidence_digest(source),
            "reviewed_scope": "synthetic contact URL",
            "reviewed_at": datetime(2026, 9, 12, 12, tzinfo=UTC),
            "reviewer_id": "synthetic-reviewer",
        }
    )
    profile = profile.model_copy(
        update={
            "facts": [*profile.facts, fact],
            "support_bindings": [*profile.support_bindings, binding],
        }
    )
    receipt = record_human_review(
        profile,
        target_type="fact",
        target_id=fact.fact_id,
        target_revision=fact.revision,
        displayed_content=canonical_json(canonical_fact_payload(fact)),
        review_id="review-contact-url-long",
        reviewer_id="synthetic-reviewer",
        reviewed_at=datetime(2026, 9, 12, 13, tzinfo=UTC),
    )
    reviews.append(receipt)
    approved = fact_approval_from_review(receipt)
    profile = profile.model_copy(
        update={
            "facts": [
                item.model_copy(update={"approval": approved})
                if item.fact_id == fact.fact_id
                else item
                for item in profile.facts
            ]
        }
    )
    return profile, reviews


def _extracted_texts(pdf: Path) -> tuple[str, str]:
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    pypdf = "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    return poppler, pypdf


def _assert_complete_extraction(pdf: Path, expected: str) -> tuple[str, str]:
    recovered = _extracted_texts(pdf)
    for actual in recovered:
        assert normalize_extracted_text(actual) == normalize_extracted_text(expected)
    return recovered


def test_candidate_name_is_header_without_contact_section_label() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    output = render_text(plan, profile, reviews=reviews)
    assert output.splitlines()[0] == "Synthetic Example"
    assert "\nContact\n" not in output
    assert output.count("Synthetic Example") == 1


def test_experience_has_emphasized_roles_bullets_and_nested_linked_project() -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile, as_of=date(2026, 9, 21), reviews=reviews, support_captures=captures
    )
    sections = present_plan(plan, profile)
    experience = next(section for section in sections if section.label == "Professional Experience")
    assert experience.lines[0].style == "employment"
    assert any(line.style == "bullet" for line in experience.lines)
    linked = next(line for line in experience.lines if "Project: InSite" in line.text)
    assert linked.style == "project"
    assert not any(line.text == "Standalone Projects" for line in experience.lines)


def test_standalone_projects_are_a_content_aware_page_two_section() -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile, as_of=date(2026, 9, 21), reviews=reviews, support_captures=captures
    )
    sections = present_plan(plan, profile)
    labels = [section.label for section in sections]
    assert labels == [
        "",
        "Professional Summary",
        "Professional Experience",
        "Selected Projects",
        "Education",
        "Skills",
        "Languages",
    ]
    selected = sections[labels.index("Selected Projects")]
    assert selected.page_break_before is True
    assert selected.lines[0].text.startswith("Project:")


def test_no_standalone_projects_does_not_create_selected_projects_or_page_break() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    sections = present_plan(plan, profile)
    assert all(section.label != "Selected Projects" for section in sections)
    assert all(not section.page_break_before for section in sections)


def test_over_capacity_plan_retains_all_claim_lines_without_shrinking() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    experience = next(section for section in plan.sections if section.section_id == "experience")
    long_lines = [experience.lines[0]] + [experience.lines[1]] * 80
    expanded = plan.model_copy(
        update={
            "sections": [
                section.model_copy(update={"lines": long_lines})
                if section.section_id == "experience"
                else section
                for section in plan.sections
            ]
        }
    )
    displayed = present_plan(expanded, profile)
    shown = next(section for section in displayed if section.label == "Professional Experience")
    assert (
        len([line for line in shown.lines if line.text == "Synthetic Engineer — Example Labs"])
        == 80
    )


def test_template_keeps_left_alignment_and_no_hyphenation() -> None:
    template = _template_text()
    assert "alignment: left" in template
    assert "justified" not in template


def test_only_contact_heading_can_be_hidden_in_qa_oracle() -> None:
    with pytest.raises(ValueError, match="only the Contact heading"):
        ExpectedSection(
            label="Education",
            heading_visible=False,
            entries=[ExpectedEntry(entry_id="education", text="Synthetic education")],
        )


def test_real_no_project_pdf_has_no_project_heading_or_extra_page(tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert len(PdfReader(pdf).pages) == 1
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Selected Projects" not in text


def test_real_over_capacity_pdf_preserves_content_without_shrinking(tmp_path: Path) -> None:
    profile, reviews = approved_baseline()
    additions = [
        (
            f"over-capacity-{index}",
            f"Synthetic capacity claim {index}: "
            + "preserve this approved wording " * 24
            + f"sentinel {index}.",
        )
        for index in range(1, 25)
    ]
    profile, reviews = add_approved_variants(profile, reviews, additions)
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert len(PdfReader(pdf).pages) > 2
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "Synthetic capacity claim 1" in text
    assert "sentinel 24." in text


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_exact_review_long_contact_url_fails_before_publication(tmp_path: Path) -> None:
    url = "https://example.invalid/profile/this-is-a-very-long-contact-url-with-meaningful-components-and-no-loss"
    profile, reviews = _profile_with_contact_url(url)
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)

    with pytest.raises(PdfRenderError, match="contact URL.*fixed A4"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_fitting_contact_url_is_complete_in_both_extractors(tmp_path: Path) -> None:
    url = "https://example.invalid/profile/maintainability-and-modularity"
    profile, reviews = _profile_with_contact_url(url)
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    poppler, pypdf = _assert_complete_extraction(pdf, expected)
    for actual in (poppler, pypdf):
        assert url in normalize_extracted_text(actual)
    with pytest.raises(AssertionError):
        _assert_complete_extraction(pdf, expected.replace(url, url + "?changed=1"))
    with pytest.raises(AssertionError):
        _assert_complete_extraction(pdf, expected.replace(url, url.replace("-", "—")))


@pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)
def test_over_width_contact_url_fails_with_bounded_diagnostic(tmp_path: Path) -> None:
    url = "https://example.invalid/" + ("synthetic-component-" * 40)
    profile, reviews = _profile_with_contact_url(url)
    plan = compile_baseline(profile, as_of=date(2026, 9, 21), reviews=reviews)

    with pytest.raises(PdfRenderError, match="contact URL.*fixed A4"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()
