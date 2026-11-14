<!-- Historical local document, preserved from pre-sync TASK-009 HEAD.
Use docs/PROGRESS.md and docs/REVIEW_HANDOFF.md for current instructions. -->

# Current review target — M1-FIX-005 literal-hyphen correction

Use this prompt in a separate coding-agent session. Review the exact
M1-FIX-005 implementation commit below; do not approve it as the implementer.

```text
Independently review M1-FIX-005 in this repository.

Implementation commit: 5743a8743b4ab49d0c0026e83812b9e5fe62eea9
Parent/base: 211ad81c837699d5ba00bd133f97f496a5f9af65
Branch: task/009-m1-fix-005

Read AGENTS.md, docs/ARCHITECTURE.md, docs/PROGRESS.md,
docs/reviews/M1.md, docs/REVIEW_PROTOCOL.md, docs/adr/ADR-018.md,
docs/tasks/TASK-004.md, docs/tasks/TASK-006.md, docs/tasks/TASK-007.md and
the complete diff from the parent to the exact implementation commit.

Reproduce the synthetic summary and project/body cases that place ordinary
ASCII-hyphenated compounds such as `full-stack` and `cost-forensics` at a
line edge. Confirm the trusted PDF boundary detects arbitrary hyphenated
tokens, emits the original literal characters in atomic Typst boxes, and
keeps the URL/contact boundary unchanged. Inspect the measured width guard,
including style and bullet/project inset, and confirm an over-wide compound
fails before any PDF is published with the bounded diagnostic.

Run `uv sync --locked`, Python 3.12, the full pytest
suite (expected 116 tests), Ruff check, Ruff format check and mypy. Inspect
`artifacts/verification/m1-fix-005/`: the two-page synthetic PDF, Poppler and
pypdf texts, and both raster pages. Verify complete ordered extraction is
identical through both extractors, changed hyphens and suffixes fail, page
count/A4/layout remain valid, and no clipping or content loss occurs. Confirm
the template version, canonical wording, narrow normalization, literal-text
escaping, provenance and existing identity/scope/snapshot regressions remain
intact. Confirm no personal output was regenerated and no applicant approval,
export, second renderer or TASK-010 work was introduced.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/M1-FIX-005.md report with exact commit IDs and measured
results. Update PROGRESS with the actual review state. Do not modify
implementation, regenerate personal output, approve applicant artifacts,
merge, push or self-approve.
```

## Historical review target — M1-FIX-004 F-01 corrective implementation

Independently review exact corrective commit
`c7d957b08d24e54fb88eda55e3edb87b8a410bc6` on `task/009-m1-fix-004`; its
parent is the preserved review documentation head
`4c0c757111547906623f32da3d0729ef7053e6c2`. This correction addresses only
the blocking long ContactUrl extraction finding in
`docs/reviews/M1-FIX-004.md`; do not rewrite that historical finding or review
personal outputs.

Read `AGENTS.md`, `docs/tasks/M1-FIX-004.md`, `docs/adr/ADR-018.md`,
`docs/ARCHITECTURE.md`, `docs/PROGRESS.md`, and the complete diff from
`4c0c757111547906623f32da3d0729ef7053e6c2` to the corrective commit. Run the
locked checks and the focused synthetic contact tests. Reproduce the exact
review URL `https://example.invalid/profile/this-is-a-very-long-contact-url-with-meaningful-components-and-no-loss`:
it must fail before publishing a PDF with the bounded fixed-width diagnostic.
Also exercise a fitting synthetic URL through the actual production adapter
and compare complete ordered text independently with Poppler and pypdf. Check
changed URL suffix and punctuation negative controls, the separate contact
line and non-breakable trusted blocks, A4/20 mm/11 pt settings, identity and
provenance validation, no-hyphenation, CLI template identity, snapshot/export,
isolation and all prior M1-FIX-004 regressions. Inspect the generated fitting
fixture raster. Confirm no URL is truncated, relabelled, broadly normalized,
or silently published when it cannot fit. The corrective template identity is
`baseline-v3-presentation-m1-fix004-f01`.

