"""Tests for the authoritative content model and its validator."""

import json
import os

import pytest

from context2html.content_model import (
    ContentModel,
    ContentModelError,
    validate_content_model,
)

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


def _fixture(name):
    with open(os.path.join(FIXTURES, name), 'r', encoding='utf-8') as fh:
        return json.load(fh)


FULL_MODEL = _fixture('slot-26-model.json')


class TestContentModelValidation:
    def test_accepts_minimal_model(self):
        model = validate_content_model({'title': 'A chart'})
        assert isinstance(model, ContentModel)
        assert model.title == 'A chart'
        assert model.to_dict() == {
            'title': 'A chart', 'subtitle': '', 'items': [], 'series': [],
        }

    def test_preserves_full_model(self):
        model = validate_content_model(FULL_MODEL)
        assert model.to_dict() == FULL_MODEL

    def test_missing_title_names_field(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({'subtitle': 'no title'})
        assert exc.value.field == 'title'
        assert 'missing field' in str(exc.value)

    def test_title_must_be_non_empty_string(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({'title': '   '})
        assert exc.value.field == 'title'

    def test_subtitle_must_be_string(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({'title': 'T', 'subtitle': 3})
        assert exc.value.field == 'subtitle'

    def test_missing_item_label_names_field(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'items': [{'value': 1}],
            })
        assert exc.value.field == 'items[0].label'

    def test_item_value_is_optional(self):
        model = validate_content_model({
            'title': 'T', 'items': [{'label': 'A'}, {'label': 'B'}],
        })
        assert [item.value for item in model.items] == [None, None]
        assert model.to_dict()['items'] == [
            {'label': 'A', 'note': '', 'accent': ''},
            {'label': 'B', 'note': '', 'accent': ''},
        ]

    def test_absent_item_value_is_omitted_from_the_canonical_form(self):
        data = validate_content_model({
            'title': 'T', 'items': [{'label': 'A'}],
        }).to_dict()
        assert 'value' not in data['items'][0]

    def test_zero_item_value_is_kept(self):
        data = validate_content_model({
            'title': 'T', 'items': [{'label': 'A', 'value': 0}],
        }).to_dict()
        assert data['items'][0]['value'] == 0

    def test_item_value_must_be_numeric(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'items': [{'label': 'A', 'value': '1'}],
            })
        assert exc.value.field == 'items[0].value'

    def test_item_value_rejects_booleans(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'items': [{'label': 'A', 'value': True}],
            })
        assert exc.value.field == 'items[0].value'

    def test_item_note_must_be_string(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'items': [{'label': 'A', 'value': 1, 'note': 2}],
            })
        assert exc.value.field == 'items[0].note'

    def test_missing_series_name_names_field(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'series': [{'values': [1]}],
            })
        assert exc.value.field == 'series[0].name'

    def test_missing_series_values_names_field(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'series': [{'name': 'S'}],
            })
        assert exc.value.field == 'series[0].values'

    def test_non_numeric_series_value_names_index(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T', 'series': [{'name': 'S', 'values': [1, 'x']}],
            })
        assert exc.value.field == 'series[0].values[1]'

    def test_series_length_must_match_items(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model({
                'title': 'T',
                'items': [{'label': 'A', 'value': 1}],
                'series': [{'name': 'S', 'values': [1, 2]}],
            })
        assert exc.value.field == 'series[0].values'

    def test_top_level_must_be_object(self):
        with pytest.raises(ContentModelError) as exc:
            validate_content_model([])
        assert exc.value.field == 'content model'
