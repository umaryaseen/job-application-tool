"""The private, isolated RenderCV/Typst production adapter.

Only a plan that passes the existing provenance validator reaches this module.
Candidate strings are inserted into a generated Typst file as escaped string
values; they are never interpreted as Typst, YAML, a template, a path, or a
link.  The worker process is run under macOS ``sandbox-exec`` with networking
denied.  This adapter therefore has an explicit current-laptop support scope.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from importlib.resources import files
from pathlib import Path

from ..config import ConfigurationError, private_data_root, safe_private_path
from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..verification.document import validate_document_plan
from ..verification.support import EvidenceKey
from .packages import PackageAssetsError, prepare_typst_packages
from .presentation import present_plan

RENDERCV_VERSION = "2.8"
TYPST_VERSION = "0.15.0"
FONTS_VERSION = "0.5.1"
TEMPLATE_VERSION = "baseline-v3-presentation-m1-fix005-hyphen-compounds"
NETWORK_DENY_PROFILE = "(version 1) (allow default) (deny network*)"
MAX_PDF_BYTES = 2_000_000
DEFAULT_TIMEOUT_SECONDS = 60
CONTACT_URL_WIDTH_ERROR = (
    "contact URL exceeds the fixed A4 20 mm margin and 11 pt contact width; "
    "use an approved shorter URL or omit this contact"
)
HYPHENATED_COMPOUND_WIDTH_ERROR = (
    "hyphenated compound exceeds the fixed A4 content width at the approved typography; "
    "use an approved shorter wording"
)
_HYPHENATED_TOKEN = re.compile(r"(?<!\S)(?P<token>\S*-\S+)")


class PdfRenderError(RuntimeError):
    """Raised when a production PDF cannot be safely built."""


def _template_text() -> str:
    return (
        files("job_application_engine.rendering.templates")
        .joinpath("baseline.yaml")
        .read_text(encoding="utf-8")
    )


def template_sha256() -> str:
    return hashlib.sha256(_template_text().encode("utf-8")).hexdigest()


def _yaml_for_plan(
    plan: DocumentPlan, profile: ProfileRevision
) -> tuple[str, dict[str, dict[str, str]]]:
    """Build the fixed RenderCV input and a token map from a validated plan."""

    tokens: dict[str, dict[str, str]] = {}
    section_lines: list[str] = []
    header_name: str | None = None
    header_contacts: str | None = None
    for section_index, section in enumerate(present_plan(plan, profile)):
        if not section.label:
            if section.lines:
                header_name = section.lines[0].text
                header_contacts = "\n".join(line.text for line in section.lines[1:])
            continue
        # RenderCV wraps each section body in a container where Typst's
        # pagebreak operator is forbidden.  A trusted section-name marker
        # lets the worker add a conditional page-fill spacer before the
        # heading, preserving content-aware pagination without exposing a
        # page-break flag to caller text.
        section_label = (
            f"JAE_PAGE_FILL_BEFORE__{section.label}" if section.page_break_before else section.label
        )
        section_lines.append(f"    {section_label}:")
        for line_index, line in enumerate(section.lines):
            token = f"JAECLAIM_{section_index:02d}_{line_index:03d}"
            tokens[token] = {"text": line.text, "style": line.style}
            section_lines.append(f"      - {json.dumps(token, ensure_ascii=False)}")
    template = _template_text().replace("    __JAE_SECTIONS__", "\n".join(section_lines))
    if header_name is not None:
        tokens["JAE_HEADER_NAME"] = {"text": header_name, "style": "header-name"}
        tokens["JAE_HEADER_CONTACTS"] = {
            "text": header_contacts or "",
            "style": "header-contacts",
        }
        template = template.replace("  name: null", '  name: "JAE_HEADER_NAME"')
        template = template.replace("  headline: null", '  headline: "JAE_HEADER_CONTACTS"')
    return template, tokens


def _sandbox_executable() -> str:
    executable = shutil.which("sandbox-exec")
    if executable is None:
        raise PdfRenderError(
            "RenderCV PDF build requires macOS sandbox-exec; network isolation is unavailable"
        )
    return executable


def _private_stage(root: Path, stage: Path) -> Path:
    try:
        relative = stage.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise PdfRenderError("renderer staging path is outside the private data root") from error
    try:
        return safe_private_path(relative, root=root)
    except ConfigurationError as error:
        raise PdfRenderError(str(error)) from error


def _contact_url_width_guard(contact_text: str) -> str:
    """Return a Typst measurement guard for each literal URL contact line."""

    url_lines = [line for line in contact_text.splitlines() if line.startswith("Url: ")]
    checks: list[str] = []
    for line in url_lines:
        encoded = json.dumps(line, ensure_ascii=False)
        error = json.dumps(CONTACT_URL_WIDTH_ERROR)
        checks.append(
            "#context {\n"
            f'  let jae_contact_url = text(font: "Raleway", size: 11pt, {encoded})\n'
            "  layout(size => {\n"
            "    if measure(jae_contact_url).width > size.width {\n"
            f"      panic({error})\n"
            "    }\n"
            "  })\n"
            "}\n"
        )
    return "".join(checks)


def _literal_text_expression(text_value: str) -> str:
    """Emit escaped literal text with atomic ASCII-hyphenated compounds."""

    parts: list[str] = []
    cursor = 0
    for match in _HYPHENATED_TOKEN.finditer(text_value):
        if match.start() > cursor:
            parts.append(
                f"#text({json.dumps(text_value[cursor : match.start()], ensure_ascii=False)})"
            )
        parts.append(f"#box[#text({json.dumps(match.group('token'), ensure_ascii=False)})]")
        cursor = match.end()
    if cursor < len(text_value):
        parts.append(f"#text({json.dumps(text_value[cursor:], ensure_ascii=False)})")
    return "".join(parts) or '#text("")'


def _compound_width_guard(tokens: Sequence[tuple[str, str]]) -> str:
    """Measure each atomic compound before layout can overflow or clip it."""

    checks: list[str] = []
    seen: set[tuple[str, str]] = set()
    for token, style in tokens:
        key = (token, style)
        if key in seen:
            continue
        seen.add(key)
        size = "15pt" if style == "name" else "11pt"
        weight = ', weight: "bold"' if style in {"employment", "subheading"} else ""
        inset = "0.4cm" if style in {"bullet", "project"} else "0pt"
        encoded = json.dumps(token, ensure_ascii=False)
        error = json.dumps(HYPHENATED_COMPOUND_WIDTH_ERROR)
        checks.append(
            "#context {\n"
            f'  let jae_compound = text(font: "Raleway", size: {size}{weight}, {encoded})\n'
            "  layout(size => {\n"
            f"    if measure(jae_compound).width > size.width - {inset} {{\n"
            f"      panic({error})\n"
            "    }\n"
            "  })\n"
            "}\n"
        )
    return "".join(checks)


def _worker(stage_argument: str) -> int:
    """Render inside the already sandboxed child process."""

    root = private_data_root()
    stage = _private_stage(root, Path(stage_argument))
    input_path = stage / "input.yaml"
    typ_path = stage / "generated.typ"
    safe_typ_path = stage / "safe.typ"
    output_path = stage / "output.pdf"
    tokens_path = stage / "tokens.json"
    if not all(path.is_file() for path in (input_path, tokens_path)):
        return 20

    executable = Path(sys.executable).with_name("rendercv")
    if not executable.is_file():
        return 21
    environment = os.environ.copy()
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"):
        environment.pop(name, None)
        environment.pop(name.lower(), None)
    try:
        result = subprocess.run(
            [
                str(executable),
                "render",
                "input.yaml",
                "-typ",
                "generated.typ",
                "-nopdf",
                "-nopng",
                "-nomd",
                "-q",
            ],
            cwd=stage,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 22
    if result.returncode != 0 or not typ_path.is_file():
        return 23

    try:
        typ_text = typ_path.read_text(encoding="utf-8")
        # Keep approved words intact across line boundaries.  This is a
        # trusted-template setting; it does not alter candidate text.
        typ_text = "#set text(hyphenate: false)\n" + typ_text
        typ_text = re.sub(
            r"^== JAE\\_PAGE\\_FILL\\_BEFORE\\_\\_(.+)$",
            lambda match: (
                "#context { if counter(page).get().first() == 1 { v(1fr) } }\n"
                f"== {match.group(1)}"
            ),
            typ_text,
            flags=re.MULTILINE,
        )
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
        if not isinstance(tokens, dict):
            return 24
        compound_tokens: list[tuple[str, str]] = []
        for token, value in tokens.items():
            if (
                not isinstance(token, str)
                or not isinstance(value, dict)
                or not isinstance(value.get("text"), str)
                or value.get("style")
                not in {
                    "body",
                    "name",
                    "subheading",
                    "employment",
                    "bullet",
                    "project",
                    "header-name",
                    "header-contacts",
                }
            ):
                return 25
            text_value = value["text"]
            style = value["style"]
            if style not in {"header-name", "header-contacts"}:
                compound_tokens.extend(
                    (match.group("token"), style)
                    for match in _HYPHENATED_TOKEN.finditer(text_value)
                )
            if style == "header-name":
                replacement = json.dumps(text_value, ensure_ascii=False)[1:-1]
            elif style == "header-contacts":
                contact_lines = text_value.splitlines()
                replacement = (
                    "#linebreak()".join(
                        f"#block(breakable: false)[#text({json.dumps(line, ensure_ascii=False)})]"
                        for line in contact_lines
                        if line
                    )
                    or '#text("")'
                )
            elif style == "employment":
                expression = _literal_text_expression(text_value)
                replacement = f'#block(breakable: false)[#text(weight: "bold")[{expression}]]'
            elif style == "bullet":
                replacement = (
                    "#block(inset: (left: 0.4cm))["
                    "#set par(first-line-indent: -0.4cm); "
                    f"{_literal_text_expression('• ' + text_value)}]"
                )
            elif style == "project":
                replacement = f"#pad(left: 0.4cm)[{_literal_text_expression(text_value)}]"
            elif style == "name":
                replacement = (
                    f'#text(weight: "bold", size: 15pt)[{_literal_text_expression(text_value)}]'
                )
            elif style == "subheading":
                replacement = f'#text(weight: "bold")[{_literal_text_expression(text_value)}]'
            else:
                replacement = _literal_text_expression(text_value)
            typ_text = typ_text.replace(token, replacement).replace(
                token.replace("_", r"\_"), replacement
            )
        if "JAECLAIM_" in typ_text:
            return 26
        compound_guard = _compound_width_guard(compound_tokens)
        contact_text = next(
            (value["text"] for value in tokens.values() if value["style"] == "header-contacts"),
            "",
        )
        width_guard = _contact_url_width_guard(contact_text)
        if width_guard:
            heading = re.search(r"^= [^\n]*$", typ_text, flags=re.MULTILINE)
            if heading is None:
                return 26
            typ_text = typ_text[: heading.start()] + width_guard + typ_text[heading.start() :]
        if compound_guard:
            heading = re.search(r"^= [^\n]*$", typ_text, flags=re.MULTILINE)
            if heading is None:
                return 26
            typ_text = typ_text[: heading.start()] + compound_guard + typ_text[heading.start() :]
        safe_typ_path.write_text(typ_text, encoding="utf-8")
        import rendercv  # type: ignore[import-untyped]
        import rendercv_fonts  # type: ignore[import-untyped]
        import typst

        package_path = Path(rendercv.__file__).parent / "renderer" / "rendercv_typst"
        try:
            local_packages = prepare_typst_packages(stage, package_path)
        except (OSError, PackageAssetsError):
            return 29
        compiler = typst.Compiler(
            input=str(safe_typ_path),
            root=str(stage),
            font_paths=[str(path) for path in rendercv_fonts.paths_to_font_folders],
            ignore_system_fonts=True,
            package_path=str(local_packages),
            package_cache_path=str(local_packages),
        )
        compiler.compile(output=str(output_path))
    except Exception as error:
        if CONTACT_URL_WIDTH_ERROR in str(error) or HYPHENATED_COMPOUND_WIDTH_ERROR in str(error):
            try:
                diagnostic = (
                    CONTACT_URL_WIDTH_ERROR
                    if CONTACT_URL_WIDTH_ERROR in str(error)
                    else HYPHENATED_COMPOUND_WIDTH_ERROR
                )
                (stage / "error.txt").write_text(diagnostic, encoding="utf-8")
            except OSError:
                pass
        return 27
    if not output_path.is_file() or output_path.stat().st_size > MAX_PDF_BYTES:
        return 28
    return 0


def build_pdf(
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
    support_captures: Mapping[EvidenceKey, bytes | bytearray | Path] | None = None,
    data_root: str | os.PathLike[str] | None = None,
    output_name: str = "baseline.pdf",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Path:
    """Validate and build one PDF under the configured private data root."""

    validate_document_plan(plan, profile, reviews=reviews, support_captures=support_captures)
    if timeout_seconds < 1 or timeout_seconds > DEFAULT_TIMEOUT_SECONDS:
        raise PdfRenderError("renderer timeout must be between 1 and 60 seconds")
    sandbox = _sandbox_executable()
    root = private_data_root(data_root)
    try:
        final_path = safe_private_path(Path("outputs") / output_name, root=root)
    except ConfigurationError as error:
        raise PdfRenderError(str(error)) from error
    if final_path.suffix.lower() != ".pdf":
        raise PdfRenderError("output name must end in .pdf")
    if final_path.exists():
        raise PdfRenderError("refusing to overwrite an existing private PDF")
    final_path.parent.mkdir(parents=True, exist_ok=True)

    yaml_text, tokens = _yaml_for_plan(plan, profile)
    with tempfile.TemporaryDirectory(prefix=".jae-pdf-", dir=root) as temporary:
        stage = Path(temporary)
        _private_stage(root, stage)
        (stage / "input.yaml").write_text(yaml_text, encoding="utf-8")
        (stage / "tokens.json").write_text(
            json.dumps(tokens, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )
        worker_command = [sandbox, "-p", NETWORK_DENY_PROFILE, sys.executable, "-m"]
        worker_command.extend(["job_application_engine.rendering.pdf", "--worker", str(stage)])
        environment = os.environ.copy()
        environment["JAE_DATA_DIR"] = str(root)
        try:
            result = subprocess.run(
                worker_command,
                cwd=stage,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise PdfRenderError("RenderCV PDF build timed out") from error
        except OSError as error:
            raise PdfRenderError("RenderCV PDF worker could not start") from error
        if result.returncode == 29:
            raise PdfRenderError(
                "offline Typst packages missing or changed; run scripts/setup_typst_packages.py "
                "and set JAE_TYPST_PACKAGE_ROOT"
            )
        if result.returncode != 0:
            try:
                diagnostic = (stage / "error.txt").read_text(encoding="utf-8")
            except OSError:
                diagnostic = ""
            if diagnostic not in {
                CONTACT_URL_WIDTH_ERROR,
                HYPHENATED_COMPOUND_WIDTH_ERROR,
            }:
                diagnostic = f"RenderCV PDF build failed (worker exit {result.returncode})"
            raise PdfRenderError(diagnostic)
        built = stage / "output.pdf"
        if not built.is_file() or built.stat().st_size > MAX_PDF_BYTES:
            raise PdfRenderError("RenderCV PDF worker produced no bounded PDF")
        os.replace(built, final_path)
    return final_path


def _main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        return _worker(sys.argv[2])
    return 2


if __name__ == "__main__":
    raise SystemExit(_main())
