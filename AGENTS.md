# context2html — Agent notes

Pure HTML/CSS/JS at runtime: no bundler, no build step, no server. Reports open from `file://`.

A **skill repo** that augments `teach_more_pic`: 31 visual components, 20 themes, one report workflow. `SKILL.md` holds the workflow and the Framework API; `README.md` is for humans.

## Commands

```bash
python -m pytest scripts/ -q                 # all tests; the run prints its own count
ruff check .                                 # CI gates on this
python scripts/check-js-parity.py            # parity gate (needs node)
python scripts/mutation-smoke.py             # fails if a mutant survives; -k <area> scopes, --list shows
python scripts/validate-report.py <report>   # 23 hard checks + 5 humanization warnings
python scripts/sync-component-index.py --check   # generated component table is fresh
python scripts/sync-check-table.py --check   # generated checklist matches the validator
python scripts/generate-theme-css.py         # DESIGN.md -> report-themes.css
python scripts/sync-template-styles.py       # base-styles.css -> both templates
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1   # Windows preview
```

CI (`.github/workflows/ci.yml`) gates on three jobs for push/PR to `main`: **test** (Python 3.12–3.14, coverage floor 90, parity, demo report, generated artifacts in sync), **lint**, **mutation-smoke** (plus `git diff --exit-code` proving sources were restored).

## Where things live

`context2html/` is the programmatic surface; `runtime/` is its browser twin.

| Module | Owns |
|---|---|
| `registry.py` | `components/*.md` front matter → `ComponentMeta`; `list_components(content_model=True)` is the 14 swappable components |
| `renderer.py` | `assemble(template, components, theme, slots=None, editable=False)` — zone insertion, CSS merge, library injection |
| `content_model.py` | The normalized model (title, subtitle, items, series) and its validation |
| `slots.py` | Slot markup + sidecar JSON block; the 6 chart-family renderers |
| `structure.py` | The 8 structure-family renderers |
| `editor.py` | Inlines the editor runtime, sets `data-editable="true"` |
| `validator/` | The 23 checks and 5 warnings; `run_all()` is the entry point |
| `runtime/slots.js` | Browser twin of `slots.py` + `structure.py` |
| `runtime/editor-core.js` | Pure editor logic (candidates, preview, undo) — testable under node |
| `runtime/editor.js` | DOM wiring |

## Traps

- **Parity** — `slots.py` and `structure.py` each have a browser twin. Change one, change both, regenerate that component's fixture pair in `scripts/fixtures/golden/`, then run `check-js-parity.py`: it compares Python↔node and both against the golden. The two families escape `'` differently (`&#39;` vs `&#x27;`) by design — ADR 0003 says why.
- **Baseline** — `scripts/fixtures/renderer-baseline-report-starter.html` pins `assemble()` output. Regenerate it in the same commit as a deliberate output change; an unexplained diff there means output moved.
- **Theme CSS** — edit `theme/*/DESIGN.md`, then `generate-theme-css.py`; `theme/report-themes.css` is regenerated from it.
- **Manual themes** — `spotify` and `tesla` have no YAML front matter; edit the `MANUAL_THEMES` dict, a local variable inside `main()` in `generate-theme-css.py`.
- **Template CSS** — edit `templates/base-styles.css`, then `sync-template-styles.py`; the `<style>` blocks inside both HTML templates are generated from it.
- **Slots are opt-in** — `slots=None` is the default. Pass `(component_id, model)` entries to emit `data-slot`/`data-component` markup plus its JSON block; only the 14 `content_model: true` components qualify, and each slot needs exactly one block (the 23rd check).
- **`editable=True` costs ~150 KB** (93 KB of inlined runtime, CSS for all 14, ECharts preloaded) against ~52 KB for a plain report. Default off for that reason.
- **`__loadLib()` returns a Promise** — CDN first, local `libs/` fallback; the editor awaits it before rendering a swapped chart. Slot libraries at generation time load synchronously instead, so the inline init script can find them.
- **`var(--accent)` is invisible to Canvas** — ECharts options need the `gv()` helper (`getComputedStyle(...).getPropertyValue(n)`).
- **Validator paths resolve against the report's own directory**, not the repo root.
- **Components are `.md` files** — copy the fenced `html`/`css`/`js` blocks, not the surrounding prose.
- **`examples/0001-demo-report.html` is the smoke fixture**; `examples/report-themes.html` is a theme gallery and fails validation.
- **`ComponentRegistry.get_component()` is gone** — `list_components(id=26)` returns a list, empty when missing.
- **mutmut needs WSL** — `scripts/mutation-smoke.py` is the native stand-in. Entries live in `scripts/mutants/<area>.py`, one module per area so parallel work never appends to the same list; add one when you fix a bug a test should have caught.
- **Most tests import the package directly**; tests for standalone scripts load them with `importlib.util`.

## Domain docs

`GLOSSARY.md` is the vocabulary — use it in identifiers and docs; `scripts/test_glossary_consistency.py` fails when a word is both defined and listed as one to avoid. Hard-to-reverse decisions live in `docs/adr/` (read ADR 0003 before touching escaping). Feature plans live in `docs/specs/`. Those two are the only tracked paths under `docs/`.
