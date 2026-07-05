"""Tests for context2html.registry."""
import os

from context2html.registry import ComponentRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPONENTS_DIR = os.path.join(BASE_DIR, 'components')


class TestComponentRegistry:
    def setup_method(self):
        self.r = ComponentRegistry(COMPONENTS_DIR)

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
        comps = self.r.list_components(id=26)
        assert len(comps) == 1
        c = comps[0]
        assert c.metadata.id == 26
        assert c.metadata.name == 'ECharts 交互式图表集'
        assert 'echarts.min.js' in c.metadata.dependencies
        assert 'report' in c.metadata.compat_types

    def test_get_component_unknown_returns_empty(self):
        assert self.r.list_components(id=999) == []

    def test_get_component_26_has_html(self):
        comps = self.r.list_components(id=26)
        assert len(comps[0].html) > 0

    def test_get_component_26_has_css(self):
        comps = self.r.list_components(id=26)
        assert len(comps[0].css) > 0

    def test_get_component_26_has_js(self):
        comps = self.r.list_components(id=26)
        assert len(comps[0].js) > 0

    def test_resolve_dependencies_single(self):
        deps = self.r.resolve_dependencies([26])
        assert 'echarts.min.js' in deps

    def test_resolve_dependencies_unknown_id(self):
        deps = self.r.resolve_dependencies([999])
        assert deps == []

    def test_resolve_dependencies_deduplicates(self):
        deps = self.r.resolve_dependencies([26, 26])
        assert len(deps) == 1

    def test_list_combined_filters_content_type_and_id(self):
        result = self.r.list_components(content_type='doc', id=26)
        assert len(result) == 1
        assert result[0].metadata.id == 26

    def test_list_combined_filters_no_match(self):
        result = self.r.list_components(content_type='doc', id=999)
        assert result == []

    def test_list_combined_content_type_and_id_both_apply(self):
        # #27 (Three.js) is compatible with doc, #26 (ECharts) is not
        # Make sure content_type filter is not bypassed by id filter
        result = self.r.list_components(content_type='not_a_real_type', id=26)
        assert result == []
