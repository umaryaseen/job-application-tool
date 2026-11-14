# Continuation: reviewed TASK-011 draft source candidates

The decision, fixture and implementation reviews are complete; do not restart
them. The [implementation review](reviews/TASK-011.md) returned APPROVED WITH
FOLLOW-UP for local `d47311e` / published `c72d93a`, matching tree `54340c9a`.
Its sole low-priority status-text finding is corrected in the closure. The
instructions below preserve the completed review scope. Verify the final
published PR #4 head and hosted CI before main integration.

Base: merged main `83497777a03e6e8f642edadff9781c6cdeb741ad`.
Branch: `task/011-requirement-candidates`. Review the exact candidate commit/tree
provided with this handoff, including its decision/fixture history.

## Decisions and independently reviewed oracle

Read AGENTS, TASK-011, ADR-007/020/021, the relevant architecture/A17/privacy
sections and REVIEW_PROTOCOL. ADR-021 was independently approved before coding
and explicitly allows source-only TASK-011–014 on their dependencies. Only
TASK-011 is implemented here; M1/M2 acceptance and matching/tailoring/export
remain gated. Never infer applicant approval from a merged PR or synthetic test.

The 16 EN/16 DE literal oracle was committed before implementation and separately
[reviewed](reviews/TASK-011-FIXTURES.md). Do not derive expected labels from the
parser or change them to conceal a mismatch. Kind and priority are separate;
every candidate stays draft, needs_review and priority unspecified.

## Review focus

Completed implementation-review scope:

- Typed exact raw source identity, original Unicode-codepoint half-open offsets,
  quote round-trip, candidate/heading IDs, repeated occurrences, section scope,
  lexical subspans, analysis digest and revision binding.
- Bounded sentence/list/section segmentation, CRLF/BOM/combining characters,
  common abbreviations, wrapped prose and unknown headings. Responsibilities,
  benefits/context, unsupported technologies and mixed/ambiguous clauses must
  stay visible without turning a negative, optional or OR clause into a hard gate.
- Read-only actual `job-extract` CLI against verified saved jobs, explicit and
  current revisions, missing/tampered/path-traversal input, second-read mutation,
  output bounds and absence of network or source execution. Analysis must not
  mutate job revisions, read career profiles or persist approvals.
- Rule/lexical limits are disclosed: no canonical aliases, priority/groups,
  matching, LLM/provider, new dependency, URL fetching, storage framework or CV
  change. README's captures-dir example only aligns with an existing required flag.

## Verification

Run `uv run pytest tests/test_requirement_spans.py tests/test_ingestion.py -ra`,
Ruff check/format, mypy and whitespace/link checks. Inspect hosted complete
macOS CI for the exact published candidate; Linux cannot qualify the existing
production renderer. Local TASK-011 focused suite passed 57 tests before review.
Independent review passed 84 extraction/intake tests plus adversarial probes
and lint/types. Hosted CI on implementation `c72d93a` passed 204 tests; see the
review for the exact run, logs and matching checkout tree. These are recorded
results, not a request to repeat completed review after a status-only closure.
Record actual commands/results, exact heads/trees, findings and independent
verdict in `docs/reviews/TASK-011.md`. Do not modify implementation while giving
that verdict. No private profile or final CV inspection is needed for this
source-only task. Do not merge or impersonate applicant approval.

The faithful status/report-only closure requires a short scoped check, retaining
all source/approval/milestone gates. Inspect final-head CI before integration.
After PR #4 is merged, TASK-012 is next on its reviewed dependency: interpret
priority/negation/alternatives from the same source, retaining uncertainty and
draft review state. No career matching, tailoring or export gate is waived.
