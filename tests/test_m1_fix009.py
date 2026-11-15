"""M1-FIX-009: compact contact block, unbroken skill items, language line format."""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from job_application_engine.domain.evidence import FactApproval, SupportBinding
from job_application_engine.domain.fact import ContactFact, SkillFact
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.profile.review import fact_approval_from_review, record_human_review
from job_application_engine.rendering.pdf import (
    TEMPLATE_VERSION,
    PdfRenderError,
    _items_expression,
    _valid_token_value,
    _yaml_for_plan,
    build_pdf,
    item_problem,
)
from job_application_engine.rendering.presentation import present_plan
from job_application_engine.rendering.text import render_text
from job_application_engine.verification.support import (
    canonical_fact_payload,
    canonical_json,
    evidence_digest,
    fact_digest,
)
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix004 import _assert_complete_extraction

AT = datetime(2026, 9, 12, 13, tzinfo=UTC)
renderer = pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)


def _with_facts(extra: list[dict]):
    """The compact synthetic profile plus locally reviewed extra facts."""

    profile, reviews = approved_baseline()
    source = profile.evidence[0]
    adapter = {"contact": ContactFact, "skill": SkillFact}
    added, bindings = [], []
    for item in extra:
        fact = adapter[item["kind"]].model_validate(
            {
                **item,
                "revision": 1,
                "subject_id": "synthetic-person",
                "status": "approved",
                "approval": FactApproval(
                    fact_sha256="0" * 64,
                    evidence_bundle_sha256="0" * 64,
                    approved_at=AT,
                    reviewer_id="synthetic-reviewer",
                ),
                "evidence_refs": [{"evidence_id": source.evidence_id, "revision": source.revision}],
                "support_binding_refs": [f"binding-{item['fact_id']}"],
            }
        )
        added.append(fact)
        bindings.append(
            SupportBinding.model_validate(
                {
                    "binding_id": f"binding-{fact.fact_id}",
                    "fact_id": fact.fact_id,
                    "fact_revision": 1,
                    "evidence_id": source.evidence_id,
                    "evidence_revision": source.revision,
                    "fact_sha256": fact_digest(fact),
                    "evidence_sha256": evidence_digest(source),
                    "reviewed_scope": f"synthetic {fact.fact_id}",
                    "reviewed_at": datetime(2026, 9, 12, 12, tzinfo=UTC),
                    "reviewer_id": "synthetic-reviewer",
                }
            )
        )
    profile = profile.model_copy(
        update={
            "facts": [*profile.facts, *added],
            "support_bindings": [*profile.support_bindings, *bindings],
        }
    )
    approvals = {}
    for fact in added:
        receipt = record_human_review(
            profile,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=1,
            displayed_content=canonical_json(canonical_fact_payload(fact)),
            review_id=f"review-{fact.fact_id}",
            reviewer_id="synthetic-reviewer",
            reviewed_at=AT,
        )
        reviews.append(receipt)
        approvals[fact.fact_id] = fact_approval_from_review(receipt)
    profile = profile.model_copy(
        update={
            "facts": [
                f.model_copy(update={"approval": approvals[f.fact_id]})
                if f.fact_id in approvals
                else f
                for f in profile.facts
            ]
        }
    )
    return profile, reviews


def _contact(fact_id: str, kind: str, value: str) -> dict:
    return {"fact_id": fact_id, "kind": "contact", "value": {"kind": kind, "value": value}}


CONTACTS = [
    # Fact IDs sort in plan order email, url, phone, location: display reorders.
    _contact("contact-a-url", "url", "https://www.linkedin.com/in/example-synthetic/"),
    _contact("contact-b-phone", "phone", "+49 000 0000"),
    _contact("contact-c-location", "location", "Example City, Example Country"),
    _contact("contact-d-url", "url", "https://example.invalid/portfolio"),
]


def _header(profile, reviews):
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    return plan, present_plan(plan, profile)[0]


def test_contacts_compact_to_location_phone_email_then_each_url() -> None:
    profile, reviews = _with_facts(CONTACTS)
    plan, header = _header(profile, reviews)
    assert [line.text for line in header.lines] == [
        "Synthetic Example",
        "Example City, Example Country | +49 000 0000 | synthetic@example.com",
        "LinkedIn: https://www.linkedin.com/in/example-synthetic/",
        "Url: https://example.invalid/portfolio",
    ]
    assert header.lines[1].items == (
        "Example City, Example Country",
        "+49 000 0000",
        "synthetic@example.com",
    )
    token = _yaml_for_plan(plan, profile)[1]["JAE_HEADER_CONTACTS"]
    assert token["lines"] == [list(line.items) for line in header.lines[1:]]
    assert _valid_token_value(token)
    text = render_text(plan, profile, reviews=reviews)
    assert "Example City, Example Country | +49 000 0000 | synthetic@example.com\n" in text


