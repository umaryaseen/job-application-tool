"""Synthetic end-to-end regression for M1 responsibility/project preservation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from job_application_engine.ats_qa.expected import ExpectedDocument, ExpectedEntry, ExpectedSection
from job_application_engine.ats_qa.pdf import run_pdf_qa
from job_application_engine.ats_qa.report import VisualReview, overall_status
from job_application_engine.ats_qa.text import normalize_extracted_text
from job_application_engine.domain.document import DocumentLine, DocumentPlan, DocumentSection
from job_application_engine.domain.evidence import EvidenceApproval
from job_application_engine.domain.fact import FactRef
from job_application_engine.domain.profile import ProfileRevision
from job_application_engine.profile.baseline import _project_key, compile_baseline
from job_application_engine.profile.review import (
    evidence_approval_from_review,
    fact_approval_from_review,
    record_human_review,
)
from job_application_engine.rendering.pdf import build_pdf
from job_application_engine.rendering.text import render_text
from job_application_engine.snapshots.export import export_snapshot
from job_application_engine.snapshots.review import approve_snapshot
from job_application_engine.snapshots.store import SnapshotBuild, build_snapshot
from job_application_engine.verification.document import (
    DocumentValidationError,
    document_plan_digest,
    profile_digest,
    validate_document_plan,
)
from job_application_engine.verification.support import canonical_json, evidence_digest, fact_digest
from tests.test_document_plan import approved_baseline

NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


def manually_reconstructed_plan(
    profile: ProfileRevision,
    *,
    experience_order: list[str],
) -> DocumentPlan:
    """Build a plan at the public boundary without using the baseline compiler."""

    facts = {fact.fact_id: fact for fact in profile.facts}
    variants = {variant.variant_id: variant for variant in profile.variants}

    def fact_line(fact_id: str, text: str) -> DocumentLine:
        fact = facts[fact_id]
        return DocumentLine(
            text=text,
            source="fact",
            fact_ref=FactRef(fact_id=fact.fact_id, revision=fact.revision),
            support_binding_refs=list(fact.support_binding_refs),
        )

    def variant_line(variant_id: str) -> DocumentLine:
        variant = variants[variant_id]
        return DocumentLine(
            text=variant.text,
            source="variant",
            variant_id=variant.variant_id,
            variant_revision=variant.revision,
            support_binding_refs=list(variant.support_binding_refs),
        )

    text_by_id = {
        "contact-name": "Synthetic Example",
        "contact-email": "Email: synthetic@example.com",
        "employment-one": "Synthetic Engineer — Example Labs | 2022-01 – ongoing",
        "employment-two": "Synthetic Analyst — Example Labs | 2022-01 – 2023-12",
        "responsibility-one": "Led synthetic service reliability work for the team.",
        "project-one": (
            "InSite — Software Engineer | 2024-01 – end date unknown | Technologies: YOLO v11, "
            "Roboflow | Integrated synthetic drone imagery detection."
        ),
        "project-two": (
            "Cost CLI — Contributor | start date unknown – end date unknown | "
            "Technologies: Python | "
            "Built an open-source CLI cost-forensics tool."
        ),
        "education-one": (
            "Synthetic MSc — Synthetic Computing, Example University "
            "(status: unknown;  – end date unknown)"
        ),
        "skill-german": "Größe Ä Ö Ü ß (context: study; proficiency: unknown)",
        "language-one": "German (CEFR B2)",
    }
    sections = [
        DocumentSection(
            section_id="contact",
            label="Contact",
            lines=[
                fact_line("contact-name", text_by_id["contact-name"]),
                fact_line("contact-email", text_by_id["contact-email"]),
            ],
        ),
        DocumentSection(
            section_id="headline",
            label="Professional Summary",
            lines=[variant_line("headline-one")],
        ),
        DocumentSection(
            section_id="experience",
            label="Professional Experience",
            lines=[fact_line(fact_id, text_by_id[fact_id]) for fact_id in experience_order],
        ),
        DocumentSection(
            section_id="education",
            label="Education",
            lines=[fact_line("education-one", text_by_id["education-one"])],
        ),
        DocumentSection(
            section_id="skills",
            label="Skills",
            lines=[fact_line("skill-german", text_by_id["skill-german"])],
        ),
        DocumentSection(
            section_id="languages",
            label="Languages",
            lines=[fact_line("language-one", text_by_id["language-one"])],
        ),
    ]
    draft = DocumentPlan(
        plan_version="1.0",
        profile_id=profile.profile_id,
        profile_revision=profile.revision,
        profile_digest=profile_digest(profile),
        as_of=date(2026, 9, 14),
        locale="en",
        sections=sections,
        plan_sha256="0" * 64,
    )
    return draft.model_copy(update={"plan_sha256": document_plan_digest(draft)})


def supported_project_profile() -> tuple[
    ProfileRevision, list[object], dict[tuple[str, int], bytes]
]:
    """Create one synthetic employment, responsibilities and projects."""

    base, reviews = approved_baseline()
    capture = b"synthetic documentary project capture\n"
    capture_sha = hashlib.sha256(capture).hexdigest()
    data = base.model_dump(mode="json")
    data["entities"].extend(
        [
            {"entity_id": "project-insite", "entity_type": "project", "display_name": "InSite"},
            {"entity_id": "project-cli", "entity_type": "project", "display_name": "Cost CLI"},
        ]
    )
    data["evidence"].append(
        {
            "evidence_id": "project-document",
            "revision": 1,
            "kind": "document_reference",
            "source": {
                "kind": "document_reference",
                "document_sha256": capture_sha,
                "locator": "synthetic/project-review.txt",
            },
            "support_capture_sha256": capture_sha,
            "captured_at": NOW.isoformat(),
            "status": "draft",
        }
    )
    data["facts"].extend(
        [
            {
                "fact_id": "responsibility-one",
                "revision": 1,
                "subject_id": "synthetic-person",
                "kind": "responsibility",
                "employment_ref": {"fact_id": "employment-one", "revision": 1},
                "text": "Led synthetic service reliability work for the team.",
                "evidence_refs": [{"evidence_id": "project-document", "revision": 1}],
                "support_binding_refs": ["binding-responsibility-one"],
                "status": "approved",
                "approval": {
                    "fact_sha256": "0" * 64,
                    "evidence_bundle_sha256": "0" * 64,
                    "approved_at": NOW.isoformat(),
                    "reviewer_id": "synthetic-reviewer",
                },
            },
            {
                "fact_id": "project-one",
                "revision": 1,
                "subject_id": "synthetic-person",
                "kind": "project",
                "project_entity_id": "project-insite",
                "employment_ref": {"fact_id": "employment-one", "revision": 1},
                "project_name": "InSite",
                "role": "Software Engineer",
                "period": {
                    "start": {"precision": "month", "year": 2024, "month": 1},
                    "start_state": "known",
                    "end": None,
                    "end_state": "unknown",
                },
                "description": "Integrated synthetic drone imagery detection.",
                "technologies": ["YOLO v11", "Roboflow"],
                "evidence_refs": [{"evidence_id": "project-document", "revision": 1}],
                "support_binding_refs": ["binding-project-one"],
                "status": "approved",
                "approval": {
                    "fact_sha256": "0" * 64,
                    "evidence_bundle_sha256": "0" * 64,
                    "approved_at": NOW.isoformat(),
                    "reviewer_id": "synthetic-reviewer",
                },
            },
            {
                "fact_id": "project-two",
                "revision": 1,
                "subject_id": "synthetic-person",
                "kind": "project",
                "project_entity_id": "project-cli",
                "project_name": "Cost CLI",
                "role": "Contributor",
                "period": {
                    "start": None,
                    "start_state": "unknown",
                    "end": None,
                    "end_state": "unknown",
                },
                "description": "Built an open-source CLI cost-forensics tool.",
                "technologies": ["Python"],
                "evidence_refs": [{"evidence_id": "project-document", "revision": 1}],
                "support_binding_refs": ["binding-project-two"],
                "status": "approved",
                "approval": {
                    "fact_sha256": "0" * 64,
                    "evidence_bundle_sha256": "0" * 64,
                    "approved_at": NOW.isoformat(),
                    "reviewer_id": "synthetic-reviewer",
                },
            },
        ]
    )
    for fact_id in ("responsibility-one", "project-one", "project-two"):
        data["support_bindings"].append(
            {
                "binding_id": f"binding-{fact_id}",
                "fact_id": fact_id,
                "fact_revision": 1,
                "evidence_id": "project-document",
                "evidence_revision": 1,
                "fact_sha256": "0" * 64,
                "evidence_sha256": "0" * 64,
                "reviewed_scope": f"synthetic support for {fact_id}",
                "reviewed_at": NOW.isoformat(),
                "reviewer_id": "synthetic-reviewer",
            }
        )
    provisional = ProfileRevision.model_validate_json(json.dumps(data))
    evidence = provisional.evidence[-1].model_copy(
        update={
            "status": "approved",
            "approval": EvidenceApproval(
                evidence_sha256="0" * 64, approved_at=NOW, reviewer_id="synthetic-reviewer"
            ),
        }
    )
    provisional = provisional.model_copy(
        update={"evidence": [*provisional.evidence[:-1], evidence]}
    )
    evidence_review = record_human_review(
        provisional,
        target_type="evidence",
        target_id=evidence.evidence_id,
        target_revision=1,
        displayed_content=canonical_json(evidence.model_dump(mode="json", exclude={"approval"})),
        review_id="review-project-document",
        reviewer_id="synthetic-reviewer",
        reviewed_at=NOW,
    )
    evidence = evidence.model_copy(
        update={"approval": evidence_approval_from_review(evidence_review)}
    )
    profile = provisional.model_copy(update={"evidence": [*provisional.evidence[:-1], evidence]})
    reviews = [*reviews, evidence_review]
    profile = profile.model_copy(
        update={
            "support_bindings": [
                binding.model_copy(
                    update={
                        "fact_sha256": fact_digest(
                            next(f for f in profile.facts if f.fact_id == binding.fact_id)
                        ),
                        "evidence_sha256": evidence_digest(evidence),
                    }
                )
                if binding.fact_id in {"responsibility-one", "project-one", "project-two"}
                else binding
                for binding in profile.support_bindings
            ]
        }
    )
    facts = []
    for fact in profile.facts:
        if fact.fact_id not in {"responsibility-one", "project-one", "project-two"}:
            facts.append(fact)
            continue
        review = record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=1,
            displayed_content=canonical_json(fact.model_dump(mode="json", exclude={"approval"})),
            review_id=f"review-{fact.fact_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=NOW,
        )
        reviews.append(review)
        facts.append(fact.model_copy(update={"approval": fact_approval_from_review(review)}))
    profile = profile.model_copy(update={"facts": facts})
    return profile, reviews, {("project-document", 1): capture}


def test_m1_claims_preserve_scope_dates_and_support_end_to_end() -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile,
        as_of=date(2026, 9, 14),
        reviews=reviews,
        support_captures=captures,
    )
    experience = next(section for section in plan.sections if section.section_id == "experience")
    lines = [line.text for line in experience.lines]
    employment_index = next(
        i for i, line in enumerate(lines) if line.startswith("Synthetic Engineer")
    )
    assert "Led synthetic service reliability work" in lines[employment_index + 1]
    assert "InSite — Software Engineer" in lines[employment_index + 2]
    assert "end date unknown" in lines[employment_index + 2]
    assert lines[-1].startswith("Cost CLI — Contributor")
    assert "Present" not in render_text(plan, profile, reviews=reviews, support_captures=captures)


def test_candidate_name_binding_is_required_at_public_plan_boundary(tmp_path: Path) -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile, as_of=date(2026, 9, 14), reviews=reviews, support_captures=captures
    )
    contact = next(section for section in plan.sections if section.section_id == "contact")
    without_name = plan.model_copy(
        update={
            "sections": [
                section
                if section is not contact
                else contact.model_copy(update={"lines": contact.lines[1:]})
                for section in plan.sections
            ],
            "plan_sha256": "0" * 64,
        }
    )
    without_name = without_name.model_copy(
        update={"plan_sha256": document_plan_digest(without_name)}
    )
    with pytest.raises(DocumentValidationError, match="candidate-name|identity"):
        validate_document_plan(without_name, profile, reviews=reviews, support_captures=captures)
    with pytest.raises(DocumentValidationError, match="candidate-name|identity"):
        build_pdf(
            without_name,
            profile,
            reviews=reviews,
            support_captures=captures,
            data_root=tmp_path,
        )

    name = contact.lines[0]
    stale = name.model_copy(update={"fact_ref": FactRef(fact_id="contact-name", revision=2)})
    stale_contact = contact.model_copy(update={"lines": [stale, *contact.lines[1:]]})
    stale_plan = plan.model_copy(
        update={
            "sections": [
                stale_contact if section is contact else section for section in plan.sections
            ],
            "plan_sha256": "0" * 64,
        }
    )
    stale_plan = stale_plan.model_copy(update={"plan_sha256": document_plan_digest(stale_plan)})
    with pytest.raises(DocumentValidationError):
        validate_document_plan(stale_plan, profile, reviews=reviews, support_captures=captures)


def test_m1_rejects_wrong_employment_subject_and_missing_capture() -> None:
    profile, reviews, captures = supported_project_profile()
    project = next(f for f in profile.facts if f.fact_id == "project-one")
    bad = project.model_copy(
        update={"employment_ref": FactRef(fact_id="employment-two", revision=1)}
    )
    with_error = profile.model_copy(
        update={"facts": [bad if f.fact_id == project.fact_id else f for f in profile.facts]}
    )
    import pytest

    from job_application_engine.profile.validation import (
        ProvenanceValidationError,
        validate_profile,
    )

    with pytest.raises(ProvenanceValidationError, match="stale_fact_approval|project"):
        validate_profile(with_error, reviews=reviews, support_captures=captures)
    with pytest.raises(ProvenanceValidationError, match="support_capture"):
        validate_profile(profile, reviews=reviews, support_captures={})

    wrong_subject = project.model_copy(update={"subject_id": "another-person"})
    changed = profile.model_copy(
        update={
            "facts": [wrong_subject if f.fact_id == project.fact_id else f for f in profile.facts]
        }
    )
    with pytest.raises(ProvenanceValidationError, match="project_scope"):
        validate_profile(changed, reviews=reviews, support_captures=captures)


def test_m1_real_pdf_qa_and_snapshot_export_preserve_claims(tmp_path: Path) -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile,
        as_of=date(2026, 9, 14),
        reviews=reviews,
        support_captures=captures,
    )
    pdf = build_pdf(
        plan,
        profile,
        reviews=reviews,
        support_captures=captures,
        data_root=tmp_path,
    )
    poppler = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    from pypdf import PdfReader

    pypdf = "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    expected_lines = [
        "Synthetic Example",
        "Email: synthetic@example.com",
        "Professional Summary",
        "Synthetic Engineer",
        "Professional Experience",
        "Synthetic Analyst — Example Labs",
        "January 2022 – December 2023",
        "Synthetic Engineer — Example Labs",
        "January 2022 – ongoing",
        "• Led synthetic service reliability work for the team.",
        ("Project: InSite — Software Engineer | Start: January 2024"),
        "Technologies: YOLO v11, Roboflow",
        "Integrated synthetic drone imagery detection.",
        "Selected Projects",
        ("Project: Cost CLI — Contributor"),
        "Technologies: Python",
        "Built an open-source CLI cost-forensics tool.",
        "Education",
        ("Synthetic MSc — Synthetic Computing, Example University"),
        "Skills",
        "Data processing & analysis",
        "Größe Ä Ö Ü ß (study, recent experience)",
        "Languages",
        "German (CEFR B2)",
    ]
    normalized_poppler = normalize_extracted_text(poppler)
    normalized_pypdf = normalize_extracted_text(pypdf)
    assert all(normalize_extracted_text(line) in normalized_poppler for line in expected_lines)
    assert all(normalize_extracted_text(line) in normalized_pypdf for line in expected_lines)
    oracle = ExpectedDocument(
        required_identity="Synthetic Example",
        sections=[
            ExpectedSection(
                label="Contact",
                heading_visible=False,
                entries=[
                    ExpectedEntry(entry_id="name", text=expected_lines[0]),
                    ExpectedEntry(entry_id="contact", text=expected_lines[1]),
                ],
            ),
            ExpectedSection(
                label="Professional Summary",
                entries=[ExpectedEntry(entry_id="summary", text=expected_lines[3])],
            ),
            ExpectedSection(
                label="Professional Experience",
                entries=[
                    ExpectedEntry(entry_id=f"experience-{i}", text=text)
                    for i, text in enumerate(expected_lines[5:13])
                ],
            ),
            ExpectedSection(
                label="Selected Projects",
                entries=[
                    ExpectedEntry(entry_id="project", text=expected_lines[14]),
                    ExpectedEntry(entry_id="project-technologies", text=expected_lines[15]),
                    ExpectedEntry(entry_id="project-description", text=expected_lines[16]),
                ],
            ),
            ExpectedSection(
                label="Education",
                entries=[
                    ExpectedEntry(entry_id="education", text=expected_lines[18]),
                    ExpectedEntry(
                        entry_id="thesis-title", text="Thesis: Synthetic validation thesis"
                    ),
                    ExpectedEntry(
                        entry_id="thesis-description",
                        text="Synthetic research on bounded optimization.",
                    ),
                    ExpectedEntry(
                        entry_id="coursework",
                        text="Coursework: Synthetic Algorithms | Synthetic Systems",
                    ),
                ],
            ),
            ExpectedSection(
                label="Skills",
                entries=[
                    ExpectedEntry(entry_id="skill-category", text=expected_lines[20]),
                    ExpectedEntry(entry_id="skill", text=expected_lines[21]),
                ],
            ),
            ExpectedSection(
                label="Languages",
                entries=[ExpectedEntry(entry_id="language", text=expected_lines[23])],
            ),
        ],
        unicode_tokens=["Größe Ä Ö Ü ß"],
        expected_pages=2,
    )
    report = run_pdf_qa(
        pdf,
        oracle,
        report_path=tmp_path / "qa" / "report.json",
        raster_dir=tmp_path / "qa" / "rasters",
        profile=profile,
        reviews=reviews,
        support_captures=captures,
    )
    assert report.overall_status == "not_checked"
    assert all(check.status == "pass" for check in report.checks if check.mandatory)
    visual = VisualReview(
        status="pass",
        reviewer_id="synthetic-visual-reviewer",
        reviewed_at=NOW,
        artifact_sha256=report.artifact_sha256,
        notes="Synthetic page observation for regression coverage.",
    )
    qa_report = report.model_copy(
        update={"visual_review": visual, "overall_status": overall_status(report.checks, visual)}
    )
    text = render_text(plan, profile, reviews=reviews, support_captures=captures).encode()
    cli_inputs = tmp_path / "cli-inputs"
    cli_inputs.mkdir()
    (cli_inputs / "profile.json").write_text(profile.model_dump_json(), encoding="utf-8")
    (cli_inputs / "plan.json").write_text(plan.model_dump_json(), encoding="utf-8")
    (cli_inputs / "reviews.json").write_text(
        json.dumps([review.model_dump(mode="json") for review in reviews]), encoding="utf-8"
    )
    (cli_inputs / "pdf.bin").write_bytes(pdf.read_bytes())
    (cli_inputs / "text.bin").write_bytes(text)
    (cli_inputs / "qa.json").write_bytes(qa_report.model_dump_json().encode())
    (cli_inputs / "source.bin").write_bytes(b'{"slice":"m1-fix-cli"}\n')
    cli_captures = cli_inputs / "captures"
    cli_captures.mkdir()
    cli_captures.joinpath("project-document-r1.bin").write_bytes(captures[("project-document", 1)])
    cli_env = {**__import__("os").environ, "JAE_DATA_DIR": str(tmp_path)}
    cli_root = [sys.executable, "-m", "job_application_engine.cli"]
    build_result = subprocess.run(
        cli_root
        + [
            "snapshot-build",
            "--profile",
            "cli-inputs/profile.json",
            "--plan",
            "cli-inputs/plan.json",
            "--reviews",
            "cli-inputs/reviews.json",
            "--pdf",
            "cli-inputs/pdf.bin",
            "--text",
            "cli-inputs/text.bin",
            "--qa",
            "cli-inputs/qa.json",
            "--source-slice",
            "cli-inputs/source.bin",
            "--captures-dir",
            "cli-inputs/captures",
            "--snapshot-id",
            "m1-fix-cli",
            "--as-of",
            "2026-09-14",
        ],
        cwd=Path(__file__).parents[1],
        env=cli_env,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, build_result.stderr
    before_approval = subprocess.run(
        cli_root
        + [
            "snapshot-export",
            "--snapshot-id",
            "m1-fix-cli",
            "--destination",
            "cli-export-before",
            "--profile",
            "cli-inputs/profile.json",
            "--reviews",
            "cli-inputs/reviews.json",
            "--captures-dir",
            "cli-inputs/captures",
        ],
        cwd=Path(__file__).parents[1],
        env=cli_env,
        capture_output=True,
        text=True,
    )
    assert before_approval.returncode != 0
    assert not (tmp_path / "cli-export-before").exists()
    approval_result = subprocess.run(
        cli_root
        + [
            "snapshot-approve",
            "--snapshot-id",
            "m1-fix-cli",
            "--reviewer-id",
            "synthetic-final-reviewer",
        ],
        cwd=Path(__file__).parents[1],
        env=cli_env,
        capture_output=True,
        text=True,
    )
    assert approval_result.returncode == 0, approval_result.stderr
    cli_export = subprocess.run(
        cli_root
        + [
            "snapshot-export",
            "--snapshot-id",
            "m1-fix-cli",
            "--destination",
            "cli-export",
            "--profile",
            "cli-inputs/profile.json",
            "--reviews",
            "cli-inputs/reviews.json",
            "--captures-dir",
            "cli-inputs/captures",
        ],
        cwd=Path(__file__).parents[1],
        env=cli_env,
        capture_output=True,
        text=True,
    )
    assert cli_export.returncode == 0, cli_export.stderr
    cli_snapshot = tmp_path / "snapshots/m1-fix-cli"
    assert (tmp_path / "cli-export/output.pdf").read_bytes() == (
        cli_snapshot / "pdf/output.pdf"
    ).read_bytes()
    assert (tmp_path / "cli-export/output.txt").read_bytes() == (
        cli_snapshot / "text/output.txt"
    ).read_bytes()
    request = SnapshotBuild(
        snapshot_id="m1-fix-synthetic",
        profile=profile,
        plan=plan,
        reviews=reviews,
        support_captures=captures,
        source_slice=b'{"slice":"m1-fix-synthetic"}\n',
        pdf=pdf.read_bytes(),
        text=text,
        qa_report=qa_report.model_dump_json().encode(),
        configuration={"locale": "en", "template": "synthetic"},
        tool_versions={"python": "3.12"},
        as_of=date(2026, 9, 14),
    )
    result = build_snapshot(request, root=tmp_path)
    approve_snapshot(
        "m1-fix-synthetic",
        reviewer_id="synthetic-final-reviewer",
        approved_at=NOW,
        root=tmp_path,
    )
    destination = tmp_path / "exported"
    export_snapshot(
        "m1-fix-synthetic",
        destination=destination,
        profile=profile,
        reviews=reviews,
        support_captures=captures,
        now=NOW,
        root=tmp_path,
    )
    assert (destination / "output.pdf").read_bytes() == (
        result.path / "pdf/output.pdf"
    ).read_bytes()
    assert (destination / "output.txt").read_bytes() == (
        result.path / "text/output.txt"
    ).read_bytes()


def test_m1_cli_build_forwards_required_support_captures(tmp_path: Path) -> None:
    profile, reviews, captures = supported_project_profile()
    plan = compile_baseline(
        profile,
        as_of=date(2026, 9, 14),
        reviews=reviews,
        support_captures=captures,
    )
    profile_path = tmp_path / "profile.json"
    plan_path = tmp_path / "plan.json"
    reviews_path = tmp_path / "reviews.json"
    profile_path.write_text(profile.model_dump_json(), encoding="utf-8")
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    reviews_path.write_text(
        json.dumps([review.model_dump(mode="json") for review in reviews]), encoding="utf-8"
    )
    captures_dir = tmp_path / "captures"
    captures_dir.mkdir()
    captures_dir.joinpath("project-document-r1.bin").write_bytes(captures[("project-document", 1)])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "job_application_engine.cli",
            "build-cv",
            "--profile",
            str(profile_path),
            "--plan",
            str(plan_path),
            "--reviews",
            str(reviews_path),
            "--captures-dir",
            "captures",
        ],
        cwd=Path(__file__).parents[1],
        env={**__import__("os").environ, "JAE_DATA_DIR": str(tmp_path)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "outputs/baseline.pdf").is_file()


def test_reconstructed_plan_rejects_moved_claims_at_validation_and_pdf_boundaries(
    tmp_path: Path,
) -> None:
    profile, reviews, captures = supported_project_profile()
    valid_order = [
        "employment-two",
        "employment-one",
        "responsibility-one",
        "project-one",
        "project-two",
    ]
    valid = manually_reconstructed_plan(profile, experience_order=valid_order)
    from job_application_engine.verification.document import DocumentValidationError

    validate_document_plan(valid, profile, reviews=reviews, support_captures=captures)

    def with_order(order: list[str]) -> DocumentPlan:
        plan = manually_reconstructed_plan(profile, experience_order=order)
        return plan

    attacks = [
        (
            "responsibility moved under employment-two",
            [
                "employment-two",
                "responsibility-one",
                "employment-one",
                "project-one",
                "project-two",
            ],
            "responsibility placement",
        ),
        (
            "linked project moved under employment-two",
            [
                "employment-two",
                "project-one",
                "employment-one",
                "responsibility-one",
                "project-two",
            ],
            "project placement",
        ),
    ]
    for _label, order, message in attacks:
        altered = with_order(order)
        with pytest.raises(DocumentValidationError, match=message):
            validate_document_plan(altered, profile, reviews=reviews, support_captures=captures)
        with pytest.raises(DocumentValidationError, match=message):
            render_text(altered, profile, reviews=reviews, support_captures=captures)
        with pytest.raises(DocumentValidationError, match=message):
            build_pdf(
                altered,
                profile,
                reviews=reviews,
                support_captures=captures,
                data_root=tmp_path / _label.replace(" ", "-"),
            )

    bad_revision = manually_reconstructed_plan(
        profile,
        experience_order=[
            "employment-two",
            "employment-one",
            "responsibility-one",
            "project-one",
            "project-two",
        ],
    )
    experience = next(
        section for section in bad_revision.sections if section.section_id == "experience"
    )
    employment = next(
        line
        for line in experience.lines
        if line.fact_ref and line.fact_ref.fact_id == "employment-one"
    )
    assert employment.fact_ref is not None
    replacement = employment.model_copy(
        update={"fact_ref": FactRef(fact_id="employment-one", revision=2)}
    )
    changed_lines = [replacement if line is employment else line for line in experience.lines]
    changed_section = experience.model_copy(update={"lines": changed_lines})
    bad_revision = bad_revision.model_copy(
        update={
            "sections": [
                changed_section if section is experience else section
                for section in bad_revision.sections
            ],
            "plan_sha256": "0" * 64,
        }
    )
    bad_revision = bad_revision.model_copy(
        update={"plan_sha256": document_plan_digest(bad_revision)}
    )
    with pytest.raises(DocumentValidationError, match="missing or unapproved fact revision"):
        validate_document_plan(bad_revision, profile, reviews=reviews, support_captures=captures)


def test_standalone_project_is_valid_and_project_order_is_unknown_first_with_stable_ties() -> None:
    profile, _reviews, _captures = supported_project_profile()
    base = next(f for f in profile.facts if f.fact_id == "project-one")
    specs = [
        (
            "unknown-z",
            {"start": None, "start_state": "unknown", "end": None, "end_state": "unknown"},
        ),
        (
            "year",
            {
                "start": {"precision": "year", "year": 2024},
                "start_state": "known",
                "end": None,
                "end_state": "unknown",
            },
        ),
        (
            "unknown-a",
            {"start": None, "start_state": "unknown", "end": None, "end_state": "unknown"},
        ),
        (
            "month",
            {
                "start": {"precision": "month", "year": 2025, "month": 1},
                "start_state": "known",
                "end": None,
                "end_state": "unknown",
            },
        ),
        (
            "day",
            {
                "start": {"precision": "day", "year": 2025, "month": 1, "day": 3},
                "start_state": "known",
                "end": None,
                "end_state": "unknown",
            },
        ),
        (
            "tie-b",
            {
                "start": {"precision": "day", "year": 2025, "month": 1, "day": 3},
                "start_state": "known",
                "end": None,
                "end_state": "unknown",
            },
        ),
        (
            "tie-a",
            {
                "start": {"precision": "day", "year": 2025, "month": 1, "day": 3},
                "start_state": "known",
                "end": None,
                "end_state": "unknown",
            },
        ),
    ]
    projects = [
        base.model_copy(
            update={
                "fact_id": fact_id,
                "project_entity_id": "project-cli",
                "employment_ref": None,
                "period": type(base.period).model_validate(period),
            }
        )
        for fact_id, period in specs
    ]
    shuffled = list(reversed(projects))
    expected = ["unknown-a", "unknown-z", "day", "tie-a", "tie-b", "month", "year"]
    assert [project.fact_id for project in sorted(shuffled, key=_project_key)] == expected

    standalone = manually_reconstructed_plan(
        profile,
        experience_order=[
            "employment-two",
            "employment-one",
            "responsibility-one",
            "project-one",
            "project-two",
        ],
    )
    validate_document_plan(standalone, profile, reviews=_reviews, support_captures=_captures)
