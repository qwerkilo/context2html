"""Tests for context2html.renderer."""
import os

from context2html.renderer import TemplateRenderer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


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
        import pytest
        with pytest.raises(ValueError, match="Unknown template"):
            self.r.assemble('nonexistent', [], 'warm')

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
