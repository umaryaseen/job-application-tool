# Security and privacy design

This document specifies controls to implement. It does not assert the unimplemented application is secure or legally compliant. The source reports' data minimization guidance informs the design; EDPB describes minimization, accuracy, purpose, retention and confidentiality principles. [EDPB guidance](https://www.edpb.europa.eu/sme/learn-the-basics/data-protection-basics_en).

## Assets and trust boundaries

| Asset/input | Classification | Handling |
|---|---|---|
| Code, ADRs, synthetic fixtures | Repository material | Private GitHub initially; reviewed before commit |
| Canonical profile, job snapshots, generated CVs, approvals | Private applicant data | Explicit local data root outside repo, no CI/telemetry |
| Private employment/education evidence | Sensitive supporting material | Store only reference/digest where enough; no identity scans required |
| Passwords, tokens, session cookies, private keys | Secrets | OS credential mechanisms/environment at boundary only; never model input or logs |
| Job posting text | Untrusted data | Bounded UTF-8, never executed or treated as instructions |
| Model response | Untrusted proposal | Schema/provenance checks, human semantic approval, no tools |
| Templates/fonts/dependencies | Executable supply chain | Trusted local assets, version/hash/license review |

Applicants control their own facts. The system can enforce consistency with approved sources; it cannot determine whether an applicant attestation is objectively true. A malicious local user with OS write access can alter files/code; hashes provide integrity detection within the workflow, not tamper-proof hardware security.

## Threats and required controls

| Threat | Control and introducing task |
|---|---|
| Personal data accidentally committed | `.gitignore` exists before any profile; staged path/fixture checks, secret scanner, explicit staging and clean diff review in TASK-001 |
| Private logs/test outputs in CI | Structured error codes without complete values; synthetic-only test inputs/artifacts; no real profile execution on hosted CI |
| Invented claims with legitimate IDs | Exact approved variant/typed field publishing; subject/scope support and current revision validation, TASK-003/004 |
| JD prompt injection | No LLM in early pipeline; later no tool capability, strict proposals, bounded data and mandatory review, TASK-028/031 |
| Template/code injection | Scalar escaping, trusted templates only, no arbitrary Typst/HTML, no remote assets/file includes; TASK-005/006 |
| Renderer accessing local files or network | Controlled asset root, subprocess arguments without shell, constrained paths, deny egress and include behavior; tests before backend adoption |
| Huge or malformed input | Limits, strict UTF-8, bounded recursion/collections/timeouts; no arbitrary document upload parser in MVP |
| Path traversal/symlink escapes | Resolve outputs under configured private root, reject escaping paths/symlinks, use fresh private temp dirs; TASK-001/008 |
| Stale approval / output substitution | Approval of exact manifest/output bytes; rehash on export; revocation check; TASK-008 |
| Lost/inconsistent application history | Atomic snapshots, no overwrite; SQLite transactions/FKs later; backups/restore tests |
| Dependency or model supply-chain compromise | Lock versions, inspect licenses, isolated optional extras, model revision/checksum, no remote code execution for model loading |
| Cloud data disclosure | Disabled by default, explicit user opt-in, minimal selected evidence, contact reinsertion locally; provider-specific policy review |
| Future SSRF/authenticated browser risk | No fetcher/browser session in MVP. Later URL validation, private-network/redirect/DNS rules and isolated credentials require their own task/ADR |

## Storage and privacy policy

`JAE_DATA_DIR` is explicit and normally outside Git, shared folders and public/synchronized directories. Do not promise encryption from ordinary JSON/SQLite. Recommend using the laptop's encrypted disk and user-controlled protected backups; the app does not silently alter OS security settings. Restrict file permissions on platforms that support them and document Windows ACL differences if Windows is added.

Keep no mandatory DOB, birthplace, family status, religion, nationality, photo or street address. Work authorization is optional, exact and applicant-approved; no legal inference. Do not include raw certificates, passport/residence card numbers or browser cookies in the career schema.

Default retention: do not persist raw provider prompts/responses unless needed for an enabled feature's reproducibility and explicitly selected; store the minimal proposal/source bundle privately when that feature is enabled. Temporary renderer files are removed after successful publication and on handled failures. Failed staging directories are identifiable for safe explicit cleanup. Draft/application snapshots remain until the user deletes them; no hidden retention promise or unattended destructive cleanup. TASK-033 provides export and selective deletion including caches and tracker links. Backups have separate retention; deletion does not mean secure erasure from SSDs or already-created backups.

Embeddings can reveal career content and are private data, not anonymous caches. Hashes of low-entropy personal fields are not anonymization. Do not use profile text as a filename, shell fragment or log label.

## Model boundary

A coding agent operating on this repository is different from an LLM used by the finished application. Neither is authorized to ingest private applicant documents merely because the code repository is available.

The eventual app provider gets only the approved selected professional fact slice and bounded JD text necessary for its task, with name/contact/identity information omitted. Redaction reduces disclosure; professional history may still identify the person. Show that trade-off when enabling cloud use. Provider retention/training/location claims must be checked for the actual chosen service/account at that time; do not claim “no training” generically.

No credentials, browser/filesystem tools, system prompts with secrets, or model-controlled URLs. Do not log private reasoning traces. Audit records contain IDs, version hashes, selections and short rationale codes. Invalid responses fail closed or remain proposals; deterministic generation remains available.

## GitHub and CI

Create `job-application-engine` as PRIVATE. Verify actual privacy and origin after creation, not just the requested flag. Before first push inspect all tracked files, history and staged changes; `.gitignore` cannot remove previously committed material. If a secret is found, stop publication, remove it safely, rotate it through the owner's credential workflow and document the incident without reproducing the secret. Do not rewrite shared history without explicit authorization.

CI runs sanitized fixtures only with minimal read permissions and pinned actions. Do not use privileged `pull_request_target` workflows for untrusted code, upload private artifacts, or print env/config dumps. Use a mature secret scanner as a development gate, documenting its install/version and false-positive exceptions. Exceptions must not permit real keys.

## Future product expansion

Multi-user hosting, commercial applicant processing, employer-side ranking and authenticated browser automation are new trust boundaries. They need fresh security/privacy/legal assessment. This project does not claim a household exemption, GDPR certification, AI Act classification or permission to automate any particular website.

Source policy is separate from generation. Default deny automation, preserve exact application approvals, and request screening declarations directly when facts are missing. Autonomous mass submission remains out of initial scope.
