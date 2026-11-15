# Review handoff: M1-FIX-009 compact contacts, unbroken items, sticky entries

Implementer: Claude Code. Independent reviewer: a separate Codex session.
Base: main `deee9aa`. Branch: `task/009-m1-fix-009-compact-contacts`.

Read AGENTS, PROGRESS, [the task](tasks/M1-FIX-009.md), REVIEW_PROTOCOL and
SECURITY_AND_PRIVACY; M1-FIX-004 (contact URL guard), M1-FIX-007 (atomic
compounds) and M1-FIX-008 (skill-group leads, QA headings) are the closest
context.

Focus: contact compaction order and kinds, and that URLs keep their own
guarded lines; the item contract (presentation items, token `items`/`lines`,
the worker's exact-shape check, text equality) and escaping of every item in
the generated Typst; that boxes carry trailing separators so no line can start
with "|" and no item splits, with extraction unchanged; the item width guard
(fails before publication, never clips); sticky employment headers and dates;
the language line format; that fixture/test updates only move to the new
display; template identity; no typography, selection or provenance change.
Record findings and one verdict in `docs/reviews/M1-FIX-009.md` without
modifying implementation. Renderer tests need macOS `sandbox-exec`: inspect
hosted CI for the exact head.

## Round 2 request

Round 1 ([report](reviews/M1-FIX-009.md)) found F-01 (items that begin with
"|" or have no visible text), F-02 (control and Unicode line-separator
characters inside items) and F-03 (placeholder collisions from repeated global
replacement). Items are now checked by `item_problem` in the parent (clear
`ITEM_CONTENT_ERROR`) and in the worker token check; placeholders are
substituted in one regex pass with all placeholders accounted for. Review the
delta from `241145c`.
