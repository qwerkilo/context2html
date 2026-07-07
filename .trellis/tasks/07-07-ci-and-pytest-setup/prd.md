# PRD: CI 和 pytest 配置

## 目标

为项目添加 GitHub Actions CI，优化 pytest 配置。

## 背景

- 已有 `pyproject.toml` 含基础 pytest 配置（testpaths, python_files）
- 无 `.github/workflows/`，无任何 CI 自动化
- 测试依赖 conftest.py 自动添加项目根到 sys.path

## 验收标准

1. `.github/workflows/ci.yml` 存在，push/PR 到 main 时触发：
   - checkout + setup Python 3.12
   - pip install -e ".[dev]"
   - 运行 `python -m pytest scripts/ --tb=short --no-header`
2. pyproject.toml 的 `[tool.pytest.ini_options]` 增加：
   - `addopts = "-v --tb=short --no-header"`
3. CI 能通过全部现有测试
