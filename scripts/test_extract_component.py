"""Tests for extract-component.py."""
import sys, os, importlib.util, pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "ec", os.path.join(os.path.dirname(__file__), "extract-component.py")
)
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)

COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'components')


class TestExtractComponent:
    def test_list_components(self):
        components = ec.list_components()
        assert len(components) >= 31

    def test_extract_html(self):
        path = os.path.join(COMPONENTS_DIR, '01-SVG 流程图.md')
        result = ec.extract_html(path)
        assert len(result) > 0

    def test_extract_css(self):
        path = os.path.join(COMPONENTS_DIR, '02-角色卡片.md')
        result = ec.extract_css(path)
        assert len(result) > 0

    def test_extract_js(self):
        path = os.path.join(COMPONENTS_DIR, '26-ECharts 交互式图表集.md')
        result = ec.extract_js(path)
        assert len(result) > 0

    def test_extract_nonexistent_mode(self):
        old_argv = sys.argv
        sys.argv = ['extract-component.py', 'INVALID']
        try:
            with pytest.raises(SystemExit) as exc:
                ec.main()
            assert exc.value.code == 1
        finally:
            sys.argv = old_argv

    def test_extract_nonexistent_file(self):
        old_argv = sys.argv
        sys.argv = ['extract-component.py', 'HTML', '/nonexistent/file.md']
        try:
            with pytest.raises(SystemExit) as exc:
                ec.main()
            assert exc.value.code == 1
        finally:
            sys.argv = old_argv
