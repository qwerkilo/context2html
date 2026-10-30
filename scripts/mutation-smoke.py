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

Entries live in `scripts/mutants/<area>.py`, one module per area. Parallel work
on different areas appends to different files, so two implementers never edit
the same list.
"""

import importlib
import io
import os
import pkgutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUTANTS_DIR = os.path.join(ROOT, 'scripts', 'mutants')

sys.path.insert(0, os.path.join(ROOT, 'scripts'))


def load_mutants():
    """Collect every MUTANTS list under scripts/mutants, in module-name order."""
    entries = []
    for info in sorted(pkgutil.iter_modules([MUTANTS_DIR]), key=lambda i: i.name):
        module = importlib.import_module(f'mutants.{info.name}')
        entries.extend(getattr(module, 'MUTANTS', []))
    return entries


MUTANTS = load_mutants()


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
