# context2html — Agent notes

Pure HTML/CSS/JS. No frameworks, no build tools, no package.json. Open directly in browser after generation.

This is a **skill repo** — it augments `teach_more_pic` with a report-generation workflow. 31 visual components in `components/` (29 from teach_more_pic + 2 custom). **SKILL.md is the workflow** (Step 0-5 + Step 2.5 humanize checkpoint).

## Commands

```bash
# All 376 tests
python -m pytest scripts/test_validate_report.py scripts/test_validate_lesson.py scripts/test_generate_theme_css.py -v --tb=short

# Single test file
python -m pytest scripts/test_validate_report.py -v --tb=short

# Validate a report (21 hard checks + 3 humanization warnings)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Preview server (root-relative paths need same cwd)
bash templates/start-server.sh
```

## Hard constraints

- **Vanilla JS** — ES5 IIFE + try/catch. No React/Vue/Svelte/jQuery/Alpine.
- **Bilingual** — every text block needs `data-lang="zh"` + `data-lang="en"`. L key toggles.
- **Template-based** — always copy `templates/report-starter.html` (report type) or `templates/starter.html` (other types). Never write HTML from scratch — lose CSS variable system, toolbar, keyboard nav.
- **Visual density** — ≥1 component per 500 words. `references/decision-guide.md` for selection.
- **ECharts priority** — tabular/comparison data (3+ data points) → ECharts #26 before HTML tables #5/#22.
- **Tag group #17** — required at end of every chapter.
- **Theme** — 20 brand themes via `<html data-theme="xxx">`. Preview: open `examples/report-themes.html`, press T to cycle.
- **5 content types** — `data-content-type` on `<html>`: `report`, `article`, `doc`, `tutorial`, `note`.
- **D1-D5 humanization** — D4: no paragraph-initial "首先/其次/最后/综上所述/值得注意的是". D1: every paragraph must mix ≤10‑char and ≥35‑char sentences. D5: substitute terms every 800 chars. See `references/humanize_matrix.md`.

## MCP usage

### codebase-memory-mcp

Indexed as `storage-emulated-0-Download-opencode` (~5.7K nodes / 19K edges). Skips `libs/`, `node_modules/`, `.git`.

Use `search_graph` to find component names (e.g. `search_graph(query="GSAP 滚动动画")`) and `get_code_snippet` to read their source. The 31 components are indexed as Section nodes in `components/NN-name.md`. For architecture overview, `get_architecture(project="storage-emulated-0-Download-opencode")` shows clusters. `trace_path` works for cross-file JS patterns like `__loadLib` or `gv()` calls.

**Limitation**: `libs/*` min.js files inflate the graph. Filter with `file_pattern` or `label` when searching — or use `rg`/`fd` directly for string patterns in `*.py` / `*.html` files.

### sequential-thinking

Use for: multi-step report structure planning (Step 1 → Step 2 → Step 2.5 ordering with human checkpoints), D1-D5 humanization analysis across paragraphs, or debugging complex validator failures where 21 checks interact.

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit. Re-run `generate-theme-css.py` after DESIGN.md changes.
- **Two manual themes** — `spotify` and `tesla` have NO YAML front matter in their DESIGN.md. Edit `MANUAL_THEMES` dict in `generate-theme-css.py` instead. All other 18 themes come from `theme/*/DESIGN.md`.
- **CDN-first + local fallback** — template has `__loadLib()` that tries jsDelivr CDN first, falls back to local `libs/`. Use `<script>__loadLib('libs/echarts.min.js')</script>` instead of raw `<script src>`. Validator checks both CDN presence AND local file existence.
- **`__loadLib` for theme CSS** — use `__loadLib('theme/report-themes.css','../theme/report-themes.css')` in generated reports.
- **Validator path resolution** — paths resolved relative to the report HTML's own directory, NOT project root.
- **Test imports use `importlib`** — tests load modules via `importlib.util.spec_from_file_location`. Tests live in `scripts/` next to modules under test.
- **Components are .md files** — copy the ```html/css/js code blocks, not the whole file.
- **ECharts color in Canvas** — `var(--accent)` does NOT resolve inside ECharts options (Canvas2D ignores CSS var()). Always use the `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`).
- **English text overflows on lang toggle** — English is wider than Chinese. Template has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove.
- **Heatmap Canvas vmin/vmax** — initialize with `vmin=Infinity, vmax=-Infinity` (not the inverse), or get NaN black cells.
- **CSS source of truth** — edit `templates/base-styles.css`, then run `python scripts/sync-template-styles.py` to push changes to both `starter.html` and `report-starter.html`.
- **`docs/` gitignore** — `docs/*` is gitignored except `docs/agents/`. Agent skill configs there are tracked; other docs are not.
- **`examples/report-themes.html` is NOT a valid report** — will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.

## Agent skills

### Issue tracker

GitHub issues via `gh` CLI. External PRs not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default strings: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` at root + `docs/adr/`. See `docs/agents/domain.md`.
