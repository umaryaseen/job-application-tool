<!-- Historical local document, preserved from pre-sync TASK-009 HEAD.
Use docs/PROGRESS.md and docs/REVIEW_HANDOFF.md for current instructions. -->

# Progress — authoritative implementation state
M1-FIX-005 literal-hyphen correction: **APPROVED** on `task/009-m1-fix-005`, implementation
`5743a8743b4ab49d0c0026e83812b9e5fe62eea9`. The trusted PDF boundary now keeps
ordinary ASCII-hyphenated compounds atomic while preserving their literal
characters, and fails closed when an atomic compound exceeds the available A4
content width. Synthetic summary/project regressions pass through Poppler and
pypdf; no personal output was regenerated. Baseline-r0008 and its failed QA
remain historical. See `docs/reviews/M1-FIX-005.md`.
TASK-009 baseline resume after M1-FIX-005: **IMPLEMENTED — TECHNICAL QA PASS,
APPLICANT APPEARANCE APPROVED, PDF/TXT CONTENT APPROVAL PENDING** on
`task/009-personal-baseline`. Merge
`35309ea` integrated the approved correction. A fresh plan was compiled from
the latest reviewed private profile and the next private baseline-r0009 was
built through `jae build-cv`; baseline-r0008 and all earlier outputs remain
historical. Independent Poppler/pypdf content, identity, scope, contact/URL,
Unicode, punctuation, A4, geometry, pagination and file checks pass. Both
raster pages received a separate technical visual observation. The applicant
approved the appearance and layout of the exact PDF; the private
appearance-only record is `reviews/applicant-appearance-approval-r0001.json`.
PDF/TXT content approval, final artifact approval and export remain pending.
Private content and artifact hashes remain outside Git.
TASK-009 personal baseline resume: **IMPLEMENTED — TECHNICAL QA BLOCKED** on
`task/009-personal-baseline` after integrating approved M1-FIX-004 with merge
`8ed7429cd114ac7c6e8e9d8c70304b51c96b748c`. A fresh private plan and
baseline-r0008 were generated from the current reviewed private profile. The
PDF is visually readable and identity/scope/geometry checks pass, but mandatory
complete ordered Poppler/pypdf checks fail on two natural source-hyphen line
breaks (`full-stack` and `cost-forensics`) under the changed page composition.
The exact private PDF, TXT, both extractor outputs, failed QA and technical
raster observation remain outside Git; no final applicant approval or export
was recorded. See the current M1 record for the reproduction and gate.
M1-FIX-004 F-01 corrective implementation: **APPROVED** on `task/009-m1-fix-004`; implementation `c7d957b08d24e54fb88eda55e3edb87b8a410bc6` follows preserved review head `4c0c757111547906623f32da3d0729ef7053e6c2`. It rejects non-fitting contact URLs before PDF publication and preserves fitting URLs under both extractors. See `docs/reviews/M1-FIX-004.md`; TASK-010 remains blocked pending applicant acceptance.
M1-FIX-004 independent review: **CHANGES REQUIRED** for F-01 long ContactUrl extraction. Reviewed implementation `d0822deb1e7aeb89dd14f5635b16ca5603d729eb`; branch head `cd56bd1c5954d61b6a6723b192f7ead177107a14` is documentation-only after implementation. See `docs/reviews/M1-FIX-004.md`; TASK-010 remains blocked.
TASK-009 contact-layout correction `3a4d8a8c22ddeaa6f68f1bc88035dd414d6b7ac2` independently reviewed and APPROVED; branch documentation head `4967f2ae8564f152f3c310213e6d240318ebd335`. See `docs/reviews/M1-CONTACT-CORRECTION.md`.
Independent review of M1 profile-digest correction `bc7439a047d5072a95668ebc8fa884b2acd7ae48` approved; reviewed head `2c523d525c23f2dedd62805c36d29747932ac8a9` has documentation-only tail. See `docs/reviews/M1-DIGEST-CORRECTION.md`.

M1-FIX-003 implementation `1291ba94fbffdde1d89f5fba7b5ac78c7ebd5ab8` was independently reviewed and APPROVED at `100b955cfe26a7d8ccba032e1fe867e5c294cf7a`; see `docs/reviews/M1-FIX-003.md`. TASK-010 remains gated by subsequent milestone planning.

Last updated: 2026-09-22. TASK-001–004 are APPROVED; TASK-005 is APPROVED WITH FOLLOW-UP under amended ADR-004; TASK-006–008 are APPROVED. M1-FIX-004 F-01 is APPROVED; TASK-009 remains open pending applicant final artifact acceptance.

## Environment and completed work

- Read all three supplied research reports, including examples, schema and roadmap; exact copies identified in SOURCE_REGISTER/research-manifest.
- Compared consensus, conflicts, assumptions, questionable examples and postponements; checked relevant primary upstream documentation.
- Independent research audit identified insufficient evidence-membership checks, optional provenance schema fields, unsafe date/metric semantics and mismatched scope estimates. Those are addressed in the architecture and ADRs.
- Historical planning record: created repository-ready documents, 16 ADRs, 35 scoped task files, acceptance/test matrix, privacy/dependency guidance, review protocol and local Codex handoff. This describes the planning-era cloud package, not the current laptop implementation state.
- Created `.gitignore` before any career data. Historical planning snapshot: no real applicant data, credentials, executable application code or generated personal CV existed in that snapshot; current implementation state is described in the task entries below.
- Initialized a cloud-workspace planning Git repository with an exclusions commit, a planning branch and normal corrective history. Independent reviewer approved corrected planning head `bea4cbc1a0144b6d3f4190e9b29722546ed46670` on 2026-09-09; [M0 review](../reviews/M0.md) records the initial findings and resolution. This is not the laptop repository.
- Historical planning environment note: the initial package checks ran in a cloud Linux workspace with Git 2.51.1 and no laptop bridge/`gh`. Current laptop verification is recorded in each task entry; no GitHub login, repository creation or push occurred.

## State table

| Milestone / task | State | Evidence / next action |
|---|---|---|
| M0 research | COMPLETE | Three complete reports and independent research audit |
| M0 architecture | APPROVED | Independent exact-head review of bea4cbc; see reviews/M0.md |
| M0 package | VERIFIED | Clean bundle restoration, tracked-file byte comparison, archive CRC and source identities passed; export-specific hashes in PACKAGE_VERIFICATION.json |
| Laptop repository | RESTORED | Bundle cloned and verified locally |
| Private GitHub repository | NOT CREATED | Native `gh` authentication is invalid; no remote configured |
| TASK-001 | APPROVED | Independent verification gate resolved (uv located locally); see reviews/TASK-001.md |
| TASK-002 | APPROVED | Strict profile/fact schemas and exported JSON Schema; see reviews/TASK-002.md |
| TASK-003 | APPROVED | Deterministic evidence graph, immutable capture checks and local review receipts; see reviews/TASK-003.md |
| TASK-004 | APPROVED | See reviews/TASK-004.md |
| TASK-005 | APPROVED WITH FOLLOW-UP | Current-laptop RenderCV accepted by ADR-004 amendment; comparison remains blocked, exit 2 |
| TASK-006 | APPROVED | Production RenderCV/Typst adapter; see reviews/TASK-006-rereview.md |
| TASK-007 | APPROVED | PDF/ATS QA checks; see reviews/TASK-007.md |
| TASK-008 | APPROVED | Private snapshots and current-eligibility export; see reviews/TASK-008.md |
| TASK-009 / M1 | IMPLEMENTED — APPROVED, APPLICANT APPEARANCE APPROVED, PDF/TXT CONTENT PENDING | M1-FIX-005 is independently approved; baseline-r0009 passes technical QA and has appearance-only approval; final PDF/TXT content approval and export remain gated; baseline-r0008 and its prior failed QA remain preserved |
| TASK-010–016 / M2 | NOT STARTED | EN/DE requirements and matrix |
| TASK-017–020 / M3 | NOT STARTED | Tested tailoring MVP |
| TASK-021–023 / M4 | NOT STARTED | Letters/tracker |
| TASK-024–035 | DEFERRED / NOT STARTED | Optional extensions and later design only |

## Tests and validation

