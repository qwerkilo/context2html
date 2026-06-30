# context2html — Agent notes

## What this is

Sub-skill augmenting **teach_more_pic**. Both must be loaded via `Skills:` in AGENTS.md. The 29 visual components in `components/` are copied from teach_more_pic — they live locally and can be edited here. Differentiator from teach_more_pic: report (not course) workflow, 20 brand themes, bilingual, humanize-D1-D5 writing rules.

`SKILL.md` is the sole workflow document — follow its 7 steps (input → plan → select → humanize → generate → validate → output) in order. Step 2.5 (humanize) is mandatory and has its own STOP checkpoint before HTML generation.

## Generation rules (hard constraints)

- **Bilingual always** — every content block must have `data-lang="zh"` + `data-lang="en"`. L key toggles.
- **Humanize Chinese prose** — D1-D5 rules in SKILL.md (vary sentence length, rotate paragraph structure, reduce connectors, substitute terms). Read `references/humanize_matrix.md` after writing to apply the 20-row micro-adjustments.
- **One visual component per 500 words minimum** — use `references/decision-guide.md` matrix.
- **Tag group #17 at end of every chapter** — all tags must carry `#` prefix unless user explicitly says otherwise.
- **Theme** — pick from the 20 themes in `references/decision-guide.md`. Set `<html data-theme="xxx">`.

## Commands

```bash
# Unit tests only (pytest, 217 tests across 3 files)
python -m pytest scripts/test_validate_report.py scripts/test_validate_lesson.py scripts/test_generate_theme_css.py -v --tb=short

# Or use the wrapper (Windows PowerShell):
powershell -ExecutionPolicy Bypass -File scripts/run-tests.ps1
# Note: run-tests.ps1 covers report+lesson validator tests only — theme-css tests are NOT included.

# Validate a single report before delivery (17 checks)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from teach_more_pic DESIGN.md
python scripts/generate-theme-css.py

# Local preview server
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1
# macOS/Linux: bash templates/start-server.sh
```

## Validator scripts (17 + 24 checks)

- `scripts/validate-report.py` — **17 checks** for report HTML. Path resolution is relative to the HTML file's directory, NOT project root.
- `scripts/validate-lesson.py` — inherited from teach_more_pic, used for course HTML.
- Newer visual-contract checks added 2026-06: `check_bar_fill_width` (no width > 100%), `check_cmp_table_responsive` (must have `@media max-width: 700px` rule covering `.cmp-table`), `check_cross_refs` (chapter refs must be `#chN` form).

## CodeGraph

Indexed: **15 files (8 Python + 7 JS), 953 nodes, 1794 edges** as of last sync. Use `codegraph_explore` to understand check functions in `scripts/validate-report.py` (faster than reading raw files). `codegraph_search` for symbol lookup.

### Recovery: if MCP returns "database disk image is malformed"

The SQLite db in `.codegraph/` can corrupt after a crashed daemon. Fix:

```bash
# 1. Kill any codegraph node processes still holding the db
Get-Process node | Where-Object { $_.Path -match 'codegraph' } | Stop-Process -Force
# 2. Delete the db files (keep .gitignore + daemon config)
Remove-Item -Force .codegraph\codegraph.db, .codegraph\codegraph.db-shm, .codegraph\codegraph.db-wal
# 3. Rebuild
codegraph init
```

The MCP server caches the old db handle, so `codegraph status` may keep failing until you restart the MCP connection. `codegraph status` from CLI shows the DB is healthy after rebuild — that's the source of truth.

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit. Re-run `generate-theme-css.py` after any teach_more_pic DESIGN.md change. Themes without `--font-h` YAML field fall back to `--font`.
- **Two manual themes** — `spotify` and `tesla` DESIGN.md have no YAML front matter. The generator handles them via hardcoded fallback dict (`MANUAL_THEMES`). If you add another theme without YAML, extend that dict.
- **Manual theme hex format** — `MANUAL_THEMES` entries must be 6-char hex (e.g. `#1ed760`). The generator now uses `hex_to_rgba()` which handles short hex, so 3-char hex won't crash, but stick to 6-char for consistency.
- **Template `<link>` path** — `templates/report-starter.html` uses `<link href="../theme/report-themes.css">`. When copying to a new location, adjust or inline the CSS for standalone distribution.
- **Copy `libs/` alongside reports** — ECharts/Three.js/D3 offline packages must exist at the report's runtime location. The validator checks both local `libs/<lib>.min.js` AND `<script src="libs/...">` path resolution against base_dir.
- **Validator path resolution** — `validate-report.py` resolves `libs/` and SVG paths relative to the report HTML's own directory. External `<script src="...">` paths in the report must exist there.
- **No opencode.json** — skill is loaded via OpenCode's `Skills:` mechanism, not CLI config.
- **`results.tsv` and `test-prompts.json`** — update after darwin-skill optimization or generation workflow changes.
- **File-sync conflict files** (`*Conflicted copy*`) can appear in `references/`, `scripts/` from Windows sync clients — covered by `.gitignore`, safe to delete.
- **`start-server.sh` is macOS/Linux only** — on Windows use `templates/start-server.ps1`. The `.sh` file is kept for cross-platform contributors.
- **Report-themes.html is NOT a valid report** — `examples/report-themes.html` is the theme picker page and will fail `validate-report.py`. Use `examples/0001-demo-report.html` for the smoke test.

## Test artifacts

- `examples/0001-demo-report.html` — full report skeleton, passes `validate-report.py`. Use as smoke test.
- `examples/report-themes.html` — 20-theme preview page. Press T to cycle themes. NOT a validatable report.
- `references/humanize_matrix.md` — 20-row D1-D5 change matrix. Read after writing each chapter.
- `test-prompts.json` — 3 typical scenarios (long, file-based, compact) for manual generation testing.
- `results.tsv` — darwin-skill optimization history.