"""Deterministic draft annotations, with no priority or skill normalization."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ..config import private_data_root, safe_private_path
from ..domain.job import JobRevision
from ..domain.requirement import (
    CandidateKind,
    LexicalSignal,
    RequirementCandidate,
    RequirementExtraction,
    SectionHeading,
    SectionKind,
    SignalKind,
    SourceSpan,
)
from ..ingestion.text import MAX_INPUT_BYTES, decode_source, load_job_revision, normalize_source
from ..verification.support import model_digest
from .spans import MAX_STRUCTURAL_SPANS, ExtractionError, segment_source, verify_span

MAX_SIGNALS = 4096
# Surface hints only. Unknown technologies remain visible as ambiguous prose.
# Do not turn this list into the canonical alias/skill dictionary (TASK-013).
TECHNOLOGIES = (
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Neo4j",
    "Apache Spark",
    "Spark",
    "Power BI",
    "DAX",
    "Docker",
    "Kubernetes",
    "Node.js",
    "React",
    "Next.js",
    "Flask",
    "FastAPI",
    "Django",
    "AWS",
    "Azure DevOps",
    "Azure",
    "Git",
    "Linux",
    "C++",
    "C#",
    ".NET",
    "CI/CD",
)
PATTERNS: tuple[tuple[SignalKind, re.Pattern[str]], ...] = (
    (
        "technology",
        re.compile(
            r"(?<!\w)(?:"
            + "|".join(re.escape(t) for t in sorted(TECHNOLOGIES, key=len, reverse=True))
            + r")(?!\w)",
            re.IGNORECASE,
        ),
    ),
    (
        "education",
        re.compile(
            r"(?<!\w)(?:bachelor(?:['’]s)?|master(?:['’]s)?|degree|studium|studienabschluss|"
            r"hochschulabschluss|abschluss|ph\.?d\.?|diplom|ausbildung)(?!\w)",
            re.IGNORECASE,
        ),
    ),
    (
        "language",
        re.compile(
            r"(?<!\w)(?:english|german|deutsch(?:kenntnisse)?|englisch(?:kenntnisse)?|"
            r"french|französisch|spanish|spanisch)(?!\w)",
            re.IGNORECASE,
        ),
    ),
    (
        "years",
        re.compile(
            r"(?<!\w)(?:[0-9]{1,3}(?:[.,][0-9]{1,2})?(?:\s*[-–]\s*[0-9]{1,3})?\+?|"
            r"one|two|three|four|five|several|many|ein|zwei|drei|vier|fünf|mehrere)"
            r"\s+(?:years?|jahre?n?|months?|monate?n?)(?!\w)",
            re.IGNORECASE,
        ),
    ),
)


def _identifier(prefix: str, job: JobRevision, span: SourceSpan) -> str:
    value = f"{job.record_digest}:{span.start}:{span.end}".encode()
    return prefix + "-" + hashlib.sha256(value).hexdigest()[:24]


def _verify_source(source: str, job: JobRevision) -> None:
    try:
        raw = source.encode("utf-8")
    except UnicodeError:
        raise ExtractionError("JD source is not valid UTF-8") from None
    if (
        not raw
        or len(raw) > MAX_INPUT_BYTES
        or len(raw) != job.raw_bytes
        or len(source) != job.raw_codepoints
        or hashlib.sha256(raw).hexdigest() != job.raw_sha256
        or hashlib.sha256(normalize_source(source).encode()).hexdigest() != job.normalized_sha256
        or model_digest(job, exclude={"record_digest"}) != job.record_digest
    ):
        raise ExtractionError("JD source or revision identity does not match the verified record")


def _signals(source: str, span: SourceSpan) -> list[LexicalSignal]:
    result: list[LexicalSignal] = []
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(span.quote):
            if len(result) >= MAX_SIGNALS:
                raise ExtractionError("JD analysis exceeds 4096 lexical signals; review the source")
            start, end = span.start + match.start(), span.start + match.end()
            result.append(
                LexicalSignal(
                    kind=kind, span=SourceSpan(start=start, end=end, quote=source[start:end])
                )
            )
    return sorted(result, key=lambda signal: (signal.span.start, signal.span.end, signal.kind))


def _kind(section: SectionKind, signals: list[LexicalSignal]) -> CandidateKind:
    if section == "responsibilities":
        return "responsibility"
    if section in {"benefits", "context"}:
        return "context"
    kinds = {signal.kind for signal in signals}
    if len(kinds) != 1:
        return "ambiguous"
    if "technology" in kinds:
        return "technology"
    if "education" in kinds:
        return "education"
    if "language" in kinds:
        return "language"
    return "experience"


def validate_extraction(extraction: RequirementExtraction, source: str, job: JobRevision) -> None:
    """Validate structural/source identity; draft semantics still require review."""
    try:
        checked = RequirementExtraction.model_validate_json(extraction.model_dump_json())
        checked_job = JobRevision.model_validate_json(job.model_dump_json())
    except ValueError:
        raise ExtractionError("extraction or job record structure is invalid") from None
    _verify_source(source, checked_job)
    if (
        checked.job_id,
        checked.job_revision,
        checked.job_record_digest,
        checked.raw_sha256,
        checked.locale,
    ) != (job.job_id, job.revision, job.record_digest, job.raw_sha256, job.locale) or model_digest(
        checked, exclude={"analysis_digest"}
    ) != checked.analysis_digest:
        raise ExtractionError("extraction revision or analysis checksum does not match")
    if len(checked.sections) + len(checked.candidates) > MAX_STRUCTURAL_SPANS:
        raise ExtractionError("JD analysis exceeds 2048 structural spans; review the source")
    previous_end = 0
    for heading in checked.sections:
        verify_span(source, heading.span)
        if heading.span.start < previous_end or heading.heading_id != _identifier(
            "section", job, heading.span
        ):
            raise ExtractionError("section order or identity is invalid")
        previous_end = heading.span.end
    previous_end, total_signals = 0, 0
    for candidate in checked.candidates:
        verify_span(source, candidate.span)
        prior = [h for h in checked.sections if h.span.end <= candidate.span.start]
        expected_section = prior[-1].heading_id if prior else None
        if (
            candidate.span.start < previous_end
            or candidate.candidate_id != _identifier("req", job, candidate.span)
            or candidate.section_id != expected_section
            or any(
                h.span.start < candidate.span.end and h.span.end > candidate.span.start
                for h in checked.sections
            )
        ):
            raise ExtractionError("candidate order, identity or section placement is invalid")
        previous_end = candidate.span.end
        seen = set()
        for signal in candidate.signals:
            verify_span(source, signal.span)
            key = (signal.kind, signal.span.start, signal.span.end)
            if (
                signal.span.start < candidate.span.start
                or signal.span.end > candidate.span.end
                or key in seen
            ):
                raise ExtractionError("lexical signal is outside its source clause or duplicated")
            seen.add(key)
        total_signals += len(candidate.signals)
        if total_signals > MAX_SIGNALS:
            raise ExtractionError("JD analysis exceeds 4096 lexical signals; review the source")


def extract_requirements(source: str, *, job: JobRevision) -> RequirementExtraction:
    _verify_source(source, job)
    sections: list[SectionHeading] = []
    candidates: list[RequirementCandidate] = []
    active: SectionHeading | None = None
    total_signals = 0
    for segment in segment_source(source):
        if segment.heading:
            active = SectionHeading(
                heading_id=_identifier("section", job, segment.span),
                kind=segment.section_kind,
                span=segment.span,
            )
            sections.append(active)
        else:
            signals = _signals(source, segment.span)
            total_signals += len(signals)
            if total_signals > MAX_SIGNALS:
                raise ExtractionError("JD analysis exceeds 4096 lexical signals; review the source")
            candidates.append(
                RequirementCandidate(
                    candidate_id=_identifier("req", job, segment.span),
                    section_id=active.heading_id if active else None,
                    kind=_kind(active.kind if active else "unknown", signals),
                    span=segment.span,
                    signals=signals,
                )
            )
    result = RequirementExtraction(
        job_id=job.job_id,
        job_revision=job.revision,
        job_record_digest=job.record_digest,
        raw_sha256=job.raw_sha256,
        locale=job.locale,
        sections=sections,
        candidates=candidates,
        analysis_digest="0" * 64,
    )
    result = result.model_copy(
        update={"analysis_digest": model_digest(result, exclude={"analysis_digest"})}
    )
    validate_extraction(result, source, job)
    return result


def load_saved_source(
    job_id: str, *, revision: int | None = None, data_root: str | Path | None = None
) -> tuple[str, JobRevision]:
    """Load a verified saved revision's raw quote source (re-checked by the caller)."""
    root = private_data_root(data_root)
    saved = load_job_revision(job_id, revision=revision, data_root=root)
    path = safe_private_path((saved.path / "job_description.raw.txt").relative_to(root), root)
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    return decode_source(raw), saved.record


def extract_saved_job(
    job_id: str, *, revision: int | None = None, data_root: str | Path | None = None
) -> RequirementExtraction:
    source, job = load_saved_source(job_id, revision=revision, data_root=data_root)
    return extract_requirements(source, job=job)
