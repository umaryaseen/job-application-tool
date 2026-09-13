# Dependency and component register

Versions below are **not selected** unless an introducing task records its actual resolution. The TASK-001 lockfile contains the immediate development tools; TASK-002 adds the pinned Pydantic runtime dependency. Prefer the standard library where it solves the task directly.

| Component | Purpose | Stage / status | License or review note |
|---|---|---|---|
| Python 3.12 | Single runtime | TASK-001, target | Record patch/platform; avoid runtime matrix until needed |
| uv | Environment/package locking | TASK-001 | Development tool; verify current version and upstream license |
| argparse, json, pathlib, hashlib, decimal, datetime, sqlite3 | CLI, serialization, paths, hashes, typed numbers/dates, later tracker | Standard library | No trivial wrapper dependency |
| Pydantic 2 | Strict domain validation / JSON Schema export | TASK-002, TASK-006 | MIT; pinned to 2.12.5 in `pyproject.toml`/`uv.lock`; RenderCV 2.8 requires >=2.12.5; extra=forbid and explicit validators |
| pytest | Regression/integration tests | TASK-001 | Development only; actual feature tests required |
| Ruff / mypy | Lint/format/type gates | TASK-001 | Development only; pin and record |
| Gitleaks or a justified mature alternative | Staged/history secret detection | TASK-001 | Tool, no applicant uploads; record version/config and safe synthetic test |
| RenderCV | Candidate PDF backend and trusted YAML-to-Typst adapter | TASK-006 | MIT; pinned `rendercv[full]==2.8` in `pyproject.toml`/`uv.lock`; runs in the isolated production worker |
| Typst | Local PDF compiler used by RenderCV | TASK-006 | Apache-2.0; pinned `typst==0.15.0`; package path is local and network-denied |
| rendercv-fonts | Pinned local font assets | TASK-006 | MIT; pinned `rendercv-fonts==0.5.1`; only bundled font folders are passed to Typst |
| pypdf | Independent production PDF text regression extraction | TASK-006/TASK-007 runtime QA | BSD-3-Clause; pinned `pypdf==6.18.1` in the runtime set; no applicant upload or OCR |
| Jinja2 + Playwright/Chromium | Alternative renderer experiment | TASK-005 only unless chosen | Escaping, browser install and network isolation tested; do not keep unused backend |
| pypdf | Independent PDF text/page extraction | TASK-007 | BSD-3-Clause; pinned `pypdf==6.18.1` in the runtime set; no OCR/upload requirement |
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
## Historical bootstrap and TASK-002 dependency record

This table retains the TASK-001 development pins and the dependency recorded
when TASK-002 was implemented. The Pydantic row is historical and superseded;
it is not the current runtime pin.

| Package | Locked version | Use | License source | Introduced |
|---|---:|---|---|---|
| pytest | 8.4.1 | Synthetic unit and security-boundary tests | PyPI metadata | TASK-001 |
| Ruff | 0.12.11 | Lint and format checks | PyPI metadata | TASK-001 |
| mypy | 1.17.1 | Static type checking | PyPI metadata | TASK-001 |
| pydantic | 2.11.7 | Strict profile/fact models and JSON Schema export | MIT / PyPI metadata; **historical TASK-002 pin, superseded by TASK-006** | TASK-002 |

TASK-002 adds Pydantic as the runtime validation dependency. `setuptools` is
the build backend and is not imported at runtime. No renderer, network,
database, model, import adapter, or applicant-data dependency is installed.

## TASK-005 isolated renderer experiment

These dependencies are intentionally outside the baseline runtime and are
locked in `experiments/renderer/uv.lock`:

| Package | Locked version | Purpose | License/source | Offline note |
|---|---:|---|---|---|
| RenderCV | 2.8 | YAML-to-Typst experiment | MIT; [upstream](https://github.com/rendercv/rendercv) | Runs with the local package and template |
| typst | 0.15.0 | Local Typst compiler binding | Apache-2.0; [typst-py](https://github.com/messense/typst-py) | Compiles from local input/package paths |
| rendercv-fonts | 0.5.1 | Pinned local fonts | MIT; [upstream](https://github.com/rendercv/rendercv-fonts) | Font directories are passed explicitly |
| Playwright | 1.62.0 | HTML/Chromium candidate | Apache-2.0; [Python package](https://playwright.dev/python/docs/library) | Browser download is separate and was blocked on macOS 13 |
| pypdf | 6.18.1 | Independent PDF text extraction | BSD-3-Clause; [docs](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | Used only by the experiment venv |

The experiment's Playwright dependency remains outside the baseline lockfile.
Poppler 25.08.0 (`pdftotext`, `pdftoppm`) is a host measurement tool and is not
bundled.

## TASK-006 production adapter and TASK-007 QA

The selected current-laptop backend is installed by the root locked
environment: RenderCV 2.8 (full extra), Typst 0.15.0 and rendercv-fonts 0.5.1.
RenderCV 2.8 requires Pydantic 2.12.5, so the TASK-002 pin was raised to that
compatible patch line and re-locked. `pypdf` is runtime QA extraction coverage; Poppler remains a separately installed host QA tool. The production
adapter does not import or use the ignored experiment virtual environment.

The current runtime pins are `pydantic==2.12.5` and `pypdf==6.18.1` in `pyproject.toml` and `uv.lock`.
On 2026-09-13, installed RenderCV metadata reported
`Requires-Dist: pydantic[email]>=2.12.5` (and
`pydantic-extra-types>=2.11.0`). The locked project graph records
`rendercv[full]==2.8` and `pydantic==2.12.5`; no dependency or lockfile change
is part of this documentation correction.

The adapter invokes a worker under macOS `sandbox-exec` with
`(deny network*)`; it passes only local package/font paths, fixed template
settings and private staging files. It fails closed when that isolation
mechanism is unavailable. This is a current macOS 13.6.9 x86_64 support scope,
not a cross-platform promise. No Playwright dependency is installed in the
production environment. TASK-007 promotes the unchanged pypdf pin from the
TASK-006 development record to runtime because the QA command invokes it as
an independent extractor; no dependency or lockfile regeneration was needed.
