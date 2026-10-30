"""Structure-family slot renderers — content model in, markup plus data block out.

Eight components share one normalized content model: card grids (#2), CSS
timelines (#3), comparison tables (#5 basic, #22 enhanced), data-card grids
(#12), quote cards (#13), tag badge groups (#17) and callout bars (#18).  None
of them is a chart, a meter or a numeric-metric display, which is what keeps
them out of the chart family.

Bilingual text
--------------
Every human-readable model field has an optional English counterpart
(``title_en``, ``label_en``, ``note_en``, ``name_en``).  A renderer that emits
body text emits the Chinese and the English version as a ``data-lang`` pair, so
the existing bilingual check stays balanced after a swap.  When a counterpart
is missing the renderer falls back to the Chinese text instead of emitting an
empty block.  Numbers and other language-neutral values are emitted once, with
no ``data-lang`` at all.

Empty states
------------
A list-driven renderer whose item list is empty emits an explicit bilingual
empty state and no empty container.  The quote card is the one exception: its
text lives in ``title``/``subtitle``, so an empty item list means "single
quote", not "no data" (see :func:`_render_quote_card`).
"""

import html
import re

from context2html.content_model import (
    ContentModelError,
    require_item_values,
    require_numbers,
)

COMPONENT_ROLE_CARDS = 2
COMPONENT_TIMELINE = 3
COMPONENT_COMPARISON_TABLE = 5
COMPONENT_DATA_CARDS = 12
COMPONENT_QUOTE_CARD = 13
COMPONENT_TAG_GROUP = 17
COMPONENT_CALLOUTS = 18
COMPONENT_COMPARISON_TABLE_ENHANCED = 22

_SAFE_COLOR = re.compile(r'(?:#[0-9A-Fa-f]{3,8}|var\(--[A-Za-z0-9_-]+\))')


def _esc(value):
    return html.escape(str(value), quote=True)


def _pair(tag, zh, en='', attrs=''):
    """Two sibling elements, one per language, sharing the same attributes."""
    en = en or zh
    return (
        f'<{tag}{attrs} data-lang="zh">{_esc(zh)}</{tag}>'
        f'<{tag}{attrs} data-lang="en">{_esc(en)}</{tag}>'
    )


def _inline_pair(zh, en=''):
    """Both languages inside a single parent element (table cells, headers)."""
    en = en or zh
    return (
        f'<span data-lang="zh">{_esc(zh)}</span>'
        f'<span data-lang="en">{_esc(en)}</span>'
    )


def _empty_state():
    return (
        '<p class="ic-empty" data-lang="zh">暂无数据</p>'
        '<p class="ic-empty" data-lang="en">No data</p>'
    )


def _slot(component_id, slot_id, body):
    return (
        f'<section class="ic-slot" data-slot="{slot_id}" '
        f'data-component="{component_id}">\n{body}\n</section>'
    )


def _require_items(model, component_id):
    """Return True when items exist; raise when the model only has series.

    A component that cannot read series must not silently render an empty
    state over real data — the caller has to pick a component that can.
    """
    if model.items:
        return True
    if model.series:
        raise ContentModelError(
            'items',
            f'component {component_id} needs items; the model has series only')
    return False


def _accent(item, fallback=''):
    """Return the item's emphasis colour when it is a safe CSS value."""
    if _SAFE_COLOR.fullmatch(item.accent):
        return item.accent
    return fallback


