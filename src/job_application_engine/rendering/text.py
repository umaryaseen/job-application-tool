"""UTF-8 text output from a validated document plan."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..verification.document import validate_document_plan


def render_text(
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
) -> str:
    validate_document_plan(plan, profile, reviews=reviews)
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
) -> None:
    Path(path).write_text(render_text(plan, profile, reviews=reviews), encoding="utf-8")