Application unit/integration/model tests and the TASK-006 production rendering tests are implemented incrementally; exact current results are recorded in the TASK-006 entry below. No PDF support or ATS score is claimed beyond the checked synthetic fixtures.

### TASK-001 implementation

- Branch: `task/001-project-bootstrap`; base: `8939d9e8ec5af2035ca6b5a86c94ae74efedbabb`.
- Adds a Python 3.12 package and `jae` entry point, standard-library private-root/path validation, synthetic CLI and repository-policy tests, Ruff/mypy/pytest configuration, locked dev dependencies, a staged-file safeguard, and minimal read-only-permission CI.
- The required `JAE_DATA_DIR` is absolute, existing, non-symlink, outside the repository; path traversal and symlink traversal are rejected. No personal data or application domain schema was added.
- Environment: macOS 13.6.9 x86_64; uv 0.12.13 with managed CPython 3.12.14. `uv sync --locked --group dev` passed and installed pytest 8.4.1, Ruff 0.12.11, and mypy 1.17.1.
- Checks: `uv run pytest` — 7 passed; `uv run ruff check .` — passed; `uv run ruff format --check .` — passed; `uv run mypy src` — no issues in 3 source files. `jae --version` printed `jae 0.1.0`; missing `JAE_DATA_DIR` makes `jae config-check` exit 2.
- GitHub remote setup is blocked by invalid native `gh` authentication; no remote URL or privacy claim is made. Rendering, schema, model, database, scraping, UI and application-submission checks are intentionally not implemented or run.

Planning checks passed for required files, 256 internal Markdown links at the reviewed head, 35 acyclic task dependencies, three source identities, and 14 private-path exclusions. Independent review required immutable support captures and explicit export expiry/source-eligibility rules; the corrections were independently re-reviewed and APPROVED at bea4cbc. Application behavior remains unimplemented. The supplied archive is a planning handoff, not a working MVP or a laptop installation. Final artifact checks are recorded separately after bundle creation to avoid circular Git/hash metadata.

## Open gates

1. TASK-006 is READY after normal integration of the reviewed TASK-005 branch; no merge or implementation occurred in this clarification.
2. ADR-004 accepts current-laptop RenderCV selection. TASK-006/007 must still validate the production adapter; Playwright comparison is reconsideration evidence, not a prerequisite.
3. TASK-009 obtains actual reviewed career data and accepts a genuine baseline CV. Chat memory/research templates are not evidence.
4. Optional provider/model/data choices remain deferred and do not block deterministic implementation.

## Per-task update format

Record task ID/state; branch; base/head or containing commit reference; actual modules/behavior; dependency versions; exact commands and exit results; skipped/unrun checks; security/privacy notes; independent review verdict/report; pending applicant input; next unblocked task. Use IMPLEMENTED — AWAITING REVIEW before independent approval.

Do not change historical submitted snapshots when facts improve. Correct canonical data and generate a new version. Keep implementation and review status synchronized with Git, not aspirations.


Independent TASK-001 review: CHANGES REQUIRED at `cfaeaf1eb9eb609f89f4cbc74297066572c56a95` for F-001 (hook not enabled) and F-002 (explicit root bypass). The review is preserved in [TASK-001 review](../reviews/TASK-001.md).

### TASK-001 corrective implementation

- F-001: `scripts/install_hooks.sh` provides an idempotent repository-local setup step. It sets only local `core.hooksPath`, preserves and reports conflicting hook configuration, and was applied locally; `git config --local --get core.hooksPath` returns `.githooks` and `.githooks/pre-commit` is executable.
- F-001 regression coverage now creates a fresh temporary Git repository, installs the hook, makes a safe real commit, and verifies real Git commits reject both staged synthetic secrets and prohibited private paths. The secret case changes the working-tree copy after staging, proving the hook scans the index.
- F-002: explicit roots passed to `safe_private_path` use the same absolute, existing-directory, non-symlink, repository-boundary validator as `JAE_DATA_DIR`. Tests cover valid roots, symlink roots, file roots, repository roots, traversal and symlink escapes.
- Corrective verification: `uv sync --locked` passed; `uv run python --version` reported Python 3.12.14; `uv run pytest` reported 10 passed; Ruff check and format check passed; mypy reported no issues in 3 source files. No lockfile regeneration was needed.

Re-review of corrective head `a1e7d43c2fd387c2f5b048a42ac59b69758b4aaa`: F-001 and F-002 are addressed by `cf60afb`; however required uv/Python 3.12 verification remains an unresolved gate because uv is unavailable in the review environment. Verdict: CHANGES REQUIRED. See the appended re-review in `docs/reviews/TASK-001.md`.

### TASK-001 independent verification gate (resolved)

Diff `a1e7d43..b2fce65` (current `HEAD`) is documentation-only (`docs/PROGRESS.md`, `docs/reviews/TASK-001.md`); no further implementation review was required. On the laptop checkout (`<repository>`, Darwin 22.6.0 x86_64), `uv` was found at `uv` (not on `PATH` in the review shell) and used by absolute path; no code/dependency/lockfile change was needed. Independently executed: `uv sync --locked` (resolved/checked, no changes needed), `uv run python --version` (`Python 3.12.14`), `uv run pytest` (10 passed), `uv run ruff check .` (all checks passed), `uv run ruff format --check .` (7 files already formatted), `uv run mypy src` (no issues in 3 source files). Hook activation and explicit-root regression tests were inspected and confirmed to exercise real `git commit` invocations and repository-boundary/symlink checks for both default and explicit roots. Verdict: **APPROVED**. Full detail in [TASK-001 review](../reviews/TASK-001.md).

### TASK-002 implementation

- Base: merge commit `6c00c9b` (`main` after approved TASK-001); branch: `task/002-profile-schemas`.
- Adds strict Pydantic 2.11.7 models for versioned profile revisions, stable IDs/revisions, typed dates and states, contacts, employment, education, skills, languages, authorization, credentials and decimal metrics.
- Adds mandatory evidence references, kind-specific source identities, immutable support-capture hashes, support bindings, hash-bound fact/evidence/variant approvals, duplicate-safe JSON loading, and checked-in JSON Schema export at `schemas/profile.schema.json`.
- Schema models intentionally do not resolve dangling references or prove provenance; graph-level validation remains TASK-003. Fixtures are synthetic and use reserved example domains.
- Verification so far: `uv sync --locked` passed; `uv run pytest` reported 17 passed; Ruff and mypy passed. Final full-suite results and commit hash will be recorded after the staged review and commit.

Independent TASK-002 review approved exact head `6cb81c04c139a18f571cc0f3dcc3281ee5ecf86a`. All required uv, Python 3.12, pytest (17 passed), Ruff, format, mypy and schema-drift checks passed. See `docs/reviews/TASK-002.md`.

### TASK-003 implementation

- Base: approved TASK-002 merge commit `1874f1cc0e07ed45ca291969b67f759d94f5f328`; implementation head: `b4526561620f5f829fcb32477ca33d2558788f28`; branch: `task/003-evidence-validation`; status: IMPLEMENTED — AWAITING REVIEW.
- Adds exact `(id, revision)` graph resolution, fact/evidence/variant support-scope checks, cycle/dangling/revoked/stale rejection, immutable support-capture verification, and source-file/repository pinning requirements for approved documentary and repository evidence.
- Adds `record_human_review`, which records the exact displayed payload and revision-bound digests. Provider/import approval fields do not satisfy the local review receipt requirement; the local review operation is the trust boundary for approvals. User attestations remain an explicitly identified source kind and do not require certificates.
- Adds synthetic adversarial coverage for unrelated IDs, wrong scopes, stale revisions, changed/missing captures, unpinned sources, generated output, and changed wording. JSON Schema was regenerated for the TASK-003 model additions.
- No new dependency was added; Pydantic 2.11.7 remains the only runtime dependency and the lockfile is unchanged.
- Verification: `uv sync --locked` passed; `uv run python --version` reported Python 3.12.14; `uv run pytest` reported 24 passed; `uv run ruff check .` passed; `uv run ruff format --check .` reported 22 files already formatted; `uv run mypy src` reported no issues in 16 source files. The local safeguard remains enabled at `.githooks` and the staged pre-commit check passed.
- Deterministic checks establish internal support integrity only; they do not establish the real-world truth of arbitrary prose. Rendering, LLM entailment, matching, snapshot/export, database, import adapters and TASK-004 remain out of scope.

