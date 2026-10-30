"""Regenerate the validation checklist in references/decision-guide.md.

Source of truth: `build_checks()` in `scripts/validate-report.py`. The Chinese
wording and the remediation advice are hand-written here, keyed by the
validator's own label, so a check that is added, renamed, or deleted without an
entry fails this script instead of silently drifting out of the docs.

    python scripts/sync-check-table.py          # rewrite the blocks
    python scripts/sync-check-table.py --check  # exit 1 if out of sync
"""

import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, 'references', 'decision-guide.md')
VALIDATOR = os.path.join(ROOT, 'scripts', 'validate-report.py')

CHECK_START = '<!-- CHECK-TABLE:START -->'
CHECK_END = '<!-- CHECK-TABLE:END -->'
WARN_START = '<!-- WARNING-TABLE:START -->'
WARN_END = '<!-- WARNING-TABLE:END -->'

STUB = '<!DOCTYPE html><html data-content-type="{ct}"><head></head><body></body></html>'
CONTENT_TYPES = ('report', 'article', 'doc', 'tutorial', 'note')

# label -> (检查项, 失败时处理)
ENTRIES = {
    'SVG files exist & valid': (
        'SVG 文件存在且 XML 合法', '修复 SVG 路径或 XML 语法'),
    'Exactly one <h1>': (
        '`<h1>` 个数 1 或 2（中英双语）', '删除多余 h1 或补全双语'),
    'Relative links only': (
        '所有链接为相对路径', '把 `/absolute/path` 改为相对路径'),
    'SVG text/background contrast': (
        'SVG 文本/背景对比度 ≥ 3:1', '修改 SVG 中的浅色文字颜色'),
    ':focus-visible outline': (
        '`:focus-visible` 样式存在', '在 `<style>` 中添加 focus-visible 样式'),
    'tabular-nums alignment': (
        '`font-variant-numeric: tabular-nums`', '在 body 样式中添加'),
    'Semantic HTML elements': (
        '语义 HTML 元素（article/section/nav）', '将 `<div>` 替换为语义元素'),
    'Library deps (ECharts/Three.js)': (
        '外链库（ECharts/Three/D3）本地文件存在', '确认 `libs/` 目录包含所需文件'),
    'Bilingual (data-lang zh/en + toggle)': (
        '中英双语 `data-lang` 配对 + 切换按钮 + L 键',
        '补全缺少的 data-lang 属性或监听器'),
    'Content type valid': (
        '内容类型 `data-content-type` 有效', '使用 report/article/doc/tutorial/note 之一'),
    'Slot data blocks (1 per component slot)': (
        '每个组件插槽有对应 JSON 数据块',
        '为 `data-slot` 补上同 id 的 `<script type="application/json">`'),
    'theme/report-themes.css referenced': (
        '`theme/report-themes.css` 被引用且文件存在',
        '在 `<head>` 中添加 `<link>` 引用，确认文件复制到目标位置'),
    '.exec-summary section': (
        '`.exec-summary` 存在', '添加关键发现摘要段'),
    '.report-chapter sections (>=1)': (
        '`.report-chapter` 至少一个', '报告必须包含正文章节'),
    '.conclusion-page section': (
        '`.conclusion-page` 存在', '添加结论与建议段'),
    '.report-footer element': (
        '`.report-footer` 存在', '添加脚注区域'),
    'Bar-fill width <= 100%': (
        '`.bar-fill` width 不超过 100%', '检查条形图数据值，修正超过 100% 的设置'),
    'Comparison table responsive (max-width 600-700px)': (
        '`.cmp-table` 在 ≤700px 屏幕下有响应式规则',
        '基础样式已含该规则；手写报告需自行补 `@media (max-width: 700px)`'),
    'English layout (overflow-wrap + table-layout:fixed)': (
        '英文排版（overflow-wrap + table-layout:fixed）',
        '在 body 中加 `overflow-wrap: break-word`；`.cmp-table` 加 `table-layout: fixed`'),
    'ECharts var() not used directly in script': (
        'ECharts 不使用 `var()` 直接设色', "用 `gv('--xxx')` 辅助函数替代 `var(--xxx)`"),
    'Chapter cross-refs use #chN anchors': (
        '章节交叉引用使用 `#chN` 锚点', '把 `href="#chapter-name"` 改为 `#chN`'),
    'GSAP data-gsap mode valid': (
        'GSAP `data-gsap` 模式值有效', '仅允许 fade/stagger/parallax/flip/zoom'),
    'data-anim syntax valid': (
        '`data-anim` 语法有效', '仅允许 fade-up/fade/slide-left/blur'),
    'Article structure (<article> elements)': (
        '文章结构（`<article>` 元素）', '用 `<article>` 包裹正文'),
    'Document structure (TOC <nav> with links)': (
        '文档结构（目录 `<nav>` 含链接）', '添加带锚点链接的 `<nav>` 目录'),
    'Tutorial structure (step indicators)': (
        '教程结构（步骤指示器）', '为步骤添加指示器标记'),
    'Note structure': (
        '笔记结构', '按笔记类型补齐必备区块'),
}

