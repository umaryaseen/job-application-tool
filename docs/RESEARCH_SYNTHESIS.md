# Research synthesis

Date: 2026-09-08. All three supplied reports were read in full: R1 (1,444 lines), R2 (870), R3 (2,008). [SOURCE_REGISTER.md](SOURCE_REGISTER.md) supplies exact filenames, hashes and retrieval notes. References such as `R3 §Security model, lines 802–848` refer to those immutable copies. Research examples are illustrative, not adopted specifications or applicant evidence.

## Agreement across all three reports

| Shared recommendation | R1 anchors | R2 anchors | R3 anchors | Result |
|---|---|---|---|---|
| Structured master data; documents are projections | 150–231, 509–560 | 226–317 | 321–361, 494–539 | Custom canonical JSON; profile revisions |
| Tailor selection/wording, preserve facts | 455–473, 698–733 | 240–260, 270–317 | 339–361, 510–539 | Approved variants and typed field rendering |
| German baseline: 1–2 A4 pages, reverse chronology | 35–54, 291–333 | 67–106 | 59–69, 157–186 | Explicit template contract and page gate |
| Single text flow, body contact details, conventional headings | 56–81, 316–333 | 129–201 | 188–209, 264–319 | PDF round-trip and structural QA |
| PDF default, portal instructions take precedence | 123–148 | 161–174 | 157–186 | PDF/TXT first; DOCX postponed |
| Photos/demographic details optional; omit by default | 35–54 | 31–65 | 111–155 | Minimal data; no optional photo template in MVP |
| Requirements distinct from evidence; never fill a gap by invention | 562–667 | 392–468 | 541–624 | Reviewed requirement matrix |
| Local scores cannot reproduce every employer ATS | 1365–1387 | 131–159, 605–637 | 264–319 | Separate measured checks and coverage |
| Minimal data disclosure and human review | 1060–1190 | 561–603 | 727–847 | Offline defaults and hash-bound review |
| Delay or constrain submission automation | 764–799, 1389–1443 | 529–559, 591–603 | 437–455, 727–772 | No submission layer in MVP |

This is agreement within the reports, not three independent experiments. They reuse several of the same authorities, especially BA and Greenhouse. Official conventions and vendor failure descriptions are stronger evidence than each report's estimates, sample weights or library recommendations.

## Disagreements and explicit decisions

| Question | Different recommendations | Decision and rationale | Record |
|---|---|---|---|
| Canonical schema | R1 560: JSON Resume extensions; R3 387 and 1061–1671: custom schema | Custom evidence-aware schema; later lossy JSON Resume projection | ADR-001 |
| Storage | R1 844–869: files/SQLite; R3 692–695: PostgreSQL with SQLite mode | Files first; SQLite only when tracking needs it; one backend | ADR-002 |
| Interface | R1 844–854: CLI/FastAPI; R3 678–724: Next.js/FastAPI/Compose | CLI first; no server or UI before reliable pipeline | ADR-003 |
| PDF generation | R1 851: RenderCV; R3 703–707: HTML/CSS + Playwright | Recommend RenderCV, conditional on a local comparison; implement one winner | ADR-004 |
| Semantic model | R1 813–816: Sentence Transformers/KeyBERT/SkillNER; R3 697–701: spaCy/Transformers/local LLM | Exact baseline first; optional multilingual Sentence Transformers benchmark | ADR-005 |
| ESCO role | R1 593–596: internal taxonomy; R2 392–446 and R3 389–414: central ESCO | Local aliases first; pinned dataset enrichment later | ADR-006 |
| Extraction | R1 1397: deterministic first; R3 541–571: structured LLM surrounded by rules | Rules with source spans and uncertainty; LLM proposes only later | ADR-007 |
| Model location | R1 856–869: local mode; R2 571–579: selective cloud; R3 697–701: local optional | Neither required; application LLM off by default; provider choice deferred | ADR-008 |
| DOCX | R1 959: later; R2 470–495 and R3 1936–1942: early PDF+DOCX | Independent python-docx export after M3; no PDF conversion | ADR-009 |
| Resume Matcher | R1 811, 829–838: evaluate/fork; R2 535: reference/layer; R3 417–435: compose | Study workflows; no fork or runtime coupling | ADR-010 |
| Factual guarantee | All demand truth; example checks only test membership | Scope-bound source support and approved text, not reference existence alone | ADR-011 |
| Approval and versions | R2 357, 497–527: approved version; R3 667–674: Boolean | Separate fact/wording/document approval; exact hashes and revisions | ADR-012 |
| Section order/localization | R1/R2 prioritize experience; R3 49 has skills before experience; R3 v0.1 bilingual | Experience-led EN first; multilingual schema/fixtures now, approved DE later | ADR-013 |
| Scope and time | R1 3–5-day prototype; R2 ~10 weeks; R3 34–54 person-days | Different scopes; gated slices, no averaged promise | ADR-014 |
| Security/deployment | R3 adds services/Compose; R1 allows very small local pipeline | Single offline process, bounded renderer; no deployment infrastructure | ADR-015 |
| Submission policy | R1 hard-fit gate and queue; R2 prefill; R3 policy layer | Preparation remains independent; future source policies default deny | ADR-016 |

ADRs include alternatives, consequences, validation gates and reconsideration triggers. They are engineering decisions/recommendations under the user's delegation, not attributed to unanimous research or silently assumed user preferences.

## Corrections required before implementation