### TASK-004 implementation

- Base: approved TASK-003 merge commit `faacbc5323d44d0ca7350356347b60dfb62984d0`; branch: `task/004-baseline-document`; status: IMPLEMENTED — AWAITING REVIEW.
- Adds a strict renderer-independent `DocumentPlan` with pinned profile digest, revision, explicit as-of date, locale, allowlisted section labels, exact fact/variant references, and required support-binding references.
- Adds deterministic baseline compilation for contacts, approved variants, employment, education, skills and languages. Employment and education retain typed date precision, unknown end dates render as `end date unknown`, ongoing dates render as `ongoing`, ties use stable fact IDs, and empty optional sections are omitted.
- Adds a validation boundary that reuses TASK-003 provenance checks, rejects altered plan digests, stale profiles, unsupported typed wording, arbitrary headline/skill text, wrong sections, unapproved revisions and mismatched support bindings. UTF-8 text output is produced only after validation.
- Synthetic expected output is checked independently at `tests/fixtures/documents/baseline.txt`; no PDF API, renderer backend, automatic rewriting, matching or artifact export was added. No dependency or lockfile change was needed.
- Implementation head: `d8427071d7cdaf145dcd9a5dc6c3a2fae43d5814`. Verification: `uv sync --locked` passed; Python 3.12.14; 28 tests passed; Ruff check and format checks passed; mypy passed with no issues in 21 source files; `.githooks` safeguard remained enabled. The generated text is a deterministic text-plan example only; it makes no PDF pagination or ATS compatibility claim.

Independent TASK-003 review approved implementation `b4526561620f5f829fcb32477ca33d2558788f28`; inspected branch head `ca252bad2987731671e3ba392a3f46c91d8739fc` contains documentation-only changes after implementation. uv/Python 3.12 checks passed: 24 tests, Ruff, format and mypy. See `docs/reviews/TASK-003.md`.

Independent TASK-004 review approved implementation `d8427071d7cdaf145dcd9a5dc6c3a2fae43d5814`; inspected branch head `b04e4f271384e3b57987d3f716a0920a38299046` differed only by documentation. Python 3.12/uv checks passed: 28 tests, Ruff, format and mypy. See `docs/reviews/TASK-004.md`.

### TASK-005 implementation

- Base: approved TASK-004 merge `82deb141f84c59d86da78f68f06c4e35dfc339c0`; branch: `task/005-renderer-experiment`; status: **IMPLEMENTED — AWAITING REVIEW**.
- Implementation commit: `dcc30ea` (full hash is recorded in the review handoff); documentation-only follow-up records the independent review prompt.
- Adds an isolated `experiments/renderer` lock and runner. The runner prepares the same validated synthetic TASK-004 `DocumentPlan` claims for RenderCV/Typst and HTML/CSS + Playwright, plus short, two-page, German-Unicode, long-wrapping, hostile-text and one-page synthetic letter fixtures. It does not add experiment packages to baseline runtime dependencies.
- RenderCV 2.8 + Typst 0.15.0 + rendercv-fonts 0.5.1 rendered every CV fixture offline under macOS `sandbox-exec` with local fonts, 11pt body text, 20mm margins and A4 media boxes. Measured pages: short 1, two-page 2, German-Unicode 1, long-wrapping 1, hostile-text 1, letter 1. Poppler 25.08.0 and pypdf 6.18.1 recovered claim prefixes in order; raster inspection covered all seven pages. The hostile scalar boundary preserved markup as literal text and did not recover the synthetic sentinel.
- Playwright 1.62.0 installed as an experiment dependency, but Chromium setup returned `ERROR: Playwright does not support chromium on mac13` on this macOS 13.6.9 host. HTML PDFs, browser raster output and browser-side probes are recorded as blocked, not passes. The HTML adapter still escapes text and aborts requests when a browser is available.
- A sandboxed local HTTP probe returned `Operation not permitted`; no network sentinel was exposed. RenderCV and Typst use local package/font paths only. Security findings and limitations are in `docs/experiments/RENDERER_DECISION.md`; ADR-004 remains PROPOSED / SPIKE REQUIRED pending independent review.
- Verification: `uv sync --locked` passed; `uv run python --version` reported Python 3.12.14; `uv run pytest` reported 28 passed; Ruff check passed; Ruff format check reported 30 files already formatted; `uv run mypy src` reported no issues in 21 source files; isolated `uv sync --project experiments/renderer --locked` passed; the local `.githooks` safeguard remains enabled. The experiment runner completed with all six synthetic RenderCV cases and the letter pass, five HTML candidate runs blocked by the unavailable browser, and the network probe blocked as intended.
- No applicant data, credentials, authenticated browser profile, UI, production renderer adapter, PDF export workflow, matching or TASK-006 work was added. The proposed RenderCV recommendation is conditional and is not an approval.

Next action: obtain an independent review of the exact TASK-005 commit and decide ADR-004; do not start TASK-006 before approval.

Independent TASK-005 review: CHANGES REQUIRED for implementation `dcc30ea05e7d51adbd384fe700c57cf459922fd1` (documentation head `4f5008f49e85f25d6215b4e00e4d0a53ee69bf2f`). Renderer reproduction exposed prefix-only extraction acceptance: long-wrapping and hostile-text lose complete claims while prefixes pass. Playwright remains correctly blocked by unavailable Chromium. See `docs/reviews/TASK-005.md`.

### TASK-005 corrective implementation (F-001/F-002)

- Status: **IMPLEMENTED — AWAITING REVIEW**. The original review at `f91357338fcaf02ba6f5492ad598d258ad2cc121` remains preserved; these corrections do not approve TASK-005.
- Corrective implementation commits: `4b2f3ea`, `180917a` and `62eddb3` (full hashes are pinned in the corrective review handoff); documentation-only follow-up records the latest corrective head.
- F-001 root cause: RenderCV/Typst preserved complete claim text, while Poppler and pypdf inserted extractor layout artifacts (soft hyphens in wrapped words and date separators, plus a split `https://`). The prefix-only check accepted those losses. The runner now compares an independently written ordered-content oracle containing static headings and all claims in full against both extractors.
- Normalization is narrow: Unicode NFC; date hyphen restoration only for a soft hyphen between digits; removal of soft hyphen line-break markers; repair of an extractor-split HTTP(S) scheme; and whitespace collapse. Punctuation, numbers, units, qualifiers, negation and words are not broadened or truncated.
- Negative controls reject suffix removal, qualification/metric changes, duplication, reordering and unexpected content. Any complete-content mismatch marks PDF generation unsuccessful. All five CV fixtures and the synthetic letter matched the complete oracle in both Poppler and pypdf; all negative controls returned rejection.
- F-002: ADR-004 and the experiment report now explicitly qualify the outcome as a feasible current-laptop RenderCV backend only. Playwright 1.62.0 package installation succeeded, but Chromium installation failed on macOS 13.6.9 with `ERROR: Playwright does not support chromium on mac13`; HTML/Playwright quality and security remain untested. No cross-platform or comparative-quality claim is made. Reconsideration triggers are a supported target environment, any unmet RenderCV mandatory gate, or excessive adapter maintenance. If RenderCV fails, no backend is recommended and TASK-006 remains blocked.
- Added baseline regression coverage for the content normalizer and mutation controls. The existing security, Unicode, sandbox and visual checks remain.
- Independently specified complete-content fixtures are checked in under `tests/fixtures/rendering/expected/`; the original extractor fragments remain in `tests/fixtures/rendering/extraction_failures.json`. The runner exits nonzero for a failed or blocked mandatory gate (this laptop returned 2 for blocked Chromium).

Next action: independent re-review of the focused corrective commits, then an ADR-004 decision by the supervising engineer. Do not start TASK-006.

TASK-005 corrective re-review approved with follow-up: corrected implementation `62eddb346995c8ef7ade694d45775779f5017c36`, documentation head `c13ecb2cbaa875795dfd8c4f0c7e0445ea7208b4`. Full Poppler/pypdf content oracle and negative controls pass; RenderCV mandatory gates pass. Playwright remains BLOCKED/UNTESTED on macOS 13, so ADR-004 is accepted only as a laptop qualification; supported-browser comparison remains a gate before production adapter work. See appended TASK-005 review.


