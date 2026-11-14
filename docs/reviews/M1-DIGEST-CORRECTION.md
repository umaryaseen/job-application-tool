# M1 profile-digest compatibility correction handoff

Review the focused corrective commit `bc7439a047d5072a95668ebc8fa884b2acd7ae48`
on `task/009-personal-baseline` independently. It follows the approved
M1-FIX-003 integration merge `6783fa21dfb3e61c8ce5d22d6894e081f21ce229`.

The correction keeps approval-inclusive profile payloads for profile digests
while using approval-free canonical fact payloads for fact digests and local
review receipts. It is required for preserved profile-r0005 and baseline-r0003
plan compatibility. Run the full locked checks and inspect the frozen legacy
digest regression in `tests/test_m1_fix003.py`. This correction is not covered
by the independent M1-FIX-003 approval and is not self-approved here.

## Independent review

Correction `bc7439a047d5072a95668ebc8fa884b2acd7ae48` was reviewed against
approved integration `6783fa21dfb3e61c8ce5d22d6894e081f21ce229`; head
`2c523d525c23f2dedd62805c36d29747932ac8a9` is a descendant with a
documentation-only tail. Working tree and ancestry are clean.

Profile digests include approval-bearing fact payloads for historical
compatibility; fact digests and local receipts remain approval-free. Approval
or fact mutations stale plans, while missing local receipts fail closed despite
imported approval fields. Snapshot QA/export bind current profile, plan and
artifact digests; historical bytes remain unchanged.

Locked sync, Python 3.12.14, full pytest (101 passed), Ruff check/format and
mypy (36 files) all passed. Frozen digest, schema/provenance, CLI,
snapshot/export and isolation regressions passed. No personal data or outputs
were modified.

**Verdict: APPROVED.**
