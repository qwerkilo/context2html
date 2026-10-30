"""Component index in references/decision-guide.md must match component front matter."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    'sync_component_index',
    os.path.join(os.path.dirname(__file__), 'sync-component-index.py'))
sci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sci)


def test_block_has_markers():
    block = sci.build_block()
    assert block.startswith(sci.START)
    assert block.endswith(sci.END)


def test_block_covers_all_components():
    block = sci.build_block()
    rows = [l for l in block.split('\n') if l.startswith('| ') and not l.startswith('| #')]
    assert len(rows) == 31, f'expected 31 component rows, got {len(rows)}'
    for n in range(1, 32):
        assert f'| {n} |' in block, f'component {n} missing from index'


def test_guide_is_in_sync():
    with open(sci.GUIDE, 'r', encoding='utf-8') as fh:
        current = fh.read()
    updated = sci.replace_block(current, sci.build_block())
    assert updated == current, (
        'references/decision-guide.md is out of sync with component front matter '
        '— run: python scripts/sync-component-index.py')


def test_replace_block_is_idempotent():
    block = sci.build_block()
    once = sci.replace_block('heading\n\n' + block + '\n', block)
    twice = sci.replace_block(once, block)
    assert once == twice


def test_replace_block_appends_when_absent():
    out = sci.replace_block('# Title\n', 'BLOCK')
    assert 'BLOCK' in out
    assert out.startswith('# Title')


def test_description_strips_pipes():
    body = '> **🎯 效果**：a | b 效果'
    assert '\\|' in sci._description(body)
