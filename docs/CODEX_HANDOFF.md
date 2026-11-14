# Continue the existing engine

Use this prompt in Codex or Claude Code in the actual checkout. A separate reviewer supplies the independent verdict.

```text
Continue the existing job-application engine. Do not restart bootstrap or create
a second canonical profile, tracker or renderer.

Inspect working tree, branch and AGENTS.md. Read PROGRESS, the assigned task,
and affected design/ADR/acceptance/security sections. Read APPLICATION_WORKFLOW
for the requested user journey. Check for unpublished local work.

Use the next unblocked reviewed task from PROGRESS. TASK-001–008 are integrated.
The next product gate is TASK-009: reconcile the real private canonical profile
and Applied AI / Full Stack bases, preserve their evidence and versions, and
obtain actual baseline document acceptance. Existing files do not establish it.

ADR-020 separately permits TASK-010 draft JD intake before that personal gate.
Check PROGRESS before choosing work: do not restart already implemented intake
or interpret a stored posting as personal baseline acceptance.

Then follow the workflow roadmap and existing task dependencies: preserve a JD,
compare both bases, produce a tailored CV and letter, retain MD/interview notes,
and update a private job record. Do not implement all historical optional tasks
or add models/UI/source integrations just to deliver the first application.

Keep personal data under the existing JAE_DATA_DIR, outside Git/CI. Preserve
facts, unknowns, prototype status, source approvals and exact-output review.
Do not infer application outcomes or submit applications.

Use a task branch. Run relevant tests plus required lint/types; use the supported
macOS environment for full PDF verification and disclose blocked/skipped checks.
Update PROGRESS, commit the reviewable result, and hand the exact base/head to
a separate reviewer using REVIEW_HANDOFF. Do not merge your own unreviewed work.
```

When handing off due to limits, record task, branch/base/head, changed files, measured test results, findings, private input references without their contents, and the single next action. Git and PROGRESS remain the implementation record.
