# Logging Guidelines

**N/A** — This project does not use a logging framework. CLI scripts use `print()` to output results and error messages directly to stdout/stderr.

```python
print(f"{FAIL} File not found: {path}")  # Error
print(f"  {PASS} All checks passed")      # Success
```

No log levels, no structured logging, no log files.
