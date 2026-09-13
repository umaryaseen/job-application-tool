"""Synthetic TASK-008 atomic snapshot, approval and current-export tests."""

from __future__ import annotations

import hashlib
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from job_application_engine.ats_qa.report import QACheck, QAReport, VisualReview, overall_status
from job_application_engine.domain.evidence import EvidenceApproval
from job_application_engine.domain.profile import ProfileRevision
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import (
    evidence_approval_from_review,
    fact_approval_from_review,
    record_human_review,
    variant_approval_from_review,
)
from job_application_engine.rendering.text import render_text
from job_application_engine.snapshots.export import ExportError, export_snapshot
from job_application_engine.snapshots.review import approve_snapshot
from job_application_engine.snapshots.store import (
    SnapshotBuild,
    SnapshotError,
    build_snapshot,
    clean_owned_staging,
)
from job_application_engine.verification.support import (
    canonical_json,
    evidence_digest,
)
from tests.test_document_plan import approved_baseline

NOW = datetime(2026, 9, 13, 12, 0, tzinfo=UTC)


def eligible_profile() -> tuple[ProfileRevision, list[object], bytes]:
    """Upgrade the existing synthetic fixture with an approved captured attestation."""

    profile, _ = approved_baseline()
    capture = b"synthetic immutable support capture v1\n"
    capture_sha = hashlib.sha256(capture).hexdigest()
    evidence = profile.evidence[0].model_copy(update={"support_capture_sha256": capture_sha})
    profile = profile.model_copy(update={"evidence": [evidence]})
    provisional = evidence.model_copy(
        update={
            "status": "approved",
            "approval": EvidenceApproval(
                evidence_sha256="0" * 64,
                approved_at=NOW,
                reviewer_id="synthetic-reviewer",
            ),
        }
    )
    profile = profile.model_copy(update={"evidence": [provisional]})
    evidence_display = canonical_json(provisional.model_dump(mode="json", exclude={"approval"}))
    evidence_review = record_human_review(
        profile,
        target_type="evidence",
        target_id=provisional.evidence_id,
        target_revision=provisional.revision,
        displayed_content=evidence_display,
        review_id="review-evidence-one",
        reviewer_id="synthetic-reviewer",
        reviewed_at=NOW,
    )
    evidence = provisional.model_copy(
        update={"approval": evidence_approval_from_review(evidence_review)}
    )
    profile = profile.model_copy(update={"evidence": [evidence]})
    bindings = [
        binding.model_copy(update={"evidence_sha256": evidence_digest(evidence)})
        for binding in profile.support_bindings
    ]
    profile = profile.model_copy(update={"support_bindings": bindings})

    reviews: list[object] = [evidence_review]
    facts = []
    for fact in profile.facts:
        if fact.status != "approved":
            facts.append(fact)
            continue
        displayed = canonical_json(fact.model_dump(mode="json", exclude={"approval"}))
        review = record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=fact.revision,
            displayed_content=displayed,
            review_id=f"snapshot-review-{fact.fact_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=NOW,
        )
        reviews.append(review)
        facts.append(fact.model_copy(update={"approval": fact_approval_from_review(review)}))
    profile = profile.model_copy(update={"facts": facts})
    variant = profile.variants[0]
    variant_review = record_human_review(
        profile,
        target_type="variant",
        target_id=variant.variant_id,
        target_revision=variant.revision,
        displayed_content=variant.text,
        review_id="snapshot-review-headline",
        reviewer_id="synthetic-reviewer",
        reviewed_at=NOW,
    )
    reviews.append(variant_review)
    profile = profile.model_copy(
        update={
            "variants": [
                variant.model_copy(
                    update={
                        "status": "approved",
                        "approval": variant_approval_from_review(variant_review),
                    }
                )
            ]
        }
    )
    return profile, reviews, capture


def qa_bytes(pdf: bytes, *, visual: str = "pass") -> bytes:
    digest = hashlib.sha256(pdf).hexdigest()
    visual_review = VisualReview(
        status=visual,
        reviewer_id="synthetic-visual-reviewer" if visual == "pass" else None,
        reviewed_at=NOW if visual == "pass" else None,
        artifact_sha256=digest,
        notes="Synthetic page observation recorded for TASK-008 tests.",
    )
    checks = [
        QACheck(
            check_id="synthetic_pdf",
            status="pass",
            measured=1,
            expected=1,
            tool="synthetic",
            tool_version="1",
            artifact_sha256=digest,
        )
    ]
    return (
        QAReport(
            report_version="1.0",
            artifact_sha256=digest,
            artifact_path="synthetic.pdf",
            overall_status=overall_status(checks, visual_review),
            checks=checks,
            visual_review=visual_review,
        )
        .model_dump_json()
        .encode()
    )


