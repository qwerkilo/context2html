"""Structure-family renderers: fixed content model in, expected structure out.

Each component is rendered through the ticket-01 slot mechanism, so every test
also checks that the markup carries ``data-slot``/``data-component`` and that
the bilingual pairs it emits stay balanced.
"""

from html.parser import HTMLParser


import pytest

from context2html.content_model import ContentModelError
from context2html.registry import ComponentRegistry
from context2html.slots import render_slot

VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
}


class _TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'unexpected </{tag}> with open {self.stack[-3:]}')
            return
        self.stack.pop()


def assert_well_formed(markup):
    parser = _TagBalance()
    parser.feed(markup)
    parser.close()
    assert parser.errors == []
    assert parser.stack == []


def assert_balanced_languages(markup):
    assert markup.count('data-lang="zh"') == markup.count('data-lang="en"')


DATA_CARDS = {
    'title': '关键数据',
    'items': [
        {
            'label': '全球财富蒸发',
            'label_en': 'Global wealth lost',
            'value': 8.8,
            'note': '万亿美元',
            'note_en': 'trillion USD',
            'accent': '',
        },
        {
            'label': '倒闭银行数',
            'label_en': 'Banks failed',
            'value': 127,
            'note': '家',
            'note_en': 'banks',
            'accent': '',
        },
    ],
}


class TestDataCardGrid:
    def test_renders_one_card_per_item(self):
        slot = render_slot(12, DATA_CARDS)
        assert slot.component_id == 12
        assert 'class="data-grid"' in slot.markup
        assert slot.markup.count('class="dg-card"') == 2
        assert f'data-slot="{slot.slot_id}"' in slot.markup
        assert 'data-component="12"' in slot.markup

    def test_renders_value_unit_and_label(self):
        markup = render_slot(12, DATA_CARDS).markup
        assert '<div class="dg-value">8.8</div>' in markup
        assert '<div class="dg-value">127</div>' in markup
        assert '<div class="dg-unit" data-lang="zh">万亿美元</div>' in markup
        assert '<div class="dg-unit" data-lang="en">trillion USD</div>' in markup
        assert '<div class="dg-label" data-lang="zh">倒闭银行数</div>' in markup
        assert '<div class="dg-label" data-lang="en">Banks failed</div>' in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(12, {'title': '空'}).markup
        assert 'dg-card' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(12, DATA_CARDS).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_escapes_model_text(self):
        markup = render_slot(12, {
            'title': 'T',
            'items': [{'label': '<b>not bold</b>', 'value': 1}],
        }).markup
        assert '<b>not bold</b>' not in markup
        assert '&lt;b&gt;not bold&lt;/b&gt;' in markup

    def test_missing_english_falls_back_to_the_chinese_text(self):
        markup = render_slot(12, {
            'title': 'T',
            'items': [{'label': '只有中文', 'value': 1}],
        }).markup
        assert '<div class="dg-label" data-lang="zh">只有中文</div>' in markup
        assert '<div class="dg-label" data-lang="en">只有中文</div>' in markup


ROLE_CARDS = {
    'title': '参与角色',
    'items': [
        {
            'label': '决策者',
            'label_en': 'Decision maker',
            'value': 1,
            'note': '负责战略方向与投资决策',
            'note_en': 'Owns strategy and investment decisions',
            'accent': '',
        },
        {
            'label': '执行者',
            'label_en': 'Executor',
            'value': 2,
            'note': '负责落地实施与日常运营',
            'note_en': 'Owns delivery and daily operations',
            'accent': '',
        },
    ],
}


class TestRoleCards:
    def test_renders_one_card_per_item(self):
        slot = render_slot(2, ROLE_CARDS)
        assert slot.component_id == 2
        assert 'class="role-grid"' in slot.markup
        assert slot.markup.count('class="role-card"') == 2
        assert 'data-component="2"' in slot.markup

    def test_header_cycles_the_semantic_palette(self):
        markup = render_slot(2, ROLE_CARDS).markup
        assert 'style="background:#3b82f6;color:#fff"' in markup
        assert 'style="background:#f59e0b;color:#fff"' in markup

    def test_accent_overrides_the_header_colour(self):
        markup = render_slot(2, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 1, 'accent': '#123456'}],
        }).markup
        assert 'style="background:#123456;color:#fff"' in markup

    def test_unsafe_accent_falls_back_to_the_palette(self):
        markup = render_slot(2, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 1, 'accent': 'red;background:url(x)'}],
        }).markup
        assert 'red;background' not in markup
        assert 'style="background:#3b82f6;color:#fff"' in markup

    def test_note_becomes_a_bilingual_body_paragraph(self):
        markup = render_slot(2, ROLE_CARDS).markup
        assert '<p data-lang="zh">负责战略方向与投资决策</p>' in markup
        assert (
            '<p data-lang="en">Owns strategy and investment decisions</p>' in markup)

    def test_card_without_note_has_no_empty_body(self):
        markup = render_slot(2, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 1}],
        }).markup
        assert 'role-body' not in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(2, {'title': '空'}).markup
        assert 'role-grid' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(2, ROLE_CARDS).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


