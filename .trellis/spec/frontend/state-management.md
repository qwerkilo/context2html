# State Management

**N/A** — No state management library (no Redux, Zustand, Pinia, Vuex, React Query).

State is handled via `localStorage`:

```javascript
// Theme preference
localStorage.getItem('theme') || 'warm'
localStorage.setItem('theme', newTheme)

// Language preference
localStorage.getItem('lang') || 'zh'
localStorage.setItem('lang', newLang)
```

That's the extent of state management in this project.
