"""Run the TASK-005 RenderCV/Typst and HTML/Playwright comparison."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CASE_ROOT = ROOT / "artifacts" / "renderer" / "task-005" / "cases"
OUT = ROOT / "artifacts" / "renderer" / "task-005" / "outputs"
VENV = ROOT / "experiments" / "renderer" / ".venv"
RENDERCV = VENV / "bin" / "rendercv"
PACKAGE_PATH = (
    VENV / "lib" / "python3.12" / "site-packages" / "rendercv" / "renderer" / "rendercv_typst"
)
FONT_ROOT = VENV / "lib" / "python3.12" / "site-packages" / "rendercv_fonts"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_rendercv(case_dir: Path, typ_path: Path, input_name: str = "input.yaml") -> dict[str, Any]:
    command = [
        str(RENDERCV),
        "render",
        input_name,
        "-typ",
        str(typ_path),
        "-nopdf",
        "-nopng",
        "-nomd",
    ]
    sandboxed = shutil.which("sandbox-exec")
    if sandboxed:
        command = [sandboxed, "-p", "(version 1) (allow default) (deny network*)", *command]
    try:
        completed = subprocess.run(
            command, cwd=case_dir, text=True, capture_output=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "error", "sandboxed": bool(sandboxed), "error": str(error)}
    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "sandboxed": bool(sandboxed),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def compile_typst(typ_path: Path, pdf_path: Path) -> dict[str, Any]:
    try:
        import typst  # type: ignore[import-not-found]

        compiler = typst.Compiler(
            input=str(typ_path),
            root=str(typ_path.parent),
            font_paths=[str(path) for path in FONT_ROOT.iterdir() if path.is_dir()],
            ignore_system_fonts=True,
            package_path=str(PACKAGE_PATH),
        )
        compiler.compile(output=str(pdf_path))
    except Exception as error:  # renderer experiment records candidate failures
        return {"status": "failed", "error": str(error)}
    return {"status": "ok", "sha256": sha256(pdf_path)}


def measure_pdf(pdf_path: Path, expected: list[str], output_dir: Path) -> dict[str, Any]:
    info = subprocess.run(["pdfinfo", str(pdf_path)], text=True, capture_output=True, check=False)
    text_path = output_dir / f"{pdf_path.stem}.txt"
    extracted = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(text_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""
    normalized = re.sub(r"\s+", " ", text).strip()
    missing = [item for item in expected if re.sub(r"\s+", " ", item).strip() not in normalized]
    prefixes_missing = [
        item[:48] for item in expected if re.sub(r"\s+", " ", item[:48]).strip() not in normalized
    ]
    page_info: dict[str, Any] = {}
    for line in info.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            page_info[key.strip()] = value.strip()
    pypdf_text = ""
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]

        pypdf_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)
    except Exception as error:
        page_info["pypdf_error"] = str(error)
    raster_prefix = output_dir / pdf_path.stem
    raster = subprocess.run(
        ["pdftoppm", "-png", "-r", "110", str(pdf_path), str(raster_prefix)],
        text=True,
        capture_output=True,
        check=False,
    )
    sentinel = "SECRET_SENTINEL_NOT_CLAIM_TEXT"
    positions = [normalized.find(re.sub(r"\s+", " ", item[:48]).strip()) for item in expected]
    return {
        "sha256": sha256(pdf_path),
        "pdfinfo": page_info,
        "pdftotext_returncode": extracted.returncode,
        "pypdf_text_sha256": hashlib.sha256(pypdf_text.encode("utf-8")).hexdigest(),
        "expected_claims_missing_from_pdftotext": missing,
        "claim_prefixes_missing_from_pdftotext": prefixes_missing,
        "claim_prefixes_in_document_order": all(position >= 0 for position in positions)
        and positions == sorted(positions),
        "unicode_preserved": "Größe Ä Ö Ü ß" in text,
        "sentinel_not_recovered": sentinel not in text and sentinel not in pypdf_text,
        "raster_returncode": raster.returncode,
        "raster_pages": [path.name for path in sorted(output_dir.glob(f"{pdf_path.stem}-*.png"))],
        "text_path": str(text_path.relative_to(ROOT)),
    }


def safe_typst_case(case_id: str) -> dict[str, Any]:
    case_dir = CASE_ROOT / case_id
    output_dir = OUT / "rendercv" / case_id
    output_dir.mkdir(parents=True, exist_ok=True)
    typ_path = output_dir / "generated.typ"
    render_result = run_rendercv(case_dir, typ_path)
    if render_result["status"] != "ok":
        return {"backend": "rendercv-typst", "status": "failed", "rendercv": render_result}
    typ_text = typ_path.read_text(encoding="utf-8")
    tokens = json.loads((case_dir / "tokens.json").read_text(encoding="utf-8"))
    sentinel_path = output_dir / "sentinel"
    sentinel_path.write_text("SECRET_SENTINEL_NOT_CLAIM_TEXT", encoding="utf-8")
    for token, value in tokens.items():
        # Candidate strings are inserted as Typst string literals after the
        # template is generated. This prevents candidate text from becoming
        # Typst markup, includes, reads, links, or other commands.
        replacement = f"#text({json.dumps(value, ensure_ascii=False)})"
        typ_text = typ_text.replace(token, replacement).replace(
            token.replace("_", r"\_"), replacement
        )
    safe_path = output_dir / "safe.typ"
    safe_path.write_text(typ_text, encoding="utf-8")
    pdf_path = output_dir / "output.pdf"
    compiled = compile_typst(safe_path, pdf_path)
    if compiled["status"] != "ok":
        return {
            "backend": "rendercv-typst",
            "status": "failed",
            "rendercv": render_result,
            "compile": compiled,
        }
    plan = json.loads((case_dir / "plan.json").read_text(encoding="utf-8"))
    expected = [str(line["text"]) for section in plan["sections"] for line in section["lines"]]
    measured = measure_pdf(pdf_path, expected, output_dir)
    return {
        "backend": "rendercv-typst",
        "status": "ok",
        "rendercv": render_result,
        "compile": compiled,
        "measurements": measured,
    }


def html_case(case_id: str) -> dict[str, Any]:
    case_dir = CASE_ROOT / case_id
    output_dir = OUT / "html-playwright" / case_id
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads((case_dir / "plan.json").read_text(encoding="utf-8"))
    sections = []
    expected = []
    for section in plan["sections"]:
        rows = []
        for line in section["lines"]:
            value = str(line["text"])
            expected.append(value)
            rows.append(f"<p>{html.escape(value, quote=True)}</p>")
        sections.append(
            f"<section><h2>{html.escape(str(section['label']))}</h2>{''.join(rows)}</section>"
        )
    source = (
        '<!doctype html><meta charset="utf-8"><style>\n'
        "@page { size: A4; margin: 20mm; }\n"
        "body { font-family: sans-serif; font-size: 11pt; line-height: 1.25; margin: 0; }\n"
        "h1 { font-size: 16pt; margin: 0 0 8pt; } "
        "h2 { font-size: 12pt; border-bottom: .5pt solid; "
        "margin: 14pt 0 5pt; }\n"
        "p { margin: 0 0 4pt; overflow-wrap: anywhere; } section { break-inside: avoid; }\n"
        "</style><main><h1>synthetic baseline</h1>" + "".join(sections) + "</main>"
    )
    html_path = output_dir / "input.html"
    html_path.write_text(source, encoding="utf-8")
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]

        pdf_path = output_dir / "output.pdf"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.route("**/*", lambda route: route.abort())
            page.set_content(source, wait_until="load")
            page.pdf(
                path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True
            )
            browser.close()
        measured = measure_pdf(pdf_path, expected, output_dir)
        return {"backend": "html-playwright", "status": "ok", "measurements": measured}
    except Exception as error:
        return {
            "backend": "html-playwright",
            "status": "blocked",
            "error": str(error),
            "html_path": str(html_path.relative_to(ROOT)),
            "hostile_markup_escaped": "&lt;script&gt;" in source
            and "<script>synthetic</script>" not in source,
            "external_url_is_plain_text": "href=" not in source
            and "https://example.invalid" in source,
        }


def network_probe() -> dict[str, Any]:
    """Verify the sandbox denies a synthetic local HTTP resource."""
    if not shutil.which("sandbox-exec"):
        return {"status": "unrun", "reason": "sandbox-exec unavailable"}
    import http.server
    import threading

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"SECRET_NETWORK_SENTINEL")

        def log_message(self, *_args: object) -> None:
            return

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    code = (
        "import urllib.request; "
        f"urllib.request.urlopen('http://127.0.0.1:{server.server_port}', timeout=2).read()"
    )
    command = [
        "/usr/bin/sandbox-exec",
        "-p",
        "(version 1) (allow default) (deny network*)",
        str(VENV / "bin" / "python"),
        "-c",
        code,
    ]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=10)
    finally:
        server.shutdown()
        server.server_close()
    return {
        "status": "blocked" if result.returncode != 0 else "unexpectedly_allowed",
        "returncode": result.returncode,
        "stderr": result.stderr[-1000:],
        "synthetic_sentinel": "SECRET_NETWORK_SENTINEL",
    }


def letter_case() -> dict[str, Any]:
    case_dir = CASE_ROOT / "letter"
    output_dir = OUT / "rendercv" / "letter"
    output_dir.mkdir(parents=True, exist_ok=True)
    text = json.loads((case_dir / "letter.json").read_text(encoding="utf-8"))["text"]
    yaml = "\n".join(
        [
            "cv:",
            '  name: "Synthetic Example"',
            "  headline: null",
            "  sections:",
            "    Letter:",
            '      - "JAELETTER"',
            "design:",
            "  theme: engineeringclassic",
            "  page:",
            "    size: a4",
            "    top_margin: 20mm",
            "    bottom_margin: 20mm",
            "    left_margin: 20mm",
            "    right_margin: 20mm",
            "    show_footer: false",
            "    show_top_note: false",
            "",
        ]
    )
    input_path = output_dir / "letter.yaml"
    input_path.write_text(yaml, encoding="utf-8")
    typ_path = output_dir / "letter.typ"
    result = run_rendercv(output_dir, typ_path, "letter.yaml")
    if result["status"] != "ok":
        return {"status": "failed", "rendercv": result}
    typ_text = typ_path.read_text(encoding="utf-8").replace(
        "JAELETTER", f"#text({json.dumps(text, ensure_ascii=False)})"
    )
    safe_path = output_dir / "letter-safe.typ"
    safe_path.write_text(typ_text, encoding="utf-8")
    pdf_path = output_dir / "letter.pdf"
    compiled = compile_typst(safe_path, pdf_path)
    if compiled["status"] != "ok":
        return {"status": "failed", "rendercv": result, "compile": compiled}
    return {
        "status": "ok",
        "rendercv": result,
        "compile": compiled,
        "measurements": measure_pdf(
            pdf_path, ["Synthetic Example", "one-page feasibility"], output_dir
        ),
    }


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {
        "environment": {"python": sys.version, "platform": sys.platform},
        "cases": {},
    }
    for case_id in ["short", "two-page", "german-unicode", "long-wrapping", "hostile-text"]:
        results["cases"][case_id] = {
            "rendercv": safe_typst_case(case_id),
            "html": html_case(case_id),
        }
    results["letter"] = letter_case()
    results["security_probe"] = network_probe()
    (OUT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
