# Manually curating the master profile

This checklist is used in TASK-009 after the schema, renderer and safeguards exist. It is not a completed personal profile. Do not populate it with research examples or remembered chat facts.

## Input session

Choose an explicit private data directory outside Git. Start with contact details and one current/recent role so incomplete history does not stall schema feedback. Add remaining roles, projects, education, skills and languages deliberately. Importing a legacy CV, if later supported, creates drafts; extraction is not verification.

For the current local session, configure the supplied private root before
running project commands:

```sh
export JAE_DATA_DIR=$JAE_DATA_DIR
uv run jae config-check
```

The directory must remain outside the repository, be non-symlinked and have
restricted permissions. Future shells need to export `JAE_DATA_DIR` again;
the project does not write it to global shell configuration.

| Area | Collect and confirm | Never infer |
|---|---|---|
| Identity/contact | Exact display name, city/country, preferred email/phone/links | Contact values from memory or a similar profile |
| Employment | Actual employer, formal title, location, start/end precision, ongoing status, employment type | Missing months, normalized seniority, end date from another role |
| Responsibilities | What the applicant personally did; project/team/context; approved bullet wording | Participation into leadership; team work into sole ownership |
| Metrics | Value, unit, measure, comparator, period, scope, method and evidence | Percentage uplift, team size, customer count or cost savings |
| Skills/technologies | Actual use/exposure with specific evidence and depth | A vacancy keyword, adjacent tool, library ecosystem or taxonomy relation as possession |
| Education | Institution, degree/field, completion state/date, exact grade if useful | A course/enrollment as a completed degree |
| Certifications | Award/issuer/date/expiry/status | Online course as professional certification |
| Languages | Applicant-approved description/CEFR or exact named test score, evidence date | IELTS to CEFR conversion; German CV to German ability |
| Authorization | Optional current exact statement and scope/date if applicant wants it shown | Legal entitlement from residence, nationality or student status |
| Target label/summary | Approved professional positioning and relevant fact-backed wording | Job title from the JD as an already-held title |

The supplied three research documents contain no verified current career database for this applicant. No employers, grades, dates, contact details or language claims are prefilled in this repository.

## Evidence and wording

Give each source an evidence ID/revision. A user attestation may document firsthand responsibilities where documentary evidence would be impractical; label its nature honestly. Documentary/repository evidence needs a minimal immutable reviewed support capture, its hash and pinned source identity (file SHA-256 or repository object/revision). Avoid copying whole certificates or personal document numbers; a locator by itself remains an unverified reference. Record any later correction/withdrawal in source eligibility, even if the old capture remains available for history.

Review each fact and its source relationship, including subject/project/period. Approve the exact payload with current revisions. Then approve exact EN wording variants; keep long and short forms only if both preserve meaning. Do not approve a model's proposed summary merely because it contains some familiar terms.

Unclear fact → keep draft/unknown and collect clarification. No filler values and no “approximately” invented to conceal uncertainty. Unknown is useful data.

## Personal M1 acceptance

Build the baseline, inspect both extracted text reports, read every PDF page visually, and confirm no missing important history, overflow, unsupported claims or incorrect dates. The applicant reviews final content and layout before the exact snapshot is marked approved.

Commit only a sanitized milestone record stating the outcome and any open issues. The personal profile, documents, approvals and detailed QA remain private. M1 stays incomplete if the applicant has not supplied/approved the profile, even when all synthetic tests pass.
