"""Slot rendering — one content model in, markup plus its data block out.

A slot is the unit the browser editor swaps.  Its rendered root carries a
stable ``data-slot`` id and a ``data-component`` id; a sibling
``<script type="application/json" data-slot="...">`` block holds the content
model that produced the markup.  Both come from the same call so they cannot
drift apart.

Only the chart family is implemented here — #4, #15, #19, #20, #24 and #26;
the structure family joins ``_RENDERERS`` as it gains renderers.  Every
renderer reads the fields it needs and ignores the rest, so a slot can be
re-rendered as a different component from the same content model.
"""

import hashlib
import json
import re
from dataclasses import dataclass

from context2html.content_model import (
    ContentModel,
    ContentModelError,
    ContentSeries,
    validate_content_model,
)

_SLOT_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:-]*')
_COLOR_VARS = (
    '--accent', '--chart-3', '--chart-4',
    '--success', '--warning', '--error',
)
_ACCENT_TOKENS = frozenset({
    'accent', 'success', 'warning', 'error',
    'chart-1', 'chart-2', 'chart-3', 'chart-4',
})
_RE_HEX_COLOR = re.compile(r'#[0-9A-Fa-f]{3,8}')
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


def _escape(text):
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _percent(value, maximum):
    if maximum <= 0:
        return 0.0
    return round(value / maximum * 100, 1)


def _accent_css(accent, index):
    """Map a content-model accent to a safe CSS color value."""
    if accent in _ACCENT_TOKENS:
        return f'var(--{accent})'
    if accent and _RE_HEX_COLOR.fullmatch(accent):
        return accent
    return f'var(--chart-{(index % 4) + 1})'


def _empty_state():
    return (
        '<div class="ic-empty" role="status">'
        '<span data-lang="zh">暂无数据</span>'
        '<span data-lang="en">No data</span>'
        '</div>'
    )


def _section(component_id, slot_id, model, body):
    return (
        f'<section class="ic-slot" data-slot="{slot_id}" '
        f'data-component="{component_id}" '
        f'aria-label="{_escape(model.title)}">\n'
        f'{body}\n'
        '</section>\n'
    )


def _item_entries(model):
    """Return ``(label, value, note, accent)`` tuples and the error field path.

    Items are the natural source; a series-only model falls back to the first
    series with positional labels so a chart-family swap never shows an empty
    state while the slot still holds data.
    """
    if model.items:
        return (
            [(item.label, item.value, item.note, item.accent)
             for item in model.items],
            'items[{}].value')
    if model.series:
        return (
            [(str(index + 1), value, '', '')
             for index, value in enumerate(model.series[0].values)],
            'series[0].values[{}]')
    return None, ''


def _render_bar_chart(model, slot_id):
    entries, field = _item_entries(model)
    if entries is None:
        return _section(4, slot_id, model, _empty_state())

    for index, (_, value, _, _) in enumerate(entries):
        if value < 0:
            raise ContentModelError(
                field.format(index), 'expected a non-negative number')
    maximum = max(value for _, value, _, _ in entries)

    rows = []
    for index, (label, value, _, accent) in enumerate(entries):
        width = _percent(value, maximum)
        rows.append(
            '  <div class="bar-item">\n'
            f'    <div class="bar-label">{_escape(label)}</div>\n'
            '    <div class="bar-track">\n'
            f'      <div class="bar-fill" style="width:{width:g}%; '
            f'background:{_accent_css(accent, index)};">'
            f'{_escape(_format_number(value))}</div>\n'
            '    </div>\n'
            '  </div>')
    body = '  <div class="bar-chart">\n' + '\n'.join(rows) + '\n  </div>'
    return _section(4, slot_id, model, body)


def _progress_state(value):
    if value >= 100:
        return 'done'
    if value > 0:
        return 'current'
    return 'pending'


