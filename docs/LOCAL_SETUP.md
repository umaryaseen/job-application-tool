# Local setup

The existing repository is [umaryaseen/job-application-tool](https://github.com/umaryaseen/job-application-tool). If already checked out, inspect branch, working tree and remote first. Preserve local changes and check for unpublished workstation work before bringing in GitHub changes.

For a fresh directory only:

```bash
git clone https://github.com/umaryaseen/job-application-tool.git
cd job-application-tool
uv sync --locked --group dev
./scripts/install_hooks.sh
uv run jae --help
```

Requires Python 3.12 and `uv`. The hook installer changes only this checkout's `core.hooksPath` and preserves conflicting hooks. Do not replace an unrelated remote, reinitialize the project or change global Git settings.

## Private inputs

Select an existing absolute private directory outside the checkout. Preserve existing profiles, evidence, reviews and snapshots.

```bash
export JAE_DATA_DIR=/private/path/to/job-application-data
uv run jae config-check
```

GitHub cannot supply files deliberately kept local. Do not commit personal inputs, application outcomes or generated documents. The current source repository is public; the planning-era private-origin assumption is historical. Routine setup does not create another repository or change visibility.

## Verification

Production PDF rendering/measurement require macOS `sandbox-exec` and Poppler on PATH. ADR-004 records the existing laptop qualification. Cleanup CI targets `macos-15-intel`; the complete CI result remains a separate qualification gate.

Install the transitive public Typst package once with explicit network opt-in:

```bash
export JAE_TYPST_PACKAGE_ROOT="$HOME/Library/Caches/jae/typst-packages"
uv run python scripts/setup_typst_packages.py --destination "$JAE_TYPST_PACKAGE_ROOT" --download
```

This downloads only pinned public dependency files, not applicant information. Every file is checksum-verified again before copying into a renderer stage. Keep the environment variable set for PDF builds. Without `--download`, the setup command verifies local files without network. A missing or changed asset fails the build; there is no global-cache or unisolated fallback.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -ra
```

Install missing host tools through the normal local package manager without disabling renderer isolation. On Linux report unsupported renderer checks accurately; domain tests do not verify PDF rendering. The two simulated subprocess-error tests intentionally do not execute a renderer.

Old bundle-restoration instructions remain in Git history at `3c562fe`; they are unnecessary for a normal clone. Research reports are optional local reference inputs identified in SOURCE_REGISTER. Use `JAE_RESEARCH_ROOT` where present and record missing relevant source material honestly.
