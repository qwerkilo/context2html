"""Slot rendering — one content model in, markup plus its data block out.

A slot is the unit the browser editor swaps.  Its rendered root carries a
stable ``data-slot`` id and a ``data-component`` id; a sibling
``<script type="application/json" data-slot="...">`` block holds the content
model that produced the markup.  Both come from the same call so they cannot
drift apart.

Only component #26 (ECharts interactive chart kit) is implemented here; the
remaining swappable components join ``_RENDERERS`` as they gain a renderer.
"""

import hashlib
import json
import re
from dataclasses import dataclass

from context2html.content_model import (
    ContentModel,
    ContentSeries,
    validate_content_model,
)

_SLOT_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:-]*')
_COLOR_VARS = (
    '--accent', '--chart-3', '--chart-4',
    '--success', '--warning', '--error',
)
_GV_TEXT = '@@GV_TEXT@@'
_GV_MUTED = '@@GV_MUTED@@'
_GV_COLOR = '@@GV_COLOR_{}@@'
_GV_COLOR_RE = re.compile(r'"@@GV_COLOR_(\d+)@@"')


class SlotError(ValueError):
    """Raised when a slot cannot be rendered (unknown component, bad id)."""


@dataclass(frozen=True)
class RenderedSlot:
    slot_id: str
    component_id: int
    markup: str
    data_block: str

    @property
    def fragment(self):
        """Markup followed by its data block, ready to insert into a report."""
        return f'{self.markup}\n{self.data_block}\n'


def render_slot(component_id, model, slot_id=None):
    """Render one component slot from a content model.

    ``model`` is a plain dict or a validated :class:`ContentModel`.  When
    ``slot_id`` is omitted it is derived from the canonical model JSON, so the
    same component + data always produces the same id.
    """
    renderer = _RENDERERS.get(component_id)
    if renderer is None:
        raise SlotError(f'unsupported component id: {component_id!r}')

    if not isinstance(model, ContentModel):
        model = validate_content_model(model)

    if slot_id is None:
        slot_id = _derive_slot_id(component_id, model)
    elif not isinstance(slot_id, str) or not _SLOT_ID.fullmatch(slot_id):
        raise SlotError(f'invalid slot id: {slot_id!r}')

    canonical = _canonical_json(model)
    data_block = (
        f'<script type="application/json" data-slot="{slot_id}">'
        f'{_script_safe(canonical)}</script>'
    )
    return RenderedSlot(
        slot_id=slot_id,
        component_id=component_id,
        markup=renderer(model, slot_id),
        data_block=data_block,
    )


def _derive_slot_id(component_id, model):
    digest = hashlib.sha1(_canonical_json(model).encode('utf-8')).hexdigest()[:8]
    return f'slot-{component_id}-{digest}'


def _canonical_json(model):
    return json.dumps(
        model.to_dict(), ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _script_safe(text):
    return text.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def _render_echarts(model, slot_id):
    option = _echarts_option(model)
    option_js = json.dumps(option, ensure_ascii=False, indent=2)
    option_js = _substitute_colors(option_js)
    lines = option_js.splitlines()
    option_js = '\n'.join([lines[0]] + ['  ' + line for line in lines[1:]])

    return (
        f'<section class="ic-slot" data-slot="{slot_id}" data-component="26">\n'
        '  <div class="ic-chart" '
        f'id="chart-{slot_id}" style="width:100%;height:350px;margin:1rem 0;"></div>\n'
        '  <div class="no-js-fallback"><p>图表加载需要 JavaScript</p></div>\n'
        '</section>\n'
        '<script>\n'
        '(function () {\n'
        f'  var el = document.getElementById("chart-{slot_id}");\n'
        '  if (!el || typeof echarts === "undefined") return;\n'
        '  function gv(n) { return getComputedStyle(document.documentElement)'
        '.getPropertyValue(n).trim(); }\n'
        '  var chart = echarts.init(el);\n'
        f'  chart.setOption({option_js});\n'
        '})();\n'
        '</script>'
    )


def _echarts_option(model):
    series = list(model.series) or [
        ContentSeries(name=model.title, values=tuple(item.value for item in model.items))
    ]
    labels = [item.label for item in model.items]
    if not labels:
        longest = max((len(item.values) for item in series), default=0)
        labels = [str(index + 1) for index in range(longest)]

    title = {'text': model.title}
    if model.subtitle:
        title['subtext'] = model.subtitle

    option = {
        'title': title,
        'tooltip': {'trigger': 'axis'},
        'legend': {'textStyle': {'color': _GV_TEXT}},
        'xAxis': {
            'type': 'category',
            'data': labels,
            'axisLabel': {'color': _GV_MUTED},
        },
        'yAxis': {'type': 'value', 'axisLabel': {'color': _GV_MUTED}},
        'series': [],
        'grid': {'left': 60, 'right': 30, 'top': 60, 'bottom': 30},
    }
    for index, item in enumerate(series):
        entry = {'name': item.name, 'type': 'bar'}
        if len(series) > 1:
            entry['stack'] = 'total'
        entry['data'] = list(item.values)
        entry['itemStyle'] = {'color': _GV_COLOR.format(index)}
        option['series'].append(entry)
    return option


def _substitute_colors(option_js):
    option_js = option_js.replace(f'"{_GV_TEXT}"', "gv('--text')")
    option_js = option_js.replace(f'"{_GV_MUTED}"', "gv('--muted')")
    return _GV_COLOR_RE.sub(
        lambda match: f"gv('{_COLOR_VARS[int(match.group(1)) % len(_COLOR_VARS)]}')",
        option_js,
    )


_RENDERERS = {
    26: _render_echarts,
}