Record `APPROVED`, `APPROVED WITH FOLLOW-UP`, or `CHANGES REQUIRED` in a new
sanitized review report with exact commit IDs and measured results. Do not
modify implementation, personal outputs, merge, push, self-approve, or begin
TASK-010.

## Historical review handoffs

The following prompts are retained for audit history and are not current
targets.

# Current review target — M1-FIX-002 corrective findings

Review corrective head `be4d9dc1c6411520d874a98539ec6904c8ba4873` on branch
`task/009-m1-fix-002`.
Base implementation under review: `3d9c7916f6a8cc2bcc9552160abff27d0ab5de36`;
independent review: `f6a6f8c66da8dd397e3a5c10b9169059f4ec1143` (CHANGES REQUIRED).
Inspect only the F-01 trusted QA identity binding and F-02 effective-theme
hyphenation correction. Preserve the historical review at
`docs/reviews/M1-FIX-002.md` and do not regenerate personal outputs.

Correction base: `b985674a31f57382abfebef7464376a6699477fa`.
Prior implementation: `d93dc0f09f1075dc876c35382ec9573da760fe0a`.
Corrective head: `157b973830727cccd9628ec0c21b916f1a880f3a`.
Architecture review: `004aeda9c4bb24c0b1c1f8a7d3d8726a04da2473`.
Branch: `task/009-m1-fix-001`.

Verdict on prior head: CHANGES REQUIRED; see [implementation review](../reviews/M1-FIX-001.md).
The corrective delta addresses F-01 document placement scope and F-02 ordering
policy. Review the complete corrective head independently; architecture
clearance alone is insufficient. Do not merge, generate a personal CV on
unapproved code, or start TASK-010.

The old `664d08c` resolves to `664d08cb0cb7bd5745945ed8929125635b4a2ed8`;
its CLI tests were included in the complete base-to-final review. The final
`b985674` commit changes handoff documentation only.

## Corrective re-review prompt

Review the exact corrective head above in a separate session. Preserve the
historical F-01/F-02 findings and inspect the full `b985674..157b973830727cccd9628ec0c21b916f1a880f3a`
delta. Confirm that independently reconstructed plans cannot move a
responsibility or employment-linked project beneath another same-person
employment (including incorrect revisions), while standalone projects remain
valid. Exercise validation, text/PDF boundaries, recomputed plan digests and
capture integrity. Confirm `_project_key` implements ADR-017 unknown-first,
known-date and stable-ID tie ordering with shuffled synthetic inputs. Run the
locked full suite, Ruff, format and mypy. Record a sanitized independent
verdict in `docs/reviews/M1-FIX-001.md` or a new corrective review file; do not
modify implementation, merge, or self-approve.

## Historical handoffs — obsolete targets, retained for audit

The prompts below are historical and must not override the current target above.

# Current review target — M1-FIX-004

Review the exact synthetic implementation on branch `task/009-m1-fix-004`.

Base: `139c48f822611275d93d43d64ba68d4d918b75b1`. Implementation commits:
`531a486e447cf71961fb9f18e414072f72ce178b` and `d0822de`; review the full
corrective head `d0822de`. No personal outputs were
regenerated. The task versions the trusted presentation/template policy as
`baseline-v3-presentation-m1-fix004`.

Read `AGENTS.md`, `docs/tasks/M1-FIX-004.md`, `docs/adr/ADR-018.md`,
`docs/ARCHITECTURE.md`, `docs/PROGRESS.md`, `docs/reviews/M1.md` and the
relevant TASK-004/006/007/009 contracts. Inspect the complete diff from the
base and the staged history safeguards. Run locked Python 3.12 checks, the
full synthetic suite, Ruff, format and mypy.

