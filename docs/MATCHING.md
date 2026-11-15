# Evaluate constraints and experience durations

TASK-015 adds a library (no CLI yet) in `job_application_engine.matching` that
evaluates typed constraints against a profile's **approved** facts at a pinned
`as_of` date:

```python
from datetime import date
from job_application_engine.matching.constraints import evaluate_constraints

results = evaluate_constraints(profile, constraints, as_of=date(2026, 11, 15), reviews=receipts)
```

The profile is validated first (approvals, receipts, support captures). Each
result has a `state` — `direct`, `explicitly_unmet`, `no_evidence` or
`unknown` — a `rationale` code and the exact fact revisions it relied on. No
state is an application decision; a gap stays visible.

| Constraint | Shape | Notes |
| --- | --- | --- |
| Language | `{"type": "language", "language": "German", "min_level": "B2"}` | Identity is an exact TASK-013 language concept (`German` = `Deutsch`) or, for a name no alias covers, the normalized name; a constraint naming an ambiguous or non-language term (`Spark`, `AWS`) is rejected, and such a fact never matches. Only a CEFR fact is compared. Test scores (IELTS …) are never converted, self-descriptions are never parsed, native is never C2. `min_level: null` with a matching fact is `unknown`. |
| Credential | `{"type": "credential", "name": "…"}` | Exact normalized name. Expiry uses `expires_at` (in UTC) or `valid_through` against `as_of`; an `awarded_on` after `as_of` is not yet awarded, one whose month or year contains `as_of` is `unknown`; in-progress, expired and not-yet-awarded are `explicitly_unmet`. |
| Degree | `{"type": "degree", "degree_name": "M.Sc."}` | Ongoing or withdrawn degrees are `explicitly_unmet`; completion dates are compared with their precision. |
| Authorization | `{"type": "authorization", "country": "…", "scope": null}` | Only an exact approved statement supports it. Missing, expired, non-matching or not-yet-dated statements (a statement month or year that contains `as_of`) are `unknown`, never a negative; nothing is inferred from location, residence, nationality or student status. |
| Duration | `{"type": "duration", "months": 36, "scope": {...}}` | Minimum months; `months_from_threshold` converts a TASK-012 duration threshold (`gte`/`unqualified` minimum, `gt` +1 month, `range` lower bound). Scope `overall` (employment), `skill` (projects listing a non-language concept by an exact alias) or `role` (exact title). |

Durations are calendar months, not FTE. Each interval contributes a lower bound
(months it certainly covered in full, given its date precision) and an upper
bound (every month it may have touched); the results are unions, so overlapping
jobs count once and gaps never count. Ongoing roles end at `as_of`. Intervals
with unknown start or end are listed as excluded. A documented total below the
threshold is `unknown`, not unmet, because the profile does not claim to be
complete (`below_threshold_with_unknown_intervals` when an undated interval
could close the gap). Responsibilities and skills without their own period
never add time, and a role scope matches the title exactly, so a promotion
without a date never yields "senior" years.

Mapping reviewed requirement rows (TASK-014) to constraints, coverage and
`equivalent`/`adjacent` states belong to TASK-016. The rules are fixed by the
reviewed synthetic oracle in `tests/fixtures/matching/`.
