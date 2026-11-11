# Repository audit — 11 November 2026

Inspected GitHub main `3c562fe1c3de0239a129fad10804abd375c1d38e`, full tree, source/CLI/tests, review history and locked environment. Only main and no open PRs were exposed at inspection. Unpushed workstation code and private applicant files are outside the audit.

## Developed versus planned

| Area | Observed state |
| --- | --- |
| Package/CLI and private data paths | Implemented |
| Typed facts, evidence and reviewed wording | Implemented |
| Deterministic baseline plan/text | Implemented |
| RenderCV/Typst PDF build | Implemented; macOS isolation required |
| PDF/text/geometry QA | Implemented; isolation and Poppler required |
| Snapshot/approval/export | Implemented; TASK-008 correction approved and integrated |
| Genuine applicant baseline | TASK-009 not accepted in inspected repository |
| JD intake, extraction and base matching | Planned |
| Tailoring, letters, DOCX, interviews and tracker | Planned |

## Cleanup findings

| Finding | Effect | Change |
| --- | --- | --- |
| README says TASK-006; PROGRESS header says TASK-008 awaiting review despite final approval/merge | Restarted work and resolved gates look blocked | Reconcile from exact Git/review evidence |
| Setup/handoff assumes old bundle, no remote and unstarted TASK-001 | Repeated bootstrap/authentication overhead | Existing-checkout setup and continuation prompt |
| Active progress mixes current state with long superseded execution history | Excess context and contradictory instructions | Linked historical log, short current state |
| Every task must reread all large design documents | Avoidable context cost | Task-scoped reads; preserve affected rules and review |
| Ubuntu CI versus mandatory macOS renderer/measurement | Full suite fails before expected assertions | macOS Intel CI, isolation/Poppler preflight, complete suite |
| Two simulated process tests need real macOS tool discovery | Wrong failure branch on Linux | Stub only their isolation locator |
| Staged-file guard reads deleted paths from index | Legitimate cleanup commits fail | Filter deleted paths while retaining content checks |
| Large speculative backlog obscures application journey | Risk of another parallel framework | Map user workflow onto existing tasks |

There is no basis to delete provenance, validation, QA or immutable export as unused overhead: current CLI/tests exercise them. The renderer experiment is not a second production backend; test helpers still import it. A later cleanup could extract those helpers before retiring experiment code. No production source module or dependency was removed here.

## Baseline evidence

Locked sync succeeded with Python 3.12.14; Ruff check/format and mypy passed. Full Linux `uv run pytest -ra` produced **53 passed, 25 failed, 3 skipped**. Observed failures stem from missing macOS isolation, including unmeasured PDF reports and the two simulated tests. Local ignored evidence: `artifacts/verification/cleanup-001/baseline.xml`.

Post-change results, CI and review are recorded in PROGRESS. The source repository is public; private applicant data remains outside Git/CI. Visibility was not changed.