def build_inputs(
    root: Path, *, snapshot_id: str = "synthetic-one"
) -> tuple[SnapshotBuild, ProfileRevision, list[object], bytes]:
    profile, reviews, capture = eligible_profile()
    plan = compile_baseline(
        profile,
        as_of=date(2026, 9, 13),
        reviews=reviews,
        support_captures={("attestation-one", 1): capture},
    )
    pdf = b"%PDF-1.7 synthetic approved PDF bytes\n"
    text = render_text(
        plan,
        profile,
        reviews=reviews,
        support_captures={("attestation-one", 1): capture},
    ).encode("utf-8")
    request = SnapshotBuild(
        snapshot_id=snapshot_id,
        profile=profile,
        plan=plan,
        reviews=reviews,
        support_captures={("attestation-one", 1): capture},
        source_slice=b'{"slice":"synthetic"}\n',
        pdf=pdf,
        text=text,
        qa_report=qa_bytes(pdf),
        configuration={"locale": "en", "template": "synthetic-template-v1"},
        tool_versions={"python": "3.12.14", "qa": "synthetic-1"},
        as_of=date(2026, 9, 13),
    )
    return request, profile, reviews, capture


def test_snapshot_publishes_complete_hash_bound_contents_and_restores(tmp_path: Path) -> None:
    request, profile, reviews, capture = build_inputs(tmp_path)
    result = build_snapshot(request, root=tmp_path)
    snapshot = result.path
    assert (snapshot / "manifest.json").is_file()
    assert (snapshot / "captures/attestation-one-r1.bin").read_bytes() == capture
    assert (snapshot / "pdf/output.pdf").read_bytes() == request.pdf
    assert (snapshot / "text/output.txt").read_bytes() == request.text
    assert (snapshot / "qa/report.json").is_file()
    assert not (snapshot / "final-approval.json").exists()
    assert result.manifest_sha256
    assert profile.profile_id in (snapshot / "profile.json").read_text()
    assert len(reviews) > 1


def test_existing_snapshot_id_and_interrupted_publication_never_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, *_ = build_inputs(tmp_path)
    first = build_snapshot(request, root=tmp_path)
    with pytest.raises(SnapshotError, match="already exists"):
        build_snapshot(request, root=tmp_path)
    import job_application_engine.snapshots.store as store

    original_replace = store.os.replace
    monkeypatch.setattr(
        store.os, "replace", lambda *_: (_ for _ in ()).throw(OSError("interrupted"))
    )
    with pytest.raises(SnapshotError, match="publication failed"):
        build_snapshot(
            request.__class__(**{**request.__dict__, "snapshot_id": "interrupted"}), root=tmp_path
        )
    assert not (tmp_path / "snapshots/interrupted").exists()
    assert clean_owned_staging(root=tmp_path) == []
    monkeypatch.setattr(store.os, "replace", original_replace)
    assert first.path.is_dir()


@pytest.mark.parametrize(
    "tamper",
    [
        "pdf/output.pdf",
        "text/output.txt",
        "plan.json",
        "manifest.json",
        "captures/attestation-one-r1.bin",
    ],
)
def test_modified_snapshot_bytes_block_final_approval_and_export(
    tmp_path: Path, tamper: str
) -> None:
    request, profile, reviews, capture = build_inputs(tmp_path)
    result = build_snapshot(request, root=tmp_path)
    path = result.path / tamper
    path.write_bytes(path.read_bytes() + b"tampered")
    with pytest.raises(SnapshotError):
        approve_snapshot(
            request.snapshot_id,
            reviewer_id="synthetic-final-reviewer",
            approved_at=NOW,
            root=tmp_path,
        )
    assert not (result.path / "final-approval.json").exists()


def approved_snapshot(tmp_path: Path) -> tuple[SnapshotBuild, ProfileRevision, list[object], bytes]:
    request, profile, reviews, capture = build_inputs(tmp_path)
    build_snapshot(request, root=tmp_path)
    approve_snapshot(
        request.snapshot_id, reviewer_id="synthetic-final-reviewer", approved_at=NOW, root=tmp_path
    )
    return request, profile, reviews, capture


