"""Tests for content_type.py and report.py check functions — imports from framework package."""
from context2html.validator.content_type import detect_content_type, check_content_type_valid
from context2html.validator.report import (
    check_article_structure, check_doc_structure,
    check_tutorial_structure, check_note_structure,
    _get_style_css, _extract_para_texts,
)


class TestDetectContentType:
    def test_default_report(self):
        assert detect_content_type('<html><body></body></html>') == 'report'

    def test_valid_article(self):
        assert detect_content_type(
            '<html data-content-type="article"></html>') == 'article'

    def test_valid_doc(self):
        assert detect_content_type(
            '<html data-content-type="doc"></html>') == 'doc'

    def test_empty_value_defaults(self):
        assert detect_content_type(
            '<html data-content-type=""></html>') == 'report'


class TestCheckContentTypeValid:
    def test_valid_report(self):
        assert check_content_type_valid(
            '<html data-content-type="report"></html>') == []

    def test_valid_article(self):
        assert check_content_type_valid(
            '<html data-content-type="article"></html>') == []

    def test_valid_doc(self):
        assert check_content_type_valid(
            '<html data-content-type="doc"></html>') == []

    def test_valid_tutorial(self):
        assert check_content_type_valid(
            '<html data-content-type="tutorial"></html>') == []

    def test_valid_note(self):
        assert check_content_type_valid(
            '<html data-content-type="note"></html>') == []

    def test_invalid_unknown(self):
        issues = check_content_type_valid(
            '<html data-content-type="unknown"></html>')
        assert len(issues) > 0
        assert 'unknown' in issues[0]

    def test_empty_defaults_to_report(self):
        assert check_content_type_valid('<html></html>') == []

    def test_invalid_weird_type(self):
        issues = check_content_type_valid(
            '<html data-content-type="slideshow"></html>')
        assert len(issues) > 0


class TestCheckArticleStructure:
    def test_article_present_passes(self):
        assert not check_article_structure(
            '<html><article><p>content</p></article></html>')

    def test_article_present_deeply_nested_passes(self):
        assert not check_article_structure(
            '<html><div><section><article>deep</article></section></div></html>')

    def test_no_article_fails(self):
        assert len(check_article_structure(
            '<html><section><p>no article</p></section></html>')) > 0

    def test_empty_fails(self):
        assert len(check_article_structure('')) > 0

    def test_self_closing_article_tag(self):
        assert not check_article_structure(
            '<html><article/></html>')


class TestCheckDocStructure:
    def test_nav_with_links_passes(self):
        assert not check_doc_structure(
            '<html><nav><a href="#ch1">Chapter 1</a></nav></html>')

    def test_nav_with_multiple_links_passes(self):
        assert not check_doc_structure(
            '<html><nav><a href="#ch1">Ch1</a><a href="#ch2">Ch2</a></nav></html>')

    def test_nav_without_links_fails(self):
        assert len(check_doc_structure(
            '<html><nav><span>no links</span></nav></html>')) > 0

    def test_no_nav_fails(self):
        assert len(check_doc_structure(
            '<html><div>no nav at all</div></html>')) > 0

    def test_empty_fails(self):
        assert len(check_doc_structure('')) > 0

    def test_nav_with_class_and_links_passes(self):
        assert not check_doc_structure(
            '<html><nav class="toc"><a href="#intro">Intro</a></nav></html>')


class TestCheckTutorialStructure:
    def test_si_step_class_passes(self):
        assert not check_tutorial_structure(
            '<html><div class="si-step">Step 1</div></html>')

    def test_sc_step_class_passes(self):
        assert not check_tutorial_structure(
            '<html><div class="sc-step">Step A</div></html>')

    def test_both_step_classes_passes(self):
        assert not check_tutorial_structure(
            '<html><div class="si-step">1</div><div class="sc-step">A</div></html>')

    def test_no_step_fails(self):
        assert len(check_tutorial_structure(
            '<html><div class="step">plain step</div></html>')) > 0

    def test_empty_fails(self):
        assert len(check_tutorial_structure('')) > 0

    def test_step_in_combined_class_passes(self):
        assert not check_tutorial_structure(
            '<html><div class="content si-step active">Step with other classes</div></html>')


