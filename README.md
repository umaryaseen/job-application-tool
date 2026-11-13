# Job application engine

A local Python tool for preparing truthful job applications and retaining the exact documents reviewed and exported.

**Implemented:** profile/evidence validation, deterministic document plans, RenderCV/Typst PDF rendering, PDF/text QA, immutable snapshot/approval/export, and private draft JD intake. See [current progress](docs/PROGRESS.md) for integration/review states. A genuine applicant-approved baseline has not been accepted in the inspected repository.

**User workflow:** paste a JD → compare Applied AI and Full Stack base CVs → tailor a CV and cover letter → save JD/interview preparation → track company, submission, interviews and outcomes → analyze recurring skills. Intake is implemented; the remaining application steps are planned. See [workflow roadmap](docs/APPLICATION_WORKFLOW.md) and [repository audit](docs/REPOSITORY_AUDIT.md).

## Start here

1. Read [PROGRESS](docs/PROGRESS.md) and [AGENTS.md](AGENTS.md).
2. Use [local setup](docs/LOCAL_SETUP.md) for an existing checkout or fresh clone.
3. Continue with [the agent handoff](docs/CODEX_HANDOFF.md). Do not restart completed bootstrap tasks.

The user-selected source repository is currently public. Personal CVs, profiles, evidence, application outcomes and generated documents stay in an explicit private directory outside Git and CI. No real applicant data is bundled here. No project license has been selected; dependency/reference licenses remain their owners' licenses.

## Setup and checks

Requires Python 3.12 and `uv`. Production rendering and PDF measurement require macOS `sandbox-exec` and Poppler (`pdftotext`, `pdftoppm`, `pdfinfo`). Linux can run domain and simulated-process tests, but is not a supported production PDF environment.

```bash
uv sync --locked --group dev
./scripts/install_hooks.sh
export JAE_TYPST_PACKAGE_ROOT="$HOME/Library/Caches/jae/typst-packages"
uv run python scripts/setup_typst_packages.py --destination "$JAE_TYPST_PACKAGE_ROOT" --download
uv run jae --help
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -ra
```

CI targets a macOS Intel runner with isolation/tool preflight and the complete synthetic suite. Its actual result is required; a runner change alone does not establish rendering qualification. Missing isolation is never replaced with unisolated rendering.

The explicit setup command downloads only checksum-pinned public Typst package files. Builds use verified local copies in the correct package namespace and keep network denial enabled. They no longer depend on a warm global Typst cache. Run setup without `--download` to verify installed assets offline.

## Available commands

| Command | Behavior |
| --- | --- |
| `jae config-check` | Validate the private data root |
| `jae job-ingest` | Save bounded UTF-8 file/stdin, source metadata and immutable JD revisions |
| `jae job-show` | Verify and show a saved JD revision and its supplied metadata |
| `jae build-cv` | Render an explicitly reviewed profile and document plan into a PDF |
| `jae snapshot-build` | Create an immutable private PDF/TXT/QA/source snapshot |
| `jae snapshot-approve` | Record explicit review of that exact snapshot |
| `jae snapshot-export` | Revalidate current eligibility and export approved PDF/TXT bytes |
| `python -m job_application_engine.ats_qa` | Measure a PDF against independently supplied expectations |

Use `--help` for actual command arguments. Base comparison, requirement extraction, tailoring, letters, DOCX, interviews, tracking and skill analytics are not implemented commands yet. No application LLM, browser or submission integration is active.

## Save a vacancy

```bash
uv run jae job-ingest --text vacancy.md --job-id example-ai-role \
  --company "Example Company" --title "AI Engineer" --external-id "EX-42" --locale en
uv run jae job-show --job-id example-ai-role
```

Use `--text -` for pasted stdin, ending input with EOF. Reuse the job ID when a posting changes. The original UTF-8 bytes and normalized Markdown are kept separately; identical current input is deduplicated. All records remain draft. See [the intake guide](docs/JOB_INTAKE.md) for revision and metadata behavior.

## Baseline example

Set `JAE_DATA_DIR` to an existing absolute private directory outside the checkout. Inputs must already be curated and reviewed; this command does not invent or approve facts.

```bash
export JAE_DATA_DIR=/private/path/to/job-application-data
uv run jae build-cv \
  --profile /private/path/to/profile.json \
  --plan /private/path/to/document-plan.json \
  --reviews /private/path/to/reviews.json \
  --output-name baseline.pdf
```

Output goes under `JAE_DATA_DIR/outputs/`. Snapshot commands use private-root-relative inputs. [Architecture](docs/ARCHITECTURE.md) explains source/review/export rules; [DEPENDENCIES](docs/DEPENDENCIES.md) records locked tools. Research originals remain outside Git and are identified in [SOURCE_REGISTER](docs/SOURCE_REGISTER.md).
