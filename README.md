# job-application-engine

A local application compiler for full-time job applications in Germany: approved career facts → a readable baseline CV → job requirements → evidence matching → tailored documents → checks → human review.

**Status: TASK-006 implemented — awaiting independent review.** The repository
contains a synthetic, private-staging RenderCV/Typst baseline adapter; no real
applicant profile or approved final CV is included. See [actual progress](docs/PROGRESS.md).

## Start here

1. Read [the brief](docs/PROJECT_BRIEF.md) and [research synthesis](docs/RESEARCH_SYNTHESIS.md).
2. Read [architecture](docs/ARCHITECTURE.md), [decisions](docs/adr/README.md), and [acceptance criteria](docs/ACCEPTANCE_CRITERIA.md).
3. Follow [LOCAL_SETUP.md](docs/LOCAL_SETUP.md) to restore the supplied Git bundle on your laptop and create a **private** GitHub repository when authenticated.
4. Give local Codex [CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md), which starts exactly one task. All agents must follow [AGENTS.md](AGENTS.md).

The original three research reports accompany the downloadable handoff **outside the Git repository**. [SOURCE_REGISTER.md](docs/SOURCE_REGISTER.md) identifies them by title, checksum, and section/line references. They are design research, not verified applicant facts.

## First delivery

M1 must take a manually reviewed career profile, validate facts and evidence, render an ATS-safe English CV suitable for an English-language German vacancy, verify extracted text and layout, and record approval of the exact output. German text handling is tested from the beginning; full German content localization is later.

No LLM, database server, HTTP server, scraper, browser session, or job-board account is needed for M1. The `jae build-cv` command is available for explicitly supplied profile, plan and local review JSON; later commands remain planned contracts.

## Recommended foundation

| Concern | Plan |
|---|---|
| Runtime | Python 3.12, one package, synchronous CLI |
| Career source | Versioned custom JSON with typed facts, evidence and approved text variants |
| Interchange | JSON Resume adapter later; its schema does not govern provenance |
| First PDF | RenderCV 2.8/Typst 0.15.0 current-laptop adapter; independent review remains required |
| Storage | Private JSON and immutable file snapshots first; SQLite for tracking later |
| Matching | Exact and reviewed aliases first; optional local multilingual retrieval |
| AI | Provider interface introduced only when needed; disabled by default |
| Publication | Private source repository; personal inputs and outputs excluded |

## Non-negotiable behavior

Every candidate claim, including headings that assert a professional title, must resolve to approved facts and evidence at specific revisions. An unrelated evidence ID is insufficient. Unsupported claims fail validation. AI cannot grant its own approvals. Requirement coverage and parser checks are reported separately; the system does not advertise a universal ATS score.

Milestones: **M0 plan → M1 usable baseline → M2 match matrix → M3 tested tailoring MVP → M4 letters/tracker → M5 optional enhancements**. The issue-sized backlog and gates are in [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md).

The repository is private development work. No open-source license has been selected for the project's original code. Dependency and reference licenses remain their owners' licenses; see [DEPENDENCIES.md](docs/DEPENDENCIES.md).

## Baseline PDF build

Set `JAE_DATA_DIR` to an existing private directory outside this checkout and
run the locked environment. The command requires an explicitly validated
DocumentPlan, its profile revision and the local human review receipts; it does
not infer or approve content:

```bash
export JAE_DATA_DIR=/private/path/to/job-application-data
uv run jae build-cv \
  --profile /private/path/to/profile.json \
  --plan /private/path/to/document-plan.json \
  --reviews /private/path/to/reviews.json \
  --output-name baseline.pdf
```

The PDF is published under `JAE_DATA_DIR/outputs/` after isolated RenderCV/Typst
completion. The current production support scope requires macOS
`sandbox-exec`; the adapter fails clearly instead of rendering without network
isolation. Candidate strings are inserted as literal text, and arbitrary
templates, remote fonts, links, includes and fallback backends are not accepted.
