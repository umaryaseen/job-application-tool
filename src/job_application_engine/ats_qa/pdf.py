"""Measure actual local PDF bytes; never infer PDF quality from template settings."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .expected import ExpectedDocument
from .report import QACheck, QAReport, QAStatus, VisualReview, overall_status
from .text import normalize_extracted_text

MAX_PDF_BYTES = 2_000_000
TIMEOUT_SECONDS = 30
A4 = (595.276, 841.89)
TOLERANCE_PT = 1.0
NETWORK_DENY = "(version 1) (allow default) (deny network*)"


@dataclass(frozen=True)
class Result:
    status: QAStatus
    output: str = ""
    diagnostic: str = ""


def _run(command: list[str]) -> Result:
    sandbox = shutil.which("sandbox-exec")
    if sandbox is None:
        return Result("not_checked", diagnostic="required network isolation unavailable")
    try:
        completed = subprocess.run(
            [sandbox, "-p", NETWORK_DENY, *command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Result("fail", diagnostic="measurement subprocess timed out")
    except (OSError, UnicodeError):
        return Result("fail", diagnostic="measurement subprocess could not run")
    if completed.returncode:
        return Result("fail", diagnostic=f"measurement exit {completed.returncode}")
    if len(completed.stdout) > 20_000_000:
        return Result("fail", diagnostic="measurement output exceeds QA limit")
    return Result("pass", completed.stdout)


def _poppler(name: str, args: list[str]) -> tuple[Result, str | None]:
    executable = shutil.which(name)
    if executable is None:
        return Result("not_checked", diagnostic=f"{name} unavailable"), None
    # Poppler writes its version to stderr, separately from measured PDF text.
    sandbox = shutil.which("sandbox-exec")
    if sandbox is None:
        return Result("not_checked", diagnostic="required network isolation unavailable"), None
    try:
        info = subprocess.run(
            [sandbox, "-p", NETWORK_DENY, executable, "-v"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        lines = (info.stdout or info.stderr).splitlines()
        tool_version = lines[0][:100] if info.returncode == 0 and lines else None
    except (OSError, subprocess.TimeoutExpired):
        tool_version = None
    if tool_version is None:
        return Result("fail", diagnostic=f"{name} version could not be verified"), None
    return _run([executable, *args]), tool_version


def _fingerprint(text: str) -> dict[str, object]:
    return {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "characters": len(text),
        "words": len(text.split()),
    }


def _coverage(found: int, total: int) -> dict[str, int | float | None]:
    return {"found": found, "total": total, "fraction": found / total if total else None}


def _text_checks(text: str, expected: ExpectedDocument) -> dict[str, tuple[bool, Any, Any]]:
    actual = normalize_extracted_text(text)
    wanted = normalize_extracted_text(expected.ordered_text)
    positions = [actual.find(section.label) for section in expected.sections]
    headings_ok = all(p >= 0 for p in positions) and positions == sorted(set(positions))
    entry_total = sum(len(section.entries) for section in expected.sections)
    found_entries = 0
    field_total = field_found = 0
    for index, section in enumerate(expected.sections):
        end = positions[index + 1] if index + 1 < len(positions) else len(actual)
        block = actual[positions[index] + len(section.label) : end] if headings_ok else ""
        cursor = 0
        for entry in section.entries:
            exact = normalize_extracted_text(entry.text)
            position = block.find(exact, cursor)
            # Full-entry span, with word boundaries: a number elsewhere cannot
            # satisfy a field missing from this entry.
            scoped = position >= 0
            if scoped:
                found_entries += 1
                cursor = position + len(exact)
            field_total += len(entry.fields)
            if scoped:
                field_found += len(entry.fields)
    result: dict[str, tuple[bool, Any, Any]] = {
        "complete_text": (
            bool(actual) and actual == wanted,
            _fingerprint(actual),
            _fingerprint(wanted),
        ),
        "standard_headings": (
            headings_ok,
            positions,
            [section.label for section in expected.sections],
        ),
        "entry_claim_sequence": (
            found_entries == entry_total,
            _coverage(found_entries, entry_total),
            "every complete entry in section/claim order",
        ),
        "critical_fields": (
            field_found == field_total,
            _coverage(field_found, field_total),
            "all mapped fields within complete entry spans",
        ),
    }
    for check_id, tokens in (
        ("unicode", expected.unicode_tokens),
        ("quantitative_punctuation", expected.quantitative_tokens),
    ):
        found = sum(
            actual.count(normalize_extracted_text(token))
            == wanted.count(normalize_extracted_text(token))
            for token in tokens
        )
        result[check_id] = (
            found == len(tokens),
            _coverage(found, len(tokens)),
            "exact token multiplicity in normalized content",
        )
    return result


def _geometry(xml: str) -> dict[str, object]:
    root = ET.fromstring(xml)
    words = outside = 0
    per_page: list[dict[str, object]] = []
    for page in root.iter():
        if page.tag.rsplit("}", 1)[-1] != "page":
            continue
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        bounds: list[tuple[float, float, float, float]] = []
        for word in page.iter():
            if word.tag.rsplit("}", 1)[-1] != "word":
                continue
            x0, y0, x1, y1 = (float(word.attrib[key]) for key in ("xMin", "yMin", "xMax", "yMax"))
            words += 1
            outside += not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height)
            bounds.append((x0, y0, x1, y1))
        per_page.append(
            {
                "width_pt": width,
                "height_pt": height,
                "words": len(bounds),
                "text_bounds_pt": [
                    min(b[0] for b in bounds),
                    min(b[1] for b in bounds),
                    max(b[2] for b in bounds),
                    max(b[3] for b in bounds),
                ]
                if bounds
                else None,
            }
        )
    return {"word_count": words, "out_of_page_words": outside, "pages": per_page}


def run_pdf_qa(
    pdf_path: str | Path,
    expected: ExpectedDocument,
    *,
    report_path: str | Path,
    raster_dir: str | Path,
) -> QAReport:
    """Measure a local generated PDF against a separately curated oracle.

    Caller must store private artifacts/reports outside Git. This QA API does
    not approve provenance, career facts, or final application artifacts.
    Existing outputs are refused. A temporary byte copy pins all tools to the
    same content; this is not TASK-008 snapshot/export functionality.
    """
    pdf, output, rasters = Path(pdf_path), Path(report_path), Path(raster_dir)
    if output.exists() or rasters.exists():
        raise ValueError("QA report and raster destination must be new")
    if pdf.stat().st_size > 10_000_000:
        raise ValueError("PDF exceeds bounded QA input size (10 MB)")
    data = pdf.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    rasters.mkdir(parents=True, mode=0o700)
    checks: list[QACheck] = []

    def add(
        check_id: str,
        status: QAStatus,
        measured: Any,
        wanted: Any,
        tool: str,
        tool_version: str | None,
        diagnostic: str = "",
        *,
        mandatory: bool = True,
    ) -> None:
        checks.append(
            QACheck(
                check_id=check_id,
                status=status,
                measured=measured,
                expected=wanted,
                tool=tool,
                tool_version=tool_version,
                artifact_sha256=digest,
                diagnostics=[diagnostic] if diagnostic else [],
                mandatory=mandatory,
            )
        )

    add(
        "file_size",
        "pass" if 0 < len(data) < MAX_PDF_BYTES else "fail",
        len(data),
        {"minimum_exclusive": 0, "maximum_exclusive": MAX_PDF_BYTES},
        "filesystem",
        sys.version.split()[0],
    )
    with tempfile.TemporaryDirectory(prefix=".qa-", dir=output.parent) as temporary:
        frozen = Path(temporary) / "input.pdf"
        frozen.write_bytes(data)
        poppler, poppler_version = _poppler("pdftotext", ["-layout", str(frozen), "-"])
        try:
            pypdf_version = version("pypdf")
            worker = _run(
                [sys.executable, "-m", "job_application_engine.ats_qa._worker", str(frozen)]
            )
        except PackageNotFoundError:
            pypdf_version = None
            worker = Result("not_checked", diagnostic="pypdf unavailable")
        inspected: dict[str, Any] = {}
        if worker.status == "pass":
            try:
                inspected = json.loads(worker.output)
                if not isinstance(inspected.get("text"), str) or not inspected.get("pages"):
                    raise ValueError("incomplete result")
            except (ValueError, AttributeError):
                worker = Result("fail", diagnostic="invalid pypdf worker result")
        recovered = Result(worker.status, inspected.get("text", ""), worker.diagnostic)
        for name, result, tool_version in (
            ("poppler", poppler, poppler_version),
            ("pypdf", recovered, pypdf_version),
        ):
            for check_id, (passed, measured, wanted) in _text_checks(
                result.output, expected
            ).items():
                status: QAStatus = (
                    ("pass" if passed else "fail") if result.status == "pass" else result.status
                )
                add(
                    f"{check_id}_{name}",
                    status,
                    measured if result.status == "pass" else None,
                    wanted,
                    name,
                    tool_version,
                    result.diagnostic,
                )

        pages = inspected.get("pages", [])
        add(
            "page_count",
            "pass"
            if len(pages) == expected.expected_pages
            else "fail"
            if worker.status == "pass"
            else worker.status,
            len(pages) if pages else None,
            expected.expected_pages,
            "pypdf",
            pypdf_version,
            worker.diagnostic,
        )
        a4 = bool(pages) and all(
            abs(page["media"][2] - page["media"][0] - A4[0]) <= TOLERANCE_PT
            and abs(page["media"][3] - page["media"][1] - A4[1]) <= TOLERANCE_PT
            and page["crop"] == page["media"]
            and page["rotation"] == 0
            and page["user_unit"] == 1
            for page in pages
        )
        add(
            "a4_dimensions",
            ("pass" if a4 else "fail") if worker.status == "pass" else worker.status,
            pages or None,
            {
                "a4_pt": A4,
                "tolerance_pt": TOLERANCE_PT,
                "crop_equals_media": True,
                "rotation": 0,
                "user_unit": 1,
            },
            "pypdf",
            pypdf_version,
            worker.diagnostic,
        )
        hazards = inspected.get("hazards", [])
        add(
            "visibility_operators",
            ("fail" if hazards else "pass") if worker.status == "pass" else worker.status,
            hazards if worker.status == "pass" else None,
            "no nonpainting/clipping text, explicit clips, transparency/masks or unanalyzed forms",
            "pypdf",
            pypdf_version,
            worker.diagnostic,
        )

        bbox, bbox_version = _poppler("pdftotext", ["-cropbox", "-bbox-layout", str(frozen), "-"])
        geometry: dict[str, object] | None = None
        if bbox.status == "pass":
            try:
                geometry = _geometry(bbox.output)
            except (ET.ParseError, KeyError, ValueError):
                bbox = Result("fail", diagnostic="invalid bbox result")
        geometry_ok = (
            geometry is not None
            and bool(geometry["word_count"])
            and geometry["out_of_page_words"] == 0
        )
        add(
            "text_geometry",
            ("pass" if geometry_ok else "fail") if bbox.status == "pass" else bbox.status,
            geometry,
            "nonempty text boxes wholly inside measured crop page",
            "pdftotext -bbox-layout",
            bbox_version,
            bbox.diagnostic,
        )
        raster, raster_version = _poppler(
            "pdftoppm",
            ["-png", "-r", "110", "-f", "1", "-l", "10", str(frozen), str(rasters / "page")],
        )
        images = sorted(rasters.glob("page-*.png"))
        add(
            "raster_generation",
            ("pass" if len(images) == expected.expected_pages else "fail")
            if raster.status == "pass"
            else raster.status,
            [
                {"name": image.name, "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}
                for image in images
            ],
            {"pages": expected.expected_pages, "dpi": 110},
            "pdftoppm",
            raster_version,
            raster.diagnostic,
        )
    add(
        "input_unchanged",
        "pass" if pdf.read_bytes() == data else "fail",
        digest,
        digest,
        "sha256",
        "stdlib",
    )
    visual = VisualReview(
        status="not_checked",
        artifact_sha256=digest,
        notes=(
            "Raster generation is not visual inspection. Record a named "
            "observation of every page against this exact PDF hash."
        ),
    )
    report = QAReport(
        report_version="1.0",
        artifact_sha256=digest,
        artifact_path=str(pdf),
        overall_status=overall_status(checks, visual),
        checks=checks,
        visual_review=visual,
    )
    report.write_json(str(output))
    return report