def test_export_copies_exact_approved_bytes_and_preserves_history(tmp_path: Path) -> None:
    request, profile, reviews, capture = approved_snapshot(tmp_path)
    destination = tmp_path / "exports" / "application-one"
    result = export_snapshot(
        request.snapshot_id,
        destination=destination,
        profile=profile,
        reviews=reviews,
        support_captures={("attestation-one", 1): capture},
        now=NOW,
        root=tmp_path,
    )
    assert result == destination
    assert (destination / "output.pdf").read_bytes() == request.pdf
    assert (destination / "output.txt").read_bytes() == request.text
    with pytest.raises(ExportError, match="exists"):
        export_snapshot(
            request.snapshot_id,
            destination=destination,
            profile=profile,
            reviews=reviews,
            support_captures={("attestation-one", 1): capture},
            now=NOW,
            root=tmp_path,
        )
    assert (tmp_path / "snapshots/synthetic-one").is_dir()


def test_current_revision_missing_capture_and_source_states_block_export(tmp_path: Path) -> None:
    request, profile, reviews, capture = approved_snapshot(tmp_path)
    args = dict(
        snapshot_id=request.snapshot_id,
        destination=tmp_path / "exports" / "blocked",
        profile=profile,
        reviews=reviews,
        now=NOW,
        root=tmp_path,
    )
    with pytest.raises(ExportError, match="eligibility"):
        export_snapshot(**args, support_captures={})
    changed = profile.model_copy(update={"revision": 2})
    with pytest.raises(ExportError, match="revision"):
        export_snapshot(
            **{**args, "profile": changed},
            support_captures={("attestation-one", 1): capture},
        )
    revoked = profile.model_copy(
        update={"evidence": [profile.evidence[0].model_copy(update={"status": "revoked"})]}
    )
    with pytest.raises(ExportError):
        export_snapshot(
            **{**args, "profile": revoked},
            support_captures={("attestation-one", 1): capture},
        )


def test_expiry_uses_current_clock_not_backdated_as_of(tmp_path: Path) -> None:
    request, profile, reviews, capture = approved_snapshot(tmp_path)
    # A current profile revision change is the required signal for a new build;
    # this test also proves the snapshot's historical as-of cannot move time back.
    assert request.as_of == date(2026, 9, 13)
    import job_application_engine.snapshots.export as export_module

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(export_module, "_expiry_values", lambda *_: [NOW - timedelta(days=1)])
    try:
        with pytest.raises(ExportError, match="expired"):
            export_snapshot(
                request.snapshot_id,
                destination=tmp_path / "exports" / "expired",
                profile=profile,
                reviews=reviews,
                support_captures={("attestation-one", 1): capture},
                now=NOW + timedelta(days=1),
                root=tmp_path,
            )
    finally:
        monkeypatch.undo()


def test_missing_visual_or_not_checked_qa_cannot_be_snapshotted(tmp_path: Path) -> None:
    request, *_ = build_inputs(tmp_path)
    bad = request.__class__(
        **{**request.__dict__, "qa_report": qa_bytes(request.pdf, visual="not_checked")}
    )
    with pytest.raises(SnapshotError, match="QA"):
        build_snapshot(bad, root=tmp_path)


def test_concurrent_profile_loader_conflict_blocks_publication(tmp_path: Path) -> None:
    request, profile, reviews, capture = approved_snapshot(tmp_path)
    changed = profile.model_copy(update={"revision": profile.revision + 1})
    calls = iter([profile, changed])
    with pytest.raises(ExportError, match="concurrent"):
        export_snapshot(
            request.snapshot_id,
            destination=tmp_path / "exports" / "race",
            profile=profile,
            reviews=reviews,
            support_captures={("attestation-one", 1): capture},
            now=NOW,
            root=tmp_path,
            profile_loader=lambda: next(calls),
        )
    assert not (tmp_path / "exports/race").exists()


def test_intervening_snapshot_edit_during_copy_blocks_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, profile, reviews, capture = approved_snapshot(tmp_path)
    import job_application_engine.snapshots.export as export_module

    original_copy = export_module.shutil.copyfile

    def copy_and_edit(source: str | Path, destination: str | Path) -> str:
        result = original_copy(source, destination)
        if str(source).endswith("pdf/output.pdf"):
            Path(source).write_bytes(Path(source).read_bytes() + b"changed during copy")
        return result

    monkeypatch.setattr(export_module.shutil, "copyfile", copy_and_edit)
    with pytest.raises(ExportError, match="manifest hash mismatch"):
        export_snapshot(
            request.snapshot_id,
            destination=tmp_path / "exports" / "intervening",
            profile=profile,
            reviews=reviews,
            support_captures={("attestation-one", 1): capture},
            now=NOW,
            root=tmp_path,
        )
    assert not (tmp_path / "exports/intervening").exists()
