"""Byte-for-byte parity between the Python and browser slot renderers.

For every component whose front matter says ``content_model: true`` this
script loads the golden content model, renders it with ``context2html.slots``
and with ``runtime/slots.js`` under node, and compares both against the
committed golden fragment.

Usage:
    python scripts/check-js-parity.py
    python scripts/check-js-parity.py --fixtures-dir path/to/golden
    python scripts/check-js-parity.py -k 12 -k 26
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from context2html.registry import ComponentRegistry  # noqa: E402
from context2html.slots import render_slot  # noqa: E402

FIXTURES_DIR = os.path.join(ROOT, 'scripts', 'fixtures', 'golden')
NODE_RUNNER = os.path.join(ROOT, 'scripts', 'js', 'render-fixture.js')
_REGISTRY = None


class ParityError(RuntimeError):
    """Raised when one side cannot be rendered or the node runner fails."""


def _registry():
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ComponentRegistry()
    return _REGISTRY


def component_label(component_id):
    components = _registry().list_components(id=component_id)
    name = components[0].metadata.name if components else 'unknown component'
    return f'component {component_id} ({name})'


def swappable_component_ids(registry=None):
    """Return the ids whose front matter opts into the content model."""
    registry = registry or _registry()
    return sorted(
        component.metadata.id
        for component in registry.list_components(content_model=True)
    )


def fixture_paths(component_id, fixtures_dir=FIXTURES_DIR):
    """Return ``(model_path, golden_path)`` for one component."""
    stem = f'slot-{component_id:02d}'
    return (
        os.path.join(fixtures_dir, f'{stem}-model.json'),
        os.path.join(fixtures_dir, f'{stem}.golden.html'),
    )


def read_text(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return handle.read()


def load_model(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def render_python(component_id, model_path):
    """Render one fixture through the generation-time renderer."""
    return render_slot(component_id, load_model(model_path)).fragment


def node_executable():
    return os.environ.get('NODE') or shutil.which('node')


def render_node(component_id, model_path, node=None):
    """Render one fixture through runtime/slots.js under node."""
    executable = node or node_executable()
    if not executable:
        raise ParityError('node executable not found; install node or set NODE')
    try:
        result = subprocess.run(
            [executable, NODE_RUNNER, str(component_id), model_path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
    except OSError as exc:
        raise ParityError(
            f'{component_label(component_id)}: could not run node: {exc}') from exc
    if result.returncode != 0:
        raise ParityError(
            f'{component_label(component_id)}: node renderer failed\n{result.stderr.strip()}')
    return result.stdout


def first_difference(expected, actual):
    """Return the character index of the first difference, or ``None``."""
    for index, (left, right) in enumerate(zip(expected, actual)):
        if left != right:
            return index
    if len(expected) != len(actual):
        return min(len(expected), len(actual))
    return None


def _context(text, index, radius=40):
    start = max(0, index - radius)
    end = min(len(text), index + radius)
    excerpt = text[start:end]
    marker = index - start
    if marker >= len(excerpt):
        excerpt += '[<end>]'
    else:
        excerpt = excerpt[:marker] + '[' + excerpt[marker] + ']' + excerpt[marker + 1:]
    return excerpt.replace('\n', '\\n').replace('\r', '\\r')


def describe_difference(component_id, expected, actual):
    """Name the component and locate the first byte that disagrees."""
    index = first_difference(expected, actual)
    if index is None:
        return f'{component_label(component_id)}: no difference'
    line = expected.count('\n', 0, index) + 1
    column = index - expected.rfind('\n', 0, index)
    byte_offset = len(expected[:index].encode('utf-8'))
    return (
        f'{component_label(component_id)}: first difference at character {index} '
        f'(line {line}, column {column}, byte {byte_offset})\n'
        f'  expected: {_context(expected, index)}\n'
        f'  actual:   {_context(actual, index)}'
    )


def check_component(component_id, fixtures_dir=FIXTURES_DIR, node=None):
    """Return a list of human-readable problems for one component."""
    model_path, golden_path = fixture_paths(component_id, fixtures_dir)
    missing = [
        os.path.basename(path)
        for path in (model_path, golden_path)
        if not os.path.exists(path)
    ]
    if missing:
        return [
            f'{component_label(component_id)}: missing golden fixture: '
            + ', '.join(missing)
        ]

    try:
        model = load_model(model_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f'{component_label(component_id)}: invalid golden model: {exc}']
    try:
        golden = read_text(golden_path)
    except OSError as exc:
        return [f'{component_label(component_id)}: unreadable golden fragment: {exc}']
    try:
        python_fragment = render_slot(component_id, model).fragment
    except Exception as exc:  # noqa: BLE001 - report the component, do not crash the run
        return [f'{component_label(component_id)}: Python renderer failed: {exc}']
    try:
        js_fragment = render_node(component_id, model_path, node=node)
    except ParityError as exc:
        return [str(exc)]

    if python_fragment != js_fragment:
        return [describe_difference(component_id, python_fragment, js_fragment)]
    if python_fragment != golden:
        return [describe_difference(component_id, golden, python_fragment)]
    return []


def run(fixtures_dir=FIXTURES_DIR, only=None, node=None):
    """Check every swappable component; return ``(checked, problems)``."""
    component_ids = swappable_component_ids()
    if only is not None:
        selected = set(only)
        component_ids = [cid for cid in component_ids if cid in selected]

    problems = []
    for component_id in component_ids:
        problems.extend(check_component(component_id, fixtures_dir, node=node))
    return component_ids, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures-dir', default=FIXTURES_DIR,
                        help='directory holding slot-NN-model.json / slot-NN.golden.html')
    parser.add_argument('-k', '--component', type=int, action='append', dest='components',
                        help='check only this component id (repeatable)')
    parser.add_argument('--node', default=None, help='node executable to use')
    args = parser.parse_args(argv)

    component_ids, problems = run(
        fixtures_dir=args.fixtures_dir,
        only=args.components,
        node=args.node,
    )
    if not component_ids:
        print('parity: no swappable components matched')
        return 1
    for problem in problems:
        print(problem)
    if problems:
        print(f'\nparity: {len(problems)} failure(s) across {len(component_ids)} component(s)')
        return 1
    print(f'parity: {len(component_ids)}/{len(component_ids)} components byte-identical')
    return 0


if __name__ == '__main__':
    sys.exit(main())
