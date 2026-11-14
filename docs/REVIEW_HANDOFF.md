# Independent review: TASK-011 draft source candidates

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
Record actual commands/results, exact heads/trees, findings and independent
verdict in `docs/reviews/TASK-011.md`. Do not modify implementation while giving
that verdict. No private profile or final CV inspection is needed for this
source-only task. Do not merge or impersonate applicant approval.

After approval, update current progress and this handoff faithfully, retaining
all source/approval/milestone gates. Inspect final-head CI before integration.
