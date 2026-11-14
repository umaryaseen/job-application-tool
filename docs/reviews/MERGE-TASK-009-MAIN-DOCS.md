# TASK-009 / main merge — scoped documentation follow-up review

Verdict: **APPROVED** (scoped: documentation delta only)
Reviewer: Claude Code (Opus 5.5), separate review session; not the implementer
of the follow-up. Date: 2026-11-14. This review does not approve applicant
facts, private CV content, final artifacts or export.

## Candidate identity

| Item | Value |
| --- | --- |
| Branch | `task/009-personal-baseline` (merge in progress, uncommitted) |
| Parent 1 (HEAD) | `d0f1436d20fb8cc959feca3e9d355856f17c76ff` |
| Parent 2 (MERGE_HEAD, main) | `0cc9119df20a2be974f8db41ed9869663493f800` |
| Base: independently reviewed code tree | `2794c6af04df5beb982561c0115eadde58196500` |
| Head: staged tree (`git write-tree`) | `084d1a670bdf927bcb40ab175eb75b7eaa4ab649` |

Before and after review: no unstaged tracked changes and no untracked files.
The tree was re-recorded after all checks and is unchanged. This file is
untracked and is not part of that tree.

## Delta inspected

`git diff --name-status 2794c6a 084d1a6` lists only:

- `M docs/MERGE_RECONCILIATION.md`
- `M docs/PROGRESS.md`
- `M docs/REVIEW_HANDOFF.md`
- `M docs/adr/README.md` (one line)
- `A docs/reviews/MERGE-TASK-009-MAIN.md`

The follow-up changes no source, test, script, CI, schema, `pyproject.toml`,
`uv.lock` or fixture paths, and adds no private applicant data.

## Scope items

- **F-01 fixed.** REVIEW_HANDOFF names the current identity
  `baseline-v3-presentation-m1-fix005-hyphen-compounds`, which matches
  `TEMPLATE_VERSION` in `rendering/pdf.py`. The stale
  `baseline-v2-presentation-adr018` wording is gone. The runtime code is
  unchanged. ADR-018, `history/` and earlier reviews still carry their
  original identity strings.
- **F-03 fixed.** The ADR index now lists ADR-017 as
  "PROPOSED — IMPLEMENTATION CLEARED BY INDEPENDENT REVIEW", which matches
  ADR-017's own status line exactly. ADR-017 itself is unchanged, and the
  follow-up makes no new decision or approval.
- **Attribution.** PROGRESS and MERGE_RECONCILIATION credit the 147-test macOS
  run and the APPROVED WITH FOLLOW-UP verdict to the independent review, and
  link to it. They describe it as a local run, not combined-tree CI. The
  TASK-009 row still says that exact PDF/TXT content, final artifact acceptance
  and export are pending. Appearance-only approval keeps its original scope.
- **F-02 kept as a future gate.** MERGE_RECONCILIATION and the PROGRESS next
  action say the implementer of the first downstream feature that makes
  `source_url` clickable or fetchable must validate allowed URL schemes first.
  TASK-010 still treats the value as metadata only.
- **Original review included unchanged.** The added
  `docs/reviews/MERGE-TASK-009-MAIN.md` matches the content, identity and
  findings that review reported. The staged blob equals the working copy, and
  the file's modification time (2026-11-13) is earlier than the follow-up edits
  (2026-11-14). No pre-staging copy was available, so I could not compare it
  byte for byte against the original untracked file. Its sentence "This file is
  untracked" now reads as historical, which is expected for a record that was
  included unchanged.

## Commands and results

| Command | Exit | Result |
| --- | --- | --- |
| `git write-tree` (before and after) | 0 | `084d1a670bdf927bcb40ab175eb75b7eaa4ab649` |
| `git rev-parse HEAD`; `cat .git/MERGE_HEAD` | 0 | parents as above |
| `git diff --check 2794c6a 084d1a6` | 0 | no whitespace errors |
| `git diff --name-status 2794c6a 084d1a6` | 0 | 5 documentation paths only |
| `uv run python scripts/check_staged.py` | 0 | staged-content policy passed |
| Pattern scan of added lines (emails, names, home paths, tokens, keys, URLs) | — | no real hits; the only matches were `TASK-` false positives |
| Relative link check of the 5 changed files | — | 0 broken |

I did not rerun Ruff, mypy or pytest, because no code paths changed. The
147-pass result belongs to tree `2794c6a`. Under REVIEW_PROTOCOL, routine
documentation corrections can receive a scoped review without a full runtime
regression.

## Findings

None.

## Assessment and next gate

- Architecture/ADRs: index status aligned; no decision changes.
- Security/privacy: no personal data, secrets or private paths in the delta; no
  private artifacts were read or regenerated.
- Limitations: no combined-tree CI has run yet; the original review is
  compared by content and timestamps, not against a byte-level original.

Next gate: completing the merge commit for tree `084d1a6` (or a tree that adds
only this review record) is a separate action. Push only on explicit user
instruction. TASK-009 content and final artifact acceptance remain the user's
decision.
