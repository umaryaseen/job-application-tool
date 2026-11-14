"""Local human review receipts bound to exactly displayed revisions."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, cast

from pydantic import Field, field_validator

from ..domain.common import Sha256, StableId, StrictModel
from ..domain.evidence import (
    EvidenceApproval,
    EvidenceRecord,
    FactApproval,
    SupportBinding,
    VariantApproval,
)
from ..domain.fact import Fact
from ..domain.profile import ProfileRevision
from ..domain.variant import ApprovedVariant
from ..verification.support import (
    canonical_fact_payload,
    canonical_json,
    evidence_digest,
    sha256_text,
    support_bundle_digest,
)
from .validation import ProvenanceValidationError, ValidationIssue

ReviewText = Annotated[str, Field(min_length=1, max_length=20000)]


class LocalReviewReceipt(StrictModel):
    """A receipt issued only by the local review operation, never by an importer."""

    review_id: StableId
    issuer: Literal["local_human"]
    target_type: Literal["fact", "evidence", "variant"]
    target_id: StableId
    target_revision: int = Field(strict=True, ge=1)
    displayed_content: ReviewText
    displayed_content_sha256: Sha256
    support_bundle_sha256: Sha256
    decision: Literal["approve", "reject"]
    reviewer_id: StableId
    reviewed_at: datetime

    @field_validator("reviewed_at")
    @classmethod
    def reviewed_at_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("review timestamps must include a timezone")
        return value


def _find_target(
    profile: ProfileRevision, target_type: str, target_id: str, revision: int
) -> object:
    collection: list[object]
    if target_type == "fact":
        collection = list(profile.facts)
        id_name = "fact_id"
    elif target_type == "evidence":
        collection = list(profile.evidence)
        id_name = "evidence_id"
    else:
        collection = list(profile.variants)
        id_name = "variant_id"
    for item in collection:
        if getattr(item, id_name) == target_id and getattr(item, "revision", None) == revision:
            return item
    raise ProvenanceValidationError(
        [
            ValidationIssue(
                "missing_review_target", f"missing {target_type} {target_id} revision {revision}"
            )
        ]
    )


def _support_for_fact(
    profile: ProfileRevision, fact: Fact
) -> tuple[list[EvidenceRecord], list[SupportBinding]]:
    evidence = {(item.evidence_id, item.revision): item for item in profile.evidence}
    bindings = {item.binding_id: item for item in profile.support_bindings}
    resolved_evidence: list[EvidenceRecord] = []
    resolved_bindings: list[SupportBinding] = []
    for reference in fact.evidence_refs:
        item = evidence.get((reference.evidence_id, reference.revision))
        if item is None:
            raise ProvenanceValidationError(
                [
                    ValidationIssue(
                        "dangling_evidence", f"{fact.fact_id} review has missing evidence"
                    )
                ]
            )
        resolved_evidence.append(item)
    for binding_id in fact.support_binding_refs:
        binding = bindings.get(binding_id)
        if binding is None or (binding.fact_id, binding.fact_revision) != (
            fact.fact_id,
            fact.revision,
        ):
            raise ProvenanceValidationError(
                [
                    ValidationIssue(
                        "invalid_review_support",
                        f"{fact.fact_id} review has invalid support binding",
                    )
                ]
            )
        resolved_bindings.append(binding)
    return resolved_evidence, resolved_bindings


def record_human_review(
    profile: ProfileRevision,
    *,
    target_type: Literal["fact", "evidence", "variant"],
    target_id: str,
    target_revision: int,
    displayed_content: str,
    review_id: str,
    reviewer_id: str,
    reviewed_at: datetime,
    decision: Literal["approve", "reject"] = "approve",
) -> LocalReviewReceipt:
    """Record a review only when the displayed content matches current revision bytes."""

    target = _find_target(profile, target_type, target_id, target_revision)
    if target_type == "variant":
        variant = cast(ApprovedVariant, target)
        expected_content = variant.text
        evidence: list[EvidenceRecord] = []
        bindings: list[SupportBinding] = []
        facts = {(item.fact_id, item.revision): item for item in profile.facts}
        binding_index = {item.binding_id: item for item in profile.support_bindings}
        for reference in variant.fact_refs:
            fact = facts.get((reference.fact_id, reference.revision))
            if fact is None:
                raise ProvenanceValidationError(
                    [
                        ValidationIssue(
                            "dangling_variant_fact", f"{variant.variant_id} review has missing fact"
                        )
                    ]
                )
            fact_evidence, fact_bindings = _support_for_fact(profile, fact)
            evidence.extend(item for item in fact_evidence if item not in evidence)
            bindings.extend(item for item in fact_bindings if item not in bindings)
        for binding_id in variant.support_binding_refs:
            if binding_index.get(binding_id) is None:
                raise ProvenanceValidationError(
                    [
                        ValidationIssue(
                            "dangling_variant_binding",
                            f"{variant.variant_id} review has missing binding",
                        )
                    ]
                )
        support_digest = support_bundle_digest(evidence, bindings)
    elif target_type == "fact":
        fact = cast(Fact, target)
        expected_content = canonical_json(canonical_fact_payload(fact))
        evidence, bindings = _support_for_fact(profile, fact)
        support_digest = support_bundle_digest(evidence, bindings)
    else:
        evidence_record = cast(EvidenceRecord, target)
        expected_content = canonical_json(
            evidence_record.model_dump(mode="json", exclude={"approval"})
        )
        support_digest = evidence_digest(evidence_record)

    if displayed_content != expected_content:
        raise ProvenanceValidationError(
            [ValidationIssue("display_changed", f"{target_type} {target_id} changed after display")]
        )
    return LocalReviewReceipt(
        review_id=review_id,
        issuer="local_human",
        target_type=target_type,
        target_id=target_id,
        target_revision=target_revision,
        displayed_content=displayed_content,
        displayed_content_sha256=sha256_text(displayed_content),
        support_bundle_sha256=support_digest,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
    )


def fact_approval_from_review(review: LocalReviewReceipt) -> FactApproval:
    if review.target_type != "fact" or review.decision != "approve":
        raise ValueError("review is not an approved fact review")
    return FactApproval(
        fact_sha256=review.displayed_content_sha256,
        evidence_bundle_sha256=review.support_bundle_sha256,
        approved_at=review.reviewed_at,
        reviewer_id=review.reviewer_id,
    )


def evidence_approval_from_review(review: LocalReviewReceipt) -> EvidenceApproval:
    if review.target_type != "evidence" or review.decision != "approve":
        raise ValueError("review is not an approved evidence review")
    return EvidenceApproval(
        evidence_sha256=review.displayed_content_sha256,
        approved_at=review.reviewed_at,
        reviewer_id=review.reviewer_id,
    )


def variant_approval_from_review(review: LocalReviewReceipt) -> VariantApproval:
    if review.target_type != "variant" or review.decision != "approve":
        raise ValueError("review is not an approved variant review")
    return VariantApproval(
        variant_sha256=review.displayed_content_sha256,
        evidence_bundle_sha256=review.support_bundle_sha256,
        approved_at=review.reviewed_at,
        reviewer_id=review.reviewer_id,
    )
