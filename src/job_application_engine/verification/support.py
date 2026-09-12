"""Hash and immutable-support checks used by the evidence graph validator."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..domain.evidence import EvidenceRecord, SupportBinding
from ..domain.fact import Fact

EvidenceKey = tuple[str, int]


class SupportIntegrityError(ValueError):
    """Raised when a required support capture is absent or has changed."""


def canonical_json(value: BaseModel | Mapping[str, Any]) -> str:
    """Serialize a model deterministically for revision-bound digest checks."""

    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def model_digest(model: BaseModel, *, exclude: set[str] | None = None) -> str:
    payload = model.model_dump(mode="json", exclude=exclude or set())
    return sha256_text(canonical_json(payload))


def fact_digest(fact: Fact) -> str:
    return model_digest(fact, exclude={"approval"})


def evidence_digest(evidence: EvidenceRecord) -> str:
    return model_digest(evidence, exclude={"approval"})


def binding_digest(binding: SupportBinding) -> str:
    return model_digest(binding)


def support_bundle_digest(
    evidence: Iterable[EvidenceRecord], bindings: Iterable[SupportBinding]
) -> str:
    payload = {
        "evidence": [
            json.loads(canonical_json(item.model_dump(mode="json", exclude={"approval"})))
            for item in evidence
        ],
        "bindings": [json.loads(canonical_json(item)) for item in bindings],
    }
    return sha256_text(canonical_json(payload))


def _capture_bytes(capture: bytes | bytearray | Path) -> bytes:
    if isinstance(capture, Path):
        try:
            return capture.read_bytes()
        except OSError as error:
            raise SupportIntegrityError(f"support capture cannot be read: {capture}") from error
    return bytes(capture)


def verify_support_captures(
    evidence: Iterable[EvidenceRecord],
    captures: Mapping[EvidenceKey, bytes | bytearray | Path] | None = None,
    *,
    required: set[EvidenceKey] | None = None,
) -> None:
    """Verify supplied bytes and require captures for approved evidence.

    A locator is never read as evidence. The caller supplies an immutable local
    capture explicitly, and its bytes must match the recorded support hash.
    """

    capture_map = captures or {}
    required_keys = required or {
        (item.evidence_id, item.revision) for item in evidence if item.status == "approved"
    }
    for item in evidence:
        key = (item.evidence_id, item.revision)
        capture = capture_map.get(key)
        if capture is None:
            if key in required_keys:
                raise SupportIntegrityError(
                    f"missing support capture for {key[0]} revision {key[1]}"
                )
            continue
        digest = hashlib.sha256(_capture_bytes(capture)).hexdigest()
        if digest != item.support_capture_sha256:
            raise SupportIntegrityError(
                f"support capture hash mismatch for {key[0]} revision {key[1]}"
            )
