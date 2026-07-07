# Post-grilling cleanup

## Summary

Grilling session identified and fixed 11 optimization points across the context2html project.

## Changes Made

### Dead Code Removal
1. Deleted `scripts/checks/` (3 orphaned files, zero references — leftover from validator framework migration)
2. Deleted `scripts/_validate_common.py` (barrel re-export, flattened into `validate-lesson.py`)
3. Deleted 33 stale component demo files from `examples/` (kept `0001-demo-report.html` + `report-themes.html`)

### Documentation Sync
4. Fixed SKILL.md: `get_component(id)` → `list_components(id=N)` (2 occurrences)
5. Fixed CONTEXT.md + SKILL.md: D2/D3 changed from "需人工 review" to "全部 5 项自动化"
6. Fixed CONTEXT.md: "3 个 D1/D4/D5 警告" → "5 个 D1-D5 警告"
7. Added 3 missing glossary terms to CONTEXT.md (降级组件/组件选择矩阵/子图表)
8. Updated README.md examples count 15+ → 2

### Framework Enhancement
9. Added convenience exports to `context2html/__init__.py` (ComponentRegistry, check_bilingual, etc. — direct import from top-level package)
10. Version bump 0.1.0 → 0.2.0

### Housekeeping
11. Added `.scratch/` to `.gitignore`

### Test Migration
12. Updated `test_checks_content_type.py`: replaced `importlib` loading of old `scripts/checks/` with direct framework-package imports

## Acceptance Criteria
- [x] 453 tests pass
- [x] `from context2html import ComponentRegistry, check_bilingual` works
- [x] No references to deleted modules remain
