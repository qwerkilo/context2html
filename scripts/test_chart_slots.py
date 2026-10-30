"""Tests for the chart-family slot renderers.

Chart family: #4 CSS bar chart, #15 status chain, #19 heatmap, #20 step
indicator, #24 CSS/SVG chart set, #26 ECharts.  Every test drives the public
``render_slot`` seam: a fixed content model in, markup plus its data block out.
"""

import json

import pytest

from context2html.content_model import ContentModelError, validate_content_model
from context2html.slots import render_slot
from context2html.validator.slots import check_slot_data_blocks


def _data_block_json(slot):
    _, rest = slot.data_block.split('>', 1)
    body, _ = rest.rsplit('</script>', 1)
    return json.loads(body)


class TestCssBarChart:
    """#4 — horizontal bars, one per item, width normalized to the largest."""

    MODEL = {
        'title': '市场规模',
        'items': [
            {'label': '美国', 'value': 80, 'accent': 'accent'},
            {'label': '中国', 'value': 40, 'accent': 'warning'},
            {'label': '日本', 'value': 20},
        ],
    }

    def test_renders_one_bar_per_item(self):
        slot = render_slot(4, self.MODEL)
        assert 'data-component="4"' in slot.markup
        assert slot.markup.count('class="bar-item"') == 3
        assert (
            '<div class="bar-label"><span data-lang="zh">美国</span>'
            '<span data-lang="en">美国</span></div>'
        ) in slot.markup
        assert 'width:100%' in slot.markup
        assert 'width:50%' in slot.markup
        assert 'width:25%' in slot.markup
        assert 'background:var(--accent)' in slot.markup
        assert 'background:var(--warning)' in slot.markup

    def test_data_block_parses_back_to_the_model(self):
        slot = render_slot(4, self.MODEL)
        assert _data_block_json(slot) == validate_content_model(self.MODEL).to_dict()

    def test_empty_items_render_an_explicit_empty_state(self):
        slot = render_slot(4, {'title': '没有数据'})
        assert 'ic-empty' in slot.markup
        assert 'No data' in slot.markup
        assert 'bar-item' not in slot.markup

    def test_negative_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(4, {
                'title': 'T',
                'items': [{'label': 'A', 'value': -1}],
            })
        assert exc.value.field == 'items[0].value'

    def test_non_numeric_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(4, {
                'title': 'T',
                'items': [{'label': 'A', 'value': '80'}],
            })
        assert exc.value.field == 'items[0].value'


class TestStatusChain:
    """#15 — one milestone per item; ``value`` is completion percentage."""

    MODEL = {
        'title': '项目阶段',
        'items': [
            {'label': '需求分析', 'value': 100, 'note': '已完成'},
            {'label': '系统设计', 'value': 60, 'note': '进行中'},
            {'label': '开发实施', 'value': 0, 'note': '待开始'},
        ],
    }

    def test_renders_one_step_per_item_with_state_classes(self):
        slot = render_slot(15, self.MODEL)
        assert 'data-component="15"' in slot.markup
        assert slot.markup.count('class="sc-step ') == 3
        assert 'sc-step done' in slot.markup
        assert 'sc-step current' in slot.markup
        assert 'sc-step pending' in slot.markup
        assert (
            '<div class="sc-label"><span data-lang="zh">需求分析</span>'
            '<span data-lang="en">需求分析</span></div>'
        ) in slot.markup
        assert (
            '<div class="sc-status"><span data-lang="zh">已完成</span>'
            '<span data-lang="en">已完成</span></div>'
        ) in slot.markup

    def test_note_is_optional(self):
        slot = render_slot(15, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 100}],
        })
        assert 'sc-status' not in slot.markup

    def test_empty_items_render_an_explicit_empty_state(self):
        slot = render_slot(15, {'title': '没有数据'})
        assert 'ic-empty' in slot.markup
        assert 'sc-step' not in slot.markup

    def test_non_numeric_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(15, {
                'title': 'T',
                'items': [{'label': 'A', 'value': 'done'}],
            })
        assert exc.value.field == 'items[0].value'


