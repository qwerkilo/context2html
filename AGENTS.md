# context2html — Agent notes

## What this is

Sub-skill augmenting **teach_more_pic**. Both loaded via `Skills:`. 31 visual components in `components/` are local copies from teach_more_pic (#1-29) + 2 custom (#30 GSAP, #31 SVG.js) — editable here. Differentiator: report workflow (not course), 20 brand themes, bilingual, D1-D5 humanization.

**SKILL.md is the workflow document** (Step 0-5 + Step 2.5 humanize sub-step with STOP checkpoint before HTML generation).

## Vanilla JS only

**No JS frameworks.** No React/Vue/Svelte/jQuery/Alpine. Template uses ES5 IIFE + try/catch wrapping for maximum browser compatibility. All app logic is inline `<script>`, no external modules. Pre-downloaded libraries (ECharts, D3, Three.js, GSAP, SVG.js) go in `libs/` loaded via `<script src>` tags. Do NOT introduce build tools, bundlers, or framework runtimes.

## No build system

Pure HTML/CSS/JS. No package.json, no npm. Open directly in browser after generation.

## Commands

```bash
# All tests (276 tests: report 147 + lesson 107 + theme_css 22)
python -m pytest scripts/test_validate_report.py scripts/test_validate_lesson.py scripts/test_generate_theme_css.py -v --tb=short
```bash
# Single test file
python -m pytest scripts/test_validate_report.py -v --tb=short

# Validate a report (21 hard checks + 3 humanization warnings). Paths resolved relative to report HTML directory.
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Preview server (uses same cwd as root; access via localhost)
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1   # Windows
bash templates/start-server.sh                                        # Linux/macOS
```

## Hard constraints

- **Vanilla JS** — no frameworks, no build tools, no bundlers
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

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit. Re-run `generate-theme-css.py` after teach_more_pic DESIGN.md changes.
- **`generate-theme-css.py` speed** — uses `yaml.CSafeLoader` (C extension). Requires `pip install pyyaml` with compiled C extension. Pure-Python fallback is ~2× slower but works.
- **Two manual themes** — `spotify` and `tesla` have NO YAML front matter in their DESIGN.md, so `generate-theme-css.py` falls back to the `MANUAL_THEMES` dict at the top of the script. **Editing their DESIGN.md will have no effect on the generated CSS** — edit `MANUAL_THEMES` instead. All other 18 themes are generated from `theme/*/DESIGN.md` YAML front matter.
- **Template `<link>` path** — `report-starter.html` uses `<link href="../theme/report-themes.css">`. Adjust or inline when distributing standalone.
- **`examples/*.html` paths** — files in `examples/` use `../libs/` not `libs/` for script/style paths. Demo HTMLs opened via `file://` protocol may need inlined external CSS (see `heatmap-demo.html` for the magicui-effects.css inlining pattern).
- **Three.js WebGPU first** — component #27 uses `importmap` + `type="module"` for WebGPU, falls back to UMD `libs/three.min.js` for WebGL. Both patterns must be included.
- **Copy `libs/` alongside report** — validator checks both `libs/<lib>.min.js` existence AND `<script src="libs/...">` path resolution (relative to the report HTML directory, not project root).
- **Validator path resolution** — `validate-report.py` resolves SVG paths, `<script src>` paths relative to the report HTML's own directory, NOT project root.
- **Test imports** — `test_validate_report.py` uses `importlib` to load `validate-report.py` (non-standard import pattern). Tests are in `scripts/` next to the module under test.
- **Components are .md files** — `components/NN-name.md` contain embedded ```html/css/js code blocks. Copy the blocks, not the whole file. Each component now has a standardized structure: `🎯 效果` preview header → HTML → CSS → JS → layout parameter table → usage rules → degradation notes. Simple components (#02-#20) include hover transitions (translateY + shadow) by default.
- **ECharts color in Canvas** — `var(--accent)` in ECharts options does NOT resolve (Canvas2D ignores CSS var()). Always use `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`). Three.js #27 correctly already uses `getComputedStyle`.
- **English text overflows on lang toggle** — English is wider than Chinese; template body has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove these.
- **Bilingual block-level elements** — `[data-lang].active` default is `display: inline`. Overrides exist for h1/h2/p/div/section/article/aside/td/th/cover-badge PLUS pre/blockquote/figure/ul/ol/li. If adding a new block-level element with `data-lang`, add it to the override chain.
- **`examples/report-themes.html` is NOT a valid report** — it's a theme preview page and will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.
- **`docs/` is gitignored** — `.gitignore` excludes `docs/`. Agent skill config files there won't be tracked.
- **`CONTEXT.md`** exists at root with 5 resolved domain terms (可视化报告/人类化/视觉组件/双语/验证). Read before generating a report.
- **`results.tsv` and `test-prompts.json`** — update after darwin-skill optimization runs.
- **Heatmap Canvas init** — when computing vmin/vmax from a data matrix, start with `vmin=Infinity, vmax=-Infinity` (not `-Infinity, Infinity`). The inverse produces NaN normalize values and black cells.
- **`examples/gsap-demo.html`** uses `../libs/` for GSAP scripts (not `libs/`). CDN fallback creates fresh `<script>` elements rather than mutating the existing one's `src`, which is unreliable across browsers.

## Issue triage

Issues are GitHub issues (create via `gh issue create`). PRs are not a triage surface. Labels: needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix.
