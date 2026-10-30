"""Regenerate the component index table in references/decision-guide.md.

Source of truth: YAML front matter + the `> **🎯 效果**` line of each
components/NN-name.md file. Run after adding, renaming, or re-tagging a
component:

    python scripts/sync-component-index.py          # rewrite the block
    python scripts/sync-component-index.py --check  # exit 1 if out of sync
"""

import glob
import os
import re
import sys

from context2html.markdown_utils import parse_front_matter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPONENTS_DIR = os.path.join(ROOT, 'components')
GUIDE = os.path.join(ROOT, 'references', 'decision-guide.md')

START = '<!-- COMPONENT-INDEX:START -->'
END = '<!-- COMPONENT-INDEX:END -->'

HEADER = (
    '| # | 组件 | 文件 | 适用 content-type | 依赖 | 降级到 | 说明 |\n'
    '|---|---|---|---|---|---|---|'
)


def _description(body):
    """First `> **🎯 效果**：...` line after the heading, else first blockquote."""
    m = re.search(r'^>\s*\*\*🎯\s*效果\*\*\s*[：:]\s*(.+)$', body, re.MULTILINE)
    if not m:
        m = re.search(r'^>\s*(?!\*\*)(.+)$', body, re.MULTILINE)
    if not m:
        return ''
    text = m.group(1).strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('|', '\\|')
    return text


def _cell(value):
    return str(value).replace('|', '\\|').strip()


def build_block():
    """Return the full generated block, markers included."""
    rows = [HEADER]
    files = sorted(glob.glob(os.path.join(COMPONENTS_DIR, '*.md')))
    for path in files:
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        meta, body = parse_front_matter(content)
        if not meta:
            continue
        cid = int(meta['id'])
        name = _cell(meta.get('name', ''))
        fname = 'components/' + os.path.basename(path)
        compat = ', '.join(meta.get('compat_types') or [])
        deps = meta.get('dependencies') or []
        if isinstance(deps, str):
            deps = [deps]
        deps_cell = ', '.join(deps) if deps else '—'
        degrade = str(meta.get('degrade_to', '—'))
        rows.append(
            f'| {cid} | {name} | {fname} | {compat} | {deps_cell} | '
            f'{degrade} | {_description(body)} |'
        )
    return START + '\n' + '\n'.join(rows) + '\n' + END


def replace_block(text, block):
    """Swap the marked block in `text`, or append it if absent."""
    if START in text and END in text:
        pattern = re.compile(
            re.escape(START) + r'.*?' + re.escape(END), re.DOTALL)
        return pattern.sub(lambda _: block, text)
    return text.rstrip('\n') + '\n\n' + block + '\n'


def main(argv):
    check_only = '--check' in argv
    with open(GUIDE, 'r', encoding='utf-8') as fh:
        current = fh.read()

    block = build_block()
    updated = replace_block(current, block)

    if check_only:
        if updated != current:
            print('[FAIL] references/decision-guide.md component index is out of sync '
                  '— run: python scripts/sync-component-index.py')
            return 1
        print('[PASS] Component index in sync')
        return 0

    if updated == current:
        print('[OK] Component index already in sync')
        return 0

    with open(GUIDE, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(updated)
    print(f'[OK] Updated {os.path.relpath(GUIDE, ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
