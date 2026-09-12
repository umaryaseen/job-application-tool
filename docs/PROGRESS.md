# Progress — authoritative implementation state

Last updated: 2026-09-12. TASK-001–003 are APPROVED; TASK-004 is IMPLEMENTED — AWAITING REVIEW.

## Environment and completed work

- Read all three supplied research reports, including examples, schema and roadmap; exact copies identified in SOURCE_REGISTER/research-manifest.
- Compared consensus, conflicts, assumptions, questionable examples and postponements; checked relevant primary upstream documentation.
- Independent research audit identified insufficient evidence-membership checks, optional provenance schema fields, unsafe date/metric semantics and mismatched scope estimates. Those are addressed in the architecture and ADRs.
- Created repository-ready documents, 16 ADRs, 35 scoped task files, acceptance/test matrix, privacy/dependency guidance, review protocol and local Codex handoff.
- Created `.gitignore` before any career data. No real applicant data, credentials, executable application code or generated personal CV exists in the repository.
- Initialized a cloud-workspace planning Git repository with an exclusions commit, a planning branch and normal corrective history. Independent reviewer approved corrected planning head `bea4cbc1a0144b6d3f4190e9b29722546ed46670` on 2026-09-09; [M0 review](reviews/M0.md) records the initial findings and resolution. This is not the laptop repository.
- Environment: cloud Linux workspace with Git 2.51.1. No laptop filesystem bridge and no `gh` executable was available. No GitHub login, repository creation or push occurred.

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
| TASK-004 | IMPLEMENTED — AWAITING REVIEW | Renderer-independent baseline plan and validated UTF-8 text; independent review pending |
| TASK-005–009 / M1 | NOT STARTED | First actual CV milestone; applicant curation still required |
| TASK-010–016 / M2 | NOT STARTED | EN/DE requirements and matrix |
| TASK-017–020 / M3 | NOT STARTED | Tested tailoring MVP |
| TASK-021–023 / M4 | NOT STARTED | Letters/tracker |
| TASK-024–035 | DEFERRED / NOT STARTED | Optional extensions and later design only |

## Tests and validation

Application unit/integration/rendering/model tests: **NOT IMPLEMENTED / NOT RUN**. No fabricated pass rate. Planned tests and their introducing tasks are in ACCEPTANCE_CRITERIA.

### TASK-001 implementation

- Branch: `task/001-project-bootstrap`; base: `8939d9e8ec5af2035ca6b5a86c94ae74efedbabb`.
- Adds a Python 3.12 package and `jae` entry point, standard-library private-root/path validation, synthetic CLI and repository-policy tests, Ruff/mypy/pytest configuration, locked dev dependencies, a staged-file safeguard, and minimal read-only-permission CI.
- The required `JAE_DATA_DIR` is absolute, existing, non-symlink, outside the repository; path traversal and symlink traversal are rejected. No personal data or application domain schema was added.
- Environment: macOS 13.6.9 x86_64; uv 0.12.13 with managed CPython 3.12.14. `uv sync --locked --group dev` passed and installed pytest 8.4.1, Ruff 0.12.11, and mypy 1.17.1.
- Checks: `uv run pytest` — 7 passed; `uv run ruff check .` — passed; `uv run ruff format --check .` — passed; `uv run mypy src` — no issues in 3 source files. `jae --version` printed `jae 0.1.0`; missing `JAE_DATA_DIR` makes `jae config-check` exit 2.
- GitHub remote setup is blocked by invalid native `gh` authentication; no remote URL or privacy claim is made. Rendering, schema, model, database, scraping, UI and application-submission checks are intentionally not implemented or run.

Planning checks passed for required files, 256 internal Markdown links at the reviewed head, 35 acyclic task dependencies, three source identities, and 14 private-path exclusions. Independent review required immutable support captures and explicit export expiry/source-eligibility rules; the corrections were independently re-reviewed and APPROVED at bea4cbc. Application behavior remains unimplemented. The supplied archive is a planning handoff, not a working MVP or a laptop installation. Final artifact checks are recorded separately after bundle creation to avoid circular Git/hash metadata.

## Open gates

1. TASK-001 is APPROVED; TASK-002 (strict profile and typed fact schemas) is the next unblocked task, on a fresh branch with independent review.
2. TASK-005 experimentally resolves renderer and exact versions; no backend is production-approved yet.
3. TASK-009 obtains actual reviewed career data and accepts a genuine baseline CV. Chat memory/research templates are not evidence.
4. Optional provider/model/data choices remain deferred and do not block deterministic implementation.

## Per-task update format

