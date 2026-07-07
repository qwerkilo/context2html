# Quality Guidelines

> Python coding standards for context2html.

## Imports

Use absolute imports from the package root:

```python
# GOOD
from context2html.markdown_utils import parse_front_matter
from context2html.validator import check_h1_count, check_bilingual

# ACCEPTABLE (for loose scripts without the package installed)
import importlib.util
spec = importlib.util.spec_from_file_location("vr", "validate-report.py")
vr = importlib.util.module_from_spec(spec)
```

- No relative imports (`from ..validator import ...`)
- Always import through the `validator/__init__.py` barrel, not from sub-modules directly

## Testing

- Class-based organization: `class Test{Feature}:` (camelCase, Test-prefixed)
- Method naming: `test_{scenario}` or `test_{behavior}_{condition}`
- Plain `assert` statements only (no `self.assert*` / unittest style)
- `pytest.raises` for expected exceptions
- `tmp_path` fixture for file I/O tests
- Tests pass raw HTML strings to check functions — no file I/O for most tests

```python
class TestComponentRegistry:
    def test_list_components_returns_all(self):
        result = self.r.list_components()
        assert len(result) >= 1

    def test_unknown_type_returns_empty(self):
        result = self.r.list_components(content_type='invalid')
        assert result == []
```

## Type Hints

Used but not enforced. Dataclass fields are typed. Function return types often omitted.

```python
# Typed
@dataclass
class ValidationResult:
    content_type: str = ''
    all_pass: bool = True

# Untyped (acceptable for simple check functions)
def check_exec_summary(html):
    ...
```

## Docstrings

- Module docstring: required, one-line summary
- Function docstring: present for utils/helpers, optional for self-explanatory check functions
- CLI scripts: module docstring doubles as usage text

```python
def parse_front_matter(text):
    """Parse YAML front matter from markdown text.
    Returns (dict, body) — dict is empty if no front matter found.
    """
```

## Forbidden

- Hardcoded file paths (use `os.path.join(BASE_DIR, ...)` or project root references)
- `sys.exit(0)` on validation failure (use `sys.exit(1)`)
- Bare `except:` without specifying exception type
- Test files outside `scripts/` directory
