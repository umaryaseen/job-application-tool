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

## Re-review of corrections and ADR-004 qualification

Reviewer: Codex (independent reviewer)  
Date: 2026-09-12  
Corrected implementation: `62eddb346995c8ef7ade694d45775779f5017c36`  
Documentation head inspected: `c13ecb2cbaa875795dfd8c4f0c7e0445ea7208b4`

Ancestry and clean state were verified. The delta after the corrected implementation is documentation-only. F-001 is **addressed**: the oracle is generated from validated plans before rendering, and Poppler and pypdf complete-content comparisons pass. Normalization removes only extraction line-break artifacts/soft hyphens and preserves meaningful values; negative controls for suffix, qualification, duplication, order and unexpected content all return failures. RenderCV output passed all mandatory gates, including A4/pages, Unicode, hostile input, sandboxed compilation, and raster generation. The short and german-unicode hashes are identical because their plans are identical; required Unicode characters are covered by the synthetic cases.

F-002 is **qualified follow-up**: ADR-004's selection of RenderCV is acceptable for this laptop because every RenderCV gate passes, while Playwright remains explicitly BLOCKED/UNTESTED due to the macOS 13 Chromium installation failure. The experiment reports overall status `blocked`, so blocked HTML cannot mask a RenderCV failure. The qualification does not claim comparative superiority or cross-platform support. The remaining gate before production adapter work is a supported Playwright rerun (or explicit future ADR update); TASK-006 must not begin from the blocked comparison.

## Re-review verification

- `/Users/apple/.local/bin/uv sync --locked`; Python 3.12.14; baseline pytest **31 passed**; Ruff check/format and mypy passed.
- Renderer environment lock sync passed; real experiment completed with RenderCV/Typst and letter success, Poppler+pypdf complete matches, all negative controls rejected, sandboxed/network-denied probe, and raster pages generated for every case. Playwright installation failure was reproduced and retained as BLOCKED (exit 2 semantics recorded by the runner/report).

**Verdict: APPROVED WITH FOLLOW-UP.**
