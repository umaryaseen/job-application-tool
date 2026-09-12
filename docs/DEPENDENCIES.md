# Dependency and component register

No runtime dependencies have been installed or locked for this project yet. Versions below are **not selected** unless an introducing task records its actual resolution. Do not create a speculative lockfile. Prefer the standard library where it solves the task directly.

| Component | Purpose | Stage / status | License or review note |
|---|---|---|---|
| Python 3.12 | Single runtime | TASK-001, target | Record patch/platform; avoid runtime matrix until needed |
| uv | Environment/package locking | TASK-001 | Development tool; verify current version and upstream license |
| argparse, json, pathlib, hashlib, decimal, datetime, sqlite3 | CLI, serialization, paths, hashes, typed numbers/dates, later tracker | Standard library | No trivial wrapper dependency |
| Pydantic 2 | Strict domain validation / JSON Schema export | TASK-002 | Verify pinned version/license; extra=forbid and explicit validators |
| pytest | Regression/integration tests | TASK-001 | Development only; actual feature tests required |
| Ruff / mypy | Lint/format/type gates | TASK-001 | Development only; pin and record |
| Gitleaks or a justified mature alternative | Staged/history secret detection | TASK-001 | Tool, no applicant uploads; record version/config and safe synthetic test |
| RenderCV | Candidate PDF backend | TASK-005 experiment, then 006 if chosen | Upstream declares MIT; inspect exact version/transitives and theme API |
| Typst and font assets | RenderCV engine/design dependencies | With selected backend | Pin versions/checksums and attribution; no external content includes |
| Jinja2 + Playwright/Chromium | Alternative renderer experiment | TASK-005 only unless chosen | Escaping, browser install and network isolation tested; do not keep unused backend |
| pypdf | Independent PDF text/page extraction | TASK-007 | Check pinned release license; no OCR/upload requirement |
| Poppler pdftotext/pdftoppm | Independent text/geometry and page raster QA | TASK-005/007 system tools | Record OS package/version; check redistribution terms if bundling tools later |
| python-docx | Direct validated-plan DOCX output | TASK-024 | Upstream library creates/updates DOCX; verify exact version/license |
| Sentence Transformers + model runtime | Optional local semantic retrieval | TASK-029 | Separate extra; library/model licenses separate; pin model revision/checksums |
| ESCO EN/DE data | Optional skill concept enrichment | TASK-026 | Classification attribution/reuse terms separate from EUPL API software; no service install |
| Provider SDK or HTTP client | Optional model proposals | TASK-031 | One chosen adapter; no vendor dependency in core |
| JSON Resume schema | Interchange validation | TASK-030 | Use current monorepo schema and pinned revision; license/notice preserved if vendored |
| spaCy, KeyBERT, SkillNER | Possible NLP helpers | Not selected | Need a concrete measured requirement before adding |
| Resume Matcher / Reactive Resume | Workflow/UI references | Study only | No implementation copied, no runtime dependency |
| OpenResume / pyresparser | Optional parser comparison | TASK-034 evaluation only | AGPL/GPL concerns; do not assert process isolation removes obligations |

Every addition must record: name, exact installed version, upstream URL, purpose, task/ADR, runtime/dev/optional group, license source, transitive or asset concerns, lockfile location, offline behavior and alternatives considered. Optional libraries cannot become mandatory imports in baseline paths.

Upstream observations made on 2026-09-08: [RenderCV](https://github.com/rendercv/rendercv), [Pydantic strict validation](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/), [python-docx](https://python-docx.readthedocs.io/en/latest/), [Sentence Transformers](https://sbert.net/docs/sentence_transformer/pretrained_models.html). These pages confirm capabilities, not suitability on the unseen laptop. Recheck exact APIs at implementation.
## TASK-001 direct dependencies

| Package | Locked version | Use | License source | Introduced |
|---|---:|---|---|---|
| pytest | 8.4.1 | Synthetic unit and security-boundary tests | PyPI metadata | TASK-001 |
| Ruff | 0.12.11 | Lint and format checks | PyPI metadata | TASK-001 |
| mypy | 1.17.1 | Static type checking | PyPI metadata | TASK-001 |

The runtime package uses only the Python 3.12 standard library. `setuptools` is
the build backend and is not imported at runtime. No model, renderer, network,
database, or applicant-data dependency is installed by TASK-001.