### Current architecture decision — 2026-09-13

Supersedes the earlier pre-adapter browser gate: the supervising engineer proposal is independently accepted in ADR-004 and the TASK-005 review addendum. TASK-006 is **READY**, not started, subject to normal reviewed-branch integration. TASK-005 remains APPROVED WITH FOLLOW-UP; F-002 comparison evidence is now nonblocking and owned by the supervising engineer upon environment change, RenderCV requirement failure or excessive maintenance. Historical experiment status remains blocked/exit 2; Playwright remains untested. Production process isolation, complete content/Unicode and other TASK-006/007 gates remain mandatory. This documentation-only assessment does not rerun or expand the earlier runtime evidence. Earlier implementation and review entries above are historical.

### TASK-006 implementation — IMPLEMENTED — AWAITING REVIEW

- Base: TASK-005 approved integration merge `75b8b1f`; branch: `task/006-pdf-adapter`; implementation commits: `119d27b0af0f2ad1ed4a4224778037c679fab129`, `0b2d05464142c3bde31486b7a5fd14497089035c`, `452edbe21f94a844b04d080ed7549e216c13e42f`.
- Adds `rendering/pdf.py` and a packaged `rendering/templates/baseline.yaml`. The adapter validates the complete `DocumentPlan` and profile/support review receipts with the TASK-003/TASK-004 validator before creating private staging files. It emits only the fixed A4, one-column, 11pt, 20mm RenderCV template and literal escaped Typst text tokens.
- RenderCV 2.8, Typst 0.15.0, rendercv-fonts 0.5.1 and Pydantic 2.12.5 are locked runtime dependencies. Pydantic was raised from 2.11.7 because RenderCV 2.8 declares `pydantic[email]>=2.12.5`; no Playwright dependency enters the production environment. `pypdf` 6.18.1 is development-only extraction coverage.
- The worker and its RenderCV child run under macOS `sandbox-exec` with `(deny network*)`; proxies are removed, local font/package paths are explicit, subprocess arguments use arrays, and output is bounded to 2,000,000 bytes. Missing isolation, timeout, failed worker, stale/tampered plan, unsafe output name and existing output fail closed. Temporary files are removed on success and handled failures.
- `jae build-cv` requires explicit profile JSON, DocumentPlan JSON and local human review receipt JSON. It publishes only to `JAE_DATA_DIR/outputs/`; no profile, plan or review data is bundled in Git. The README records the command and current-laptop limitation.
- Synthetic production tests cover complete Poppler and pypdf extraction, German Unicode, hostile Typst/HTML/template-like text, URLs/file-like references, a two-page long plan, tampered plans, missing isolation, timeout and worker-failure cleanup. No PDF is accepted from an unisolated fallback.
- Verification: `uv sync --locked` passed; Python 3.12.14; full `uv run pytest` passed (38 tests); `uv run ruff check .` passed; `uv run ruff format --check .` reported 37 files already formatted; `uv run mypy src` passed with no issues in 23 source files. Production tests built short, hostile and long two-page synthetic PDFs under sandbox-exec; Poppler and pypdf complete-content comparisons passed, and timeout/worker/isolation/tamper cleanup tests passed. A CLI smoke build produced an A4 one-page PDF. Poppler and raster inspection are host tools; cross-platform support, Playwright quality and ATS scoring remain unclaimed.
- Inspected ignored synthetic artifacts: one-page PDF/preview at `artifacts/renderer/task-006/production-1/` (PDF SHA-256 `70f5300f28e99ec70c00a1a6df549840c8f47467345e69eae0fe26b48f2d3c6f`) and two-page PDF/previews at `artifacts/renderer/task-006/production-3/` (PDF SHA-256 `3559ae867387f4d7ddbab96ee0ffa7e79e998a98b83aca8aa1c0a1cea369f70c`). Both are A4; the two-page case has two raster pages with no visible clipping in the inspected previews.

Next action: obtain independent review of the exact TASK-006 implementation commit. Do not merge or start TASK-007 before approval.

Independent TASK-006 review: CHANGES REQUIRED for implementation `452edbe21f94a844b04d080ed7549e216c13e42f` (documentation head `b6c73204a052ce860eca573a8a2ca778815b9f29`). Findings: stale Pydantic 2.11.7 documentation versus locked 2.12.5, and missing pypdf complete-content assertion for the two-page production test. Required checks passed (38 tests, Python 3.12.14, Ruff, format, mypy); CLI help/invalid usage and production staging/isolation tests were exercised. See `docs/reviews/TASK-006.md`.

### TASK-006 review corrections — IMPLEMENTED — AWAITING REVIEW

- Correction commit: `8f8181fd88925c1bc33e6800576c938f3f9857e1` on `task/006-pdf-adapter`; no dependency or lockfile changes.
- F-001: `docs/DEPENDENCIES.md` now labels Pydantic 2.11.7 as the historical TASK-002 pin and records the current Pydantic 2.12.5 runtime pin. Installed RenderCV 2.8 metadata reports `pydantic[email]>=2.12.5` and `pydantic-extra-types>=2.11.0`; the locked graph records RenderCV 2.8 and Pydantic 2.12.5.
- F-002: the real production two-page test now extracts the generated PDF independently with Poppler and pypdf and compares both results to the same expected plan using the existing narrow normalization. The existing complete-content and negative-control tests remain unchanged.
- Verification: targeted two-page test passed; full pytest passed (38 tests); locked sync passed; Python 3.12.14; Ruff check passed; Ruff format check passed with 37 files formatted; mypy passed with no issues in 23 source files. The staged diff contains only `docs/DEPENDENCIES.md` and `tests/test_rendering.py`.

Next action: independent re-review of correction commit `8f8181fd88925c1bc33e6800576c938f3f9857e1`; do not merge or start TASK-007.

Scoped TASK-006 re-review approved corrected implementation `8f8181fd88925c1bc33e6800576c938f3f9857e1` with documentation head `93e61499ff4bacbbfd44ff99b4f56738a9d79b15`. F-001 dependency documentation and F-002 independent two-page Poppler/pypdf extraction are addressed. Locked Python 3.12 checks passed: targeted test 1 passed, full suite 38 passed, Ruff, format and mypy passed. See `docs/reviews/TASK-006-rereview.md`.

## TASK-007 — APPROVED

Base: the approved TASK-006 merge `d04d4dfe247958c175e66df5ab64f228d206246a`. Implementation commits: `72daba1beb691e81f068825ae032c36a43da367e` and corrective `4437ff51c79cb93e3bd458dcfc910538dd045361`.
This implementation adds `job_application_engine.ats_qa`, which measures the
actual PDF bytes with independent Poppler and pypdf extraction, complete NFC /
layout normalization, exact ordered section and entry expectations, scoped
critical fields, Unicode and quantitative token multiplicity, page count/A4
media and crop boxes, byte size, Poppler word geometry, visibility-operator
flags, and raster-page hashes. `QAReport` records every check with status,
measurement, expected value, tool/version, artifact hash and bounded
diagnostics. Visual review remains `not_checked` until an identified person
records an observation against the exact hash; raster generation never counts
as that observation. A pypdf worker runs under the same macOS network-denied
sandbox and rejects oversized streams.

Synthetic fixtures and actual-PDF tests are in `tests/rendering/` and
`tests/fixtures/rendering/task007/`. Reproduction is
`uv run python tests/rendering/reproduce_task007.py`;
it writes PDFs, JSON reports and raster pages below ignored
`artifacts/qa/task-007-<UTC>/`. The command reports `not_checked` overall until
manual visual observations are recorded. The corrective commit explicitly counts every mapped field value inside its recovered complete entry span. The checker detects text-layer loss,
wrong content/order/scope, duplicate/unexpected text, missing meaningful
numbers and Unicode, invalid dimensions, out-of-page text, explicit nonpainting
text modes, clipping operators and selected transparency/forms. It cannot
universally detect occlusion, white-on-white paint, complex clipping, image
meaning or an employer ATS score; those limitations remain explicit.

Dependency change: pypdf `6.18.1` is now a locked runtime QA dependency so the
production QA command can invoke its independent extractor. The version was
already locked by TASK-006; the dependency register records the promotion.
Poppler 25.08.0 and sandbox-exec are host tools. No online upload, OCR,
commercial parser, second renderer, final approval or TASK-008 work was added.

