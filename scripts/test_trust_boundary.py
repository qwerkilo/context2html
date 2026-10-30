"""Trust-boundary tests: model text is untrusted and must never become markup.

A report file is untrusted input — it can arrive from a colleague, a download,
or a hand-edited copy. The editor re-renders a swapped slot through
``template.innerHTML``, so anything a renderer fails to escape becomes live
HTML. This is the project's substitute for permission tests: there is no
server, no auth and no session, so the whole security surface is "does text
stay text".

The invariant is structural: **the DOM shape must not depend on the text.** A
benign model and a hostile model of the same shape must produce the same set of
elements and attributes. Comparing those signatures catches an injected tag, an
injected attribute, or a payload that closes a ``<script>`` early — without
having to enumerate payloads in the assertions.

Every payload below breaks a naive escaper, and the table runs each through all
14 swappable components on both renderers, so a component that joins the
swappable set is covered without touching this file.
"""

import json
import os
import subprocess
from html.parser import HTMLParser

import pytest

from context2html.registry import ComponentRegistry
from context2html.slots import render_slot

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_RUNNER = os.path.join(ROOT, 'scripts', 'js', 'render-fixture.js')

# One payload per field, so a single model exercises four escaping sites.
PAYLOADS = {
    'title': '<script>alert(1)</script>',
    'label': '"><img src=x onerror=alert(1)>',
    'note': '</script><script>alert(2)</script>',
    'series': 'a\u2028b\u2029c',
}


class DomSignature(HTMLParser):
    """Collect the element/attribute shape, ignoring all text content."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.scripts = 0
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, tuple(sorted(name for name, _ in attrs))))
        if tag == 'script':
            self.scripts += 1
            self.in_script = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False

    def signature(self):
        return (tuple(self.elements), self.scripts)


def signature(markup):
    parser = DomSignature()
    parser.feed(markup)
    parser.close()
    return parser.signature()


def swappable_ids():
    return sorted(meta.id for meta in
                  ComponentRegistry().list_components(content_model=True))


def model_with(title, label, note, series):
    return {
        'title': title,
        'subtitle': title,
        'items': [
            {'label': label, 'value': 10, 'note': note},
            {'label': label, 'value': 20, 'note': note},
        ],
        'series': [{'name': series, 'values': [10, 20]}],
    }


def benign_model():
    return model_with('标题', '标签', '备注', '系列')


def hostile_model():
    return model_with(PAYLOADS['title'], PAYLOADS['label'],
                      PAYLOADS['note'], PAYLOADS['series'])


def render_node(component_id, model, tmp_path):
    path = tmp_path / f'model-{component_id}.json'
    path.write_text(json.dumps(model, ensure_ascii=False), encoding='utf-8')
    out = subprocess.run(
        ['node', NODE_RUNNER, str(component_id), str(path)],
        capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert out.returncode == 0, out.stderr
    return out.stdout


def data_block_body(fragment):
    """Return the JSON text inside the slot's application/json script block."""
    marker = '<script type="application/json"'
    start = fragment.index(marker)
    body_start = fragment.index('>', start) + 1
    body_end = fragment.index('</script>', body_start)
    return fragment[body_start:body_end]


@pytest.mark.parametrize('component_id', swappable_ids())
def test_python_renderer_dom_shape_ignores_model_text(component_id):
    benign = signature(render_slot(component_id, benign_model()).markup)
    hostile = signature(render_slot(component_id, hostile_model()).markup)

    assert hostile == benign, (
        f'component {component_id}: hostile text changed the DOM shape')


@pytest.mark.parametrize('component_id', swappable_ids())
def test_python_data_block_cannot_break_out_of_its_script_tag(component_id):
    body = data_block_body(render_slot(component_id, hostile_model()).fragment)

    assert '</script' not in body.lower()
    assert '\u2028' not in body and '\u2029' not in body
    parsed = json.loads(body)
    assert parsed['title'] == PAYLOADS['title']
    assert parsed['items'][0]['label'] == PAYLOADS['label']
    assert parsed['series'][0]['name'] == PAYLOADS['series']


@pytest.mark.parametrize('component_id', swappable_ids())
def test_browser_renderer_dom_shape_ignores_model_text(component_id, tmp_path):
    benign = signature(render_node(component_id, benign_model(), tmp_path))
    hostile = signature(render_node(component_id, hostile_model(), tmp_path))

    assert hostile == benign, (
        f'component {component_id}: hostile text changed the DOM shape')


@pytest.mark.parametrize('component_id', swappable_ids())
def test_browser_data_block_cannot_break_out_of_its_script_tag(component_id, tmp_path):
    fragment = render_node(component_id, hostile_model(), tmp_path)
    body = data_block_body(fragment)

    assert '</script' not in body.lower()
    assert json.loads(body)['title'] == PAYLOADS['title']
