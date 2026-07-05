"""Tests for context2html.renderer."""
import os, sys, importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "context2html.renderer",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "context2html", "renderer.py")
)
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


class TestTemplateRenderer:
    def setup_method(self):
        self.r = rd.TemplateRenderer(templates_dir=TEMPLATES_DIR)

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
        assert 'chart-bar' in result

    def test_assemble_unknown_template_raises(self):
        import pytest
        with pytest.raises(ValueError, match="Unknown template"):
            self.r.assemble('nonexistent', [], 'warm')

    def test_assemble_unknown_component_skipped(self):
        result = self.r.assemble('starter', [999], 'warm')
        assert 'data-theme="warm"' in result

    def test_assemble_multiple_same_component(self):
        result = self.r.assemble('starter', [26, 26], 'warm')
        assert result.count('chart-bar') == 2