Record task ID/state; branch; base/head or containing commit reference; actual modules/behavior; dependency versions; exact commands and exit results; skipped/unrun checks; security/privacy notes; independent review verdict/report; pending applicant input; next unblocked task. Use IMPLEMENTED — AWAITING REVIEW before independent approval.

Do not change historical submitted snapshots when facts improve. Correct canonical data and generate a new version. Keep implementation and review status synchronized with Git, not aspirations.


Independent TASK-001 review: CHANGES REQUIRED at `cfaeaf1eb9eb609f89f4cbc74297066572c56a95` for F-001 (hook not enabled) and F-002 (explicit root bypass). The review is preserved in [TASK-001 review](reviews/TASK-001.md).

### TASK-001 corrective implementation

- F-001: `scripts/install_hooks.sh` provides an idempotent repository-local setup step. It sets only local `core.hooksPath`, preserves and reports conflicting hook configuration, and was applied locally; `git config --local --get core.hooksPath` returns `.githooks` and `.githooks/pre-commit` is executable.
- F-001 regression coverage now creates a fresh temporary Git repository, installs the hook, makes a safe real commit, and verifies real Git commits reject both staged synthetic secrets and prohibited private paths. The secret case changes the working-tree copy after staging, proving the hook scans the index.
- F-002: explicit roots passed to `safe_private_path` use the same absolute, existing-directory, non-symlink, repository-boundary validator as `JAE_DATA_DIR`. Tests cover valid roots, symlink roots, file roots, repository roots, traversal and symlink escapes.
- Corrective verification: `uv sync --locked` passed; `uv run python --version` reported Python 3.12.14; `uv run pytest` reported 10 passed; Ruff check and format check passed; mypy reported no issues in 3 source files. No lockfile regeneration was needed.

Re-review of corrective head `a1e7d43c2fd387c2f5b048a42ac59b69758b4aaa`: F-001 and F-002 are addressed by `cf60afb`; however required uv/Python 3.12 verification remains an unresolved gate because uv is unavailable in the review environment. Verdict: CHANGES REQUIRED. See the appended re-review in `docs/reviews/TASK-001.md`.

### TASK-001 independent verification gate (resolved)

Diff `a1e7d43..b2fce65` (current `HEAD`) is documentation-only (`docs/PROGRESS.md`, `docs/reviews/TASK-001.md`); no further implementation review was required. On the laptop checkout (`/Users/apple/Desktop/webapps/job-application-engine-handoff/job-application-engine`, Darwin 22.6.0 x86_64), `uv` was found at `/Users/apple/.local/bin/uv` (not on `PATH` in the review shell) and used by absolute path; no code/dependency/lockfile change was needed. Independently executed: `uv sync --locked` (resolved/checked, no changes needed), `uv run python --version` (`Python 3.12.14`), `uv run pytest` (10 passed), `uv run ruff check .` (all checks passed), `uv run ruff format --check .` (7 files already formatted), `uv run mypy src` (no issues in 3 source files). Hook activation and explicit-root regression tests were inspected and confirmed to exercise real `git commit` invocations and repository-boundary/symlink checks for both default and explicit roots. Verdict: **APPROVED**. Full detail in [TASK-001 review](reviews/TASK-001.md).

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
- Verification: `/Users/apple/.local/bin/uv sync --locked` passed; `/Users/apple/.local/bin/uv run python --version` reported Python 3.12.14; `/Users/apple/.local/bin/uv run pytest` reported 28 passed; Ruff check passed; Ruff format check reported 30 files already formatted; `/Users/apple/.local/bin/uv run mypy src` reported no issues in 21 source files; isolated `uv sync --project experiments/renderer --locked` passed; the local `.githooks` safeguard remains enabled. The experiment runner completed with all six synthetic RenderCV cases and the letter pass, five HTML candidate runs blocked by the unavailable browser, and the network probe blocked as intended.
- No applicant data, credentials, authenticated browser profile, UI, production renderer adapter, PDF export workflow, matching or TASK-006 work was added. The proposed RenderCV recommendation is conditional and is not an approval.

Next action: obtain an independent review of the exact TASK-005 commit and decide ADR-004; do not start TASK-006 before approval.

Independent TASK-005 review: CHANGES REQUIRED for implementation `dcc30ea05e7d51adbd384fe700c57cf459922fd1` (documentation head `4f5008f49e85f25d6215b4e00e4d0a53ee69bf2f`). Renderer reproduction exposed prefix-only extraction acceptance: long-wrapping and hostile-text lose complete claims while prefixes pass. Playwright remains correctly blocked by unavailable Chromium. See `docs/reviews/TASK-005.md`.
