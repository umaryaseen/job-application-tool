# Requested application workflow

This roadmap describes the requested product; it is not a list of available commands. Keep one local package, one canonical profile and one private application store.

| Step | Saved result | Existing path |
| --- | --- | --- |
| Capture a vacancy | Supplied company/title/job ID/source; exact input, faithful Markdown and revisions; missing fields remain unknown | TASK-010 draft intake implemented; see JOB_INTAKE |
| Analyze requirements | Exact quotes, required/preferred/unspecified, language/degree/seniority/technology constraints | TASK-011–014 |
| Compare both CV bases | Applied AI versus Full Stack; evidence map, recommendation and gaps; both base versions preserved | TASK-009 registration, TASK-015–017 selection extension |
| Tailor documents | Separate CV and letter in PDF/DOCX; chronology and confirmed facts retained | TASK-017–022, TASK-024 |
| Verify and review | Factual/text/layout/grammar QA, source/base/run manifest, exact document review | Existing validators/QA/snapshots plus TASK-019–020/024 |
| Prepare interviews | Role summary, likely questions, factual STAR outlines, gaps and interviewer questions | Bounded follow-up to the application slice |
| Track real progress | Company, actual submission/date/files, interviews, next action/date, contacts and outcomes | TASK-023 |
| Learn across jobs | Unique current postings per skill/priority with source quotes; known outcome counts and learning priorities | TASK-013/016/023 plus TASK-033 analytics extension |

## Application pack

Private job folder: original text, `job_description.md`, `job_record.json`, `match_analysis.json`, CV/letter PDF and DOCX, `interview_prep.md`, QA and immutable manifest. Preserve source/profile/base versions; avoid competing spreadsheet/data stores.

Choose the more relevant base and use confirmed evidence from either where useful. Explain the choice without invented ATS scores. Rewriting cannot invent technology, results, promotion, leadership or proficiency. New wording follows existing proposal/review rules. Degree, language and availability constraints stay visible.

The Markdown JD preserves employer wording/language; analysis is separate. Interview answers distinguish demonstrated results from a hypothetical approach. Preserve the user's actual question/answer drafts and later interview feedback.

## Records and outcomes

Preparation state and application stage are separate. Generated files do not imply submission. Historical imports start `unknown` unless Umar confirms a stage. Stages include not applied, applied, screening, assessment, interview, offer received, offer accepted/declined, rejected, withdrawn and closed. An employer offer and the applicant's acceptance are distinct events.

Maintain actual known dates and event history. Deadline, salary, contact, interview notes, next action, follow-up date and reason remain unknown until provided. The user submits manually. Storing a follow-up date does not schedule a reminder.

Count distinct current postings per normalized skill, preserving required/preferred/unspecified and quote evidence. Show sample size; this selected sample is not the entire market. Response/rejection rates require known submissions and outcomes, with unknowns disclosed.

## Delivery order

1. Complete TASK-010 implementation review and use private draft intake under ADR-018; CLEANUP-001 is integrated.
2. Complete TASK-009 using actual private profile and both bases, preserving approvals and reconciling missing facts. Draft intake does not complete this gate.
3. Deliver requirement extraction/matching/tailoring through the existing dependencies, comparing both bases before producing a tailored CV.
4. Complete the application pack with letters, DOCX, tracking and interview notes, tied to existing snapshots.
5. Aggregate skill demand and known outcomes. Optional ESCO, embeddings, UI, reminders and integrations stay deferred.

The historical 35-task backlog is acceptance detail, not 35 new products to build before the first useful application.
