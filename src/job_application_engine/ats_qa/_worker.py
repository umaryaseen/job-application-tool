"""Bounded pypdf inspection in a network-denied subprocess (never execute PDF actions)."""

from __future__ import annotations

import json
import re
import sys
from importlib.metadata import version

from pypdf import PdfReader


def inspect_pdf(path: str) -> dict[str, object]:
    reader = PdfReader(path, strict=True)
    if reader.is_encrypted or not 1 <= len(reader.pages) <= 10:
        raise ValueError("unsupported encryption or page count")
    text: list[str] = []
    dimensions: list[dict[str, object]] = []
    hazards: list[dict[str, object]] = []
    for index, page in enumerate(reader.pages):
        contents = page.get_contents()
        if contents and len(contents.get_data()) > 10_000_000:
            raise ValueError("decoded content stream exceeds QA limit")
        text.append(page.extract_text() or "")
        dimensions.append(
            {
                "media": [float(v) for v in page.mediabox],
                "crop": [float(v) for v in page.cropbox],
                "rotation": page.rotation,
                "user_unit": page.user_unit,
            }
        )
        # Conservative flags: any non-painting text mode or text clip operator,
        # even if subsequently reset; no claim of full graphics-state simulation.
        if contents is not None:
            raw_contents = contents.get_data()
            if re.search(rb"(?:^|\s)[3-7]\s+Tr(?:\s|$)", raw_contents):
                hazards.append({"page": index + 1, "reason": "invisible_or_clipping_text_mode"})
            if re.search(rb"(?:^|\s)W(?:\*?)?(?:\s|$)", raw_contents):
                hazards.append({"page": index + 1, "reason": "explicit_clip_path"})
            for _, (operands, operator) in enumerate(contents.operations):
                reason = None
                if operator == b"Tr" and int(operands[0]) in (3, 4, 5, 6, 7):
                    reason = "invisible_or_clipping_text_mode"
                if operator in (b"W", b"W*"):
                    reason = "explicit_clip_path"
                if reason:
                    hazards.append({"page": index + 1, "reason": reason})
        resources = page.get("/Resources", {})
        resources = resources.get_object()
        for state in (
            resources.get("/ExtGState", {}).get_object().values()
            if "/ExtGState" in resources
            else []
        ):
            state = state.get_object()
            if any(float(state.get(key, 1)) < 1 for key in ("/ca", "/CA")) or "/SMask" in state:
                hazards.append({"page": index + 1, "reason": "transparency_or_soft_mask"})
        for obj in (
            resources.get("/XObject", {}).get_object().values() if "/XObject" in resources else []
        ):
            if obj.get_object().get("/Subtype") == "/Form":
                hazards.append({"page": index + 1, "reason": "form_visibility_not_analyzed"})
    recovered = "\n".join(text)
    if len(recovered) > 1_000_000:
        raise ValueError("recovered text exceeds QA limit")
    return {
        "text": recovered,
        "pages": dimensions,
        "hazards": hazards[:100],
        "version": version("pypdf"),
    }


if __name__ == "__main__":
    try:
        result = inspect_pdf(sys.argv[1])
    except Exception:
        # PDF payloads and parser error messages can contain private strings.
        raise SystemExit(2) from None
    print(json.dumps(result, ensure_ascii=False))
