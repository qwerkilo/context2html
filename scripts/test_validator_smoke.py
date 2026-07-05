"""Smoke tests for context2html.validator package — verify all functions importable."""
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


class TestValidatorImports:
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
