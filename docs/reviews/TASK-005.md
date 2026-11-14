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

`uv sync --locked` passed; Python 3.12.14; baseline pytest 28 passed; Ruff check/format and mypy passed (21 source files). Renderer experiment sync passed, cases were prepared, and the runner completed RenderCV/Typst, letter, Poppler/pypdf, raster and network-denial probes. RenderCV and final Typst compilation reported sandboxed success with A4 output (short 1 page, two-page 2 pages, letter 1 page). Every raster page was produced; generated outputs were inspected. Playwright reproduction failed with the recorded missing Chromium executable and remained BLOCKED. The standalone network probe was denied; the runner records RenderCV sandboxing, but HTML was not executed.

The short and german-unicode PDFs have identical hashes because their fixture plans render identical content; this does not demonstrate distinct Unicode coverage. The inspected hostile fixture includes markup/sentinel content and the runner reports escaping/sentinel absence. The implementation tests cover token escaping and replacement mechanics, but the complete extraction failure above remains blocking. Review documentation and progress were updated without implementation changes.

## Re-review of corrections and ADR-004 qualification

Reviewer: Codex (independent reviewer)  
Date: 2026-09-12  
Corrected implementation: `62eddb346995c8ef7ade694d45775779f5017c36`  
Documentation head inspected: `c13ecb2cbaa875795dfd8c4f0c7e0445ea7208b4`

Ancestry and clean state were verified. The delta after the corrected implementation is documentation-only. F-001 is **addressed**: the oracle is generated from validated plans before rendering, and Poppler and pypdf complete-content comparisons pass. Normalization removes only extraction line-break artifacts/soft hyphens and preserves meaningful values; negative controls for suffix, qualification, duplication, order and unexpected content all return failures. RenderCV output passed all mandatory gates, including A4/pages, Unicode, hostile input, sandboxed compilation, and raster generation. The short and german-unicode hashes are identical because their plans are identical; required Unicode characters are covered by the synthetic cases.

F-002 is **qualified follow-up**: ADR-004's selection of RenderCV is acceptable for this laptop because every RenderCV gate passes, while Playwright remains explicitly BLOCKED/UNTESTED due to the macOS 13 Chromium installation failure. The experiment reports overall status `blocked`, so blocked HTML cannot mask a RenderCV failure. The qualification does not claim comparative superiority or cross-platform support. The remaining gate before production adapter work is a supported Playwright rerun (or explicit future ADR update); TASK-006 must not begin from the blocked comparison.

## Re-review verification

- `uv sync --locked`; Python 3.12.14; baseline pytest **31 passed**; Ruff check/format and mypy passed.
- Renderer environment lock sync passed; real experiment completed with RenderCV/Typst and letter success, Poppler+pypdf complete matches, all negative controls rejected, sandboxed/network-denied probe, and raster pages generated for every case. Playwright installation failure was reproduced and retained as BLOCKED (exit 2 semantics recorded by the runner/report).

**Verdict: APPROVED WITH FOLLOW-UP.**


## Architecture gate clarification — 2026-09-13

Scope: independent assessment of the supervising engineer's adoption proposal,
not a new runtime review. Starting review commit:
`aa244a66fb75d393b2dcb1f8c215d0df40fffb86`; implementation remains
`62eddb346995c8ef7ade694d45775779f5017c36`. Clean branch state and ancestry
were verified; intervening changes are documentation-only.

**Decision: accept the explicit ADR-004 amendment. TASK-006 is READY for
current-laptop implementation, after normal reviewed-branch integration.**
The earlier statement that a supported-browser comparison must precede production
adapter work is superseded by this reasoned amendment, not silently deleted.
The TASK-005 verdict remains **APPROVED WITH FOLLOW-UP**; F-001's recorded
disposition is unchanged. F-002 becomes nonblocking reconsideration owned by the
supervising engineer on target-environment change, unmet RenderCV requirements,
or excessive maintenance.

The original TASK-005/ADR-004 did require a two-engine experiment, so an amendment
is necessary. No concrete product requirement in A08–A14 or ADR-013/015 makes a
successful Chromium run a prerequisite to implementing RenderCV. R1 844–859 and
R3 695–707 recommend different pipelines; R2 470–495 requires output validation
and multiple extractors, not two rendering backends. Recorded RenderCV results
in the prior review provide feasibility evidence for this laptop. A Chromium run
would add comparative layout/install/maintenance evidence, but cannot validate
RenderCV's security or compatibility. We accept that comparative uncertainty;
we do not waive any selected-engine requirement.

ADR-004 is accepted only for this environment. The historical comparison is still
BLOCKED/UNTESTED with runner exit 2; no claim of comparative superiority, portability,
or a completed two-engine comparison follows. TASK-006/007 must independently
validate the production adapter, including the process policy, literal insertion,
asset bounds, cleanup, full text and complete Unicode corpus. Changed environments
require fresh selected-backend validation before support is claimed. Future letter
work must validate its maintained route; the feasibility spike is not that approval.

Verification for this documentation-only clarification: read TASK-005/006, ADR-004,
ADR-013/015, acceptance matrix, source-register sections R1 844–859, R2 470–495,
R3 695–707, experiment report and review protocol. Inspected runner exit mapping
(0=ok, 1=failed, 2=blocked). Prior measured results are cited as historical evidence;
no renderer, browser installation, raster review or runtime suite was rerun in
this turn, and no new runtime acceptance claim is made. Documentation whitespace,
scope and staged-content safeguards are checked before commit.
