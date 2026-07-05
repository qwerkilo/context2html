# PRD: context2html Framework — Agent-Programmable Content Visualization Engine

**Status:** ready-for-agent
**Labels:** needs-triage

---

## Problem Statement

context2html started as a research-report generator — a linear 5-step workflow (SKILL.md) that agent operators follow to produce bilingual visual HTML reports. Over time it grew 5 content types (report/article/doc/tutorial/note), a generic `starter.html` template, and content-type-aware validation. But the project's architecture still assumes a single workflow path:

- Components are `.md` files that agents must manually parse (find code blocks, extract HTML/CSS/JS)
- Template assembly is a copy-paste process driven by human-readable comments (`<!-- INSERT: 视觉组件 HTML -->`)
- Theme selection requires opening a preview HTML and pressing T to cycle — no programmatic access
- SKILL.md is the only workflow definition; any agent that wants a different flow must either hack around it or write everything from scratch

This means every new content type, every new output format, and every new generation strategy requires editing the same monolithic workflow. Agents cannot reuse context2html's components, validation, themes, or rendering as composable building blocks.

## Solution

Refactor context2html from a single-workflow skill into a **programmable framework** that other skills and agents can import and compose. The framework exposes three core APIs:

1. **Component Registry** — parse and query the 31 visual components by content type, dependencies, and metadata
2. **Template Renderer** — assemble components into templates using `data-zone` markers instead of comment-based copy-paste
3. **Theme Provider** — programmatic access to 20 brand themes with recommendation logic

SKILL.md becomes a two-layer document: a reference workflow recipe on top, and the API reference underneath. Agents can follow the recipe or compose their own flow using the framework APIs.

A Python package (`context2html/`) houses the framework code. Existing `scripts/` entry points import from this package.

## User Stories

1. As an **agent operator** building a new content type (e.g. "newsletter"), I want to query the component registry for components compatible with my content type, so that I don't manually flip through 31 `.md` files.

2. As an **agent operator**, I want to call a renderer with a template name + component list + theme, so that the HTML is assembled without manual copy-paste.

3. As an **agent operator**, I want to resolve all library dependencies for a set of components in one call, so that I know which `libs/` files to include or copy.

4. As a **skill developer**, I want to import `ComponentRegistry` from a Python package, so that my own skill can compose context2html components without forking SKILL.md.

5. As a **skill developer**, I want to call `ThemeProvider.recommend_theme(content_type, topic)` to get a theme suggestion, so that my workflow can automate theme selection.

6. As a **skill developer**, I want to supply custom template zones beyond the defaults, so that my generated HTML has custom insertion points for specialized content.

7. As the **project maintainer**, I want component metadata to live in the component `.md` file as YAML front matter, so that the `.md` remains human-readable and the registry parser stays in sync with what humans see.

8. As an **agent operator** writing a new workflow, I want to skip parts of the 5-step flow without breaking the toolchain, so that I can build quick prototypes using only component selection + rendering.

9. As an **agent operator**, I want the framework to validate my assembled HTML via the same checks that `validate-report.py` runs, so that I don't need to call a separate validation step.

10. As a **project maintainer**, I want existing tests to keep passing during the refactor, so that I can make the change incrementally without a big-bang rewrite.

11. As an **agent operator**, I want `SKILL.md` to still describe a complete end-to-end workflow as before, so that new sessions can start with the familiar 5-step process.

12. As an **agent operator**, I want the theme provider to return core CSS variables (accent, bg, text) for any theme, so that I can use them in component logic without parsing the full theme CSS file.

13. As a **skill developer**, I want to override the default renderer behavior (e.g. custom CSS merging strategy), so that I can adapt the framework to my own HTML structure conventions.

## Implementation Decisions

### Seam architecture

The refactor introduces three new abstractions. They are tested as independent modules first, then wired into the existing entry points.

| Seam | Module | Existing precedent |
|------|--------|-------------------|
| Component Registry | `context2html/registry.py` | `scripts/extract-component.py` (ad-hoc extraction, no metadata) |
| Template Renderer | `context2html/renderer.py` | Template comments `<!-- INSERT: ... -->` + manual assembly in SKILL.md |
| Theme Provider | `context2html/theme.py` | `theme/theme-index.json` (exists but read-only, no query API) |

### Python package structure

