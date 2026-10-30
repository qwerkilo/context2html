"""Tests for slot rendering: one content model in, markup + data block out."""

import json
import os

import pytest

from context2html.content_model import ContentModelError, validate_content_model
from context2html.slots import SlotError, render_slot

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


def _fixture(name):
    with open(os.path.join(FIXTURES, name), 'r', encoding='utf-8') as fh:
        return fh.read()


MODEL_DATA = json.loads(_fixture('slot-26-model.json'))


def _data_block_json(slot):
    opening, rest = slot.data_block.split('>', 1)
    body, _ = rest.rsplit('</script>', 1)
    return json.loads(body)


class TestSlotRenderer:
    def test_renders_markup_and_data_block_in_one_call(self):
        slot = render_slot(26, MODEL_DATA)
        assert slot.component_id == 26
        assert slot.slot_id.startswith('slot-26-')
        assert f'data-slot="{slot.slot_id}"' in slot.markup
        assert 'data-component="26"' in slot.markup
        assert 'echarts.init(' in slot.markup
        assert f'data-slot="{slot.slot_id}"' in slot.data_block
        assert _data_block_json(slot) == validate_content_model(MODEL_DATA).to_dict()

    def test_slot_id_is_stable_for_same_model(self):
        first = render_slot(26, MODEL_DATA)
        second = render_slot(26, MODEL_DATA)
        assert first.slot_id == second.slot_id
        assert first.markup == second.markup

    def test_slot_id_changes_when_data_changes(self):
        changed = dict(MODEL_DATA, title='另一个标题')
        assert render_slot(26, MODEL_DATA).slot_id != render_slot(26, changed).slot_id

    def test_explicit_slot_id_overrides_derived_id(self):
        slot = render_slot(26, MODEL_DATA, slot_id='ev-sales')
        assert slot.slot_id == 'ev-sales'
        assert 'data-slot="ev-sales"' in slot.markup
        assert 'data-slot="ev-sales"' in slot.data_block

    def test_rejects_unsafe_explicit_slot_id(self):
        with pytest.raises(SlotError):
            render_slot(26, MODEL_DATA, slot_id='x" onload="alert(1)')

    def test_rejects_unsupported_component(self):
        with pytest.raises(SlotError, match='99'):
            render_slot(99, MODEL_DATA)

    def test_rejects_invalid_content_model(self):
        with pytest.raises(ContentModelError) as exc:
            render_slot(26, {'subtitle': 'no title'})
        assert exc.value.field == 'title'

    def test_accepts_a_validated_model(self):
        model = validate_content_model(MODEL_DATA)
        slot = render_slot(26, model)
        assert slot.slot_id == render_slot(26, MODEL_DATA).slot_id

    def test_renders_single_series_from_items(self):
        slot = render_slot(26, {
            'title': '单一序列',
            'items': [{'label': 'A', 'value': 1}, {'label': 'B', 'value': 2}],
        })
        assert '"type": "bar"' in slot.markup
        assert '"name": "单一序列"' in slot.markup
        assert '"stack": "total"' not in slot.markup
        assert '"A"' in slot.markup and '"B"' in slot.markup

    def test_golden_fixture_markup_and_data_block(self):
        slot = render_slot(26, MODEL_DATA)
        assert slot.fragment == _fixture('slot-26.golden.html')

    def test_golden_data_block_parses_back_to_original_model(self):
        slot = render_slot(26, MODEL_DATA)
        assert _data_block_json(slot) == MODEL_DATA