class TestHeatmap:
    """#19 — series are rows, items are columns, values become intensity 0-4."""

    MODEL = {
        'title': '风险密度',
        'items': [
            {'label': '2007', 'value': 0},
            {'label': '2008', 'value': 0},
            {'label': '2009', 'value': 0},
        ],
        'series': [
            {'name': '美国', 'values': [1, 4, 2]},
            {'name': '欧洲', 'values': [0, 3, 3]},
        ],
    }

    def test_renders_one_row_per_series_and_one_cell_per_value(self):
        slot = render_slot(19, self.MODEL)
        assert 'data-component="19"' in slot.markup
        assert 'class="heatmap"' in slot.markup
        assert slot.markup.count('class="hm-cell"') == 6
        assert (
            '<div class="hm-hdr"><span data-lang="zh">2007</span>'
            '<span data-lang="en">2007</span></div>'
        ) in slot.markup
        assert (
            '<div class="hm-label"><span data-lang="zh">美国</span>'
            '<span data-lang="en">美国</span></div>'
        ) in slot.markup
        assert 'data-l="4">4</div>' in slot.markup
        assert 'data-l="0">0</div>' in slot.markup

    def test_falls_back_to_a_single_row_from_items(self):
        slot = render_slot(19, {
            'title': '单行',
            'items': [
                {'label': 'A', 'value': 1},
                {'label': 'B', 'value': 5},
            ],
        })
        assert slot.markup.count('class="hm-cell"') == 2
        assert 'data-l="0">1</div>' in slot.markup
        assert 'data-l="4">5</div>' in slot.markup

    def test_data_block_parses_back_to_the_model(self):
        slot = render_slot(19, self.MODEL)
        assert _data_block_json(slot) == validate_content_model(self.MODEL).to_dict()

    def test_empty_data_renders_an_explicit_empty_state(self):
        slot = render_slot(19, {'title': '没有数据'})
        assert 'ic-empty' in slot.markup
        assert 'heatmap' not in slot.markup

    def test_non_numeric_series_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(19, {
                'title': 'T',
                'series': [{'name': 'S', 'values': [1, 'high']}],
            })
        assert exc.value.field == 'series[0].values[1]'


class TestStepIndicator:
    """#20 — numbered steps; ``value`` is completion percentage."""

    MODEL = {
        'title': '实施步骤',
        'items': [
            {'label': '需求分析', 'value': 100},
            {'label': '系统设计', 'value': 100},
            {'label': '开发实施', 'value': 40},
            {'label': '测试验收', 'value': 0},
        ],
    }

    def test_renders_numbered_steps_with_state_classes(self):
        slot = render_slot(20, self.MODEL)
        assert 'data-component="20"' in slot.markup
        assert slot.markup.count('class="si-step ') == 4
        assert 'si-step done' in slot.markup
        assert 'si-step current' in slot.markup
        assert 'si-step pending' in slot.markup
        assert '<div class="si-num">1</div>' in slot.markup
        assert '<div class="si-num">4</div>' in slot.markup
        assert (
            '<div class="si-label"><span data-lang="zh">需求分析</span>'
            '<span data-lang="en">需求分析</span></div>'
        ) in slot.markup

    def test_empty_items_render_an_explicit_empty_state(self):
        slot = render_slot(20, {'title': '没有数据'})
        assert 'ic-empty' in slot.markup
        assert 'si-step' not in slot.markup

    def test_non_numeric_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(20, {
                'title': 'T',
                'items': [{'label': 'A', 'value': None}],
            })
        assert exc.value.field == 'items[0].value'


class TestDataChartSet:
    """#24 — the zero-dependency vertical bar chart (variant 24a)."""

    MODEL = {
        'title': 'GDP 对比',
        'items': [
            {'label': '美国', 'value': 100},
            {'label': '中国', 'value': 50},
            {'label': '日本', 'value': 25},
        ],
    }

    def test_renders_vertical_bars_with_normalized_height(self):
        slot = render_slot(24, self.MODEL)
        assert 'data-component="24"' in slot.markup
        assert slot.markup.count('class="vc-bar"') == 3
        assert '--h:100;' in slot.markup
        assert '--h:50;' in slot.markup
        assert '--h:25;' in slot.markup
        assert (
            '<span class="vc-label" data-lang="zh">美国</span>'
            '<span class="vc-label" data-lang="en">美国</span>'
        ) in slot.markup
        assert '<span class="vc-val">100</span>' in slot.markup

    def test_falls_back_to_the_first_series_when_items_are_absent(self):
        slot = render_slot(24, {
            'title': 'T',
            'series': [{'name': 'S', 'values': [10, 20]}],
        })
        assert slot.markup.count('class="vc-bar"') == 2
        assert 'data-lang="zh">1</span>' in slot.markup
        assert 'data-lang="zh">2</span>' in slot.markup
        assert '--h:100;' in slot.markup

    def test_empty_data_renders_an_explicit_empty_state(self):
        slot = render_slot(24, {'title': '没有数据'})
        assert 'ic-empty' in slot.markup
        assert 'vc-bar' not in slot.markup

    def test_negative_value_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(24, {
                'title': 'T',
                'items': [{'label': 'A', 'value': -5}],
            })
        assert exc.value.field == 'items[0].value'


