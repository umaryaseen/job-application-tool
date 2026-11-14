# TASK-005 renderer experiment

This is an isolated experiment. It does not add RenderCV, Typst, Playwright,
Chromium, or pypdf to the baseline runtime. The checked-in lockfile belongs to
this directory only.

```sh
export PATH="$HOME/.local/bin:$PATH"
uv sync --project experiments/renderer --locked
uv run python experiments/renderer/prepare_cases.py
experiments/renderer/.venv/bin/python experiments/renderer/runner/render_experiment.py
```

`prepare_cases.py` runs in the repository environment so it can use the
validated TASK-004 `DocumentPlan` compiler. The renderer runner consumes only
the resulting JSON plans and YAML/HTML adapters. Outputs, PDFs, PNG previews,
logs, and sentinels are written below the ignored repository `artifacts/`
directory. Rendering is attempted offline: the RenderCV process is run in the
macOS `sandbox-exec` network-denied profile when available, and the Playwright
adapter aborts every browser request. No authenticated browser profile or
private path is used.

The current laptop is macOS 13.6.9 x86_64. Playwright 1.62.0 installed, but its
current Chromium installer rejects this OS; the experiment records that result
rather than downloading an unsupported browser.

The runner exits `0` only when all measured engines pass their mandatory
checks, `1` when a measured engine fails, and `2` when the current comparison
is blocked by the unavailable browser. On this macOS 13 laptop, inspect
`artifacts/renderer/task-005/outputs/results.json` after the expected exit `2`:
the RenderCV checks must still be `ok` with complete Poppler and pypdf matches.
Expected contents are checked in independently under
`tests/fixtures/rendering/expected/`; the generated cases never derive the
oracle from extracted output.
