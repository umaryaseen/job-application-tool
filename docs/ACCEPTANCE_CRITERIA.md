# Acceptance criteria and test specification

This is the required test plan, not a claim tests already exist or pass. Each named case is implemented in the linked task; unimplemented cases are `NOT RUN`. Synthetic fixtures must be clearly marked, realistic enough to expose parser behavior, and contain no applicant data. No live employer application is submitted to test the system.

## Milestone release gates

| Gate | Required evidence |
|---|---|
| M0 planning | Three sources read; disagreements and assumptions explicit; complete backlog/ADRs; independent review and package integrity checks |
| M1 baseline | TASK-001–009 reviewed; actual applicant-reviewed profile; baseline PDF/TXT; claim validation, two extractors, layout/Unicode/page checks; exact artifact approval |
| M2 matrix | TASK-010–016 reviewed after M1; EN/DE source-grounded extraction, priorities/groups and exact matching; unknown/unmet/adjacent distinctions; user can correct source-bound requirements |
| M3 tailoring MVP | TASK-017–020 reviewed; two different pasted jobs produce relevant evidence selections while preserving facts; all M1–M3 regression tests pass; tampering blocks export |
| M4 letters/tracker | TASK-021–023 reviewed; one-page fact-backed letter and immutable document references in transactional tracker; no submission integration |

M1 technical fixture success may be recorded separately from personal acceptance. **The milestone is not complete until the applicant's genuine CV is curated, generated and reviewed.** The reports and chat memory cannot supply verified facts automatically.

## Mandatory test matrix

| ID | Named behavior / fixture | Assertion | Task |
|---|---|---|---|
| A01 | schema_valid_and_invalid | Unknown keys, coercions, invalid enums, overlimits, unsupported versions fail; valid synthetic profile succeeds | 002 |
| A02 | profile_evidence_graph | Empty/dangling/duplicate references, cycles, revoked evidence, unsupported bindings, unpinned documentary references, mutated/missing support captures fail | 003 |
| A03 | every_visible_claim_is_bound | All visible candidate text including identity, summary, skill labels, degree and date has a claim node and approved sources | 004 |
| A04 | unrelated_valid_evidence | A real ID cannot authorize unrelated text; replacing claim text with novel prose fails | 003, 019 |
| A05 | date_precision_and_state | Unknown end is not Present; reversed/invalid dates fail; incomplete precision is explicit | 002, 004 |
| A06 | numeric_scope_verification | 30% vs 30 percentage points; approximate/exact; decimal comma/dot; number words; wrong role/project/period/unit fail | 003, 019 |
| A07 | language_and_credentials | No IELTS→CEFR inference; no native/C2 equivalence; expiry/ongoing/completion preserved; missing authorization stays unknown | 002, 015, 019 |
| A08 | renderer_data_injection | Typst/HTML/Markdown metacharacters, template delimiters, file/remote links stay data or are rejected; no file/network access | 005, 006 |
| A09 | pdf_text_round_trip | Poppler and pypdf each recover all expected visible claim text under documented normalization | 007 |
| A10 | pdf_critical_fields | 100% name/contact/employer/title/date/degree/skills fields in correct entry scope for golden fixtures | 007 |
| A11 | pdf_reading_order | Exact expected section/entry/claim sequence; deliberately swapped/two-column fixture fails despite same words | 007 |
| A12 | standard_headings | Finite allowed EN/DE headings, correct document order; no creative replacements | 007, 025 |
| A13 | page_count_and_geometry | 1–2 A4 pages, no out-of-page words; overflow fails; raster pages manually checked | 007, 018 |
| A14 | unicode_german | `ä ö ü Ä Ö Ü ß`, `Müller`, `Groß`, `İpek`, `Łukasz`, `François` survive NFC and extraction; missing glyph rejected | 007 |
| A15 | ats_regression | Fixed approved synthetic fixtures, baseline expected text/field map; duplication, hidden text, lost dates and ordering changes detected | 007, 020 |
| A16 | job_snapshot_integrity | Raw hash preserved, duplicate import identified, changed JD creates revision, bad UTF-8/oversize rejected, no network | 010 |
| A17 | extraction_source_spans | Exact original Unicode offsets/quote round-trip in EN/DE; invented or out-of-bounds span fails | 011 |
| A18 | priority_classification | Required/must/erforderlich vs preferred/wünschenswert; negation and ambiguous section cues handled; no forced priority | 012 |
| A19 | alternatives_and_groups | Python OR Java; degree OR equivalent experience; conjunctive nested group; unknown grammar remains needs_review | 012 |
| A20 | requirement_review_versions | Correction preserved; JD edit invalidates prior review; ambiguous clauses cannot be silently used as hard gates | 014 |
| A21 | exact_skill_normalization | C/C++/C#/R/.NET, word boundaries, EN/DE aliases; deep learning ≠ PyTorch; AWS ≠ SageMaker | 013 |
| A22 | match_states | Explicit negative vs no evidence vs adjacent vs direct; project exposure cannot satisfy production/depth requirement | 015, 016 |
| A23 | experience_interval_union | Overlap counted once, gaps excluded, role/skill scope respected, fixed as-of date; unknown precision returns uncertainty | 015 |
| A24 | coverage_denominators | ANY/ALL count semantics, duplicate requirements, preferred/mandatory split, zero denominator=N/A | 016 |
| A25 | deterministic_selection | Different JDs select relevant approved bullets; chronology/identity facts unchanged; stable tie-breaking; evidence trace kept | 017 |
| A26 | bounded_page_budget | Remove optional low-value content only; protected sections survive; at most 20 iterations; no font shrink or PDF clipping | 018 |
| A27 | generated_claim_adversaries | Correct ID/wrong employer, leadership inflation, exposure→expertise, negation flip, invented technology/degree/dates/years fail | 019 |
| A28 | immutable_application_snapshot | Atomic completion, no overwrite, interrupted build leaves no ready snapshot; exact bytes and manifest recoverable | 008 |
| A29 | approval_and_tamper | Exact hashes; PDF/plan/template/profile modification, stale wording, source correction/supersession/revocation/deletion, missing capture/eligibility and elapsed expiry block new export; external original removal alone does not invalidate intact active capture | 008, 019 |
| A30 | full_pipeline_baseline | Real CLI builds a fixture profile into PDF/TXT/QA without LLM/network; nonzero exits on unsupported input | 009, 020 |
| A31 | full_pipeline_tailoring | Pasted JD→review→matrix→tailor→QA→approve→export, plus an unsupported injected claim that fails | 020 |
| A32 | cover_letter_provenance | Company claims from JD/company evidence; applicant claims from profile; motivations/availability approved; unreviewed prose rejected | 021 |
| A33 | tracker_snapshot_foreign_keys | Status events reference real immutable snapshot; transaction rollback and migration; approved ≠ submitted | 023 |
| A34 | local_privacy | Private-path/secret stage guard; no PII logs or CI artifacts; no external network in build; temp cleanup and paths constrained | 001, 006, 019 |
| A35 | semantic_real_model | Held-out bilingual positive/negative pairs with actual pinned encoder; adjacent never promoted solely by cosine | 027, 029 |
| A36 | provider_injection | Hostile JD, invalid JSON, timeout, oversize, unknown IDs; no tools/egress beyond chosen provider; failures retain deterministic path | 028, 031 |
| A37 | docx_round_trip | Field/order/Unicode checks from XML plus actual office-render layout QA; no PDF-to-DOCX inference | 024 |
| A38 | localization_integrity | Approved DE variants preserve titles, date state, numeric units and skill depth; incomplete translations cannot silently pass | 025 |
| A39 | esco_revision_cache | Same data hashes reproduce concepts; broader/related relations not aliases; unavailable dataset does not break baseline | 026 |
| A40 | backup_restore_and_analytics | Export/restore hashes and snapshot links preserved; denominators count actual submissions; no causal claims | 033 |

