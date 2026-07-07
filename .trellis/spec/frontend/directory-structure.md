# Directory Structure

> How frontend (HTML/CSS/JS) assets are organized.

## Layout

```
templates/                         # HTML starter files (edit base-styles.css, NOT templates directly)
├── base-styles.css                # CSS source of truth — edit here, then run sync-template-styles.py
├── starter.html                   # Generic template (auto-synced)
└── report-starter.html            # Report template (auto-synced)

components/                        # 31 visual components (Markdown files with code blocks)
├── 01-SVG 流程图.md               # Component CSS + HTML + JS in fenced code blocks
├── 02-角色卡片.md
├── 04-CSS 条形图.md
├── ...
└── 31-SVG.js 动态图表.md

theme/                             # 20 brand themes
├── report-themes.css              # Auto-generated from DESIGN.md files — DO NOT HAND-EDIT
├── theme-index.json               # Auto-generated metadata index
├── theme-index.md                 # Human-readable theme reference
├── {brand-name}/DESIGN.md         # YAML design tokens per brand

libs/                              # Local JS/CDN fallback libraries
├── echarts.min.js, echarts-gl.min.js
├── three.min.js, three.module.js
├── d3.min.js, d3-sankey.min.js
├── gsap.min.js, ScrollTrigger.min.js
├── svg.min.js
└── magicui-effects.css            # 13 CSS-only decorative effects

examples/                          # 35 demo HTML files
├── 0001-demo-report.html          # Smoke test report
├── echarts-demo.html, three-demo.html, d3-demo.html, gsap-demo.html
└── report-themes.html             # Theme preview (T-key toggle)
```

## Key Rules

- No `src/`, `dist/`, `build/` directories — this is a flat no-build project.
- Component source files are `.md` documents, not `.js`/`.vue`/`.tsx`.
- Libraries committed locally for offline use (CDN-first via `__loadLib()`).
- Theme CSS is always auto-generated — DESIGN.md is the source of truth.
- Examples are not production reports — `examples/report-themes.html` will fail the validator.
