"""Bilingual text on the content model.

Body-text blocks that a component emits must come in zh/en pairs.  The model
therefore carries an optional English counterpart for every human-readable
field.  Empty counterparts are omitted from ``to_dict()`` so the canonical
data block stays identical to the single-language form.
"""

import pytest

from context2html.content_model import ContentModelError, validate_content_model

BILINGUAL = {
    'title': '全球金融危机',
    'title_en': 'Global financial crisis',
    'subtitle': '2007-2009',
    'subtitle_en': '2007-2009',
    'items': [
        {
            'label': '决策者',
            'label_en': 'Decision maker',
            'value': 1,
            'note': '负责战略方向',
            'note_en': 'Owns strategy',
            'accent': '',
        },
    ],
    'series': [
        {'name': '方案 A', 'name_en': 'Option A', 'values': [1]},
    ],
}


class TestBilingualContentModel:
    def test_round_trips_bilingual_fields(self):
        model = validate_content_model(BILINGUAL)
        assert model.title_en == 'Global financial crisis'
        assert model.items[0].label_en == 'Decision maker'
        assert model.items[0].note_en == 'Owns strategy'
        assert model.series[0].name_en == 'Option A'
        assert model.to_dict() == BILINGUAL

    def test_omits_empty_english_fields_from_canonical_form(self):
        model = validate_content_model({'title': '标题'})
        assert model.title_en == ''
        assert model.to_dict() == {
            'title': '标题', 'subtitle': '', 'items': [], 'series': [],
        }

    def test_english_fields_default_to_empty_string(self):
        model = validate_content_model(BILINGUAL)
        assert model.subtitle_en == '2007-2009'
        plain = validate_content_model({'title': 'T', 'items': [{'label': 'A', 'value': 1}]})
        assert plain.items[0].label_en == ''
        assert plain.items[0].note_en == ''

    def test_english_field_must_be_a_string(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({'title': 'T', 'title_en': 3})
        assert exc.value.field == 'title_en'

    def test_item_english_label_must_be_a_string(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T',
                'items': [{'label': 'A', 'value': 1, 'label_en': 2}],
            })
        assert exc.value.field == 'items[0].label_en'
