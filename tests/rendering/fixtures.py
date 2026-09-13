"""Real PDF fixture recipes; expectations are separately authored JSON files."""

from datetime import date
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject, NumberObject

from experiments.renderer.prepare_cases import add_approved_variants
from job_application_engine.ats_qa.expected import ExpectedDocument
from job_application_engine.profile.baseline import compile_baseline
from job_application_engine.rendering.pdf import build_pdf
from tests.test_document_plan import approved_baseline

ORACLES = Path(__file__).parents[1] / "fixtures" / "rendering" / "task007"


def expected(name: str) -> ExpectedDocument:
    return ExpectedDocument.model_validate_json((ORACLES / f"{name}.json").read_text())


def production_pdf(root: Path, *, two_pages: bool) -> Path:
    profile, reviews = approved_baseline()
    additions = [
        ("qa-names", "Synthetic test names: Müller, Groß, İpek, Łukasz, François. ä ö ü Ä Ö Ü ß."),
        (
            "qa-metric",
            "Synthetic result: 30% is not 30 percentage points; 1,5 ms and 1.5 s (study only).",
        ),
    ]
    if two_pages:
        additions.extend(
            (
                f"qa-long-{n}",
                f"Synthetic statement {n}: "
                + "with deterministic wrapping " * 18
                + f"qualification {n} only.",
            )
            for n in range(1, 7)
        )
    profile, reviews = add_approved_variants(profile, reviews, additions)
    plan = compile_baseline(profile, as_of=date(2026, 9, 12), reviews=reviews)
    return build_pdf(plan, profile, reviews=reviews, data_root=root)


def adversarial_pdf(path: Path, mutation: str = "none") -> Path:
    # Minimal test-only PDF objects, no additional renderer/template backend.
    # Keep these actual content strings independent of expected JSON traversal.
    lines = [
        "Contact",
        "Synthetic Candidate",
        "Email: synthetic@example.com",
        "Professional Experience",
        "Analyst at Alpha Example 2020-01 to 2021-12: 30% (study only).",
        "Engineer at Beta Example 2022-01 to 2022-12: 1.5 s (not production).",
    ]
    if mutation == "wrong_order":
        lines[4], lines[5] = lines[5], lines[4]
    elif mutation == "duplicate":
        lines.append(lines[4])
    elif mutation == "missing":
        lines.pop(4)
    elif mutation == "suffix_loss":
        lines[4] = lines[4].replace(" (study only).", "")
    elif mutation == "qualification":
        lines[4] = lines[4].replace("study only", "production")
    elif mutation == "numeric_punctuation":
        lines[5] = lines[5].replace("1.5", "15")
    elif mutation == "lost_date":
        lines[4] = lines[4].replace("2020-01", "")
    elif mutation == "wrong_scope":
        lines[4] = lines[4].replace("2020-01", "2022-01")
        lines[5] = lines[5].replace("2022-01", "2020-01")
    elif mutation == "unexpected":
        lines.append("Unexpected synthetic claim")
    elif mutation == "heading":
        lines[3] = "Career Adventures"
    elif mutation in {"empty", "image_only"}:
        lines = []
    writer = PdfWriter()
    page = writer.add_blank_page(width=612 if mutation == "dimensions" else 595.276, height=841.89)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    resources = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )
    page[NameObject("/Resources")] = resources
    commands = ["q 50 710 10 10 re W n" if mutation == "clip" else "q"]
    for index, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        x = 580 if mutation == "overflow" and index == 4 else 55
        mode = 3 if mutation == "hidden" and index == 4 else 0
        commands.append(f"BT /F1 11 Tf {mode} Tr {x} {780 - index * 25} Td ({escaped}) Tj ET")
    if mutation == "image_only":
        img = DecodedStreamObject()
        img.set_data(b"\x00\x00\x00")
        img.update(
            {
                NameObject("/Type"): NameObject("/XObject"),
                NameObject("/Subtype"): NameObject("/Image"),
                NameObject("/Width"): NumberObject(1),
                NameObject("/Height"): NumberObject(1),
                NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
                NameObject("/BitsPerComponent"): NumberObject(8),
            }
        )
        resources[NameObject("/XObject")] = DictionaryObject(
            {NameObject("/Im1"): writer._add_object(img)}
        )
        commands.append("100 0 0 100 55 600 cm /Im1 Do")
    commands.append("Q")
    stream = DecodedStreamObject()
    stream.set_data("\n".join(commands).encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    with path.open("wb") as output:
        writer.write(output)
    return path