class TestEchartsChart:
    """#26 — the ECharts slot from ticket 01 keeps working, plus empty state."""

    def test_empty_data_renders_an_explicit_empty_state(self):
        slot = render_slot(26, {'title': '没有数据'})
        assert 'data-component="26"' in slot.markup
        assert 'ic-empty' in slot.markup
        assert 'echarts.init' not in slot.markup

    def test_still_renders_a_chart_from_items(self):
        slot = render_slot(26, {
            'title': '单一序列',
            'items': [{'label': 'A', 'value': 1}],
        })
        assert 'echarts.init(' in slot.markup
        assert 'ic-empty' not in slot.markup

    def test_invalid_model_names_the_field(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(26, {'subtitle': 'no title'})
        assert exc.value.field == 'title'


CHART_MODELS = [
    (4, TestCssBarChart.MODEL),
    (15, TestStatusChain.MODEL),
    (19, TestHeatmap.MODEL),
    (20, TestStepIndicator.MODEL),
    (24, TestDataChartSet.MODEL),
    (26, {'title': 'ECharts', 'items': [{'label': 'A', 'value': 3}]}),
]


@pytest.mark.parametrize('component_id, marker', [
    (4, 'bar-item'),
    (15, 'sc-step'),
    (20, 'si-step'),
    (24, 'vc-bar'),
])
def test_series_only_models_render_instead_of_an_empty_state(component_id, marker):
    slot = render_slot(component_id, {
        'title': 'T',
        'series': [{'name': 'S', 'values': [10, 20]}],
    })
    assert slot.markup.count(marker) == 2
    assert 'ic-empty' not in slot.markup



@pytest.mark.parametrize('component_id, model', CHART_MODELS)
def test_every_chart_slot_carries_a_parseable_data_block(component_id, model):
    slot = render_slot(component_id, model)
    assert _data_block_json(slot) == validate_content_model(model).to_dict()


@pytest.mark.parametrize('component_id, model', CHART_MODELS)
def test_every_chart_slot_pairs_with_its_data_block(component_id, model):
    slot = render_slot(component_id, model)
    assert check_slot_data_blocks(slot.fragment) == []


@pytest.mark.parametrize('component_id', [4, 15, 19, 20, 24])
def test_labels_are_html_escaped(component_id):
    model = {
        'title': 'T',
        'items': [{'label': '<script>alert(1)</script>', 'value': 1}],
    }
    slot = render_slot(component_id, model)
    assert '<script>alert(1)</script>' not in slot.markup
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in slot.markup

BILINGUAL_CHART_MODEL = {
    'title': '市场规模',
    'title_en': 'Market size',
    'subtitle': '单位：亿美元',
    'subtitle_en': 'USD 100m',
    'items': [
        {
            'label': '美国', 'label_en': 'United States',
            'value': 80, 'note': '来源：统计局', 'note_en': 'Source: statistics',
            'accent': 'accent',
        },
        {'label': '中国', 'label_en': 'China', 'value': 40},
    ],
    'series': [
        {'name': '纯电', 'name_en': 'BEV', 'values': [50, 30]},
        {'name': '插混', 'name_en': 'PHEV', 'values': [30, 10]},
    ],
}


@pytest.mark.parametrize('component_id', [4, 15, 19, 20, 24, 26])
def test_chart_renderers_pair_english_text(component_id):
    """A bilingual slot swapped to a chart must stay paired in both languages."""
    slot = render_slot(component_id, BILINGUAL_CHART_MODEL)
    assert slot.markup.count('data-lang="zh"') == slot.markup.count('data-lang="en"')
    assert slot.markup.count('data-lang="en"') >= 1
    assert 'United States' in slot.markup


def test_bar_chart_pairs_the_item_label():
    markup = render_slot(4, BILINGUAL_CHART_MODEL).markup
    assert (
        '<div class="bar-label"><span data-lang="zh">美国</span>'
        '<span data-lang="en">United States</span></div>'
    ) in markup


def test_status_chain_pairs_label_and_note():
    markup = render_slot(15, BILINGUAL_CHART_MODEL).markup
    assert (
        '<div class="sc-label"><span data-lang="zh">美国</span>'
        '<span data-lang="en">United States</span></div>'
    ) in markup
    assert (
        '<div class="sc-status"><span data-lang="zh">来源：统计局</span>'
        '<span data-lang="en">Source: statistics</span></div>'
    ) in markup


def test_heatmap_pairs_column_and_row_labels():
    markup = render_slot(19, BILINGUAL_CHART_MODEL).markup
    assert (
        '<div class="hm-hdr"><span data-lang="zh">美国</span>'
        '<span data-lang="en">United States</span></div>'
    ) in markup
    assert (
        '<div class="hm-label"><span data-lang="zh">纯电</span>'
        '<span data-lang="en">BEV</span></div>'
    ) in markup


def test_step_indicator_pairs_the_label():
    markup = render_slot(20, BILINGUAL_CHART_MODEL).markup
    assert (
        '<div class="si-label"><span data-lang="zh">美国</span>'
        '<span data-lang="en">United States</span></div>'
    ) in markup


def test_chart_set_pairs_the_bar_label():
    markup = render_slot(24, BILINGUAL_CHART_MODEL).markup
    assert (
        '<span class="vc-label" data-lang="zh">美国</span>'
        '<span class="vc-label" data-lang="en">United States</span>'
    ) in markup


def test_echarts_carries_english_legend_and_subtitle():
    markup = render_slot(26, BILINGUAL_CHART_MODEL).markup
    assert '"name": "BEV"' in markup
    assert '"subtext": "USD 100m"' in markup
    assert '"subtext": "单位：亿美元"' in markup
    assert '<p data-lang="en">' in markup


@pytest.mark.parametrize('component_id, model', CHART_MODELS)
def test_every_chart_section_has_an_aria_label(component_id, model):
    slot = render_slot(component_id, model)
    assert 'aria-label="' + model['title'] + '"' in slot.markup
