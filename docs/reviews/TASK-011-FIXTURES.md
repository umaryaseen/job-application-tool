# TASK-011 independent fixture-label review

- Reviewer: independent review agent `/root/intake_review`; not the fixture author or parser implementer.
- Date: 2026-11-14.
- Verdict: **APPROVED — fixture labels only**. No required fixture corrections.
- Base: `99edad04ea13d96f7812c932935cf160fe760e80`.
- Inspected fixture commit: `ab616e2b5cb61fc9753c866b26bb1926fd91c345`.
- Fixture commit tree: `a19f20ef807a957b15d1a0cedc6dc6c1739c9471`.
- `candidates.json` SHA-256: `de15376084945633ed1fa736bc80b6e39a08f742a03770ddfc84272150ca702a`.

## Scope and independence

Reviewed the complete two-file fixture delta: `tests/fixtures/requirements/README.md`
and `tests/fixtures/requirements/candidates.json`. Compared all 32 literal source
postings and expected annotations directly against TASK-011, A17, ADR-007 and
ADR-021. Parser behavior was not used to derive or assess expected results. The
fixture commit contains no extraction implementation. Concurrent uncommitted
source work was excluded from this review and was not modified.

## Semantic assessment

The 16 English and 16 German cases have defensible draft kind, section and
lexical-signal labels. Explicit required/preferred language and negative German
requirements remain source mentions, with the README requiring unspecified
priority and `needs_review` throughout. No positive possession or mandatory
requirement is inferred from those lexical labels.

Responsibilities and benefits/company context retain their section meaning
despite technology or language mentions. Degree-or-experience and Python-or-Java
alternatives remain complete source clauses. Mixed education/years clauses are
ambiguous. Unsupported prose remains visible with no invented signal. Repeated
clauses, abbreviation punctuation, list items, CRLF and wrapped source text are
represented without rewriting their quotes. No blocking label discrepancy was
found in either language.

## Independent checks

- `git diff --check ab616e2^..ab616e2`: exit 0.
- `git diff-tree --no-commit-id --name-only -r ab616e2`: only the two fixture
  files above; 531 added lines.
- Standard-library validation reading JSON with `git show` at the exact fixture
  commit: exit 0; 32 unique case IDs, 16 cases per locale, and all **36 ordered
  literal quote occurrences** round-trip exactly. Duplicate-case quotes were
  checked as separate successive occurrences, not repeated first-match lookups.
- SHA-256 of the committed JSON bytes matches the digest recorded above.
- `git ls-tree -r --name-only ab616e2 src/job_application_engine/extraction`:
  empty, confirming no extraction implementation in the reviewed fixture commit.

No runtime, type-checking or general extraction-accuracy result is claimed by
this fixture-only review. The fixture files are synthetic and introduce no
applicant content, executable posting text, dependency or network operation.

## Implementation gate

These labels may now be used as independent expectations for their exact
examples. They do not establish general EN/DE recall, priority interpretation,
canonical skills, ALL/ANY grouping or requirement approval. Implementation tests
must assert `priority=unspecified` and `needs_review` for every candidate; these
global invariants are documented in the README rather than repeated in each JSON
row. Also test a known-section-to-unknown-heading transition: the isolated
unknown-heading examples do not alone demonstrate resetting prior section
context. This is an implementation coverage reminder, not a fixture correction.

TASK-011 source, negative/security cases, bounds, raw revision identity, Unicode
offsets, read-only CLI behavior and supported CI require their own independent
exact-head review. M1 personal acceptance, M2 release, matching, tailoring and
export remain outside this approval.
