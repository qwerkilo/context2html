"""Tests for context2html.renderer."""
import importlib.util
import os

import pytest

from context2html.renderer import TemplateRenderer
from context2html.slots import SlotError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
BASELINE = os.path.join(
    BASE_DIR, 'scripts', 'fixtures', 'renderer-baseline-report-starter.html')

_spec = importlib.util.spec_from_file_location(
    'validate_report_for_renderer_tests',
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
        {'label': '2026 Q3', 'value': 2, 'note': '上线', 'accent': 'accent'},
    ],
}


class TestTemplateRenderer:
    def setup_method(self):
        self.r = TemplateRenderer(templates_dir=TEMPLATES_DIR)

    def test_assemble_starter_no_components(self):
        result = self.r.assemble('starter', [], 'warm')
        assert 'data-theme="warm"' in result
        assert '<!DOCTYPE html>' in result
        assert '</html>' in result

    def test_assemble_report_starter_theme_override(self):
        result = self.r.assemble('report-starter', [], 'airbnb')
        assert 'data-theme="airbnb"' in result

    def test_assemble_with_component_26(self):
        result = self.r.assemble('starter', [26], 'warm')
        assert 'chart-bar' in result or 'echarts' in result

    def test_assemble_unknown_template_raises(self):
        with pytest.raises(ValueError, match="Unknown template"):
            self.r.assemble('nonexistent', [], 'warm')

    def test_assemble_rejects_theme_name_with_quotes(self):
        with pytest.raises(ValueError, match="Invalid theme name"):
            self.r.assemble('starter', [], 'x" onload="alert(1)')

    def test_assemble_rejects_theme_name_with_angle_bracket(self):
        with pytest.raises(ValueError, match="Invalid theme name"):
            self.r.assemble('starter', [], '<script>')

    def test_assemble_accepts_dotted_theme_name(self):
        result = self.r.assemble('starter', [], 'x.ai')
        assert 'data-theme="x.ai"' in result

    def test_assemble_unknown_component_skipped(self):
        result = self.r.assemble('starter', [999], 'warm')
        assert 'data-theme="warm"' in result

    def test_assemble_multiple_same_component(self):
        result = self.r.assemble('starter', [26, 26], 'warm')
        # Component 26 now includes all sub-charts (26a-26d). Insert twice.
        assert result.count('chart-bar') >= 2

    def test_unknown_components_skipped_silently(self):
        result = self.r.assemble('starter', [999, -1], 'warm')
        assert 'data-theme="warm"' in result

    def test_all_31_components_resolve(self):
        all_ids = list(range(1, 32))
        for cid in all_ids:
            comps = self.r._reg.list_components(id=cid)
            assert len(comps) == 1, f"Component {cid} not found"
            assert comps[0].metadata.name, f"Component {cid} has no name"

    def test_resolve_dependencies_all(self):
        deps = self.r._reg.resolve_dependencies(list(range(1, 32)))
        assert 'echarts.min.js' in deps
        assert 'three.min.js' in deps

    def test_slot_output_off_by_default_matches_committed_baseline(self):
        """Slot output is off unless asked for; the bytes must not move."""
        with open(BASELINE, 'r', encoding='utf-8') as fh:
            assert self.r.assemble('report-starter', [26, 17], 'warm') == fh.read()

    def test_slots_parameter_emits_slot_markup_and_data_block(self):
        result = self.r.assemble('report-starter', [], 'warm', slots=[(26, MODEL)])
        assert 'class="ic-slot"' in result
        assert 'data-component="26"' in result
        assert '<script type="application/json" data-slot=' in result

    def test_slot_components_merge_their_css_and_js_without_demo_markup(self):
        result = self.r.assemble('report-starter', [], 'warm', slots=[(26, MODEL)])
        comp = self.r._reg.list_components(id=26)[0]
        assert comp.css in result
        assert comp.js in result
        assert 'id="chart-bar"' not in result

    def test_slot_components_load_their_library_dependencies_in_the_head(self):
        """The inline slot script needs echarts before the body runs."""
        result = self.r.assemble('report-starter', [], 'warm', slots=[(26, MODEL)])
        tag = '<script src="libs/echarts.min.js"></script>'
        assert tag in result
        assert result.index(tag) < result.index('</head>')

    def test_generated_report_with_slots_passes_all_23_hard_checks(self, tmp_path):
        (tmp_path / 'libs').mkdir()
        (tmp_path / 'libs' / 'echarts.min.js').write_text('', encoding='utf-8')
        (tmp_path / 'theme').mkdir()
        (tmp_path / 'theme' / 'report-themes.css').write_text(
            '/* stub */', encoding='utf-8')

        html = self.r.assemble('report-starter', [5], 'warm', slots=[
            {'component': 26, 'model': MODEL, 'slot_id': 'ev-sales'},
            (3, TIMELINE),
        ])

        result = _vr.run_checks(html, str(tmp_path))
        failures = {label: issues for label, issues in result.checks if issues}
        assert failures == {}
        assert len(result.checks) == 23

    def test_the_17_components_outside_the_swappable_set_are_untouched(self):
        swappable = self.r._reg.list_components(content_model=True)
        others = [
            comp for comp in self.r._reg.list_components()
            if comp.id not in {c.id for c in swappable}
        ]
        assert len(swappable) == 14
        assert len(others) == 17

        for comp in others:
            result = self.r.assemble(
                'report-starter', [comp.id], 'warm', slots=[(26, MODEL)])
            assert comp.html in result, comp.id
            assert comp.css in result, comp.id
            if comp.js:
                assert comp.js in result, comp.id

    def test_explicit_slot_id_reaches_markup_and_data_block(self):
        result = self.r.assemble(
            'report-starter', [], 'warm', slots=[(26, MODEL, 'ev-sales')])
        assert 'data-slot="ev-sales"' in result
        assert '<script type="application/json" data-slot="ev-sales">' in result

    def test_slot_mapping_form_is_accepted(self):
        result = self.r.assemble(
            'report-starter', [], 'warm',
            slots=[{'component': 3, 'model': TIMELINE}])
        assert 'data-component="3"' in result
        assert '<script type="application/json" data-slot=' in result

    def test_duplicate_slot_ids_are_rejected(self):
        with pytest.raises(ValueError, match='duplicate slot id'):
            self.r.assemble(
                'report-starter', [], 'warm',
                slots=[(26, MODEL, 'same'), (3, TIMELINE, 'same')])

    def test_non_swappable_component_in_slots_is_rejected(self):
        with pytest.raises(SlotError):
            self.r.assemble('report-starter', [], 'warm', slots=[(1, MODEL)])

    def test_malformed_slot_spec_is_rejected(self):
        with pytest.raises(ValueError, match='each slot'):
            self.r.assemble('report-starter', [], 'warm', slots=['nope'])

    def test_empty_slots_list_also_matches_the_baseline(self):
        with open(BASELINE, 'r', encoding='utf-8') as fh:
            assert self.r.assemble(
                'report-starter', [26, 17], 'warm', slots=[]) == fh.read()
