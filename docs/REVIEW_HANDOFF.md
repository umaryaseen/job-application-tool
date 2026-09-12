# Handoff to an independent reviewer

Use this prompt in a **separate** coding-agent session. Review the focused
TASK-005 corrective implementation below; do not approve it as the
implementer.

```text
Independently re-review TASK-005 corrective findings F-001 and F-002.

Original TASK-005 implementation:
dcc30ea05e7d51adbd384fe700c57cf459922fd1
Original independent review: f91357338fcaf02ba6f5492ad598d258ad2cc121
Corrective implementation commits: 4b2f3eae32e59e8a6059bb3ae2d18dc1d75628a7, 180917a
Branch: task/005-renderer-experiment

Resolve both full corrective hashes; the latest corrective head is 180917a. Read AGENTS.md, docs/tasks/TASK-005.md,
docs/experiments/RENDERER_DECISION.md, docs/adr/ADR-004,
docs/adr/ADR-015, docs/PROGRESS.md and docs/reviews/TASK-005.md. Inspect the
complete corrective diff from the original implementation to the corrective
head and preserve the earlier review findings.

Reproduce the experiment using the locked baseline and experiment commands:
`/Users/apple/.local/bin/uv sync --locked`, Python 3.12, pytest, Ruff,
format, mypy, `uv sync --project experiments/renderer --locked`, and the
commands in experiments/renderer/README.md. Inspect every regenerated
RenderCV raster page. Confirm Playwright remains explicitly blocked on this
macOS 13 host rather than being treated as a pass.

For F-001, verify that the expected content is an independent ordered oracle
including static headings and every claim, and that BOTH Poppler and pypdf
must match the complete content. Check the narrow normalization rules for
NFC, soft hyphens, date hyphens, split HTTP(S) schemes and whitespace. Confirm
that punctuation, numbers, units, negation and qualifiers remain meaningful.
Run or inspect the negative controls for suffix removal, qualification change,
duplication, reordering and unexpected content. Confirm any complete-content
failure makes the experiment unsuccessful even when PDF generation succeeds.
Reproduce long-wrapping and hostile-text cases and inspect their corrected
results, hashes and Unicode/security behavior.

For F-002, verify the ADR-004 qualification: the planned two-engine quality
comparison was not completed; Playwright package setup succeeded but Chromium
installation failed with the recorded macOS 13 error; HTML/Playwright layout,
extraction, raster and browser security remain untested; no cross-platform or
comparative-quality claim is made; and reconsideration triggers and the
no-backend/TASK-006 gate are explicit. Do not accept ADR-004 or start
TASK-006.

Confirm no applicant data, credentials, authenticated browser profile,
production renderer, UI, matching, export workflow or unrelated feature was
introduced. Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in
a new sanitized docs/reviews/TASK-005.md report with exact reviewed commit
IDs and update PROGRESS with the actual verdict. Do not modify implementation,
merge, force-push or self-approve.
```
