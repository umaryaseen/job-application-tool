"""TASK-013 reviewed exact skill-alias normalization (A21)."""

from __future__ import annotations

import hashlib
import json
import time
import unicodedata
from pathlib import Path

import pytest

from job_application_engine.extraction.classification import classify_requirements
from job_application_engine.extraction.rules import extract_requirements
from job_application_engine.ingestion.text import ingest_job
from job_application_engine.normalization.aliases import (
    NormalizationError,
    SkillMention,
    find_mentions,
    normalize_classification,
    normalize_surface,
    relations_of,
    validate_dictionary,
)
from job_application_engine.normalization.dictionary import CONCEPTS, Alias, Concept, Relation

FIXTURE = Path(__file__).parent / "fixtures/normalization/aliases.json"
ORACLE = json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", ORACLE["scan_cases"], ids=[c["id"] for c in ORACLE["scan_cases"]])
def test_independently_reviewed_scan_oracle(case) -> None:
    mentions = find_mentions(case["text"])
    assert [
        {"quote": m.span.quote, "concept": m.concept_id, "status": m.status} for m in mentions
    ] == case["expected"]
    for mention in mentions:
        assert case["text"][mention.span.start : mention.span.end] == mention.span.quote


@pytest.mark.parametrize(
    "case", ORACLE["surface_cases"], ids=[repr(c["surface"]) for c in ORACLE["surface_cases"]]
)
def test_independently_reviewed_surface_oracle(case) -> None:
    mention = normalize_surface(case["surface"])
    assert (mention.concept_id, mention.status) == (case["concept"], case["status"])
    assert mention.span.quote == case["surface"].strip()
    assert case["surface"][mention.span.start : mention.span.end] == mention.span.quote


@pytest.mark.parametrize("relation", ORACLE["relations"], ids=lambda r: f"{r['from']}->{r['to']}")
def test_relations_are_typed_and_never_equivalence(relation) -> None:
    assert (relation["type"], relation["to"]) in relations_of(relation["from"])
    assert relation["type"] in {"broader", "related"}


def test_fixture_identity_and_a21_coverage() -> None:
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert digest == "e9b302a1fcf6e35e545ecefae27619f21b54b492a7e8c2d6b918a80185ea8570"
    locales = [case["locale"] for case in ORACLE["scan_cases"]]
    assert locales.count("en") >= 12 and locales.count("de") >= 12
    concepts = {m["concept"] for c in ORACLE["scan_cases"] for m in c["expected"]}
    assert {"c", "cpp", "csharp", "r", "dotnet", "java", "javascript"} <= concepts
    assert {"deep-learning", "pytorch", "aws", "aws-sagemaker"} <= concepts


@pytest.mark.parametrize(
    ("text", "concepts"),
    [
        ("Amazon SageMaker", ["aws-sagemaker"]),
        ("AWS", ["aws"]),
        ("PyTorch", ["pytorch"]),
        ("deep learning", ["deep-learning"]),
        ("Azure DevOps", ["azure-devops"]),
        ("ASP.NET", ["aspnet"]),
    ],
)
def test_narrower_or_related_concepts_never_expand(text, concepts) -> None:
    assert [m.concept_id for m in find_mentions(text)] == concepts


def test_dictionary_is_valid_and_every_concept_has_provenance() -> None:
    validate_dictionary()
    assert all(concept.rationale.strip() for concept in CONCEPTS)


@pytest.mark.parametrize(
    "bad",
    [
        (*CONCEPTS, Concept(concept_id="dup", label="x", kind="technology",
                            aliases=(Alias(text="python"),), rationale="duplicate alias")),
        (*CONCEPTS, Concept(concept_id="python", label="x", kind="technology",
                            aliases=(Alias(text="Pyth0n"),), rationale="duplicate id")),
        (*CONCEPTS, Concept(concept_id="two", label="x", kind="technology",
                            aliases=(Alias(text="ab", style="letter"),), rationale="bad letter")),
        (*CONCEPTS, Concept(concept_id="loop", label="x", kind="technology",
                            aliases=(Alias(text="Loopy"),),
                            relations=(Relation(type="related", target="loop"),),
                            rationale="self relation")),
        (*CONCEPTS, Concept(concept_id="dangle", label="x", kind="technology",
                            aliases=(Alias(text="Dangly"),),
                            relations=(Relation(type="broader", target="missing"),),
                            rationale="missing target")),
        (*CONCEPTS, Concept(concept_id="norat", label="x", kind="technology",
                            aliases=(Alias(text="Norat"),), rationale="  ")),
    ],
)  # fmt: skip
def test_invalid_dictionaries_are_rejected(bad) -> None:
    with pytest.raises(NormalizationError):
        validate_dictionary(bad)