**References do not prove entailment.** R2 311–316 calls ID tracing a zero-hallucination invariant, R3 1808–1814 tests only membership, and R1 1348 uses existence of a number elsewhere. These permit false prose with real IDs. M1–M3 restrict export to approved exact variants and deterministic slots. Later wording requires human review against scoped sources. Tests must reject the correct number attached to the wrong employer, non-leadership rewritten as leadership, and adjacent AWS knowledge rewritten as SageMaker experience. No claim of automated proof of real-world truth is made.

**R3's schema is not safe to copy.** Evidence is optional at the root (1075–1082), in bullets (1296–1311) and skills (1532–1539). Education, languages, credentials, contact/authorization and summaries lack uniform fact-level support. The shared month definition permits null starts and ends (1170–1173). Metrics permit untyped strings and optional units/evidence (1315–1336). Required IDs, explicit unknown/ongoing state, typed values, approval bindings, expiry/status and graph validation replace those examples.

**Matching is not a proof engine.** The illustrative formulas in R1 616–627, R2 455 and R3 596–602 are not calibrated. Do not ship them as defaults or use employment titles to infer seniority/years. Broader concepts are not aliases: R3's PyTorch/deep-learning diagram at 397–405 is unsafe if interpreted as equivalence. An ESCO relationship or high cosine similarity can suggest an adjacent fact, never establish skill possession.

**Missing is not false.** No profile evidence for German B2 means unknown/no evidence. A user-confirmed A2 level against B2 is explicitly unmet. A preference to stay in one city differs from a legal authorization constraint. Preserve those distinctions and OR alternatives rather than multiplying everything by a fit score.

**Approval is not a mutable Boolean.** Approval covers exact content, source revisions and artifact hashes; editing any of them creates an unapproved version. Tracking status changes do not rewrite previously submitted documents.

**ATS QA starts in M1.** Some diagrams place QA after generation and late in the roadmap. Before the first real CV, text round-trip, protected fields, reading order, Unicode, pages, and visual review are required. Two PDF extractors are not two employer ATS products. Do not claim tests passed because generated text contains a few expected words.

## Current upstream verification

Primary upstream pages were checked on 2026-09-08 to validate availability and update assumptions; supplied reports remain the design source. No dependency was installed or benchmarked by this planning step.

- RenderCV documents Python 3.12+, YAML input, configurable design and locales. Its ATS page describes its own checks; this is not proof that a custom template passes our fixtures. [RenderCV docs](https://docs.rendercv.com/), [ATS documentation](https://docs.rendercv.com/ats_compatibility/).
- JSON Resume's old schema repository is archived and points to the monorepo. Pin the actual schema revision in the later adapter task; do not depend on the archived package layout. [Migration notice](https://github.com/jsonresume/resume-schema), [schema location](https://github.com/jsonresume/jsonresume.org/tree/master/packages/schema).
- Resume Matcher currently describes master-resume upload, JD tailoring, review and PDF export, and declares Apache-2.0. OpenResume declares AGPL-3.0 and provides a builder/parser. Neither was inspected at implementation depth; no code has been copied. [Resume Matcher](https://github.com/srbhr/Resume-Matcher), [OpenResume](https://github.com/xitanggg/open-resume).
- **ESCO correction:** the official page marks the current local API as reference-only and due for replacement. Use downloaded versioned EN/DE data, without the API service. Official downloads offer CSV and other formats; record attribution terms separately from the API software license. [API notice](https://esco.ec.europa.eu/en/use-esco/use-esco-services-api), [downloads](https://esco.ec.europa.eu/en/use-esco/download), [reuse terms](https://esco.ec.europa.eu/en/use-esco/download/privacy-statement).
- The proposed multilingual MiniLM baseline's model card specifies a short input limit. Embed individual bounded requirement/fact chunks and reject silent truncation; do not embed a whole CV/JD as one string. [Model card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
- Greenhouse documents formatting failure cases and a 2.5 MB parser limit. Our <2,000,000-byte default is a conservative project policy, not a universal ATS rule. [Vendor documentation](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse).

## Reuse and postponement

Use focused components when their introducing task needs them: Pydantic for contracts, a renderer, local PDF extractors, and later Sentence Transformers and python-docx. Use standard library JSON, hashing, CLI parsing and sqlite3. KeyBERT/spaCy/SkillNER are candidates only if the rule baseline demonstrates a need. Do not install NLP libraries merely to expand a few aliases.

Do not fork Resume Matcher, vendor OpenResume or pyresparser, adopt AIHawk/ApplyPilot, deploy an ESCO server, or build browser automation now. Mature libraries reduce work; inheriting an entire unrelated product adds work. See [DEPENDENCIES.md](DEPENDENCIES.md).

## Unresolved questions and owners

| Question | Owner / resolution | Blocks |
|---|---|---|
| Laptop runtime compatibility and installation | Local Codex, TASK-001 | Execution on laptop |
| Renderer winner, exact version and theme | TASK-005 experiment + independent reviewer | TASK-006, not schema work |
| Current factual profile/contact/language/authorization | Applicant with curation workflow, TASK-009 | Personal M1 acceptance |
| Exact model/revision and useful retrieval improvement | TASK-029 benchmark | Optional semantic feature only |
| ESCO dataset availability/terms | TASK-026 manual official acquisition | Optional taxonomy only |
| Cloud provider/model/data budget | Applicant when enabling TASK-031 | Cloud option only |
| GitHub authentication | Applicant using native gh flow on laptop | Remote creation/push only |
| Open-source license for original code | Owner before any public distribution | Public release only |

None warrants guessing or blocks the complete planning package. Milestone progression depends on evidence of quality, not calendar dates.