def _num(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _render_data_cards(model, slot_id):
    if not _require_items(model, COMPONENT_DATA_CARDS):
        return _slot(COMPONENT_DATA_CARDS, slot_id, _empty_state())
    require_item_values(model)

    cards = []
    for item in model.items:
        parts = ['<div class="dg-card" data-anim="fade-up">']
        color = _accent(item)
        style = f' style="color:{color}"' if color else ''
        parts.append(f'<div class="dg-value"{style}>{_esc(_num(item.value))}</div>')
        if item.note:
            parts.append(_pair('div', item.note, item.note_en, ' class="dg-unit"'))
        parts.append(_pair('div', item.label, item.label_en, ' class="dg-label"'))
        parts.append('</div>')
        cards.append(''.join(parts))

    body = '<div class="data-grid">' + ''.join(cards) + '</div>'
    return _slot(COMPONENT_DATA_CARDS, slot_id, body)


def _render_role_cards(model, slot_id):
    if not _require_items(model, COMPONENT_ROLE_CARDS):
        return _slot(COMPONENT_ROLE_CARDS, slot_id, _empty_state())

    palette = ('#3b82f6', '#f59e0b', '#ef4444', '#10b981')
    cards = []
    for index, item in enumerate(model.items):
        color = _accent(item, palette[index % len(palette)])
        header = (
            f'<div class="role-header" style="background:{color};color:#fff">'
            f'{_inline_pair(item.label, item.label_en)}</div>'
        )
        body = ''
        if item.note:
            body = (
                '<div class="role-body">'
                f'{_pair("p", item.note, item.note_en)}'
                '</div>'
            )
        cards.append(f'<div class="role-card">{header}{body}</div>')

    grid = '<div class="role-grid">' + ''.join(cards) + '</div>'
    return _slot(COMPONENT_ROLE_CARDS, slot_id, grid)


def _render_timeline(model, slot_id):
    """Events ordered by ``value``; a non-empty ``accent`` marks a key milestone."""
    if not _require_items(model, COMPONENT_TIMELINE):
        return _slot(COMPONENT_TIMELINE, slot_id, _empty_state())
    require_item_values(model)

    events = []
    for item in sorted(model.items, key=lambda event: event.value):
        color = _accent(item)
        classes = 'tl-dot major' if item.accent else 'tl-dot'
        style = f' style="background:{color}"' if color else ''
        parts = [
            f'<div class="tl-item"><div class="{classes}"{style}></div>',
            _pair('div', item.label, item.label_en, ' class="tl-date"'),
        ]
        if item.note:
            parts.append(_pair('div', item.note, item.note_en, ' class="tl-desc"'))
        parts.append('</div>')
        events.append(''.join(parts))

    body = '<div class="timeline">' + ''.join(events) + '</div>'
    return _slot(COMPONENT_TIMELINE, slot_id, body)


_CMP_ARROW = '<span class="cmp-arrow">↕</span>'

_SORT_SCRIPT = """<script>
(function () {
  var table = document.getElementById("cmp-{slot_id}");
  if (!table) return;
  table.querySelectorAll('th[data-sort]').forEach(function (th) {
    th.addEventListener("click", function () {
      var body = table.tBodies[0];
      var rows = Array.prototype.slice.call(body.rows);
      var index = Array.prototype.indexOf.call(th.parentNode.children, th);
      var asc = !th.classList.contains("sorted-asc");
      table.querySelectorAll("th").forEach(function (cell) {
        cell.classList.remove("sorted-asc", "sorted-desc");
      });
      th.classList.add(asc ? "sorted-asc" : "sorted-desc");
      rows.sort(function (a, b) {
        var x = a.cells[index].textContent.trim();
        var y = b.cells[index].textContent.trim();
        var p = parseFloat(x);
        var q = parseFloat(y);
        if (!isNaN(p) && !isNaN(q)) return asc ? p - q : q - p;
        return asc ? x.localeCompare(y, "zh-CN") : y.localeCompare(x, "zh-CN");
      });
      rows.forEach(function (row) { body.appendChild(row); });
    });
  });
})();
</script>"""


def _table_columns(model):
    """Columns are the series; without series the table degrades to label/value."""
    if model.series:
        return [(series.name, series.name_en) for series in model.series]
    return [('数值', 'Value')]


def _table_head(model, sortable=False):
    if sortable:
        first = f'<th data-sort>{_inline_pair("维度", "Dimension")}{_CMP_ARROW}</th>'
        cells = ''.join(
            f'<th data-sort>{_inline_pair(zh, en)}{_CMP_ARROW}</th>'
            for zh, en in _table_columns(model))
        return f'<tr>{first}{cells}</tr>'
    cells = ''.join(
        f'<th>{_inline_pair(zh, en)}</th>' for zh, en in _table_columns(model))
    return f'<tr><th></th>{cells}</tr>'


def _table_rows(model):
    rows = []
    for index, item in enumerate(model.items):
        cells = [f'<td data-label="维度">{_inline_pair(item.label, item.label_en)}</td>']
        if model.series:
            for series in model.series:
                cells.append(
                    f'<td data-label="{_esc(series.name)}">'
                    f'{_esc(_num(series.values[index]))}</td>')
        else:
            cells.append(f'<td data-label="数值">{_esc(_num(item.value))}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return ''.join(rows)


def _table_markup(model, table_class, table_attrs='', sortable=False):
    return (
        f'<table class="{table_class}"{table_attrs}>'
        f'<thead>{_table_head(model, sortable)}</thead>'
        f'<tbody>{_table_rows(model)}</tbody>'
        '</table>'
    )


def _render_comparison_table(model, slot_id):
    if not _require_items(model, COMPONENT_COMPARISON_TABLE):
        return _slot(COMPONENT_COMPARISON_TABLE, slot_id, _empty_state())
    require_numbers(model)

    body = _table_markup(model, 'cmp-table')
    if model.subtitle:
        body += _pair('p', model.subtitle, model.subtitle_en, ' class="cmp-caption"')
    return _slot(COMPONENT_COMPARISON_TABLE, slot_id, body)


def _render_comparison_table_enhanced(model, slot_id):
    if not _require_items(model, COMPONENT_COMPARISON_TABLE_ENHANCED):
        return _slot(COMPONENT_COMPARISON_TABLE_ENHANCED, slot_id, _empty_state())
    require_numbers(model)

    table = _table_markup(
        model, 'cmp-table', f' data-sortable id="cmp-{slot_id}"', sortable=True)
    body = (
        f'<div class="cmp-wrap" data-anim="fade-up">\n{table}\n</div>\n'
        f'{_SORT_SCRIPT.replace("{slot_id}", slot_id)}'
    )
    if model.subtitle:
        body += '\n' + _pair(
            'p', model.subtitle, model.subtitle_en, ' class="cmp-caption"')
    return _slot(COMPONENT_COMPARISON_TABLE_ENHANCED, slot_id, body)


def _render_quote_card(model, slot_id):
    """One card per item; with no items the title itself is the single quote."""
    quotes = [
        (item.label, item.label_en, item.note, item.note_en)
        for item in model.items
    ] or [(model.title, model.title_en, model.subtitle, model.subtitle_en)]

    cards = []
    for text, text_en, source, source_en in quotes:
        parts = [
            '<div class="quote-card" data-anim="fade-up">',
            '<div class="qc-bar"></div>',
            '<div class="qc-body">',
            _pair('p', text, text_en, ' class="qc-text"'),
        ]
        if source:
            attribution = _pair('span', source, source_en, ' class="qc-title"')
            parts.append(f'<div class="qc-source">{attribution}</div>')
        parts.append('</div></div>')
        cards.append(''.join(parts))

    return _slot(COMPONENT_QUOTE_CARD, slot_id, ''.join(cards))


_TAG_PALETTE = ('blue', 'red', 'green', 'orange', 'purple')


def _tag_label(label):
    return label if label.lstrip().startswith('#') else f'# {label}'


def _tag_class(item, index):
    if item.accent in _TAG_PALETTE:
        return f'tag tag-{item.accent}'
    return f'tag tag-{_TAG_PALETTE[index % len(_TAG_PALETTE)]}'


def _render_tag_group(model, slot_id):
    if not _require_items(model, COMPONENT_TAG_GROUP):
        return _slot(COMPONENT_TAG_GROUP, slot_id, _empty_state())

    tags = []
    for index, item in enumerate(model.items):
        classes = _tag_class(item, index)
        english = _tag_label(item.label_en) if item.label_en else ''
        tags.append(_pair('span', _tag_label(item.label), english, f' class="{classes}"'))

    body = f'<div class="tag-group" data-anim="fade-up">{"".join(tags)}</div>'
    return _slot(COMPONENT_TAG_GROUP, slot_id, body)


_CALLOUT_TYPES = {
    'info': ('info', '💡'),
    'warning': ('warning', '⚠️'),
    'error': ('error', '❌'),
    'success': ('success', '✅'),
}


def _render_callouts(model, slot_id):
    if not _require_items(model, COMPONENT_CALLOUTS):
        return _slot(COMPONENT_CALLOUTS, slot_id, _empty_state())

    bars = []
    for item in model.items:
        kind, icon = _CALLOUT_TYPES.get(item.accent, _CALLOUT_TYPES['info'])
        paragraphs = [_pair('p', item.label, item.label_en)]
        if item.note:
            paragraphs.append(_pair('p', item.note, item.note_en))
        bars.append(
            f'<div class="callout callout-{kind}" data-anim="fade-up">'
            f'<div class="callout-icon">{icon}</div>'
            f'<div class="callout-body">{"".join(paragraphs)}</div>'
            '</div>')

    return _slot(COMPONENT_CALLOUTS, slot_id, ''.join(bars))


STRUCTURE_RENDERERS = {
    COMPONENT_ROLE_CARDS: _render_role_cards,
    COMPONENT_TIMELINE: _render_timeline,
    COMPONENT_COMPARISON_TABLE: _render_comparison_table,
    COMPONENT_DATA_CARDS: _render_data_cards,
    COMPONENT_QUOTE_CARD: _render_quote_card,
    COMPONENT_TAG_GROUP: _render_tag_group,
    COMPONENT_CALLOUTS: _render_callouts,
    COMPONENT_COMPARISON_TABLE_ENHANCED: _render_comparison_table_enhanced,
}
