# TASK-013 independent fixture-label review

## Round 1 provenance (recorded by the implementer, not part of the reviewer's text)

- Reviewer: Codex `codex exec` v0.160.0, model `gpt-6.1-terra`, reasoning
  `xhigh`, sandbox `read-only`, detached checkout of fixture commit `bbc31ad`
  (no normalizer code), no network, session `01a1dcec-55ca-77f0-89c6-b2669cdd3d92`.
- The amended contract and cases are in the following commit; the
  implementation review re-checks them. The report below is verbatim.

---

VERDICT: CHANGES REQUIRED

# TASK-013 fixture-label review

- Reviewer: Codex, independent reviewer; labels not authored by reviewer
- Date: 2026-11-15
- Base: `ee590699b49077a1cd61161caa679f104b99b659` (tree `1d7387c7dd2aa5fb11ae63d2d6ee19f9ab9d24f7`)
- Candidate: `bbc31ad936a46cc1d454f68e87ae24b5aa1dabac` (tree `4a90722d00ae0ac4c0426dde966f50ecb53b7d49`)
- Scope: `tests/fixtures/normalization/README.md` and `tests/fixtures/normalization/aliases.json`

## Commands and results

| Command | Result |
|---|---|
| `git diff --name-status base..head` | Exit 0; exactly the two requested files |
| `git diff --check base..head` | Exit 0 |
| `python -m json.tool tests/fixtures/normalization/aliases.json` | Exit 0 |
| Fixture invariant probe | Exit 0; 38 scan, 20 surface, 8 relation cases; quote containment and status invariants passed |
| `ruff check --no-cache .` | Exit 0 |
| `ruff format --check --no-cache .` | Exit 0; 77 files formatted |
| `mypy src` | Exit 0; 47 source files |
| `uv run --offline ...` | Exit 127; `uv` unavailable in this checkout |
| `pytest -q -s` | Exit 2; collection failed because the package is not installed in this detached checkout; no TASK-013 test exists yet |
| Synthetic/PII scan | No personal data, secrets, URLs or applicant-shaped records found |

## Findings

| ID | Severity | Case / field | Expected versus rules |
|---|---|---|---|
| F-01 | blocking | Surface cases `s15`, `s17`, `s18` | Surface matching is unspecified. `s15` (`Python 3`) and `s17` (`Deep Learning — applied object detection`) are labelled unmatched, but Rules 1–2 would find `Python` and `Deep Learning` as bounded aliases if scan semantics applies. `s18` (`  Kubernetes `) is labelled matched, which assumes trimming not stated by the README. Define surfaces as trimmed whole-string alias matches, or revise these labels. |
| F-02 | high | Scan case `de-10` | Expected no mention for `Go-to-market`. If `Go` is an explicit technology alias, Rule 2 treats start/`-` as word boundaries and requires `Go` to match. The alias inventory is absent, so the expected result is underdetermined. Enumerate the reviewed alias set or add a specific compound/context restriction. |
| F-03 | high | Relations `aws-sagemaker→aws`, `aws-ec2→aws`, `aspnet→dotnet`, `azure-pipelines→azure-devops`, `deep-learning→machine-learning`, `machine-learning→artificial-intelligence` | The rows are sensible only if `from` is the narrower concept and `to` is the broader target. The README says relations are non-equivalences but does not define edge direction. A consumer could reverse them and violate the AWS/SageMaker and deep-learning/machine-learning distinctions. Document orientation and prohibit relation traversal as alias equivalence. |
| F-04 | medium | README Rule 2 | “No letter or digit” does not define `_`, combining marks, or other connector characters. Word-boundary behavior can therefore vary by implementation. Specify the Unicode boundary policy before using the fixture as an exact oracle. |

## A21 assessment

The named A21 coverage is present:

- C/C++/C#/R/.NET boundaries: `en-01`–`en-07`, `en-23`, `de-05`, surfaces `s1`–`s8`.
- Word-boundary negatives: `en-03`–`en-06`, `en-17`, `en-23`, surface `s5`.
- EN/DE aliases and inflections: `de-01`–`de-14`, surfaces `s19`–`s20`.
- Abbreviation expansion: JS, ML, NLP, KI, AWS, k8s and LLMs.
- Java versus JavaScript: `en-08`, `en-21`.
- Deep learning versus PyTorch: `en-12`, `de-07`, relation rows.
- AWS versus SageMaker: `en-13`, `en-14`, `de-08`, relation rows.

`DL` and `GCP` are listed in the rules but have no fixture coverage. The corpus is synthetic only. No label asserts possession, and no broad, related or narrower relation is treated as equivalence.
