"""The generated validation checklist must track the validator, not drift.

`references/decision-guide.md` used to carry a hand-written table of the 23
checks; it had already drifted (content-type was listed as #22 while the
validator runs it at #10). The table is now generated, and this file proves the
generator notices when the two disagree.
"""

import importlib.util
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(BASE_DIR, 'scripts', 'sync-check-table.py')

_spec = importlib.util.spec_from_file_location('sync_check_table', SCRIPT)
sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync)


class TestCheckTableSync(unittest.TestCase):
    def test_committed_file_is_in_sync(self):
        with open(sync.GUIDE, 'r', encoding='utf-8') as fh:
            current = fh.read()
        check_block, warn_block = sync.build_blocks()
        updated = sync.replace_block(current, sync.CHECK_START, sync.CHECK_END, check_block)
        updated = sync.replace_block(updated, sync.WARN_START, sync.WARN_END, warn_block)
        self.assertEqual(updated, current,
                         'run: python scripts/sync-check-table.py')

    def test_report_table_lists_every_check(self):
        check_block, _ = sync.build_blocks()
        rows = [line for line in check_block.split('\n')
                if line.startswith('| ') and not line.startswith('| #')]
        module = sync._validator()
        _, checks, _ = module.build_checks(
            sync.STUB.format(ct='report'), sync.ROOT)
        self.assertEqual(len(rows), len(checks))
        self.assertEqual(len(checks), 23)

    def test_guard_rejects_a_check_without_a_doc_entry(self):
        module = sync._validator()
        labels = sync._labels_by_type(module)
        missing = dict(sync.ENTRIES)
        del missing['Slot data blocks (1 per component slot)']
        original = sync.ENTRIES
        try:
            sync.ENTRIES = missing
            with self.assertRaises(SystemExit) as ctx:
                sync._guard(labels)
        finally:
            sync.ENTRIES = original
        self.assertIn('Slot data blocks', str(ctx.exception))

    def test_guard_rejects_a_stale_doc_entry(self):
        module = sync._validator()
        labels = sync._labels_by_type(module)
        stale = dict(sync.ENTRIES)
        stale['A check that was deleted'] = ('x', 'y')
        original = sync.ENTRIES
        try:
            sync.ENTRIES = stale
            with self.assertRaises(SystemExit) as ctx:
                sync._guard(labels)
        finally:
            sync.ENTRIES = original
        self.assertIn('A check that was deleted', str(ctx.exception))

    def test_guard_accepts_the_current_pairing(self):
        module = sync._validator()
        sync._guard(sync._labels_by_type(module))


if __name__ == '__main__':
    unittest.main()