```
context2html/
├── __init__.py
├── registry.py        # ComponentRegistry: list, get, resolve_dependencies
├── renderer.py        # TemplateRenderer: assemble(template, components, theme) → str
├── theme.py           # ThemeProvider: list, get, recommend
└── validator/         # Moved from scripts/checks/ + _validate_common.py
    ├── __init__.py
    ├── checks.py
    └── content_type.py
```

`pyproject.toml` already created (uv-managed). The package has zero external runtime dependencies — only `pytest` for development.

### Component metadata (YAML front matter)

Each component `.md` file gains a YAML front matter block:

```yaml
---
id: 26
name: ECharts 交互式图表集
dependencies: [echarts.min.js, echarts-gl.min.js]
compat_types: [report, article, doc, tutorial, note]
degrade_to: "05"    # falls back to comparison table
requires_3d: false
---
```

Backward compatible: the existing body content stays unchanged. Agents that read the `.md` directly still see the same content.

### Template zones (`data-zone` attribute)

Insertion points in templates change from HTML comments to `data-zone` attributes:

```html
<style data-zone="component-css"></style>
<div data-zone="component-html"></div>
<script data-zone="component-js"></script>
```

Both `starter.html` and `report-starter.html` get these attributes. The `sync-template-styles.py` script updates them alongside the CSS sync.

### Theme index extension

`theme/theme-index.json` gets two new optional fields per entry:

```json
{
  "name": "warm",
  "display_name": "暖阳",
  "brand": "default",
  "accent": "#c0392b",
  "bg": "#faf9f7",
  "recommend_for": ["report", "article"],
  "recommend_topics": ["经济", "社会", "教育"]
}
```

`recommend_for` limits which content types the theme suits. `recommend_topics` enables topic-based matching.

### SKILL.md restructure

- Keep Steps 0-5 as a **reference workflow** under a `## Example flow` heading
- Add a `## Framework API` section listing the three modules with usage patterns
- Mark that agents may either follow the example flow or compose their own using the APIs

### No `gh` dependency at runtime

The framework itself does not call `gh` or any issue-tracker CLI. Publishing to the issue tracker remains a separate concern handled by triage skills.

## Testing Decisions

### What makes a good test

- Test the public API of each framework module (what it does, not how)
- Use real components from `components/` for registry tests, not synthetic fixtures — ensures the parser stays in sync with actual file format
- Template renderer tests use small inline HTML strings, not full template files, to keep them fast
- Theme provider tests use `theme/theme-index.json` as-is to catch schema drift

### Modules to test

| Module | Test focus | Prior art |
|--------|-----------|-----------|
| `registry.py` | parse front matter, list by content type, resolve deps | `test_generate_theme_css.py` (parse_front_matter tests) |
| `renderer.py` | zone insertion, component merging, CSS dedup | No direct prior art; pattern from `test_validate_report.py` (HTML string manipulation tests) |
| `theme.py` | list/get/recommend theme | `test_generate_theme_css.py` (theme CSS generation tests) |

### Package tests

New tests live in `scripts/test_*.py` alongside existing tests, using the same `importlib` pattern or direct `from context2html` imports after package install. All existing 376 tests must pass unmodified.

## Out of Scope

- **CLI tool** — this PRD covers agent-facing APIs, not a human-facing command-line tool
- **New visual components** — no new #32-#nn components; only metadata retrofits to existing 31
- **New content types** — the 5 existing types (report/article/doc/tutorial/note) are sufficient; framework enables new types without modifying the framework itself
- **Non-HTML output formats** — PDF, Markdown, etc. are not targets
- **`gh` CLI integration** — publishing to the issue tracker is handled by triage skills, not by this framework
- **Web UI / dashboard** — no browser-based designer

## Further Notes

- The first consumer of this framework should be the SKILL.md reference workflow itself — rewrite Steps 0-5 to call the framework APIs internally, proving the seams work
- Theme recommendation rules can start simple (exact topic match → fall back to content type match → return default) and grow later via additional fields in `theme-index.json`
- Framework API stability is not a concern at this stage — the sole consumer is the agent ecosystem; breaking changes are acceptable if communicated via SKILL.md
- `validator` migration from `scripts/checks/` into the package is optional for this phase — the framework APIs can work without it; it's included in the structure sketch for completeness
