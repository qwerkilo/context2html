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
Running `validate-report.py` performs 23 hard checks + 5 humanization warnings (hard checks are blocking — any failure exits with code 1; D1-D5 warnings are non-blocking). Hard checks cover SVG validity, HTML structure (h1 count, semantic elements, relative links), CSS rules (bar-fill overflow, English layout overflow-wrap, cmp-table responsive breakpoints), library dependency paths, GSAP `data-gsap` modes, `data-anim` syntax, chapter cross-references (`#chN`), ECharts Canvas color usage (`gv()` helper), and slot/data-block pairing (one JSON block per component slot).
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

**内容模型 (Content Model)**:
The single normalized data shape that every swappable component consumes: `{title, subtitle, items[{label, value, note, accent}], series[{name, values[]}]}`. A component reads the fields it needs and ignores the rest, which is what makes cross-family swapping (chart → card grid → table) possible at all. Components that do not consume a content model (Three.js scenes, PPT-style layouts, decorative SVG) are outside the swappable set.
_Avoid_: Data schema, props, 数据契约

**组件插槽 (Component Slot)**:
One occurrence of a visual component in a finished report, identified by `data-slot` and `data-component`. A slot owns both its rendered markup and its content-model data, so the browser can re-render the same slot as a different component without touching the surrounding text. Swapping is a slot-level operation, never a document-level one.
_Avoid_: Instance, mount point, 占位

**运行时组件库 (Runtime Component Library)**:
The browser-side copy of the swappable components' render functions, inlined into an editable report so a swap needs no server and no network. Distinct from `components/NN.md`, which is the generation-time source the agent reads. Both must render identical markup from identical data, enforced by a golden fixture test.
_Avoid_: Runtime bundle, client library

**槽位输出 (Slot Output)**:
The renderer mode that turns swappable components into component slots: rendered markup plus its JSON data block. Off by default — `TemplateRenderer.assemble(..., slots=None)` produces byte-identical output to a report generated before slots existed. When on, the caller passes `(component_id, model)` entries; the renderer emits each slot, merges that component's CSS/JS and loads its libraries synchronously in `<head>` so the inline init script can run. Only the 14 `content_model: true` components can be slots.
_Avoid_: 可编辑报告, editable report

**编辑模式 (Edit Mode)**:
The browser-side state a reader enters by clicking the 「编辑」 toggle on an editable report. Slots are outlined and clickable, a click opens the candidate list, and a swap re-renders that one slot from its data block. Leaving edit mode restores the read-only appearance exactly. Distinct from 槽位输出: slots are what the generator writes, edit mode is what the reader operates.
_Avoid_: 编辑器, 编辑态

**映射预览 (Mapping Preview)**:
The confirmation shown before a cross-family swap. It lists the content-model fields the target component will display and the fields it will drop, so a reader sees that three series become one card before committing. Same-family swaps skip it because nothing is lost.
_Avoid_: 预览, 差异提示

**微调报告 (Tuned Report)**:
A report the user already adjusted in the browser editor — components swapped, slots re-rendered. It is the source of truth for later work: the agent reads its slots and data blocks and edits incrementally, never regenerates the whole report over it.
_Avoid_: 修改稿, 导出稿, exported report
