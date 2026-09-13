"""UTF-8 text output from a validated document plan."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..verification.document import validate_document_plan
from ..verification.support import EvidenceKey


def render_text(
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path] | None = None,
) -> str:
    validate_document_plan(plan, profile, reviews=reviews, support_captures=support_captures)
    blocks = [
        "\n".join([section.label, *(line.text for line in section.lines)])
        for section in plan.sections
    ]
    return "\n\n".join(blocks) + "\n"


def write_text(
    path: str | Path,
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path] | None = None,
) -> None:
    Path(path).write_text(
        render_text(plan, profile, reviews=reviews, support_captures=support_captures),
        encoding="utf-8",
    )
