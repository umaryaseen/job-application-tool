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
import unicodedata
from collections.abc import Mapping, Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any

from ..config import ConfigurationError, private_data_root, safe_private_path
from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.baseline import URL_CONTACT_LABELS
from ..profile.review import LocalReviewReceipt
from ..verification.document import validate_document_plan
from ..verification.support import EvidenceKey
from .packages import PackageAssetsError, prepare_typst_packages
from .presentation import SKILL_GROUP_HEADINGS, present_plan

RENDERCV_VERSION = "2.8"
TYPST_VERSION = "0.15.0"
FONTS_VERSION = "0.5.1"
TEMPLATE_VERSION = "baseline-v7-m1-fix009-compact-contacts"
NETWORK_DENY_PROFILE = "(version 1) (allow default) (deny network*)"
MAX_PDF_BYTES = 2_000_000
DEFAULT_TIMEOUT_SECONDS = 60
CONTACT_URL_WIDTH_ERROR = (
    "contact URL exceeds the fixed A4 20 mm margin and 11 pt contact width; "
    "use an approved shorter URL or omit this contact"
)
ITEM_CONTENT_ERROR = (
    "a skill or contact item has no visible text, contains a control or line-break "
    "character, or begins with the | separator; use an approved corrected wording"
)
ITEM_WIDTH_ERROR = (
    "a skill or contact item exceeds the fixed A4 content width at the approved "
    "typography; use an approved shorter wording"
)
HYPHENATED_COMPOUND_WIDTH_ERROR = (
    "hyphenated or slash-joined compound exceeds the fixed A4 content width at the "
    "approved typography; "
    "use an approved shorter wording"
)
# Whitespace-delimited tokens containing a hyphen or slash anywhere ("full-stack",
# "CI/CD", "ISO/DIN", "trailing/", a lone "/") are atomic: a line break inside
# them would change the extracted text that applicant-tracking systems read.
_HYPHENATED_TOKEN = re.compile(r"(?<!\S)(?P<token>\S*[-/]\S*)")


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
) -> tuple[str, dict[str, dict[str, Any]]]:
    """Build the fixed RenderCV input and a token map from a validated plan."""

    tokens: dict[str, dict[str, Any]] = {}
    section_lines: list[str] = []
    header_name: str | None = None
    header_contacts: str | None = None
    header_lines: list[list[str]] = []
    for section_index, section in enumerate(present_plan(plan, profile)):
        if not section.label:
            if section.lines:
                header_name = section.lines[0].text
                header_contacts = "\n".join(line.text for line in section.lines[1:])
                header_lines = [list(line.items) for line in section.lines[1:]]
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
            if line.style == "skill-group":
                tokens[token]["lead"] = line.lead
                tokens[token]["items"] = list(line.items)
            section_lines.append(f"      - {json.dumps(token, ensure_ascii=False)}")
    template = _template_text().replace("    __JAE_SECTIONS__", "\n".join(section_lines))
    if header_name is not None:
        tokens["JAE_HEADER_NAME"] = {"text": header_name, "style": "header-name"}
        tokens["JAE_HEADER_CONTACTS"] = {
            "text": header_contacts or "",
            "style": "header-contacts",
            "lines": header_lines,
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

    prefixes = tuple(f"{label}: " for label in URL_CONTACT_LABELS)
    url_lines = [line for line in contact_text.splitlines() if line.startswith(prefixes)]
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
    """Emit escaped literal text with atomic hyphen- or slash-joined compounds."""

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
        # A skill-group line mixes a bold lead with regular text; measuring its
        # compounds in bold is the conservative (wider) choice.
        weight = ', weight: "bold"' if style in {"employment", "subheading", "skill-group"} else ""
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


_TOKEN_STYLES = frozenset(
    {
        "body",
        "name",
        "subheading",
        "employment",
        "bullet",
        "project",
        "skill-group",
        "period",
        "header-name",
        "header-contacts",
    }
)


def item_problem(item: object) -> str | None:
    """Why ``item`` cannot be one unbreakable skill or contact box, or None.

    An item must contain visible text, no control, line- or paragraph-separator
    character (any of which would break the box), and must not begin with the
    "|" separator (which would then start a line).
    """

    if not isinstance(item, str):
        return "not text"
    if any(unicodedata.category(char) in {"Cc", "Zl", "Zp"} for char in item):
        return "contains a control or line-break character"
    visible = [char for char in item if unicodedata.category(char)[0] not in {"Z", "C"}]
    if not visible:
        return "has no visible text"
    if visible[0] == "|":
        return "begins with the | separator"
    return None


def _valid_items(items: object) -> bool:
    return (
        isinstance(items, list)
        and bool(items)
        and all(item_problem(item) is None for item in items)
    )


def _valid_token_value(value: object) -> bool:
    """Accept only the exact token shapes the trusted parent writes.

    A skill-group token carries ``lead`` (one allowlisted static heading) and
    ``items``; its text must be exactly ``lead + ": " + " | ".join(items)``. The
    header-contacts token carries ``lines`` (items per line); its text must be
    exactly those lines joined. Every other token has only text and style.
    """

    if not isinstance(value, dict):
        return False
    text_value, style = value.get("text"), value.get("style")
    if not isinstance(text_value, str) or style not in _TOKEN_STYLES:
        return False
    if style == "skill-group":
        lead, items = value.get("lead"), value.get("items")
        return (
            set(value) == {"text", "style", "lead", "items"}
            and isinstance(lead, str)
            and lead in SKILL_GROUP_HEADINGS
            and _valid_items(items)
            and text_value == f"{lead}: " + " | ".join(items)  # type: ignore[arg-type]
        )
    if style == "header-contacts":
        lines = value.get("lines")
        return (
            set(value) == {"text", "style", "lines"}
            and isinstance(lines, list)
            and all(_valid_items(items) for items in lines)
            and text_value == "\n".join(" | ".join(items) for items in lines)
        )
    return set(value) == {"text", "style"}


def _items_expression(items: Sequence[str]) -> str:
    """Unbreakable boxes, each item keeping its trailing separator."""

    last = len(items) - 1
    return " ".join(
        f"#box[#text({json.dumps(item + ('' if index == last else ' |'), ensure_ascii=False)})]"
        for index, item in enumerate(items)
    )


def _item_width_guard(boxes: Sequence[tuple[str, bool]]) -> str:
    """Fail before layout can overflow if an unbreakable item cannot fit a line."""

    checks: list[str] = []
    for text_value, bold in dict.fromkeys(boxes):
        encoded = json.dumps(text_value, ensure_ascii=False)
        weight = ', weight: "bold"' if bold else ""
        error = json.dumps(ITEM_WIDTH_ERROR)
        checks.append(
            "#context {\n"
            f'  let jae_item = text(font: "Raleway", size: 11pt{weight}, {encoded})\n'
            "  layout(size => {\n"
            "    if measure(jae_item).width > size.width {\n"
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
        item_boxes: list[tuple[str, bool]] = []
        replacements: dict[str, str] = {}
        for token, value in tokens.items():
            if not isinstance(token, str) or not _valid_token_value(value):
                return 25
            text_value = value["text"]
            style = value["style"]
            lead = value.get("lead")
            if style not in {"header-name", "header-contacts"}:
                compound_tokens.extend(
                    (match.group("token"), style)
                    for match in _HYPHENATED_TOKEN.finditer(text_value)
                )
            if style == "header-name":
                replacement = json.dumps(text_value, ensure_ascii=False)[1:-1]
            elif style == "header-contacts":
                contact_lines = value["lines"]
                for items in contact_lines:
                    last = len(items) - 1
                    item_boxes.extend(
                        (item + ("" if i == last else " |"), False) for i, item in enumerate(items)
                    )
                replacement = (
                    "#linebreak()".join(
                        f"#block(breakable: false)[{_items_expression(items)}]"
                        for items in contact_lines
                    )
                    or '#text("")'
                )
            elif style == "employment":
                # Sticky: an employment header never ends a page without its dates.
                expression = _literal_text_expression(text_value)
                replacement = (
                    f'#block(breakable: false, sticky: true)[#text(weight: "bold")[{expression}]]'
                )
            elif style == "period":
                # Sticky: the dates stay with the first responsibility or project line.
                expression = _literal_text_expression(text_value)
                replacement = f"#block(breakable: false, sticky: true)[{expression}]"
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
            elif style == "skill-group":
                assert isinstance(lead, str)
                items = value["items"]
                last = len(items) - 1
                item_boxes.append((lead + ":", True))
                item_boxes.extend(
                    (item + ("" if i == last else " |"), False) for i, item in enumerate(items)
                )
                encoded_lead = json.dumps(lead + ":", ensure_ascii=False)
                replacement = (
                    f'#box[#text(weight: "bold", {encoded_lead})] {_items_expression(items)}'
                )
            else:
                replacement = _literal_text_expression(text_value)
            replacements[token] = replacement
        # One pass over the generated source: inserted candidate text is never
        # scanned again, so text that happens to spell a placeholder stays text.
        spellings = {token: token for token in replacements}
        spellings |= {token.replace("_", r"\_"): token for token in replacements}
        placeholder = re.compile(
            "|".join(re.escape(text) for text in sorted(spellings, key=len, reverse=True))
        )
        used: set[str] = set()

        def substitute(match: re.Match[str]) -> str:
            token = spellings[match.group(0)]
            used.add(token)
            return replacements[token]

        claims_before = len(re.findall(r"JAECLAIM", typ_text))
        claims_matched = sum(
            spellings[match.group(0)].startswith("JAECLAIM")
            for match in placeholder.finditer(typ_text)
        )
        typ_text = placeholder.sub(substitute, typ_text)
        if used != set(replacements) or claims_before != claims_matched:
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
        item_guard = _item_width_guard(item_boxes)
        if item_guard:
            heading = re.search(r"^= [^\n]*$", typ_text, flags=re.MULTILINE)
            if heading is None:
                return 26
            typ_text = typ_text[: heading.start()] + item_guard + typ_text[heading.start() :]
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
        known = (CONTACT_URL_WIDTH_ERROR, HYPHENATED_COMPOUND_WIDTH_ERROR, ITEM_WIDTH_ERROR)
        if any(message in str(error) for message in known):
            try:
                diagnostic = next(message for message in known if message in str(error))
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
    item_lists = [value["items"] for value in tokens.values() if "items" in value] + [
        items for value in tokens.values() for items in value.get("lines", [])
    ]
    if any(item_problem(item) is not None for items in item_lists for item in items):
        raise PdfRenderError(ITEM_CONTENT_ERROR)
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
                ITEM_WIDTH_ERROR,
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
