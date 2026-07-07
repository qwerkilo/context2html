# Component Guidelines

> How visual components are structured and used.

## Component File Format

Every component lives in `components/NN-name.md` with YAML front matter and three fenced code blocks:

```markdown
---
id: 4
name: CSS 条形图
dependencies: []
compat_types:
- report
- article
- doc
requires_3d: false
---

### N. Component Title

> **🎯 效果**: Description of what the component does.

Guidance text / usage instructions...

### CSS

```css
/* Component CSS using var(--xxx) — copy into template <style> */
```

### HTML

```html
<!-- Component HTML — copy into template body -->
```

### JS (optional)

```html
<script>
// Component JS — copy into template <script>
</script>
```
```

## Template Insertion

- Components are COPIED (not imported) — paste HTML/CSS/JS into the starter template.
- Template has `<!-- INSERT: ... -->` comments marking insertion zones.
- CSS goes in `<style>` section, HTML in `<body>`, JS in the final `<script>` block.

## CSS Conventions

- All colors reference theme variables: `var(--accent)`, `var(--surface)`, `var(--text)`.
- Component class names use prefixed naming: `.rc-card`, `.tl-item`, `.bar-fill`, `.heatmap-cell`.
- Semantic class structure: modifier classes use `--` suffix, e.g. `.rc-card--highlight`.
- Layout uses CSS Grid or Flexbox — no table-based layouts except `.cmp-table` for data comparison.

## JS Conventions

- Vanilla JS only (ES5-compatible syntax).
- Library loading via `__loadLib()` — never raw `<script src>`.
- ECharts: use `echarts.init(el).setOption({...})` with `gv('--color')` for theme colors.
- GSAP: use `data-gsap` attribute with valid modes: `fade|stagger|parallax|flip|zoom`.
- data-anim: valid values are `fade-up|fade|slide-left|blur`.
- No JavaScript modules, no imports, no bundling.
