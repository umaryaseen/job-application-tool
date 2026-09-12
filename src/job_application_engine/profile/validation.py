"""Deterministic support-graph and approval validation.

This module proves that local records, revisions, hashes, scopes, and review
receipts are internally consistent. It does not decide whether arbitrary prose
is true in the real world.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from ..domain.evidence import (
    DocumentSource,
    EvidenceRecord,
    ImportSource,
    RepositorySource,
    SupportBinding,
)
from ..domain.fact import Fact
from ..domain.profile import ProfileRevision
from ..verification.support import (
    EvidenceKey,
    SupportIntegrityError,
    evidence_digest,
    fact_digest,
    sha256_text,
    support_bundle_digest,
    verify_support_captures,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


class ProvenanceValidationError(ValueError):
    """Raised when a profile cannot be trusted for supported publication."""

    def __init__(self, issues: Sequence[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("; ".join(f"{item.code}: {item.message}" for item in self.issues))


def _key(record: Any) -> tuple[str, int]:
    identifier = getattr(record, "fact_id", None)
    if identifier is None:
        identifier = getattr(record, "evidence_id", None)
    if identifier is None:
        identifier = record.variant_id
    return identifier, record.revision


def _review_matches(
    reviews: Iterable[object],
    *,
    target_type: str,
    target_id: str,
    target_revision: int,
    content_sha256: str,
    support_sha256: str,
    reviewer_id: str,
    approved_at: object,
) -> bool:
    for review in reviews:
        if (
            getattr(review, "issuer", None) == "local_human"
            and getattr(review, "decision", None) == "approve"
            and getattr(review, "target_type", None) == target_type
            and getattr(review, "target_id", None) == target_id
            and getattr(review, "target_revision", None) == target_revision
            and getattr(review, "displayed_content_sha256", None) == content_sha256
            and getattr(review, "support_bundle_sha256", None) == support_sha256
            and getattr(review, "reviewer_id", None) == reviewer_id
            and getattr(review, "reviewed_at", None) == approved_at
        ):
            return True
    return False


def _source_issues(evidence: EvidenceRecord, issues: list[ValidationIssue]) -> None:
    if (
        isinstance(evidence.source, ImportSource)
        and evidence.source.source_role == "generated_output"
    ):
        issues.append(
            ValidationIssue("generated_source", f"{evidence.evidence_id} is generated output")
        )
    if evidence.status != "approved":
        return
    if isinstance(evidence.source, DocumentSource) and evidence.source.document_sha256 is None:
        issues.append(
            ValidationIssue("unpinned_document", f"{evidence.evidence_id} has no source-file hash")
        )
    if isinstance(evidence.source, RepositorySource) and evidence.source.revision is None:
        issues.append(
            ValidationIssue("unpinned_repository", f"{evidence.evidence_id} has no pinned revision")
        )
    if isinstance(evidence.source, ImportSource) and evidence.source.source_sha256 is None:
        issues.append(
            ValidationIssue("unpinned_import", f"{evidence.evidence_id} has no source hash")
        )


def _index(records: Iterable[Any], label: str, issues: list[ValidationIssue]) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for record in records:
        key = _key(record) if label != "binding" else record.binding_id
        if key in result:
            issues.append(ValidationIssue("duplicate_revision", f"duplicate {label} {key}"))
        result[key] = record
    return result


def _check_binding_cycles(
    bindings: Mapping[str, SupportBinding], issues: list[ValidationIssue]
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(binding_id: str) -> None:
        if binding_id in visiting:
            issues.append(
                ValidationIssue("cyclic_binding", f"binding dependency cycle at {binding_id}")
            )
            return
        if binding_id in visited:
            return
        binding = bindings.get(binding_id)
        if binding is None:
            issues.append(ValidationIssue("dangling_binding", f"missing binding {binding_id}"))
            return
        visiting.add(binding_id)
        for dependency in binding.depends_on_binding_refs:
            visit(dependency)
        visiting.remove(binding_id)
        visited.add(binding_id)

    for binding_id in bindings:
        visit(binding_id)


def validate_profile(
    profile: ProfileRevision,
    *,
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path] | None = None,
    reviews: Sequence[object] = (),
) -> ProfileRevision:
    """Validate all revision-bound support relationships and local approvals."""

    issues: list[ValidationIssue] = []
    facts = _index(profile.facts, "fact", issues)
    evidence = _index(profile.evidence, "evidence", issues)
    bindings = _index(profile.support_bindings, "binding", issues)
    typed_bindings: dict[str, SupportBinding] = {str(key): value for key, value in bindings.items()}
    _check_binding_cycles(typed_bindings, issues)

    for evidence_record in profile.evidence:
        _source_issues(evidence_record, issues)
        if evidence_record.status == "approved" and evidence_record.approval is None:
            issues.append(
                ValidationIssue(
                    "missing_evidence_approval",
                    f"{evidence_record.evidence_id} is approved without review",
                )
            )
        elif evidence_record.status == "approved" and evidence_record.approval is not None:
            digest = evidence_digest(evidence_record)
            if not _review_matches(
                reviews,
                target_type="evidence",
                target_id=evidence_record.evidence_id,
                target_revision=evidence_record.revision,
                content_sha256=digest,
                support_sha256=digest,
                reviewer_id=evidence_record.approval.reviewer_id,
                approved_at=evidence_record.approval.approved_at,
            ):
                issues.append(
                    ValidationIssue(
                        "unreviewed_evidence",
                        f"{evidence_record.evidence_id} lacks local human review",
                    )
                )

    for binding in profile.support_bindings:
        fact: Fact | None = cast(Fact | None, facts.get((binding.fact_id, binding.fact_revision)))
        item: EvidenceRecord | None = cast(
            EvidenceRecord | None, evidence.get((binding.evidence_id, binding.evidence_revision))
        )
        if fact is None:
            issues.append(
                ValidationIssue(
                    "dangling_binding_fact",
                    f"{binding.binding_id} references missing fact revision",
                )
            )
        if item is None:
            issues.append(
                ValidationIssue(
                    "dangling_binding_evidence",
                    f"{binding.binding_id} references missing evidence revision",
                )
            )
        if fact is not None and binding.fact_sha256 != fact_digest(fact):
            issues.append(
                ValidationIssue("stale_fact_binding", f"{binding.binding_id} fact digest is stale")
            )
        if item is not None:
            if item.status == "revoked":
                issues.append(
                    ValidationIssue(
                        "revoked_evidence", f"{binding.binding_id} uses revoked evidence"
                    )
                )
            if binding.evidence_sha256 != evidence_digest(item):
                issues.append(
                    ValidationIssue(
                        "stale_evidence_binding", f"{binding.binding_id} evidence digest is stale"
                    )
                )

    def evidence_for_fact(fact: Fact) -> tuple[list[EvidenceRecord], list[SupportBinding]]:
        resolved_evidence: list[EvidenceRecord] = []
        resolved_bindings: list[SupportBinding] = []
        for reference in fact.evidence_refs:
            item = evidence.get((reference.evidence_id, reference.revision))
            if item is None:
                issues.append(
                    ValidationIssue(
                        "dangling_evidence", f"{fact.fact_id} references missing evidence revision"
                    )
                )
            else:
                if item.status == "revoked":
                    issues.append(
                        ValidationIssue(
                            "revoked_evidence", f"{fact.fact_id} references revoked evidence"
                        )
                    )
                resolved_evidence.append(item)
        for binding_id in fact.support_binding_refs:
            variant_binding = cast(SupportBinding | None, bindings.get(binding_id))
            if variant_binding is None:
                issues.append(
                    ValidationIssue(
                        "dangling_binding",
                        f"{fact.fact_id} references missing binding {binding_id}",
                    )
                )
                continue
            if (variant_binding.fact_id, variant_binding.fact_revision) != (
                fact.fact_id,
                fact.revision,
            ):
                issues.append(
                    ValidationIssue(
                        "wrong_fact_scope",
                        f"{variant_binding.binding_id} is bound to another fact",
                    )
                )
            resolved_bindings.append(variant_binding)
        return resolved_evidence, resolved_bindings

    for fact in profile.facts:
        fact_evidence, fact_bindings = evidence_for_fact(fact)
        if fact.status != "approved":
            continue
        if not fact_bindings:
            issues.append(
                ValidationIssue("missing_support_binding", f"{fact.fact_id} has no support binding")
            )
        if fact.approval is None:
            issues.append(
                ValidationIssue(
                    "missing_fact_approval", f"{fact.fact_id} is approved without review"
                )
            )
            continue
        bundle = support_bundle_digest(fact_evidence, fact_bindings)
        if (
            fact.approval.fact_sha256 != fact_digest(fact)
            or fact.approval.evidence_bundle_sha256 != bundle
        ):
            issues.append(
                ValidationIssue("stale_fact_approval", f"{fact.fact_id} approval is stale")
            )
        if not _review_matches(
            reviews,
            target_type="fact",
            target_id=fact.fact_id,
            target_revision=fact.revision,
            content_sha256=fact_digest(fact),
            support_sha256=bundle,
            reviewer_id=fact.approval.reviewer_id,
            approved_at=fact.approval.approved_at,
        ):
            issues.append(
                ValidationIssue("unreviewed_fact", f"{fact.fact_id} lacks local human review")
            )

    for variant in profile.variants:
        resolved_facts: list[Fact] = []
        variant_bindings: list[SupportBinding] = []
        variant_evidence: list[EvidenceRecord] = []
        for reference in variant.fact_refs:
            fact = facts.get((reference.fact_id, reference.revision))
            if fact is None:
                issues.append(
                    ValidationIssue(
                        "dangling_variant_fact",
                        f"{variant.variant_id} references missing fact revision",
                    )
                )
                continue
            if fact.subject_id != variant.subject_scope:
                issues.append(
                    ValidationIssue("variant_scope", f"{variant.variant_id} crosses subject scope")
                )
            resolved_facts.append(fact)
            fact_evidence, fact_bindings = evidence_for_fact(fact)
            for evidence_item in fact_evidence:
                if evidence_item not in variant_evidence:
                    variant_evidence.append(evidence_item)
            for fact_binding in fact_bindings:
                if fact_binding not in variant_bindings:
                    variant_bindings.append(fact_binding)
        for binding_id in variant.support_binding_refs:
            variant_binding = cast(SupportBinding | None, bindings.get(binding_id))
            if variant_binding is None:
                issues.append(
                    ValidationIssue(
                        "dangling_variant_binding",
                        f"{variant.variant_id} references missing binding",
                    )
                )
            elif variant_binding not in variant_bindings:
                issues.append(
                    ValidationIssue(
                        "variant_support_scope",
                        f"{variant.variant_id} binding is outside its facts",
                    )
                )
        if variant.status != "approved":
            continue
        if variant.approval is None:
            issues.append(
                ValidationIssue(
                    "missing_variant_approval", f"{variant.variant_id} is approved without review"
                )
            )
            continue
        bundle = support_bundle_digest(variant_evidence, variant_bindings)
        displayed_digest = sha256_text(variant.text)
        if (
            variant.approval.variant_sha256 != displayed_digest
            or variant.approval.evidence_bundle_sha256 != bundle
        ):
            issues.append(
                ValidationIssue("stale_variant_approval", f"{variant.variant_id} approval is stale")
            )
        if not _review_matches(
            reviews,
            target_type="variant",
            target_id=variant.variant_id,
            target_revision=variant.revision,
            content_sha256=displayed_digest,
            support_sha256=bundle,
            reviewer_id=variant.approval.reviewer_id,
            approved_at=variant.approval.approved_at,
        ):
            issues.append(
                ValidationIssue(
                    "unreviewed_variant", f"{variant.variant_id} lacks local human review"
                )
            )

    try:
        verify_support_captures(profile.evidence, support_captures)
    except SupportIntegrityError as error:
        issues.append(ValidationIssue("support_capture", str(error)))

    if issues:
        raise ProvenanceValidationError(issues)
    return profile
