# context2html — Agent notes

## How this skill works

**This is a sub-skill augmenting teach_more_pic.** Both must be loaded via `Skills:` in AGENTS.md. The 28 visual components (SVG/ECharts/Three.js/D3) live in teach_more_pic, not here.

SKILL.md is the sole workflow document — follow its 5 steps (input → plan → select → generate → validate → output) in order.

## Generation rules

- **One visual component per 500 words minimum** — use `references/decision-guide.md` to pick.
- **Bilingual always** — every content block must have `data-lang="zh"` + `data-lang="en"`. L key toggles.
- **Humanize Chinese prose** — follow D1-D5 rules in SKILL.md (vary sentence length, rotate paragraph structure, reduce connectors, substitute terms).
- **Tags per chapter end** — tag group #17 at the end of every chapter.
- **Theme** — choose from the 10-row table in `references/decision-guide.md` theme section. Set `<html data-theme="xxx">`.

## Commands

```bash
# Validate report (required before delivery)
python scripts/validate-report.py path/to/report.html

# Regenerate theme CSS from teach_more_pic DESIGN.md
python scripts/generate-theme-css.py

# Local preview server
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1
```

## Gotchas

- **Theme CSS is auto-generated** (`theme/report-themes.css`). Never hand-edit — run `generate-theme-css.py` after DESIGN.md changes in teach_more_pic.
- **Template path adjustment** — `<link href="../theme/report-themes.css">` in `templates/report-starter.html` uses a relative path. Adjust it for the actual report output location, or inline the CSS for standalone distribution.
- **Copy libs/ alongside reports** — ECharts/Three.js/D3.js offline packages in `libs/` must be present at the report's runtime location.
- **Two validators exist** — `validate-report.py` (context2html, 14 checks) vs `validate-lesson.py` (inherited from teach_more_pic, for courses). Use the right one.
- **spotify and tesla** have no YAML front matter in their DESIGN.md files — the generator handles them with hardcoded fallback values.
- **No opencode.json** — the skill is loaded through OpenCode's skill mechanism, not CLI config.
