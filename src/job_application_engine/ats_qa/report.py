"""Machine-readable QA report records."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator

from ..domain.common import Sha256, StrictModel

QAStatus = Literal["pass", "fail", "warn", "not_checked"]


class QACheck(StrictModel):
    """One bounded, reproducible QA measurement."""

    check_id: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    status: QAStatus
    mandatory: bool = True
    measured: Any = None
    expected: Any = None
    tool: str = Field(min_length=1, max_length=100)
    tool_version: str | None = Field(default=None, max_length=300)
    artifact_sha256: Sha256
    diagnostics: list[str] = Field(default_factory=list, max_length=20)


class VisualReview(StrictModel):
    """Manual visual observation, kept separate from automated raster output."""

    status: Literal["pass", "fail", "warn", "not_checked"]
    reviewer_id: str | None = Field(default=None, max_length=100)
    reviewed_at: datetime | None = None
    artifact_sha256: Sha256
    notes: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def observation_requires_identity(self) -> VisualReview:
        if self.status != "not_checked" and (not self.reviewer_id or self.reviewed_at is None):
            raise ValueError("visual observations require reviewer identity and time")
        return self


class QAReport(StrictModel):
    """The complete report; an absent mandatory measurement cannot be a pass."""

    report_version: Literal["1.0"]
    artifact_sha256: Sha256
    artifact_path: str = Field(min_length=1, max_length=1000)
    overall_status: QAStatus
    checks: list[QACheck] = Field(min_length=1, max_length=100)
    visual_review: VisualReview

    def write_json(self, path: str) -> None:
        with Path(path).open("x", encoding="utf-8") as stream:
            stream.write(self.model_dump_json(indent=2) + "\n")
        Path(path).chmod(0o600)


def overall_status(checks: list[QACheck], visual: VisualReview) -> QAStatus:
    """Calculate status without treating warnings or missing checks as passes."""

    if any(check.status == "fail" for check in checks) or visual.status == "fail":
        return "fail"
    if visual.status == "not_checked" or any(
        check.mandatory and check.status == "not_checked" for check in checks
    ):
        return "not_checked"
    if any(check.status in {"warn", "not_checked"} for check in checks):
        return "warn"
    if visual.status == "warn":
        return "warn"
    return "pass"


def record_visual_observation(
    report: QAReport,
    pdf: Path,
    *,
    reviewer_id: str,
    status: Literal["pass", "fail", "warn"],
    notes: str,
) -> QAReport:
    """Record an explicit local observation, not final application approval.

    This is an attributed statement by the caller, not an authenticated human
    identity. Neither raster generation nor imported approval flags invoke it.
    """
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != report.artifact_sha256:
        raise ValueError("PDF changed since QA; visual observation rejected")
    visual = VisualReview(
        status=status,
        reviewer_id=reviewer_id,
        reviewed_at=datetime.now(UTC),
        artifact_sha256=report.artifact_sha256,
        notes=notes,
    )
    return report.model_copy(
        update={"visual_review": visual, "overall_status": overall_status(report.checks, visual)}
    )
