# context2html — Agent notes

Pure HTML/CSS/JS. No frameworks, no build tools required at runtime. Open generated reports directly in a browser.

**Docs hierarchy:** `SKILL.md` (workflow + API) → `AGENTS.md` (this file, quick ref) → `README.md` (human-facing overview).

This is a **skill repo** — it augments `teach_more_pic` with a report-generation workflow. 31 visual components in `components/` (29 from teach_more_pic + 2 custom). **SKILL.md is the workflow** (Step 0-5 + Step 2.5 humanize checkpoint) and the **Framework API reference**.

A Python framework package (`context2html/`) provides programmatic access: `ComponentRegistry`, `TemplateRenderer`, `ThemeProvider`, `markdown_utils`, and `validator`.

## Commands

```bash
# All 453 tests
python -m pytest scripts/ -v --tb=short

# Single test file
python -m pytest scripts/test_validate_report.py -v --tb=short

# Validate a report (22 hard checks + 5 humanization warnings)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Regenerate the component index table in references/decision-guide.md
python scripts/sync-component-index.py

# Preview server (root-relative paths need same cwd)
bash templates/start-server.sh
```

## MCP usage

### CodeGraph

The repo has a local `.codegraph/` index (~73 source files, ~6K nodes, ~34K edges; Python + JS). Prefer it over grep/glob when locating or understanding code.

- **MCP tool** (when available): `codegraph_explore` — one call returns the relevant symbols' verbatim source plus call paths and blast radius.
- **Shell** (always works): `codegraph explore "<symbols or question>"`, `codegraph node <symbol>`, `codegraph callers|callees|impact <symbol>`, `codegraph status`, `codegraph sync` after edits.

**Limitation**: `libs/*.min.js` (echarts/three/d3/gsap) dominate the graph — filter by path or language when searching. For plain string patterns in `*.py` / `*.html` / `*.md`, `rg` is still faster.

### sequential-thinking

Use for: multi-step report structure planning (Step 1 → Step 2 → Step 2.5 ordering with human checkpoints), D1-D5 humanization analysis across paragraphs, or debugging complex validator failures where 21 checks interact.

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit. Re-run `generate-theme-css.py` after DESIGN.md changes.
- **Two manual themes** — `spotify` and `tesla` have NO YAML front matter in their DESIGN.md. Edit `MANUAL_THEMES` dict in `generate-theme-css.py` instead. All other 18 themes come from `theme/*/DESIGN.md`.
- **CDN-first + local fallback** — template has `__loadLib()` that tries jsDelivr CDN first, falls back to local `libs/`. Use `<script>__loadLib('libs/echarts.min.js')</script>` instead of raw `<script src>`. Validator checks both CDN presence AND local file existence.
- **`__loadLib` for theme CSS** — use `__loadLib('theme/report-themes.css','../theme/report-themes.css')` in generated reports.
- **Validator path resolution** — paths resolved relative to the report HTML's own directory, NOT project root.
- **Components are .md files** — copy the ```html/css/js code blocks, not the whole file.
- **ECharts color in Canvas** — `var(--accent)` does NOT resolve inside ECharts options (Canvas2D ignores CSS var()). Always use the `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`).
- **English text overflows on lang toggle** — English is wider than Chinese. Template has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove.
- **Heatmap Canvas vmin/vmax** — initialize with `vmin=Infinity, vmax=-Infinity` (not the inverse), or get NaN black cells.
- **CSS source of truth** — edit `templates/base-styles.css`, then run `python scripts/sync-template-styles.py` to push changes to both `starter.html` and `report-starter.html`.
- **`docs/` gitignore** — `docs/*` is gitignored. Generated reference docs (`theme-index.md`, ADRs) live on disk but are not committed.
- **`examples/report-themes.html` is NOT a valid report** — will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.
- **`ComponentRegistry.get_component()` removed** — use `list_components(id=26)` which returns a list (empty if not found).
- **Validator in framework package** — `from context2html.validator import check_h1_count, check_bilingual, ...` works directly.
- **Framework package tests** — `test_registry.py`, `test_renderer.py`, `test_theme.py` use direct imports (`from context2html.xxx import ...`). Other tests still use `importlib`.

## Domain docs

Single-context vocabulary lives in `CONTEXT.md` at the repo root. Update it when a core term gains a new meaning.