TIMELINE = {
    'title': '危机时间线',
    'items': [
        {
            'label': '2008 年 9 月',
            'label_en': 'September 2008',
            'value': 2008.75,
            'note': '雷曼兄弟破产',
            'note_en': 'Lehman Brothers collapses',
            'accent': '#ef4444',
        },
        {
            'label': '2006 年中',
            'label_en': 'Mid 2006',
            'value': 2006.5,
            'note': '房价见顶',
            'note_en': 'Housing prices peak',
            'accent': '',
        },
        {
            'label': '2009 年初',
            'label_en': 'Early 2009',
            'value': 2009.0,
            'note': '大规模刺激计划',
            'note_en': 'Large stimulus package',
            'accent': '',
        },
    ],
}


class TestTimeline:
    def test_renders_one_item_per_event_in_value_order(self):
        markup = render_slot(3, TIMELINE).markup
        assert 'class="timeline"' in markup
        assert markup.count('class="tl-item"') == 3
        first = markup.index('Mid 2006')
        second = markup.index('September 2008')
        third = markup.index('Early 2009')
        assert first < second < third

    def test_accent_marks_a_major_milestone_and_colours_the_dot(self):
        markup = render_slot(3, TIMELINE).markup
        assert markup.count('class="tl-dot major"') == 1
        assert 'class="tl-dot major" style="background:#ef4444"' in markup
        assert markup.count('class="tl-dot"') == 2

    def test_date_and_description_are_bilingual(self):
        markup = render_slot(3, TIMELINE).markup
        assert '<div class="tl-date" data-lang="zh">2008 年 9 月</div>' in markup
        assert '<div class="tl-date" data-lang="en">September 2008</div>' in markup
        assert '<div class="tl-desc" data-lang="zh">雷曼兄弟破产</div>' in markup
        assert '<div class="tl-desc" data-lang="en">Lehman Brothers collapses</div>' in markup

    def test_event_without_note_omits_the_description(self):
        markup = render_slot(3, {
            'title': 'T',
            'items': [{'label': '2000', 'value': 2000}],
        }).markup
        assert 'tl-desc' not in markup
        assert 'tl-date' in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(3, {'title': '空'}).markup
        assert 'class="timeline"' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(3, TIMELINE).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


COMPARISON = {
    'title': '方案对比',
    'subtitle': '数据来源：团队评估（2026）',
    'subtitle_en': 'Source: team assessment (2026)',
    'items': [
        {'label': '成本', 'label_en': 'Cost', 'value': 0},
        {'label': '速度', 'label_en': 'Speed', 'value': 0},
    ],
    'series': [
        {'name': '方案 A', 'name_en': 'Option A', 'values': [1, 2]},
        {'name': '方案 B', 'name_en': 'Option B', 'values': [3, 4]},
    ],
}


class TestComparisonTable:
    def test_series_become_columns_and_items_become_rows(self):
        markup = render_slot(5, COMPARISON).markup
        assert '<table class="cmp-table">' in markup
        assert markup.count('<tr>') == 3  # header row + two data rows
        assert (
            '<th><span data-lang="zh">方案 A</span>'
            '<span data-lang="en">Option A</span></th>') in markup
        assert (
            '<td data-label="维度"><span data-lang="zh">成本</span>'
            '<span data-lang="en">Cost</span></td>') in markup
        assert '<td data-label="方案 A">1</td>' in markup
        assert '<td data-label="方案 B">4</td>' in markup

    def test_without_series_falls_back_to_label_value_columns(self):
        markup = render_slot(5, {
            'title': 'T',
            'items': [{'label': '成本', 'value': 12}],
        }).markup
        assert '<td data-label="数值">12</td>' in markup
        assert markup.count('<th>') == 2

    def test_subtitle_becomes_a_bilingual_caption(self):
        markup = render_slot(5, COMPARISON).markup
        assert (
            '<p class="cmp-caption" data-lang="zh">数据来源：团队评估（2026）</p>'
            in markup)
        assert (
            '<p class="cmp-caption" data-lang="en">Source: team assessment (2026)</p>'
            in markup)

    def test_without_subtitle_there_is_no_caption(self):
        markup = render_slot(5, {'title': 'T', 'items': [{'label': 'A', 'value': 1}]}).markup
        assert 'cmp-caption' not in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(5, {'title': '空'}).markup
        assert '<table' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(5, COMPARISON).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


