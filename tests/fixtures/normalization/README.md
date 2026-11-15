# TASK-013 synthetic skill-normalization oracle

`aliases.json` holds synthetic EN/DE phrases and surfaces with literal expected
skill mentions. The labels were authored from TASK-013, A21, ADR-005/006/007
and the rules below before the normalizer existed. They are synthetic, not
applicant data; a separate review must approve them independently of output.

## Format

- `scan_cases`: `text` with every expected mention in source order:
  `quote` (literal substring), `concept` (internal concept ID) and `status`
  (`matched`, or `ambiguous` for a context-restricted alias whose concept is
  only a candidate).
- `surface_cases`: one whole `surface` (for example a skill name) with the
  expected `concept` and `status`; `unmatched` keeps the literal surface and
  has no concept.
- `relations`: typed links that must never make two concepts equivalent.

## Rules

1. Only explicit dictionary aliases create mentions. At each position the
   longest alias wins; mentions never overlap. Text outside aliases is not a
   skill mention and is not guessed.
2. Word aliases match case-insensitively at word boundaries: no letter or digit
   immediately before or after. Words inside a multi-word alias may be
   separated by any run of whitespace.
3. Abbreviations that collide with ordinary words or units are case-sensitive:
   C, R, ML, DL, JS, NLP, KI, AWS, GCP, LLM/LLMs and k8s ("ml" or "aws" in
   lowercase is not a mention).
4. Single-letter languages (C, R) match only between: start, whitespace, `(`,
   `,`, `/` before and end, whitespace, `)`, `,`, `/`, `;`, `:` or a final `.`
   after. So "R&D", "C-level", "Objective-C", "C++" and "C#" do not produce C
   or R.
5. Symbolic aliases (C++, C#, .NET, ASP.NET, Node.js, CI/CD) match
   case-insensitively and must not be preceded by a letter, digit or `.` nor
   followed by a letter or digit, so ".NET" inside "ASP.NET" is not separate.
6. Context-restricted aliases ("Spark" without "Apache") yield `ambiguous`
   with a candidate concept, never `matched`.
7. Relations (broader, narrower, related) never create equivalence: PyTorch is
   not deep learning, SageMaker and EC2 are not AWS, Azure DevOps is not
   Azure, ASP.NET is not .NET, deep learning is not machine learning.
8. Polarity and context come from the caller (for example a negated
   requirement); normalization never asserts that anyone possesses a skill.
9. Language mentions use explicit EN/DE forms, including the listed
   inflections (Deutschkenntnisse, maschinellem Lernen). No form is inferred.

The corpus proves these examples only, not general taxonomy coverage.
