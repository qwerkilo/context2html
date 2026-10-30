"""Pure editor logic: candidate filtering, mapping preview and undo history.

The DOM wiring is deliberately thin; everything a swap decides is decided by
``runtime/editor-core.js``.  These tests drive that module through node, the
same way the parity harness drives the renderer.
"""

import json
import os
import shutil
import subprocess

import pytest

from context2html.registry import ComponentRegistry

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, 'scripts', 'js', 'editor-core-runner.js')

CHART_IDS = [4, 15, 19, 20, 24, 26]
STRUCTURE_IDS = [2, 3, 5, 12, 13, 17, 18, 22]
ALL_IDS = STRUCTURE_IDS + CHART_IDS

SERIES_MODEL = {
    'title': '季度销量',
    'series': [
        {'name': '直营', 'values': [10, 20, 30]},
        {'name': '经销', 'values': [5, 8, 13]},
    ],
}

ITEMS_MODEL = {
    'title': '渠道销量',
    'items': [
        {'label': '直营', 'value': 120, 'note': '一线城市', 'accent': 'accent'},
        {'label': '经销', 'value': 80},
    ],
}

BOTH_MODEL = {
    'title': '渠道销量',
    'subtitle': '按季度',
    'items': [
        {'label': '直营', 'value': 120, 'note': '一线城市', 'accent': 'accent'},
        {'label': '经销', 'value': 80},
    ],
    'series': [
        {'name': '一季度', 'values': [60, 40]},
        {'name': '二季度', 'values': [60, 40]},
    ],
}


def _node():
    executable = os.environ.get('NODE') or shutil.which('node')
    if not executable:
        pytest.skip('node executable not found; install node or set NODE')
    return executable


