"""Synthetic TASK-008 integration coverage through the installed ``jae`` entry point."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from tests.test_snapshots import build_inputs

ROOT = Path(__file__).parents[1]


def _write_cli_inputs(root: Path) -> None:
    request, _profile, reviews, capture = build_inputs(root)
    (root / "profile.json").write_text(request.profile.model_dump_json(), encoding="utf-8")
    (root / "plan.json").write_text(request.plan.model_dump_json(), encoding="utf-8")
    (root / "reviews.json").write_text(
        json.dumps([review.model_dump(mode="json") for review in reviews], ensure_ascii=False),
        encoding="utf-8",
    )
    (root / "source.json").write_bytes(request.source_slice)
    (root / "input.pdf").write_bytes(request.pdf)
    (root / "input.txt").write_bytes(request.text)
    (root / "qa.json").write_bytes(request.qa_report)
    captures = root / "captures"
    captures.mkdir()
    (captures / "attestation-one-r1.bin").write_bytes(capture)


def _run_cli(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("jae")
    assert executable is not None, "the installed jae entry point is required"
    environment = os.environ.copy()
    environment["JAE_DATA_DIR"] = str(root)
    return subprocess.run(
        [executable, *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _assert_failure(result: subprocess.CompletedProcess[str], message: str) -> None:
    assert result.returncode != 0
    diagnostic = result.stderr.strip()
    assert diagnostic.startswith("jae:") or "usage:" in diagnostic
    assert message in diagnostic
    assert len(diagnostic) < 2000


def test_snapshot_cli_workflow_and_negative_cases(tmp_path: Path) -> None:
    _write_cli_inputs(tmp_path)
    snapshot_id = "cli-synthetic"
    common_build = (
        "snapshot-build",
        "--profile",
        "profile.json",
        "--plan",
        "plan.json",
        "--reviews",
        "reviews.json",
        "--pdf",
        "input.pdf",
        "--text",
        "input.txt",
        "--qa",
        "qa.json",
        "--source-slice",
        "source.json",
        "--captures-dir",
        "captures",
        "--snapshot-id",
        snapshot_id,
        "--as-of",
        "2026-09-13",
    )

    built = _run_cli(tmp_path, *common_build)
    assert built.returncode == 0, built.stderr
    snapshot = tmp_path / "snapshots" / snapshot_id
    assert snapshot.is_dir()
    assert (snapshot / "manifest.json").is_file()
    assert (snapshot / "profile.json").is_file()
    assert (snapshot / "plan.json").is_file()
    assert (snapshot / "reviews.json").is_file()
    assert (snapshot / "source-slice.json").is_file()
    assert (snapshot / "pdf/output.pdf").read_bytes() == (tmp_path / "input.pdf").read_bytes()
    assert (snapshot / "text/output.txt").read_bytes() == (tmp_path / "input.txt").read_bytes()
    assert not (snapshot / "final-approval.json").exists()

    export_args = (
        "snapshot-export",
        "--snapshot-id",
        snapshot_id,
        "--destination",
        "exports/before-approval",
        "--profile",
        "profile.json",
        "--reviews",
        "reviews.json",
        "--captures-dir",
        "captures",
    )
    before_approval = _run_cli(tmp_path, *export_args)
    _assert_failure(before_approval, "final approval")
    assert not (tmp_path / "exports/before-approval").exists()

    approved = _run_cli(
        tmp_path,
        "snapshot-approve",
        "--snapshot-id",
        snapshot_id,
        "--reviewer-id",
        "synthetic-cli-reviewer",
    )
    assert approved.returncode == 0, approved.stderr
    approval = json.loads((snapshot / "final-approval.json").read_text(encoding="utf-8"))
    manifest_bytes = (snapshot / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    assert approval["reviewer_id"] == "synthetic-cli-reviewer"
    assert approval["snapshot_id"] == snapshot_id
    assert approval["manifest_sha256"] == __import__("hashlib").sha256(manifest_bytes).hexdigest()
    files = {item["path"]: item["sha256"] for item in manifest["files"]}
    assert approval["pdf_sha256"] == files["pdf/output.pdf"]
    assert approval["text_sha256"] == files["text/output.txt"]

    exported = _run_cli(
        tmp_path,
        "snapshot-export",
        "--snapshot-id",
        snapshot_id,
        "--destination",
        "exports/approved",
        "--profile",
        "profile.json",
        "--reviews",
        "reviews.json",
        "--captures-dir",
        "captures",
    )
    assert exported.returncode == 0, exported.stderr
    destination = tmp_path / "exports" / "approved"
    assert (destination / "output.pdf").read_bytes() == (snapshot / "pdf/output.pdf").read_bytes()
    assert (destination / "output.txt").read_bytes() == (snapshot / "text/output.txt").read_bytes()

    missing = _run_cli(tmp_path, "snapshot-build")
    _assert_failure(missing, "required")

    escaped_target = tmp_path.parent / "outside-export"
    escaped_target.write_text("unrelated sentinel", encoding="utf-8")
    escape = _run_cli(
        tmp_path,
        "snapshot-export",
        "--snapshot-id",
        snapshot_id,
        "--destination",
        "../outside-export",
        "--profile",
        "profile.json",
        "--reviews",
        "reviews.json",
        "--captures-dir",
        "captures",
    )
    _assert_failure(escape, "private path")
    assert escaped_target.read_text(encoding="utf-8") == "unrelated sentinel"

    existing_before = (destination / "output.txt").read_bytes()
    existing = _run_cli(
        tmp_path,
        "snapshot-export",
        "--snapshot-id",
        snapshot_id,
        "--destination",
        "exports/approved",
        "--profile",
        "profile.json",
        "--reviews",
        "reviews.json",
        "--captures-dir",
        "captures",
    )
    _assert_failure(existing, "destination exists")
    assert (destination / "output.txt").read_bytes() == existing_before

    pdf_path = snapshot / "pdf/output.pdf"
    pdf_path.write_bytes(pdf_path.read_bytes() + b"tampered")
    tampered = _run_cli(
        tmp_path,
        "snapshot-export",
        "--snapshot-id",
        snapshot_id,
        "--destination",
        "exports/after-tamper",
        "--profile",
        "profile.json",
        "--reviews",
        "reviews.json",
        "--captures-dir",
        "captures",
    )
    _assert_failure(tampered, "manifest hash mismatch")
    assert not (tmp_path / "exports/after-tamper").exists()
