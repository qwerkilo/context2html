# Hook Guidelines

**N/A** — This project uses vanilla JavaScript (ES5-compatible IIFEs). No React, no hooks, no framework.

JS patterns used:
- Immediately-invoked function expressions for scoping
- `window.addEventListener('DOMContentLoaded', ...)` for initialization
- Direct DOM manipulation (`document.querySelector`, `el.addEventListener`)
- `IntersectionObserver` for scroll-triggered animations
- `localStorage` get/set for persistent preferences
