# PRD: 清理冲突文件和 Git 同步

## 目标

清理 OneDrive 同步残留的冲突副本文件，并将本地分支与 `origin/main` 同步。

## 背景

- `scripts/` 目录下有 `(Conflicted copy from DESKTOP-480AVGM on 2026-07-06).*` 文件（.py, .md 等），源自 OneDrive 同步冲突
- 本地 `main` 落后 `origin/main` 20 commits
- Trellis 系统文件（`.opencode/`, `.trellis/`）尚未跟踪

## 验收标准

1. `scripts/` 目录下所有 `(Conflicted copy*)` 文件被删除
2. `__pycache__/` 中的冲突残留被清除
3. `.gitignore` 已添加 `*Conflicted copy*` 模式（如有遗漏补充）
4. `git pull --rebase origin main` 成功，本地与远程同步
5. 变更已提交到本地 `main`
