"""Deterministic evaluation of typed constraints against approved facts (TASK-015).

States are ``direct``, ``explicitly_unmet``, ``no_evidence`` and ``unknown``;
none is an application decision. Nothing is inferred: test scores are never
converted to CEFR, self-descriptions are never parsed, native is never C2,
authorization comes only from an exact approved statement (never location,
residence, nationality or student status), roles are compared as written, and
durations are calendar months from scoped intervals, never summed overlaps and
never FTE.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import Field

from ..domain.common import ShortText, StrictModel
from ..domain.fact import (
    AuthorizationFact,
    AuthorizationValue,
    CredentialFact,
    CredentialValue,
    EducationFact,
    EmploymentFact,
    FactRef,
    LanguageFact,
    ProjectFact,
)
from ..domain.profile import ProfileRevision
from ..domain.requirement import CefrLevel, Threshold
from ..normalization.aliases import normalize_surface
from ..normalization.dictionary import CONCEPTS, ConceptId
from ..profile.review import LocalReviewReceipt
from ..profile.validation import validate_profile
from ..verification.support import EvidenceKey
from .durations import ExclusionReason, earliest_day, latest_day, union_bounds

MatchState = Literal["direct", "explicitly_unmet", "no_evidence", "unknown"]
Rationale = Literal[
    "no_language_fact",
    "required_level_unspecified",
    "cefr_meets",
    "cefr_below",
    "assessment_not_comparable",
    "no_credential_fact",
    "credential_valid",
    "credential_status_unknown",
    "award_date_precision",
    "credential_in_progress",
    "awarded_after_as_of",
    "credential_expired",
    "no_degree_fact",
    "degree_in_progress",
    "degree_withdrawn",
    "degree_status_unknown",
    "degree_completed",
    "completed_after_as_of",
    "completion_precision",
    "authorization_not_recorded",
    "authorization_status_unknown",
    "statement_after_as_of",
    "statement_date_precision",
    "authorization_expired_needs_review",
    "authorization_statement_matches",
    "no_matching_authorization_statement",
    "duration_meets",
    "no_scoped_interval",
    "only_unknown_dates",
    "precision_insufficient",
    "below_threshold_with_unknown_intervals",
    "documented_below_threshold",
]
_CEFR = ("A1", "A2", "B1", "B2", "C1", "C2")
MAX_DURATION_MONTHS = 1200


class ConstraintError(ValueError):
    """A constraint outside the supported, reviewed vocabulary."""


class LanguageConstraint(StrictModel):
    type: Literal["language"]
    language: ShortText
    min_level: CefrLevel | None


class CredentialConstraint(StrictModel):
    type: Literal["credential"]
    name: ShortText


class DegreeConstraint(StrictModel):
    type: Literal["degree"]
    degree_name: ShortText


class AuthorizationConstraint(StrictModel):
    type: Literal["authorization"]
    country: ShortText
    scope: ShortText | None = None


class OverallScope(StrictModel):
    kind: Literal["overall"]


class SkillScope(StrictModel):
    kind: Literal["skill"]
    concept: ConceptId


class RoleScope(StrictModel):
    kind: Literal["role"]
    title: ShortText


DurationScope = Annotated[OverallScope | SkillScope | RoleScope, Field(discriminator="kind")]


class DurationConstraint(StrictModel):
    type: Literal["duration"]
    months: int = Field(strict=True, ge=1, le=MAX_DURATION_MONTHS)
    scope: DurationScope


Constraint = Annotated[
    LanguageConstraint
    | CredentialConstraint
    | DegreeConstraint
    | AuthorizationConstraint
    | DurationConstraint,
    Field(discriminator="type"),
]


class ConstraintResult(StrictModel):
    constraint: Constraint
    as_of: date
    state: MatchState
    rationale: Rationale
    fact_refs: list[FactRef] = Field(default_factory=list, max_length=4096)
    lower_months: int | None = Field(default=None, strict=True, ge=0)
    upper_months: int | None = Field(default=None, strict=True, ge=0)
    excluded: dict[str, ExclusionReason] = Field(default_factory=dict)
    basis: Literal["calendar_months_not_fte"] | None = None


def months_from_threshold(threshold: Threshold) -> int:
    """Minimum whole months for a TASK-012 duration threshold.

    ``gte`` and ``unqualified`` ("3 years experience") are minimums, ``gt`` adds
    one month, and a ``range`` uses its lower bound. CEFR thresholds are not
    durations.
    """

    if threshold.measure != "duration" or threshold.value is None:
        raise ConstraintError("only duration thresholds convert to months")
    months = threshold.value * (12 if threshold.unit == "years" else 1)
    if threshold.operator == "gt":
        months += 1
    if not 1 <= months <= MAX_DURATION_MONTHS:
        raise ConstraintError("duration threshold is outside the supported range")
    return months


def _name(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split()).casefold()


_CONCEPT_KINDS = {concept.concept_id: concept.kind for concept in CONCEPTS}


def _language_key(text: str) -> tuple[str, str] | None:
    """Identity of a language surface, or None if it is not a language.

    An exact (non-ambiguous) TASK-013 language concept gives concept identity;
    a surface no alias covers compares by normalized name. An ambiguous alias or
    a technology/field concept is not a language and never matches.
    """

    mention = normalize_surface(text)
    if mention.status == "unmatched":
        return "name", _name(text)
    if (
        mention.status == "matched"
        and mention.concept_id is not None
        and _CONCEPT_KINDS.get(mention.concept_id) == "language"
    ):
        return "concept", mention.concept_id
    return None


def _expired(value: CredentialValue | AuthorizationValue, as_of: date) -> bool:
    if value.expires_at is not None and value.expires_at.astimezone(UTC).date() < as_of:
        return True
    return value.valid_through is not None and latest_day(value.valid_through) < as_of


def _refs(facts: Sequence[Any]) -> list[FactRef]:
    return [
        FactRef(fact_id=fact.fact_id, revision=fact.revision)
        for fact in sorted(facts, key=lambda fact: fact.fact_id)
    ]


def _result(
    constraint: Any, as_of: date, state: MatchState, rationale: Rationale, facts: Sequence[Any]
) -> ConstraintResult:
    return ConstraintResult(
        constraint=constraint, as_of=as_of, state=state, rationale=rationale, fact_refs=_refs(facts)
    )


def _language(constraint: LanguageConstraint, facts: list[Any], as_of: date) -> ConstraintResult:
    key = _language_key(constraint.language)
    if key is None:
        raise ConstraintError("language constraint names a term that is not a language")
    matching = [
        fact
        for fact in facts
        if isinstance(fact, LanguageFact) and _language_key(fact.language) == key
    ]
    if not matching:
        return _result(constraint, as_of, "no_evidence", "no_language_fact", [])
    if constraint.min_level is None:
        return _result(constraint, as_of, "unknown", "required_level_unspecified", matching)
    wanted = _CEFR.index(constraint.min_level)
    meeting = [
        fact
        for fact in matching
        if fact.assessment.assessment == "cefr" and _CEFR.index(fact.assessment.level) >= wanted
    ]
    if meeting:
        return _result(constraint, as_of, "direct", "cefr_meets", meeting)
    if all(fact.assessment.assessment == "cefr" for fact in matching):
        return _result(constraint, as_of, "explicitly_unmet", "cefr_below", matching)
    return _result(constraint, as_of, "unknown", "assessment_not_comparable", matching)


def _credential(
    constraint: CredentialConstraint, facts: list[Any], as_of: date
) -> ConstraintResult:
    wanted = _name(constraint.name)
    matching = [
        fact
        for fact in facts
        if isinstance(fact, CredentialFact) and _name(fact.value.name) == wanted
    ]
    if not matching:
        return _result(constraint, as_of, "no_evidence", "no_credential_fact", [])

    def outcome(value: CredentialValue) -> str:
        if value.status != "awarded":
            return value.status
        if value.awarded_on is not None and earliest_day(value.awarded_on) > as_of:
            return "not_yet_awarded"
        if value.awarded_on is not None and latest_day(value.awarded_on) > as_of:
            return "award_uncertain"
        return "expired" if _expired(value, as_of) else "valid"

    outcomes = {fact.fact_id: outcome(fact.value) for fact in matching}
    valid = [fact for fact in matching if outcomes[fact.fact_id] == "valid"]
    if valid:
        return _result(constraint, as_of, "direct", "credential_valid", valid)
    present = set(outcomes.values())
    order: tuple[tuple[str, MatchState, Rationale], ...] = (
        ("unknown", "unknown", "credential_status_unknown"),
        ("award_uncertain", "unknown", "award_date_precision"),
        ("in_progress", "explicitly_unmet", "credential_in_progress"),
        ("not_yet_awarded", "explicitly_unmet", "awarded_after_as_of"),
    )
    for key, state, rationale in order:
        if key in present:
            return _result(constraint, as_of, state, rationale, matching)
    return _result(constraint, as_of, "explicitly_unmet", "credential_expired", matching)


def _degree(constraint: DegreeConstraint, facts: list[Any], as_of: date) -> ConstraintResult:
    wanted = _name(constraint.degree_name)
    matching = [
        fact
        for fact in facts
        if isinstance(fact, EducationFact)
        and fact.degree_name is not None
        and _name(fact.degree_name) == wanted
    ]
    if not matching:
        return _result(constraint, as_of, "no_evidence", "no_degree_fact", [])
    found: dict[Rationale, list[EducationFact]] = {}
    for fact in matching:
        rationale: Rationale
        if fact.degree_status == "ongoing":
            rationale = "degree_in_progress"
        elif fact.degree_status == "withdrawn":
            rationale = "degree_withdrawn"
        elif fact.degree_status == "unknown":
            rationale = "degree_status_unknown"
        elif fact.completion_date is None or latest_day(fact.completion_date) <= as_of:
            rationale = "degree_completed"
        elif earliest_day(fact.completion_date) > as_of:
            rationale = "completed_after_as_of"
        else:
            rationale = "completion_precision"
        found.setdefault(rationale, []).append(fact)
    order: tuple[tuple[Rationale, MatchState], ...] = (
        ("degree_completed", "direct"),
        ("degree_status_unknown", "unknown"),
        ("completion_precision", "unknown"),
        ("degree_in_progress", "explicitly_unmet"),
        ("completed_after_as_of", "explicitly_unmet"),
        ("degree_withdrawn", "explicitly_unmet"),
    )
    for rationale, state in order:
        if rationale in found:
            supporting = found[rationale] if state == "direct" else matching
            return _result(constraint, as_of, state, rationale, supporting)
    raise AssertionError("unreachable: every degree fact has an outcome")  # pragma: no cover


def _authorization(
    constraint: AuthorizationConstraint, facts: list[Any], as_of: date
) -> ConstraintResult:
    statements = [fact for fact in facts if isinstance(fact, AuthorizationFact)]
    if not statements:
        return _result(constraint, as_of, "unknown", "authorization_not_recorded", [])
    found: dict[str, list[AuthorizationFact]] = {}
    for fact in statements:
        value = fact.value
        if value.status != "known":
            outcome = "status_unknown"
        elif (
            value.country is None
            or _name(value.country) != _name(constraint.country)
            or (
                constraint.scope is not None
                and (value.scope is None or _name(value.scope) != _name(constraint.scope))
            )
        ):
            outcome = "no_match"
        elif value.as_of is not None and earliest_day(value.as_of) > as_of:
            outcome = "after"
        elif value.as_of is not None and latest_day(value.as_of) > as_of:
            outcome = "date_precision"
        elif _expired(value, as_of):
            outcome = "expired"
        else:
            outcome = "valid"
        found.setdefault(outcome, []).append(fact)
    if "valid" in found:
        return _result(
            constraint, as_of, "direct", "authorization_statement_matches", found["valid"]
        )
    for outcome, rationale in (
        ("after", "statement_after_as_of"),
        ("date_precision", "statement_date_precision"),
        ("expired", "authorization_expired_needs_review"),
        ("status_unknown", "authorization_status_unknown"),
    ):
        if outcome in found:
            return _result(constraint, as_of, "unknown", rationale, statements)  # type: ignore[arg-type]
    return _result(constraint, as_of, "unknown", "no_matching_authorization_statement", statements)


def _duration(constraint: DurationConstraint, facts: list[Any], as_of: date) -> ConstraintResult:
    scope = constraint.scope
    candidates: list[EmploymentFact | ProjectFact]
    if isinstance(scope, OverallScope):
        candidates = [fact for fact in facts if isinstance(fact, EmploymentFact)]
    elif isinstance(scope, RoleScope):
        title = _name(scope.title)
        candidates = [
            fact
            for fact in facts
            if isinstance(fact, EmploymentFact) and _name(fact.title) == title
        ]
    else:
        kind = _CONCEPT_KINDS.get(scope.concept)
        if kind is None:
            raise ConstraintError("duration scope names an unknown concept")
        if kind == "language":
            raise ConstraintError("a language is not a duration skill scope")
        candidates = []
        for fact in facts:
            if not isinstance(fact, ProjectFact):
                continue
            for technology in fact.technologies:
                mention = normalize_surface(technology)
                if mention.status == "matched" and mention.concept_id == scope.concept:
                    candidates.append(fact)
                    break
    bounds = union_bounds([(fact.fact_id, fact.period) for fact in candidates], as_of)
    by_id = {fact.fact_id: fact for fact in candidates}
    state: MatchState
    rationale: Rationale
    if bounds.lower_months >= constraint.months:
        state, rationale = "direct", "duration_meets"
    elif not bounds.contributing and not bounds.uncertain:
        state, rationale = "no_evidence", "no_scoped_interval"
    elif not bounds.contributing:
        state, rationale = "unknown", "only_unknown_dates"
    elif bounds.upper_months >= constraint.months:
        state, rationale = "unknown", "precision_insufficient"
    elif bounds.uncertain:
        state, rationale = "unknown", "below_threshold_with_unknown_intervals"
    else:
        state, rationale = "unknown", "documented_below_threshold"
    return ConstraintResult(
        constraint=constraint,
        as_of=as_of,
        state=state,
        rationale=rationale,
        fact_refs=_refs([by_id[fact_id] for fact_id in bounds.contributing]),
        lower_months=bounds.lower_months,
        upper_months=bounds.upper_months,
        excluded=dict(sorted(bounds.excluded.items())),
        basis="calendar_months_not_fte",
    )


def evaluate_constraints(
    profile: ProfileRevision,
    constraints: Sequence[Constraint],
    *,
    as_of: date,
    reviews: Sequence[LocalReviewReceipt] = (),
    support_captures: Mapping[EvidenceKey, bytes | bytearray] | None = None,
) -> list[ConstraintResult]:
    """Evaluate each constraint against the profile's approved facts at ``as_of``."""

    if isinstance(as_of, datetime) or not isinstance(as_of, date):
        raise ConstraintError("as_of must be a calendar date")
    validate_profile(profile, reviews=reviews, support_captures=support_captures)
    facts = [fact for fact in profile.facts if fact.status == "approved"]
    results = []
    for constraint in constraints:
        if isinstance(constraint, LanguageConstraint):
            results.append(_language(constraint, facts, as_of))
        elif isinstance(constraint, CredentialConstraint):
            results.append(_credential(constraint, facts, as_of))
        elif isinstance(constraint, DegreeConstraint):
            results.append(_degree(constraint, facts, as_of))
        elif isinstance(constraint, AuthorizationConstraint):
            results.append(_authorization(constraint, facts, as_of))
        elif isinstance(constraint, DurationConstraint):
            results.append(_duration(constraint, facts, as_of))
        else:  # pragma: no cover - the discriminated union is exhaustive
            raise ConstraintError("unsupported constraint type")
    return results