class TestEnhancedComparisonTable:
    def test_wraps_the_table_for_horizontal_overflow(self):
        markup = render_slot(22, COMPARISON).markup
        assert '<div class="cmp-wrap" data-anim="fade-up">' in markup
        assert '<table class="cmp-table" data-sortable id="cmp-' in markup
        assert markup.count('<tr>') == 3

    def test_headers_are_sortable_and_labelled(self):
        markup = render_slot(22, COMPARISON).markup
        assert '<th data-sort><span data-lang="zh">维度</span>' in markup
        assert markup.count('class="cmp-arrow"') == 3
        assert (
            '<th data-sort><span data-lang="zh">方案 A</span>'
            '<span data-lang="en">Option A</span>') in markup

    def test_sort_script_is_scoped_to_this_slot(self):
        slot = render_slot(22, COMPARISON)
        assert f'id="cmp-{slot.slot_id}"' in slot.markup
        assert f'getElementById("cmp-{slot.slot_id}")' in slot.markup
        assert "querySelectorAll('th[data-sort]')" in slot.markup

    def test_rows_carry_the_same_data_as_the_basic_table(self):
        markup = render_slot(22, COMPARISON).markup
        assert '<td data-label="方案 A">1</td>' in markup
        assert '<td data-label="方案 B">4</td>' in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(22, {'title': '空'}).markup
        assert '<table' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(22, COMPARISON).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


class TestQuoteCard:
    def test_single_quote_comes_from_title_and_subtitle(self):
        markup = render_slot(13, {
            'title': '这不仅仅是一场金融危机，更是一次结构性转型。',
            'title_en': 'This is more than a crisis; it is a structural shift.',
            'subtitle': '斯蒂格利茨《全球化及其不满》，2002',
            'subtitle_en': 'Stiglitz, Globalization and Its Discontents, 2002',
        }).markup
        assert '<div class="quote-card" data-anim="fade-up">' in markup
        assert '<div class="qc-bar"></div>' in markup
        assert (
            '<p class="qc-text" data-lang="zh">'
            '这不仅仅是一场金融危机，更是一次结构性转型。</p>') in markup
        assert (
            '<p class="qc-text" data-lang="en">'
            'This is more than a crisis; it is a structural shift.</p>') in markup
        assert (
            '<span class="qc-title" data-lang="zh">'
            '斯蒂格利茨《全球化及其不满》，2002</span>') in markup

    def test_items_render_one_card_per_quote(self):
        markup = render_slot(13, {
            'title': '引文',
            'items': [
                {'label': '引文一', 'label_en': 'Quote one', 'value': 1,
                 'note': '甲', 'note_en': 'A'},
                {'label': '引文二', 'label_en': 'Quote two', 'value': 2,
                 'note': '乙', 'note_en': 'B'},
            ],
        }).markup
        assert markup.count('class="quote-card"') == 2
        assert '<p class="qc-text" data-lang="zh">引文一</p>' in markup
        assert '<p class="qc-text" data-lang="en">Quote two</p>' in markup
        assert '<span class="qc-title" data-lang="zh">甲</span>' in markup

    def test_quote_without_attribution_omits_the_source_line(self):
        markup = render_slot(13, {'title': '一句话'}).markup
        assert 'qc-source' not in markup
        assert 'qc-text' in markup

    def test_empty_item_list_means_single_quote_not_empty_state(self):
        markup = render_slot(13, {'title': '一句话'}).markup
        assert 'class="ic-empty"' not in markup
        assert 'quote-card' in markup

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(13, {
            'title': '引文',
            'items': [{'label': '甲', 'value': 1, 'note': '乙'}],
        }).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


