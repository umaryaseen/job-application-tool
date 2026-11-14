# Scoped review handoff: TASK-009 / main merge documentation follow-up

State: IMPLEMENTED — AWAITING SCOPED INDEPENDENT REVIEW. The merge remains
uncommitted. Review the complete staged delta from the independently reviewed
code tree `2794c6af04df5beb982561c0115eadde58196500` to the staged tree
reported by `git write-tree`. The merge parents remain local HEAD
`d0f1436d20fb8cc959feca3e9d355856f17c76ff` and main
`0cc9119df20a2be974f8db41ed9869663493f800`.

The [independent merge review](reviews/MERGE-TASK-009-MAIN.md) returned
**APPROVED WITH FOLLOW-UP** for the reviewed tree, including 147 tests passed
on macOS. It records the commands, findings and limitations. This follow-up
includes that review record and addresses its documentation findings; it does
not extend the verdict to the new staged tree without a scoped review.

## Review scope

Using [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md), inspect the entire staged delta
from the reviewed tree and confirm it contains documentation only:

- F-01: the current template identity is
  `baseline-v3-presentation-m1-fix005-hyphen-compounds`. Runtime identities and
  historical records are unchanged.
- F-03: the ADR-017 index status matches ADR-017 itself, without a new decision
  or approval.
- PROGRESS and MERGE_RECONCILIATION accurately attribute the verification and
  code verdict to the independent reviewer. The applicant's PDF/TXT content and
  final artifact approval, and export, remain pending; the earlier appearance
  approval retains its original scope.
- F-02 remains a future gate: the implementer of the first downstream feature
  making `source_url` clickable or fetchable must validate allowed URL schemes
  before doing so. TASK-010 continues to treat it as metadata only.
- The original independent merge review is included unchanged, with no source,
  test, dependency or private applicant data changes in the follow-up.

Confirm the staged tree and parents, check the staged diff for whitespace,
secrets and personal information, and record the scoped verdict and exact tree
identity. No private artifacts need to be read or regenerated. The original
review was a local macOS run, not combined-tree CI; its test results are not a
fresh run of this documentation delta. After scoped approval, merge completion
is a separate action. Do not commit or push as part of this handoff.
