# Review handoff: M1-FIX-007 slash-joined compounds

Round 2: re-review `df9e9bb..<candidate>` for round-1 F-01 (joiner anywhere in a token), F-02 (exact identity assertion) and F-03 (line-start witness); append a "Round 2" section to `docs/reviews/M1-FIX-007.md`.

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `68aa5369db17efb3e9c878328bffeee8983afd62`. Branch:
`task/009-m1-fix-007`. M1-FIX-006 is merged (see
[its review](reviews/M1-FIX-006.md)).

Read AGENTS, PROGRESS, [the task](tasks/M1-FIX-007.md), the M1-FIX-005 review
context for atomic hyphen compounds, REVIEW_PROTOCOL and SECURITY_AND_PRIVACY.

Focus: the `[-/]` token rule and escaping in `_literal_text_expression`; the
width guard for over-width slash tokens (fails before publication, no
clipping/shrinking); interaction with contact URLs and other slash-bearing
text; extraction equality with TXT; template identity; that the sweep test
really exercises line-end slashes (it fails on the previous renderer); no
content or typography change. Record findings and one verdict in
`docs/reviews/M1-FIX-007.md` without modifying implementation. Renderer tests
need macOS `sandbox-exec`: inspect hosted CI for the exact head. Implementer
full suite: 478 passed.