def _render_status_chain(model, slot_id):
    entries, _ = _item_entries(model)
    if entries is None:
        return _section(15, slot_id, model, _empty_state())

    steps = []
    for label, value, note, _ in entries:
        status = ''
        if note:
            status = f'\n    <div class="sc-status">{_escape(note)}</div>'
        steps.append(
            f'  <div class="sc-step {_progress_state(value)}">\n'
            '    <div class="sc-dot"></div>\n'
            f'    <div class="sc-label">{_escape(label)}</div>{status}\n'
            '  </div>')
    body = '  <div class="status-chain">\n' + '\n'.join(steps) + '\n  </div>'
    return _section(15, slot_id, model, body)


def _intensity(value, lowest, highest):
    if highest <= lowest:
        return 2
    return int(round((value - lowest) / (highest - lowest) * 4))


def _render_heatmap(model, slot_id):
    if model.series:
        rows = [(series.name, series.values) for series in model.series]
    elif model.items:
        rows = [(model.title, tuple(item.value for item in model.items))]
    else:
        return _section(19, slot_id, model, _empty_state())

    width = max((len(values) for _, values in rows), default=0)
    if width == 0:
        return _section(19, slot_id, model, _empty_state())

    labels = [item.label for item in model.items]
    if not labels:
        labels = [str(index + 1) for index in range(width)]

    numbers = [value for _, values in rows for value in values]
    lowest, highest = min(numbers), max(numbers)

    header = (
        '    <div class="hm-row">\n'
        '      <div class="hm-label"></div>\n'
        + '\n'.join(
            f'      <div class="hm-hdr">{_escape(label)}</div>'
            for label in labels)
        + '\n    </div>')

    body_rows = []
    for name, values in rows:
        cells = '\n'.join(
            f'      <div class="hm-cell" data-l="{_intensity(value, lowest, highest)}">'
            f'{_escape(_format_number(value))}</div>'
            for value in values)
        body_rows.append(
            '    <div class="hm-row">\n'
            f'      <div class="hm-label">{_escape(name)}</div>\n'
            f'{cells}\n'
            '    </div>')

    body = ('  <div class="heatmap">\n' + header + '\n'
            + '\n'.join(body_rows) + '\n  </div>')
    return _section(19, slot_id, model, body)


def _render_step_indicator(model, slot_id):
    entries, _ = _item_entries(model)
    if entries is None:
        return _section(20, slot_id, model, _empty_state())

    steps = []
    for index, (label, value, _, _) in enumerate(entries):
        steps.append(
            f'  <div class="si-step {_progress_state(value)}">'
            f'<div class="si-num">{index + 1}</div>'
            f'<div class="si-label">{_escape(label)}</div></div>')
    body = '  <div class="step-indicator">\n' + '\n'.join(steps) + '\n  </div>'
    return _section(20, slot_id, model, body)


def _render_chart_set(model, slot_id):
    entries, field = _item_entries(model)
    if entries is None:
        return _section(24, slot_id, model, _empty_state())

    for index, (_, value, _, _) in enumerate(entries):
        if value < 0:
            raise ContentModelError(
                field.format(index), 'expected a non-negative number')
    maximum = max(value for _, value, _, _ in entries)

    bars = []
    for label, value, _, _ in entries:
        height = _percent(value, maximum)
        bars.append(
            f'      <div class="vc-bar" style="--h:{height:g};" '
            f'data-label="{_escape(label)}">'
            f'<span class="vc-val">{_escape(_format_number(value))}</span></div>')
    body = ('  <div class="vchart">\n'
            '    <div class="vc-group">\n'
            + '\n'.join(bars) + '\n'
            '    </div>\n'
            '  </div>')
    return _section(24, slot_id, model, body)


def _render_echarts(model, slot_id):
    if not model.items and not model.series:
        return _section(26, slot_id, model, _empty_state())

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
    4: _render_bar_chart,
    15: _render_status_chain,
    19: _render_heatmap,
    20: _render_step_indicator,
    24: _render_chart_set,
    26: _render_echarts,
}