Independent TASK-007 review: CHANGES REQUIRED for corrected implementation `4437ff51c79cb93e3bd458dcfc910538dd045361`; documentation head `5bcb43fe2087fc0ee0577312689e6f850e025746` is documentation-only after implementation. Scoped-field and report/visual hash logic inspected. Locked sync, Python 3.12, collection (56 tests), Ruff and mypy passed, but full pytest did not complete within the review window, leaving the required verification gate unresolved. See `docs/reviews/TASK-007.md`.

TASK-007 verification re-review completed: implementation `4437ff51c79cb93e3bd458dcfc910538dd045361`, documentation head `5bcb43fe2087fc0ee0577312689e6f850e025746`. Reconciled 56-versus-67 count: current configuration collects 67 nodes across 8 test files; 56 was an earlier incomplete/stale collection count. Persistent full run with JUnit (`uv run pytest -vv --durations=0 --junitxml=artifacts/verification/task-007/junit.xml`) exited 0 with 67 passed in 45.54s. Prior findings resolved; final independent verdict APPROVED. See appended review.

## TASK-008 — APPROVED

M1-FIX-002 independent review: **CHANGES REQUIRED** for implementation `3d9c7916f6a8cc2bcc9552160abff27d0ab5de36` and documentation head `d924438dfc4d310c4c7a0ce0f69424a9a2ea663d`. Findings: QA identity is caller-authorized (F-01), and production theme hyphenation remains enabled despite the attempted setting (F-02). Full suite 93 passed, but these acceptance/security boundaries require correction. See `docs/reviews/M1-FIX-002.md`.

TASK-007 approved merge/base: `a83324f9afcef143ef264c554c5d4e7764d1e8bd`. Initial implementation commit: `d53276b8357846774e5147bd13448af23b73cc5d`; corrective implementation head: `c0c25f81baca6bf34822aea58a56340000c15ce6`.

Added `snapshots/manifest.py`, `snapshots/store.py`, `snapshots/review.py` and
`snapshots/export.py`. A build validates the current profile, exact document
plan, local review receipts, supplied immutable support captures, UTF-8 text,
PDF size and a passing TASK-007 QA report with an attributed visual review. It
writes profile/selected source slice/reviews/plan/PDF/TXT/QA/configuration/tool
versions/capture bytes and a hash manifest into a private same-filesystem
staging directory, fsyncs, then atomically publishes a new ID. Existing IDs
cannot be overwritten; only staging directories carrying the implementation's
owner marker are cleanable.

Final approval is an explicit separate `final-approval.json`, bound to the
manifest, PDF and text digests, reviewer and aware timestamp. Export rechecks
manifest and every artifact/capture hash, current profile revision/digest,
current plan/provenance/reviews, mandatory QA plus visual review, support
availability/status and expiry against the injected current clock. The
historical snapshot is retained and only exact PDF/TXT bytes are copied to a
new destination. A profile loader detects concurrent revision changes before
publication. Backdated plan `as_of` values do not move the export clock;
external-original removal is harmless when the reviewed capture remains
intact. No dependencies were added.

CLI commands are `jae snapshot-build`, `jae snapshot-approve` and
`jae snapshot-export`; all input/output paths are private-root-relative under
`JAE_DATA_DIR`. The complete synthetic API workflow is reproducible with
`uv run python tests/reproduce_task008.py`; it created a
private snapshot, matching final approval, and exact PDF/TXT export with
manifest digest `dcba708224133f6f0128a7651b7ed461378f070f3b3b81f4e55df6d97ea10fec`.
The persisted JUnit report is under ignored
`artifacts/verification/task-008/junit.xml`.

Verification: locked sync passed; Python 3.12.14; full suite 80 passed with
zero failures (JUnit at `artifacts/verification/task-008/junit-corrective.xml`);
focused snapshot suite 13 passed; Ruff check/format and mypy passed
(35 source files). Synthetic tampering, interruption, no-overwrite, current
revision/capture/status, stale/missing visual QA, expiry, concurrent revision,
restore/hash and exact-byte export cases pass. The corrective test mutates the
source PDF between copying and publication; the manifest recheck rejects the
export and removes its staging directory. The implementation does not
provide signing, encryption, SQLite tracking, browser submission, identity
Document copying, history deletion or TASK-009 work.

Next action: independent review of the exact corrective TASK-008 implementation commit;
do not merge TASK-008 or start TASK-009 before approval.

Independent TASK-008 review: CHANGES REQUIRED for corrected implementation `c0c25f81baca6bf34822aea58a56340000c15ce6`; documentation head `ff66a8617a9e9884efdff44023570e7c3081ba40` is documentation-only after implementation. Locked sync/Python 3.12, full pytest (80 passed), reproduction, Ruff, format and mypy passed. Blocking finding: required snapshot-build/approve/export CLI workflow was not independently exercised; reproduction is API-only and no CLI integration test was found. See `docs/reviews/TASK-008.md`.

### TASK-008 CLI review correction — IMPLEMENTED — AWAITING REVIEW

- Preserved the independent finding in `docs/reviews/TASK-008.md`. Corrective implementation commits: `ee3db56edf4b91892d8c17ded2741fea961d8e07` and `045b1e598b5e47bd73b3838442d466fa50e40286`; the corrective head is based on reviewed implementation `c0c25f81baca6bf34822aea58a56340000c15ce6` and adds no dependency or lockfile changes.
- Added `tests/test_snapshot_cli.py`, which resolves the installed `jae` executable and runs `snapshot-build`, `snapshot-approve`, and `snapshot-export` as subprocesses against a temporary external `JAE_DATA_DIR`. It checks complete snapshot files, pre-approval rejection, synthetic reviewer and manifest/PDF/TXT digest binding, exact exported bytes, missing arguments, private-root traversal, existing-destination protection and post-approval PDF tampering.
- The CLI defect found by the integration test was corrected in `cli._reviews`: JSON review receipts now use Pydantic JSON validation so ISO timestamps are parsed at the actual command boundary while duplicate-key rejection remains in place.
- Targeted verification: `uv run pytest tests/test_snapshot_cli.py -vv` — 1 passed. The private-root escape case preserves an unrelated sentinel file. Full locked verification: `uv sync --locked` passed; Python 3.12.14; `uv run pytest -q --junitxml=artifacts/verification/task-008-cli/junit.xml` — 81 passed, 0 failures/errors; Ruff check and format passed; mypy passed with no issues in 35 source files.

Next action: independent re-review of corrective head `045b1e598b5e47bd73b3838442d466fa50e40286`; do not merge TASK-008 or start TASK-009.

TASK-008 corrective CLI re-review approved implementation `045b1e598b5e47bd73b3838442d466fa50e40286` with documentation head `bd7c8185816d8cb4af6ce881948aa1bb81d38dba`; prior CLI finding resolved. Focused CLI test passed; full suite **81 passed**, Python 3.12.14, Ruff/format/mypy passed. Planning-era cloud/no-executable-code statements were labeled historical. See appended TASK-008 review.

## TASK-009 — BLOCKED — AWAITING APPLICANT REVIEW

- Base: approved TASK-008 integration merge `3c562fe1c3de0239a129fad10804abd375c1d38e`; branch: `task/009-personal-baseline`.
- The user-supplied external root was created/preserved with restricted permissions and is configured for project commands with `JAE_DATA_DIR`; no unrelated laptop folders were scanned. The supplied CV was copied into the private source area and retained outside Git. Poppler and pypdf extracted the two-page A4 source, and both raster pages were visually inspected.
- Private curation revision 2 records the applicant's supplied Batch 1 and Batch 2 confirmations outside Git. Confirmed scope includes the selected contact, employment, education, summary, skill and language decisions; full addresses remain private. SH3, ES3 and the unassigned project context are excluded from this baseline.
- The exact merged SH1+SH5 wording and the other displayed responsibility wording are now confirmed in private curation revision 3. Newly composed P1/P3/P4 project wording remains pending review. No runtime fact/wording approval receipt, support binding, baseline PDF/TXT, QA report or final applicant approval has been created.
- The deterministic production path currently lacks the document-plan sections and support-capture forwarding needed for these approved project/responsibility claims. The private readiness record keeps those gates blocked rather than omitting or misclassifying content. Technical synthetic regressions remain available from TASK-008. See `docs/reviews/M1.md` for the sanitized milestone handoff.

