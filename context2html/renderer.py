"""Template Renderer — assemble components into templates."""

import os
import re

from context2html.editor import enable_editable
from context2html.registry import ComponentRegistry
from context2html.slots import render_slot

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

_TEMPLATE_MAP = {
    'report-starter': 'report-starter.html',
    'starter': 'starter.html',
}

_CSS_ZONE_MARKER = (
    r'INSERT: 从 components/NN-name\.md 复制 CSS 到这里（组件 CSS 可追加在下方）'
)
_RE_CSS_ZONE = re.compile(rf'<!-- {_CSS_ZONE_MARKER} -->')
# The shipped templates mark the CSS insertion point with a CSS comment, which
# _RE_CSS_ZONE never matched.  Slot output inserts CSS through this pattern so a
# generated editable report carries the component styles it needs; slot output
# off stays byte-identical to the historical behaviour.
_RE_CSS_ZONE_SLOT = re.compile(rf'<!-- {_CSS_ZONE_MARKER} -->|/\* {_CSS_ZONE_MARKER} \*/')
_RE_HTML_ZONE = re.compile(
    r'<!-- INSERT: 视觉组件 HTML -->'
)
_RE_JS_ZONE = re.compile(
    r'<!-- INSERT: 从 components/NN-name\.md 复制 JS 到这里（可追加在下方） -->'
)
_RE_THEME_ATTR = re.compile(r'data-theme="[^"]*"')
_RE_THEME_NAME = re.compile(r'[A-Za-z0-9._-]+')
_RE_LIB_NAME = re.compile(r'[A-Za-z0-9._-]+')


class TemplateRenderer:
    def __init__(self, registry=None, templates_dir=None):
        self._reg = registry or ComponentRegistry()
        self._templates_dir = templates_dir or TEMPLATES_DIR

    def assemble(self, template_name, components, theme_name='warm', slots=None,
                 editable=False):
        template_file = _TEMPLATE_MAP.get(template_name)
        if not template_file:
            raise ValueError(f"Unknown template: {template_name}. Use: {', '.join(_TEMPLATE_MAP.keys())}")

        if not _RE_THEME_NAME.fullmatch(theme_name):
            raise ValueError(
                f"Invalid theme name: {theme_name!r} "
                "(expected letters, digits, dot, underscore or hyphen)")

        slot_specs = _normalise_slots(slots)
        rendered_slots = [
            render_slot(component_id, model, slot_id)
            for component_id, model, slot_id in slot_specs
        ]
        _reject_duplicate_slot_ids(rendered_slots)
        slot_fragments = [slot.fragment for slot in rendered_slots]
        slot_component_ids = {component_id for component_id, _, _ in slot_specs}
        merge_ids = list(components) + [
            cid for cid in dict.fromkeys(
                component_id for component_id, _, _ in slot_specs)
            if cid not in components
        ]

        tpl_path = os.path.join(self._templates_dir, template_file)
        if not os.path.exists(tpl_path):
            raise FileNotFoundError(f"Template not found: {tpl_path}")

        with open(tpl_path, 'r', encoding='utf-8') as f:
            html = f.read()

        html = _RE_THEME_ATTR.sub(f'data-theme="{theme_name}"', html)

        if slot_specs:
            html = _insert_library_dependencies(html, self._reg, slot_specs)

        component_html_parts = []
        component_css_parts = []
        component_js_parts = []

        for cid in merge_ids:
            comps = self._reg.list_components(id=cid)
            if not comps:
                continue
            comp = comps[0]
            if comp.html and cid not in slot_component_ids:
                markup = comp.html
                if editable:
                    markup = (
                        f'<div class="ic-static" data-component="{cid}" '
                        f'data-swap="unavailable">{markup}</div>')
                component_html_parts.append(markup)
            if comp.css:
                component_css_parts.append(comp.css)
            if comp.js:
                component_js_parts.append(comp.js)

        if editable:
            # A swap can land on any of the fourteen components, so the report
            # must already carry their CSS even when only one was used.
            seen_css = set(merge_ids)
            for comp in self._reg.list_components(content_model=True):
                if comp.id in seen_css:
                    continue
                if comp.css:
                    component_css_parts.append(comp.css)

        if component_css_parts:
            css_zone = _RE_CSS_ZONE_SLOT if (slot_specs or editable) else _RE_CSS_ZONE
            html = css_zone.sub(
                _make_inserter('\n'.join(component_css_parts) + '\n'), html, count=1
            )

        html_parts = list(slot_fragments)
        if component_html_parts:
            html_parts.append('\n'.join(component_html_parts) + '\n')
        if html_parts:
            html = _RE_HTML_ZONE.sub(
                _make_inserter('\n'.join(html_parts)), html, count=1
            )

        if component_js_parts:
            html = _RE_JS_ZONE.sub(
                _make_inserter('\n'.join(component_js_parts) + '\n'), html, count=1
            )

        if editable:
            html = enable_editable(html)

        return html


def _reject_duplicate_slot_ids(rendered_slots):
    """A report with two slots sharing an id would fail the validator; stop early."""
    seen = set()
    for slot in rendered_slots:
        if slot.slot_id in seen:
            raise ValueError(f'duplicate slot id: {slot.slot_id!r}')
        seen.add(slot.slot_id)


def _insert_library_dependencies(html, registry, slot_specs):
    """Load each slot component's libraries synchronously before ``</head>``.

    The slot markup runs an inline init script while the body parses, so the
    library has to be there already; the template's CDN-first loader appends
    asynchronously and would arrive too late.  Only components actually
    rendered as slots contribute dependencies: an editable report with no
    slots loads nothing, which keeps "mail one file" delivery honest.
    """
    tags = []
    seen = set()
    component_ids = [cid for cid, _, _ in slot_specs]
    for component_id in dict.fromkeys(component_ids):
        comps = registry.list_components(id=component_id)
        if not comps:
            continue
        for dependency in comps[0].metadata.dependencies:
            if dependency in seen or not _RE_LIB_NAME.fullmatch(dependency):
                continue
            seen.add(dependency)
            tags.append(f'<script src="libs/{dependency}"></script>')
    if not tags:
        return html
    return html.replace('</head>', '\n'.join(tags) + '\n</head>', 1)


def _normalise_slots(slots):
    """Turn ``slots`` into ``(component_id, model, slot_id_or_None)`` tuples.

    ``None`` (the default) means slot output is off.  A slot is either a
    ``(component_id, model)`` / ``(component_id, model, slot_id)`` tuple or a
    mapping with ``component``, ``model`` and an optional ``slot_id``.
    """
    if slots is None:
        return []
    if isinstance(slots, (str, bytes, dict)):
        raise ValueError(
            'slots must be a sequence of (component_id, model) tuples or mappings')

    specs = []
    for spec in slots:
        if isinstance(spec, dict):
            if 'component' not in spec or 'model' not in spec:
                raise ValueError(
                    "each slot mapping needs 'component' and 'model' keys")
            component_id = spec['component']
            model = spec['model']
            slot_id = spec.get('slot_id')
        elif isinstance(spec, (tuple, list)) and len(spec) in (2, 3):
            component_id = spec[0]
            model = spec[1]
            slot_id = spec[2] if len(spec) == 3 else None
        else:
            raise ValueError(
                'each slot must be a (component_id, model) tuple or a mapping '
                "with 'component' and 'model' keys")
        specs.append((component_id, model, slot_id))
    return specs


def _make_inserter(content):
    def replacer(match):
        return match.group(0) + '\n' + content
    return replacer
