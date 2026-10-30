"""Single authoritative definition of the swappable-component content model.

Every swappable visual component consumes this normalized shape::

    {
      "title": str,
      "subtitle": str,
      "items": [{"label": str, "value": number, "note": str, "accent": str}],
      "series": [{"name": str, "values": [number, ...]}]
    }

Components read the fields they need and ignore the rest.  ``title`` is the
only required field; everything else defaults to an empty value.
"""

from dataclasses import dataclass

_MISSING = object()


class ContentModelError(ValueError):
    """Raised when content-model data does not conform; ``field`` names it."""

    def __init__(self, field, message):
        self.field = field
        super().__init__(f'{field}: {message}')


@dataclass(frozen=True)
class ContentItem:
    label: str
    value: int | float
    note: str = ''
    accent: str = ''


@dataclass(frozen=True)
class ContentSeries:
    name: str
    values: tuple[int | float, ...]


@dataclass(frozen=True)
class ContentModel:
    title: str
    subtitle: str = ''
    items: tuple[ContentItem, ...] = ()
    series: tuple[ContentSeries, ...] = ()

    def to_dict(self):
        """Return the canonical plain-data form (what a data block stores)."""
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'items': [
                {
                    'label': item.label,
                    'value': item.value,
                    'note': item.note,
                    'accent': item.accent,
                }
                for item in self.items
            ],
            'series': [
                {'name': series.name, 'values': list(series.values)}
                for series in self.series
            ],
        }


def _field(path, key):
    return f'{path}{key}'


def _require_string(mapping, key, path):
    value = mapping.get(key, _MISSING)
    field = _field(path, key)
    if value is _MISSING:
        raise ContentModelError(field, 'missing field')
    if not isinstance(value, str) or not value.strip():
        raise ContentModelError(field, 'expected a non-empty string')
    return value


def _optional_string(mapping, key, path):
    value = mapping.get(key, _MISSING)
    if value is _MISSING:
        return ''
    if not isinstance(value, str):
        raise ContentModelError(_field(path, key), 'expected a string')
    return value


def _optional_list(mapping, key, path):
    value = mapping.get(key, _MISSING)
    if value is _MISSING:
        return []
    if not isinstance(value, list):
        raise ContentModelError(_field(path, key), 'expected a list')
    return value


def _require_list(mapping, key, path):
    value = mapping.get(key, _MISSING)
    if value is _MISSING:
        raise ContentModelError(_field(path, key), 'missing field')
    if not isinstance(value, list):
        raise ContentModelError(_field(path, key), 'expected a list')
    return value


def _number_value(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContentModelError(field, 'expected a number')
    return value


def _require_number(mapping, key, path):
    value = mapping.get(key, _MISSING)
    field = _field(path, key)
    if value is _MISSING:
        raise ContentModelError(field, 'missing field')
    return _number_value(value, field)


def validate_content_model(data):
    """Validate ``data`` and return a :class:`ContentModel`.

    Raises :class:`ContentModelError` on the first non-conforming field; the
    exception's ``field`` attribute names the missing or invalid path, e.g.
    ``title``, ``items[0].label`` or ``series[0].values[1]``.
    """
    if not isinstance(data, dict):
        raise ContentModelError('content model', 'expected a JSON object')

    title = _require_string(data, 'title', '')
    subtitle = _optional_string(data, 'subtitle', '')
    raw_items = _optional_list(data, 'items', '')
    raw_series = _optional_list(data, 'series', '')

    items = []
    for index, raw in enumerate(raw_items):
        path = f'items[{index}].'
        if not isinstance(raw, dict):
            raise ContentModelError(f'items[{index}]', 'expected an object')
        items.append(ContentItem(
            label=_require_string(raw, 'label', path),
            value=_require_number(raw, 'value', path),
            note=_optional_string(raw, 'note', path),
            accent=_optional_string(raw, 'accent', path),
        ))

    series = []
    for index, raw in enumerate(raw_series):
        path = f'series[{index}].'
        if not isinstance(raw, dict):
            raise ContentModelError(f'series[{index}]', 'expected an object')
        name = _require_string(raw, 'name', path)
        raw_values = _require_list(raw, 'values', path)
        values = tuple(
            _number_value(value, f'{path}values[{value_index}]')
            for value_index, value in enumerate(raw_values)
        )
        if items and len(values) != len(items):
            raise ContentModelError(
                f'{path}values',
                f'expected {len(items)} values to match items, got {len(values)}')
        series.append(ContentSeries(name=name, values=values))

    return ContentModel(
        title=title,
        subtitle=subtitle,
        items=tuple(items),
        series=tuple(series),
    )