# label -> (维度, 失败时处理)
WARNING_ENTRIES = {
    'D1 — 句长交替 (≤10字短句 + ≥35字长句)': (
        'D1 句长交替', '每段混入 ≤10 字短句 1-2 + ≥35 字长句 1-2'),
    'D2 — 段落结构 (避免同结构相邻/总结句结尾/模板化开头)': (
        'D2 段落结构', '相邻段落换结构，避免每段都以数据开头或总结句收尾'),
    'D3 — 信息密度交替 (避免连续高密/低密段)': (
        'D3 信息密度', '高密段后接过渡段，避免连续三段同一密度'),
    'D4 — 连接词控制 (段落开头禁用 + ≤6/千字)': (
        'D4 连接词控制', '段落开头禁用"首先/其次/值得注意的是"；≤6 个/千字'),
    'D5 — 术语变体 (同术语 ≤1次/800字)': (
        'D5 术语变体', '每 800 字替换同义术语（"重要"→"关键/绕不开/真正"）'),
}


def _validator():
    spec = importlib.util.spec_from_file_location('validate_report', VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _labels_by_type(module):
    """Every check label the validator can emit, across all content types."""
    out = {}
    for ct in CONTENT_TYPES:
        _, checks, warnings = module.build_checks(STUB.format(ct=ct), ROOT)
        out[ct] = ([label for label, _ in checks], [label for label, _ in warnings])
    return out


def _guard(labels_by_type):
    """Fail loudly when the docs and the validator disagree about what exists."""
    every_check = set()
    every_warning = set()
    for checks, warnings in labels_by_type.values():
        every_check.update(checks)
        every_warning.update(warnings)

    problems = []
    for label in sorted(every_check - set(ENTRIES)):
        problems.append(f'validator check has no doc entry: {label!r}')
    for label in sorted(set(ENTRIES) - every_check):
        problems.append(f'doc entry has no validator check: {label!r}')
    for label in sorted(every_warning - set(WARNING_ENTRIES)):
        problems.append(f'validator warning has no doc entry: {label!r}')
    for label in sorted(set(WARNING_ENTRIES) - every_warning):
        problems.append(f'doc warning entry has no validator check: {label!r}')
    if problems:
        raise SystemExit('[FAIL] checklist is out of date with the validator:\n  '
                         + '\n  '.join(problems))


def _cell(text):
    return str(text).replace('|', '\\|').strip()


def build_blocks():
    module = _validator()
    labels = _labels_by_type(module)
    _guard(labels)

    checks, warnings = labels['report']
    rows = ['| # | 检查项 | 失败时处理 |', '|---|--------|-----------|']
    for i, label in enumerate(checks, 1):
        name, fix = ENTRIES[label]
        rows.append(f'| {i} | {_cell(name)} | {_cell(fix)} |')
    check_block = CHECK_START + '\n' + '\n'.join(rows) + '\n' + CHECK_END

    rows = ['| # | 维度 | 失败时处理 |', '|---|------|-----------|']
    for label in warnings:
        name, fix = WARNING_ENTRIES[label]
        rows.append(f'| — | **{_cell(name)}**（warning） | {_cell(fix)} |')
    warn_block = WARN_START + '\n' + '\n'.join(rows) + '\n' + WARN_END

    return check_block, warn_block


def replace_block(text, start, end, block):
    if start in text and end in text:
        pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.DOTALL)
        return pattern.sub(lambda _: block, text)
    return text.rstrip('\n') + '\n\n' + block + '\n'


def main(argv):
    check_only = '--check' in argv
    with open(GUIDE, 'r', encoding='utf-8') as fh:
        current = fh.read()

    check_block, warn_block = build_blocks()
    updated = replace_block(current, CHECK_START, CHECK_END, check_block)
    updated = replace_block(updated, WARN_START, WARN_END, warn_block)

    if check_only:
        if updated != current:
            print('[FAIL] references/decision-guide.md checklist is out of sync '
                  '— run: python scripts/sync-check-table.py')
            return 1
        print('[PASS] Validation checklist in sync')
        return 0

    if updated == current:
        print('[OK] Validation checklist already in sync')
        return 0

    with open(GUIDE, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(updated)
    print(f'[OK] Updated {os.path.relpath(GUIDE, ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