Focus on the trusted validated-plan presentation boundary: the bound
candidate name is prominent with no visible Contact heading; contacts remain
complete literal values with long URLs preserved; employment headings and
hanging responsibility bullets retain every claim; linked AUAV remains nested
under the exact eSketchers employment revision; standalone projects appear
under Selected Projects only when present, preserving P3 association-only
unknown dates and P4 standalone scope; education, grouped skills, qualifiers,
coursework and unknowns remain exact. Confirm ongoing degree status is not
duplicated, date precision is unchanged, and no caller marker can conceal or
reassociate claims.

Exercise the synthetic one-page/no-project, representative two-page and
over-capacity cases. Confirm Selected Projects starts page 2 for the intended
two-page fixture without blank pages when absent or when prior content already
spills; excess content remains present and would fail the page limit rather
than being shrunk or omitted. Compare complete Poppler and pypdf text, identity
and entry sequence, inspect every raster page, and retain hostile literal-text,
long-URL, Unicode, provenance, CLI, snapshot/export and isolation regressions.
Verify the presentation/template identity is bound to new outputs and old
artifact approvals cannot transfer. No personal data, applicant approval,
second renderer, TASK-010 work, merge or push is in scope.

Record APPROVED, APPROVED WITH FOLLOW-UP or CHANGES REQUIRED in a new
sanitized review with exact reviewed commit IDs. Do not modify implementation,
merge, force-push or self-approve.

# Historical handoffs — retained for audit

The prompts below are historical and must not override the current target.

# Handoff to an independent reviewer

Use this prompt in a separate coding-agent session. Review the exact
TASK-008 implementation commit below; do not approve it as the implementer.

```text
Independently review TASK-008 in this repository.

TASK-007 approved merge/base: a83324f9afcef143ef264c554c5d4e7764d1e8bd
TASK-008 corrective implementation: 045b1e598b5e47bd73b3838442d466fa50e40286
Earlier corrective commit: ee3db56edf4b91892d8c17ded2741fea961d8e07
Reviewed implementation before correction: c0c25f81baca6bf34822aea58a56340000c15ce6
Initial implementation: d53276b8357846774e5147bd13448af23b73cc5d
Branch: task/008-snapshots-export

Read AGENTS.md, docs/PROJECT_BRIEF.md, docs/ARCHITECTURE.md,
docs/IMPLEMENTATION_PLAN.md, docs/ACCEPTANCE_CRITERIA.md,
docs/SECURITY_AND_PRIVACY.md, docs/PROGRESS.md, docs/tasks/TASK-008.md,
ADR-002, ADR-011, ADR-012, ADR-015, relevant research sections in
SOURCE_REGISTER.md, and docs/REVIEW_PROTOCOL.md.

Inspect the complete diff from the TASK-007 approved merge to the exact
corrective TASK-008 head, including the intervening-edit recheck and CLI
integration correction. Run the locked checks independently:

  uv sync --locked
  uv run python --version
  uv run pytest -vv --durations=0 --junitxml=artifacts/verification/task-008/review-junit.xml
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy src
  uv run python tests/reproduce_task008.py
  uv run pytest tests/test_snapshot_cli.py -vv

Focus on atomic same-filesystem staging and publication, owner-marked staging
cleanup, no-overwrite IDs, complete source slice/capture/review/plan/PDF/TXT/QA
/config/tool files, manifest hashes without self-reference, restore verification,
and rejection of modified PDF/TXT/plan/manifest/capture bytes. Confirm failed or
interrupted builds never publish ready snapshots and historical snapshots remain.

Confirm final approval is a distinct explicit local-human record bound to exact
manifest/PDF/TXT digests, reviewer and timezone-aware time. Confirm export
revalidates the current trusted profile, exact fact/variant revisions and local
reviews, support capture hashes/status/availability, current profile and plan
digests, mandatory QA and attributed visual review, and explicit expiry using
current time rather than a backdated plan as-of. Check corrected, superseded,
revoked, deleted and unavailable support; an external-original deletion with
an intact capture must remain usable. Exercise concurrent profile-loader
revision conflicts and unauthorized/missing approvals.

Run or inspect the synthetic A28–A29 tests for all of those mutations. Confirm
export copies only the verified approved PDF/TXT bytes, refuses an existing
destination, does not mutate snapshots, and has no SQLite, signing, browser,
identity-document, history-deletion or TASK-009 work. Confirm no dependency or
lockfile change was introduced and no applicant data or credentials are present.

Exercise the installed `jae` entry point in a temporary external `JAE_DATA_DIR`.
Confirm `snapshot-build`, `snapshot-approve`, and `snapshot-export` run as real
subprocesses; pre-approval export fails; approval records the synthetic reviewer
and exact manifest/PDF/TXT digests; approved export preserves exact bytes; missing
arguments, private-root traversal, existing destinations and post-approval
artifact tampering produce nonzero exits with bounded diagnostics and no unsafe
publication.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/TASK-008.md report with exact reviewed commit IDs and
measured results. For each blocking finding provide a narrow reproduction,
affected modules, acceptance criteria and regression tests. Update PROGRESS
with the actual review state. Do not modify implementation, merge, force-push,
or self-approve.
```

