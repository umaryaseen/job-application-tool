# Progress — authoritative implementation state

Last updated: 2026-09-12. TASK-001 is IMPLEMENTED — AWAITING REVIEW.

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
| TASK-001 | IMPLEMENTED — AWAITING REVIEW | Corrective commits address independent review findings; re-review exact corrective head |
| TASK-002–009 / M1 | NOT STARTED | First actual CV milestone; applicant curation still required |
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

1. Local Codex restores repository and implements TASK-001.
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