def test_only_present_contact_kinds_appear() -> None:
    profile, reviews = _with_facts([CONTACTS[0]])
    _, header = _header(profile, reviews)
    assert [line.text for line in header.lines] == [
        "Synthetic Example",
        "synthetic@example.com",
        "LinkedIn: https://www.linkedin.com/in/example-synthetic/",
    ]


def test_language_lines_use_a_colon() -> None:
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    languages = next(s for s in present_plan(plan, profile) if s.label == "Languages")
    assert [line.text for line in languages.lines] == ["German: CEFR B2"]


def test_items_expression_keeps_separators_with_items_and_escapes() -> None:
    expression = _items_expression(["Azure Pipelines", 'a "q" \\ #x [y]', "last"])
    assert expression == (
        '#box[#text("Azure Pipelines |")] '
        '#box[#text("a \\"q\\" \\\\ #x [y] |")] '
        '#box[#text("last")]'
    )


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ({"text": "A | B", "style": "header-contacts", "lines": [["A", "B"]]}, True),
        ({"text": "A | B\nL: u", "style": "header-contacts",
          "lines": [["A", "B"], ["L: u"]]}, True),
        ({"text": "A | B", "style": "header-contacts", "lines": [["A", "C"]]}, False),
        ({"text": "A | B", "style": "header-contacts"}, False),
        ({"text": "A", "style": "header-contacts", "lines": [["A"]], "x": 1}, False),
        ({"text": "", "style": "header-contacts", "lines": [[]]}, False),
        ({"text": "A\nB", "style": "header-contacts", "lines": [["A\nB"]]}, False),
        ({"text": "Programming Languages: A | B", "style": "skill-group",
          "lead": "Programming Languages", "items": ["A", "B"]}, True),
        ({"text": "Programming Languages: A | B", "style": "skill-group",
          "lead": "Programming Languages", "items": ["A | B"]}, True),
        ({"text": "Programming Languages: A | B", "style": "skill-group",
          "lead": "Programming Languages", "items": ["A", "C"]}, False),
        ({"text": "Programming Languages: ", "style": "skill-group",
          "lead": "Programming Languages", "items": []}, False),
        ({"text": "Programming Languages: A", "style": "skill-group",
          "lead": "Programming Languages", "items": "A"}, False),
        ({"text": "Body", "style": "body", "items": ["Body"]}, False),
    ],
)  # fmt: skip
def test_worker_accepts_only_exact_item_shapes(value: dict, valid: bool) -> None:
    assert _valid_token_value(value) is valid


def test_template_identity_changed() -> None:
    assert TEMPLATE_VERSION == "baseline-v7-m1-fix009-compact-contacts"


MULTIWORD = [
    "Azure Pipelines", "ETL Pipelines", "Interactive Data Visualization", "REST APIs",
    "Vector Search", "Model Evaluation", "Prompt Engineering", "Data Validation",
    "AWS CodePipeline", "Azure DevOps", "Document Processing", "LLM Integration",
]  # fmt: skip
CATEGORIES = [
    "Programming languages", "AI & retrieval", "Data processing & analysis",
    "Databases & backend", "Visualization & frontend", "Tools & infrastructure",
    "Quality & development",
]  # fmt: skip


def _skill_profile():
    facts = []
    for group, category in enumerate(CATEGORIES):
        # A different leading item per group shifts every wrap position.
        names = ["Pad" + "d" * (group * 3)] + [f"{name} {group}" for name in MULTIWORD]
        facts.extend(
            {"fact_id": f"skill-g{group}-{i:02d}", "kind": "skill", "name": name,
             "context": "unknown", "category": category}
            for i, name in enumerate(names)
        )  # fmt: skip
    return _with_facts(facts)


@renderer
def test_real_pdf_never_starts_a_line_with_a_separator_or_splits_an_item(tmp_path: Path) -> None:
    profile, reviews = _skill_profile()
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    _assert_complete_extraction(pdf, expected)
    lines = [
        " ".join(line.split())
        for line in subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    ]
    skill_lines = [line for line in lines if " | " in line or line.endswith(" |")]
    assert len(skill_lines) > len(CATEGORIES)  # the groups really wrap
    assert not any(line.startswith("|") for line in lines)
    for group in range(len(CATEGORIES)):
        for name in MULTIWORD:
            item = f"{name} {group}"
            assert any(item in line for line in lines), item


@renderer
def test_real_pdf_compact_contacts_extract_exactly(tmp_path: Path) -> None:
    profile, reviews = _with_facts(CONTACTS)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    poppler, _ = _assert_complete_extraction(pdf, expected)
    compact = "Example City, Example Country | +49 000 0000 | synthetic@example.com"
    assert any(" ".join(line.split()) == compact for line in poppler.splitlines())