## M1-FIX-001 independent implementation review

Review the exact corrective implementation below in a separate coding-agent
session. Do not approve it as the implementer.

```text
Independently review M1-FIX-001 at commit 664d08c on branch
task/009-m1-fix-001. The implementation commit is d93dc0f and the final head
adds only synthetic CLI regression coverage and sanitized documentation. The architecture amendment was independently reviewed
with APPROVED WITH FOLLOW-UP at 004aeda; preserve the original CHANGES REQUIRED
report in docs/reviews/ADR-017.md.

Read AGENTS.md, docs/ARCHITECTURE.md, docs/PROGRESS.md, docs/reviews/M1.md,
docs/tasks/M1-FIX-001.md, ADR-011, ADR-012, ADR-013, ADR-015, ADR-017 and the
relevant TASK-004/006/008/009 records. Inspect the complete diff from
273cdd484081948bfbedca1ff37e390b27dbd5af to d93dc0f.

Run `uv sync --locked`, Python 3.12, full pytest,
Ruff check, Ruff format check and mypy. Exercise tests/test_m1_fix.py and
confirm the synthetic production path reaches typed profile records,
validated DocumentPlan, UTF-8 text, RenderCV PDF, independent Poppler and
pypdf extraction, QA, snapshot publication/approval/export and exact-byte
preservation.

Focus on exact revision-bound employment references; same-person wrong-
employment and wrong-subject rejection; project entities and no duplicate
employment entries; project names, roles, technologies, descriptions and
dates bound by approved fact/evidence records; deterministic ordering;
unknown dates never becoming ongoing; support-capture forwarding through
compile/render/build_pdf/CLI/snapshot boundaries; and preservation of all
existing stale, revoked and missing-capture failures. Confirm the CLI requires
captures only for approved evidence and cannot bypass provenance validation.

Confirm no applicant data, private paths, credentials, renderer changes,
matching, submission or TASK-010 work was introduced. Record APPROVED,
APPROVED WITH FOLLOW-UP or CHANGES REQUIRED in a new sanitized
docs/reviews/M1-FIX-001.md report with exact commit IDs and narrow regression
details. Do not modify implementation, merge, force-push or self-approve.
```
# Current review target — M1-FIX-002

Review the exact corrective implementation on branch `task/009-m1-fix-002`.

Base: `e2c5294ef6e95990b1089f519772661865134738`.
Implementation head: `3d9c7916f6a8cc2bcc9552160abff27d0ab5de36`.
Read `docs/tasks/M1-FIX-002.md`,
`docs/PROGRESS.md`, `docs/reviews/M1.md`, the TASK-004/006/007/009 contracts
and ADR-011/013/015/017. Inspect the full diff and run locked sync, Python
3.12, pytest, Ruff, format and mypy.

