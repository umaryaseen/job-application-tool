"""Exact, reviewed skill-alias normalization (TASK-013).

Mentions come only from explicit dictionary aliases with per-style boundary
rules; the longest alias wins and mentions never overlap. Unmatched surfaces
are kept literally. Polarity and context come from the caller: normalization
never asserts that anyone possesses a skill, and relations never make two
concepts equivalent.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from functools import lru_cache
from typing import Literal

from pydantic import Field

from ..domain.common import StableId, StrictModel
from ..domain.requirement import (
    ConditionGroup,
    ConditionTerm,
    RequirementClassification,
    SourceSpan,
)
from .dictionary import CONCEPTS, DICTIONARY_VERSION, Alias, Concept, ConceptId

Polarity = Literal["positive", "negated", "unknown"]
MentionContext = Literal["requirement", "profile", "other"]
MAX_TEXT = 200_000
MAX_MENTIONS = 4096

_LETTER_BEFORE = r"(?<![^\s(,/])"
_LETTER_AFTER = r"(?=$|[\s),/;:]|\.(?![^\W_]))"


@lru_cache(maxsize=1)
def _unicode_tables() -> tuple[str, dict[str, tuple[str, ...]]]:
    """Combining-mark class and case-fold equivalents, from the Unicode database.

    A combining mark (any category M) belongs to the preceding letter, so it is
    never a boundary. Case-insensitive matching means per-character Unicode
    ``casefold()`` equality, not ``re.IGNORECASE`` (which also equates dotted
    and dotless I with i).
    """
    ranges: list[tuple[int, int]] = []
    folds: dict[str, list[str]] = {}
    for code in range(sys.maxunicode + 1):
        char = chr(code)
        if unicodedata.category(char).startswith("M"):
            if ranges and ranges[-1][1] == code - 1:
                ranges[-1] = (ranges[-1][0], code)
            else:
                ranges.append((code, code))
        folded = char.casefold()
        if len(folded) == 1 and (folded != char or char.lower() != char or char.upper() != char):
            folds.setdefault(folded, []).append(char)
    marks = (
        "["
        + "".join(
            re.escape(chr(a)) if a == b else f"{re.escape(chr(a))}-{re.escape(chr(b))}"
            for a, b in ranges
        )
        + "]"
    )
    return marks, {key: tuple(sorted(set(value))) for key, value in folds.items()}


def _boundaries() -> tuple[str, str]:
    marks, _ = _unicode_tables()
    return rf"(?<![^\W_])(?<!{marks})", rf"(?![^\W_]|{marks})"


def _casefold_text(text: str) -> str:
    """Regex for ``text`` matching exactly the case-fold-equivalent spellings."""
    _, folds = _unicode_tables()
    pieces = []
    for char in text:
        folded = char.casefold()
        if len(folded) != 1:
            raise NormalizationError(f"alias character {char!r} folds to several characters")
        variants = sorted({char, folded, *folds.get(folded, ())})
        variants = [v for v in variants if v.casefold() == folded]
        pieces.append(
            re.escape(variants[0])
            if len(variants) == 1
            else "[" + "".join(re.escape(v) for v in variants) + "]"
        )
    return "".join(pieces)


class NormalizationError(ValueError):
    """Dictionary or input outside the supported bounds."""


class SkillMention(StrictModel):
    span: SourceSpan
    concept_id: ConceptId | None = None
    alias: str | None = None
    status: Literal["matched", "ambiguous", "unmatched"]
    polarity: Polarity = "unknown"
    context: MentionContext = "other"


class TermNormalization(StrictModel):
    candidate_id: StableId
    mention: SkillMention


class ClassificationNormalization(StrictModel):
    dictionary_version: Literal["skill-aliases-v1"] = DICTIONARY_VERSION
    classification_digest: str
    terms: list[TermNormalization] = Field(default_factory=list, max_length=MAX_MENTIONS)


def _alias_pattern(alias: Alias) -> str:
    """Style-specific part only; the shared letter/digit/mark boundary wraps all."""
    if alias.style in {"word", "symbol"}:
        body = r"\s+".join(_casefold_text(part) for part in alias.text.split())
    else:
        body = r"\s+".join(re.escape(part) for part in alias.text.split())
    if alias.style == "word" or alias.style == "abbreviation":
        return body
    if alias.style == "letter":
        return f"{_LETTER_BEFORE}{body}{_LETTER_AFTER}"
    return rf"(?<!\.){body}"


def validate_dictionary(concepts: tuple[Concept, ...] = CONCEPTS) -> None:
    """Reject duplicate IDs, aliases shared by two concepts and untyped links."""
    ids = [concept.concept_id for concept in concepts]
    if len(ids) != len(set(ids)):
        raise NormalizationError("duplicate concept identifiers")
    owners: dict[str, str] = {}
    for concept in concepts:
        if not concept.aliases or not concept.rationale.strip():
            raise NormalizationError(f"{concept.concept_id} needs aliases and a rationale")
        for alias in concept.aliases:
            if alias.style == "letter" and len(alias.text) != 1:
                raise NormalizationError(f"letter alias must be one character: {alias.text}")
            if alias.style in {"word", "symbol"} and any(
                len(char.casefold()) != 1 for char in alias.text if not char.isspace()
            ):
                raise NormalizationError(
                    f"case-insensitive alias needs single-character folds: {alias.text}"
                )
            key = " ".join(alias.text.split())
            key = key if alias.style in {"abbreviation", "letter"} else key.casefold()
            for other_key in (key, key.casefold()):
                owner = owners.get(other_key)
                if owner is not None and owner != concept.concept_id:
                    raise NormalizationError(f"alias {alias.text!r} maps to two concepts")
            owners[key] = concept.concept_id
            owners.setdefault(key.casefold(), concept.concept_id)
        for relation in concept.relations:
            if relation.target not in ids or relation.target == concept.concept_id:
                raise NormalizationError(f"{concept.concept_id} has an invalid relation")


@lru_cache(maxsize=1)
def _matcher() -> tuple[re.Pattern[str], dict[str, tuple[Concept, Alias]]]:
    validate_dictionary()
    entries = [(concept, alias) for concept in CONCEPTS for alias in concept.aliases]
    # Longest alias first so alternation prefers it at the same start position.
    entries.sort(key=lambda item: (-len(item[1].text), item[1].text))
    groups: dict[str, tuple[Concept, Alias]] = {}
    parts = []
    for index, (concept, alias) in enumerate(entries):
        name = f"a{index}"
        groups[name] = (concept, alias)
        parts.append(f"(?P<{name}>{_alias_pattern(alias)})")
    # Every style forbids a letter, digit or combining mark on either side, so the
    # boundary is tested once around the alternation; on failure the engine
    # backtracks into the alternation and tries shorter aliases at the same start.
    before, after = _boundaries()
    return re.compile(before + "(?:" + "|".join(parts) + ")" + after), groups


def find_mentions(
    text: str, *, offset: int = 0, polarity: Polarity = "unknown", context: MentionContext = "other"
) -> list[SkillMention]:
    """All alias mentions in ``text``; spans are offset into the caller's source."""
    if len(text) > MAX_TEXT:
        raise NormalizationError("text exceeds the 200,000-character normalization limit")
    pattern, groups = _matcher()
    mentions: list[SkillMention] = []
    for match in pattern.finditer(text):
        if len(mentions) >= MAX_MENTIONS:
            raise NormalizationError("text exceeds 4096 skill mentions; review the source")
        concept, alias = groups[match.lastgroup or ""]
        start, end = offset + match.start(), offset + match.end()
        mentions.append(
            SkillMention(
                span=SourceSpan(start=start, end=end, quote=match.group()),
                concept_id=concept.concept_id,
                alias=alias.text,
                status="matched" if alias.status == "exact" else "ambiguous",
                polarity=polarity,
                context=context,
            )
        )
    return mentions


