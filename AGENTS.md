# context2html — Agent notes

## What this is

Sub-skill augmenting **teach_more_pic**. Both loaded via `Skills:`. 30 visual components in `components/` are local copies from teach_more_pic (+ 1 custom, #30 GSAP) — editable here. Differentiator: report workflow (not course), 20 brand themes, bilingual, D1-D5 humanization.

**SKILL.md is the workflow document** (Step 0-5 + Step 2.5 humanize sub-step with STOP checkpoint before HTML generation).

## Vanilla JS only

**No JS frameworks.** No React/Vue/Svelte/jQuery/Alpine. Template uses ES5 IIFE + try/catch wrapping for maximum browser compatibility. All app logic is inline `<script>`, no external modules. Pre-downloaded libraries (ECharts, D3, Three.js, GSAP) go in `libs/` loaded via `<script src>` tags. Do NOT introduce build tools, bundlers, or framework runtimes.

## No build system

Pure HTML/CSS/JS. No package.json, no npm. Open directly in browser after generation.

## Commands

```bash
# All tests (270 tests across 3 files)
python -m pytest scripts/test_validate_report.py scripts/test_validate_lesson.py scripts/test_generate_theme_css.py -v --tb=short

# Or just `pytest` (works directly, no python -m needed when pytest is on PATH)
pytest scripts/test_validate_report.py -v --tb=short

# Validate a report (22 hard checks + 3 humanization warnings). Paths resolved relative to report HTML directory.
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Preview server
bash templates/start-server.sh          # Linux/macOS
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1   # Windows
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
- **Two manual themes** — `spotify` and `tesla` have NO YAML front matter in their DESIGN.md, so `generate-theme-css.py` falls back to the `MANUAL_THEMES` dict at the top of the script. **Editing their DESIGN.md will have no effect on the generated CSS** — edit `MANUAL_THEMES` instead. All other 18 themes are generated from `theme/*/DESIGN.md` YAML front matter.
- **Template `<link>` path** — `report-starter.html` uses `<link href="../theme/report-themes.css">`. Adjust or inline when distributing standalone.
- **Three.js WebGPU first** — component #27 uses `importmap` + `type="module"` for WebGPU, falls back to UMD `libs/three.min.js` for WebGL. Both patterns must be included.
- **Copy `libs/` alongside report** — validator checks both `libs/<lib>.min.js` existence AND `<script src="libs/...">` path resolution.
- **Validator path resolution** — `validate-report.py` resolves SVG paths, `<script src>` paths relative to the report HTML's own directory, NOT project root.
- **Test imports** — `test_validate_report.py` uses `importlib` to load `validate-report.py` (non-standard import pattern).
- **Components are .md files** — `components/NN-name.md` contain embedded ```html/css/js code blocks. Copy the blocks, not the whole file.
- **ECharts color in Canvas** — `var(--accent)` in ECharts options does NOT resolve (Canvas2D ignores CSS var()). Always use `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`). Three.js #27 correctly already uses `getComputedStyle`.
- **English text overflows on lang toggle** — English is wider than Chinese; template body has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove these.
- **Bilingual block-level elements** — `[data-lang].active` default is `display: inline`. Overrides exist for h1/h2/p/div/section/article/aside/td/th/cover-badge PLUS pre/blockquote/figure/ul/ol/li. If adding a new block-level element with `data-lang`, add it to the override chain.
- **`examples/report-themes.html` is NOT a valid report** — it's a theme preview page and will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.
- **Git push** — remote uses SSH key `/root/.ssh/id_rsa_teach` (opencode-teach-sync). `~/.ssh/config` already configured for `github.com`.
- **`docs/` is gitignored** — `.gitignore` excludes `docs/`. Agent skill config files there won't be tracked.
- `results.tsv` and `test-prompts.json` — update after darwin-skill optimization runs.

## Agent skills

### Issue tracker

Issues live as GitHub issues. External PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (one CONTEXT.md + docs/adr/ at root, created lazily). See `docs/agents/domain.md`.