def call(op, *args):
    """Invoke one editor-core function and return its decoded result."""
    result = subprocess.run(
        [_node(), RUNNER],
        input=json.dumps({'op': op, 'args': list(args)}),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def ids(candidates):
    return [candidate['id'] for candidate in candidates]


class TestSlotShape:
    def test_series_slot_is_a_series_slot(self):
        assert call('slotShape', SERIES_MODEL) == 'series'

    def test_items_slot_is_an_items_slot(self):
        assert call('slotShape', ITEMS_MODEL) == 'items'

    def test_items_and_series_lead_with_series(self):
        assert call('slotShape', BOTH_MODEL) == 'series'

    def test_model_without_data_is_empty(self):
        assert call('slotShape', {'title': '空'}) == 'empty'


class TestCandidateFiltering:
    def test_series_slot_leads_with_chart_family(self):
        candidates = call('candidatesFor', SERIES_MODEL, 26)
        result_ids = ids(candidates)
        assert set(CHART_IDS) - {26} <= set(result_ids)
        assert result_ids[:len(CHART_IDS) - 1] == [4, 15, 19, 20, 24]
        assert [c['sameFamily'] for c in candidates[:5]] == [True] * 5

    def test_series_slot_excludes_components_that_need_items(self):
        result_ids = ids(call('candidatesFor', SERIES_MODEL, 26))
        for component_id in (2, 3, 5, 12, 17, 18, 22):
            assert component_id not in result_ids

    def test_series_slot_keeps_the_quote_card_as_a_cross_family_option(self):
        candidates = call('candidatesFor', SERIES_MODEL, 26)
        quote = [c for c in candidates if c['id'] == 13]
        assert len(quote) == 1
        assert quote[0]['sameFamily'] is False
        assert quote[0]['family'] == 'structure'

    def test_items_slot_rendered_by_a_chart_leads_with_the_chart_family(self):
        candidates = call('candidatesFor', ITEMS_MODEL, 4)
        assert ids(candidates)[:5] == [15, 19, 20, 24, 26]
        assert [c['sameFamily'] for c in candidates[:5]] == [True] * 5
        assert all(c['sameFamily'] is False for c in candidates[5:])

    def test_items_slot_rendered_by_a_structure_component_leads_with_structure(self):
        candidates = call('candidatesFor', ITEMS_MODEL, 2)
        assert ids(candidates)[:7] == [3, 5, 12, 13, 17, 18, 22]
        assert [c['sameFamily'] for c in candidates[:7]] == [True] * 7
        assert ids(candidates)[7:] == [4, 15, 19, 20, 24, 26]

    def test_both_slot_rendered_by_a_structure_component_leads_with_structure(self):
        candidates = call('candidatesFor', BOTH_MODEL, 13)
        assert ids(candidates)[:7] == [2, 3, 5, 12, 17, 18, 22]
        assert ids(candidates)[7:] == [4, 15, 19, 20, 24, 26]

    def test_items_slot_offers_every_component_that_can_read_items(self):
        result_ids = ids(call('candidatesFor', ITEMS_MODEL, 4))
        assert set(result_ids) == set(ALL_IDS) - {4}

    def test_current_component_is_not_a_candidate(self):
        for model in (SERIES_MODEL, ITEMS_MODEL, BOTH_MODEL):
            for component_id in ALL_IDS:
                assert component_id not in ids(call('candidatesFor', model, component_id))

    def test_negative_values_exclude_bar_renderers(self):
        model = {
            'title': '盈亏',
            'items': [
                {'label': 'A', 'value': 10},
                {'label': 'B', 'value': -3},
            ],
        }
        result_ids = ids(call('candidatesFor', model, 3))
        assert 4 not in result_ids
        assert 24 not in result_ids
        assert 19 in result_ids

    def test_empty_model_only_offers_the_quote_card(self):
        assert ids(call('candidatesFor', {'title': '只有标题'}, 4)) == [13]

    def test_every_candidate_is_unique_and_known(self):
        candidates = call('candidatesFor', BOTH_MODEL, 26)
        result_ids = ids(candidates)
        assert len(result_ids) == len(set(result_ids))
        assert set(result_ids) <= set(ALL_IDS)
        assert all(candidate['name'] for candidate in candidates)

class TestMappingPreview:
    def test_cross_family_preview_names_what_is_shown_and_dropped(self):
        preview = call('mappingPreview', 4, 12, BOTH_MODEL)
        assert preview['crossFamily'] is True
        assert preview['from'] == {'id': 4, 'name': 'CSS 条形图', 'family': 'chart'}
        assert preview['to'] == {'id': 12, 'name': '数据卡片网格', 'family': 'structure'}
        assert preview['displays'] == ['条目标签', '条目数值', '条目备注', '强调色']
        assert preview['drops'] == ['标题', '副标题', '系列名称', '系列数值']
        assert '新组件显示' in preview['summary']
        assert '将丢弃' in preview['summary']

    def test_same_family_preview_still_reports_the_mapping(self):
        preview = call('mappingPreview', 4, 26, BOTH_MODEL)
        assert preview['crossFamily'] is False
        assert preview['displays'] == ['标题', '副标题', '条目标签', '系列名称', '系列数值']
        assert preview['drops'] == ['条目数值', '条目备注', '强调色']

    def test_preview_marks_item_values_used_only_for_ordering(self):
        preview = call('mappingPreview', 4, 3, BOTH_MODEL)
        assert '条目数值（排序依据）' in preview['displays']
        assert '条目备注' in preview['displays']
        assert '系列数值' in preview['drops']
        assert '标题' in preview['drops']

    def test_preview_marks_item_values_used_for_progress_state(self):
        preview = call('mappingPreview', 12, 15, ITEMS_MODEL)
        assert '条目数值（进度状态）' in preview['displays']

    def test_preview_drops_the_second_series_when_only_the_first_is_read(self):
        preview = call('mappingPreview', 13, 4, SERIES_MODEL)
        assert preview['displays'] == ['系列数值']
        assert preview['drops'] == ['标题', '系列名称', '第 2 条及之后的系列']

    def test_preview_of_a_table_reads_series_as_columns(self):
        preview = call('mappingPreview', 4, 5, BOTH_MODEL)
        assert preview['displays'] == [
            '副标题', '条目标签', '系列名称', '系列数值']
        assert preview['drops'] == ['标题', '条目数值', '条目备注', '强调色']

    def test_preview_of_the_quote_card_keeps_labels_and_notes(self):
        preview = call('mappingPreview', 4, 13, ITEMS_MODEL)
        assert preview['displays'] == ['条目标签', '条目备注']
        assert preview['drops'] == ['标题', '条目数值', '强调色']

    def test_preview_with_nothing_to_drop_says_so(self):
        preview = call('mappingPreview', 13, 13, {'title': '只有标题'})
        assert preview['drops'] == []
        assert '无' in preview['summary']

    def test_preview_drops_a_title_the_target_only_uses_as_a_label(self):
        preview = call('mappingPreview', 4, 12, ITEMS_MODEL)
        assert '标题' in preview['drops']
        assert '标题' not in preview['displays']

    def test_preview_of_a_quote_card_without_items_shows_the_title(self):
        preview = call('mappingPreview', 4, 13, {'title': '只有标题'})
        assert preview['displays'] == ['标题']
        assert preview['drops'] == []


class TestUndoHistory:
    def test_initial_history_has_nothing_to_undo(self):
        history = call('createHistory')
        assert call('canUndo', history) is False
        assert call('undo', history) is None

    def test_history_records_multiple_patches_in_order(self):
        history = call('createHistory')
        first = {'slotId': 'a', 'from': 4, 'to': 26}
        second = {'slotId': 'b', 'from': 3, 'to': 12}
        third = {'slotId': 'a', 'from': 26, 'to': 5}
        history = call('recordPatch', history, first)
        history = call('recordPatch', history, second)
        history = call('recordPatch', history, third)
        assert call('canUndo', history) is True

        result = call('undo', history)
        assert result['patch'] == third
        result = call('undo', result['history'])
        assert result['patch'] == second
        result = call('undo', result['history'])
        assert result['patch'] == first
        assert call('canUndo', result['history']) is False
        assert call('undo', result['history']) is None

    def test_recording_a_patch_does_not_mutate_the_previous_history(self):
        history = call('createHistory')
        call('recordPatch', history, {'slotId': 'a', 'from': 4, 'to': 26})
        assert call('canUndo', history) is False


class TestEditableFlag:
    def test_true_and_bare_attribute_enable_the_editor(self):
        assert call('isEditableFlag', 'true') is True
        assert call('isEditableFlag', '') is True

    def test_missing_or_false_flag_keeps_the_editor_off(self):
        assert call('isEditableFlag', None) is False
        assert call('isEditableFlag', 'false') is False

    def test_catalog_has_the_fourteen_components_in_two_families(self):
        assert call('componentIds') == sorted(ALL_IDS)
        for component_id in CHART_IDS:
            assert call('familyOf', component_id) == 'chart'
        for component_id in STRUCTURE_IDS:
            assert call('familyOf', component_id) == 'structure'
        assert call('familyOf', 1) is None

    def test_cross_family_flag_is_relative_to_the_current_component(self):
        by_id = {c['id']: c for c in call('candidatesFor', ITEMS_MODEL, 4)}
        assert by_id[15]['crossFamily'] is False
        assert by_id[26]['crossFamily'] is False
        assert by_id[2]['crossFamily'] is True

    def test_first_series_must_hold_values_for_entry_based_charts(self):
        model = {
            'title': '空首系列',
            'series': [
                {'name': '空', 'values': []},
                {'name': '有数据', 'values': [1, 2]},
            ],
        }
        result_ids = ids(call('candidatesFor', model, 3))
        for component_id in (4, 15, 20, 24):
            assert component_id not in result_ids
        assert 19 in result_ids
        assert 26 in result_ids

    def test_no_values_at_all_only_offers_the_quote_card(self):
        model = {'title': '空系列', 'series': [{'name': '空', 'values': []}]}
        assert ids(call('candidatesFor', model, 3)) == [13]

    def test_editor_catalog_matches_the_registry_ids_and_names(self):
        expected = {
            comp.id: comp.metadata.name
            for comp in ComponentRegistry().list_components(content_model=True)
        }
        candidates = call('candidatesFor', ITEMS_MODEL, 1)
        assert {candidate['id']: candidate['name'] for candidate in candidates} == expected