TAGS = {
    'title': '关键词',
    'items': [
        {'label': '宏观经济', 'label_en': 'Macroeconomics', 'value': 0, 'accent': 'blue'},
        {'label': '金融危机', 'label_en': 'Financial crisis', 'value': 0, 'accent': 'red'},
        {'label': '政策应对', 'label_en': 'Policy response', 'value': 0, 'accent': 'purple'},
        {'label': '#监管改革', 'label_en': '#Regulatory reform', 'value': 0, 'accent': ''},
    ],
}


class TestTagGroup:
    def test_renders_one_tag_per_item(self):
        markup = render_slot(17, TAGS).markup
        assert 'class="tag-group" data-anim="fade-up"' in markup
        assert markup.count('<span class="tag ') == 8  # 4 tags x 2 languages

    def test_every_tag_has_the_hash_prefix(self):
        markup = render_slot(17, TAGS).markup
        assert '<span class="tag tag-blue" data-lang="zh"># 宏观经济</span>' in markup
        assert '<span class="tag tag-orange" data-lang="zh">#监管改革</span>' in markup

    def test_accent_names_select_the_palette_class(self):
        markup = render_slot(17, TAGS).markup
        assert 'class="tag tag-blue"' in markup
        assert 'class="tag tag-red"' in markup
        assert 'class="tag tag-purple"' in markup

    def test_unknown_accent_cycles_the_palette(self):
        markup = render_slot(17, {
            'title': 'T',
            'items': [
                {'label': 'A', 'value': 0, 'accent': '#123456'},
                {'label': 'B', 'value': 0, 'accent': ''},
            ],
        }).markup
        assert 'class="tag tag-blue"' in markup
        assert 'class="tag tag-red"' in markup

    def test_labels_are_bilingual(self):
        markup = render_slot(17, TAGS).markup
        assert '<span class="tag tag-blue" data-lang="en"># Macroeconomics</span>' in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(17, {'title': '空'}).markup
        assert 'tag-group' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(17, TAGS).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_tag_list_without_values_renders(self):
        slot = render_slot(17, {
            'title': '关键词',
            'items': [{'label': '宏观经济'}, {'label': '金融危机'}],
        })
        assert slot.markup.count('<span class="tag ') == 4
        assert '# 宏观经济' in slot.markup
        assert '"value"' not in slot.data_block


CALLOUTS = {
    'title': '提示',
    'items': [
        {'label': '一般提示信息', 'label_en': 'General note', 'value': 0,
         'note': '补充报告背景', 'note_en': 'Adds report context', 'accent': 'info'},
        {'label': '需要注意的风险', 'label_en': 'A risk to watch', 'value': 0,
         'accent': 'warning'},
        {'label': '操作失败', 'label_en': 'Operation failed', 'value': 0,
         'accent': 'error'},
        {'label': '恢复完成', 'label_en': 'Recovery complete', 'value': 0,
         'accent': 'success'},
        {'label': '未指定类型', 'label_en': 'No type given', 'value': 0,
         'accent': ''},
    ],
}


class TestCalloutBars:
    def test_renders_one_callout_per_item(self):
        markup = render_slot(18, CALLOUTS).markup
        assert markup.count('class="callout callout-') == 5
        assert 'data-anim="fade-up"' in markup

    def test_accent_selects_the_callout_type_and_icon(self):
        markup = render_slot(18, CALLOUTS).markup
        assert '<div class="callout callout-info" data-anim="fade-up">' in markup
        assert '<div class="callout callout-warning" data-anim="fade-up">' in markup
        assert '<div class="callout callout-error" data-anim="fade-up">' in markup
        assert '<div class="callout callout-success" data-anim="fade-up">' in markup
        assert '<div class="callout-icon">💡</div>' in markup
        assert '<div class="callout-icon">⚠️</div>' in markup
        assert '<div class="callout-icon">❌</div>' in markup
        assert '<div class="callout-icon">✅</div>' in markup

    def test_unknown_accent_falls_back_to_info(self):
        markup = render_slot(18, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 0, 'accent': 'nonsense'}],
        }).markup
        assert 'class="callout callout-info"' in markup
        assert '<div class="callout-icon">💡</div>' in markup

    def test_body_text_is_bilingual_and_note_adds_a_second_paragraph(self):
        markup = render_slot(18, CALLOUTS).markup
        assert (
            '<div class="callout-body">'
            '<p data-lang="zh">一般提示信息</p>'
            '<p data-lang="en">General note</p>'
            '<p data-lang="zh">补充报告背景</p>'
            '<p data-lang="en">Adds report context</p>'
            '</div>') in markup

    def test_empty_items_render_empty_state(self):
        markup = render_slot(18, {'title': '空'}).markup
        assert 'class="callout ' not in markup
        assert 'class="ic-empty"' in markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)

    def test_markup_is_well_formed_and_bilingual(self):
        markup = render_slot(18, CALLOUTS).markup
        assert_well_formed(markup)
        assert_balanced_languages(markup)