### M1-FIX-001 — CHANGES REQUIRED (independent review 2026-09-15)

- Base: `273cdd484081948bfbedca1ff37e390b27dbd5af`; branch: `task/009-m1-fix-001`.
- Implementation commit: `d93dc0f` (full hash is recorded in Git); the review handoff is appended to `docs/REVIEW_HANDOFF.md`.
- Reproduction identifies two independent gaps: the profile/document-plan schema has no typed responsibility or project claim records, so `compile_baseline` emits only flattened employment identity lines; separately, `build_pdf` does not accept or forward support captures. Existing fixtures cover those paths independently and therefore did not detect end-to-end omission.
- ADR-017 proposes bounded responsibility/project records, exact revision-bound scopes, additive version policy and fail-closed capture forwarding through plan, text/PDF, QA and snapshot/export. Independent re-review of `004aeda` returned APPROVED WITH FOLLOW-UP; implementation is cleared with concrete scope-validator and wrong-scope test follow-ups. No applicant data is involved.
- The correction adds `ResponsibilityFact` and `ProjectFact` records with exact employment `FactRef`s, subject/entity checks, deterministic experience ordering and explicit unknown project dates. `compile_baseline` preserves employment-linked responsibilities/projects and standalone contributions without duplicate employers. `build_pdf` and `jae build-cv` now require and forward captures for approved evidence; unapproved evidence captures are not demanded.
- Synthetic regression `tests/test_m1_fix.py` exercises validated profile → plan → text/PDF (Poppler and pypdf) → QA → snapshot build/approval/export, plus missing-capture and wrong-employment/subject failures. The production PDF/QA test records an attributed synthetic visual observation solely for test coverage; no applicant approval is represented.
- Verification: locked sync, Python 3.12.14, 85 tests passed, Ruff check/format and mypy passed. Remaining M1 gates are applicant confirmation of exact P1/P3/P4 wording and runtime canonical receipts, followed by a genuine private baseline and separate final PDF/TXT approval.


Independent M1-FIX-001 review of `b985674a31f57382abfebef7464376a6699477fa`: **CHANGES REQUIRED**. Reconstructed plans can move responsibility/project claims beneath the wrong employment with a recomputed digest (F-01); project unknown-start ordering contradicts ADR-017 (F-02). Full suite 85 passed; focused suite 4 passed; locked sync, Python 3.12.14, Ruff/format/mypy passed. Installed synthetic CLI build/snapshot/approval/export and exact-byte checks passed; one synthetic raster page inspected. These passing checks do not resolve the adversarial findings. See [review](../reviews/M1-FIX-001.md). Architecture approval and private wording confirmation do not authorize personal PDF generation using this unapproved implementation. TASK-010 remains blocked.

### M1-FIX-001 corrective implementation — IMPLEMENTED — AWAITING REVIEW

- Correction base: `b985674a31f57382abfebef7464376a6699477fa`; branch:
  `task/009-m1-fix-001`. The historical F-01/F-02 review is preserved above.
- F-01 root cause was that the flat experience line list validated exact fact
  wording and support but had no placement check. The correction treats each
  trusted employment line as the active anchor and requires every linked
  responsibility/project to match its exact `(fact_id, revision)` reference;
  standalone projects clear the anchor and remain valid. Reconstructed plans
  with recomputed digests are rejected by document validation, text rendering
  and PDF build before publication.
- F-02 root cause was reverse sorting that put known project starts first and
  reversed ties. `_project_key` now applies the ADR-017 unknown-first key,
  descending known date precision components, and ascending stable IDs. Tests
  cover mixed unknown/year/month/day starts, equal-date ties and shuffled input.
- No schema, dependency or lockfile change was made. Synthetic regressions in
  `tests/test_m1_fix.py` independently construct malicious plans and verify
  valid standalone behavior, exact revision failures and production-boundary
  rejection. Personal curation, runtime receipts and final applicant PDF/TXT
  approval remain outside Git and pending.
- Implementation commit: `157b973830727cccd9628ec0c21b916f1a880f3a`.
- Verification: `uv sync --locked` passed;
  Python 3.12.14; targeted `uv run pytest tests/test_m1_fix.py -q` — 6
  passed; full `uv run pytest -q` — 87 passed; Ruff check and format check
  passed; mypy passed with no issues in 35 source files. The full-suite JUnit
  report is retained under ignored `artifacts/verification/m1-fix-001-corrective/`.

Next action: independent re-review of the exact corrective head in
`docs/REVIEW_HANDOFF.md`; do not merge or start TASK-010 before approval.

M1-FIX-001 corrective re-review approved corrected implementation `157b973830727cccd9628ec0c21b916f1a880f3a`; documentation head `803fa0fda9f11be97883f8b0b96a30d0a42a3d72` differs only by documentation. F-01 active employment context/placement and F-02 unknown-first project ordering are resolved. Focused tests 6 passed; full suite 85 passed; locked Python 3.12, Ruff, format and mypy passed. ADR-017 implementation follow-ups are satisfied; applicant wording gates remain. See appended review.

### TASK-009 resumed after M1-FIX-001 approval — APPLICANT REVIEW PENDING

- Approved M1-FIX-001 was integrated into `task/009-personal-baseline` with
  merge commit `03d06703775a1891e78ec2a5df3be60d9fac1554` using `--no-ff`.
  The unfinished personal milestone remains unmerged into `main`.
- Test-count reconciliation: the approval record reports 85 full-suite tests,
  while the implementation's focused report lists 6 M1 tests. A fresh
  collection at the approved code produced 87 nodes: 29 PDF-QA, 6 CLI, 4
  document-plan, 6 M1-FIX, 7 schema, 7 provenance, 3 experiment, 7 rendering,
  4 repository-policy, 1 snapshot-CLI and 13 snapshot tests. The retained
  JUnit file `artifacts/verification/m1-fix-001-corrective/junit.xml` records
  `tests="87"`, zero failures and zero errors; its two additional node IDs
  are `test_reconstructed_plan_rejects_moved_claims_at_validation_and_pdf_boundaries`
  and `test_standalone_project_is_valid_and_project_order_is_unknown_first_with_stable_ties`.
  No required tests were omitted; the 85 figure is a reporting discrepancy.
- Private curation revision 3 was inspected in place and preserved. The
  consolidated pending review is outside Git at
  `$JAE_DATA_DIR/reviews/applicant-review-projects-r0002.md`
  with canonical preview payloads in the adjacent `.json` file. Only exact
  P1/P3/P4 wording remains unapproved; P2, SH3 and ES3 remain excluded or
  pending as previously confirmed. The older canonical review mapped
  eSketchers revision 1; the new pending payload correctly maps the latest
  curation's eSketchers revision 2 and issues no runtime receipt.
- After explicit wording confirmation, use the established local review
  mechanism, then generate and inspect the genuine baseline PDF/TXT and QA.
  Final applicant artifact approval and independent M1 milestone review remain
  open. No personal data or generated artifact was written to Git.

### TASK-009 private baseline attempt — QA BLOCKED / FINAL REVIEW PENDING

- The applicant approved the exact P1, P3 and P4 wording. Private native
  records were prepared through the local review mechanism; P3 retains its
  AUAV inSite project association but has no `employment_ref`, so it does not
  imply eSketchers attribution or inherit P1 dates. P4 remains standalone with
  contributor status and unknown dates. P2, SH3 and ES3 remain excluded or
  pending as previously confirmed.
- A genuine two-page production PDF and UTF-8 text were generated privately
  under the configured data root. Both pages were rasterized and manually
  inspected; text is legible and no clipping was observed. Private outputs,
  extracted texts, rasters and QA report remain outside Git.
- QA result for PDF digest
  `37eed719e5a6998ae873c06a0c57815ab49ff029fb59b12d19d6d6d73113e464`:
  Poppler complete text passed (4173 normalized characters); pypdf mandatory
  complete-text and entry-sequence checks failed. The exact differences are
  pypdf splitting the LinkedIn URL after `https:/`, and exposing automatic
  hyphenation in `maintainability`, `modularity` and `validation`. These are
  extraction/rendering compatibility failures, not normalized away.
