"""Supported ALL/ANY groups, degree-or-equivalent and numeric thresholds.

Anything outside this small grammar stays visible and needs review; an OR clause
is never split into separate conditions, and no partial condition is emitted.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field
from typing import Literal, cast

from ..domain.requirement import (
    MAX_CONDITION_DEPTH,
    MAX_CONDITION_TERMS,
    CefrLevel,
    Condition,
    ConditionGroup,
    ConditionTerm,
    LexicalSignal,
    ReviewReason,
    SourceSpan,
    TermKind,
    Threshold,
)
from .spans import ExtractionError, SpanCover

MAX_CLAUSE_LEVELS = 4096

CONNECTIVE = re.compile(
    r"and/or|und/oder|as\s+well\s+as|als\s+auch|(?<!\w)bzw\.|(?<!\w)(?:or|oder|either|entweder|"
    r"alternatively|alternativ|beziehungsweise|and|und|sowie|both|sowohl)(?!\w)",
    re.I,
)
_ALTERNATIVES = {
    "or",
    "oder",
    "either",
    "entweder",
    "alternatively",
    "alternativ",
    "beziehungsweise",
    "and/or",
    "und/oder",
    "bzw.",
}
_GAP_TOKEN = re.compile(
    r"\s*(?:(?P<comma>,)|(?P<open>\()|(?P<close>\))|(?P<andor>and/or|und/oder)|"
    r"(?P<aswell>as\s+well\s+as)|(?P<alsauch>als\s+auch)|"
    r"(?<!\w)(?P<word>and|und|sowie|or|oder|either|entweder|both|sowohl)(?!\w))\s*",
    re.I,
)
_WORD_TYPES = {
    "and": "and",
    "und": "and",
    "sowie": "and",
    "or": "or",
    "oder": "or",
    "either": "either",
    "entweder": "either",
    "both": "both",
    "sowohl": "both",
}
_LEADING = re.compile(r"(?:(?<!\w)(?:either|both|entweder|sowohl)|\()\s*$", re.I)
_TRAILING = re.compile(r"\s*\)")  # used with match(pos): no ^ anchor

EQUIVALENT = re.compile(
    r",?\s*(?<!\w)(?P<conn>or|oder)\s+(?:an?\s+|eine[nmrs]?\s+)?(?P<term>"
    r"(?:equivalent|comparable|relevant|similar)\s+"
    r"(?:(?:practical|professional|work|industry|hands-on)\s+)?"
    r"(?:experience|qualifications?|education|training)|"
    r"(?:vergleichbare|gleichwertige|entsprechende|äquivalente)[nmrs]?\s+"
    r"(?:berufserfahrung|praxiserfahrung|erfahrung|qualifikation|ausbildung)|"
    r"equivalent(?=\s*(?:[.,;)]|$)))(?!\w)",
    re.I,
)
FIELD_ALTERNATIVE = re.compile(
    r"(?<!\w)(?:or|oder)\s+(?:in\s+)?(?:an?\s+|eine[nmrs]?\s+)?(?:other\s+)?"
    r"(?:related|similar|comparable|relevant|verwandten|vergleichbaren|ähnlichen|artverwandten)\s+"
    r"(?:technical\s+)?(?:fields?|disciplines?|subjects?|areas?|degrees?|studies|fach|fächern|"
    r"studiengang|fachrichtung|bereich|disziplin)(?!\w)",
    re.I,
)
_EXPERIENCE_WORDS = ("experience", "erfahrung")
_FIELD_LINK = re.compile(r"\s+(?:in\s+der|in\s+den|im\s+bereich|in|of|der|des|im)\s+", re.I)
_FIELD_WORD = re.compile(r"[^\W\d_][\w\-]*")
_FIELD_SPACE = re.compile(r"[ \t]+")
_FIELD_GAP = re.compile(r",?\s*")
_NEXT_WORD = re.compile(r"[ \t-]+(?P<word>[^\W\d_]+)")
MAX_FIELD_WORDS = 4

_NUMBER = re.compile(r"(?P<value>\d{1,3})(?:\s*[-–]\s*(?P<upper>\d{1,3}))?(?P<plus>\+)?")
_WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "ein": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
}
_VAGUE = {"several", "many", "mehrere"}
MAX_DURATION = 99  # Threshold model bound; larger values go to review, never to a raw error
# Any numeric duration, including forms the TASK-011 signal does not capture
# (four digits, no space, "yrs"); uncaptured ones need review.
ANY_DURATION = re.compile(
    r"(?<![\w.,])\d[\d.,]*\s*(?:[-–]\s*\d[\d.,]*\s*)?\+?\s*"
    r"(?:years?|yrs?|jahre?n?|months?|mos?|monate?n?)(?!\w)",
    re.I,
)
_AMOUNT = re.compile(r"(?P<number>.+?)\s+(?P<unit>\S+)", re.S)
PREFIX_GTE = re.compile(
    r"(?<!\w)(?:at\s+least|a\s+minimum\s+of|minimum\s+of|minimum|min\.?|mindestens|wenigstens)\s*$",
    re.I,
)
PREFIX_GT = re.compile(r"(?<!\w)(?:more\s+than|over|mehr\s+als|über)\s*$", re.I)
# Operator words outside the supported grammar: never silently reduced to "unqualified".
UNSUPPORTED_PREFIX = re.compile(
    r"(?<!\w)(?:up\s+to|max(?:imum)?\.?|at\s+most|less\s+than|fewer\s+than|under|"
    r"approximately|approx\.?|about|around|roughly|ca\.?|circa|etwa|rund|ungefähr|"
    r"bis\s+zu|höchstens|maximal|weniger\s+als|unter)\s*$",
    re.I,
)
UNSUPPORTED_POSTFIX = re.compile(
    r"\s*(?:minimum|min\.?|minimal|at\s+least|or\s+(?:more|longer|above|higher|better)|plus|"
    r"maximum|max\.?|at\s+most|mindestens|oder\s+(?:mehr|länger|höher|besser)|maximal|"
    r"höchstens)(?!\w)",
    re.I,
)
# Every operator word, supported or not. One outside an accepted threshold span
# ("3 years of Python minimum", "About at least 3 years") makes the clause's
# numeric interpretation unreliable, so its thresholds are withheld.
OPERATOR_WORD = re.compile(
    r"(?<!\w)(?:at\s+least|at\s+most|minimum|minimal|min\.?|maximum|maximal|max\.?|"
    r"up\s+to|more\s+than|less\s+than|fewer\s+than|over|under|approximately|approx\.?|"
    r"about|around|roughly|ca\.?|circa|or\s+(?:more|longer|above|higher|better)|mindestens|"
    r"wenigstens|höchstens|etwa|rund|ungefähr|bis\s+zu|mehr\s+als|weniger\s+als|über|"
    r"unter|oder\s+(?:mehr|länger|höher|besser))(?!\w)",
    re.I,
)
UNIT_WORD = re.compile(r"(?<!\w)(?:years?|yrs?|jahre?n?|months?|monate?n?|monat)(?!\w)", re.I)
# Words that may surround interpreted spans without changing their meaning. Any
# other uncovered word may be an unrecognized operand, so the condition is
# withheld for review instead of being kept partially.
FILLER = frozenset(
    """
    a an the is are be been will would should can could may you your we our us they
    have has having had with within in of on for to at as by from using use used via
    also but knowledge experience experienced experiences skill skills skilled strong
    good solid excellent very deep basic advanced fluent fluency proficiency proficient
    working hands practical professional level levels understanding familiarity familiar
    background expertise ability s ll re ve d
    ein eine einer einen einem eines der die das den dem des ist sind wird werden sein
    mit im von vom auf für zu zum zur bei sehr gute guter gutes gut guten fundierte
    fundierter fundiertes fundierten solide soliden sichere sicherer sicheren fließend
    fließende fließenden verhandlungssicher verhandlungssichere verhandlungssicheren
    kenntnis kenntnisse erfahrung erfahrungen berufserfahrung praxiserfahrung aber auch
    sie du ihr haben hast habt bringst bringen bringt niveau
    """.split()
)
# Content-bearing descriptors are exempt only where they modify an adjacent term:
# directly before a degree ("completed degree", "Abgeschlossenes Studium") ...
EDUCATION_MODIFIERS = frozenset(
    """
    completed relevant university academic technical formal accredited recognized
    abgeschlossen abgeschlossene abgeschlossener abgeschlossenes abgeschlossenen
    einschlägige einschlägiger einschlägiges einschlägigen universitäre universitäres
    technische technischer technisches technischen akademische akademischer
    akademisches anerkannte anerkannter anerkanntes
    """.split()
)
# ... and directly after a recognized language ("German language skills").
LANGUAGE_SUFFIXES = frozenset({"language", "languages"})
# A degree field stops only at function words and connectives, never at
# descriptive words, so "A degree in formal language" keeps its whole field.
_FIELD_STOP = frozenset(
    """
    with mit and or und oder sowie plus including inkl etc both either entweder sowohl
    bzw is are be will would should ist sind wird werden sein from for by using via as
    to at on von vom für bei zu zum zur the a an der die das den dem des ein eine einer
    einen einem eines e z
    """.split()
)
_WORDS = re.compile(r"[^\W\d_]+|\d+")
CEFR = re.compile(
    r"(?<!\w)(?P<level>[ABC][12])(?P<plus>\+)?(?:\s*[-–]\s*(?P<upper>[ABC][12]))?"
    r"(?P<suffix>(?i:(?:\s*-?\s*(?:level|niveau))?\s+(?:or\s+(?:higher|above|better)|"
    r"oder\s+(?:höher|besser))))?(?!\w)"
)
_SCOPE_LEAD = re.compile(
    r"\s*['’]?\s*(?:(?:in\s+der|in\s+einem|in\s+einer|of|in|with|im|mit)"
    r"(?:\s+|(?=[.,;:!?)]|$)))?",
    re.I,
)
_TRAILING_WORD = re.compile(
    r"(?:^|\s)(?:is|are|be|would|will|ist|sind|wäre|wären|wird|werden|and|or|und|oder|sowie)$",
    re.I,
)


Operator = Literal["gte", "gt", "range", "unqualified"]


class _Unsupported(Exception):
    """The run is outside the supported grouping grammar."""


@dataclass(frozen=True)
class _Token:
    type: str
    span: SourceSpan
    term_kind: TermKind | None = None


@dataclass
class Structure:
    condition: Condition | None = None
    thresholds: list[Threshold] = field(default_factory=list)
    reasons: set[ReviewReason] = field(default_factory=set)


def span_of(source: str, start: int, end: int) -> SourceSpan:
    return SourceSpan(start=start, end=end, quote=source[start:end])


def trim_end(source: str, start: int, end: int) -> int:
    """Strip trailing punctuation and linking/connective words from a scope."""
    while True:
        text = source[start:end].rstrip().rstrip(".,;:!?").rstrip()
        match = _TRAILING_WORD.search(text)
        if match:
            text = text[: match.start()].rstrip()
        new_end = start + len(text)
        if new_end == end:
            return end
        end = new_end


_PREFIX_WINDOW = 48  # operator words sit immediately before a number
_LEADING_WINDOW = 64


def _prefix(pattern: re.Pattern[str], source: str, floor: int, end: int) -> re.Match[str] | None:
    # pos/endpos (not slicing) keep the real preceding character visible to (?<!\w).
    return pattern.search(source, max(floor, end - _PREFIX_WINDOW), end)


def _gap_tokens(source: str, start: int, end: int, *, hyphen: bool) -> list[_Token] | None:
    """Tokenize text between two terms; None when it is not purely connective."""
    tokens: list[_Token] = []
    position = start
    if hyphen and source.startswith("-", position) and source[position + 1 : end][:1].isspace():
        position += 1  # German suspended compound: "Deutsch- und Englischkenntnisse"
    while position < end:
        match = _GAP_TOKEN.match(source, position, end)
        if match is None or match.end() == position:
            return None
        group = match.lastgroup or ""
        inner = span_of(source, match.start(group), match.end(group))
        if group == "word":
            kind = _WORD_TYPES[inner.quote.casefold()]
        else:
            kind = {"andor": "or", "aswell": "and"}.get(group, group)
        tokens.append(_Token(kind, inner))
        position = match.end()
    return tokens or None


class _Parser:
    def __init__(self, tokens: list[_Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def peek(self, *types: str) -> _Token | None:
        if self.index < len(self.tokens) and self.tokens[self.index].type in types:
            return self.tokens[self.index]
        return None

    def take(self, *types: str) -> _Token:
        token = self.peek(*types)
        if token is None:
            raise _Unsupported
        self.index += 1
        return token

    def parse(self, source: str) -> Condition:
        result = self.parse_list(source, 1)
        if self.index != len(self.tokens):
            raise _Unsupported
        return result

    def term(self) -> ConditionTerm:
        token = self.take("atom")
        assert token.term_kind is not None
        return ConditionTerm(term_kind=token.term_kind, span=token.span)

    def parse_list(self, source: str, depth: int) -> Condition:
        if depth > MAX_CONDITION_DEPTH:
            raise _Unsupported
        items = [self.parse_item(source, depth)]
        separators: list[tuple[bool, _Token | None]] = []
        while self.peek("comma", "and", "or"):
            comma = self.peek("comma") is not None
            if comma:
                self.index += 1
            separators.append((comma, self.peek("and", "or") and self.take("and", "or")))
            items.append(self.parse_item(source, depth))
        if len(items) == 1:
            return items[0]
        conjunctions = [token for _, token in separators if token is not None]
        if separators[-1][1] is None or len({token.type for token in conjunctions}) != 1:
            raise _Unsupported  # comma-only list or mixed AND/OR precedence
        node: Literal["any", "all"] = "any" if conjunctions[0].type == "or" else "all"
        start, end = items[0].span.start, items[-1].span.end
        return ConditionGroup(
            node=node,
            span=span_of(source, start, end),
            connectives=[token.span for token in conjunctions],
            children=items,
        )

    def parse_item(self, source: str, depth: int) -> Condition:
        if self.peek("atom"):
            return self.term()
        if self.peek("open"):
            self.index += 1
            inner = self.parse_list(source, depth + 1)
            self.take("close")
            return inner
        if self.peek("either"):
            opener = self.take("either")
            children: list[Condition] = [self.term()]
            connectives = [opener.span]
            while self.peek("or"):
                connectives.append(self.take("or").span)
                children.append(self.term())
            if len(children) < 2:
                raise _Unsupported
            return ConditionGroup(
                node="any",
                span=span_of(source, opener.span.start, children[-1].span.end),
                connectives=connectives,
                children=children,
            )
        if self.peek("both"):
            opener = self.take("both")
            first = self.term()
            joiner = self.take("and", "alsauch")
            second = self.term()
            return ConditionGroup(
                node="all",
                span=span_of(source, opener.span.start, second.span.end),
                connectives=[opener.span, joiner.span],
                children=[first, second],
            )
        raise _Unsupported


def _runs(
    source: str, clause: SourceSpan, atoms: list[LexicalSignal]
) -> tuple[list[list[_Token]], bool]:
    """Group adjacent terms joined only by connectives; flag a bare slash between terms."""
    runs: list[list[_Token]] = []
    slash = False
    floor = clause.start
    current: list[_Token] = []
    for index, atom in enumerate(atoms):
        token = _Token("atom", atom.span, term_kind=cast(TermKind, atom.kind))
        if current:
            previous = atoms[index - 1].span.end
            gap = _gap_tokens(source, previous, atom.span.start, hyphen=True)
            if gap is not None:
                current.extend(gap)
                current.append(token)
                continue
            slash = slash or source[previous : atom.span.start].strip() == "/"
            floor = _close_run(source, clause, current, runs)
        leading: list[_Token] = []
        end = atom.span.start
        # Bounded: deeper nesting cannot parse, and the window keeps each search O(1).
        while len(leading) <= MAX_CONDITION_DEPTH and (
            match := _LEADING.search(source, max(floor, end - _LEADING_WINDOW), end)
        ):
            text = match.group().strip()
            kind = "open" if text == "(" else _WORD_TYPES[text.casefold()]
            word_start = match.start()
            leading.insert(0, _Token(kind, span_of(source, word_start, word_start + len(text))))
            end = word_start
        current = [*leading, token]
    if current:
        _close_run(source, clause, current, runs)
    return runs, slash


def _close_run(source: str, clause: SourceSpan, run: list[_Token], runs: list[list[_Token]]) -> int:
    end = run[-1].span.end
    while (match := _TRAILING.match(source, end, clause.end)) is not None:
        close = match.end() - 1
        run.append(_Token("close", span_of(source, close, close + 1)))
        end = match.end()
    runs.append(run)
    return end


def _adjacent_words(
    source: str, floor: int, start: int, allowed: frozenset[str]
) -> list[SourceSpan]:
    """Contiguous allowed modifier words immediately before ``start``."""
    found: list[SourceSpan] = []
    position = start
    while True:
        cut = position
        while cut > floor and source[cut - 1].isspace():
            cut -= 1
        word_start = cut
        while word_start > floor and source[word_start - 1].isalpha():
            word_start -= 1
        if cut == position or word_start == cut:
            return found
        if source[word_start:cut].casefold() not in allowed:
            return found
        found.append(span_of(source, word_start, cut))
        position = word_start


def _language_suffixes(
    source: str, clause: SourceSpan, signals: list[LexicalSignal]
) -> list[SourceSpan]:
    found = []
    for signal in signals:
        if signal.kind != "language":
            continue
        match = _NEXT_WORD.match(source, signal.span.end, clause.end)
        if match and match.group("word").casefold() in LANGUAGE_SUFFIXES:
            found.append(span_of(source, match.start("word"), match.end("word")))
    return found


def _education_term_end(
    source: str, education: list[LexicalSignal], limit: int
) -> tuple[int, list[SourceSpan]]:
    """End of the explicitly interpreted degree term and any related-field span.

    Grammar: consecutive education words; optionally ``in/of/der/des/im`` plus a
    field of at most four words that stops at filler, connectives or punctuation;
    optionally "or a related field" directly after. Anything later stays outside
    the term, so the coverage rule can send it to review.
    """
    end = education[0].span.end
    for signal in education[1:]:
        if signal.span.start >= limit or source[end : signal.span.start].strip():
            break
        end = signal.span.end
    link = _FIELD_LINK.match(source, end, limit)
    if link is not None:
        position, words = link.end(), 0
        while words < MAX_FIELD_WORDS:
            word = _FIELD_WORD.match(source, position, limit)
            if word is None or word.group().casefold() in _FIELD_STOP:
                break
            end, words = word.end(), words + 1
            space = _FIELD_SPACE.match(source, end, limit)
            if space is None:
                break
            position = space.end()
    gap = _FIELD_GAP.match(source, end, limit)
    alternative = FIELD_ALTERNATIVE.match(source, gap.end() if gap else end, limit)
    if alternative is not None:
        field = span_of(source, alternative.start(), alternative.end())
        return field.end, [field]
    return end, []


def _education(
    source: str, clause: SourceSpan, signals: list[LexicalSignal], stops: list[int]
) -> tuple[Condition | None, list[SourceSpan]]:
    education = [signal for signal in signals if signal.kind == "education"]
    if not education:
        return None, []
    start = education[0].span.start
    limit = min([clause.end, *[stop for stop in stops if stop > start]])
    semicolon = source.find(";", start, limit)
    limit = semicolon if semicolon != -1 else limit
    term_end, fields = _education_term_end(source, education, limit)
    term = ConditionTerm(term_kind="education", span=span_of(source, start, term_end))
    fields = [*_adjacent_words(source, clause.start, start, EDUCATION_MODIFIERS), *fields]
    for match in EQUIVALENT.finditer(source, term_end, limit):
        conn = span_of(source, match.start("conn"), match.end("conn"))
        right = span_of(source, match.start("term"), match.end("term"))
        kind: TermKind = (
            "equivalent_experience"
            if right.quote.casefold().endswith(_EXPERIENCE_WORDS)
            else "equivalent_qualification"
        )
        group = ConditionGroup(
            node="any",
            span=span_of(source, start, right.end),
            connectives=[conn],
            children=[term, ConditionTerm(term_kind=kind, span=right)],
        )
        # Words between the degree term and "or equivalent …" are not part of
        # either term; coverage sends them to review.
        return group, [*fields, conn]
    return term, fields


def _duration(source: str, clause: SourceSpan, signal: LexicalSignal) -> Threshold | ReviewReason:
    parts = _AMOUNT.fullmatch(signal.span.quote)
    if parts is None:
        return "unsupported_number"
    number, unit_text = parts["number"], parts["unit"]
    unit: Literal["years", "months"] = (
        "years" if unit_text.casefold().startswith(("year", "jahr")) else "months"
    )
    gte = _prefix(PREFIX_GTE, source, clause.start, signal.span.start)
    gt = _prefix(PREFIX_GT, source, clause.start, signal.span.start)
    if _prefix(UNSUPPORTED_PREFIX, source, clause.start, signal.span.start) or (
        UNSUPPORTED_POSTFIX.match(source, signal.span.end, clause.end)
    ):
        return "unsupported_number"
    folded = " ".join(number.split()).casefold()
    if folded in _VAGUE:
        return "vague_quantity"
    plus, upper = False, None
    operator: Operator
    if folded in _WORD_NUMBERS:
        value = _WORD_NUMBERS[folded]
    elif (parsed := _NUMBER.fullmatch(number)) is not None:
        if any(len(n) > 1 and n.startswith("0") for n in (parsed["value"], parsed["upper"] or "")):
            return "unsupported_number"
        value, plus = int(parsed["value"]), parsed["plus"] is not None
        upper = int(parsed["upper"]) if parsed["upper"] else None
    else:
        return "unsupported_number"
    if value > MAX_DURATION or (upper is not None and upper > MAX_DURATION):
        return "unsupported_number"
    if upper is not None:
        if plus or gte or gt or upper <= value:
            return "unsupported_number"
        operator = "range"
    elif gt:
        if plus:
            return "unsupported_number"
        operator = "gt"
    else:
        operator = "gte" if gte or plus else "unqualified"
    prefix = gte or gt
    start = prefix.start() if prefix else signal.span.start
    return Threshold(
        measure="duration",
        operator=operator,
        value=value,
        upper=upper,
        unit=unit,
        span=span_of(source, start, signal.span.end),
    )


def _cefr(source: str, clause: SourceSpan, match: re.Match[str]) -> Threshold | ReviewReason:
    start, end = clause.start + match.start(), clause.start + match.end()
    gte = _prefix(PREFIX_GTE, source, clause.start, start)
    gt = _prefix(PREFIX_GT, source, clause.start, start)
    if _prefix(UNSUPPORTED_PREFIX, source, clause.start, start) or (
        UNSUPPORTED_POSTFIX.match(source, end, clause.end)
    ):
        return "unsupported_number"
    raised = bool(match["plus"] or match["suffix"] or gte)
    if gt or (match["upper"] and (raised or match["upper"] <= match["level"])):
        return "unsupported_number"
    operator: Operator = "range" if match["upper"] else ("gte" if raised else "unqualified")
    begin = gte.start() if gte else start
    return Threshold(
        measure="language_level",
        operator=operator,
        level=cast(CefrLevel, match["level"]),
        upper_level=cast(CefrLevel | None, match["upper"]),
        unit="cefr",
        span=span_of(source, begin, end),
    )


def _scope(
    source: str, threshold: Threshold, clause: SourceSpan, stops: list[int]
) -> SourceSpan | None:
    """``stops`` is sorted: cue/negation starts and every numeric anchor."""
    after = threshold.span.end
    index = bisect.bisect_left(stops, after)
    limit = min(clause.end, stops[index]) if index < len(stops) else clause.end
    for mark in (";", "("):
        found = source.find(mark, after, limit)
        limit = found if found != -1 else limit
    lead = _SCOPE_LEAD.match(source, after, limit)
    start = lead.end() if lead else after
    end = trim_end(source, start, limit)
    if end <= start or not any(char.isalpha() for char in source[start:end]):
        return None  # e.g. "3 years of." has no scope, not the scope "of"
    return span_of(source, start, end)


def _captured_durations(
    source: str, clause: SourceSpan, signals: list[LexicalSignal]
) -> tuple[list[LexicalSignal], bool]:
    """Keep year/month signals that exactly match a numeric amount in the clause.

    Returns (usable signals, partial) where ``partial`` marks an amount the
    lexical signal did not capture exactly (four digits, "3yrs", "10,000 years").
    A signal inside such a larger amount is dropped so it cannot invent a value.
    """
    years = [signal for signal in signals if signal.kind == "years"]
    starts = [signal.span.start for signal in years]
    exact = {(signal.span.start, signal.span.end) for signal in years}
    dropped: set[int] = set()
    partial = False
    for amount in ANY_DURATION.finditer(clause.quote):
        start, end = clause.start + amount.start(), clause.start + amount.end()
        if (start, end) in exact:
            continue
        partial = True
        index = bisect.bisect_left(starts, start)
        while index < len(years) and years[index].span.start < end:
            dropped.add(index)
            index += 1
    return [signal for index, signal in enumerate(years) if index not in dropped], partial


def _leaf_spans(node: Condition) -> list[SourceSpan]:
    if isinstance(node, ConditionGroup):
        return [*node.connectives, *(s for child in node.children for s in _leaf_spans(child))]
    return [node.span]


def _uninterpreted(source: str, clause: SourceSpan, interpreted: list[SourceSpan]) -> bool:
    """True when a word outside every interpreted span is not a known filler word."""
    cover = SpanCover(interpreted)
    for match in _WORDS.finditer(clause.quote):
        word = span_of(source, clause.start + match.start(), clause.start + match.end())
        if not cover.contains(word) and word.quote.casefold() not in FILLER:
            return True
    return False


def _symbols(clause: SourceSpan) -> list[tuple[int, str]]:
    return [(clause.start + i, char) for i, char in enumerate(clause.quote) if char in "/|&+"]


def _list_continues(
    source: str, clause: SourceSpan, run: SourceSpan, protected: list[SourceSpan]
) -> bool:
    """True when a comma/semicolon joins the term run to further unrecognized text.

    A comma that only separates the run from a cue/negation (``Ideally, Python``)
    or ends the clause does not extend the list.
    """
    starts = {span.start for span in protected}
    ends = {span.end for span in protected}
    after = run.end
    while after < clause.end and source[after].isspace():
        after += 1
    if after < clause.end and source[after] in ",;":
        rest = after + 1
        while rest < clause.end and source[rest].isspace():
            rest += 1
        if rest < clause.end and rest not in starts and source[rest] not in ".;:!?)":
            return True
    before = run.start
    while before > clause.start and source[before - 1].isspace():
        before -= 1
    if before > clause.start and source[before - 1] in ",;":
        prior = before - 1
        while prior > clause.start and source[prior - 1].isspace():
            prior -= 1
        if prior > clause.start and prior not in ends:
            return True
    return False


def analyze_structure(
    source: str,
    clause: SourceSpan,
    signals: list[LexicalSignal],
    protected: list[SourceSpan],
) -> Structure:
    """Return the supported condition/thresholds and review reasons for one clause.

    ``protected`` holds cue and negation spans: they end threshold scopes and
    education phrases, and connectives inside them are not unparsed grammar.
    """
    result = Structure()
    cue_starts = sorted(span.start for span in protected)
    cefr_matches = list(CEFR.finditer(clause.quote))
    if len(cefr_matches) > MAX_CLAUSE_LEVELS:
        raise ExtractionError("a JD clause exceeds 4096 annotations; review the source")
    anchors = sorted(
        [signal.span.start for signal in signals if signal.kind == "years"]
        + [clause.start + match.start() for match in cefr_matches]
    )
    consumed: list[SourceSpan] = list(protected)
    languages = [signal for signal in signals if signal.kind == "language"]
    found_all: list[Threshold] = []
    years, partial = _captured_durations(source, clause, signals)
    kept = SpanCover(signal.span for signal in years)
    if partial or any(
        not kept.contains(span_of(source, clause.start + m.start(), clause.start + m.end()))
        for m in UNIT_WORD.finditer(clause.quote)
    ):
        result.reasons.add("unsupported_number")  # e.g. "six years", "3-year"
    for item in [
        *(_duration(source, clause, s) for s in years),
        *(_cefr(source, clause, match) for match in cefr_matches),
    ]:
        if isinstance(item, str):
            result.reasons.add(item)
        else:
            found_all.append(item)
    # A scope ends at the next cue/negation, numeric anchor or threshold (with its prefix).
    amounts = [clause.start + m.start() for m in ANY_DURATION.finditer(clause.quote)]
    stops = sorted({*anchors, *amounts, *cue_starts, *(t.span.start for t in found_all)})
    for item in found_all:
        if item.measure == "duration":
            scope = _scope(source, item, clause, stops)
        else:
            scope = languages[0].span if len(languages) == 1 else None
        result.thresholds.append(item.model_copy(update={"scope": scope}))
    result.thresholds.sort(key=lambda item: (item.span.start, item.span.end))
    accepted = SpanCover(item.span for item in result.thresholds)
    if result.thresholds and any(
        not accepted.contains(span_of(source, clause.start + m.start(), clause.start + m.end()))
        for m in OPERATOR_WORD.finditer(clause.quote)
    ):
        result.reasons.add("unsupported_number")
        result.thresholds = []
    for threshold in result.thresholds:
        consumed.append(threshold.span)
        if threshold.scope is None:
            result.reasons.add("threshold_scope_unclear")
    if len(result.thresholds) > 1:
        result.reasons.add("multiple_thresholds")

    atoms = [signal for signal in signals if signal.kind in {"technology", "language"}]
    education, education_consumed = _education(
        source, clause, signals, cue_starts + [t.span.start for t in result.thresholds]
    )
    consumed.extend(education_consumed)
    condition: Condition | None = None
    runs, slash = _runs(source, clause, atoms) if atoms else ([], False)
    if slash:
        result.reasons.add("unparsed_alternative")
    if education is not None and atoms:
        result.reasons.add("unsupported_grouping")
    elif education is not None:
        condition = education
    elif len(runs) == 1 and len([t for t in runs[0] if t.type == "atom"]) <= MAX_CONDITION_TERMS:
        try:
            condition = _Parser(runs[0]).parse(source)
            run = span_of(source, runs[0][0].span.start, runs[0][-1].span.end)
            consumed.append(run)
            if _list_continues(source, clause, run, protected):
                result.reasons.add("unsupported_grouping")
        except _Unsupported:
            result.reasons.add("unsupported_grouping")
    elif runs:
        result.reasons.add("unsupported_grouping")

    cover = SpanCover(consumed)
    # Symbol separators outside a recognized term or supported structure can join
    # an unrecognized operand ("Python / Rust", "Python & QuuxDB"); never drop them.
    terms = SpanCover(signal.span for signal in signals)
    for index, char in _symbols(clause):
        mark = span_of(source, index, index + 1)
        if not cover.contains(mark) and not terms.contains(mark):
            result.reasons.add("unparsed_alternative" if char in "/|" else "unparsed_conjunction")
    for match in CONNECTIVE.finditer(clause.quote):
        found = span_of(source, clause.start + match.start(), clause.start + match.end())
        if cover.contains(found):
            continue
        word = " ".join(found.quote.split()).casefold()
        result.reasons.add(
            "unparsed_alternative" if word in _ALTERNATIVES else "unparsed_conjunction"
        )
    interpreted = [
        *consumed,
        *(signal.span for signal in signals),
        *_language_suffixes(source, clause, signals),
    ]
    if condition is not None:
        interpreted.extend(_leaf_spans(condition))
    else:
        # Without a condition, a threshold's literal scope is its interpretation.
        interpreted.extend(t.scope for t in result.thresholds if t.scope is not None)
    withheld = {"unparsed_alternative", "unparsed_conjunction", "unsupported_grouping"}
    # Only when no other rule already withholds the condition: then any uncovered
    # non-filler word could be an unrecognized operand ("Python with QuuxDB").
    if (
        not result.reasons & withheld
        and (condition is not None or result.thresholds)
        and _uninterpreted(source, clause, interpreted)
    ):
        result.reasons.add("uninterpreted_text")
        # Unplaced words may qualify the numbers too: withhold thresholds as well.
        result.thresholds = []
        result.reasons -= {"threshold_scope_unclear", "multiple_thresholds"}
    if result.reasons & (withheld | {"uninterpreted_text"}):
        condition = None  # never emit a partial condition or split an OR
    result.condition = condition
    if condition is None and not result.thresholds:
        result.reasons.add("no_supported_condition")
    return result
