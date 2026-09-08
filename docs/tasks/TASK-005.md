# TASK-005: Run the renderer decision experiment

- Milestone: M1
- State at planning handoff: NOT STARTED
- Estimate: 3–5 h; planning range, excludes unresolved human input and review waiting
- Dependencies: [TASK-004](TASK-004.md)
- Decisions: [ADR-004](../adr/ADR-004.md), [ADR-013](../adr/ADR-013.md), [ADR-015](../adr/ADR-015.md)

## Objective

Run the renderer decision experiment.

## Background

Research disagrees between RenderCV and HTML/Playwright. The actual laptop and our fixture/security requirements must decide, with one production winner.

## Affected modules

experiments/renderer/; docs/experiments/RENDERER_DECISION.md; ADR-004; tests/fixtures/rendering/. Paths are intended additions unless already present; inspect before editing.

## Acceptance criteria

Render identical short/two-page/DE-Unicode plans in minimal RenderCV and HTML/Playwright spikes. Record versions, install friction, extraction order/fields, A4 pages, hostile-text handling, local font behavior and raster review. Validate no arbitrary includes or network requests. Recommend one backend and obtain independent review before changing ADR status. Record failures honestly.

## Tests required

A08–A14 experimental results with real engines and Poppler/pypdf where available. Show output/repro steps and measured findings; candidate failures remain in report. No winner if neither meets mandatory gates.

Run relevant tests plus Ruff and mypy once tooling exists. Record actual results and skipped checks. Test IDs refer to [ACCEPTANCE_CRITERIA.md](../ACCEPTANCE_CRITERIA.md). Use sanitized fixtures; no personal test artifacts in Git/CI.

## Explicit non-goals

Do not implement both full production adapters, add UI/browser sessions, or call vendor ATS claims a passing test. Do not switch backends silently.

## Handoff and review

Follow AGENTS.md, inspect dependencies and source/ADR context, work on `task/005-short-description`, and implement this task only. Update PROGRESS with actual commands/results, risks and next task; commit as IMPLEMENTED — AWAITING REVIEW. An independent reviewer inspects code/diff/tests/security/acceptance using REVIEW_PROTOCOL. The implementer cannot approve their own work. Additional corrections should be narrow commits preserving negative tests.