- The generated output also omits the confirmed candidate name because the
  trusted baseline template has `cv.name: null` and the current native schema
  has no bound name fact. This is a production-path representation gap; the
  document is not ready for final applicant approval. No silent fallback,
  claim removal or typography shrink was applied.
- Private artifact locations: `outputs/baseline-r0001.pdf`,
  `outputs/baseline-r0001.txt`, `outputs/baseline-r0001-poppler.txt`,
  `outputs/baseline-r0001-pypdf.txt`, `outputs/baseline-r0001-qa.json` and
  `outputs/baseline-r0001-qa-rasters/`. Final applicant PDF/TXT approval and
  independent M1 review remain pending until these blockers are resolved.

### M1-FIX-002 required identity and PDF extraction — IMPLEMENTED — AWAITING REVIEW

- Base: `e2c5294ef6e95990b1089f519772661865134738`; branch:
  `task/009-m1-fix-002`. The scope and acceptance record is
  `docs/tasks/M1-FIX-002.md`.
- F-01 root cause: the baseline schema and compiler had no typed candidate-name
  fact, while the trusted template left `cv.name` empty. The correction adds an
  approved `ContactName` fact, requires exactly one revision-bound name claim
  for the sole person entity, and rejects plans that omit or stale-bind it.
  QA now checks an independently curated required identity in both extractors,
  so a renderer omission cannot define its own passing oracle.
- F-02 root cause: Typst hyphenation and extraction line breaks exposed split
  words and HTTPS slashes. The trusted worker disables hyphenation; the shared
  narrow normalizer accepts whitespace only between the two scheme slashes and
  preserves all other punctuation, numbers, qualifiers and negation.
- Synthetic regressions cover reconstructed name removal, stale identity
  revisions, renderer omission/substitution, URL and maintainability/
  modularity/validation extraction, and existing complete-content controls.
  The earlier personal PDF remains preserved as a historical diagnostic and
  was not regenerated. Applicant final PDF/TXT approval and independent M1
  review remain open.

### M1-FIX-002 corrective review findings — IMPLEMENTED — AWAITING REVIEW

- Independent review commit `f6a6f8c66da8dd397e3a5c10b9169059f4ec1143`
  identified two defects in `3d9c791`: QA accepted a caller-supplied
  identity oracle, and the RenderCV engineeringclassic theme overrode the
  prepended no-hyphenation rule.
- The correction binds QA reports to the validated profile ID/revision/digest
  and exact approved name fact digest. Snapshot build and current export now
  reject reports lacking that binding. The substituted-PDF plus substituted-
  expectation attack fails both extractor identity checks; low-level text
  helpers have no identity authority.
- The effective trusted theme now sets
  `typography.alignment: justified-with-no-hyphenation` and permits bounded
  entry page breaks. Synthetic two-page output remains two pages with complete
  Poppler and pypdf text, no discretionary `determin-` breaks, and retained
  11 pt/A4 settings. Personal outputs were not regenerated.
- Corrective implementation commit: `be4d9dc1c6411520d874a98539ec6904c8ba4873`.
  Verification: `uv sync --locked` passed; Python
  3.12.14; full pytest **94 passed**; Ruff check/format and mypy passed.
  Targeted two-page QA and substituted-identity regressions passed. Raster
  pages were generated and manually inspected under the ignored temporary QA
  directory. The corrective head remains awaiting independent re-review.

### M1-FIX-002 integration and TASK-009 baseline resume — IMPLEMENTED — AWAITING REVIEW

- Approved M1-FIX-002 integration merge: `cf422fb972b2b9404318237bbbbe7fefaadb2170` on `task/009-personal-baseline`; main remains unchanged. The approval review and findings are preserved.
- The latest private profile revision migrates the previously confirmed candidate name into the typed `ContactName` fact required by the corrected validator. Existing applicant confirmations, P1/P3/P4 wording, exclusions and support captures were carried forward; P3 has `employment_ref` null and unknown dates, and P4 remains standalone with unknown dates.
- The next private baseline was generated through the installed `jae build-cv` command with `JAE_DATA_DIR` set to the external private root. A two-page PDF and UTF-8 text were produced. Independent Poppler and pypdf extraction both passed complete ordered-content, identity, entry-scope, Unicode and quantitative checks. A4 dimensions, page count, file-size, geometry and raster-generation checks passed. Every raster page was visually inspected and recorded separately with the PDF-bound visual-review mechanism.
- Private outputs, extracted texts, raster pages, profile/plan/review payloads and hashes remain outside Git. The exact PDF/TXT and passing QA report are presented for final applicant review; final artifact approval and independent M1 review remain pending. Baseline-r0002 and its failed QA remain historical evidence.

### M1-FIX-003 presentation correction — IMPLEMENTED — AWAITING REVIEW

Base: `d492707d80ddf97cdfae6c531ec5e84e38625645`; feature branch:
`task/009-m1-fix-003`. This synthetic-only correction adds a deterministic
applicant-facing projection for the validated plan: bound name and compact
contacts, employment headings and bullets, linked versus standalone projects,
allowlisted skill groups with exact qualifiers, typed education thesis/coursework,
and precision-preserving dates with internal unknown labels omitted from display.
The trusted template identity is versioned to
`baseline-v2-presentation-adr018`.

The projection runs only after existing provenance and placement validation. It
does not alter canonical wording or support bindings. Empty new optional fields
are omitted from one shared canonical fact payload used by fact digests, local
review receipts and profile digests, preserving old approval hashes; nonempty
fields change the digest and require a reviewed revision. Existing private
records and baseline-r0003 were not modified or regenerated.

Synthetic regressions cover duplicate skill names/revisions, notes and
qualifiers, partial project descriptions, unknown degree names, identity and
placement attacks, Poppler/pypdf complete extraction, no-hyphenation, CLI,
snapshot/export and isolation paths. The full suite collected 101 tests and
passed. Locked sync, Python 3.12.14, Ruff, format and mypy passed. Synthetic
one-page and two-page raster pages were inspected; automated reports remain
`not_checked` until a named visual receipt is recorded through the review
mechanism. ADR-018 received independent architecture review
`APPROVED WITH FOLLOW-UP`; implementation review and M1 applicant acceptance
remain open. No personal output or final applicant approval was created.

### M1-FIX-003 integration and TASK-009 baseline resume — BLOCKED — AWAITING TYPED MIGRATION/APPLICANT REVIEW

Approved M1-FIX-003 implementation `1291ba94fbffdde1d89f5fba7b5ac78c7ebd5ab8`
was integrated into `task/009-personal-baseline` with merge
`6783fa21dfb3e61c8ce5d22d6894e081f21ce229`. The independent approval is
`100b955cfe26a7d8ccba032e1fe867e5c294cf7a`; main remains unchanged.

The latest private reviewed profile is revision 5 with 58 runtime receipts and
its immutable captures. The existing audit disposition confirms the exact
responsibility wording, locations, thesis/coursework facts, and S1–S5 skill
categories. The native revision does not yet encode thesis/coursework or skill
category fields, so no changed canonical representation or runtime receipt was
fabricated. P3 remains association-only with unknown dates; P4 remains a
standalone contributor project with unknown dates.

A new private baseline revision was generated through `JAE_DATA_DIR` using the
production `jae build-cv` command: `outputs/baseline-r0004.pdf` and
`outputs/baseline-r0004.txt`. The PDF is two pages and has readable A4 output;
both raster pages were technically inspected. An independently authored audit
oracle requiring the confirmed thesis/coursework and grouped skill content
produced `outputs/baseline-r0004-qa.json`: page count, dimensions, geometry,
identity and extraction-tool checks pass, while complete-content and entry
sequence checks fail because those typed fields are absent from the current
profile revision. The exact Poppler/pypdf extractions and a separate technical
inspection note are private. Baseline-r0003 and all earlier artifacts remain
unchanged.

M1 remains incomplete. The next gate is a reviewed typed profile migration for
the confirmed thesis/coursework and skill-category representations, followed by
regeneration and QA. Final applicant PDF/TXT approval, snapshot publication and
independent M1 review remain separate; no final approval or export was recorded.

