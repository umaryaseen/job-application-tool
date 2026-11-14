"""Explicit EN/DE priority and negation cues; absence of a cue never implies priority."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from ..domain.requirement import CueLevel, PriorityBasis, ReviewReason, SourceSpan
from .spans import SpanCover

_W = r"(?<!\w)"
_E = r"(?!\w)"
_EN_MANDATORY = r"required|requires|must|mandatory|essential|necessary|prerequisite"
_DE_MANDATORY = (
    r"erforderlich(?:e[nmrs]?)?|zwingend(?:e[nmrs]?)?|notwendig(?:e[nmrs]?)?|vorausgesetzt|"
    r"voraussetzung|muss|müssen|musst|pflicht|unabdingbar|unerlässlich"
)
_EN_PREFERRED = (
    r"preferred|preferably|preferable|nice[\s-]to[\s-]have|a\s+plus|bonus|an\s+advantage|"
    r"advantageous|desirable|desired|ideally|beneficial|helpful"
)
_DE_PREFERRED = (
    r"wünschenswert(?:e[nmrs]?)?|von\s+vorteil|vorteilhaft(?:e[nmrs]?)?|idealerweise|"
    r"bevorzugt|ein\s+plus|pluspunkte?"
)
MANDATORY = re.compile(_W + "(?:" + _EN_MANDATORY + "|" + _DE_MANDATORY + ")" + _E, re.I)
PREFERRED = re.compile(_W + "(?:" + _EN_PREFERRED + "|" + _DE_PREFERRED + ")" + _E, re.I)
# Headings are short labels, so these extra phrases are recognized only there.
HEADING_MANDATORY = re.compile(_W + r"(?:minimum|basic)\s+qualifications" + _E, re.I)
HEADING_PREFERRED = re.compile(_W + r"(?:pluses|plus|kann-kriterien)" + _E, re.I)

_WORD = r"[^\W\d_][\w+#.\-]*"
NOT_REQUIRED = re.compile(
    "|".join(
        (
            _W + r"not\s+(?:strictly\s+|necessarily\s+|absolutely\s+)?"
            r"(?:required|necessary|mandatory|essential|needed|a\s+must|a\s+requirement|"
            r"a\s+prerequisite)" + _E,
            _W + r"no\s+(?:" + _WORD + r"\s+){0,3}?(?:required|necessary|needed)" + _E,
            _W + r"(?:do|does|did)\s+not\s+need" + _E,
            _W + r"(?:don|doesn|didn)[’']t\s+need" + _E,
            _W + r"nicht\s+(?:zwingend\s+|unbedingt\s+|notwendigerweise\s+)?"
            r"(?:erforderlich|notwendig|nötig|vorausgesetzt|benötigt|zwingend|verpflichtend|"
            r"pflicht|voraussetzung)" + _E,
            _W + r"kein(?:e[nmrs]?)?\s+(?:voraussetzung|pflicht|muss|bedingung)" + _E,
            _W + r"kein(?:e[nmrs]?)?\s+(?:" + _WORD + r"\s+){1,3}?"
            r"(?:erforderlich|notwendig|nötig|vorausgesetzt|benötigt)" + _E,
        )
    ),
    re.I,
)
NEGATION_TOKEN = re.compile(
    _W
    + r"(?:not|no|never|without|neither|nor|nicht|kein(?:e[nmrs]?)?|ohne|nie|niemals|weder)"
    + _E
    + r"|"
    + _W
    + r"\w+n[’']t"
    + _E,
    re.I,
)

_MARKER_PREFERRED = {
    "nice to have",
    "nice-to-have",
    "nice to haves",
    "nice-to-haves",
    "preferred",
    "preferred qualifications",
    "preferred skills",
    "desirable",
    "desired skills",
    "desired qualifications",
    "bonus",
    "bonus points",
    "plus",
    "pluses",
    "good to have",
    "wünschenswert",
    "von vorteil",
    "pluspunkte",
    "kann-kriterien",
}
_MARKER_MANDATORY = {
    "must have",
    "must-have",
    "must haves",
    "must-haves",
    "required",
    "required skills",
    "required qualifications",
    "minimum qualifications",
    "basic qualifications",
    "mandatory",
    "muss-kriterien",
    "zwingend erforderlich",
}


@dataclass(frozen=True)
class Cue:
    level: CueLevel
    span: SourceSpan


def _span(source: str, offset: int, match: re.Match[str]) -> SourceSpan:
    start, end = offset + match.start(), offset + match.end()
    return SourceSpan(start=start, end=end, quote=source[start:end])


def find_cues(source: str, span: SourceSpan, *, heading: bool = False) -> list[Cue]:
    """Return explicit cues in source order; cue words inside a negated cue are ignored."""
    text, offset = span.quote, span.start
    negated = [_span(source, offset, m) for m in NOT_REQUIRED.finditer(text)]
    cover = SpanCover(negated)
    result = [Cue("not_required", s) for s in negated]
    mandatory = [MANDATORY] + ([HEADING_MANDATORY] if heading else [])
    preferred = [PREFERRED] + ([HEADING_PREFERRED] if heading else [])
    for level, patterns in (("mandatory", mandatory), ("preferred", preferred)):
        for pattern in patterns:
            for match in pattern.finditer(text):
                found = _span(source, offset, match)
                if not cover.contains(found):
                    result.append(Cue(level, found))  # type: ignore[arg-type]
    return sorted(result, key=lambda cue: (cue.span.start, cue.span.end, cue.level))


def stray_negations(source: str, span: SourceSpan, cues: list[Cue]) -> list[SourceSpan]:
    """Negation words outside a recognized not-required pattern stay unsupported."""
    cover = SpanCover(cue.span for cue in cues if cue.level == "not_required")
    stray = (_span(source, span.start, m) for m in NEGATION_TOKEN.finditer(span.quote))
    return [found for found in stray if not cover.contains(found)]


def marker_level(text: str) -> Literal["mandatory", "preferred"] | None:
    clean = " ".join(text.strip().rstrip(":").split()).casefold()
    if clean in _MARKER_PREFERRED:
        return "preferred"
    if clean in _MARKER_MANDATORY:
        return "mandatory"
    return None


def heading_level(cues: list[Cue]) -> tuple[Literal["mandatory", "preferred"] | None, bool]:
    """A heading supplies one level only when it is unambiguous; return (level, conflict)."""
    levels = {cue.level for cue in cues}
    if not levels:
        return None, False
    if levels == {"mandatory"}:
        return "mandatory", False
    if levels == {"preferred"}:
        return "preferred", False
    return None, True


Decision = tuple[
    Literal["mandatory", "preferred", "unspecified"], PriorityBasis, list[ReviewReason]
]


def decide_priority(
    clause: list[Cue], heading: Literal["mandatory", "preferred"] | None
) -> Decision:
    """Combine explicit clause cues with an inherited heading cue, never forcing a level."""
    levels = {cue.level for cue in clause}
    if "mandatory" in levels and levels & {"preferred", "not_required"}:
        return "unspecified", "conflicting_clause_cues", ["conflicting_priority_cues"]
    conflict: Decision = (
        "unspecified",
        "clause_conflicts_with_heading",
        ["heading_clause_conflict"],
    )
    if "mandatory" in levels:
        if heading == "preferred":
            return conflict
        return "mandatory", "explicit_mandatory_cue", []
    if "preferred" in levels:
        if heading == "mandatory":
            return conflict
        return "preferred", "explicit_preferred_cue", []
    if "not_required" in levels:
        if heading == "mandatory":
            return conflict
        if heading == "preferred":
            return "preferred", "heading_preferred_cue", []
        return "unspecified", "explicitly_not_required", []
    if heading == "mandatory":
        return "mandatory", "heading_mandatory_cue", []
    if heading == "preferred":
        return "preferred", "heading_preferred_cue", []
    return "unspecified", "no_priority_cue", []
