# TASK-012 independent fixture-label review

Provenance (recorded by the implementer, not part of the reviewer's text):

- Reviewer: Codex, a separate agent session — `codex exec` (OpenAI Codex
  v0.160.0, model `gpt-6.1-terra`, reasoning effort `xhigh`), sandbox
  `read-only`, approval `never`, session `01a1da66-a236-7d40-9c29-2211c75ce725`.
  Implementer: Claude Code (Claude Opus 5.5). The reviewer did not author the labels.
- Reviewed in a clean detached checkout of fixture commit `2988f636` (tree
  `1a78911c`) containing no classifier code; implementation work happened in a
  different worktree and was not visible to the reviewer.
- `classification.json` SHA-256 at review:
  `16b05e8f0f6f1a8d274de6b06e9eacf08fc3af47d6a802fd564537d4be5b18d1`.
- The reviewer ran 53 shell commands, all inside that checkout; process exit 0.
  It reported "CLI version unavailable"; the version above is from the CLI banner.

The reviewer's report follows verbatim.

---

VERDICT: APPROVED

# TASK-012 fixture-label review

- Reviewer: Codex, GPT-6; CLI version unavailable
- Date: 2026-11-14
- Base: `f6a3bf0560df9c3e7594cc835f13864d98c3c6c3` (tree `5e02c63af4544dd489517b056c07ff37e2313704`)
- Candidate: `2988f636ab6c58b1981aac0b93bba31c659a40d9` (tree `1a78911c433fe7e4d3b3025f03a22be2dbc50e25`)
- Scope: the two requested fixture files only; clean detached working tree.

## Commands and results

- `git diff --name-status`: exactly the two fixture files.
- `git diff --check`: passed.
- `jq empty classification.json`: passed.
- Fixture count: 59 cases, 30 EN / 29 DE, 70 expected rows.
- TASK-011 segmentation boundary audit: all expected quotes matched source-order candidate boundaries.
- Synthetic-data scan for secrets/PII-shaped literals: no matches.
- No tests or dependency installation run, per review scope.

## Findings

| ID | Severity | Case / field | Finding |
|---|---|---|---|
| — | — | All cases and fields | No discrepancies found. |

The README conservatively preserves unspecified priority, explicit negation, preferred-heading conflicts, supported ANY/ALL trees, nested conjunctions, threshold uncertainty, and duplicate qualifiers. Unsupported alternatives and mixed conjunctions remain review-required; no OR is split into mandatory requirements. Required coverage, including German-not-required, degree-or-equivalent, Python-or-Java, nested groups, heading conflicts, ambiguity, and duplicates, is present. Fixtures contain synthetic content only.
