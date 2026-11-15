"""Calendar-month experience bounds from scoped approved intervals (TASK-015).

Each interval contributes a conservative lower month set (months it certainly
covered in full) and an upper month set (every month it may have touched),
given its date precision and a pinned as-of day. Results are the sizes of the
unions, so overlapping intervals count once and gaps never count. Durations are
calendar months, not full-time equivalents.
"""

from __future__ import annotations

import calendar
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Literal

from ..domain.common import DatePoint, DateRange, DayDate, MonthDate, YearDate

ExclusionReason = Literal["unknown_start", "unknown_end", "starts_after_as_of"]
UNCERTAIN: frozenset[ExclusionReason] = frozenset({"unknown_start", "unknown_end"})


def _month(year: int, month: int) -> int:
    return year * 12 + month - 1


def start_bounds(point: DatePoint) -> tuple[int, int]:
    """(lower, upper) first month of an interval starting at ``point``."""

    if isinstance(point, DayDate):
        month = _month(point.year, point.month)
        return (month if point.day == 1 else month + 1), month
    if isinstance(point, MonthDate):
        month = _month(point.year, point.month)
        return month + 1, month
    assert isinstance(point, YearDate)
    return _month(point.year + 1, 1), _month(point.year, 1)


def end_bounds(point: DatePoint) -> tuple[int, int]:
    """(lower, upper) last month of an interval ending at ``point``."""

    if isinstance(point, DayDate):
        month = _month(point.year, point.month)
        last = calendar.monthrange(point.year, point.month)[1]
        return (month if point.day == last else month - 1), month
    if isinstance(point, MonthDate):
        month = _month(point.year, point.month)
        return month - 1, month
    assert isinstance(point, YearDate)
    return _month(point.year - 1, 12), _month(point.year, 12)


def earliest_day(point: DatePoint) -> date:
    """First calendar day a date of this precision can denote."""

    if isinstance(point, DayDate):
        return date(point.year, point.month, point.day)
    if isinstance(point, MonthDate):
        return date(point.year, point.month, 1)
    assert isinstance(point, YearDate)
    return date(point.year, 1, 1)


def latest_day(point: DatePoint) -> date:
    """Last calendar day a date of this precision can denote."""

    if isinstance(point, DayDate):
        return date(point.year, point.month, point.day)
    if isinstance(point, MonthDate):
        return date(point.year, point.month, calendar.monthrange(point.year, point.month)[1])
    assert isinstance(point, YearDate)
    return date(point.year, 12, 31)


def _as_of_point(as_of: date) -> DayDate:
    return DayDate(precision="day", year=as_of.year, month=as_of.month, day=as_of.day)


@dataclass(frozen=True)
class IntervalMonths:
    """Inclusive month ranges; an empty range has ``end < start``."""

    lower: tuple[int, int]
    upper: tuple[int, int]


def interval_months(period: DateRange, as_of: date) -> IntervalMonths | ExclusionReason:
    """Month ranges of one period at ``as_of``, or why it cannot contribute."""

    if period.start is None:
        return "unknown_start"
    if period.end_state == "unknown":
        return "unknown_end"
    if earliest_day(period.start) > as_of:
        return "starts_after_as_of"
    cap_lower, cap_upper = end_bounds(_as_of_point(as_of))
    lower_start, upper_start = start_bounds(period.start)
    if period.end_state == "ongoing":
        lower_end, upper_end = cap_lower, cap_upper
    else:
        assert period.end is not None
        lower_end, upper_end = end_bounds(period.end)
    return IntervalMonths(
        lower=(lower_start, min(lower_end, cap_lower)),
        upper=(upper_start, min(upper_end, cap_upper)),
    )


def _union_size(ranges: list[tuple[int, int]]) -> int:
    """Number of distinct months covered by inclusive ranges (overlap once)."""

    total = 0
    current: tuple[int, int] | None = None
    for start, end in sorted(r for r in ranges if r[1] >= r[0]):
        if current is None or start > current[1] + 1:
            if current is not None:
                total += current[1] - current[0] + 1
            current = (start, end)
        else:
            current = (current[0], max(current[1], end))
    if current is not None:
        total += current[1] - current[0] + 1
    return total


@dataclass(frozen=True)
class DurationBounds:
    lower_months: int
    upper_months: int
    contributing: tuple[str, ...]
    excluded: dict[str, ExclusionReason]

    @property
    def uncertain(self) -> bool:
        return any(reason in UNCERTAIN for reason in self.excluded.values())


def union_bounds(periods: Iterable[tuple[str, DateRange]], as_of: date) -> DurationBounds:
    """Union of the month ranges of ``(fact_id, period)`` pairs at ``as_of``."""

    lower: list[tuple[int, int]] = []
    upper: list[tuple[int, int]] = []
    contributing: list[str] = []
    excluded: dict[str, ExclusionReason] = {}
    for fact_id, period in periods:
        months = interval_months(period, as_of)
        if isinstance(months, str):
            excluded[fact_id] = months
            continue
        if months.upper[1] >= months.upper[0]:
            contributing.append(fact_id)
        lower.append(months.lower)
        upper.append(months.upper)
    return DurationBounds(
        _union_size(lower), _union_size(upper), tuple(sorted(contributing)), excluded
    )
