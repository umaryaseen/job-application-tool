"""Typed factual records. Cross-record graph validation belongs to TASK-003."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .common import DatePoint, DateRange, LongText, ShortText, StableId, StrictModel
from .evidence import EvidenceRef, FactApproval


class ContactEmail(StrictModel):
    kind: Literal["email"]
    value: Annotated[
        str, Field(min_length=3, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    ]


class ContactPhone(StrictModel):
    kind: Literal["phone"]
    value: Annotated[str, Field(min_length=3, max_length=40, pattern=r"^[+0-9() .-]+$")]


class ContactUrl(StrictModel):
    kind: Literal["url"]
    value: Annotated[str, Field(min_length=8, max_length=2048, pattern=r"^https?://[^\s]+$")]


class ContactLocation(StrictModel):
    kind: Literal["location"]
    value: ShortText


ContactValue = Annotated[
    ContactEmail | ContactPhone | ContactUrl | ContactLocation, Field(discriminator="kind")
]


class Metric(StrictModel):
    value: Decimal
    unit: Literal["count", "percent", "percentage_points", "currency", "months", "years", "other"]
    operator: Literal["exact", "approximately", "at_least", "at_most"] = "exact"
    currency: Annotated[str, Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")] | None = None
    context: ShortText | None = None
    period: DateRange | None = None

    @field_validator("value", mode="before")
    @classmethod
    def require_decimal_representation(cls, value: object) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if not isinstance(value, str):
            raise ValueError("metric values must be decimal strings")
        try:
            parsed = Decimal(value)
        except InvalidOperation as error:
            raise ValueError("metric value is not a decimal") from error
        if not parsed.is_finite():
            raise ValueError("metric value must be finite")
        return parsed

    @model_validator(mode="after")
    def validate_currency(self) -> Metric:
        if self.unit == "currency" and self.currency is None:
            raise ValueError("currency metrics require a currency code")
        if self.unit != "currency" and self.currency is not None:
            raise ValueError("currency code is only valid for currency metrics")
        return self


class LanguageCEFR(StrictModel):
    assessment: Literal["cefr"]
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    assessed_on: DatePoint | None = None


class LanguageSelfDescription(StrictModel):
    assessment: Literal["self_description"]
    description: ShortText
    assessed_on: DatePoint | None = None


class LanguageTestScore(StrictModel):
    assessment: Literal["test_score"]
    test_name: ShortText
    score: Decimal
    scale: ShortText | None = None
    tested_on: DatePoint | None = None

    @field_validator("score", mode="before")
    @classmethod
    def require_score_decimal(cls, value: object) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if not isinstance(value, str):
            raise ValueError("test scores must be decimal strings")
        try:
            score = Decimal(value)
        except InvalidOperation as error:
            raise ValueError("test score is not a decimal") from error
        if not score.is_finite():
            raise ValueError("test score must be finite")
        return score


LanguageAssessment = Annotated[
    LanguageCEFR | LanguageSelfDescription | LanguageTestScore,
    Field(discriminator="assessment"),
]


class CredentialValue(StrictModel):
    name: ShortText
    issuer: ShortText | None = None
    status: Literal["awarded", "in_progress", "expired", "unknown"]
    awarded_on: DatePoint | None = None
    expires_at: datetime | None = None
    valid_through: DatePoint | None = None

    @field_validator("expires_at")
    @classmethod
    def expiry_is_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("credential expiry must include a timezone")
        return value

    @model_validator(mode="after")
    def status_matches_expiry(self) -> CredentialValue:
        if self.status == "expired" and self.expires_at is None and self.valid_through is None:
            raise ValueError("expired credentials require an expiry or valid-through date")
        return self


class AuthorizationValue(StrictModel):
    status: Literal["known", "unknown"]
    country: ShortText | None = None
    scope: ShortText | None = None
    as_of: DatePoint | None = None
    expires_at: datetime | None = None
    valid_through: DatePoint | None = None

    @field_validator("expires_at")
    @classmethod
    def authorization_expiry_is_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("authorization expiry must include a timezone")
        return value


class FactBase(StrictModel):
    fact_id: StableId
    revision: int = Field(strict=True, ge=1)
    subject_id: StableId
    status: Literal["draft", "approved", "revoked"] = "draft"
    evidence_refs: list[EvidenceRef] = Field(min_length=1, max_length=32)
    support_binding_refs: list[StableId] = Field(default_factory=list, max_length=32)
    approval: FactApproval | None = None

    @model_validator(mode="after")
    def approved_requires_approval(self) -> FactBase:
        if self.status == "approved" and self.approval is None:
            raise ValueError("approved facts require a hash-bound approval")
        return self


class FactRef(StrictModel):
    fact_id: StableId
    revision: int = Field(strict=True, ge=1)


class ContactFact(FactBase):
    kind: Literal["contact"]
    value: ContactValue


class EmploymentFact(FactBase):
    kind: Literal["employment"]
    employer_id: StableId
    title: ShortText
    period: DateRange
    location: ShortText | None = None
    description: LongText | None = None
    metrics: list[Metric] = Field(default_factory=list, max_length=32)


class EducationFact(FactBase):
    kind: Literal["education"]
    institution_id: StableId
    program: ShortText
    degree_name: ShortText | None = None
    degree_status: Literal["ongoing", "completed", "withdrawn", "unknown"]
    period: DateRange
    completion_date: DatePoint | None = None


class SkillFact(FactBase):
    kind: Literal["skill"]
    name: ShortText
    context: Literal["used", "exposure", "study", "unknown"]
    proficiency: Literal["unknown", "beginner", "intermediate", "advanced", "expert"] = "unknown"
    last_used: DatePoint | None = None
    notes: ShortText | None = None


class LanguageFact(FactBase):
    kind: Literal["language"]
    language: ShortText
    assessment: LanguageAssessment


class AuthorizationFact(FactBase):
    kind: Literal["authorization"]
    value: AuthorizationValue


class CredentialFact(FactBase):
    kind: Literal["credential"]
    value: CredentialValue


class MetricFact(FactBase):
    kind: Literal["metric"]
    metric: Metric


Fact = Annotated[
    (
        ContactFact
        | EmploymentFact
        | EducationFact
        | SkillFact
        | LanguageFact
        | AuthorizationFact
        | CredentialFact
        | MetricFact
    ),
    Field(discriminator="kind"),
]
