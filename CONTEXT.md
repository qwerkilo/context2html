# context2html

Transform research content into bilingual visual HTML reports. A sibling of `teach_more_pic` — same component library, different output format (report vs lesson).

## Language

**可视化报告 (Visual Report)**:
An HTML document generated from research content, using at least 1 visual component per 500 words of body text. Components include ECharts, Three.js, SVG diagrams, GSAP animations, etc. A document with only unstyled text is not a visual report.
_Avoid_: HTML page, article, document

**人类化 (Humanization)**:
Five post-processing dimensions (D1-D5) that detect and reduce AI-writing patterns. All five (D1 sentence-length variety, D2 paragraph structure, D3 information density, D4 connector overuse, D5 term repetition) have automated warning-level checks in `validate-report.py`. Warnings are non-blocking.
_Avoid_: 去AI味, anti-AI, de-AI

**视觉组件 (Visual Component)**:
One of 31 numbered component definitions (01-31) in `components/`. 29 sourced from `teach_more_pic`, 2 custom (GSAP #30, SVG.js #31). Each defines HTML structure, CSS, optional JS, and library dependencies. Components are merged into the report template during Step 3.
_Avoid_: Widget, element, module

**双语 (Bilingual)**:
Every body-text block (`<p>`, `<h1>`, `<h2>`, `<td>`, etc.) must appear twice: once with `data-lang="zh"` and once with `data-lang="en"`. The L key toggles visibility between languages. SVG `<text>` elements and Canvas-rendered chart labels (ECharts `series.name`, Three.js sprite labels) are not covered by the automated bilingual check.
_Avoid_: 中英双语, language switch, i18n

**内容类型 (Content Type)**:
One of five layout profiles: `report`, `article`, `doc`, `tutorial`, `note`. Set via `data-content-type` on `<html>`. Drives CSS layout variables (`--body-max-width`, `--sidebar-display`, `--cover-display`, component density). Default: `report` (backward compatible).
_Avoid_: 页面类型, section type

**验证 (Validation)**:
Running `validate-report.py` performs 21 hard checks (blocking — any failure exits with code 1) and 5 D1-D5 warnings (non-blocking). Hard checks cover SVG validity, HTML structure (h1 count, semantic elements, relative links), CSS rules (bar-fill overflow, English layout overflow-wrap, cmp-table responsive breakpoints), library dependency paths, GSAP `data-gsap` modes, `data-anim` syntax, chapter cross-references (`#chN`), and ECharts Canvas color usage (`gv()` helper).
_Avoid_: 自动检查, quality gate

**技能仓库 (Skill Repo)**:
A project that exists primarily to augment another skill — `context2html` augments `teach_more_pic`, sharing its 29 visual components while adding a report-generation workflow, 20 brand themes, bilingual layout, and D1-D5 humanization. SKILL.md is the workflow document (Step 0-5). Loaded via `Skills:` in the agent's config, never invoked directly.
_Avoid_: Plugin, extension, addon

**CDN优先加载 (CDN-first Loading)**:
All external libraries load from jsDelivr CDN first via `__loadLib()`, falling back to local `libs/` files on failure. The template's `__loadLib` function handles this transparently. Validator checks for both CDN presence and local fallback file existence. Second argument to `__loadLib` sets a custom fallback path (e.g. `'../theme/report-themes.css'` for generated reports).
_Avoid_: 直接 `<script src>`

**模板CSS同步 (Template CSS Sync)**:
`templates/base-styles.css` is the single source of truth for all template CSS. Edit it, then run `python scripts/sync-template-styles.py` to push changes into both `starter.html` and `report-starter.html`. Never edit `<style>` blocks inside the HTML templates directly — they will be overwritten on next sync.
_Avoid_: 直接改 HTML 模板的 style 块

**手动主题 (Manual Themes)**:
Two themes (`spotify`, `tesla`) have no YAML front matter in their `theme/*/DESIGN.md`. Their CSS comes from the `MANUAL_THEMES` dict in `scripts/generate-theme-css.py`. Editing their DESIGN.md has no effect. All other 18 themes are generated from `theme/*/DESIGN.md` YAML front matter.
_Avoid_: 直接编辑 report-themes.css

**降级组件 (Degrade To)**:
A component's ability to fall back to a simpler CSS-only variant when its JS library dependencies cannot be loaded. Declared via `degrade_to` in the component's YAML front matter (e.g., ECharts interactive chart #24 degrades to CSS bar chart #5). The validator checks that degraded components exist and have compatible content types.
_Avoid_: Fallback, fallback component

**组件选择矩阵 (Decision Guide)**:
A reference document at `references/decision-guide.md` that maps content types to recommended visual components via a decision tree and selection matrix. Includes failure modes ("if data points > 10 then prefer ECharts `dataZoom` over raw bars") and anti-patterns. Used in Step 2 of SKILL.md to pick components matching the content's data density and narrative structure.
_Avoid_: Component picker, 选型指南

**子图表 (Sub-chart)**:
A variant chart embedded inside a single component definition. Components #24 (ECharts), #25 (Three.js), #26 (ECharts kit), #28 (D3.js), and #31 (SVG.js) define multiple sub-charts in one ` ```html ` block, extracted together by `extract_code_block(multi=True)`. The validator checks that all sub-charts within a component are present before flagging a missing chart.
_Avoid_: 子变体, sub-variant, child chart
