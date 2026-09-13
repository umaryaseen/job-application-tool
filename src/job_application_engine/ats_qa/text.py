"""Reviewed TASK-005 normalization, shared by TASK-007 QA checks."""

import re
import unicodedata


def normalize_extracted_text(value: str) -> str:
    """Normalize only Unicode/layout artifacts introduced by PDF extraction.

    NFC preserves Unicode identity. A soft hyphen is a line-break marker in
    word text; between digits it replaces a date hyphen in pypdf output. PDF
    extractors can also split the two slashes in an HTTPS scheme across a line.
    All other whitespace is collapsed to one space so visual line wrapping does
    not change content. Punctuation, numbers, units, qualifiers and negation
    remain otherwise byte-for-byte meaningful after UTF-8 normalization.
    """

    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"(https?:)/[ \t]*/[ \t]*\r?\n[ \t]*", r"\1//", value)
    value = re.sub(r"(?<=\d)\u00ad(?=\d)", "-", value)
    value = re.sub(r"[ \t]*\u00ad[ \t]*\r?\n[ \t]*", "", value)
    return re.sub(r"\s+", " ", value).strip()
