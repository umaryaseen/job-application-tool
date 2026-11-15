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
full suite: 654 passed, no skips.
