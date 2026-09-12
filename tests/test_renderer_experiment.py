"""Pure content-oracle regression checks for the TASK-005 experiment."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from experiments.renderer.runner.render_experiment import (
    complete_content_controls,
    complete_content_matches,
    measurement_passed,
    normalize_extracted_text,
)


def test_pdf_layout_normalization_preserves_complete_claim_content() -> None:
    expected = "German (CEFR B2) 2022-01 https://example.invalid"
    extracted = "German (CEFR B2) 2022\N{SOFT HYPHEN}01 https:/ /\nexample.invalid"
    assert complete_content_matches(expected, extracted)


def test_complete_content_oracle_rejects_all_mutation_controls() -> None:
    expected = "\n".join(
        [
            "Professional Summary",
            "Synthetic Engineer",
            "Skills",
            "Größe Ä Ö Ü ß (context: study; proficiency: unknown)",
            "Languages",
            "German (CEFR B2)",
        ]
    )
    controls = complete_content_controls(expected)
    assert controls == {
        "suffix_removed": True,
        "qualification_changed": True,
        "claim_duplicated": True,
        "claim_moved": True,
        "unexpected_content": True,
    }
    assert not complete_content_matches(expected, expected[:-1])
    assert normalize_extracted_text(expected).startswith("Professional Summary Synthetic Engineer")


def test_failed_complete_measurement_is_not_a_render_pass() -> None:
    measurements = {
        "complete_content_match": False,
        "negative_controls_rejected": {"suffix_removed": True},
        "pdftotext_returncode": 0,
        "pdfinfo": {},
        "raster_returncode": 0,
        "unicode_preserved": True,
        "sentinel_not_recovered": True,
    }
    assert not measurement_passed(measurements, "Synthetic claim")
