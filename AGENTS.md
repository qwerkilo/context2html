# context2html — Agent notes

## How this skill works

**This is a sub-skill augmenting teach_more_pic.** Both must be loaded via `Skills:` in AGENTS.md. The 29 visual components (SVG/ECharts/Three.js/D3) are copied from teach_more_pic into `components/` — they live locally and can be edited here.

SKILL.md is the sole workflow document — follow its 6 steps (input → plan → select → humanize → generate → validate → output) in order. The humanize step (Step 2.5) is mandatory and placed before HTML generation. References to validate your choices: `references/decision-guide.md` (component selector matrix + theme picker + CSS variable ref) and `references/page-types.md` (9 page-type templates with component pairing).

## Generation rules

- **One visual component per 500 words minimum** — use `references/decision-guide.md` to pick.
- **Bilingual always** — every content block must have `data-lang="zh"` + `data-lang="en"`. L key toggles.
- **Humanize Chinese prose** — follow D1-D5 rules in SKILL.md (vary sentence length, rotate paragraph structure, reduce connectors, substitute terms). Execution is Step 2.5 with its own STOP checkpoint — not optional.
- **Tags per chapter end** — tag group #17 at the end of every chapter.
- **Theme** — choose from the 10-row table in `references/decision-guide.md` theme section. Set `<html data-theme="xxx">`.

## Commands

```bash
# Full test suite (unit tests + HTML validation)
powershell -ExecutionPolicy Bypass -File scripts/run-tests.ps1

# Validate a single report (required before delivery)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from teach_more_pic DESIGN.md
python scripts/generate-theme-css.py

# Local preview server
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1
```

## Test artifacts

- `test-prompts.json` — 3 typical scenarios (long, file-based, compact). When generating a report manually for testing, pick the scenario that matches.
- `results.tsv` — darwin-skill optimization history (baseline 80.5 → final 88.1, 3 rounds). Read this before re-optimizing.
- `examples/` — demo reports: `0001-demo-report.html` (full skeleton, pass `validate-report.py`) and `report-themes.html` (theme preview, NOT a valid report — don't validate it).
- `references/humanize_matrix.md` — 20-row D1-D5 change matrix. SKILL.md Step 2.5 says "完成后对照此文件微调". Agent should read this file after writing report body and before final validation.

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit — run `generate-theme-css.py` after DESIGN.md changes in teach_more_pic. Missing `--font-h` was a bug now fixed (fallback to `--font`), but verify new themes if they lack heading font vars.
- **Template `<link>` path** — `templates/report-starter.html` uses `<link href="../theme/report-themes.css">`. Adjust for the actual report output location, or inline the CSS for standalone distribution.
- **Copy `libs/` alongside reports** — ECharts/Three.js/D3.js offline packages must be present at the report's runtime location. The validator checks for them.
- **Two validators exist** — `validate-report.py` (context2html, 14 checks) vs `validate-lesson.py` (inherited from teach_more_pic, for courses). Use the right one.
- **Validator path resolution** — `validate-report.py` resolves `libs/` and SVG paths relative to the report HTML's own directory (`os.path.dirname`), not the project root.
- **spotify and tesla** have no YAML front matter in their DESIGN.md files — the generator handles them with hardcoded fallback values.
- **No opencode.json** — the skill is loaded through OpenCode's skill mechanism, not CLI config.
- **`components/` .md files** were ported from teach_more_pic and still use technical/process language, not report prose. They are reference docs for the agent, not content for the report.
- **`results.tsv` and `test-prompts.json`** should be updated after any darwin-skill optimization or generation workflow changes.
