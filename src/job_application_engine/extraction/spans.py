"""Bounded structural segmentation with original Unicode-codepoint offsets."""

from __future__ import annotations

import bisect
import itertools
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from ..domain.requirement import SectionKind, SourceSpan

MAX_STRUCTURAL_SPANS = 2048
BULLET = re.compile(r"^(?:[-*+•▪]\s+|\d{1,3}[.)]\s+)")
ABBREVIATIONS = (
    "e.g.",
    "i.e.",
    "bzw.",
    "etc.",
    "dr.",
    "prof.",
    "mr.",
    "ms.",
    "m.sc.",
    "b.sc.",
    "ph.d.",
    "u.s.",
    "u.k.",
)
HEADINGS: dict[str, SectionKind] = {
    **dict.fromkeys(
        (
            "requirements",
            "qualifications",
            "your qualifications",
            "your profile",
            "what you bring",
            "what we're looking for",
            "what you bring to the role",
            "anforderungen",
            "qualifikationen",
            "dein profil",
            "ihr profil",
            "was du mitbringst",
            "was sie mitbringen",
            "deine qualifikationen und erfahrung",
            "ihre qualifikationen und erfahrung",
            "what you bring to the team",
        ),
        "qualifications",
    ),
    **dict.fromkeys(
        (
            "responsibilities",
            "your responsibilities",
            "your tasks",
            "how you'll make an impact",
            "aufgaben",
            "deine aufgaben",
            "ihre aufgaben",
            "aufgaben und verantwortlichkeiten",
            "deine aufgaben und verantwortlichkeiten",
            "ihre aufgaben und verantwortlichkeiten",
        ),
        "responsibilities",
    ),
    **dict.fromkeys(
        (
            "benefits",
            "our benefits",
            "what we offer",
            "we offer",
            "wir bieten",
            "was wir bieten",
            "deine vorteile",
            "ihre vorteile",
        ),
        "benefits",
    ),
    **dict.fromkeys(
        (
            "about us",
            "about the team",
            "about the company",
            "about the role",
            "über uns",
            "über das team",
            "über die rolle",
            "unternehmen",
        ),
        "context",
    ),
}


class ExtractionError(ValueError):
    """A bounded sanitized source, integrity or analysis-limit failure."""


@dataclass(frozen=True)
class Segment:
    span: SourceSpan
    heading: bool = False
    section_kind: SectionKind = "unknown"


def source_span(source: str, start: int, end: int) -> SourceSpan:
    while start < end and (source[start].isspace() or (start == 0 and source[start] == "\ufeff")):
        start += 1
    while end > start and source[end - 1].isspace():
        end -= 1
    return SourceSpan(start=start, end=end, quote=source[start:end])


class SpanCover:
    """Logarithmic containment checks against fixed, possibly overlapping spans."""

    def __init__(self, spans: Iterable[SourceSpan]) -> None:
        ordered = sorted((span.start, span.end) for span in spans)
        self._starts = [start for start, _ in ordered]
        self._max_end = list(itertools.accumulate((end for _, end in ordered), max))

    def contains(self, span: SourceSpan) -> bool:
        index = bisect.bisect_right(self._starts, span.start)
        return index > 0 and self._max_end[index - 1] >= span.end


def verify_span(source: str, span: SourceSpan) -> None:
    if span.end > len(source) or source[span.start : span.end] != span.quote:
        raise ExtractionError("source quote or Unicode offsets do not match the raw JD")


def heading_kind(text: str, *, bullet: bool) -> SectionKind | None:
    clean = text.strip().lstrip("#").strip().strip("*").strip().rstrip(":").strip()
    if len(clean) > 160 or bullet:
        return None
    kind = HEADINGS.get(clean.casefold())
    if kind is not None:
        return kind
    # An explicit unknown heading resets the previous scope instead of borrowing it.
    if text.startswith("#") or (text.endswith(":") and len(text) <= 100):
        return "unknown"
    return None


def _sentences(source: str, start: int, end: int) -> Iterator[Segment]:
    cursor = start
    for match in re.finditer(r"[.!?](?=\s|$)", source[start:end]):
        boundary = start + match.end()
        prefix = source[max(start, boundary - 12) : boundary].casefold()
        if match.group() == "." and (
            prefix.endswith(ABBREVIATIONS) or re.search(r"(?:^|\W)[^\W\d_]\.$", prefix)
        ):
            continue
        if source[cursor:boundary].strip():
            yield Segment(source_span(source, cursor, boundary))
        cursor = boundary
    if source[cursor:end].strip():
        yield Segment(source_span(source, cursor, end))


def segment_source(source: str) -> list[Segment]:
    result: list[Segment] = []
    block_start: int | None = None
    block_end = 0

    def append(segment: Segment) -> None:
        if len(result) >= MAX_STRUCTURAL_SPANS:
            raise ExtractionError("JD analysis exceeds 2048 structural spans; review the source")
        result.append(segment)

    def flush() -> None:
        nonlocal block_start
        if block_start is not None:
            for segment in _sentences(source, block_start, block_end):
                append(segment)
            block_start = None

    offset = 0
    for line in source.splitlines(keepends=True):
        trimmed = line.strip().lstrip("\ufeff")
        if not trimmed:
            flush()
            offset += len(line)
            continue
        span = source_span(source, offset, offset + len(line))
        bullet = BULLET.match(span.quote)
        kind = heading_kind(span.quote, bullet=bullet is not None)
        if kind is not None:
            flush()
            append(Segment(span, heading=True, section_kind=kind))
        else:
            if bullet is not None:
                flush()
                block_start = span.start + bullet.end()
            elif block_start is None:
                block_start = span.start
            block_end = span.end
        offset += len(line)
    flush()
    return result
