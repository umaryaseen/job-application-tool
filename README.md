# job-application-engine

A local application compiler for full-time job applications in Germany: approved career facts → a readable baseline CV → job requirements → evidence matching → tailored documents → checks → human review.

**Status: planning repository. Application code has not been implemented.** The first implementation task is [TASK-001](docs/tasks/TASK-001.md). No CV, test pass rate, local laptop setup, or GitHub repository is claimed by this package. See [actual progress](docs/PROGRESS.md).

## Start here

1. Read [the brief](docs/PROJECT_BRIEF.md) and [research synthesis](docs/RESEARCH_SYNTHESIS.md).
2. Read [architecture](docs/ARCHITECTURE.md), [decisions](docs/adr/README.md), and [acceptance criteria](docs/ACCEPTANCE_CRITERIA.md).
3. Follow [LOCAL_SETUP.md](docs/LOCAL_SETUP.md) to restore the supplied Git bundle on your laptop and create a **private** GitHub repository when authenticated.
4. Give local Codex [CODEX_HANDOFF.md](docs/CODEX_HANDOFF.md), which starts exactly one task. All agents must follow [AGENTS.md](AGENTS.md).

The original three research reports accompany the downloadable handoff **outside the Git repository**. [SOURCE_REGISTER.md](docs/SOURCE_REGISTER.md) identifies them by title, checksum, and section/line references. They are design research, not verified applicant facts.

## First delivery

M1 must take a manually reviewed career profile, validate facts and evidence, render an ATS-safe English CV suitable for an English-language German vacancy, verify extracted text and layout, and record approval of the exact output. German text handling is tested from the beginning; full German content localization is later.

No LLM, database server, HTTP server, scraper, browser session, or job-board account is needed for M1. The target CLI is called `jae`; commands shown in the architecture are **planned contracts**, not currently available commands.

## Recommended foundation

| Concern | Plan |
|---|---|
| Runtime | Python 3.12, one package, synchronous CLI |
| Career source | Versioned custom JSON with typed facts, evidence and approved text variants |
| Interchange | JSON Resume adapter later; its schema does not govern provenance |
| First PDF | RenderCV candidate; local rendering comparison must pass ADR-004 before adoption |
| Storage | Private JSON and immutable file snapshots first; SQLite for tracking later |
| Matching | Exact and reviewed aliases first; optional local multilingual retrieval |
| AI | Provider interface introduced only when needed; disabled by default |
| Publication | Private source repository; personal inputs and outputs excluded |

## Non-negotiable behavior

Every candidate claim, including headings that assert a professional title, must resolve to approved facts and evidence at specific revisions. An unrelated evidence ID is insufficient. Unsupported claims fail validation. AI cannot grant its own approvals. Requirement coverage and parser checks are reported separately; the system does not advertise a universal ATS score.

Milestones: **M0 plan → M1 usable baseline → M2 match matrix → M3 tested tailoring MVP → M4 letters/tracker → M5 optional enhancements**. The issue-sized backlog and gates are in [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md).

The repository is private development work. No open-source license has been selected for the project's original code. Dependency and reference licenses remain their owners' licenses; see [DEPENDENCIES.md](docs/DEPENDENCIES.md).
