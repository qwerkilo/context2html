# Directory Structure

> Backend code organization for context2html.

## Package Layout

```
context2html/                    # Framework package (importable via pip install -e .)
├── __init__.py                  # Package version: 0.1.0
├── registry.py                  # ComponentRegistry — parse/query visual components
├── renderer.py                  # TemplateRenderer — assemble components into HTML
├── markdown_utils.py            # parse_front_matter, extract_code_block, extract_js_from_md
├── theme.py                     # ThemeProvider — 20 brand themes, CSS generation
└── validator/                   # Validation sub-package
    ├── __init__.py              # Barrel re-exports all check_* functions
    ├── common.py                # Shared checks: h1_count, bilingual, lib_deps, semantic HTML
    ├── report.py                # Report checks + D1-D5 humanization
    ├── content_type.py          # detect_content_type, check_content_type_valid
    └── svg.py                   # SVG link/existence/contrast checks

scripts/                         # CLI entry points + all tests
├── validate-report.py           # CLI: validate report HTML (21 checks + 5 humanization warnings)
├── validate-lesson.py           # CLI: validate lesson HTML
├── generate-theme-css.py        # CLI: regenerate theme/report-themes.css from theme/*/DESIGN.md
├── extract-component.py         # CLI: extract HTML/CSS/JS from component .md files
├── sync-template-styles.py      # CLI: sync base-styles.css into templates/starter.html
├── conftest.py                  # Pytest: adds project root to sys.path for all test files
├── checks/                      # Historical duplicate of context2html.validator (legacy)
│   ├── __init__.py, report.py, content_type.py, svg.py
└── test_*.py                    # 453 tests across 12 test files

theme/                           # Brand theme sources
├── report-themes.css            # Auto-generated (DO NOT hand-edit)
├── theme-index.json / theme-index.md
└── {theme_name}/DESIGN.md      # YAML design tokens per brand
```

## Key Rules

- Framework code goes in `context2html/` package. Entry-point scripts go in `scripts/`.
- Tests co-locate with scripts: `scripts/test_*.py` (no separate `tests/` dir).
- The `scripts/checks/` directory mirrors `context2html.validator/` for backward compatibility — new code should go in the framework package, not the duplicate.
- `conftest.py` adds project root to `sys.path` so scripts can `from context2html.xxx import ...`.
- `pyproject.toml` is the single config file (no `setup.py` / `setup.cfg`).
