# TASK-012 synthetic classification oracle

`classification.json` holds short synthetic English and German postings with
literal expected priority, negation, alternative-group and threshold labels.
They were authored from TASK-012, A18/A19, ADR-007 and the rules below before
the classifier existed. They are synthetic, not applicant data. A separate
review must approve the labels independently of classifier output. Candidate
boundaries and kinds come from the already reviewed TASK-011 extractor.

## Row format

Each expected row is one TASK-011 candidate in source order:

- `quote`: the candidate's literal source clause.
- `role`: `requirement`, `priority_marker` or `non_requirement`.
- `priority`: `mandatory`, `preferred` or `unspecified`.
- `basis`: a fixed rationale code (below).
- `negation`: `none`, `requirement_negated` or `unsupported`.
- `condition`: `null`, a literal term quote, or `{"any": [...]}` /
  `{"all": [...]}` whose members are term quotes or nested groups.
- `thresholds`: literal numeric constraints with operator, value or CEFR level,
  unit and literal scope quote (`null` when unclear).
- `review_reasons`: sorted codes; `needs_review` is true exactly when non-empty.

`duplicates` lists groups of row indexes that are equivalent repeated
requirements. Every row remains `draft`; no label approves a requirement.

## Labeling rules

1. Explicit clause cues decide priority. Mandatory: required, requires, must,
   mandatory, essential, necessary, prerequisite; erforderlich, zwingend,
   notwendig, vorausgesetzt, Voraussetzung, muss/müssen/musst, Pflicht,
   unabdingbar, unerlässlich. Preferred: preferred/preferably, nice to have,
   a plus, bonus, an advantage/advantageous, desirable/desired, ideally,
   beneficial, helpful; wünschenswert, von Vorteil, vorteilhaft, idealerweise,
   bevorzugt, ein Plus, Pluspunkt.
2. Recognized negated requirement cues ("not required", "No German required",
   "do not need", "nicht erforderlich", "kein Muss", "Keine … erforderlich")
   mean explicitly not required. Their inner cue words do not count as
   mandatory. Any other not/no/without/nicht/kein/ohne makes negation
   `unsupported` and needs review; priority still follows the explicit cues.
3. Mandatory plus preferred, or mandatory plus not-required, in one clause is a
   conflict: `unspecified`, `conflicting_clause_cues`. Preferred plus
   not-required is preferred.
4. General headings (Requirements, Your profile, Anforderungen, Ihr Profil)
   carry no priority. A heading containing a cue (Nice to have:, Must have:,
   Wünschenswert:, Muss-Kriterien:, Minimum qualifications:) supplies a
   heading cue for clauses without their own cue. A standalone candidate whose
   whole text is a priority phrase (for example `Nice to have`, `Von Vorteil`)
   is a `priority_marker`; it supplies the cue to later clauses until the next
   heading. A clause cue that disagrees with the heading cue is a conflict:
   `unspecified`, `clause_conflicts_with_heading`; a preferred section never
   turns into mandatory.
5. Responsibility and context/benefit candidates are `non_requirement`:
   always `unspecified`, no condition or threshold. A priority cue inside them
   is recorded and needs review.
6. Recognized technology and language mentions are terms. A run joined only by
   commas and one consistent conjunction forms a group: OR/oder/and/or/und/oder
   → `any`; and/und/sowie/as well as → `all`. A comma-only list, mixed AND/OR
   without explicit either/both/parentheses, or terms separated by other words
   do not form a supported group. Either/entweder and both/sowohl…als auch
   create explicit nested groups.
7. Education: `<degree phrase> or equivalent/comparable experience or
   qualification` (oder vergleichbare/gleichwertige …) is one `any` group of
   two terms. "or a related field" / "oder einem verwandten Fach" stays inside
   the degree term. Other education OR text is unsupported.
8. A condition is emitted only when every OR/AND connective in the clause is
   inside a supported structure. Otherwise it is `null` with
   `unparsed_alternative` and/or `unparsed_conjunction`. An OR is never split
   into separate mandatory conditions.
9. Durations: integer years/months with at least/minimum/mindestens or `N+`
   (`gte`), more than/über (`gt`), `N-M` (`range`) or a plain number
   (`unqualified`). Scope is the literal text after the number up to a cue,
   next threshold or clause end, minus a leading of/in/with and trailing
   linking words. Vague (several/mehrere) and decimal quantities create no
   threshold and need review. CEFR levels use the clause's single language
   term as scope; "or higher"/`mindestens` give `gte`.
10. Requirement rows with no condition and no threshold need review
    (`no_supported_condition`). Multiple thresholds need review.
11. Duplicates merge only rows with the same case-folded quote and identical
    kind, priority, basis, negation, condition, thresholds and review reasons.
    The same text under different headings is not a duplicate.

The corpus proves these exact examples, not general EN/DE language accuracy.
