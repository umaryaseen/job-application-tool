# Restore on the laptop and create private GitHub origin

The planning repository was prepared in a cloud Linux workspace. It was **not created on the applicant's laptop**. That workspace had Git but no `gh` command and no advertised local-laptop bridge. No GitHub authentication was attempted and no GitHub repository exists as a result of this handoff.

The downloadable package contains `job-application-engine.bundle` (complete planning Git history), `repository/` (readable planning files without Git internals), `research-inputs/` (original reports outside Git), and `START_HERE.md`. The bundle is the restoration source; the file copy is convenient for reading.

## 1. Restore history

From the extracted handoff directory, use a **new, nonexisting** target directory:

```bash
jae_bundle_path="$PWD/job-application-engine.bundle"
git clone ./job-application-engine.bundle ../job-application-engine
cd ../job-application-engine
git bundle verify "$jae_bundle_path"
git status --short
git log --oneline --decorate -6
```

Run the commands sequentially and stop on any error. `git bundle verify` requires a repository, so verification runs inside the newly created clone. The clone operation itself validates and imports the self-contained bundle. If the target already exists, inspect it rather than overwrite it. Use a new directory if unrelated. Bundle cloning initially sets origin to the local bundle. Remove that origin **only after confirming it points to this supplied bundle**, then configure GitHub in step 3. Never remove or replace an unrelated Git remote.

Keep the accompanying research folder outside the checkout. Set `JAE_RESEARCH_ROOT` to its actual absolute path, or let Codex resolve it from the handoff. Verify source hashes against `docs/research-manifest.json`. Do not commit copied originals. Git code/plans and private applicant data are distinct stores.

If the bundle cannot be used, copy the `repository/` directory into a new target and initialize Git there (`git init -b main`). Inspect and commit the complete planning tree with a clearly identified local author, then obtain a separate review of that exact initial tree/commit before TASK-001. Initialization alone does not establish a reviewed main branch. This fallback loses the supplied Git review history, so prefer bundle restoration and record any fallback honestly.

## 2. Inspect local tools without modifying unrelated configuration

Record OS, CPU architecture, Python 3.12 availability, Git, uv, and later required renderer/PDF tools. Use native installation appropriate to the actual laptop; no guessed package-manager commands or privileged changes. Read any applicable parent AGENTS.md. Use repository-local Git author configuration only if none exists; never impersonate the user.

TASK-001 creates the executable project, real lockfile and quality commands. Do not run planned `jae` commands before it exists. Keep `JAE_DATA_DIR` explicitly outside the repository for real applicant inputs. No personal data is needed for TASK-001.

After TASK-001 is present, enable its repository-local commit safeguard:

```bash
./scripts/install_hooks.sh
```

The command is idempotent and sets only this checkout's `core.hooksPath` to
`.githooks`; it does not change global Git configuration or overwrite an
existing local hook. If a conflicting local hook path or `.git/hooks/pre-commit`
already exists, it stops and reports the path so it can be integrated manually.

## 3. Private GitHub repository

If `gh` is installed and authenticated, create the private repository under the authenticated personal account unless the user explicitly names an organization. Inspect whether `job-application-engine` already exists and whether an origin is already configured. A failed `gh repo view` could be a network/auth error; do not assume every failure means the name is available.

Use the normal authenticated workflow. Check auth without displaying tokens:

```bash
gh auth status >/dev/null 2>&1
```

If authentication is missing, the applicant completes native `gh auth login --web --git-protocol https` on the laptop. Never request a token in chat or inspect credential stores. If gh is absent, finish the local reviewable work and provide the exact remaining installation/authentication step; do not claim remote creation.

Before pushing, inspect tracked files/history for personal data and secrets. Create without `--push` so privacy can be checked first:

```bash
gh repo create job-application-engine --private --source=. --remote=origin
gh repo view --json nameWithOwner,isPrivate,url
```

Proceed only if the returned repository is the intended account/name and `isPrivate` is true. Inspect origin without exposing credential-bearing URLs. Then:

```bash
git push -u origin main
```

Do not replace an existing public repository, change unrelated repo visibility, overwrite origin, force-push or merge unrelated histories. Resolve an existing-name collision with the user if ownership/intent cannot be established safely. Native auth interaction is the only routine approval pause; prepare all safe local work before it.

The create flags and behavior are documented by [GitHub CLI](https://cli.github.com/manual/gh_repo_create). Verify the installed version supports the command when executing.

## 4. Begin one task

Open the restored checkout in VS Code/Codex and use [CODEX_HANDOFF.md](CODEX_HANDOFF.md). TASK-001 is unstarted. Do not restart planning, implement every backlog item at once, or insert personal facts from chat. Finish one task, commit, and hand it to a separate reviewer.
