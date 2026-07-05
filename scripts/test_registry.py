"""Tests for context2html.registry."""
import os, sys, importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "context2html.registry",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "context2html", "registry.py")
)
reg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reg)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPONENTS_DIR = os.path.join(BASE_DIR, 'components')


class TestComponentRegistry:
    def setup_method(self):
        self.r = reg.ComponentRegistry(COMPONENTS_DIR)

    def test_list_components_returns_all(self):
        all_c = self.r.list_components()
        assert len(all_c) >= 1

    def test_list_components_filters_by_content_type(self):
        doc_c = self.r.list_components(content_type='doc')
        assert len(doc_c) >= 1

    def test_list_components_returns_empty_for_unknown_type(self):
        result = self.r.list_components(content_type='unknown_type')
        assert result == []

    def test_get_component_26_has_correct_metadata(self):
        c = self.r.get_component(26)
        assert c is not None
        assert c.metadata.id == 26
        assert c.metadata.name == 'ECharts 交互式图表集'
        assert 'echarts.min.js' in c.metadata.dependencies
        assert 'report' in c.metadata.compat_types

    def test_get_component_unknown_returns_none(self):
        assert self.r.get_component(999) is None

    def test_get_component_26_has_html(self):
        c = self.r.get_component(26)
        assert len(c.html) > 0

    def test_get_component_26_has_css(self):
        c = self.r.get_component(26)
        assert len(c.css) > 0

    def test_get_component_26_has_js(self):
        c = self.r.get_component(26)
        assert len(c.js) > 0

    def test_resolve_dependencies_single(self):
        deps = self.r.resolve_dependencies([26])
        assert 'echarts.min.js' in deps

    def test_resolve_dependencies_unknown_id(self):
        deps = self.r.resolve_dependencies([999])
        assert deps == []

    def test_resolve_dependencies_deduplicates(self):
        deps = self.r.resolve_dependencies([26, 26])
        assert len(deps) == 1