Focus on the typed approved `ContactName` binding: exactly one person entity,
matching display name, exact fact revision/support and rejection of omitted,
unrelated, stale or recomputed plans at validation and PDF boundaries. Confirm
QA checks required identity independently in Poppler and pypdf, including
renderer omission/substitution negative PDFs. Reproduce the synthetic URL and
maintainability/modularity/validation fixture and verify complete ordered text
with both extractors under the narrow documented normalization. Confirm the
trusted template disables hyphenation without changing candidate text and all
existing provenance, snapshot/export, CLI and isolation regressions remain.
No personal data or applicant approval is part of this fix.

Record a sanitized APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED
review with exact commit IDs. Do not modify implementation, merge, regenerate
personal outputs, self-approve or start TASK-010.

## M1-FIX-003 independent review target

Review the exact presentation correction commit below in a separate session;
do not approve it as the implementer.

```text
Repository: <repository>
Task: M1-FIX-003 — applicant-facing baseline presentation and confirmation audit
Base: d492707d80ddf97cdfae6c531ec5e84e38625645
Implementation commit: 7b54014ec7b2e2fcc83a52cb4003dcbb7937b49b
Tests follow-up: 1291ba94fbffdde1d89f5fba7b5ac78c7ebd5ab8
Documentation includes the review prompt; inspect the current branch head.
Branch: task/009-m1-fix-003

Read AGENTS.md, docs/tasks/M1-FIX-003.md, docs/adr/ADR-018.md,
docs/reviews/ADR-018.md, docs/ARCHITECTURE.md, docs/PROGRESS.md,
docs/reviews/M1.md and relevant ADRs. Inspect the full diff from the base.
Run `uv sync --locked`, Python 3.12, the 101-test
suite, Ruff check/format and mypy. Reproduce synthetic one-page and two-page
PDFs, compare complete Poppler and pypdf extraction, and inspect every raster
page. Verify no personal data or private artifacts entered Git.

Focus on the validated-plan presentation boundary: bound identity and compact
contacts; employment headings, responsibility bullets and exact placement;
linked versus standalone projects with unknown dates; complete project metadata
and partial-description handling; allowlisted skill categories preserving
same-name fact revisions, context/proficiency and notes; typed thesis/coursework
and omission of unknown degree names; date precision and no fabricated ongoing
status; UTF-8 output; and the shared canonical fact payload used by fact
approval digests, local review receipts and profile digests. Confirm empty new
optional fields preserve historical hashes, nonempty fields require re-review,
and `baseline-v2-presentation-adr018` is included in the trusted build identity.
Confirm schema drift, identity attacks, provenance, CLI, snapshot/export and
isolation regressions remain. Confirm this branch does not regenerate private
outputs, record applicant approval, start TASK-010, or mark ADR-018 accepted.

Record APPROVED, APPROVED WITH FOLLOW-UP, or CHANGES REQUIRED in a new
sanitized docs/reviews/M1-FIX-003.md report with exact commit IDs and any narrow
regressions. Update PROGRESS with the actual review state. Do not modify,
merge, force-push or self-approve.
```

## M1 profile-digest correction review target

Review `bc7439a047d5072a95668ebc8fa884b2acd7ae48` independently. This focused
correction follows the approved M1-FIX-003 merge
`6783fa21dfb3e61c8ce5d22d6894e081f21ce229` and is documented in
`docs/reviews/M1-DIGEST-CORRECTION.md`. Verify that approval-inclusive profile
digests preserve the existing private plan/profile relationship while fact
digests and local review receipts remain approval-independent, and that the
frozen legacy digest regression passes. Do not treat the correction as covered
by the M1-FIX-003 approval or approve it as the implementer.
