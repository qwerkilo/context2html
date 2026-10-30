"""Swapping to a library-backed component: load on demand, fail readably.

#26 is the only swappable component that renders through a third-party
library.  A report whose slots are all structure-family ships no ECharts, so
the editor must fetch the library at swap time and show a readable failure
when it cannot.  The loader is injected, which lets these tests drive the
exact browser path under node.
"""

import json
import os
import re
import shutil
import subprocess

import pytest

from context2html.registry import ComponentRegistry
from context2html.renderer import TemplateRenderer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_RUNNER = os.path.join(ROOT, 'scripts', 'js', 'editor-core-runner.js')
SWAP_RUNNER = os.path.join(ROOT, 'scripts', 'js', 'swap-runner.js')
TEMPLATES_DIR = os.path.join(ROOT, 'templates')

MODEL = {
    'title': '渠道销量',
    'items': [
        {'label': '直营', 'value': 120},
        {'label': '经销', 'value': 80},
    ],
}


def _node():
    executable = os.environ.get('NODE') or shutil.which('node')
    if not executable:
        pytest.skip('node executable not found; install node or set NODE')
    return executable


def call_core(op, *args):
    result = subprocess.run(
        [_node(), CORE_RUNNER],
        input=json.dumps({'op': op, 'args': list(args)}),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def swap(**request):
    result = subprocess.run(
        [_node(), SWAP_RUNNER],
        input=json.dumps(request),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def editable_report_with_structure_slot():
    renderer = TemplateRenderer(templates_dir=TEMPLATES_DIR)
    return renderer.assemble(
        'report-starter', [], 'warm', slots=[(12, MODEL)], editable=True)


def slot_identity(html):
    """Return the first slot's (id, model) from a generated editable report."""
    section = re.search(
        r'<section[^>]*\bdata-slot="([^"]+)"[^>]*\bdata-component="12"', html)
    assert section, 'the report has no structure slot'
    slot_id = section.group(1)
    block = re.search(
        r'<script type="application/json" data-slot="' + re.escape(slot_id)
        + r'">(.*?)</script>', html, re.DOTALL)
    assert block, 'the slot has no data block'
    return slot_id, json.loads(block.group(1))


class TestLibraryCatalog:
    def test_only_the_echarts_component_declares_a_library(self):
        assert call_core('libraryFor', 26) == {
            'name': 'echarts.min.js', 'global': 'echarts'}
        for comp in ComponentRegistry().list_components(content_model=True):
            if comp.id == 26:
                assert 'echarts.min.js' in comp.metadata.dependencies
                continue
            assert not comp.metadata.dependencies, comp.id
            assert call_core('libraryFor', comp.id) is None


class TestSwapLoadsTheLibrary:
    def test_structure_report_loads_echarts_before_rendering_the_chart(self):
        html = editable_report_with_structure_slot()
        assert '<script src="libs/echarts.min.js"></script>' not in html
        assert 'swapSlot' in html
        slot_id, model = slot_identity(html)

        outcome = swap(
            componentId=26,
            model=model,
            slotId=slot_id,
            hasLibrary=False,
            loadLibrary='ok',
        )

        assert outcome['events'] == [
            'hasLibrary:echarts.min.js',
            'loadLibrary:echarts.min.js',
            'render:26',
            'commit',
        ]
        assert outcome['result'] == {
            'status': 'rendered', 'library': 'echarts.min.js'}
        assert 'class="ic-chart"' in outcome['committed']['markup']
        assert 'echarts.init(' in outcome['committed']['markup']
        assert 'data-slot="' + slot_id + '"' in outcome['committed']['markup']

    def test_a_present_library_is_not_loaded_again(self):
        outcome = swap(
            componentId=26,
            model=MODEL,
            slotId='slot-26-demo',
            hasLibrary=True,
            loadLibrary='fail',
        )

        assert outcome['events'] == [
            'hasLibrary:echarts.min.js',
            'render:26',
            'commit',
        ]
        assert outcome['result']['status'] == 'rendered'

    def test_structure_targets_need_no_library_at_all(self):
        outcome = swap(
            componentId=12,
            model=MODEL,
            slotId='slot-12-demo',
            hasLibrary=False,
            loadLibrary='fail',
        )

        assert outcome['events'] == ['render:12', 'commit']
        assert outcome['result'] == {'status': 'rendered', 'library': None}
        assert 'data-grid' in outcome['committed']['markup']


class TestLoadFailure:
    def test_a_failed_load_shows_a_readable_failure_state(self):
        outcome = swap(
            componentId=26,
            model=MODEL,
            slotId='slot-26-demo',
            hasLibrary=False,
            loadLibrary='fail',
        )

        assert outcome['events'] == [
            'hasLibrary:echarts.min.js',
            'loadLibrary:echarts.min.js',
            'commit',
        ]
        assert outcome['result'] == {
            'status': 'failed', 'library': 'echarts.min.js'}

        markup = outcome['committed']['markup']
        assert 'role="alert"' in markup
        assert 'ECharts' in markup
        assert 'data-lang="zh"' in markup
        assert 'data-lang="en"' in markup
        assert 'data-component="26"' in markup
        assert 'data-slot="slot-26-demo"' in markup
        assert 'ic-chart' not in markup
        assert 'echarts.init(' not in markup
