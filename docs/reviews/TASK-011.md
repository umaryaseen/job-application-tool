# TASK-011 independent implementation review

- Reviewer: separate review agent `/root/intake_review`; not the implementer.
- Date: 2026-11-14.
- Verdict: **APPROVED WITH FOLLOW-UP**. No blocking implementation finding;
  close the bounded documentation finding F-01 before integration.
- Base: `83497777a03e6e8f642edadff9781c6cdeb741ad`.
- Local implementation head: `d47311eaaad5140096569fb7e9b3c2ac573bcd36`.
- Published head: `c72d93aa64e65f667638d2ca45c3645c32b02c7a`.
- Both heads have tree `54340c9ac1659111ece31a1a599036c57f0dbf26`.
- Published head has the stated main base as its sole parent. PR #4 is open
  and draft at the time of this review; this report does not merge it.

## Inspection and scope

Inspected the full 21-file cumulative base-to-head change: the explicit
ADR-021 sequencing amendment and adoption, independent fixture review and
unchanged oracle, typed draft models, segmentation and lexical rules, source
association validator, saved-job adapter, actual CLI, tests and operating/user
documentation. Read AGENTS, current progress/handoff, TASK-011, A17, relevant
architecture/privacy rules and ADR-007/013/015/020/021. Earlier decision and
fixture approvals were inputs, not substitutes for this code review.

The implementation is bounded local source analysis only. It preserves literal
raw Unicode-codepoint quotes and source/revision digests, distinct repeated
occurrences, section scope and nested lexical offsets. It validates source,
record and analysis integrity, and checks association/order/overlap constraints.
The read-only CLI uses verified stored revisions and checks the raw bytes again
after loading. No applicant profile is read and no requirement approval is
persisted. Priority stays unspecified and every candidate remains draft and
needs review, including negatives, optional language and OR clauses.

Responsibility and benefit/context sections retain distinct meaning. Unknown
technologies, unsupported prose and mixed lexical kinds remain visible and
uncertain. These structural and lexical checks do not certify complete semantic
interpretation or authorize a requirement, skill or career claim.

## Independent local verification

All commands ran against the stated local implementation head on Python
3.12.14. No implementation, test expectation or fixture was changed by review.

| Check | Result |
| --- | --- |
| `uv run pytest tests/test_requirement_spans.py tests/test_ingestion.py -ra` | Exit 0; **84 passed in 4.48s** |
| `uv run ruff check .` | Exit 0; all checks passed |
| `uv run ruff format --check .` | Exit 0; 73 files already formatted |
| `uv run mypy src` | Exit 0; 44 source files |
| `git diff --check 83497777..d47311ea` | Exit 0 |
| Relative Markdown links in changed documents | 95 resolved |
| Dependency, lockfile and CI workflow comparison to base | Unchanged |
| Approved bilingual JSON bytes | SHA-256 remains `de15376084945633ed1fa736bc80b6e39a08f742a03770ddfc84272150ca702a` |

Additional temporary standard-library probes independently checked five
EN/DE/Unicode/layout cases for literal coverage, wrapped prose, numbered lists,
abbreviations, negation and transitions through benefits and unknown headings.
Every non-layout source character in those cases remained in a heading or
candidate span. Five recomputed-digest mutations of job identity, candidate ID,
heading order, candidate order and section association were rejected. Reanalysis
preserved every saved file. Exact structural limits of 2,048 versus 2,049,
lexical limits of 4,096 versus 4,097, and the accepted 200,000-byte source boundary
behaved correctly.

An initial ad hoc assertion expected an education hint for `B.Sc.` and failed.
Inspection confirmed the complete alternative clause was preserved as ambiguous
and needs-review: this abbreviation is outside the documented small education
hint allowlist. The independent probe was corrected to assess the bounded
contract. No reviewed fixture or implementation was changed, and no general
education-language recall is claimed.

## Independently verified hosted regression

Fetched the actual run, job metadata and decoded job logs through GitHub, rather
than relying on a reported check name or PR description:

- [Run 43544575739](https://github.com/umaryaseen/job-application-tool/actions/runs/43544575739):
  `pull_request`, exact published head `c72d93aa64e65f667638d2ca45c3645c32b02c7a`,
  completed **success**.
- Job `132292757018`, macOS supported runner, CPython 3.12.10: **204 passed in
  153.70s**, with no skips/xfails in the test summary; Ruff passed, 73 files
  formatted, mypy passed for 44 source files. Locked sync, public asset setup,
  isolation/tool verification and all other job steps succeeded.
- The workflow checked out PR merge commit
  `100b714fa9cf8e05d880d4b872d0b9f1ad9562e8`. Independently fetched its Git tree:
  `54340c9ac1659111ece31a1a599036c57f0dbf26`, identical to the published head and
  locally inspected implementation. Its parents are the stated base and head.

This qualifies the existing renderer regression on its supported platform; a
Linux renderer run was not substituted. Subsequent published heads still need
their own check status before integration.

## Findings and follow-up

**F-01 — low, operating-document contradiction.** `docs/PROGRESS.md` retains the
historical sentence saying only draft intake precedes personal acceptance. Its
current introduction correctly states ADR-021's additional source-only exception.
Owner: supervising implementer. Before integration, qualify the old sentence as
ADR-020's historical scope and reference ADR-021. Include this in the faithful
review/status closure; no runtime change is required. Review that small delta
and the recorded review evidence, then verify final-head hosted CI.

No other required correction was found. Bounded lexical/heading coverage is an
explicit limitation, not a general NLP accuracy claim. Semantic priority,
negation/group interpretation, canonical skill normalization and persistent user
correction remain later independently reviewed tasks.

## Approval boundary

TASK-011 implementation acceptance may proceed after the documentation closure
and final-head checks. The review does not approve TASK-012 onward, a milestone
release, private CV content or final artifacts. ADR-021's narrow sequencing
exception and unchanged M1/M2, matching, tailoring and export gates remain in
force. No private applicant source was accessed. Stored URLs remain metadata;
F-02's later URL-scheme gate is unchanged.

## Documentation closure — 2026-11-14

**APPROVED; F-01 RESOLVED.** Independently inspected the uncommitted closure
against local implementation head `d47311eaaad5140096569fb7e9b3c2ac573bcd36`:
only `docs/PROGRESS.md` and `docs/REVIEW_HANDOFF.md` changed, alongside this
previously untracked review report. Inspected Git blob identities before this
note: progress `2647dc5dc9f4aa2f7cb0fa0f773c4042d5a13267`; handoff
`f8fa8bda68a65c65bbe3ddaf65291bb2f5b12280`.

The historical intake-only sentence now correctly distinguishes ADR-020 from
ADR-021. The records accurately describe completed independent reviews and
initial exact-tree CI, preserve the difference between 57 implementer-focused
tests and 84 independent extraction/intake tests, and keep PR #4 unmerged with
final-head CI still required. No runtime, fixture, dependency, workflow, private
data or approval-policy change is present. All 20 relative links across these
documents and the report resolve; whitespace checks pass; nothing was staged.
No runtime suite was repeated for this documentation-only scope.

The sole review finding is closed. TASK-011 is independently **APPROVED** at
the reviewed implementation plus this faithful closure. Commit/publication and
successful CI for the final published head remain integration checks, not a
request to repeat the original reviews. TASK-012 starts only after PR #4 merges;
personal/M1/M2, matching, tailoring and export gates retain their prior scope.