@renderer
def test_over_width_item_fails_before_publication(tmp_path: Path) -> None:
    long_name = " ".join(["Unbreakable"] * 30)
    profile, reviews = _with_facts(
        [{"fact_id": "skill-long", "kind": "skill", "name": long_name, "context": "unknown",
          "category": "AI & retrieval"}]
    )  # fmt: skip
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    with pytest.raises(PdfRenderError, match="skill or contact item"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


SINGLE = [
    "Go", "Rust", "Kotlin", "Swift", "Scala", "Elixir", "Haskell", "Erlang", "Julia", "Perl",
    "Lua", "OCaml", "Dart", "Zig", "Nim", "Crystal", "Fortran", "COBOL", "Ada", "Prolog",
]  # fmt: skip


@renderer
def test_real_pdf_single_word_items_never_lead_with_a_separator(tmp_path: Path) -> None:
    # This layout put "|" at the start of two lines with the previous renderer.
    facts = []
    for group, category in enumerate(CATEGORIES):
        names = ["Q" * (1 + (group * 2) % 13)] + [f"{word}{group}0" for word in SINGLE]
        facts.extend(
            {"fact_id": f"skill-s{group}-{i:02d}", "kind": "skill", "name": name,
             "context": "unknown", "category": category}
            for i, name in enumerate(names)
        )  # fmt: skip
    profile, reviews = _with_facts(facts)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    _assert_complete_extraction(pdf, render_text(plan, profile, reviews=reviews))
    lines = [
        " ".join(line.split())
        for line in subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    ]
    assert not any(line.startswith("|") for line in lines)


@renderer
@pytest.mark.parametrize("words", [564, 572, 580, 612])
def test_employment_header_and_its_dates_never_end_a_page_early(tmp_path: Path, words: int) -> None:
    # With the previous rendering these layouts left a header alone at the foot
    # of page 1 (580, 612) or a date line separated from its bullet (564, 572).
    from experiments.renderer.prepare_cases import add_approved_variants
    from tests.test_m1_fix import supported_project_profile

    profile, reviews, captures = supported_project_profile()
    padding = " ".join(["word"] * words) + " end."
    profile, reviews = add_approved_variants(profile, reviews, [("pad", padding)])
    plan = compile_baseline(
        profile, as_of=date(2026, 11, 15), reviews=reviews, support_captures=captures
    )
    pdf = build_pdf(plan, profile, reviews=reviews, support_captures=captures, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews, support_captures=captures)
    _assert_complete_extraction(pdf, expected)
    page = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    last = [line.strip() for line in page.splitlines() if line.strip()][-1]
    # A header always keeps its dates; the engineer's dates keep their bullet.
    # (The analyst entry ends with its dates, so they may legitimately end a page.)
    orphans = (
        "Synthetic Engineer — Example Labs",
        "Synthetic Analyst — Example Labs",
        "January 2022 – ongoing",
    )
    assert not last.startswith(orphans), last


# Review round 1: F-01/F-02 item content, F-03 placeholder collisions.


@pytest.mark.parametrize(
    ("item", "ok"),
    [
        ("Azure Pipelines", True),
        ("A | B", True),  # an inner separator stays inside one unbreakable box
        ("C#", True),
        ("|A", False),
        ("​|A", False),  # invisible character before the separator
        ("   ", False),
        ("​", False),
        (" ", False),
        ("A\rB", False),
        ("A B", False),
        ("A B", False),
        ("A\u0085B", False),
        ("A\tB", False),
        ("A\nB", False),
    ],
)
def test_item_content_rules(item: str, ok: bool) -> None:
    assert (item_problem(item) is None) is ok
    token = {"text": f"Programming Languages: {item}", "style": "skill-group",
             "lead": "Programming Languages", "items": [item]}  # fmt: skip
    assert _valid_token_value(token) is ok


@renderer
@pytest.mark.parametrize(
    "fact",
    [
        {"fact_id": "skill-pipe", "kind": "skill", "name": "|A", "context": "unknown",
         "category": "AI & retrieval"},
        {"fact_id": "skill-ls", "kind": "skill", "name": "A B", "context": "unknown",
         "category": "AI & retrieval"},
        _contact("contact-nel", "location", "Example\u0085City"),
    ],
)  # fmt: skip
def test_unsafe_items_fail_before_publication(tmp_path: Path, fact: dict) -> None:
    profile, reviews = _with_facts([fact])
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    with pytest.raises(PdfRenderError, match="no visible text, contains a control"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


@renderer
def test_text_spelling_a_placeholder_renders_as_literal_text(tmp_path: Path) -> None:
    names = ["JAECLAIM_05_000", "JAECLAIM\\_04\\_000", "JAE_HEADER_NAME", "JAE_HEADER_CONTACTS"]
    profile, reviews = _with_facts(
        [{"fact_id": f"skill-p{i}", "kind": "skill", "name": name, "context": "unknown",
          "category": "AI & retrieval"} for i, name in enumerate(names)]
    )  # fmt: skip
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    assert all(name in expected for name in names)
    _assert_complete_extraction(pdf, expected)
