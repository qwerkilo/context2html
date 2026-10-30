"""Inlining the browser editor into an editable report.

The editor is three plain scripts with no build step: the slot runtime
(``runtime/slots.js``), the pure decision layer (``runtime/editor-core.js``)
and the DOM bootstrap (``runtime/editor.js``).  They are concatenated into the
report so the file stays self-contained and works from ``file://``.
"""

import os
import re

RUNTIME_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'runtime')

RUNTIME_FILES = ('slots.js', 'editor-core.js', 'editor.js')

_HTML_OPEN = re.compile(r'<html(?=[\s>])', re.IGNORECASE)
_EDITABLE_ATTR = re.compile(r'\bdata-editable="[^"]*"', re.IGNORECASE)
_EDITOR_RUNTIME_ATTR = 'data-ic-editor-runtime="true"'


class EditorRuntimeError(RuntimeError):
    """Raised when a runtime file cannot be safely inlined."""


def read_runtime(name):
    path = os.path.join(RUNTIME_DIR, name)
    with open(path, 'r', encoding='utf-8') as handle:
        return handle.read()


def inline_runtime():
    """Return the three runtime layers as inline ``<script>`` blocks.

    A literal ``</script`` inside a runtime file would end the block early;
    the files are ours, so treat one as a build error instead of guessing.
    """
    blocks = []
    for name in RUNTIME_FILES:
        source = read_runtime(name)
        if '</script' in source.lower():
            raise EditorRuntimeError(f'{name} contains a literal </script')
        blocks.append(f'<script {_EDITOR_RUNTIME_ATTR}>\n{source}\n</script>')
    return '\n'.join(blocks)


def mark_editable(html):
    """Set ``data-editable="true"`` on the root element."""
    if _EDITABLE_ATTR.search(html):
        return _EDITABLE_ATTR.sub('data-editable="true"', html, count=1)
    return _HTML_OPEN.sub('<html data-editable="true"', html, count=1)


def enable_editable(html):
    """Mark the report editable and append the inlined editor runtime."""
    html = mark_editable(html)
    if _EDITOR_RUNTIME_ATTR in html:
        return html
    runtime = inline_runtime()
    if '</body>' in html:
        return html.replace('</body>', runtime + '\n</body>', 1)
    return html + '\n' + runtime
