"""Slot validation — every component slot must have its content-model data block."""

import json
import re

SLOT_DATA_BLOCK_LABEL = 'Slot data blocks (1 per component slot)'

_RE_TAG = re.compile(r'<[^>]+>')
_RE_SCRIPT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.DOTALL | re.IGNORECASE)
_RE_ATTR = re.compile(
    r'\b([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')')


def _attrs(tag):
    return {
        match.group(1): match.group(2) if match.group(2) is not None else match.group(3)
        for match in _RE_ATTR.finditer(tag)
    }


def _iter_slots(html):
    for match in _RE_TAG.finditer(html):
        tag = match.group(0)
        if tag.lower().startswith('<script'):
            continue
        attrs = _attrs(tag)
        slot_id = attrs.get('data-slot')
        component_id = attrs.get('data-component')
        if slot_id and component_id:
            yield slot_id, component_id


def _iter_data_blocks(html):
    for match in _RE_SCRIPT.finditer(html):
        attrs = _attrs(f'<script{match.group(1)}>')
        if attrs.get('type', '').lower() != 'application/json':
            continue
        slot_id = attrs.get('data-slot')
        if slot_id:
            yield slot_id, match.group(2)


def check_slot_data_blocks(html):
    """Return issues for slots whose data block is missing, duplicated or invalid."""
    issues = []
    blocks = {}
    for slot_id, body in _iter_data_blocks(html):
        if slot_id in blocks:
            issues.append(f"Duplicate data block for slot '{slot_id}'")
            continue
        blocks[slot_id] = body

    seen = set()
    for slot_id, component_id in _iter_slots(html):
        if slot_id in seen:
            issues.append(f"Duplicate slot id '{slot_id}'")
            continue
        seen.add(slot_id)

        block = blocks.get(slot_id)
        if block is None:
            issues.append(
                f"Slot '{slot_id}' (component {component_id}) has no matching data block")
            continue
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            issues.append(f"Slot '{slot_id}' data block is not valid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            issues.append(f"Slot '{slot_id}' data block is not a JSON object")
    return issues