def test_polarity_and_context_pass_through_without_possession() -> None:
    mentions = find_mentions("No Java required.", polarity="negated", context="requirement")
    assert [(m.concept_id, m.polarity, m.context) for m in mentions] == [
        ("java", "negated", "requirement")
    ]
    assert set(SkillMention.model_fields) == {
        "span", "concept_id", "alias", "status", "polarity", "context"
    }  # fmt: skip


def test_unmatched_surface_keeps_literal_text_and_offsets() -> None:
    mention = normalize_surface("  QuuxDB  ")
    assert (mention.status, mention.concept_id, mention.span.quote) == ("unmatched", None, "QuuxDB")
    assert (mention.span.start, mention.span.end) == (2, 8)
    with pytest.raises(NormalizationError):
        normalize_surface("   ")


@pytest.mark.parametrize("neighbour", [*" aZ5_.-+#/(),;:!&'é", "\u00a0", "\u0301", "\u093f", ""])
def test_boundary_matrix_never_produces_false_positives(neighbour) -> None:
    def alnum(ch: str) -> bool:
        # Letters, digits and combining marks (category M) are never boundaries.
        return ch.isalnum() or unicodedata.category(ch).startswith("M")

    for concept in CONCEPTS:
        for alias in concept.aliases:
            for before, after in ((neighbour, " "), (" ", neighbour), (neighbour, neighbour)):
                text = f"{before}{alias.text}{after}"
                exact = [
                    m for m in find_mentions(text)
                    if (m.span.start, m.span.end) == (len(before), len(before) + len(alias.text))
                ]  # fmt: skip
                if not exact or exact[0].concept_id != concept.concept_id:
                    continue
                if alias.style in {"word", "abbreviation"}:
                    allowed = not (before and alnum(before)) and not (after and alnum(after))
                elif alias.style == "letter":
                    allowed = (before == "" or before.isspace() or before in "(,/") and (
                        after == "" or after.isspace() or after in "),/;:."
                    )
                else:
                    allowed = not (before and (alnum(before) or before == ".")) and not (
                        after and alnum(after)
                    )
                assert allowed, (alias.text, repr(text))


def test_case_rules_for_collision_prone_abbreviations() -> None:
    for text in ("ml", "aws", "ki", "js", "nlp", "react", "c", "r", "llm", "K8S"):
        assert normalize_surface(text).status == "unmatched", text
    for text in ("ML", "AWS", "KI", "JS", "NLP", "React", "C", "R", "LLM", "k8s"):
        assert normalize_surface(text).status == "matched", text


def test_bounds_fail_cleanly_and_stay_fast() -> None:
    with pytest.raises(NormalizationError, match="200,000"):
        find_mentions("x" * 200_001)
    dense = ("C, C++, C#, R, .NET, Java, JS " * 10_000)[:199_000]
    with pytest.raises(NormalizationError, match="4096"):
        find_mentions(dense)
    prose = ("Experience building reliable systems with strong communication. " * 4000)[:199_000]
    started = time.monotonic()
    assert find_mentions(prose) == []
    assert time.monotonic() - started < 5


def _classify(source: str, root: Path):
    job = ingest_job(source.encode(), job_id="synthetic-role", locale="en", data_root=root).record
    extraction = extract_requirements(source, job=job)
    return classify_requirements(extraction, source, job=job)


def test_classification_terms_are_normalized_with_row_polarity(tmp_path: Path) -> None:
    source = (
        "Requirements\n- Python or Java is required.\n- German is not required.\n"
        "- A degree in Physics or equivalent experience.\n- QuuxDB is required."
    )
    classification = _classify(source, tmp_path)
    result = normalize_classification(classification)
    assert result.classification_digest == classification.classification_digest
    found = [(t.mention.span.quote, t.mention.concept_id, t.mention.polarity) for t in result.terms]
    assert found == [
        ("Python", "python", "positive"),
        ("Java", "java", "positive"),
        ("German", "lang-german", "negated"),
    ]
    for term in result.terms:
        assert source[term.mention.span.start : term.mention.span.end] == term.mention.span.quote
        assert term.mention.context == "requirement"


@pytest.mark.parametrize(
    ("text", "quotes"),
    [
        ("Java\u0301 runtime", []),
        ("e\u0301Python code", []),
        ("Python\u093f and \u0915\u093fJava", []),
        ("Azure DevOps\u0301 board", ["Azure"]),
        ("JAVA_HOME and Python_path", ["JAVA", "Python"]),
    ],
)
def test_combining_marks_join_letters_and_underscore_is_a_boundary(text, quotes) -> None:
    assert [m.span.quote for m in find_mentions(text)] == quotes
