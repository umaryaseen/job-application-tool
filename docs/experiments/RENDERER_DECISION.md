# TASK-005 renderer experiment decision

Date: 2026-09-12
Task branch: `task/005-renderer-experiment`
Base: `82deb141f84c59d86da78f68f06c4e35dfc339c0` (approved TASK-004 merge)

This report records an experiment, not a production backend approval. All
claims and letter text are synthetic. Generated PDFs, PNGs, HTML, logs and
sentinels are under the ignored `artifacts/renderer/task-005/` directory.

## Reproduction and environment

```sh
export PATH="$HOME/.local/bin:$PATH"
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

| Fixture | RenderCV/Typst | Pages | A4 media box | PDF SHA-256 | Complete Poppler/pypdf content | Unicode | HTML/Playwright |
|---|---:|---:|---|---|---|---|---|
| short | pass | 1 | 595.276 × 841.89 pt | `638716bbf72b110a0cfc08b967decf2b2ad3f1f6852c4eab5c65f7e4d5b62fcc` | yes (both) | yes | blocked: Chromium unavailable |
| two-page | pass | 2 | 595.276 × 841.89 pt | `49fd00f3a029f008c118ca929d5c92bda3c51a212c246d728100b505f35c465f` | yes (both) | yes | blocked: Chromium unavailable |
| german-unicode | pass | 1 | 595.276 × 841.89 pt | same as short | yes | `Größe Ä Ö Ü ß` preserved | blocked: Chromium unavailable |
| long-wrapping | pass | 1 | 595.276 × 841.89 pt | `1acd1db82580598124be102dda32f8fc370e9c330f779899ea85454a3edb1eee` | yes (both) | yes | blocked: Chromium unavailable |
| hostile-text | pass | 1 | 595.276 × 841.89 pt | `b9128bf61689564ee97756d2688855930a3a4aadc5b9ae617ccacd3a2132e0dc` | yes (both) | yes | blocked; source escaped markup and had no `href` |
| synthetic letter | pass | 1 | 595.276 × 841.89 pt | `068b5aa70299005eb324e06654e231bded57644656d76864208325a77087317f` | yes (both) | n/a | not attempted because candidate is blocked |

Poppler `pdftotext -layout` and pypdf both ran for each RenderCV PDF. The
corrective runner compares the complete ordered content oracle, including the
trusted section headings, after only the documented Unicode/layout
normalization. Every CV fixture matched the complete oracle in both
extractors; no content was accepted by prefix-only matching. The same approved
plan was not allowed to silently omit content or reduce the 11pt body size.

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

**Proposed current-laptop backend: RenderCV/Typst, conditional on independent
review.** It is the only backend that was feasible to execute on this laptop:
all synthetic CV fixtures matched their complete ordered content oracle in both
Poppler and pypdf, and the one-page synthetic letter rendered. This is a
feasibility result for this macOS 13 environment, not a comparative-quality,
cross-platform or HTML/Playwright compatibility claim. The HTML/Playwright
candidate remains blocked because its supported Chromium runtime could not be
installed on this host; its layout and security behavior remain untested.

The trade-offs are the additional template API surface, visible whitespace on
the stress page, and the requirement that production code retain the
post-template literal insertion boundary and pinned local fonts. ADR-004
remains **PROPOSED / SPIKE REQUIRED** until a separate reviewer accepts the
qualification and the supervising engineer records the backend choice. If
RenderCV fails a mandatory content, security or visual gate, the result is no
backend and TASK-006 remains blocked.

The generated sample PDF is
`artifacts/renderer/task-005/outputs/rendercv/short/output.pdf`; its raster
preview is next to it as `output-1.png`. These paths are ignored and are
reproducible from the commands above.

## Corrective review findings

The independent review at `f91357338fcaf02ba6f5492ad598d258ad2cc121`
reproduced F-001. Before correction, Poppler output for `long-wrapping`
contained a soft-hyphen (`U+00AD`) line-break artifact in
`deter<U+00AD>\nministic`; pypdf represented date hyphens as
`2022<U+00AD>01`; the hostile pypdf output split the URL as
`https:/ /\nexample.invalid`. The old prefix check passed while the complete
strings differed. The underlying Typst PDF contained the full claim; the loss
was extractor representation, not adaptation or layout.

The corrective oracle now applies NFC, converts a soft hyphen between digits
back to a date hyphen, removes soft hyphens and their line-break whitespace,
repairs only an extractor-split `http://` or `https://` scheme, and collapses
remaining whitespace. It does not remove or rewrite punctuation, digits,
units, qualifiers, negation or words. It compares the complete ordered
sequence of trusted headings and claims in both Poppler and pypdf. All five CV
fixtures and the letter matched in both extractors. Negative controls for
suffix removal, qualification change, duplication, reordering and unexpected
content were rejected for every measured PDF. A failed complete-content check
now marks the candidate `failed`; the overall experiment is `blocked` here
because HTML/Playwright cannot run.

## ADR-004 qualification amendment for independent review

This amendment narrows the proposed decision to a feasible backend for the
current laptop. The planned two-engine quality comparison was not completed:
Playwright 1.62.0 installed as a Python package, but Chromium installation on
macOS 13.6.9 x86_64 failed exactly with `ERROR: Playwright does not support
chromium on mac13`. No unsupported browser workaround was used. HTML/CSS
layout, PDF extraction, raster output and browser resource controls therefore
remain untested; the blocked candidate and reproduction commands remain in
this report and `experiments/renderer/README.md`. No cross-platform or
comparative-quality claim is made.

Reconsider ADR-004 when a supported Playwright target is available and run the
full same-content experiment, if RenderCV fails a mandatory content, Unicode,
visual, security or maintenance gate, or if the literal-boundary/local-font
adapter becomes too costly to maintain. Until an independent reviewer and the
supervising engineer accept this qualification, ADR-004 stays PROPOSED / SPIKE
REQUIRED; if RenderCV fails, recommend no backend and keep TASK-006 blocked.

The complete-content oracle is now checked in independently at
`tests/fixtures/rendering/expected/`. It is not generated from extracted
output or from the runner's section traversal. The original extractor
fragments are preserved in `tests/fixtures/rendering/extraction_failures.json`.
The runner exits 1 for a measured mandatory failure and exits 2 for the
current blocked-browser comparison; this laptop run returned 2 with all
RenderCV/Typst and letter checks passing.


## Subsequent architecture decision — 2026-09-13

The proposal above is now accepted for the current laptop through the explicit [ADR-004 amendment](../adr/ADR-004.md) and independent review addendum. TASK-006 is READY for implementation after normal branch integration. This supersedes the prior awaiting-decision language only: the measured two-engine comparison remains incomplete/blocked (exit 2), and Playwright remains untested. Reconsider it on target-environment change, unmet RenderCV requirements or excessive maintenance. No comparative superiority or production-adapter approval is implied.
