"""Tests for context2html.theme."""
import os

from context2html.theme import ThemeProvider

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, 'theme', 'theme-index.json')


class TestThemeProvider:
    def setup_method(self):
        self.tp = ThemeProvider(INDEX_PATH)

    def test_list_themes_returns_20(self):
        themes = self.tp.list_themes()
        assert len(themes) == 20

    def test_get_theme_warm(self):
        t = self.tp.get_theme('warm')
        assert t is not None
        assert t.name == 'warm'
        assert t.accent == '#c0392b'
        assert t.bg == '#faf9f7'

    def test_get_theme_unknown(self):
        assert self.tp.get_theme('nonexistent') is None

    def test_recommend_report_defaults_to_warm(self):
        name = self.tp.recommend_theme('report')
        assert name is not None

    def test_recommend_by_topic(self):
        name = self.tp.recommend_theme('tutorial', '编程')
        assert name == 'cursor'

    def test_recommend_unknown_content_type_falls_back(self):
        name = self.tp.recommend_theme('unknown_type')
        assert name == 'warm'

    def test_recommend_empty_topic_uses_first_in_list(self):
        name = self.tp.recommend_theme('note')
        assert name == 'cursor'

    def test_theme_has_recommend_for(self):
        t = self.tp.get_theme('warm')
        assert 'report' in t.recommend_for
