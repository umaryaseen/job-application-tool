# CLEANUP-001 — reconcile current state and reduce overhead

Base: `3c562fe1c3de0239a129fad10804abd375c1d38e`.
State: implementation candidate; independent review required.

## Objective

Audit existing code, remove stale startup instructions and repeated active-state claims, and align CI with the existing renderer. Map the requested application workflow onto the current engine without adding another framework.

## Acceptance

- Active README/setup/handoffs reflect integrated TASK-008 and unimplemented application features; no TASK-001 restart or incorrect private-repository claim.
- Current progress is short, historical evidence stays linked, and agent reading is task-scoped. Factuality and independent-review gates remain.
- Complete CI uses an explicit macOS Intel runner with isolation/Poppler preflight. No renderer tests are removed or broadly skipped. Two simulated process tests work without host isolation.
- Staged deletion permits cleanup, while replacement/renamed content remains scanned.
- Roadmap covers two-base comparison, CV/letter PDF/DOCX, faithful JD MD, interview knowledge, outcomes and skill-demand analysis. Planned commands are not advertised as implemented.
- Repair any cold-cache renderer package prerequisite exposed by the complete CI run, with pinned public assets, explicit setup, local integrity tests and unchanged runtime network denial. No new Python dependencies, personal data, profile/schema/export-policy changes or submissions.

## Checks

Run focused hook/simulated-renderer tests, Ruff check/format, mypy and Markdown-link validation. Record the full-suite result on the actual host. CI must run the complete suite with real macOS isolation/Poppler. Linux missing-isolation failures are not passes. Review ADR-017 and the exact candidate independently.
