"""Mutation smoke test — a Windows-native stand-in for mutmut.

mutmut refuses to run outside WSL (boxed/mutmut#397), so this script performs
the same job for a curated set of high-value mutants: apply one textual
mutation, run the targeted test file, restore the source, report the score.

Usage:
    python scripts/mutation-smoke.py           # run every mutant
    python scripts/mutation-smoke.py --list    # show mutants without running
    python scripts/mutation-smoke.py -k svg    # run mutants whose label matches

Exit code is 1 when any mutant survives, so this can gate CI.

Each entry is (label, file, original snippet, mutated snippet, test file). The
snippets must appear verbatim; a missing snippet is reported as STALE rather
than silently skipped, because a refactor that moves the code invalidates the
mutant.
"""

import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTANTS = [
    (
        'relative-links: absolute check narrowed to "//"',
        'context2html/validator/common.py',
        'if href.startswith("/") or href.startswith("http"):',
        'if href.startswith("//") or href.startswith("http"):',
        'scripts/test_validate_report.py',
    ),
    (
        'svg containment: escape guard disabled',
        'context2html/validator/svg.py',
        '        if os.path.commonpath([base, path]) != base:',
        '        if False:',
        'scripts/test_validate_report.py',
    ),
    (
        'D1 short-sentence threshold 10 -> 1',
        'context2html/validator/report.py',
        'has_short = any(n <= 10 for n in lengths)',
        'has_short = any(n <= 1 for n in lengths)',
        'scripts/test_validate_report.py',
    ),
    (
        'renderer theme-name whitelist removed',
        'context2html/renderer.py',
        '        if not _RE_THEME_NAME.fullmatch(theme_name):',
        '        if False:',
        'scripts/test_renderer.py',
    ),
    (
        'slot data blocks: missing-block issue suppressed',
        'context2html/validator/slots.py',
        '            issues.append(\n'
        '                f"Slot \'{slot_id}\' (component {component_id}) has no matching data block")',
        '            pass',
        'scripts/test_validate_slots.py',
    ),
    (
        'bar chart: empty-state guard disabled',
        'context2html/slots.py',
        '    entries, field = _item_entries(model)\n'
        '    if entries is None:\n'
        '        return _section(4, slot_id, model, _empty_state())',
        '    entries, field = _item_entries(model)\n'
        '    if False:\n'
        '        return _section(4, slot_id, model, _empty_state())',
        'scripts/test_chart_slots.py',
    ),
    (
        'registry: content_model flag ignored',
        'context2html/registry.py',
        "            content_model=bool(d.get('content_model', False)),",
        '            content_model=False,',
        'scripts/test_registry.py',
    ),
    (
        'lesson lang escaping removed',
        'scripts/validate-lesson.py',
        '                safe_lang = re.escape(lang)',
        '                safe_lang = lang',
        'scripts/test_validate_lesson.py',
    ),
    (
        'structure: empty state body emptied',
        'context2html/structure.py',
        '        \'<p class="ic-empty" data-lang="zh">暂无数据</p>\'\n'
        '        \'<p class="ic-empty" data-lang="en">No data</p>\'',
        '        \'\'',
        'scripts/test_structure.py',
    ),
    (
        'structure: model text escaping removed',
        'context2html/structure.py',
        '    return html.escape(str(value), quote=True)',
        '    return str(value)',
        'scripts/test_structure.py',
    ),
    (
        'structure: unsafe accent accepted',
        'context2html/structure.py',
        '    if _SAFE_COLOR.fullmatch(item.accent):',
        '    if item.accent:',
        'scripts/test_structure.py',
    ),
    (
        'structure: bilingual fallback disabled',
        'context2html/structure.py',
        '    en = en or zh',
        '    en = en',
        'scripts/test_structure.py',
    ),
    (
        'parity: missing-fixture guard disabled',
        'scripts/check-js-parity.py',
        '    if missing:\n'
        '        return [\n'
        "            f'{component_label(component_id)}: missing golden fixture: '\n"
        "            + ', '.join(missing)\n"
        '        ]',
        '    if False:\n'
        '        return []',
        'scripts/test_js_parity.py',
    ),
    (
        'runtime: script-closer escaping disabled',
        'runtime/slots.js',
        "      .split('</').join('<\\\\/')",
        "      .split('</').join('</')",
        'scripts/test_js_parity.py',
    ),
]


def _run_tests(test_path):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    return subprocess.run(
        [sys.executable, '-m', 'pytest', test_path, '-q', '--no-header', '-p', 'no:cacheprovider'],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env).returncode


def run_mutant(mutant):
    label, rel_path, old, new, test_path = mutant
    path = os.path.join(ROOT, rel_path)
    original_bytes = io.open(path, 'rb').read()
    original = original_bytes.decode('utf-8')
    newline = '\r\n' if '\r\n' in original else '\n'
    normalized = original.replace('\r\n', '\n')
    if old not in normalized:
        return 'STALE', label

    try:
        mutated = normalized.replace(old, new, 1).replace('\n', newline)
        io.open(path, 'wb').write(mutated.encode('utf-8'))
        return ('KILLED' if _run_tests(test_path) != 0 else 'SURVIVED'), label
    finally:
        io.open(path, 'wb').write(original_bytes)
        if io.open(path, 'rb').read() != original_bytes:
            raise RuntimeError(f'failed to restore {rel_path}')


def main(argv):
    keyword = None
    if '--list' in argv:
        for label, rel_path, _, _, test_path in MUTANTS:
            print(f'{rel_path:45} {test_path:35} {label}')
        return 0
    if '-k' in argv:
        keyword = argv[argv.index('-k') + 1]

    selected = [m for m in MUTANTS if keyword is None or keyword in m[0]]
    if not selected:
        print(f'[FAIL] No mutant matches {keyword!r}')
        return 1

    results = [run_mutant(m) for m in selected]
    for verdict, label in results:
        print(f'{verdict:10} {label}')

    killed = sum(1 for v, _ in results if v == 'KILLED')
    stale = sum(1 for v, _ in results if v == 'STALE')
    print(f'\nmutation score: {killed}/{len(results)}'
          + (f' ({stale} stale)' if stale else ''))
    return 0 if killed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
