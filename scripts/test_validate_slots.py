"""Tests for the slot/data-block pairing hard check."""

import importlib.util
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
spec = importlib.util.spec_from_file_location(
    'vr', os.path.join(os.path.dirname(__file__), 'validate-report.py'))
vr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vr)

LABEL = 'Slot data blocks (1 per component slot)'

SLOT = '<section class="ic-slot" data-slot="slot-26-abc12345" data-component="26">chart</section>'
BLOCK = ('<script type="application/json" data-slot="slot-26-abc12345">'
         '{"title":"T","items":[],"series":[]}</script>')


class TestSlotDataBlockPairing:
    def test_paired_slot_and_data_block_passes(self):
        assert not vr.check_slot_data_blocks(SLOT + BLOCK)

    def test_missing_data_block_fails(self):
        issues = vr.check_slot_data_blocks(SLOT)
        assert any('no matching data block' in issue for issue in issues)

    def test_mismatched_data_block_id_fails(self):
        other = BLOCK.replace('slot-26-abc12345', 'slot-26-other')
        issues = vr.check_slot_data_blocks(SLOT + other)
        assert any('no matching data block' in issue for issue in issues)

    def test_invalid_json_data_block_fails(self):
        bad = BLOCK.replace('{"title":"T","items":[],"series":[]}', '{oops')
        issues = vr.check_slot_data_blocks(SLOT + bad)
        assert any('not valid JSON' in issue for issue in issues)

    def test_data_block_must_be_json_object(self):
        array_block = BLOCK.replace('{"title":"T","items":[],"series":[]}', '[]')
        issues = vr.check_slot_data_blocks(SLOT + array_block)
        assert any('not a JSON object' in issue for issue in issues)

    def test_duplicate_slot_id_fails(self):
        issues = vr.check_slot_data_blocks(SLOT + SLOT + BLOCK)
        assert any('Duplicate slot id' in issue for issue in issues)

    def test_no_slots_passes(self):
        assert not vr.check_slot_data_blocks('<html><body><p>plain</p></body></html>')

    def test_check_is_wired_into_build_checks(self):
        _, checks, _ = vr.build_checks(
            '<html data-content-type="article"><article>x</article></html>', '.')
        assert LABEL in [label for label, _ in checks]

    def test_run_checks_fails_when_a_slot_lacks_its_data_block(self):
        demo = os.path.join(ROOT, 'examples', '0001-demo-report.html')
        with open(demo, 'r', encoding='utf-8') as fh:
            html = fh.read()
        broken = html.replace('</body>', SLOT + '</body>')
        result = vr.run_checks(broken, os.path.dirname(demo))
        assert result.all_pass is False
        failed = [label for label, issues in result.checks if issues]
        assert LABEL in failed
