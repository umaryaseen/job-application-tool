# Implementation plan

Planning state: no application task is implemented. This backlog is a set of issue-sized handoffs, not a command to implement the whole architecture at once. Status lives in PROGRESS; initial task-file state is a planning baseline.

## Execution rules

Start with TASK-001 after restoring the planning Git history locally. Each task reads AGENTS, architecture, relevant ADRs, source context, acceptance and progress. Use a feature branch, focused tests, a commit and independent review. A dependent task starts only after prerequisites are reviewed. No major feature may approve its own architecture.

Milestones progress in order: M1 genuine baseline → M2 requirement matrix → M3 tailored CV with validation → M4 letter/tracker. No later work substitutes for an incomplete first usable CV. Optional M5 tasks can be prioritized after M3/M4 according to their dependencies, without silently widening MVP scope.

## Milestones

| Milestone | Tasks | Exit |
|---|---|---|
| M0 | Planning package | Independently reviewed architecture and exact local handoff |
| M1 | 001–009 | Real applicant-reviewed baseline PDF/TXT; tests and rendering review |
| M2 | 010–016 | Reviewed EN/DE requirements and evidence matrix |
| M3 | 017–020 | Tested tailoring MVP with strict claim and export gates |
| M4 | 021–023 | Cover letter and SQLite tracker |
| M5 | 024–034 | Separate optional decisions/features, each reviewed |
| Later | 035 | Policy/handoff design only; no implemented portal integration |

## Backlog