STRUCTURE_IDS = {2, 3, 5, 12, 13, 17, 18, 22}


class TestSwappableSetFlag:
    def test_structure_components_declare_the_flag_in_their_front_matter(self):
        registry = ComponentRegistry()
        flagged = {c.id for c in registry.list_components(content_model=True)}
        assert STRUCTURE_IDS <= flagged

    def test_non_structure_components_are_not_flagged(self):
        registry = ComponentRegistry()
        for component_id in (1, 27, 30):
            component = registry.list_components(id=component_id)[0]
            assert component.metadata.content_model is False

    def test_registry_reads_the_flag_from_component_front_matter(self, tmp_path):
        (tmp_path / '01-demo.md').write_text(
            '---\nid: 99\nname: Demo\ncontent_model: true\n---\n\nbody\n',
            encoding='utf-8')
        (tmp_path / '02-plain.md').write_text(
            '---\nid: 98\nname: Plain\n---\n\nbody\n', encoding='utf-8')
        registry = ComponentRegistry(str(tmp_path))
        flags = {c.id: c.metadata.content_model for c in registry.list_components()}
        assert flags == {99: True, 98: False}

    def test_every_structure_component_renders_from_a_minimal_model(self):
        for component_id in sorted(STRUCTURE_IDS):
            slot = render_slot(component_id, {'title': 'T'})
            assert f'data-component="{component_id}"' in slot.markup








ITEMS_ONLY_IDS = [2, 3, 5, 12, 17, 18, 22]


@pytest.mark.parametrize('component_id', ITEMS_ONLY_IDS)
def test_items_component_rejects_series_only_data(component_id):
    """A component that needs items must fail loudly instead of showing empty."""
    with pytest.raises(ContentModelError) as exc:
        render_slot(component_id, {
            'title': 'T',
            'series': [{'name': 'S', 'values': [1, 2]}],
        })
    assert exc.value.field == 'items'
    assert 'items' in str(exc.value)


VALUE_FREE_IDS = [2, 13, 17, 18]


@pytest.mark.parametrize('component_id', VALUE_FREE_IDS)
def test_value_free_components_render_value_less_items(component_id):
    slot = render_slot(component_id, {
        'title': 'T',
        'items': [{'label': 'A'}, {'label': 'B'}],
    })
    assert 'ic-empty' not in slot.markup
    assert '"value"' not in slot.data_block


@pytest.mark.parametrize('component_id', [5, 22])
def test_comparison_table_rejects_value_less_items_without_series(component_id):
    with pytest.raises(ContentModelError) as exc:
        render_slot(component_id, {
            'title': 'T',
            'items': [{'label': 'A'}],
        })
    assert exc.value.field == 'items[0].value'
    assert 'missing field' in str(exc.value)


@pytest.mark.parametrize('component_id', [5, 22])
def test_comparison_table_accepts_value_less_items_when_series_supply_numbers(
        component_id):
    slot = render_slot(component_id, {
        'title': 'T',
        'items': [{'label': 'A'}],
        'series': [{'name': 'S', 'values': [1]}],
    })
    assert '<td data-label="S">1</td>' in slot.markup


@pytest.mark.parametrize('component_id', [3, 12])
def test_item_value_component_rejects_value_less_items_even_with_series(component_id):
    with pytest.raises(ContentModelError) as exc:
        render_slot(component_id, {
            'title': 'T',
            'items': [{'label': 'A'}],
            'series': [{'name': 'S', 'values': [1]}],
        })
    assert exc.value.field == 'items[0].value'
    assert 'missing field' in str(exc.value)


def test_names_the_first_item_without_a_value():
    with pytest.raises(ContentModelError) as exc:
        render_slot(12, {
            'title': 'T',
            'items': [{'label': 'A', 'value': 1}, {'label': 'B'}],
        })
    assert exc.value.field == 'items[1].value'