class TestCheckNoteStructure:
    def test_always_passes(self):
        assert not check_note_structure('<html></html>')

    def test_always_passes_with_content(self):
        assert not check_note_structure(
            '<html><p>random content</p></html>')

    def test_always_passes_empty(self):
        assert not check_note_structure('')


class TestGetStyleCss:
    def test_single_style_block(self):
        html = '<style>body { color: red; }</style>'
        result = _get_style_css(html)
        assert 'color: red' in result

    def test_multiple_style_blocks(self):
        html = ('<style>body { color: red; }</style>'
                '<style>h1 { font-size: 2em; }</style>')
        result = _get_style_css(html)
        assert 'color: red' in result
        assert 'font-size: 2em' in result

    def test_no_style_blocks(self):
        html = '<html><body>no styles</body></html>'
        assert _get_style_css(html) == ''

    def test_style_with_attributes(self):
        html = '<style type="text/css">body { margin: 0; }</style>'
        result = _get_style_css(html)
        assert 'margin: 0' in result

    def test_style_with_media_queries(self):
        html = '<style>@media (max-width: 600px) { .x { display: block; } }</style>'
        result = _get_style_css(html)
        assert '@media' in result

    def test_lru_cache_same_object(self):
        html = '<style>body { color: red; }</style>'
        r1 = _get_style_css(html)
        r2 = _get_style_css(html)
        assert r1 is r2

    def test_lru_cache_different_inputs(self):
        html1 = '<style>body { color: red; }</style>'
        html2 = '<style>body { color: blue; }</style>'
        r1 = _get_style_css(html1)
        r2 = _get_style_css(html2)
        assert r1 is not r2


class TestExtractParaTexts:
    def test_bilingual_paragraphs(self):
        html = ('<p data-lang="zh">中文内容</p>'
                '<p data-lang="en">English content</p>')
        result = _extract_para_texts(html)
        assert '中文内容' in result
        assert 'English content' in result
        assert len(result) == 2

    def test_only_zh(self):
        html = ('<p data-lang="zh">中文内容</p>'
                '<p data-lang="en">English content</p>')
        result = _extract_para_texts(html, lang='zh')
        assert result == ['中文内容']

    def test_only_en(self):
        html = ('<p data-lang="zh">中文内容</p>'
                '<p data-lang="en">English content</p>')
        result = _extract_para_texts(html, lang='en')
        assert result == ['English content']

    def test_html_entity_decoding(self):
        html = '<p data-lang="en">AT&amp;T &lt;bold&gt;</p>'
        result = _extract_para_texts(html)
        assert result == ['AT&T <bold>']

    def test_nested_tags_stripped(self):
        html = '<p data-lang="zh"><strong>重点</strong>内容</p>'
        result = _extract_para_texts(html)
        assert result == ['重点内容']

    def test_empty_paragraphs_skipped(self):
        html = ('<p data-lang="zh"></p>'
                '<p data-lang="zh">有内容</p>'
                '<p data-lang="en">  </p>'
                '<p data-lang="en">content</p>')
        result = _extract_para_texts(html)
        assert result == ['有内容', 'content']

    def test_no_paragraphs(self):
        html = '<html><div>no data-lang paragraphs</div></html>'
        assert _extract_para_texts(html) == []

    def test_paragraphs_with_multiple_classes(self):
        html = '<p class="intro" data-lang="zh">介绍段落</p>'
        result = _extract_para_texts(html)
        assert result == ['介绍段落']

    def test_nbsp_decoded(self):
        html = '<p data-lang="en">Hello&nbsp;World</p>'
        result = _extract_para_texts(html)
        assert result == ['Hello World']

    def test_gt_lt_decoded(self):
        html = '<p data-lang="en">x &gt; 5 &lt; 10</p>'
        result = _extract_para_texts(html)
        assert result == ['x > 5 < 10']
