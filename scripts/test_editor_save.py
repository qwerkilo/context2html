"""Save and re-edit: the delivered HTML keeps the swaps, not the editor chrome.

The save pipeline is pure string work in ``runtime/editor-core.js``; the
browser only serializes the document and triggers the download.  These tests
drive the pipeline through node, and prove the round trip by composing the
same HTML a browser would serialize after a swap: slot markup replaced, data
block untouched, editor UI present in the live DOM.
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess

import pytest

from context2html.editor import read_runtime
from context2html.renderer import TemplateRenderer
from context2html.slots import render_slot

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, 'scripts', 'js', 'save-runner.js')
BROWSER_RUNNER = os.path.join(ROOT, 'scripts', 'js', 'save-browser-runner.js')
TEMPLATES_DIR = os.path.join(ROOT, 'templates')

_spec = importlib.util.spec_from_file_location(
    'validate_report_for_save_tests',
    os.path.join(ROOT, 'scripts', 'validate-report.py'))
_vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vr)

MODEL = {
    'title': '渠道销量',
    'items': [
        {'label': '直营', 'value': 120},
        {'label': '经销', 'value': 80},
    ],
}

TIMELINE = {
    'title': '里程碑',
    'items': [
        {'label': '2025 Q1', 'value': 1, 'note': '立项'},
        {'label': '2026 Q3', 'value': 2, 'note': '上线'},
    ],
}


def _node():
    executable = os.environ.get('NODE') or shutil.which('node')
    if not executable:
        pytest.skip('node executable not found; install node or set NODE')
    return executable


def call(op, *args):
    """Invoke one save-pipeline function (or the swap simulator)."""
    result = subprocess.run(
        [_node(), RUNNER],
        input=json.dumps({'op': op, 'args': list(args)}),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def call_browser(op, *args):
    """Invoke the pipeline the way the inlined report script does."""
    result = subprocess.run(
        [_node(), BROWSER_RUNNER],
        input=json.dumps({'op': op, 'args': list(args)}),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class TestStripEditorUi:
    def test_marked_style_and_bar_are_removed(self):
        html = (
            '<html><head>'
            '<style id="ic-editor-style" data-ic-editor-ui="true">.x{}</style>'
            '</head><body>'
            '<div class="ic-editor-bar" data-ic-editor-ui="true"><button>编辑</button></div>'
            '<p>keep</p>'
            '</body></html>'
        )
        result = call('stripEditorUi', html)
        assert 'ic-editor-style' not in result
        assert 'ic-editor-bar' not in result
        assert '<p>keep</p>' in result
        assert result.startswith('<html><head></head><body>')

    def test_nested_marked_element_removes_its_children(self):
        html = (
            '<body>\n'
            '<div class="ic-editor-panel" data-ic-editor-ui="true">'
            '<div><h3>选择替换组件</h3></div><p>inside</p></div>\n'
            '<p>keep</p>\n'
            '</body>'
        )
        assert call('stripEditorUi', html) == '<body>\n\n<p>keep</p>\n</body>'

    def test_bare_marker_attribute_is_removed(self):
        html = '<body><div class="ic-editor-tooltip" data-ic-editor-ui>tip</div><p>keep</p></body>'
        assert call('stripEditorUi', html) == '<body><p>keep</p></body>'

    def test_marker_text_inside_a_script_is_left_alone(self):
        html = (
            '<script>var marker = "data-ic-editor-ui"; var tag = "<div>";</script>'
            '<p>keep</p>'
        )
        assert call('stripEditorUi', html) == html

    def test_marker_text_inside_a_style_is_left_alone(self):
        html = '<style>.ic-editor-panel[data-ic-editor-ui]{display:none}</style><p>keep</p>'
        assert call('stripEditorUi', html) == html

    def test_comment_mentioning_the_marker_is_left_alone(self):
        html = '<!-- <div data-ic-editor-ui="true"> --><p>keep</p>'
        assert call('stripEditorUi', html) == html

    def test_untouched_document_is_byte_identical(self):
        html = '<!DOCTYPE html>\n<html lang="zh-CN"><body><p>a &lt; b</p></body></html>'
        assert call('stripEditorUi', html) == html


class TestClearEditingState:
    def test_editing_class_is_dropped_from_the_root_element(self):
        html = '<html class="ic-editing" lang="zh-CN"><body></body></html>'
        assert call('clearEditingState', html) == (
            '<html lang="zh-CN"><body></body></html>')

    def test_other_root_classes_survive(self):
        html = '<html class="report ic-editing wide"><body></body></html>'
        assert call('clearEditingState', html) == (
            '<html class="report wide"><body></body></html>')

    def test_root_without_the_class_is_byte_identical(self):
        html = '<html lang="zh-CN"><body></body></html>'
        assert call('clearEditingState', html) == html

    def test_editing_class_inside_a_script_is_left_alone(self):
        html = '<html lang="zh"><body><script>var c = "ic-editing";</script></body></html>'
        assert call('clearEditingState', html) == html


def data_block(component_id, model):
    """The block the generation path emits — the independent source of truth."""
    return render_slot(component_id, model).data_block


def block_body(block):
    return re.search(r'>([^<]*)</script>$', block, re.S).group(1)


def block_tag(block):
    return block[:block.index('>') + 1]


class TestRebuildDataBlocks:
    def test_pretty_printed_block_becomes_the_generated_block_again(self):
        block = data_block(26, MODEL)
        body = json.dumps(json.loads(block_body(block)), indent=2, ensure_ascii=False)
        rebuilt = call(
            'rebuildDataBlocks', block_tag(block) + body + '</script>')
        assert rebuilt == block

    def test_block_with_extra_fields_is_left_for_the_validator(self):
        block = data_block(26, MODEL)
        body = json.loads(block_body(block))
        body['handwritten_note'] = 'keep me'
        original = block_tag(block) + json.dumps(body, ensure_ascii=False) + '</script>'
        assert call('rebuildDataBlocks', original) == original

    def test_invalid_json_block_is_left_alone(self):
        original = (
            '<script type="application/json" data-slot="s">'
            '{oops</script>')
        assert call('rebuildDataBlocks', original) == original

    def test_non_slot_json_script_is_left_alone(self):
        original = '<script type="application/json">{"a":   1}</script>'
        assert call('rebuildDataBlocks', original) == original

    def test_plain_script_with_html_looking_text_is_left_alone(self):
        original = (
            '<script>var t = \'<div class="x">\';</script>'
            '<p>keep</p>')
        assert call('rebuildDataBlocks', original) == original

    def test_script_closers_in_the_model_stay_escaped(self):
        model = {'title': 'A </script> B', 'items': [{'label': 'x', 'value': 1}]}
        block = data_block(4, model)
        assert '<\\/script>' in block
        assert call('rebuildDataBlocks', block) == block


class TestSavedHtml:
    def test_doctype_is_added_to_a_serialized_document(self):
        html = '<html data-editable="true"><body><p>x</p></body></html>'
        assert call('savedHtml', html) == '<!DOCTYPE html>\n' + html

    def test_existing_doctype_is_not_duplicated(self):
        html = '<!DOCTYPE html>\n<html><body></body></html>'
        assert call('savedHtml', html) == html

    def test_custom_doctype_is_used_when_the_document_has_none(self):
        html = '<html><body></body></html>'
        assert call('savedHtml', html, {'doctype': '<!doctype html>'}) == (
            '<!doctype html>\n' + html)

    def test_flag_and_runtime_survive_while_the_editor_ui_does_not(self):
        html = (
            '<html data-editable="true" class="ic-editing"><body>'
            '<script data-ic-editor-runtime="true">var runtime = 1;</script>'
            '<div class="ic-editor-bar" data-ic-editor-ui="true">bar</div>'
            '</body></html>'
        )
        saved = call('savedHtml', html)
        assert 'data-editable="true"' in saved
        assert 'data-ic-editor-runtime="true"' in saved
        assert 'ic-editor-bar' not in saved
        assert 'ic-editing' not in saved

    def test_saving_an_already_saved_document_is_byte_identical(self):
        html = call(
            'savedHtml',
            '<html data-editable="true"><body><p>x</p></body></html>')
        assert call('savedHtml', html) == html


class TestSavedFileName:
    def test_title_becomes_an_html_file_name(self):
        assert call('savedFileName', '报告标题 - 调研报告') == '报告标题 - 调研报告.html'

    def test_path_separators_and_reserved_characters_are_replaced(self):
        assert call('savedFileName', 'a/b:c*?d') == 'a b c d.html'

    def test_empty_title_falls_back_to_report(self):
        assert call('savedFileName', '') == 'report.html'
        assert call('savedFileName', '  ') == 'report.html'

    def test_existing_html_suffix_is_kept(self):
        assert call('savedFileName', 'draft.html') == 'draft.html'


def strip_scripts(html):
    return re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)


def markup_tags(html):
    return re.findall(r'<[^>]+>', strip_scripts(html))


def with_live_editor_ui(html):
    """The DOM a browser would serialize while the editor is open."""
    ui = (
        '<style id="ic-editor-style" data-ic-editor-ui="true">.ic-editing{}</style>'
        '<div class="ic-editor-bar" id="ic-editor-bar" data-ic-editor-ui="true">'
        '<button class="ic-editor-toggle">编辑</button>'
        '<button class="ic-editor-undo">撤销</button></div>'
        '<div class="ic-editor-backdrop" data-ic-editor-ui="true"></div>'
        '<div class="ic-editor-panel" data-ic-editor-ui="true">'
        '<h3>选择替换组件</h3><div class="ic-editor-list"></div></div>'
        '<div class="ic-editor-tooltip" data-ic-editor-ui="true">提示</div>'
    )
    html = html.replace('</body>', ui + '</body>', 1)
    return html.replace('<html ', '<html class="ic-editing" ', 1)


class TestEditorWiring:
    def test_editable_report_ships_the_save_pipeline(self):
        html = TemplateRenderer(templates_dir=TEMPLATES_DIR).assemble(
            'report-starter', [], 'warm', editable=True)
        assert 'savedHtml' in html
        assert 'ic-editor-save' in html

    def test_save_button_serializes_the_document_and_downloads_it(self):
        source = read_runtime('editor.js')
        assert 'ic-editor-save' in source
        assert 'core.savedHtml(' in source
        assert 'core.savedFileName(' in source
        assert 'URL.createObjectURL' in source
        assert 'link.download' in source

    def test_default_report_ships_no_save_button(self):
        html = TemplateRenderer(templates_dir=TEMPLATES_DIR).assemble(
            'report-starter', [], 'warm')
        assert 'ic-editor-save' not in html


class TestBrowserRuntimePath:
    def test_inlined_script_path_matches_the_node_path(self):
        block = data_block(26, MODEL)
        pretty = block_tag(block) + json.dumps(
            json.loads(block_body(block)), indent=2, ensure_ascii=False) + '</script>'
        html = (
            '<html class="ic-editing" data-editable="true"><body>'
            + pretty
            + '<div class="ic-editor-bar" data-ic-editor-ui="true">bar</div>'
            + '</body></html>'
        )
        expected = call('savedHtml', html)
        assert call_browser('savedHtml', html) == expected
        assert block in expected


class TestSavedReport:
    def setup_method(self):
        self.a = render_slot(26, MODEL)
        self.b = render_slot(3, TIMELINE)
        self.html = TemplateRenderer(templates_dir=TEMPLATES_DIR).assemble(
            'report-starter', [], 'warm',
            slots=[(26, MODEL), (3, TIMELINE)], editable=True)

    def swapped_twice(self):
        html = call('swap', self.html, self.a.slot_id, 4)
        return call('swap', html, self.b.slot_id, 12)

    def saved(self):
        return call('savedHtml', with_live_editor_ui(self.swapped_twice()))

    def test_saved_file_is_a_complete_standalone_document(self):
        saved = self.saved()
        assert saved.startswith('<!DOCTYPE html>\n<html ')
        assert saved.rstrip().endswith('</html>')
        assert 'src="runtime' not in saved

    def test_untouched_report_saves_byte_identically(self):
        assert call('savedHtml', self.html) == self.html

    def test_saved_file_carries_no_editor_ui_markup(self):
        saved = self.saved()
        for tag in markup_tags(saved):
            assert 'data-ic-editor-ui' not in tag, tag
        assert 'class="ic-editor-bar"' not in saved
        assert 'class="ic-editor-panel"' not in saved
        assert 'id="ic-editor-style"' not in saved
        assert not re.search(r'<html[^>]*class="[^"]*ic-editing', saved)

    def test_saved_file_keeps_the_flag_and_all_three_runtime_layers(self):
        saved = self.saved()
        assert 'data-editable="true"' in saved
        assert saved.count('data-ic-editor-runtime="true"') == 3
        for match in re.finditer(r'<script([^>]*data-ic-editor-runtime="true"[^>]*)>', saved):
            assert 'src=' not in match.group(1)
        assert 'SlotEditorCore' in saved

    def test_two_rounds_of_swaps_survive_the_save(self):
        saved = self.saved()
        assert render_slot(4, MODEL, self.a.slot_id).markup in saved
        assert render_slot(12, TIMELINE, self.b.slot_id).markup in saved
        assert 'data-slot="%s" data-component="4"' % self.a.slot_id in saved
        assert 'data-slot="%s" data-component="12"' % self.b.slot_id in saved

    def test_saved_data_blocks_stay_paired_and_canonical(self):
        saved = self.saved()
        assert self.a.data_block in saved
        assert self.b.data_block in saved

    def test_saved_file_can_be_swapped_again(self):
        saved = self.saved()
        again = call('swap', saved, self.a.slot_id, 24)
        assert render_slot(24, MODEL, self.a.slot_id).markup in again
        assert self.a.data_block in again

    def test_saved_file_passes_all_23_hard_checks(self, tmp_path):
        (tmp_path / 'libs').mkdir()
        (tmp_path / 'libs' / 'echarts.min.js').write_text('', encoding='utf-8')
        (tmp_path / 'theme').mkdir()
        (tmp_path / 'theme' / 'report-themes.css').write_text(
            '/* stub */', encoding='utf-8')

        result = _vr.run_checks(self.saved(), str(tmp_path))
        failures = {label: issues for label, issues in result.checks if issues}
        assert failures == {}
        assert len(result.checks) == 23
