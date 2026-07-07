"""Theme Provider — programmatic access to brand themes."""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_INDEX_PATH = os.path.join(BASE_DIR, 'theme', 'theme-index.json')


class ThemeInfo:
    def __init__(self, name, display_name=None, brand=None, accent='', bg='', text='',
                 font='', font_h='', chart_colors=None, radius='', has_dark_bg=False,
                 recommend_for=None, recommend_topics=None):
        self.name = name
        self.display_name = display_name or name
        self.brand = brand or name
        self.accent = accent
        self.bg = bg
        self.text = text
        self.font = font
        self.font_h = font_h
        self.chart_colors = chart_colors or []
        self.radius = radius
        self.has_dark_bg = has_dark_bg
        self.recommend_for = recommend_for or ['report', 'article', 'doc', 'tutorial', 'note']
        self.recommend_topics = recommend_topics or []

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get('name', ''),
            display_name=d.get('display_name', d.get('name', '')),
            brand=d.get('brand', d.get('name', '')),
            accent=d.get('accent', ''),
            bg=d.get('bg', ''),
            text=d.get('text', ''),
            font=d.get('font', ''),
            font_h=d.get('font_h', ''),
            chart_colors=d.get('chart_colors', []),
            radius=d.get('radius', ''),
            has_dark_bg=d.get('has_dark_bg', False),
            recommend_for=d.get('recommend_for', ['report', 'article', 'doc', 'tutorial', 'note']),
            recommend_topics=d.get('recommend_topics', []),
        )


class ThemeProvider:
    def __init__(self, index_path=None):
        self._path = index_path or THEME_INDEX_PATH
        self._cache = None

    def _load_all(self):
        if self._cache is not None:
            return self._cache
        with open(self._path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._cache = [ThemeInfo.from_dict(d) for d in data]
        return self._cache

    def list_themes(self):
        return self._load_all()

    def get_theme(self, name):
        for t in self._load_all():
            if t.name == name:
                return t
        return None

    def recommend_theme(self, content_type, topic=None):
        themes = self._load_all()
        candidates = [t for t in themes if content_type in t.recommend_for]
        if not candidates:
            candidates = themes
        if topic:
            topic_lower = topic.lower()
            for t in candidates:
                if any(topic_lower in rt.lower() or rt.lower() in topic_lower
                       for rt in t.recommend_topics):
                    return t.name
        if candidates:
            return candidates[0].name
        return 'warm'