### TASK-009 baseline resume after M1-FIX-003 approval — BLOCKED — TYPED MIGRATION REQUIRED

M1-FIX-003 approval was integrated into `task/009-personal-baseline` with
merge `6783fa21dfb3e61c8ce5d22d6894e081f21ce229`. The approved implementation
commit is `1291ba94fbffdde1d89f5fba7b5ac78c7ebd5ab8`; independent approval is
`100b955cfe26a7d8ccba032e1fe867e5c294cf7a`. Main remains unchanged.

During private validation, a compatibility defect was found in the approved
implementation: its profile digest removed approval fields when reconstructing
facts, so the preserved profile-r0005 digest and baseline-r0003 plan could not
validate. A narrow correction is currently uncommitted on this branch and must
be independently reviewed; it uses approval-inclusive profile payloads while
keeping fact-review payloads approval-free. The discrepancy is recorded rather
than treated as covered by the M1-FIX-003 approval.

Using that local correction, `jae build-cv` generated private
`outputs/baseline-r0005.pdf` and `outputs/baseline-r0005.txt`; baseline-r0003 and
r0004 remain untouched. The two-page PDF has readable A4 layout and both raster
pages were technically inspected. An independently authored oracle requiring
the confirmed FAU thesis/coursework and S1–S5 grouped skill content produced
`outputs/baseline-r0005-qa.json`: identity, page count, dimensions, geometry and
extractor execution pass, while Poppler and pypdf complete-content and entry
sequence checks fail because those typed representations are absent from the
current profile revision. No runtime receipt or applicant approval was
fabricated. The exact PDF/TXT/QA report and private technical review remain
outside Git.

M1 remains incomplete. A reviewed typed profile migration is required before a
passing baseline can be generated; final applicant PDF/TXT approval, snapshot
publication and independent M1 review remain separate gates.

### TASK-009 typed migration gate — BLOCKED — REPRESENTATION REVIEW REQUIRED

The latest private profile remains revision 5 and is unchanged. A private
before/after mapping was prepared at `typed-migration-r0001.md` with its
machine-readable companion `typed-migration-r0001.json`. It maps the already
confirmed FAU thesis wording, B.Sc. coursework association, and S1–S5 skill
category memberships to their existing applicant confirmation records while
preserving all qualifiers, unknowns, exclusions, P3 association-only scope and
P4 standalone status.

These are non-empty typed-field changes. The established local review
mechanism binds each fact receipt to the exact canonical payload displayed to
the applicant; no receipt was fabricated and no private profile was mutated.
The current private baseline-r0005 therefore remains the latest generated
revision, with mandatory complete-content and sequence QA failures for the
missing typed fields. Its two raster pages and failed report remain preserved.

The next gate is applicant confirmation of the exact representation delta in
the private mapping, followed by native receipts, a fresh profile revision,
a freshly compiled DocumentPlan, and a new production baseline/QA run. Final
PDF/TXT approval and independent M1 review remain separate.

### Typed migration review-sheet expansion — BLOCKED — ONE GROUP CONFLICT

The private skills sheet was expanded to revision r0002 from the actual
profile-r0005 skill names, IDs and revisions. It confirms 32 unique profile
skills, exact name preservation, and complete one-to-one coverage of the
confirmed S1–S5 names. The recorded confirmation lists contain 33 entries
because `Python` appears in both S1 and S2; the typed `category` field accepts
one category, so that single assignment remains unresolved. No profile,
approval or receipt was changed. The education delta remains as previously
listed. See the private mapping for the exact rows and reconciliation.

### TASK-009 typed migration and baseline-r0007 — IMPLEMENTED — AWAITING APPLICANT REVIEW

The applicant confirmed the exact typed representation delta, including the
FAU thesis fields, B.Sc. coursework association, S1–S5 categories, and Python
in S1. A new private profile revision and revision-bound local receipts were
created from those displayed payloads; prior profile revisions, captures and
receipts remain preserved. P3 remains association-only with unknown dates and
P4 remains a standalone contributor project with unknown dates.

A fresh DocumentPlan was compiled from the migrated profile (not reused from
baseline-r0003). The production path initially exposed a LinkedIn extraction
split after `www.`; the focused presentation correction in commit
`3a4d8a8c22ddeaa6f68f1bc88035dd414d6b7ac2` renders contact scalars on separate
compact lines. The next private baseline, baseline-r0007, now passes all
mandatory Poppler and pypdf complete-content, identity, sequence, Unicode,
quantitative, geometry, A4, pagination and file checks. Both raster pages were
inspected and recorded as a technical visual observation against the exact PDF.

The exact private PDF, UTF-8 text, extracted texts, QA report and migration
mapping are presented for final applicant review. Final artifact approval,
snapshot publication and independent M1 review remain open. No personal data
or artifact hashes were committed.

### M1-FIX-004 visual hierarchy and page composition — IMPLEMENTED — AWAITING REVIEW

Base: `139c48f822611275d93d43d64ba68d4d918b75b1`; implementation commits:
`531a486e447cf71961fb9f18e414072f72ce178b` and `d0822de`; branch:
`task/009-m1-fix-004`. Full corrective head: `d0822de`.
The focused synthetic correction versions the trusted
presentation/template policy as `baseline-v3-presentation-m1-fix004`. It
removes only the visible Contact label, makes the bound name prominent,
left-aligns body text with effective no-hyphenation, emphasizes employment
headings, applies hanging responsibility bullets, nests linked projects and
places standalone projects under Selected Projects when present. Unknown
dates, P3 association-only scope, P4 standalone scope, approved wording and
typed qualifiers remain unchanged. Ongoing degree status is not duplicated.

Page composition is content-aware: the synthetic two-page project fixture
starts Selected Projects on page 2; a no-project fixture creates no project
heading or extra page; and an over-capacity fixture retains all claims across
more than two pages rather than shrinking or omitting them. The page-fill
marker is derived after plan/provenance validation and is not a caller field.
Synthetic checks include complete Poppler/pypdf extraction, Unicode and
identity/provenance regressions, literal hostile text, long URLs, grouping,
page breaks and raster generation. The current run is 111 tests passing;
Ruff check/format and mypy pass (36 source files). No personal output was
regenerated, and baseline-r0007 remains historical private evidence. A
private non-approved wording shortlist is stored outside Git under the
configured data root. A manual visual pass covered all 9 generated synthetic
pages: one no-project page, two representative project pages and six
over-capacity pages. Applicant final PDF/TXT approval and independent M1
review remain open.

### M1-FIX-004 F-01 corrective implementation — APPROVED

Base/review head: `4c0c757111547906623f32da3d0729ef7053e6c2`; corrective
implementation: `c7d957b08d24e54fb88eda55e3edb87b8a410bc6` on
`task/009-m1-fix-004`. The preserved review found that the exact synthetic
long ContactUrl was visually present but split after `meaningful-` in both
Poppler and pypdf extraction. The production boundary now places each contact
scalar in its own trusted non-breakable block and uses the effective Raleway
11 pt Typst layout to measure each complete URL line against the A4 content
width left by the 20 mm margins. Fitting URLs remain unchanged canonical
values and pass complete ordered Poppler/pypdf extraction. The exact reviewed
URL and a synthetic over-width URL fail before publication with a bounded
diagnostic; no apparent successful PDF remains. Changed suffix and punctuation
expectations fail the complete-content regression. The corrected template
identity is `baseline-v3-presentation-m1-fix004-f01`.

Focused command: `uv run pytest tests/test_m1_fix004.py
tests/test_rendering.py tests/test_m1_fix003.py tests/test_m1_fix.py -q` — 35
passed. Locked verification: `uv sync --locked` —
passed; `uv run python --version` — Python 3.12.14;
`uv run pytest -q --junitxml=$TMPDIR/m1-fix004-f01-junit.xml`
— 114 passed; `uv run ruff check .` — passed;
`uv run ruff format --check .` — passed, 61 files;
`uv run mypy src` — passed, 36 source files. A
synthetic fitting raster at `$TMPDIR/m1-fix004-f01-fitting/page.png` was
inspected; it is one A4 page with a dedicated complete URL line and no
clipping. No personal output was regenerated and baseline-r0007 remains
historical evidence. Applicant final PDF/TXT approval and independent M1
review remain open.
