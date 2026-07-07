<!-- TRELLIS:START -->
# Trellis Instructions

Pure HTML/CSS/JS. No frameworks, no build tools, no package.json. Open directly in browser after generation.

**Docs hierarchy:** `SKILL.md` (workflow + API) → `AGENTS.md` (this file, quick ref) → `README.md` (human-facing overview).

This is a **skill repo** — it augments `teach_more_pic` with a report-generation workflow. 31 visual components in `components/` (29 from teach_more_pic + 2 custom). **SKILL.md is the workflow** (Step 0-5 + Step 2.5 humanize checkpoint) and the **Framework API reference**.

A Python framework package (`context2html/`) provides programmatic access: `ComponentRegistry`, `TemplateRenderer`, `ThemeProvider`, `markdown_utils`, and `validator`.

## Commands

```bash
# All 453 tests
python -m pytest scripts/ -v --tb=short

# Single test file
python -m pytest scripts/test_validate_report.py -v --tb=short

# Validate a report (21 hard checks + 3 humanization warnings)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from theme/*/DESIGN.md
python scripts/generate-theme-css.py

# Preview server (root-relative paths need same cwd)
bash templates/start-server.sh
```

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
- **Components are .md files** — copy the ```html/css/js code blocks, not the whole file.
- **ECharts color in Canvas** — `var(--accent)` does NOT resolve inside ECharts options (Canvas2D ignores CSS var()). Always use the `gv('--accent')` helper (`function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}`).
- **English text overflows on lang toggle** — English is wider than Chinese. Template has `overflow-wrap: break-word`, `.cmp-table` has `table-layout: fixed` + `word-break: break-word`. Do NOT remove.
- **Heatmap Canvas vmin/vmax** — initialize with `vmin=Infinity, vmax=-Infinity` (not the inverse), or get NaN black cells.
- **CSS source of truth** — edit `templates/base-styles.css`, then run `python scripts/sync-template-styles.py` to push changes to both `starter.html` and `report-starter.html`.
- **`docs/` gitignore** — `docs/*` is gitignored except `docs/agents/`. Agent skill configs there are tracked; other docs are not.
- **`examples/report-themes.html` is NOT a valid report** — will fail `validate-report.py`. Use `examples/0001-demo-report.html` for smoke tests.
- **`ComponentRegistry.get_component()` removed** — use `list_components(id=26)` which returns a list (empty if not found).
- **Validator in framework package** — `from context2html.validator import check_h1_count, check_bilingual, ...` works directly.
- **Framework package tests** — `test_registry.py`, `test_renderer.py`, `test_theme.py` use direct imports (`from context2html.xxx import ...`). Other tests still use `importlib`.

## Agent skills

### Issue tracker

GitHub issues via `gh` CLI. External PRs not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default strings: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` at root + `docs/adr/`. See `docs/agents/domain.md`.

## Trellis project management

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.
