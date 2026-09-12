# TASK-005 renderer experiment decision

Date: 2026-09-12
Task branch: `task/005-renderer-experiment`
Base: `82deb141f84c59d86da78f68f06c4e35dfc339c0` (approved TASK-004 merge)

This report records an experiment, not a production backend approval. All
claims and letter text are synthetic. Generated PDFs, PNGs, HTML, logs and
sentinels are under the ignored `artifacts/renderer/task-005/` directory.

## Reproduction and environment

```sh
export PATH="/Users/apple/.local/bin:$PATH"
uv sync --project experiments/renderer --locked
uv run python experiments/renderer/prepare_cases.py
experiments/renderer/.venv/bin/python experiments/renderer/runner/render_experiment.py
```

The repository environment is Python 3.12.14 from uv. The host is macOS
13.6.9 (Darwin 22.6.0, x86_64); uv is 0.12.13 and Poppler
`pdftotext`/`pdftoppm` are 25.08.0. The isolated lock resolves RenderCV
2.8, Typst Python binding 0.15.0, rendercv-fonts 0.5.1, Playwright 1.62.0
and pypdf 6.18.1. RenderCV is MIT licensed; rendercv-fonts is MIT; typst-py
is Apache-2.0; Playwright is Apache-2.0; pypdf is BSD-3-Clause. The exact
transitive set and hashes are in `experiments/renderer/uv.lock`.

