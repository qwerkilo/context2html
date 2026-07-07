# Quality Guidelines

> HTML/CSS/JS coding standards for context2html output pages.

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| `var(--accent)` inside ECharts `script` block | Canvas2D ignores CSS vars — use `gv('--accent')` |
| Removing `overflow-wrap: break-word` or `word-break: break-word` | English text overflows without it |
| Absolute `<a href="/path">` or external `<a href="https://...">` | Must use relative paths for portability |
| More than one `<h1>` overall (one per language pair) | Validator enforces exactly one |
| Raw `<script src="libs/xxx.js">` instead of `__loadLib()` | Breaks CDN-first + local fallback pattern |
| Hand-editing `theme/report-themes.css` | Auto-generated — edit DESIGN.md and regenerate |
| `data-gsap` with invalid mode (only `fade|stagger|parallax|flip|zoom` allowed) | Validator enforces mode whitelist |
| `.bar-fill` width > 100% | Breaks layout |
| Missing `data-lang-btn` or `key==='l'` keyboard handler | Required for bilingual toggle |
| Chapter anchor format other than `#chN` (e.g. `#chapter-one`) | Must use `#chN` for cross-references |

## CSS Variable Naming

`--{purpose}-{modifier}` kebab-case in English:

```
--bg, --text, --accent, --surface, --border, --muted
--font, --font-h, --lh, --body-size, --small-size
--radius, --section-gap
--shadow-sm, --shadow-md, --shadow-lg
--chart-1, --chart-2, --chart-3, --chart-4
--success, --warning, --error
```

All theme variables are defined flat on `[data-theme="..."]` — no nested CSS, no `@apply`, no preprocessor variables.

## Bilingual Requirements

- Every content element needs both `<span data-lang="zh">` and `<span data-lang="en">` versions.
- A `<button data-lang-btn>` must exist for manual toggle.
- Keyboard shortcut `key==='l'` must be handled.
- Language preference persisted in `localStorage` as `'lang'`.

## Theme Requirements

- Theme is set via `data-theme` attribute on `<html>`.
- T-key cycles through available themes.
- Preference persisted in `localStorage` as `'theme'`.
- Theme CSS loaded via `__loadLib('theme/report-themes.css', '../theme/report-themes.css')`.
