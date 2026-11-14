# TASK-009 sanitized publication snapshot

This publication branch is derived from reviewed snapshot commit
`266e5ef3ae217a9e8edb0c72c509996d9a891b12` (source tree
`701ac93359c7d8b3bb2c383c21e63479b323db9e`) and starts from
`origin/main` `0cc9119df20a2be974f8db41ed9869663493f800`.

The documentation was sanitized before publication by replacing concrete
workstation, repository and private-data paths with `uv`, `$HOME`,
`<repository>`, `$JAE_DATA_DIR` and `$TMPDIR` references. Historical review
results, links, template identities and approval boundaries remain intact.
No source, test, dependency, fixture or private applicant file was read or
changed; non-documentation files remain byte-identical to the reviewed source.

The independent merge review's macOS result remains **147 tests passed**, with
its recorded lint, format, type, CLI and rendering checks. That result belongs
to the reviewed source tree; publication CI is still pending. TASK-009 exact
PDF/TXT content approval, final artifact approval and export remain pending.

## Hosted CI evidence recorded 2026-11-14

The pending-CI statement above describes the original publication time.
[CI 43539855170](https://github.com/umaryaseen/job-application-tool/actions/runs/43539855170)
subsequently passed on exact published head `58f0c183`: **147 tests passed in
80.68s**, plus Ruff, formatting (68 files) and mypy (40 source files). The
[publication state reviewer](TASK-009-PUBLICATION-STATE.md) independently
fetched the run and job logs. This does not qualify a later PR head; check its
own CI result before integration. Private document approvals remain pending.