| Task | Milestone | Objective | Dependencies | Estimate |
|---|---|---|---|---|
| [TASK-001](tasks/TASK-001.md) | M1 | Bootstrap the local Python project and commit safeguards | M0 | 2–4 h |
| [TASK-002](tasks/TASK-002.md) | M1 | Define strict profile and typed fact schemas | 001 | 3–5 h |
| [TASK-003](tasks/TASK-003.md) | M1 | Enforce evidence graph and reviewed wording bindings | 002 | 4–6 h |
| [TASK-004](tasks/TASK-004.md) | M1 | Compile the baseline document plan and text | 003 | 3–5 h |
| [TASK-005](tasks/TASK-005.md) | M1 | Run the renderer decision experiment | 004 | 3–5 h |
| [TASK-006](tasks/TASK-006.md) | M1 | Implement the chosen deterministic PDF adapter | 005 | 3–5 h |
| [TASK-007](tasks/TASK-007.md) | M1 | Implement PDF and ATS robustness checks | 006 | 4–6 h |
| [TASK-008](tasks/TASK-008.md) | M1 | Create immutable snapshots and hash-bound approval/export | 007 | 4–6 h |
| [TASK-009](tasks/TASK-009.md) | M1 | Curate and accept the first genuine baseline CV | 008 | 2–4 h plus applicant review |
| [TASK-010](tasks/TASK-010.md) | M2 | Ingest pasted job descriptions as immutable snapshots | 009 | 2–3 h |
| [TASK-011](tasks/TASK-011.md) | M2 | Extract source-grounded requirement candidates | 010 | 3–5 h |
| [TASK-012](tasks/TASK-012.md) | M2 | Classify priorities, negation and alternatives | 011 | 3–5 h |
| [TASK-013](tasks/TASK-013.md) | M2 | Normalize skills with a reviewed alias dictionary | 012 | 2–4 h |
| [TASK-014](tasks/TASK-014.md) | M2 | Add requirement review and correction versions | 012, 013 | 2–4 h |
| [TASK-015](tasks/TASK-015.md) | M2 | Evaluate scoped hard requirements and experience intervals | 014 | 3–5 h |
| [TASK-016](tasks/TASK-016.md) | M2 | Produce the evidence matrix and accept M2 | 015 | 3–5 h |
| [TASK-017](tasks/TASK-017.md) | M3 | Select evidence-backed tailored content | 016 | 3–5 h |
| [TASK-018](tasks/TASK-018.md) | M3 | Enforce a deterministic rendered page budget | 017 | 3–5 h |
| [TASK-019](tasks/TASK-019.md) | M3 | Harden claim, numeric and privacy adversarial validation | 018 | 3–5 h |
| [TASK-020](tasks/TASK-020.md) | M3 | Validate and release the first tailoring MVP | 019 | 2–4 h |
| [TASK-021](tasks/TASK-021.md) | M4 | Plan cover letters from approved claims and motivation | 020 | 3–5 h |
| [TASK-022](tasks/TASK-022.md) | M4 | Render and review one-page cover letters | 021 | 2–4 h |
| [TASK-023](tasks/TASK-023.md) | M4 | Add SQLite application tracking and accept M4 | 022 | 4–6 h |
| [TASK-024](tasks/TASK-024.md) | M5 | Add direct DOCX export | 020 | 3–5 h |
| [TASK-025](tasks/TASK-025.md) | M5 | Add approved German document localization | 020 | 3–5 h plus applicant language review |
| [TASK-026](tasks/TASK-026.md) | M5 | Import optional versioned ESCO data | 016 | 3–5 h plus official data acquisition |
| [TASK-027](tasks/TASK-027.md) | M5 | Define a frozen semantic retrieval benchmark | 016 | 2–4 h |
| [TASK-028](tasks/TASK-028.md) | M5 | Define bounded model proposal interfaces | 020 | 2–4 h |
| [TASK-029](tasks/TASK-029.md) | M5 | Benchmark and optionally enable local semantic retrieval | 027 | 3–5 h |
| [TASK-030](tasks/TASK-030.md) | M5 | Add JSON Resume interchange with loss reporting | 020 | 2–4 h |
| [TASK-031](tasks/TASK-031.md) | M5 | Implement one explicitly selected model adapter | 028 | 3–5 h plus provider choice |
| [TASK-032](tasks/TASK-032.md) | M5 | Design the smallest local review UI from observed friction | 020 | 2–3 h |
| [TASK-033](tasks/TASK-033.md) | M5 | Add portable backup, selective deletion and basic outcome analytics | 023 | 4–6 h |
| [TASK-034](tasks/TASK-034.md) | M5 | Evaluate an optional independent resume parser | 020 | 2–4 h |
| [TASK-035](tasks/TASK-035.md) | LATER | Specify a permitted application-page handoff boundary | 023 | 2–3 h |

## Estimates and scope controls

Estimates are ranges for focused engineering work and are deliberately not scheduled calendar promises. The full task breakdown includes review/testing absent from the reports’ shortest prototype estimate. Re-estimate after the renderer spike and genuine M1 profile curation. Split work that runs beyond roughly one focused day into a coherent follow-up issue with its own acceptance criteria; do not hide new requirements in the original issue.

TASK-005 is a small experiment; do not build two production renderers. TASK-029 requires a real model benchmark; disabled/skipped optional tests cannot imply success. TASK-032 and TASK-035 are design-only tasks that may conclude no additional implementation is justified. TASK-009/TASK-025 require applicant data/wording review. Missing facts are a bounded input need, not permission to fill them from memory.

## Research disagreement handling during implementation

If a library API, test result or hardware limit contradicts an ADR assumption, stop only the affected work. Preserve a reproducible finding, alternatives and recommendation in the ADR/experiment report. The separate reviewer decides the engineering change. Continue unrelated already-authorized work when useful; do not install infrastructure to make an experiment look successful.

## Definition of task completion

Code/docs exist, relevant tests/lint/types passed or an explicit gate remains blocked, staged diff contains no sensitive material, PROGRESS reflects actual results, a normal Git commit exists, and independent review records a verdict. “Implemented” and “approved” remain different states. A milestone also needs its user-visible artifacts and human document review; synthetic tests alone cannot complete M1.
