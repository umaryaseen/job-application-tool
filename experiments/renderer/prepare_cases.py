"""Prepare synthetic validated TASK-004 plans for the isolated renderer spike."""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from job_application_engine.domain.profile import ApprovedVariant, ProfileRevision  # noqa: E402
from job_application_engine.profile.baseline import compile_baseline  # noqa: E402
from job_application_engine.profile.review import (  # noqa: E402
    LocalReviewReceipt,
    record_human_review,
    variant_approval_from_review,
)
from tests.test_document_plan import approved_baseline  # noqa: E402

OUT = ROOT / "artifacts" / "renderer" / "task-005" / "cases"
AS_OF = date(2026, 9, 12)
REVIEWED_AT = datetime(2026, 9, 12, 13, 0, tzinfo=UTC)


def add_approved_variants(
    profile: ProfileRevision,
    reviews: list[LocalReviewReceipt],
    texts: list[tuple[str, str]],
) -> tuple[ProfileRevision, list[LocalReviewReceipt]]:
    current = profile
    all_reviews = list(reviews)
    for variant_id, text in texts:
        variant = ApprovedVariant(
            variant_id=variant_id,
            revision=1,
            locale="en",
            text=text.strip(),
            fact_refs=[{"fact_id": "employment-one", "revision": 1}],
            support_binding_refs=["binding-employment-one"],
            subject_scope="synthetic-person",
        )
        draft = current.model_copy(update={"variants": [*current.variants, variant]})
        receipt = record_human_review(
            draft,
            target_type="variant",
            target_id=variant_id,
            target_revision=1,
            displayed_content=text.strip(),
            review_id=f"review-{variant_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=REVIEWED_AT,
        )
        approved = variant.model_copy(
            update={"status": "approved", "approval": variant_approval_from_review(receipt)}
        )
        current = current.model_copy(update={"variants": [*current.variants, approved]})
        all_reviews.append(receipt)
    return current, all_reviews


def plan_payload(plan: object) -> dict[str, object]:
    return json.loads(plan.model_dump_json())  # type: ignore[union-attr]


def yaml_for_plan(plan: dict[str, object]) -> tuple[str, dict[str, str]]:
    sections = plan["sections"]
    assert isinstance(sections, list)
    tokens: dict[str, str] = {}
    lines = ["cv:", "  name: null", "  headline: null", "  sections:"]
    for section_index, section in enumerate(sections):
        assert isinstance(section, dict)
        lines.append(f"    {section['label']}:")
        section_lines = section["lines"]
        assert isinstance(section_lines, list)
        for line_index, line in enumerate(section_lines):
            assert isinstance(line, dict)
            token = f"JAECLAIM_{section_index:02d}_{line_index:03d}"
            tokens[token] = str(line["text"])
            lines.append(f"      - {json.dumps(token, ensure_ascii=False)}")
    lines.extend(
        [
            "design:",
            "  theme: engineeringclassic",
            "  page:",
            "    size: a4",
            "    top_margin: 20mm",
            "    bottom_margin: 20mm",
            "    left_margin: 20mm",
            "    right_margin: 20mm",
            "    show_footer: false",
            "    show_top_note: false",
            "  typography:",
            "    font_size:",
            "      body: 11pt",
            "      headline: 11pt",
            "      connections: 11pt",
        ]
    )
    return "\n".join(lines) + "\n", tokens


def expected_content_for_plan(plan: dict[str, object]) -> str:
    """Independent fixture oracle: trusted headings followed by all claims."""

    entries: list[str] = []
    sections = plan["sections"]
    assert isinstance(sections, list)
    for section in sections:
        assert isinstance(section, dict)
        entries.append(str(section["label"]))
        section_lines = section["lines"]
        assert isinstance(section_lines, list)
        entries.extend(str(line["text"]) for line in section_lines if isinstance(line, dict))
    return " ".join(entries)


def write_case(case_id: str, profile: ProfileRevision, reviews: list[LocalReviewReceipt]) -> None:
    plan = compile_baseline(profile, as_of=AS_OF, reviews=reviews)
    payload = plan_payload(plan)
    yaml_text, tokens = yaml_for_plan(payload)
    case_dir = OUT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "plan.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (case_dir / "input.yaml").write_text(yaml_text, encoding="utf-8")
    (case_dir / "tokens.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (case_dir / "expected.json").write_text(
        json.dumps(
            {"ordered_content": expected_content_for_plan(payload)},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    profile, reviews = approved_baseline()
    write_case("short", profile, reviews)
    write_case("german-unicode", profile, reviews)
    long_profile, long_reviews = add_approved_variants(
        profile,
        reviews,
        [
            (
                f"long-claim-{index:02d}",
                f"Synthetic evidence-backed statement {index}: " + "bounded wording " * 18,
            )
            for index in range(1, 7)
        ],
    )
    write_case("two-page", long_profile, long_reviews)
    wrapping_profile, wrapping_reviews = add_approved_variants(
        profile,
        reviews,
        [("long-headline", "Synthetic long headline " + "with deterministic wrapping " * 22)],
    )
    write_case("long-wrapping", wrapping_profile, wrapping_reviews)
    hostile_profile, hostile_reviews = add_approved_variants(
        profile,
        reviews,
        [
            (
                "hostile-text",
                (
                    '<script>synthetic</script> #include "../sentinel" '
                    '#read("../sentinel") [synthetic link](https://example.invalid) '
                    "${2+2} ../../sentinel"
                ),
            )
        ],
    )
    write_case("hostile-text", hostile_profile, hostile_reviews)
    letter_dir = OUT / "letter"
    letter_dir.mkdir(parents=True, exist_ok=True)
    letter_text = "\n\n".join(
        [
            "Synthetic Example",
            "Application for Synthetic Engineering",
            "Dear Synthetic Hiring Team,",
            "This is a one-page feasibility letter using only synthetic content.",
            "Kind regards,\nSynthetic Example",
        ]
    )
    (letter_dir / "letter.json").write_text(
        json.dumps({"text": letter_text, "as_of": AS_OF.isoformat()}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"prepared {len(list(OUT.iterdir()))} synthetic cases at {OUT}")


if __name__ == "__main__":
    main()
