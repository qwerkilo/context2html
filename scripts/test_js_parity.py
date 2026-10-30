"""Parity harness: Python and browser slot renderers must agree byte for byte.

The golden fixtures under ``scripts/fixtures/golden/`` are the independent
record of what a component renders.  Every test drives one of three public
seams: the Python renderer, the node renderer, or the parity command itself.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(SCRIPTS, 'fixtures', 'golden')
SCRIPT = os.path.join(SCRIPTS, 'check-js-parity.py')

spec = importlib.util.spec_from_file_location('parity', SCRIPT)
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)

EXPECTED_IDS = [2, 3, 4, 5, 12, 13, 15, 17, 18, 19, 20, 22, 24, 26]


def _run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )


def _copy_fixtures(tmp_path):
    target = tmp_path / 'golden'
    shutil.copytree(FIXTURES, target)
    return target


class TestFixtureCoverage:
    def test_swappable_set_is_the_fourteen_content_model_components(self):
        assert parity.swappable_component_ids() == EXPECTED_IDS

    def test_every_swappable_component_has_a_model_and_a_golden(self):
        missing = []
        for component_id in EXPECTED_IDS:
            for path in parity.fixture_paths(component_id, FIXTURES):
                if not os.path.exists(path):
                    missing.append(os.path.basename(path))
        assert missing == []

    def test_fixture_models_are_valid_json_objects(self):
        for component_id in EXPECTED_IDS:
            model_path, _ = parity.fixture_paths(component_id, FIXTURES)
            with open(model_path, 'r', encoding='utf-8') as handle:
                assert isinstance(json.load(handle), dict)


class TestRendererParity:
    def test_python_matches_the_committed_golden(self):
        for component_id in EXPECTED_IDS:
            model_path, golden_path = parity.fixture_paths(component_id, FIXTURES)
            assert parity.render_python(component_id, model_path) == parity.read_text(golden_path), (
                f'component {component_id} drifted from its golden')

    def test_node_matches_the_committed_golden(self):
        for component_id in EXPECTED_IDS:
            model_path, golden_path = parity.fixture_paths(component_id, FIXTURES)
            assert parity.render_node(component_id, model_path) == parity.read_text(golden_path), (
                f'component {component_id} drifted from its golden')

    def test_python_and_node_agree_directly(self):
        for component_id in EXPECTED_IDS:
            model_path, _ = parity.fixture_paths(component_id, FIXTURES)
            assert parity.render_python(component_id, model_path) == parity.render_node(
                component_id, model_path), f'component {component_id} differs between Python and node'


class TestParityCommand:
    def test_command_reports_all_fourteen(self):
        result = _run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert '14/14' in result.stdout

    def test_missing_fixture_fails_with_the_component_name(self, tmp_path):
        target = _copy_fixtures(tmp_path)
        model_path, golden_path = parity.fixture_paths(13, str(target))
        os.remove(model_path)
        os.remove(golden_path)
        result = _run('--fixtures-dir', str(target))
        assert result.returncode == 1
        assert 'component 13' in result.stdout
        assert 'missing golden fixture' in result.stdout

    def test_invalid_model_names_the_component(self, tmp_path):
        target = _copy_fixtures(tmp_path)
        model_path, _ = parity.fixture_paths(4, str(target))
        with open(model_path, 'w', encoding='utf-8', newline='') as handle:
            handle.write('{not json')
        result = _run('--fixtures-dir', str(target))
        assert result.returncode == 1
        assert 'component 4' in result.stdout
        assert 'invalid golden model' in result.stdout

    def test_component_filter_runs_only_the_selected_component(self):
        result = _run('-k', '12')
        assert result.returncode == 0, result.stdout + result.stderr
        assert '1/1' in result.stdout

    def test_broken_golden_names_component_and_first_difference(self, tmp_path):
        target = _copy_fixtures(tmp_path)
        _, golden_path = parity.fixture_paths(12, str(target))
        golden = parity.read_text(golden_path)
        broken = golden.replace('data-grid', 'data-grXd', 1)
        assert broken != golden
        with open(golden_path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(broken)

        result = _run('--fixtures-dir', str(target))
        assert result.returncode == 1
        assert 'component 12' in result.stdout
        assert 'first difference' in result.stdout
        assert 'line ' in result.stdout
        assert 'expected' in result.stdout and 'actual' in result.stdout

    def test_difference_report_includes_surrounding_context(self):
        message = parity.describe_difference(12, 'alpha\nbravo charlie', 'alpha\nbraXo charlie')
        assert 'component 12' in message
        assert 'line 2' in message
        assert 'bra' in message and 'o charlie' in message


class TestCanonicalJson:
    def test_golden_data_block_escapes_script_closers_and_line_separators(self):
        _, golden_path = parity.fixture_paths(2, FIXTURES)
        golden = parity.read_text(golden_path)
        assert '<\\/script>' in golden
        assert '\\u2028' in golden
        assert '\\u2029' in golden

    def test_golden_data_block_preserves_float_lexemes(self):
        _, golden_path = parity.fixture_paths(26, FIXTURES)
        golden = parity.read_text(golden_path)
        assert '"value":3.0' in golden
        assert '13.0' in golden
