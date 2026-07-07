# Error Handling

> How Python code handles errors in context2html.

## Patterns

### 1. Validation checks return issue lists

All `check_*` functions return `list[str]` — empty list means pass, non-empty means issues found.

```python
def check_exec_summary(html):
    if not re.search(r'class="[^"]*\bexec-summary\b[^"]*"', html):
        return ["Missing .exec-summary section"]
    return []
```

### 2. Aggregation via dataclass

`validate-report.py` collects all check results into a `ValidationResult` dataclass:

```python
@dataclass
class ValidationResult:
    content_type: str = ''
    checks: list = field(default_factory=list)   # Hard checks
    warnings: list = field(default_factory=list)  # D1-D5 humanization warnings
    all_pass: bool = True                          # False if any hard check fails
```

### 3. ValueError for invalid arguments

Used in the framework package for bad input:

```python
def assemble(self, template_name, components, theme_name='warm'):
    if template_name not in _TEMPLATE_MAP:
        raise ValueError(f"Unknown template: {template_name}")
    if not os.path.exists(tpl_path):
        raise FileNotFoundError(f"Template not found: {tpl_path}")
```

### 4. sys.exit(1) for CLI failures

CLI scripts exit with code 1 on failure, with a human-readable message:

```python
if not os.path.exists(path):
    print(f"{FAIL} File not found: {path}")
    sys.exit(1)
```

## Anti-patterns

- No custom exception classes (ValueError/FileNotFoundError suffice).
- No try/except wrapping for validation — checks return lists instead of raising.
- No logging library — CLI scripts use `print()` to stdout/stderr.
