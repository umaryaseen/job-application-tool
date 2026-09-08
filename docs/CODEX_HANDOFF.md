# Exact local Codex handoff — start TASK-001

Open the extracted handoff folder or restored repository in local Codex and paste the following. The original reports are supplied alongside the bundle, outside the repository.

```text
You are implementing job-application-engine locally on my laptop.
This is an authorized incremental implementation, starting with TASK-001.

First inspect the current folder, applicable AGENTS.md, Git state and local
OS/tooling. Do not overwrite or modify unrelated repositories.

If this is the extracted handoff folder, follow repository/docs/LOCAL_SETUP.md:
verify job-application-engine.bundle and clone it to a new local directory
named job-application-engine. Preserve the bundle's existing Git history.
If already inside the restored repository, do not initialize or clone again.
Keep original research-inputs outside Git, resolving JAE_RESEARCH_ROOT to
their actual location. Verify hashes from docs/research-manifest.json.

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/RESEARCH_SYNTHESIS.md,
docs/ARCHITECTURE.md, docs/IMPLEMENTATION_PLAN.md,
docs/ACCEPTANCE_CRITERIA.md, docs/SECURITY_AND_PRIVACY.md,
docs/PROGRESS.md, docs/tasks/TASK-001.md and its ADRs.
Inspect the actual implementation state before changing anything.

Restore/configure the private GitHub origin if gh is present and authenticated,
following LOCAL_SETUP. Verify the intended repository is PRIVATE before push.
Never expose tokens, overwrite an unrelated origin, or force-push. If native
authentication needs my interaction, prepare all safe local work first and
ask only for that authentication step; do not ask me to paste credentials.
Missing remote access must be reported honestly and must not prevent the
local task from being prepared and committed for review.

Implement TASK-001 ONLY on task/001-project-bootstrap from reviewed main.
The objective is a Python 3.12 package/CLI, locked immediate tooling, explicit
private-data configuration, commit safeguards, synthetic tests and minimal CI.
Follow the task's affected modules, acceptance criteria, tests and non-goals.
Use the standard library for trivial work; document each actual dependency.
Do not implement schemas, rendering, AI, matching, UI, database, scraping or
application submission in this task. Do not add personal data.

Run the relevant real tests, Ruff and mypy. Inspect failures rather than
weakening/deleting tests. Review the full staged diff for personal information
and secrets. Update docs/PROGRESS.md with what actually exists, commands,
results, limitations and next task. Commit with normal Git history and mark
TASK-001 IMPLEMENTED — AWAITING REVIEW, not self-approved.

Return the local repository path, branch, commit hash, actual test results,
GitHub URL/privacy only if verified, remaining blockers, and a filled-out
docs/REVIEW_HANDOFF.md prompt for a SEPARATE reviewer of this exact commit.
Stop after TASK-001 and the reviewable commit. Do not start TASK-002 until
TASK-001 has independent approval. If a separate reviewer is available,
delegate review only; do not implement and approve your own architecture.
```

## Continuing after review

The supervising engineer reviews the exact commit and records one of the three verdicts. After approval, merge with normal history and assign TASK-002 using its issue file and the same workflow. For failures, use the narrow corrective task template in REVIEW_PROTOCOL. PROGRESS, not this chat, determines the next unblocked task.