def normalize_surface(
    surface: str, *, polarity: Polarity = "unknown", context: MentionContext = "other"
) -> SkillMention:
    """Normalize one whole surface; anything but a single full alias stays unmatched."""
    if len(surface) > MAX_TEXT:
        raise NormalizationError("surface exceeds the 200,000-character normalization limit")
    stripped = surface.strip()
    if not stripped:
        raise NormalizationError("surface is empty")
    start = surface.index(stripped)
    mentions = find_mentions(stripped, offset=start, polarity=polarity, context=context)
    if len(mentions) == 1 and mentions[0].span.quote == stripped:
        return mentions[0]
    return SkillMention(
        span=SourceSpan(start=start, end=start + len(stripped), quote=stripped),
        status="unmatched",
        polarity=polarity,
        context=context,
    )


def relations_of(concept_id: str) -> tuple[tuple[str, str], ...]:
    """Typed (relation, target) links; informational only, never equivalence."""
    for concept in CONCEPTS:
        if concept.concept_id == concept_id:
            return tuple((relation.type, relation.target) for relation in concept.relations)
    raise NormalizationError(f"unknown concept {concept_id}")


_ROW_POLARITY: dict[str, Polarity] = {
    "none": "positive",
    "requirement_negated": "negated",
    "unsupported": "unknown",
}


def _terms(node: ConditionTerm | ConditionGroup) -> list[ConditionTerm]:
    if isinstance(node, ConditionGroup):
        return [term for child in node.children for term in _terms(child)]
    return [node]


def normalize_classification(
    classification: RequirementClassification,
) -> ClassificationNormalization:
    """Annotate technology/language condition terms with concepts, keeping polarity.

    A requirement-negated row yields negated mentions, an unsupported negation
    yields unknown polarity; nothing here records possession or approval.
    """
    terms: list[TermNormalization] = []
    for row in classification.candidates:
        if row.role != "requirement" or row.condition is None:
            continue
        polarity = _ROW_POLARITY[row.negation]
        for term in _terms(row.condition):
            if term.term_kind not in {"technology", "language"}:
                continue
            mention = normalize_surface(term.span.quote, polarity=polarity, context="requirement")
            shifted = mention.span.model_copy(
                update={
                    "start": term.span.start + mention.span.start,
                    "end": term.span.start + mention.span.end,
                }
            )
            terms.append(
                TermNormalization(
                    candidate_id=row.candidate_id,
                    mention=mention.model_copy(update={"span": shifted}),
                )
            )
    return ClassificationNormalization(
        classification_digest=classification.classification_digest, terms=terms
    )
