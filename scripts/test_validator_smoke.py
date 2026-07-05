"""Smoke and integration tests for context2html.validator package."""

import os

from context2html.validator import (
    PASS, FAIL,
    check_svg_links, check_svg_contrast,
    check_h1_count, check_relative_links,
    check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_cross_refs, check_data_anim_syntax, check_gsap_modes,
    detect_content_type, check_content_type_valid,
    check_exec_summary, check_report_chapters, check_conclusion_page,
    check_report_footer, check_theme_css,
    check_bar_fill_width, check_cmp_table_responsive,
    check_english_layout, check_echarts_color_usage,
    check_article_structure, check_doc_structure,
    check_tutorial_structure, check_note_structure,
    check_d4_connectors, check_d1_sentence_length, check_d5_term_variety,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'starter.html')


class TestValidatorSmoke:
    def test_pass_fail_constants(self):
        assert PASS == "[PASS]"
        assert FAIL == "[FAIL]"

    def test_check_h1_count(self):
        assert check_h1_count("<html><h1>Title</h1></html>") == []
        assert len(check_h1_count("<html></html>")) > 0

    def test_check_focus_visible(self):
        assert check_focus_visible("<style>:focus-visible {}</style>") == []
        assert len(check_focus_visible("<html></html>")) > 0

    def test_check_semantic(self):
        assert check_semantic_html("<html><article>x</article></html>") == []
        assert len(check_semantic_html("<html><div>x</div></html>")) > 0

    def test_detect_content_type_default(self):
        assert detect_content_type("<html></html>") == "report"

    def test_detect_content_type_article(self):
        assert detect_content_type('<html data-content-type="article"></html>') == "article"

    def test_content_type_valid(self):
        assert check_content_type_valid('<html data-content-type="report"></html>') == []
        assert len(check_content_type_valid('<html data-content-type="invalid"></html>')) > 0

    def test_gsap_modes(self):
        html = '<div data-gsap="fade"></div>'
        assert check_gsap_modes(html) == []
        html = '<div data-gsap="invalid_mode"></div>'
        assert len(check_gsap_modes(html)) > 0

    def test_data_anim_syntax(self):
        html = '<div data-anim="fade-up"></div>'
        assert check_data_anim_syntax(html) == []
        html = '<div data-anim="wrong"></div>'
        assert len(check_data_anim_syntax(html)) > 0

    def test_echarts_color_usage_no_echarts(self):
        assert check_echarts_color_usage("<html></html>") == []

    def test_check_relative_links(self):
        assert check_relative_links('<a href="local.html">x</a>') == []
        assert len(check_relative_links('<a href="/abs.html">x</a>')) > 0


class TestValidatorIntegration:
    """Run the full check suite on a real template HTML."""

    def _load_template(self):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()

    def test_starter_html_passes_common_checks(self):
        html = self._load_template()
        base_dir = os.path.dirname(TEMPLATE_PATH)

        assert check_h1_count(html) == [], "starter should have exactly one h1 or bilingual pair"
        assert check_focus_visible(html) == [], "starter should have :focus-visible"
        assert check_bilingual(html) == [], "starter should have bilingual markup"
        assert check_semantic_html(html) == [], "starter should have semantic elements"
        assert check_tabular_nums(html) == [], "starter should have tabular-nums"
        assert check_data_anim_syntax(html) == [], "starter should have valid data-anim"
        assert check_content_type_valid(html) == [], "starter should have valid content type"
        assert check_relative_links(html) == [], "starter should have only relative links"

    def test_starter_html_lib_deps(self):
        html = self._load_template()
        base_dir = os.path.dirname(TEMPLATE_PATH)
        # starter.html doesn't use echarts/three/d3 — should pass
        assert check_lib_deps(html, base_dir) == []

    def test_starter_html_detected_as_report(self):
        html = self._load_template()
        assert detect_content_type(html) == "report"

    def test_missing_h1_flagged(self):
        assert len(check_h1_count("<html><h2>No h1</h2></html>")) > 0

    def test_no_semantic_html_flagged(self):
        assert len(check_semantic_html("<html><div>only divs</div></html>")) > 0

    def test_no_bilingual_flagged(self):
        html = '<html data-lang-btn><p data-lang="zh">only cn</p></html>'
        assert len(check_bilingual(html)) > 0

    def test_missing_focus_visible_flagged(self):
        assert len(check_focus_visible("<html><body></body></html>")) > 0
