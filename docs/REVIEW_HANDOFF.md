# Review handoff: M1-FIX-006 expected completion, specialization, display headings

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `ee590699b49077a1cd61161caa679f104b99b659`. Branch:
`task/009-m1-fix-006`. Review the exact candidate commit supplied with this
handoff. TASK-012 is merged; its reviews are complete (see
[the review](reviews/TASK-012.md)).

## Read first

AGENTS, PROGRESS, [the task](tasks/M1-FIX-006.md), ADR-011/012/013/014/015 and
the archived ADR-017/018 context, ARCHITECTURE (profile, plan, presentation,
QA and approval sections), SECURITY_AND_PRIVACY, REVIEW_PROTOCOL.

## Review focus

- The education model never implies an award: no actual completion date on an
  ongoing degree; an expected date only for an ongoing degree without a known
  end and not before a known start.
- Digest stability: empty new fields are stripped from canonical payloads; the
  pinned legacy digest is unchanged; no existing approval or binding can break
  or be silently reused for changed content.
- Presentation, plan claim text and TXT/PDF: expected date and specialization
  are visible claims bound to plan text; degrees without them render exactly
  as before; internal skill categories unchanged and only static display
  headings/order change; unknown categories stay ungrouped.
- Template identity bump, schema export, and the updated expected-heading
  fixtures and test helpers reflect only the intended change (no weakened
  assertions).
- No personal data in Git; no dependency change.

## Verification

Focused: `uv run pytest tests/test_m1_fix006.py tests/test_m1_fix003.py
tests/test_document_plan.py tests/test_profile_schema.py -ra`, plus Ruff,
format, mypy and `git diff --check`. Renderer tests need macOS
`sandbox-exec`, Poppler and pinned Typst assets: inspect hosted CI for the
exact published head. Implementer full suite: 471 passed. Record commands,
findings and one verdict in `docs/reviews/M1-FIX-006.md` without modifying
implementation. Do not approve applicant facts or artifacts.
