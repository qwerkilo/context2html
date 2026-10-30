# context2html — Agent notes

Pure HTML/CSS/JS at runtime: no framework, no bundler, no build step. Generated reports open from `file://`.

This is a **skill repo** that augments `teach_more_pic`: 31 visual components in `components/`, 20 themes in `theme/`, and a report-generation workflow. `SKILL.md` is the workflow plus the Framework API reference; this file is the quick reference; `README.md` is for humans.

A Python package (`context2html/`) exposes the same machinery programmatically, and a Python + Node toolchain verifies it.

## Commands

```bash
python -m pytest scripts/ -q                 # all tests; the run prints its own count
python -m pytest scripts/test_renderer.py -q # one file
ruff check .                                 # CI gates on this; config in pyproject.toml
python scripts/check-js-parity.py            # Python/JS renderers must agree byte for byte (needs node)
python scripts/mutation-smoke.py             # fails if a mutant survives; -k <area> to scope, --list to show
python scripts/validate-report.py <report>   # 23 hard checks + 5 humanization warnings
python scripts/sync-component-index.py --check  # fails when the generated component table is stale
python scripts/generate-theme-css.py         # theme/*/DESIGN.md -> theme/report-themes.css
python scripts/sync-template-styles.py       # templates/base-styles.css -> both templates
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1   # Windows preview server
```

CI (`.github/workflows/ci.yml`) runs three jobs on push/PR to `main`: **test** (Python 3.12/3.13/3.14, coverage floor 90%, parity, demo report, generated-artifact sync), **lint** (`ruff check .`), **mutation-smoke** (plus a `git diff --exit-code` that proves sources were restored).

## Where things live

| Module | Owns |
|---|---|
| `context2html/registry.py` | Parses `components/*.md` YAML front matter into `ComponentMeta`; `list_components(content_model=True)` selects the 14 swappable ones |
| `context2html/renderer.py` | `TemplateRenderer.assemble(template, components, theme, slots=None, editable=False)` — zone insertion, CSS merge, library injection |
| `context2html/content_model.py` | The normalized model (title, subtitle, items, series) and its validation |
| `context2html/slots.py` | Slot markup + sidecar JSON data block; renderers for the 6 chart-family components |
| `context2html/structure.py` | Renderers for the 8 structure-family components |
| `context2html/editor.py` | Inlines the editor runtime and sets `data-editable="true"` |
| `context2html/validator/` | The 23 checks and 5 warnings; `run_all()` is the single entry point |
| `runtime/slots.js` | Browser-side slot renderers — must match `slots.py`/`structure.py` byte for byte |
| `runtime/editor-core.js` | Pure editor logic (candidates, preview, undo) — testable under node |
| `runtime/editor.js` | DOM wiring only |

## Gotchas

- **Theme CSS is generated.** Never hand-edit `theme/report-themes.css`; edit `theme/*/DESIGN.md` and re-run `generate-theme-css.py`.
- **`spotify` and `tesla` are manual themes.** Their DESIGN.md has no YAML front matter; edit the `MANUAL_THEMES` dict — a local variable inside `main()` in `generate-theme-css.py`, not module scope.
- **`templates/base-styles.css` is the CSS source of truth.** Edit it, then `sync-template-styles.py`. Editing a `<style>` block inside the HTML templates gets overwritten.
- **Two renderers must agree.** Any change to `slots.py` / `structure.py` needs the same change in `runtime/slots.js` and a regenerated fixture pair under `scripts/fixtures/golden/`; `check-js-parity.py` compares Python↔node and both against the golden. The two families escape `'` differently (`&#39;` vs `&#x27;`) on purpose — see ADR 0003.
- **Renderer output is pinned by a committed baseline.** `scripts/fixtures/renderer-baseline-report-starter.html` is regenerated deliberately, never incidentally; a diff there means output changed.
- **Slot output is opt-in.** `slots=None` is the default; pass `(component_id, model)` entries to emit `data-slot`/`data-component` markup plus its JSON data block. Only the 14 `content_model: true` components are accepted, and each slot must have exactly one data block (the 23rd check).
- **`editable=True` is expensive.** It inlines the editor (~93 KB), merges CSS for all 14 swappable components and preloads ECharts: ~150 KB per report versus ~52 KB. It is off by default for that reason.
- **`__loadLib()` returns a Promise.** It tries jsDelivr then the local `libs/` copy; the editor awaits it before rendering a swapped chart. Use it instead of a raw `<script src>` — except for slot libraries at generation time, which load synchronously so the inline init script can find them.
- **`var(--accent)` does not resolve in Canvas.** ECharts options need the `gv()` helper (`getComputedStyle(...).getPropertyValue(n)`).
- **Validator paths resolve against the report's own directory**, not the repo root.
- **Components are `.md` files.** Copy the fenced `html`/`css`/`js` blocks, not the whole document.
- **`examples/report-themes.html` is not a valid report.** Use `examples/0001-demo-report.html` as the smoke fixture.
- **`ComponentRegistry.get_component()` is gone.** Use `list_components(id=26)`, which returns a list (empty when missing).
- **mutmut needs WSL.** `scripts/mutation-smoke.py` is the native stand-in; entries live in `scripts/mutants/<area>.py`, one module per area so parallel work never appends to the same list. Add one when you fix a bug a test should have caught.
- **Most tests import the package directly**; tests for standalone scripts (`validate-report.py`, `check-js-parity.py`, …) load them with `importlib.util`.

## Domain docs

`GLOSSARY.md` holds the vocabulary — use it in code identifiers and docs. A test (`scripts/test_glossary_consistency.py`) fails if a word is both defined and listed as one to avoid. Hard-to-reverse decisions go in `docs/adr/`; feature specs go in `docs/specs/` — those two are the only tracked paths under `docs/`.

The repo has a local `.codegraph/` index (Python + JS) for symbol lookup; run `codegraph status` for size. `libs/*.min.js` dominates it, so filter by path when searching.
