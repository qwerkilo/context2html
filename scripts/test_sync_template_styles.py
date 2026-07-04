"""Tests for sync-template-styles.py."""
import sys, os, re, importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "sts", os.path.join(os.path.dirname(__file__), "sync-template-styles.py")
)
sts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sts)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS_PATH = os.path.join(BASE_DIR, 'templates', 'base-styles.css')
STARTER_PATH = os.path.join(BASE_DIR, 'templates', 'starter.html')
REPORT_STARTER_PATH = os.path.join(BASE_DIR, 'templates', 'report-starter.html')


def _get_style_inner(html):
    """Extract inner content of <style> tag."""
    m = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    return m.group(1) if m else ''


def _get_css_without_header(html):
    """Get CSS content past sync comment headers."""
    inner = _get_style_inner(html)
    idx = inner.find('/* ================================================================ */')
    if idx >= 0:
        return inner[idx:].strip()
    return inner.strip()


class TestSyncTemplateStyles:
    def test_css_extracted(self):
        assert os.path.exists(CSS_PATH)
        with open(CSS_PATH, 'r', encoding='utf-8') as f:
            css = f.read()
        assert len(css) > 1000

    def test_starter_contains_css(self):
        with open(STARTER_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
        inline_css = _get_css_without_header(html)
        with open(CSS_PATH, 'r', encoding='utf-8') as f:
            base_css = f.read().strip()
        assert inline_css == base_css

    def test_report_starter_contains_css(self):
        with open(REPORT_STARTER_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
        inline_css = _get_css_without_header(html)
        with open(CSS_PATH, 'r', encoding='utf-8') as f:
            base_css = f.read().strip()
        assert inline_css == base_css

    def test_sync_idempotent(self):
        with open(STARTER_PATH, 'r', encoding='utf-8') as f:
            before = f.read()
        sts.main()
        with open(STARTER_PATH, 'r', encoding='utf-8') as f:
            after = f.read()
        assert before == after

    def test_both_templates_same_css(self):
        with open(STARTER_PATH, 'r', encoding='utf-8') as f:
            starter_css = _get_css_without_header(f.read())
        with open(REPORT_STARTER_PATH, 'r', encoding='utf-8') as f:
            report_css = _get_css_without_header(f.read())
        assert starter_css == report_css
