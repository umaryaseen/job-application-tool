# Project brief

## Problem and objective

Preparing German job applications requires accurate career facts, appropriate document conventions and vacancy-specific evidence. Independently edited CV files drift. Free-form AI writing can introduce plausible but unsupported claims. The project will compile reviewed structured data into application documents with an auditable history.

Primary user: one technically capable applicant using a local laptop for full-time jobs in Germany, especially software/data/AI roles. This is applicant assistance, not employer-side candidate screening.

## Product principles

Truth → parseability → relevance → readability → efficient preparation. This order synthesizes R1–R3 and the user's requirements. Success means a useful, trustworthy application package and less manual tailoring, not application volume.

The canonical profile is the only career source. PDF/DOCX are outputs. Facts may be selected, reordered and represented through approved equivalents; employers, dates, credentials, skills, technologies, metrics, proficiency, responsibilities, team sizes, work authorization and years of experience cannot be invented or silently changed.

## Scope and milestone gates

| Milestone | User-visible result | Release gate |
|---|---|---|
| M0 | Research comparison, ADRs, architecture, tasks and local handoff | Independent planning review; no claim of working software |
| M1 | Reviewed master profile → usable baseline CV.pdf + CV.txt + QA | No unsupported claims, verified output structure, 1–2 A4 pages, actual applicant review |
| M2 | Pasted English/German JD → reviewed requirements and evidence matrix | Requirements trace to JD spans; ambiguity and gaps remain visible |
| M3 | Job → evidence selection → tailored CV → QA → approval | Adversarial factuality tests and complete snapshot integrity pass |
| M4 | Evidence-backed cover letter and local application tracker | Letter provenance; correct snapshot/status/outcome association |
| M5 | Optional localization, DOCX, taxonomy, retrieval, AI and UI | Each feature has its own evidence-backed gate; no automatic scope expansion |

**The first tested tailoring MVP is M3.** It works without LLMs or embeddings. Optional AI suggestions can make it faster later; deterministic selection already produces vacancy-specific documents.

## Deliberately postponed

No job-board scraping, URL fetcher, job discovery, auto-apply, portal prefill, CAPTCHA handling or mass submission in the MVP. Also postpone React/FastAPI, Docker, PostgreSQL, vector databases, ESCO service hosting, local LLM setup, cloud providers, DOCX, cover letters and tracking until their defined tasks. No multi-user hosting or employer-side hiring tools are designed here.

## Assumptions to validate

- Laptop OS, CPU architecture, RAM and installed tooling have not been observed. TASK-001 records them; the renderer spike runs on that machine.
- Applicant can manually curate and approve facts. The supplied reports contain examples, not a complete current applicant profile. Task 009 collects actual evidence; no ready-to-submit personal CV can be honestly produced yet.
- First document is English for English-language German vacancies. All schemas retain locale and German Unicode from day one. German wording approval and output are Task 025.
- One user and one local writer; ordinary local filesystem, no shared network database. Reassess on multi-user requirements.
- No paid model or API is needed through M4. Any later provider, budget or data-disclosure choice is an explicit opt-in.
- The user wants a private GitHub repository. The current cloud workspace has Git but no laptop bridge or `gh`; restore and GitHub setup occur on the laptop.

## Success measures

Before application use: zero invalid claim references or unsupported published wording; all critical fields recovered by both local PDF extractors; correct sequence and German Unicode; page/size/readability checks; independent implementation review and exact document approval. These are project gates, not employer ATS guarantees.

After tracking exists: preparation time and correction count per application; observed responses and interviews divided by **submitted** applications, with sample sizes, dates and cohorts. Do not imply that small observational cohorts establish causation or optimize automatically from rejection outcomes.

## Out-of-band decisions

Actual dates, metrics, availability, language levels, degree status and authorization are applicant decisions at profile curation. Renderer and embedding effectiveness are experiment decisions at their spikes. No question about those blocks creation of the planning package or TASK-001.
