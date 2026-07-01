# context2html — Agent notes

## What this is

Sub-skill augmenting **teach_more_pic**. Both loaded via `Skills:`. 29 visual components in `components/` are local copies from teach_more_pic — editable here. Differentiator: report workflow (not course), 20 brand themes, bilingual, D1-D5 humanization.

**SKILL.md is the workflow document** (Step 0-5 + Step 2.5 humanize sub-step with STOP checkpoint before HTML generation).

## No build system

Pure HTML/CSS/JS. No package.json, no npm. Open directly in browser after generation. `libs/` has offline ECharts/Three.js/D3 packages.

## Commands

```bash
# All tests (pytest, 245 tests across 3 files)
python -m pytest scripts/test_validate_report.py scripts/test_validate_lesson.py scripts/test_generate_theme_css.py -v --tb=short

# Validate a report (17 checks). Paths resolved relative to report HTML directory.
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Preview server
bash templates/start-server.sh          # Linux/macOS
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1   # Windows
```

## Hard constraints

- **Bilingual** — every content block needs `data-lang="zh"` + `data-lang="en"`. L key toggles.
- **Template-based** — always copy `templates/report-starter.html`. Never start from scratch (loses CSS variable system, toolbar, keyboard nav).
- **Visual density** — ≥1 component per 500 words. `references/decision-guide.md` for selection.
- **ECharts priority** — for tabular/comparison data (3+ data points), prefer ECharts #26 over HTML tables #5/#22. The decision tree routes "对比分析 → ECharts #26 ⭐⭐⭐" first.
- **Responsive tables** — components #5 and #22 now include `@media (max-width: 700px)` stacked layout + `data-label` attributes. No need to write responsive CSS from scratch.
- **Tag group #17** — required at end of every chapter.
- **Theme** — pick from 20 themes via `<html data-theme="xxx">`.

## D1-D5 humanization (must read before writing)

Rules in SKILL.md §2.5 + `references/humanize_matrix.md`. Failure modes agents miss:
- D4: paragraph-initial "首先/其次/最后/综上所述/值得注意的是" = auto-fail
- D1: every paragraph must mix ≤10‑char and ≥35‑char sentences
- D5: substitute terms every 800 chars ("增长驱动"→"推力/支撑逻辑")

## codebase-memory-mcp

Indexed: 5,928 nodes, 23,089 edges. Use `search_graph` / `trace_path` / `get_code_snippet` instead of grep/glob for Python scripts and HTML/JS code.

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit. Re-run `generate-theme-css.py` after teach_more_pic DESIGN.md changes.
- **Two manual themes** — `spotify` and `tesla` have no YAML front matter. Handled via `MANUAL_THEMES` dict in generate-theme-css.py.
- **Template `<link>` path** — `report-starter.html` uses `<link href="../theme/report-themes.css">`. Adjust or inline when distributing standalone.
- **Three.js WebGPU first** — component #27 uses `importmap` + `type="module"` for WebGPU, falls back to UMD `libs/three.min.js` for WebGL. Both patterns must be included.
- **Copy `libs/` alongside report** — validator checks both `libs/<lib>.min.js` existence AND `<script src="libs/...">` path resolution.
- **validator path resolution** — `validate-report.py` resolves SVG paths, `<script src>` paths relative to the report HTML's own directory, NOT project root.
- **Test imports** — `test_validate_report.py` uses `importlib` to load `validate-report.py` (non-standard import pattern).
- **Components are .md files** — `components/NN-name.md` contain embedded ```html/css/js code blocks. Copy the blocks, not the whole file.
- **ECharts color in Canvas** — `var(--accent)` in ECharts options does NOT resolve (Canvas2D ignores CSS var()). Always use `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`). Three.js #27 correctly already uses `getComputedStyle`.
- **English text overflows on lang toggle** — English is wider than Chinese; template body has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove these.
- **Bilingual block-level elements** — `[data-lang].active` default is `display: inline`. Overrides exist for h1/h2/p/div/section/article/aside/td/th/cover-badge PLUS pre/blockquote/figure/ul/ol/li. If adding a new block-level element with `data-lang`, add it to the override chain.
- **`examples/report-themes.html` is NOT a valid report** — it's a theme preview page and will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.
- **Git push** — remote uses SSH key `/root/.ssh/id_rsa_teach` (opencode-teach-sync). `~/.ssh/config` already configured for `github.com`.
- `results.tsv` and `test-prompts.json` — update after darwin-skill optimization runs.