All requested categories, including semantic matching and snapshot/version integrity, have explicit implementation tasks. Optional semantic tests are not part of M1–M3's deterministic release, but **must run before the semantic feature is enabled**. A stub is not evidence of embedding quality.

## Fixture corpus and quality thresholds

M1: at least one compact and one two-page synthetic career profile, concurrent positions, ongoing and unknown dates, education/certification states, typed metrics, accented names and German text, long bullets/URLs, and a deliberate overflow case. Include realistic synthetic organization names and reserved domains (`example.com`, `.invalid`). Do not send fictional applications to real employers; ATS vendors may treat obvious placeholder entities differently.

M2: at least 12 short EN and 12 DE fixture postings covering explicit cues, negation, conjunction/disjunction, education equivalence, languages, years, locations, unrelated “benefits” and ambiguous clauses. Maintain separate labels for requirements, priority, spans, groups and match evidence. Have a reviewer approve expected labels independently of the implementation. Golden deterministic rules must match those explicit expected labels exactly; this is not a general language-accuracy claim.

M3: at least two role-family JDs against the same profile plus adversarial mutations. Test the exported PDF, not just the internal object. Expected text order must be defined independently of the production traversal; generating the expected answer through the same function would mirror the bug.

Later semantic feature: freeze a labeled EN/DE retrieval corpus in TASK-027, with at least 40 supported pairs and 40 hard negative/adjacent pairs across both languages. Separate tuning and held-out cases; report Recall@5, precision of retrieved suggestions, harmful promotions (required zero), CPU time and peak memory. Suggested adoption bar: ≥10 percentage-point Recall@5 improvement over exact/alias retrieval on semantic-positive held-out cases, with no false promotion to `direct/met`. Record raw numerator/denominator and uncertainty from corpus size. This is an engineering experiment threshold, not a research-derived universal value; changing it requires the reviewer to see why before looking at the held-out outcome.

## QA report contract

Each check returns `check_id`, status (`pass/fail/warn/not_checked`), measured value, threshold or expected value, tool/version, artifact digest and minimal diagnostic references. Include exact-field completeness per parser, missing/extra blocks, order errors, pages/dimensions, bytes, Unicode failures, unsupported claims, and visible requirement gaps. Empty denominators use null/N/A.

Hard failures: unsupported or stale claim; missing critical fields; missing/altered meaningful text; wrong order; unreadable glyphs; >2 pages; clipping; absent text layer; snapshot/hash mismatch. Unknown approval is not a warning that can be ignored. File-size default is a project gate of <2,000,000 bytes, overridable only by a documented portal-specific policy in later work. Missing requirements are match gaps, not factuality failures.

Visual checks are recorded as manual, with reviewer identity and exact snapshot hash. Do not claim generic PDF table/font/ATS detection beyond the checks actually implemented. pypdf/Poppler are independent text engines, not employer ATS emulators.

## Test execution and reviews

TASK-001 creates the real tooling commands. Thereafter, each task runs its focused suite plus Ruff and mypy; each milestone runs all tests for implemented features on a clean locked environment. Record versions, exit status and skipped checks in PROGRESS. Rendering tests require the real backend and both extractors. Model tests require installed pinned weights for the semantic milestone.

CI uses only synthetic data, minimal permissions and no provider secrets. No live ATS calls. Snapshot updates need an explained intentional change and independent review; never regenerate expected artifacts blindly. Preserve failing adversarial tests while fixing implementation.
