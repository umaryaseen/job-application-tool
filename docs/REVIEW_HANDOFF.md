# Review handoff: M1-FIX-008 LinkedIn label and compact skill groups

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `01f3a40a`. Branch: `task/009-m1-fix-008-display-labels`.
M1-FIX-007 is merged (see [its review](reviews/M1-FIX-007.md)).

Read AGENTS, PROGRESS, [the task](tasks/M1-FIX-008.md), REVIEW_PROTOCOL and
SECURITY_AND_PRIVACY; M1-FIX-004 (contact URL width guard) and M1-FIX-006
(skill display headings) are the closest earlier context.

Focus: `contact_label` host parsing (LinkedIn only for `linkedin.com` and its
subdomains; every lookalike, user-info, malformed or path/query mention keeps
`Url:`); that plan text, display and renderer use the one function and the
width guard measures every URL label; the skill-group `lead` contract and the
worker's exact token-shape check; escaping of the bold lead and the remaining
text; compound width measurement for skill-group lines; extraction equality
with TXT; that fixture/test updates only move the two-line layout to the
compact line and do not loosen checks; template identity; no typography,
selection or provenance change. Record findings and one verdict in
`docs/reviews/M1-FIX-008.md` without modifying implementation. Renderer tests
need macOS `sandbox-exec`: inspect hosted CI for the exact head. Implementer
full suite: 676 passed, no skips.

## Round 3 request

Round 2 (CHANGES REQUIRED, F-01) showed that a body line reading exactly like a
missing heading passed the text-level checks. The correction adds a separate
mandatory `heading_presentation` QA check from Poppler `-bbox-layout` word
heights (task item 5), a real adversarial PDF mutation with identical text and
body-sized headings, and synthetic XML cases. Review the delta from `a1e5d36`.

## Round 4 request

Round 3 (CHANGES REQUIRED) found that zero-height boxes could pass or crash the
presentation check (F-01) and that a document-wide median failed short valid
documents (F-02); F-03 (heading-sized non-heading lines, no rotation signal) was
a follow-up. The correction measures each heading against its own section body,
fails closed on any non-finite or non-positive word box (and catches arithmetic
errors at the caller), and states the F-03 limit in task item 5. Review the
delta from `2422eac`.
