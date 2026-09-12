"""Shared bounded scalar and date types for the profile schema."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StringConstraints, model_validator

StableId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_-]*$"
    ),
]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitObject = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40,64}$")]
Locale = Literal["en", "de"]
RecordStatus = Literal["draft", "approved", "revoked"]


class StrictModel(BaseModel):
    """Base model: no unknown keys, no Python-side scalar coercion, bounded records."""

    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)


class YearDate(StrictModel):
    precision: Literal["year"]
    year: StrictInt = Field(ge=1, le=9999)


class MonthDate(StrictModel):
    precision: Literal["month"]
    year: StrictInt = Field(ge=1, le=9999)
    month: StrictInt = Field(ge=1, le=12)


class DayDate(StrictModel):
    precision: Literal["day"]
    year: StrictInt = Field(ge=1, le=9999)
    month: StrictInt = Field(ge=1, le=12)
    day: StrictInt = Field(ge=1, le=31)

    @model_validator(mode="after")
    def valid_calendar_date(self) -> DayDate:
        try:
            date(self.year, self.month, self.day)
        except ValueError as error:
            raise ValueError("day is not a valid calendar date") from error
        return self


DatePoint = Annotated[YearDate | MonthDate | DayDate, Field(discriminator="precision")]
DateState = Literal["known", "ongoing", "unknown"]


def _date_key(value: DatePoint) -> tuple[int, int, int]:
    if isinstance(value, YearDate):
        return value.year, 0, 0
    if isinstance(value, MonthDate):
        return value.year, value.month, 0
    return value.year, value.month, value.day


class DateRange(StrictModel):
    """A period with explicit unknown and ongoing states and no implicit Present."""

    start: DatePoint | None = None
    start_state: Literal["known", "unknown"] = "unknown"
    end: DatePoint | None = None
    end_state: DateState = "unknown"

    @model_validator(mode="after")
    def validate_states_and_order(self) -> DateRange:
        if (self.start is None) != (self.start_state == "unknown"):
            raise ValueError("start and start_state disagree")
        if self.end_state == "known" and self.end is None:
            raise ValueError("known end requires an end date")
        if self.end_state != "known" and self.end is not None:
            raise ValueError("only a known end may carry an end date")
        if (
            self.start is not None
            and self.end is not None
            and _date_key(self.start) > _date_key(self.end)
        ):
            raise ValueError("date range is reversed")
        return self
