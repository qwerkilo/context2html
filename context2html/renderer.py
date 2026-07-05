"""Template Renderer — assemble components into templates."""

import os
import re

from context2html.registry import ComponentRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

_TEMPLATE_MAP = {
    'report-starter': 'report-starter.html',
    'starter': 'starter.html',
}

_RE_CSS_ZONE = re.compile(
    r'<!-- INSERT: 从 components/NN-name\.md 复制 CSS 到这里（组件 CSS 可追加在下方） -->'
)
_RE_HTML_ZONE = re.compile(
    r'<!-- INSERT: 视觉组件 HTML -->'
)
_RE_JS_ZONE = re.compile(
    r'<!-- INSERT: 从 components/NN-name\.md 复制 JS 到这里（可追加在下方） -->'
)
_RE_THEME_ATTR = re.compile(r'data-theme="[^"]*"')


class TemplateRenderer:
    def __init__(self, registry=None, templates_dir=None):
        self._reg = registry or ComponentRegistry()
        self._templates_dir = templates_dir or TEMPLATES_DIR

    def assemble(self, template_name, components, theme_name='warm'):
        template_file = _TEMPLATE_MAP.get(template_name)
        if not template_file:
            raise ValueError(f"Unknown template: {template_name}. Use: {', '.join(_TEMPLATE_MAP.keys())}")

        tpl_path = os.path.join(self._templates_dir, template_file)
        if not os.path.exists(tpl_path):
            raise FileNotFoundError(f"Template not found: {tpl_path}")

        with open(tpl_path, 'r', encoding='utf-8') as f:
            html = f.read()

        html = _RE_THEME_ATTR.sub(f'data-theme="{theme_name}"', html)

        component_html_parts = []
        component_css_parts = []
        component_js_parts = []

        for cid in components:
            comps = self._reg.list_components(id=cid)
            if not comps:
                continue
            comp = comps[0]
            if comp.html:
                component_html_parts.append(comp.html)
            if comp.css:
                component_css_parts.append(comp.css)
            if comp.js:
                component_js_parts.append(comp.js)

        if component_css_parts:
            html = _RE_CSS_ZONE.sub(
                _make_inserter('\n'.join(component_css_parts) + '\n'), html, count=1
            )

        if component_html_parts:
            html = _RE_HTML_ZONE.sub(
                _make_inserter('\n'.join(component_html_parts) + '\n'), html
            )

        if component_js_parts:
            html = _RE_JS_ZONE.sub(
                _make_inserter('\n'.join(component_js_parts) + '\n'), html, count=1
            )

        return html


def _make_inserter(content):
    def replacer(match):
        return match.group(0) + '\n' + content
    return replacer
