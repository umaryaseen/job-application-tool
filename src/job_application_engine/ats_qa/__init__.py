"""Deterministic PDF extraction and layout QA."""

from .expected import ExpectedDocument
from .pdf import run_pdf_qa
from .report import QAReport

__all__ = ["ExpectedDocument", "QAReport", "run_pdf_qa"]
