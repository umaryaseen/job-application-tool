# TASK-005 Independent Review

Reviewer: Codex (independent reviewer)
Date: 2026-09-12
Implementation: `dcc30ea05e7d51adbd384fe700c57cf459922fd1`
Documentation head inspected: `4f5008f49e85f25d6215b4e00e4d0a53ee69bf2f`

## Verdict

**CHANGES REQUIRED**

The documentation commits `03387eec0328687198137464b65e492af45c2982` and `4f5008f49e85f25d6215b4e00e4d0a53ee69bf2f` are descendants of the implementation and contain documentation-only changes. However, independent reproduction shows the experiment's content checks accept prefixes while losing complete claim content.

### F-001 — complete text preservation is not established (blocking)

`long-wrapping` and `hostile-text` report non-empty `expected_claims_missing_from_pdftotext` while `claim_prefixes_missing_from_pdftotext` is empty. A suffix/qualification can therefore be lost while the check passes its prefix/order criteria. This directly fails the requested complete-content gate.

Corrective task: replace prefix-only acceptance with complete expected claim sequence comparison for Poppler and pypdf, using only documented whitespace/Unicode normalization that preserves punctuation, numbers, units, negation and qualifiers. Add a negative control that alters only a claim suffix and assert rejection.

### F-002 — incomplete backend comparison (blocking)

Playwright is correctly recorded BLOCKED because Chromium is unavailable on macOS 13.6.9. Consequently HTML/CSS cannot be accepted as a mandatory comparable backend until the documented environment gate is met or ADR-004 explicitly qualifies the comparison. Keep the blocked status and do not use an unsupported workaround.

## Verification

`/Users/apple/.local/bin/uv sync --locked` passed; Python 3.12.14; baseline pytest 28 passed; Ruff check/format and mypy passed (21 source files). Renderer experiment sync passed, cases were prepared, and the runner completed RenderCV/Typst, letter, Poppler/pypdf, raster and network-denial probes. RenderCV and final Typst compilation reported sandboxed success with A4 output (short 1 page, two-page 2 pages, letter 1 page). Every raster page was produced; generated outputs were inspected. Playwright reproduction failed with the recorded missing Chromium executable and remained BLOCKED. The standalone network probe was denied; the runner records RenderCV sandboxing, but HTML was not executed.

The short and german-unicode PDFs have identical hashes because their fixture plans render identical content; this does not demonstrate distinct Unicode coverage. The inspected hostile fixture includes markup/sentinel content and the runner reports escaping/sentinel absence. The implementation tests cover token escaping and replacement mechanics, but the complete extraction failure above remains blocking. Review documentation and progress were updated without implementation changes.
