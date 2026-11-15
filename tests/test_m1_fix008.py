"""M1-FIX-008: LinkedIn contact label and compact, extended skill groups."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

from job_application_engine.ats_qa.expected import ExpectedDocument, ExpectedEntry, ExpectedSection
from job_application_engine.ats_qa.pdf import _heading_presentation, _text_checks
from job_application_engine.domain.fact import (
    ContactEmail,
    ContactLocation,
    ContactPhone,
    ContactUrl,
)
from job_application_engine.profile.baseline import (
    URL_CONTACT_LABELS,
    compile_baseline,
    contact_label,
)
from job_application_engine.rendering.pdf import (
    TEMPLATE_VERSION,
    PdfRenderError,
    _contact_url_width_guard,
    _valid_token_value,
    _yaml_for_plan,
    build_pdf,
)
from job_application_engine.rendering.presentation import SKILL_GROUP_HEADINGS, present_plan
from job_application_engine.rendering.text import render_text
from tests.test_document_plan import approved_baseline
from tests.test_m1_fix004 import _assert_complete_extraction, _profile_with_contact_url

# Synthetic LinkedIn paths; the host is the property under test.
LINKEDIN = "https://www.linkedin.com/in/example-synthetic-profile/"

renderer = pytest.mark.skipif(
    shutil.which("sandbox-exec") is None, reason="current-laptop isolation unavailable"
)


@pytest.mark.parametrize(
    "url",
    [
        LINKEDIN,
        "https://linkedin.com/in/example-synthetic",
        "http://WWW.LINKEDIN.COM/in/example-synthetic",
        "https://de.linkedin.com/in/example-synthetic",
        "https://www.linkedin.com:443/in/example-synthetic",
    ],
)
def test_linkedin_hosts_get_the_linkedin_label(url: str) -> None:
    assert contact_label(ContactUrl(kind="url", value=url)) == "LinkedIn"


@pytest.mark.parametrize(
    "url",
    [
        "https://linkedin.com.example.invalid/in/x",
        "https://notlinkedin.com/in/x",
        "https://www.linkedin.com@example.invalid/in/x",
        "https://example.invalid/www.linkedin.com/in/x",
        "https://example.invalid/?next=https://www.linkedin.com/",
        "https://linkedin.co/in/x",
        "https://www.linkedin.com./in/x",
        "https://www.lіnkedin.com/in/x",  # Cyrillic i
        "https://[::1/in/x",  # malformed authority: urlsplit raises
    ],
)
def test_other_urls_keep_the_generic_label(url: str) -> None:
    assert contact_label(ContactUrl(kind="url", value=url)) == "Url"


def test_non_url_contacts_keep_their_kind_labels() -> None:
    assert contact_label(ContactEmail(kind="email", value="a@example.invalid")) == "Email"
    assert contact_label(ContactPhone(kind="phone", value="+49 000")) == "Phone"
    assert contact_label(ContactLocation(kind="location", value="Example City")) == "Location"


def test_linkedin_label_flows_through_plan_display_and_text() -> None:
    profile, reviews = _profile_with_contact_url(LINKEDIN)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    contact = next(s for s in plan.sections if s.section_id == "contact")
    assert f"LinkedIn: {LINKEDIN}" in [line.text for line in contact.lines]
    header = present_plan(plan, profile)[0]
    assert f"LinkedIn: {LINKEDIN}" in [line.text for line in header.lines]
    text = render_text(plan, profile, reviews=reviews)
    assert f"LinkedIn: {LINKEDIN}" in text
    assert "Url:" not in text


def test_url_width_guard_covers_every_url_label() -> None:
    assert URL_CONTACT_LABELS == ("Url", "LinkedIn")
    for label in URL_CONTACT_LABELS:
        guard = _contact_url_width_guard(f"{label}: https://example.invalid/x")
        assert guard.count("panic(") == 1 and f"{label}: https://example.invalid/x" in guard
    assert _contact_url_width_guard("Email: a@example.invalid\nPhone: +49 000") == ""


@renderer
def test_over_width_linkedin_url_fails_before_publication(tmp_path: Path) -> None:
    url = "https://www.linkedin.com/in/" + ("synthetic-component-" * 40)
    profile, reviews = _profile_with_contact_url(url)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    with pytest.raises(PdfRenderError, match="contact URL.*fixed A4"):
        build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    assert not (tmp_path / "outputs" / "baseline.pdf").exists()


INTERNAL = [
    "Quality & development",
    "Tools & infrastructure",
    "Programming languages",
    "Visualization & frontend",
    "Databases & backend",
    "AI & retrieval",
    "Programming languages",
    "Unlisted category",
]


def _profile_with_all_groups():
    """Display-policy fixture: extras are added after compiling (never validated)."""
    profile, reviews = approved_baseline()
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    original = next(f for f in profile.facts if f.fact_id == "skill-german")
    extra = [
        original.model_copy(
            update={
                "fact_id": f"skill-{i}",
                "name": name,
                "category": category,
                "context": "unknown",
                "notes": None,
            }
        )
        for i, (name, category) in enumerate(
            zip(
                ["pre-commit", "CI/CD", "Zeta", "Three.js", "Flask", "RAG", "Alpha", "Loose"],
                INTERNAL,
                strict=True,
            )
        )
    ]
    profile = profile.model_copy(update={"facts": [*profile.facts, *extra]})
    section = next(s for s in plan.sections if s.section_id == "skills")
    template = section.lines[0]
    lines = [
        *section.lines,
        *(
            template.model_copy(
                update={"fact_ref": template.fact_ref.model_copy(update={"fact_id": f.fact_id})}
            )
            for f in extra
        ),
    ]
    plan = plan.model_copy(
        update={
            "sections": [
                s.model_copy(update={"lines": lines}) if s.section_id == "skills" else s
                for s in plan.sections
            ]
        }
    )
    return profile, plan


def test_compact_groups_in_fixed_order_with_static_leads() -> None:
    profile, plan = _profile_with_all_groups()
    skills = next(s for s in present_plan(plan, profile) if s.label == "Skills")
    groups = [line for line in skills.lines if line.style == "skill-group"]
    assert [line.lead for line in groups] == [
        "Programming Languages",
        "AI & Machine Learning",
        "Data Engineering & Analytics",
        "Backend & Databases",
        "Frontend & Visualization",
        "Cloud & Infrastructure",
        "Quality & Development",
    ]
    assert {line.lead for line in groups} == SKILL_GROUP_HEADINGS
    by_lead = {line.lead: line.text for line in groups}
    assert by_lead["Programming Languages"] == "Programming Languages: Alpha | Zeta"
    assert by_lead["Quality & Development"] == "Quality & Development: pre-commit"
    assert by_lead["Backend & Databases"] == "Backend & Databases: Flask"
    assert not any(line.style == "subheading" for line in skills.lines)
    # A skill appears once; an unlisted category stays an ungrouped line after the groups.
    assert skills.lines[-1].text == "Loose" and skills.lines[-1].style == "body"
    assert sum(line.text.count("Alpha") for line in skills.lines) == 1


def test_tokens_carry_static_leads_only_for_skill_groups() -> None:
    profile, plan = _profile_with_all_groups()
    tokens = _yaml_for_plan(plan, profile)[1]
    groups = [v for v in tokens.values() if v["style"] == "skill-group"]
    assert {v["lead"] for v in groups} == SKILL_GROUP_HEADINGS
    assert all(v["text"].startswith(f"{v['lead']}: ") for v in groups)
    assert all(set(v) == {"text", "style"} for v in tokens.values() if v["style"] != "skill-group")
    assert all(_valid_token_value(v) for v in tokens.values())


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ({"text": "Body", "style": "body"}, True),
        ({"text": "Programming Languages: Python", "style": "skill-group",
          "lead": "Programming Languages"}, True),
        ({"text": "Programming Languages: Python", "style": "skill-group"}, False),
        ({"text": "Python", "style": "skill-group", "lead": "Programming Languages"}, False),
        ({"text": "Programming LanguagesX: Python", "style": "skill-group",
          "lead": "Programming Languages"}, False),
        ({"text": "Invented: Python", "style": "skill-group", "lead": "Invented"}, False),
        ({"text": ": Python", "style": "skill-group", "lead": ""}, False),
        ({"text": "Body", "style": "body", "lead": "Programming Languages"}, False),
        ({"text": "Body", "style": "body", "extra": 1}, False),
        ({"text": "Body", "style": "unknown"}, False),
        ({"text": 1, "style": "body"}, False),
        (["Body", "body"], False),
    ],
)  # fmt: skip
def test_worker_accepts_only_exact_token_shapes(value: object, valid: bool) -> None:
    assert _valid_token_value(value) is valid


def test_template_identity_changed() -> None:
    assert TEMPLATE_VERSION == "baseline-v6-m1-fix008-display-labels"


@renderer
def test_real_pdf_compact_groups_and_linkedin_extract_exactly(tmp_path: Path) -> None:
    profile, reviews = _profile_with_contact_url(LINKEDIN)
    plan = compile_baseline(profile, as_of=date(2026, 11, 15), reviews=reviews)
    pdf = build_pdf(plan, profile, reviews=reviews, data_root=tmp_path)
    expected = render_text(plan, profile, reviews=reviews)
    assert "Data Engineering & Analytics: " in expected
    assert f"LinkedIn: {LINKEDIN}" in expected
    _assert_complete_extraction(pdf, expected)
    lead = "Data Engineering & Analytics"
    with pytest.raises(AssertionError):
        _assert_complete_extraction(pdf, expected.replace(f"{lead}: ", f"{lead}\n"))


# QA heading detection: a group heading ending in a section label is not a heading.
def _oracle() -> ExpectedDocument:
    return ExpectedDocument(
        required_identity="Synthetic Example",
        sections=[
            ExpectedSection(
                label="Contact",
                heading_visible=False,
                entries=[ExpectedEntry(entry_id="name", text="Synthetic Example")],
            ),
            ExpectedSection(
                label="Skills",
                entries=[
                    ExpectedEntry(entry_id="g1", text="Programming Languages: Alpha | Zeta"),
                    ExpectedEntry(entry_id="g2", text="Quality & Development: pre-commit"),
                ],
            ),
            ExpectedSection(
                label="Languages",
                entries=[ExpectedEntry(entry_id="l1", text="German (A1-A2)")],
            ),
        ],
        expected_pages=1,
    )


GOOD = (
    "Synthetic Example\nSkills\nProgramming Languages: Alpha | Zeta\n"
    "Quality & Development: pre-commit\nLanguages\nGerman (A1-A2)\n"
)


def _status(text: str) -> dict[str, bool]:
    return {key: value[0] for key, value in _text_checks(text, _oracle()).items()}


def test_group_heading_containing_a_label_does_not_split_its_section() -> None:
    result = _status(GOOD)
    assert result["standard_headings"] and result["entry_claim_sequence"]
    assert result["complete_text"]


@pytest.mark.parametrize(
    "text",
    [
        GOOD.replace("\nLanguages\n", "\n"),  # real heading missing
        GOOD.replace("\nLanguages\n", "\nLanguages German\n"),  # not a whole line
        GOOD.replace("Skills\n", "Skills\nLanguages\n"),  # duplicate heading line
        GOOD.replace("Skills\n", "").replace("Languages\n", "Languages\nSkills\n"),  # order
    ],
)
def test_missing_ambiguous_or_misordered_headings_fail(text: str) -> None:
    assert not _status(text)["standard_headings"]
    assert not _status(text)["entry_claim_sequence"]


def test_entry_outside_its_section_is_not_found() -> None:
    moved = GOOD.replace("Quality & Development: pre-commit\n", "").replace(
        "German (A1-A2)\n", "German (A1-A2)\nQuality & Development: pre-commit\n"
    )
    result = _status(moved)
    assert result["standard_headings"] and not result["entry_claim_sequence"]


# Round 2 F-01: text cannot tell a body line "Languages" from the heading, so a
# separate presentation check uses Poppler word geometry.
def _xml(lines: list[tuple[str, float, float]], pages: int = 1) -> str:
    """Synthetic -bbox-layout XML; each line is (text, top, word height)."""
    body = []
    per_page = max(1, len(lines) // pages + (len(lines) % pages > 0))
    for page in range(pages):
        chunk = lines[page * per_page : (page + 1) * per_page]
        flows = []
        for text, top, height in chunk:
            words = "".join(
                f'<word xMin="{50 + 40 * i}" yMin="{top}" xMax="{80 + 40 * i}" '
                f'yMax="{top + height}">{escape(word)}</word>'
                for i, word in enumerate(text.split())
            )
            flows.append(f"<flow><block><line>{words}</line></block></flow>")
        body.append(f'<page width="595" height="842">{"".join(flows)}</page>')
    return f"<html><body><doc>{''.join(body)}</doc></body></html>"


BODY = [
    ("Synthetic Example", 40, 12.9),
    ("Skills", 80, 18.1),
    ("Programming Languages: Alpha | Zeta", 110, 12.9),
    ("Quality & Development: pre-commit", 130, 12.9),
    ("Languages", 160, 18.1),
    ("German (A1-A2)", 190, 12.9),
]


def _presented(lines: list[tuple[str, float, float]], pages: int = 1) -> bool:
    return _heading_presentation(_xml(lines, pages), _oracle())[0]


def test_text_level_cannot_see_a_body_sized_heading_but_presentation_can() -> None:
    text = "Synthetic Example\nSkills\nProgramming Languages: Alpha | Zeta\n"
    text += "Quality & Development: pre-commit\nLanguages\nGerman (A1-A2)\n"
    assert all(_status(text)[key] for key in ("standard_headings", "entry_claim_sequence"))
    assert _presented(BODY)
    body_sized = [line if line[0] != "Languages" else ("Languages", 160, 12.9) for line in BODY]
    assert not _presented(body_sized)


@pytest.mark.parametrize(
    "lines",
    [
        [line for line in BODY if line[0] != "Languages"],  # heading missing
        [*BODY, ("Languages", 220, 18.1)],  # two heading-sized lines
        [("Languages", 60, 18.1) if line[0] == "Languages" else line for line in BODY],  # order
        [("Skills Languages", 80, 18.1) if line[0] == "Skills" else line for line in BODY],
        [("Skills", 80, 15.0) if line[0] == "Skills" else line for line in BODY],  # 1.16x
        [],
    ],
)
def test_presentation_fails_closed(lines: list[tuple[str, float, float]]) -> None:
    assert not _presented(lines)


def test_presentation_order_spans_pages_and_reports_measurements() -> None:
    assert _presented(BODY, pages=2)
    passed, measured = _heading_presentation(_xml(BODY), _oracle())
    assert passed and measured["invalid_word_boxes"] == 0
    assert [h["label"] for h in measured["headings"]] == ["Skills", "Languages"]
    assert all(
        h["section_body_height_pt"] == 12.9 and h["ratio"] > 1.2 for h in measured["headings"]
    )


# Round 3 F-01: invalid geometry fails closed, never crashes; F-02: the reference
# is each heading's own section body, so short documents and a large name pass.
@pytest.mark.parametrize("height", [0.0, -1.0, "nan", "inf"])
def test_invalid_word_boxes_fail_closed(height) -> None:
    xml = _xml(BODY).replace(
        'yMax="52.9"', f'yMax="{height}"' if isinstance(height, str) else f'yMax="{40 + height}"'
    )
    assert 'yMax="52.9"' not in xml
    passed, measured = _heading_presentation(xml, _oracle())
    assert not passed and measured["invalid_word_boxes"] >= 1


def test_all_zero_geometry_does_not_raise() -> None:
    flat = [(text, top, 0.0) for text, top, _ in BODY]
    assert _heading_presentation(_xml(flat), _oracle())[0] is False


def _one_section() -> ExpectedDocument:
    return ExpectedDocument(
        required_identity="Synthetic Example",
        sections=[
            ExpectedSection(label="Contact", heading_visible=False,
                            entries=[ExpectedEntry(entry_id="name", text="Synthetic Example")]),
            ExpectedSection(label="Skills", entries=[ExpectedEntry(entry_id="g", text="Alpha")]),
        ],
        expected_pages=1,
    )  # fmt: skip


def test_sparse_documents_and_a_large_name_pass() -> None:
    sparse = [("Synthetic Example", 40, 35.2), ("Skills", 80, 18.1), ("Alpha", 110, 12.9),
              ("Languages", 140, 18.1), ("German", 170, 12.9)]  # fmt: skip
    assert _presented(sparse)
    one = [("Synthetic Example", 40, 35.2), ("Skills", 80, 18.1), ("Alpha", 110, 12.9)]
    assert _heading_presentation(_xml(one), _one_section())[0]


def test_heading_without_a_section_body_fails() -> None:
    assert not _heading_presentation(_xml([("Skills", 80, 18.1)]), _one_section())[0]
    tail = [line for line in BODY if line[0] != "German (A1-A2)"]
    assert not _presented(tail)
