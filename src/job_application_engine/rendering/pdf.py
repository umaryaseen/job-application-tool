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
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from importlib.resources import files
from pathlib import Path

from ..config import ConfigurationError, private_data_root, safe_private_path
from ..domain.document import DocumentPlan
from ..domain.profile import ProfileRevision
from ..profile.review import LocalReviewReceipt
from ..verification.document import validate_document_plan

RENDERCV_VERSION = "2.8"
TYPST_VERSION = "0.15.0"
FONTS_VERSION = "0.5.1"
TEMPLATE_VERSION = "baseline-v1"
NETWORK_DENY_PROFILE = "(version 1) (allow default) (deny network*)"
MAX_PDF_BYTES = 2_000_000
DEFAULT_TIMEOUT_SECONDS = 60


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


def _yaml_for_plan(plan: DocumentPlan) -> tuple[str, dict[str, str]]:
    """Build the fixed RenderCV input and a token map from a validated plan."""

    tokens: dict[str, str] = {}
    section_lines: list[str] = []
    for section_index, section in enumerate(plan.sections):
        section_lines.append(f"    {section.label}:")
        for line_index, line in enumerate(section.lines):
            token = f"JAECLAIM_{section_index:02d}_{line_index:03d}"
            tokens[token] = line.text
            section_lines.append(f"      - {json.dumps(token, ensure_ascii=False)}")
    return _template_text().replace("    __JAE_SECTIONS__", "\n".join(section_lines)), tokens


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
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
        if not isinstance(tokens, dict):
            return 24
        for token, value in tokens.items():
            if not isinstance(token, str) or not isinstance(value, str):
                return 25
            replacement = f"#text({json.dumps(value, ensure_ascii=False)})"
            typ_text = typ_text.replace(token, replacement).replace(
                token.replace("_", r"\_"), replacement
            )
        if "JAECLAIM_" in typ_text:
            return 26
        safe_typ_path.write_text(typ_text, encoding="utf-8")
        import rendercv  # type: ignore[import-untyped]
        import rendercv_fonts  # type: ignore[import-untyped]
        import typst

        package_path = Path(rendercv.__file__).parent / "renderer" / "rendercv_typst"
        compiler = typst.Compiler(
            input=str(safe_typ_path),
            root=str(stage),
            font_paths=[str(path) for path in rendercv_fonts.paths_to_font_folders],
            ignore_system_fonts=True,
            package_path=str(package_path),
        )
        compiler.compile(output=str(output_path))
    except Exception:
        return 27
    if not output_path.is_file() or output_path.stat().st_size > MAX_PDF_BYTES:
        return 28
    return 0


def build_pdf(
    plan: DocumentPlan,
    profile: ProfileRevision,
    *,
    reviews: Sequence[LocalReviewReceipt] = (),
    data_root: str | os.PathLike[str] | None = None,
    output_name: str = "baseline.pdf",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Path:
    """Validate and build one PDF under the configured private data root."""

    validate_document_plan(plan, profile, reviews=reviews)
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

    yaml_text, tokens = _yaml_for_plan(plan)
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
        if result.returncode != 0:
            raise PdfRenderError(f"RenderCV PDF build failed (worker exit {result.returncode})")
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
