# Independent source-research audit

- Audit date: 2026-09-08.
- Reviewer: independent agent `/root/research_review`.
- Scope: all three complete source reports, before implementation or adoption of their sample schemas.
- Recorded by: supervising agent from the reviewer's returned findings. This is not an implementation review or a claim that code passed tests.
- Source-audit verdict: **CHANGES REQUIRED before treating report examples as executable specifications.**

## Findings and planning responses

| Finding | Source evidence | Response in planning |
|---|---|---|
| Existing evidence IDs do not prove a generated sentence is supported | R2 311–316; R3 1808–1814; R1 numeric example near 1348 | ADR-011; exact approved variants and typed fields; A03/A04/A06/A27 |
| R3 schema makes important provenance optional and omits field-level support | R3 1075–1082, 1296–1311, 1443–1630 | ADR-001; TASK-002/003 require uniform facts, support bindings and revisions |
| Unknown dates can become Present; numeric measures/scopes are underspecified | R3 1170–1173, 1315–1336 | Typed date state/precision, scoped decimal metrics, A05–A07 |
| Qualification/language/authorization facts must not be inferred | R3 1443–1595; role duration examples elsewhere | Explicit completion, expiry and assessment types; TASK-015 interval policy |
| Renderer, schema, storage/UI, extraction, model, ESCO, reuse and output-format recommendations conflict | R1 811–869; R2 392–495; R3 387–435, 541–724 | ADR-001–010; real renderer/model experiments before adoption |
| Requirement examples omit spans, priority justification, negation and alternatives | R3 549–568 | TASK-011/012/014; raw source offsets, ALL/ANY and needs_review |
| Broader concepts are not equivalent technologies | R3 397–405 PyTorch/deep-learning diagram | Typed alias/adjacent relation distinction, A21/A22 |
| Mutable Boolean approval is insufficient | R3 667–673 versus R2 357 | ADR-012; immutable snapshots and exact hash-bound approval |
| Renderer and CI need early privacy/injection controls | R3 803–845 identifies threats but does not fully specify early controls | ADR-015; TASK-001/005/006/007/019 |
| Estimate ranges refer to different scopes | R1 short prototype; R2 ten-week roadmap; R3 34–54 days | ADR-014; bounded tasks and quality gates, no averaged timeline |
| Synthetic fixtures cannot constitute the applicant's genuine CV | Supplied files are design research, not a verified career profile | TASK-009 and PROFILE_CURATION; M1 personal gate kept explicit |

The reviewer confirmed consensus on canonical data, truthful tailoring, conservative linear PDF, measurable parsing checks, privacy minimization, human approval and delayed submission automation. The subsequent independent M0 planning review determines whether these responses are adequate; this source audit alone does not approve the authored architecture.
