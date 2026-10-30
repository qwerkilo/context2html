"""Editable reports: flag, inlined runtime and non-swappable markers.

These tests drive the public ``TemplateRenderer.assemble`` seam.  The browser
behaviour itself is covered by ``test_editor_core.py`` (pure decisions) plus the
manual acceptance list in the ticket; no browser automation is used.
"""

import importlib.util
import os

from context2html.editor import RUNTIME_FILES, enable_editable, read_runtime
from context2html.renderer import TemplateRenderer
from context2html.slots import render_slot

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
BASELINE = os.path.join(
    BASE_DIR, 'scripts', 'fixtures', 'renderer-baseline-report-starter.html')

_spec = importlib.util.spec_from_file_location(
    'validate_report_for_editor_tests',
    os.path.join(BASE_DIR, 'scripts', 'validate-report.py'))
_vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vr)

MODEL = {
    'title': '渠道销量',
    'items': [
        {'label': '直营', 'value': 120},
        {'label': '经销', 'value': 80},
    ],
}

TIMELINE = {
    'title': '里程碑',
    'items': [
        {'label': '2025 Q1', 'value': 1, 'note': '立项'},
        {'label': '2026 Q3', 'value': 2, 'note': '上线'},
    ],
}


class TestEditableReport:
    def setup_method(self):
        self.r = TemplateRenderer(templates_dir=TEMPLATES_DIR)

    def test_default_report_carries_no_editor_flag_or_runtime(self):
        html = self.r.assemble('report-starter', [26, 17], 'warm')
        assert 'data-editable' not in html
        assert 'SlotRuntime' not in html
        assert 'SlotEditorCore' not in html
        assert 'ic-editor-bar' not in html

    def test_editable_report_sets_the_flag_on_the_root_element(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert 'data-editable="true"' in html
        assert html.index('data-editable="true"') < html.index('<head>')

    def test_editable_report_inlines_all_three_runtime_layers(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert 'SlotRuntime' in html
        assert 'SlotEditorCore' in html
        assert 'ic-editor-bar' in html
        assert 'isEditableFlag' in html

    def test_editor_runtime_is_not_an_external_file(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert 'src="runtime' not in html
        assert "src='runtime" not in html

    def test_runtime_layers_load_in_dependency_order_before_body_close(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        runtime = html.index('SlotRuntime')
        core = html.index('SlotEditorCore')
        bootstrap = html.index('ic-editor-bar')
        assert runtime < core < bootstrap < html.index('</body>')

    def test_editable_report_merges_css_for_every_swappable_component(self):
        html = self.r.assemble(
            'report-starter', [], 'warm', slots=[(3, TIMELINE)], editable=True)
        for component_id in (2, 4, 5, 12, 13, 15, 17, 18, 19, 20, 22, 24, 26):
            css = self.r._reg.list_components(id=component_id)[0].css
            assert css in html, component_id

    def test_editable_report_without_slots_loads_no_chart_library(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert '<script src="libs/echarts.min.js"></script>' not in html

    def test_editable_report_with_an_echarts_slot_loads_the_library(self):
        html = self.r.assemble(
            'report-starter', [], 'warm', slots=[(26, MODEL)], editable=True)
        assert '<script src="libs/echarts.min.js"></script>' in html

    def test_editable_report_with_a_structure_slot_loads_no_chart_library(self):
        html = self.r.assemble(
            'report-starter', [], 'warm', slots=[(12, MODEL)], editable=True)
        assert '<script src="libs/echarts.min.js"></script>' not in html

    def test_non_swappable_components_are_marked_for_the_hint(self):
        html = self.r.assemble('report-starter', [1], 'warm', editable=True)
        comp = self.r._reg.list_components(id=1)[0]
        assert 'data-swap="unavailable"' in html
        assert 'data-component="1"' in html
        assert comp.html in html

    def test_default_report_does_not_mark_non_swappable_components(self):
        html = self.r.assemble('report-starter', [1], 'warm')
        assert 'data-swap="unavailable"' not in html
        assert 'class="ic-static"' not in html

    def test_slot_fragment_is_byte_identical_with_editing_enabled(self):
        html = self.r.assemble(
            'report-starter', [], 'warm', slots=[(26, MODEL)], editable=True)
        assert render_slot(26, MODEL).fragment in html
        assert '<script type="application/json" data-slot=' in html

    def test_editable_report_without_slots_still_ships_the_editor(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert 'data-editable="true"' in html
        assert 'ic-editor-bar' in html

    def test_editable_report_still_passes_all_23_hard_checks(self, tmp_path):
        (tmp_path / 'libs').mkdir()
        (tmp_path / 'libs' / 'echarts.min.js').write_text('', encoding='utf-8')
        (tmp_path / 'theme').mkdir()
        (tmp_path / 'theme' / 'report-themes.css').write_text(
            '/* stub */', encoding='utf-8')

        html = self.r.assemble(
            'report-starter', [], 'warm', slots=[(26, MODEL)], editable=True)

        result = _vr.run_checks(html, str(tmp_path))
        failures = {label: issues for label, issues in result.checks if issues}
        assert failures == {}
        assert len(result.checks) == 23

    def test_editable_false_matches_the_committed_baseline(self):
        with open(BASELINE, 'r', encoding='utf-8') as handle:
            baseline = handle.read()
        assert self.r.assemble(
            'report-starter', [26, 17], 'warm', editable=False) == baseline

    def test_enabling_editing_twice_does_not_duplicate_the_runtime(self):
        html = self.r.assemble('report-starter', [], 'warm', editable=True)
        assert enable_editable(html) == html

    def test_editor_runtime_makes_no_network_requests(self):
        for name in RUNTIME_FILES:
            source = read_runtime(name)
            assert 'fetch(' not in source, name
            assert 'XMLHttpRequest' not in source, name
            assert 'http://' not in source and 'https://' not in source, name
