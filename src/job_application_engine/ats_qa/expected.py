"""Independent QA expectations, not a provenance or artifact approval record."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..domain.common import StrictModel
from .text import normalize_extracted_text


class ExpectedEntry(StrictModel):
    entry_id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=4000)
    fields: dict[str, str] = Field(default_factory=dict, max_length=30)

    @model_validator(mode="after")
    def fields_belong_to_entry(self) -> ExpectedEntry:
        for key, value in self.fields.items():
            if (
                not key
                or not value
                or normalize_extracted_text(value) not in normalize_extracted_text(self.text)
            ):
                raise ValueError("critical field must occur in its complete expected entry")
        return self


class ExpectedSection(StrictModel):
    # TASK-004 baseline headings; DE localization remains TASK-025.
    label: Literal[
        "Contact",
        "Professional Summary",
        "Professional Experience",
        "Selected Projects",
        "Education",
        "Skills",
        "Languages",
    ]
    heading_visible: bool = True
    entries: list[ExpectedEntry] = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def only_contact_heading_may_be_hidden(self) -> ExpectedSection:
        if not self.heading_visible and self.label != "Contact":
            raise ValueError("only the Contact heading may be hidden")
        return self


class ExpectedDocument(StrictModel):
    # Independently curated required identity; this is checked even when a
    # malformed plan omits its own identity claim from the expected entries.
    required_identity: str = Field(min_length=1, max_length=300)
    sections: list[ExpectedSection] = Field(min_length=1, max_length=7)
    unicode_tokens: list[str] = Field(default_factory=list, max_length=100)
    quantitative_tokens: list[str] = Field(default_factory=list, max_length=100)
    expected_pages: int = Field(strict=True, ge=1, le=2)

    @model_validator(mode="after")
    def standard_order_and_unique_entries(self) -> ExpectedDocument:
        allowed = [
            "Contact",
            "Professional Summary",
            "Professional Experience",
            "Selected Projects",
            "Education",
            "Skills",
            "Languages",
        ]
        labels = [section.label for section in self.sections]
        if labels != [label for label in allowed if label in labels]:
            raise ValueError("standard headings must be unique and in baseline order")
        ids = [entry.entry_id for section in self.sections for entry in section.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("entry IDs must be unique")
        if any(
            not token or token not in self.ordered_text
            for token in self.unicode_tokens + self.quantitative_tokens
        ):
            raise ValueError("expected tokens must occur in expected text")
        return self

    @property
    def ordered_text(self) -> str:
        return "\n".join(
            text
            for section in self.sections
            for text in [
                *([section.label] if section.heading_visible else []),
                *(entry.text for entry in section.entries),
            ]
        )