RenderCV's official CLI supports `rendercv render`, Typst output and explicit
PDF/PNG paths ([CLI reference](https://docs.rendercv.com/user_guide/cli_reference/));
RenderCV's documented pipeline is YAML → validated model → template → Typst
→ PDF ([developer guide](https://github.com/rendercv/rendercv/blob/main/docs/developer_guide/understanding_rendercv.md)). Typst's PDF compiler and
Playwright's `page.pdf(format="A4")` were used as documented
([Typst PDF reference](https://typst.app/docs/reference/pdf/),
[Playwright PDF API](https://playwright.dev/python/docs/api/class-page#page-pdf)).

Setup friction was low for the isolated Python packages. Chromium setup was
not possible on this host: `experiments/renderer/.venv/bin/python -m
playwright install chromium` returned `ERROR: Playwright does not support
chromium on mac13`. No unsupported browser was downloaded. Consequently the
HTML/Playwright PDFs, raster previews and browser-side security checks are
blocked and are not treated as passes.

## Same-content comparison

The fixtures are generated from the approved TASK-004 `DocumentPlan` compiler;
RenderCV and HTML receive the same visible claim strings. `short`,
`german-unicode`, `long-wrapping`, `two-page`, and `hostile-text` are CV plans;
`letter` is a separate synthetic feasibility fixture. The YAML adapter emits
only neutral claim tokens. After RenderCV generates the local template, each
token is replaced with a Typst string literal (`#text("…")`), so candidate
text cannot become Typst markup, `#include`, `#read`, links, or other commands.
The HTML adapter uses `html.escape` for text nodes.

| Fixture | RenderCV/Typst | Pages | A4 media box | PDF SHA-256 | Poppler/pypdf claim prefixes in order | Unicode | HTML/Playwright |
|---|---:|---:|---|---|---|---|---|
| short | pass | 1 | 595.276 × 841.89 pt | `638716bbf72b110a0cfc08b967decf2b2ad3f1f6852c4eab5c65f7e4d5b62fcc` | yes | yes | blocked: Chromium unavailable |
| two-page | pass | 2 | 595.276 × 841.89 pt | `49fd00f3a029f008c118ca929d5c92bda3c51a212c246d728100b505f35c465f` | yes | yes | blocked: Chromium unavailable |
| german-unicode | pass | 1 | 595.276 × 841.89 pt | same as short | yes | `Größe Ä Ö Ü ß` preserved | blocked: Chromium unavailable |
| long-wrapping | pass | 1 | 595.276 × 841.89 pt | `1acd1db82580598124be102dda32f8fc370e9c330f779899ea85454a3edb1eee` | yes | yes | blocked: Chromium unavailable |
| hostile-text | pass | 1 | 595.276 × 841.89 pt | `b9128bf61689564ee97756d2688855930a3a4aadc5b9ae617ccacd3a2132e0dc` | yes | yes | blocked; source escaped markup and had no `href` |
| synthetic letter | pass | 1 | 595.276 × 841.89 pt | `068b5aa70299005eb324e06654e231bded57644656d76864208325a77087317f` | key text present | n/a | not attempted because candidate is blocked |

Poppler `pdftotext -layout` and pypdf both ran for each RenderCV PDF. Exact
long-line substring checks can fail where a PDF extractor inserts line breaks;
the bounded claim prefixes remained present and in document order. No expected
short claim prefix was missing. The same approved plan was not allowed to
silently omit content or reduce the 11pt body size.

## Raster and visual findings

`pdftoppm -png -r 110` rasterized every RenderCV page. I inspected all seven
pages at:

- `artifacts/renderer/task-005/outputs/rendercv/short/output-1.png`
- `artifacts/renderer/task-005/outputs/rendercv/two-page/output-1.png` and `output-2.png`
- `artifacts/renderer/task-005/outputs/rendercv/german-unicode/output-1.png`
- `artifacts/renderer/task-005/outputs/rendercv/long-wrapping/output-1.png`
- `artifacts/renderer/task-005/outputs/rendercv/hostile-text/output-1.png`
- `artifacts/renderer/task-005/outputs/rendercv/letter/letter-1.png`

The A4 content stayed inside the margins, long text wrapped, German glyphs
rendered, and no clipping or missing glyphs were visible. The two-page fixture
kept all sections and reading order but leaves substantial blank space on page
2 because the language section follows the stress content. That is a layout
trade-off to address in a later design task; this experiment did not shrink
or remove content to improve the page count.

The two-page output is exactly two pages; short/unicode/long-wrapping/hostile
are one page; and the synthetic letter is one page. This is a measurement of
these fixtures only, not a pagination guarantee.

## Security checks and limits

- RenderCV generation ran in `/usr/bin/sandbox-exec` with `(deny network*)`.
  A controlled local HTTP server containing `SECRET_NETWORK_SENTINEL` was
  probed by a sandboxed child and returned `Operation not permitted`; the
  sentinel was not exposed.
- Typst compiled with the local RenderCV package path, only bundled
  rendercv-fonts directories, and `ignore_system_fonts=True`. No remote
  package or authenticated browser profile was used.
- The hostile plan included `<script>`, a Typst include/read, a Markdown URL,
  an expression and a traversal sentinel. The RenderCV PDF contains those as
  literal text, not executed markup; the local file sentinel content was not
  recovered. The HTML source contains escaped `<script>` text and no `href`.
- Playwright's route-abort hook is present in the adapter, but Chromium could
  not launch on macOS 13. Browser request interception, HTML PDF extraction,
  HTML raster inspection and browser resource probes are therefore **blocked,
  not observed passes**.
- The harness does not claim a formal Typst sandbox or a complete filesystem
  policy. It uses a trusted local template/font package and escaped scalar
  insertion; a production adapter would need an independently reviewed
  process policy and fixture suite.

## Proposed decision

**Proposed backend: RenderCV/Typst, conditional on independent review.** It is
the only candidate that rendered the complete synthetic plans on this laptop,
produced A4 PDFs, preserved Unicode and reading order, passed the hostile
literal-boundary and network-denial checks, and demonstrated a one-page letter
route. The trade-offs are the additional template API surface, visible
whitespace on the stress page, and the requirement that production code retain
the post-template literal insertion boundary and pinned local fonts. The
HTML/Playwright candidate remains an unverified alternative because its
Chromium runtime cannot be installed on this OS; it must not be silently
selected later.

This is a proposed decision only. ADR-004 remains **PROPOSED / SPIKE
REQUIRED** until a separate reviewer accepts the experiment and the supervising
engineer records the backend choice. If independent review rejects the
RenderCV security or layout boundary, the explicit gate before TASK-022 is to
reconsider ADR-004; no second backend is silently introduced.

The generated sample PDF is
`artifacts/renderer/task-005/outputs/rendercv/short/output.pdf`; its raster
preview is next to it as `output-1.png`. These paths are ignored and are
reproducible from the commands above.
