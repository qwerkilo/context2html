import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location("vr", os.path.join(os.path.dirname(__file__), "validate-report.py"))
vr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vr)

class TestReportSections:
    def test_exec_summary_present(self):
        assert not vr.check_exec_summary(
            '<style>.exec-summary{}</style><div class="exec-summary"><p>Key findings</p></div>')
    def test_exec_summary_missing(self):
        assert len(vr.check_exec_summary('<div class="summary">no exec here</div>')) > 0
    def test_exec_summary_empty(self):
        assert len(vr.check_exec_summary('')) > 0

    def test_report_chapters_one(self):
        assert not vr.check_report_chapters(
            '<div class="report-chapter"><h2>Chapter 1</h2></div>')
    def test_report_chapters_multiple(self):
        assert not vr.check_report_chapters(
            '<div class="report-chapter">A</div><div class="report-chapter">B</div>')
    def test_report_chapters_none(self):
        assert len(vr.check_report_chapters(
            '<div class="chapter">no report-chapter</div>')) > 0
    def test_report_chapters_empty(self):
        assert len(vr.check_report_chapters('')) > 0

    def test_conclusion_page_present(self):
        assert not vr.check_conclusion_page(
            '<style>.conclusion-page{}</style><section class="conclusion-page"><p>Conclusion</p></section>')
    def test_conclusion_page_missing(self):
        assert len(vr.check_conclusion_page(
            '<section class="results">no conclusion</section>')) > 0
    def test_conclusion_page_empty(self):
        assert len(vr.check_conclusion_page('')) > 0

    def test_report_footer_present(self):
        assert not vr.check_report_footer(
            '<style>.report-footer{}</style><footer class="report-footer"><p>Footer</p></footer>')
    def test_report_footer_missing(self):
        assert len(vr.check_report_footer(
            '<footer>no report-footer here</footer>')) > 0
    def test_report_footer_empty(self):
        assert len(vr.check_report_footer('')) > 0


class TestBilingual:
    def test_no_data_lang_skips(self):
        assert not vr.check_bilingual('<html><p>no lang attributes</p></html>')
    def test_zh_en_btn_key_passes(self):
        assert not vr.check_bilingual(
            '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>'
            '<button data-lang-btn></button>key==="l"</html>')
    def test_missing_zh_fails(self):
        assert len(vr.check_bilingual(
            '<html><span data-lang="en">EN</span><button data-lang-btn></button>key==="l"</html>')) > 0
    def test_missing_en_fails(self):
        assert len(vr.check_bilingual(
            '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0
    def test_missing_toggle_fails(self):
        assert len(vr.check_bilingual(
            '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>key==="l"</html>')) > 0
    def test_missing_L_key_fails(self):
        assert len(vr.check_bilingual(
            '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>'
            '<button data-lang-btn></button></html>')) > 0
    def test_no_data_lang_skips_even_with_toggle(self):
        assert not vr.check_bilingual('<html><p>no bilingual at all</p></html>')
    def test_single_lang_with_toggle_fails(self):
        assert len(vr.check_bilingual(
            '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0


class TestThemeCSS:
    def test_link_present_passes(self):
        assert not vr.check_theme_css('<link href="theme/report-themes.css" rel="stylesheet">')
    def test_missing_link_fails(self):
        assert len(vr.check_theme_css('<link href="theme/other.css" rel="stylesheet">')) > 0
    def test_CDN_link_flagged(self):
        assert len(vr.check_theme_css(
            '<link href="https://cdn.example.com/report-themes.css" rel="stylesheet">')) > 0
    def test_multiple_refs_ok(self):
        assert not vr.check_theme_css(
            '<link href="theme/report-themes.css"><link href="theme/report-themes.css">')
    def test_empty_html_fails(self):
        assert len(vr.check_theme_css('')) > 0
    def test_data_uri_not_link_fails(self):
        assert len(vr.check_theme_css('<style>@import "data:text/css,..."</style>')) > 0
    def test_relative_path_okay(self):
        assert not vr.check_theme_css('<link href="../theme/report-themes.css" rel="stylesheet">')
    def test_missing_file_fails_with_base_dir(self, tmp_path):
        assert len(vr.check_theme_css(
            '<link href="theme/report-themes.css" rel="stylesheet">', str(tmp_path))) > 0
    def test_existing_file_passes_with_base_dir(self, tmp_path):
        (tmp_path / "theme").mkdir()
        (tmp_path / "theme" / "report-themes.css").write_text("/* */")
        assert not vr.check_theme_css(
            '<link href="theme/report-themes.css" rel="stylesheet">', str(tmp_path))
    def test_cdn_with_base_dir_still_warns(self, tmp_path):
        assert len(vr.check_theme_css(
            '<link href="https://cdn.example.com/report-themes.css">', str(tmp_path))) > 0
    def test_missing_file_error_includes_resolved_path(self, tmp_path):
        issues = vr.check_theme_css(
            '<link href="theme/report-themes.css">', str(tmp_path))
        assert any('missing' in i.lower() for i in issues)
        assert any(str(tmp_path) in i for i in issues)


class TestSVG:
    def test_no_svgs_passes(self, tmp_path):
        assert not vr.check_svg_links('<html><p>no svg</p></html>', tmp_path)
    def test_valid_svg_passes(self, tmp_path):
        (tmp_path / "chart-ok.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>')
        assert not vr.check_svg_links(f'<html><img src="chart-ok.svg"/></html>', tmp_path)
    def test_missing_svg_fails(self, tmp_path):
        assert len(vr.check_svg_links('<html><img src="missing.svg"/></html>', tmp_path)) > 0
    def test_invalid_xml_fails(self, tmp_path):
        (tmp_path / "chart-bad.svg").write_text("not valid xml {{{")
        assert len(vr.check_svg_links(f'<html><img src="chart-bad.svg"/></html>', tmp_path)) > 0
    def test_mixed_valid_invalid_fails(self, tmp_path):
        (tmp_path / "chart-ok.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>')
        assert len(vr.check_svg_links(
            f'<html><img src="chart-ok.svg"/><img src="missing.svg"/></html>', tmp_path)) > 0
    def test_multiple_valid_passes(self, tmp_path):
        (tmp_path / "chart-ok.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>')
        assert not vr.check_svg_links(
            f'<html><img src="chart-ok.svg"/><img src="chart-ok.svg"/></html>', tmp_path)


class TestFocusVisible:
    def test_present_in_style_passes(self):
        assert not vr.check_focus_visible('<style>:focus-visible { outline: 2px solid red; }</style>')
    def test_missing_fails(self):
        assert len(vr.check_focus_visible('<style>body { color: red; }</style>')) > 0
    def test_inline_style_passes(self):
        assert not vr.check_focus_visible(
            '<html style="--focus-visible: 1px solid"><style>:focus-visible{}</style></html>')
    def test_empty_fails(self):
        assert len(vr.check_focus_visible('')) > 0
    def test_comment_still_passes(self):
        assert not vr.check_focus_visible('<!-- :focus-visible is important -->')
    def test_with_focus_visible_class_passes(self):
        assert not vr.check_focus_visible(
            '<style>.custom:focus-visible { outline: 3px solid blue; }</style>')


class TestTabularNums:
    def test_present_passes(self):
        assert not vr.check_tabular_nums(
            '<style>body { font-variant-numeric: tabular-nums; }</style>')
    def test_missing_fails(self):
        assert len(vr.check_tabular_nums('<style>body { color: red; }</style>')) > 0
    def test_in_shorthand_passes(self):
        assert not vr.check_tabular_nums(
            '<style>body { font: 16px/1.5 sans-serif; font-variant-numeric: tabular-nums; }</style>')
    def test_empty_fails(self):
        assert len(vr.check_tabular_nums('')) > 0
    def test_multiple_declarations_passes(self):
        assert not vr.check_tabular_nums(
            '<style>.a{font-variant-numeric:tabular-nums}.b{font-variant-numeric:normal}</style>')
    def test_in_class_attr_passes(self):
        assert not vr.check_tabular_nums('<div class="tabular-nums-values">123</div>')


class TestSemanticHTML:
    def test_article_passes(self):
        assert not vr.check_semantic_html('<html><article></article></html>')
    def test_section_passes(self):
        assert not vr.check_semantic_html('<html><section></section></html>')
    def test_nav_passes(self):
        assert not vr.check_semantic_html('<html><nav></nav></html>')
    def test_aside_passes(self):
        assert not vr.check_semantic_html('<html><aside></aside></html>')
    def test_main_passes(self):
        assert not vr.check_semantic_html('<html><main></main></html>')
    def test_none_fails(self):
        assert len(vr.check_semantic_html('<html><div></div></html>')) > 0
    def test_empty_fails(self):
        assert len(vr.check_semantic_html('')) > 0
    def test_multiple_nested_passes(self):
        assert not vr.check_semantic_html(
            '<html><nav><article><section></section></article></nav></html>')


class TestH1Count:
    def test_exactly_one_passes(self):
        assert not vr.check_h1_count("<html><h1>Title</h1></html>")
    def test_zero_fails(self):
        assert len(vr.check_h1_count("<html></html>")) > 0
    def test_two_fails(self):
        assert len(vr.check_h1_count("<html><h1>A</h1><h1>B</h1></html>")) > 0
    def test_bilingual_passes(self):
        assert not vr.check_h1_count(
            '<html><h1 data-lang="zh">标题</h1><h1 data-lang="en">Title</h1></html>')
    def test_bilingual_mismatch_fails(self):
        assert len(vr.check_h1_count(
            '<html><h1 data-lang="zh">标题</h1><h1 data-lang="zh">第二标题</h1></html>')) > 0


class TestRelativeLinks:
    def test_relative_passes(self):
        assert not vr.check_relative_links('<a href="0021-slug.html">link</a>')
    def test_absolute_slash_fails(self):
        assert len(vr.check_relative_links('<a href="/reports/x.html">link</a>')) > 0
    def test_absolute_http_fails(self):
        assert len(vr.check_relative_links(
            '<a href="https://example.com/report.html">link</a>')) > 0
    def test_no_html_links_fails(self):
        assert len(vr.check_relative_links('<a href="https://example.com">link</a>')) > 0
    def test_same_dir_relative_passes(self):
        assert not vr.check_relative_links('<a href="./sub/report.html">link</a>')


class TestSVGContrast:
    def test_no_svgs_passes(self, tmp_path):
        assert not vr.check_svg_contrast('<html><p>hello</p></html>', tmp_path)
    def test_safe_colors_passes(self, tmp_path):
        (tmp_path / "safe.svg").write_text(
            '<svg><rect fill="#333" width="100"/><text fill="#fff">white on dark</text></svg>')
        assert not vr.check_svg_contrast(f'<html><img src="safe.svg"/></html>', tmp_path)
    def test_light_fill_white_text_fails(self, tmp_path):
        (tmp_path / "risky.svg").write_text(
            '<svg><rect fill="#fef2f2" width="100"/><text fill="#fff">white on light</text></svg>')
        assert len(vr.check_svg_contrast(f'<html><img src="risky.svg"/></html>', tmp_path)) > 0
    def test_missing_file_no_crash(self, tmp_path):
        assert not vr.check_svg_contrast('<html><img src="noexist.svg"/></html>', tmp_path)
    def test_mixed_safe_risky_fails(self, tmp_path):
        (tmp_path / "safe.svg").write_text(
            '<svg><rect fill="#333" width="100"/><text fill="#fff">white on dark</text></svg>')
        (tmp_path / "risky.svg").write_text(
            '<svg><rect fill="#fef2f2" width="100"/><text fill="#fff">white on light</text></svg>')
        assert len(vr.check_svg_contrast(
            f'<html><img src="safe.svg"/><img src="risky.svg"/></html>', tmp_path)) > 0


class TestLibDeps:
    def test_no_echarts_three_js_passes(self):
        assert not vr.check_lib_deps('<html><p>hello</p></html>', '.')
    def test_echarts_CDN_passes(self):
        assert not vr.check_lib_deps(
            '<html><script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js">'
            '</script>echarts.init()</html>', '.')
    def test_echarts_local_missing_fails(self):
        assert len(vr.check_lib_deps('<html>echarts.init()</html>', 'C:\\nonexistent')) > 0
    def test_three_js_CDN_passes(self):
        assert not vr.check_lib_deps(
            '<html><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js">'
            '</script>new THREE.Scene()</html>', '.')
    def test_three_js_local_missing_fails(self):
        assert len(vr.check_lib_deps('<html>new THREE.Scene()</html>', 'C:\\nonexistent')) > 0
    def test_echarts_no_lib_fails(self):
        assert len(vr.check_lib_deps('<html>echarts.init()</html>', 'C:\\nonexistent')) > 0
    def test_three_js_no_lib_fails(self):
        assert len(vr.check_lib_deps('<html>new THREE.Scene()</html>', 'C:\\nonexistent')) > 0
    def test_d3_CDN_passes(self):
        assert not vr.check_lib_deps(
            '<html><script src="https://d3js.org/d3.v7.min.js">'
            '</script>d3.forceSimulation()</html>', '.')
    def test_d3_no_lib_fails(self):
        assert len(vr.check_lib_deps(
            '<html>d3.select("body")</html>', 'C:\\nonexistent')) > 0
    def test_echarts_GL_no_lib_fails(self):
        assert len(vr.check_lib_deps(
            '<html>type: "bar3D"</html>', 'C:\\nonexistent')) > 0
    def test_echarts_local_script_missing_file_fails(self, tmp_path):
        assert len(vr.check_lib_deps(
            '<html><script src="libs/echarts.min.js"></script>echarts.init()</html>',
            str(tmp_path))) > 0
    def test_echarts_local_script_existing_file_passes(self, tmp_path):
        (tmp_path / "libs").mkdir()
        (tmp_path / "libs" / "echarts.min.js").write_text("// stub")
        assert not vr.check_lib_deps(
            '<html><script src="libs/echarts.min.js"></script>echarts.init()</html>',
            str(tmp_path))
    def test_three_script_missing_fails(self, tmp_path):
        assert len(vr.check_lib_deps(
            '<html><script src="libs/three.min.js"></script>new THREE.Scene()</html>',
            str(tmp_path))) > 0
    def test_d3_script_missing_fails(self, tmp_path):
        assert len(vr.check_lib_deps(
            '<html><script src="libs/d3.min.js"></script>d3.select("body")</html>',
            str(tmp_path))) > 0
    def test_cdn_script_not_checked(self, tmp_path):
        assert not vr.check_lib_deps(
            '<html><script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js">'
            '</script>echarts.init()</html>', str(tmp_path))


class TestBarFillWidth:
    def test_inline_100_passes(self):
        assert not vr.check_bar_fill_width(
            '<div class="bar-fill" style="width: 80%;">x</div>')
    def test_inline_overflow_fails(self):
        assert len(vr.check_bar_fill_width(
            '<div class="bar-fill" style="width: 120%;">x</div>')) > 0
    def test_css_rule_100_passes(self):
        assert not vr.check_bar_fill_width(
            '<style>.bar-fill { width: 75%; }</style><div class="bar-fill"></div>')
    def test_css_rule_overflow_fails(self):
        assert len(vr.check_bar_fill_width(
            '<style>.bar-fill { width: 110%; }</style><div class="bar-fill"></div>')) > 0
    def test_no_bar_fill_passes(self):
        assert not vr.check_bar_fill_width('<div class="other"></div>')


class TestCmpTableResponsive:
    def test_no_cmp_table_skips(self):
        assert not vr.check_cmp_table_responsive('<div>no table</div>')
    def test_responsive_rule_passes(self):
        html = ('<style>@media (max-width: 600px) { .cmp-table tr { display: block; } }</style>'
                '<table class="cmp-table"></table>')
        assert not vr.check_cmp_table_responsive(html)
    def test_no_responsive_rule_fails(self):
        html = '<style>.cmp-table { width: 100%; }</style><table class="cmp-table"></table>'
        assert len(vr.check_cmp_table_responsive(html)) > 0
    def test_only_wide_breakpoint_fails(self):
        html = ('<style>@media (max-width: 1200px) { .cmp-table { display: block; } }</style>'
                '<table class="cmp-table"></table>')
        assert len(vr.check_cmp_table_responsive(html)) > 0
    def test_rule_in_second_style_block_passes(self):
        html = ('<style>body { color: red; }</style>'
                '<style>@media (max-width: 600px) { .cmp-table tr { display: block; } }</style>'
                '<table class="cmp-table"></table>')
        assert not vr.check_cmp_table_responsive(html)


class TestCrossRefs:
    def test_no_chapters_or_refs_passes(self):
        assert not vr.check_cross_refs('<div>plain</div>')
    def test_canonical_ref_passes(self):
        assert not vr.check_cross_refs(
            '<section id="ch1"></section><section id="ch2"></section>'
            '<a href="#ch1">link</a>')
    def test_chart_anchor_skipped(self):
        assert not vr.check_cross_refs('<a href="#chart-1">chart</a>')
    def test_chapter_format_fails(self):
        assert len(vr.check_cross_refs('<a href="#chapter-one">link</a>')) > 0


class TestSVGLinkVariants:
    def test_object_data_missing_fails(self, tmp_path):
        assert len(vr.check_svg_links(
            '<html><object data="missing.svg"></object></html>', str(tmp_path))) > 0
    def test_object_data_valid_passes(self, tmp_path):
        (tmp_path / "ok.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>')
        assert not vr.check_svg_links(
            '<html><object data="ok.svg"></object></html>', str(tmp_path))
    def test_iframe_src_missing_fails(self, tmp_path):
        assert len(vr.check_svg_links(
            '<html><iframe src="missing.svg"></iframe></html>', str(tmp_path))) > 0
    def test_source_src_missing_fails(self, tmp_path):
        assert len(vr.check_svg_links(
            '<html><source src="missing.svg"></html>', str(tmp_path))) > 0
    def test_https_skipped(self, tmp_path):
        assert not vr.check_svg_links(
            '<html><img src="https://cdn.example.com/x.svg"></html>', str(tmp_path))
    def test_data_uri_skipped(self, tmp_path):
        assert not vr.check_svg_links(
            '<html><img src="data:image/svg+xml;base64,xxx"></html>', str(tmp_path))


class TestEnglishLayout:
    def test_body_overflow_wrap_passes(self):
        html = '<style>body { overflow-wrap: break-word; }</style>'
        assert not vr.check_english_layout(html)
    def test_body_overflow_wrap_missing_fails(self):
        html = '<style>body { color: red; }</style>'
        assert len(vr.check_english_layout(html)) > 0
    def test_cmp_table_fixed_passes(self):
        html = '<style>body { overflow-wrap: break-word; }.cmp-table { table-layout: fixed; }</style><table class="cmp-table"></table>'
        assert not vr.check_english_layout(html)
    def test_cmp_table_fixed_missing_fails(self):
        html = '<style>.cmp-table { width: 100%; }</style><table class="cmp-table"></table>'
        assert len(vr.check_english_layout(html)) > 0
    def test_no_cmp_table_skips_fixed_check(self):
        html = '<style>body { overflow-wrap: break-word; }</style>'
        assert not vr.check_english_layout(html)


class TestEChartsColorUsage:
    def test_no_echarts_skips(self):
        assert not vr.check_echarts_color_usage('<div>plain</div>')
    def test_gv_helper_passes(self):
        html = '<script>function gv(n){return getComputedStyle(docEl).getPropertyValue(n).trim()}var c=echarts.init();c.setOption({itemStyle:{color:gv("--accent")}})</script>'
        assert not vr.check_echarts_color_usage(html)
    def test_var_direct_fails(self):
        html = '<script>var c=echarts.init();c.setOption({itemStyle:{color:"var(--accent)"}})</script>'
        assert len(vr.check_echarts_color_usage(html)) > 0
    def test_var_direct_single_quote_fails(self):
        html = "<script>var c=echarts.init();c.setOption({itemStyle:{color:'var(--accent)'}})</script>"
        assert len(vr.check_echarts_color_usage(html)) > 0


class TestGSAPComponent:
    def test_no_gsap_skips_lib_check(self):
        assert not vr.check_lib_deps('<html><p>hello</p></html>', '.')

    def test_gsap_local_libs_missing_fails(self, tmp_path):
        html = '<html><div data-gsap="fade">x</div></html>'
        issues = vr.check_lib_deps(html, str(tmp_path))
        assert len(issues) > 0

    def test_gsap_local_libs_exist_passes(self, tmp_path):
        (tmp_path / "libs").mkdir()
        (tmp_path / "libs" / "gsap.min.js").write_text("// stub")
        (tmp_path / "libs" / "ScrollTrigger.min.js").write_text("// stub")
        html = '<html><div data-gsap="stagger">x</div></html>'
        assert not vr.check_lib_deps(html, str(tmp_path))

    def test_gsap_cdn_passes_without_libs(self, tmp_path):
        html = '<html><script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script> x</html>'
        assert not vr.check_lib_deps(html, str(tmp_path))

    def test_gsap_register_plugin_detected(self, tmp_path):
        (tmp_path / "libs").mkdir()
        (tmp_path / "libs" / "gsap.min.js").write_text("// stub")
        (tmp_path / "libs" / "ScrollTrigger.min.js").write_text("// stub")
        html = '<html><script>gsap.registerPlugin(ScrollTrigger)</script></html>'
        assert not vr.check_lib_deps(html, str(tmp_path))

    def test_gsap_fromTo_detected(self, tmp_path):
        (tmp_path / "libs").mkdir()
        (tmp_path / "libs" / "gsap.min.js").write_text("// stub")
        (tmp_path / "libs" / "ScrollTrigger.min.js").write_text("// stub")
        html = '<html><script>gsap.fromTo(el,{x:0},{x:100})</script></html>'
        assert not vr.check_lib_deps(html, str(tmp_path))

    def test_gsap_mode_valid_passes(self):
        for mode in ['fade', 'stagger', 'parallax', 'flip', 'zoom']:
            assert not vr.check_gsap_modes(f'<div data-gsap="{mode}">x</div>')

    def test_gsap_mode_invalid_fails(self):
        assert len(vr.check_gsap_modes('<div data-gsap="slide">x</div>')) > 0

    def test_gsap_mode_empty_fails(self):
        assert len(vr.check_gsap_modes('<div data-gsap="">x</div>')) > 0

    def test_gsap_no_attr_skips(self):
        assert not vr.check_gsap_modes('<div>plain</div>')


class TestD4Connectors:
    def test_no_paragraphs_skips(self):
        assert not vr.check_d4_connectors('<html></html>')

    def test_clean_paragraph_passes(self):
        html = '<p data-lang="zh">市场在增长。需求在上升。供给也在扩大。</p>'
        assert not vr.check_d4_connectors(html)

    def test_banned_starter_fails(self):
        html = '<p data-lang="zh">此外，技术架构也需要升级。</p>'
        assert len(vr.check_d4_connectors(html)) > 0

    def test_multiple_banned_starters_fail(self):
        html = ('<p data-lang="zh">首先，我们看市场规模。</p>'
                '<p data-lang="zh">其次，分析竞争格局。</p>'
                '<p data-lang="zh">最后，给出结论。</p>')
        assert len(vr.check_d4_connectors(html)) > 0

    def test_too_many_connectors_fails(self):
        text = '因此，同时，此外，然而，但是，不过，所以，总之' * 10
        html = f'<p data-lang="zh">{text}</p>'
        assert len(vr.check_d4_connectors(html)) > 0


class TestD1SentenceLength:
    def test_no_paragraphs_skips(self):
        assert not vr.check_d1_sentence_length('<html></html>')

    def test_varied_lengths_passes(self):
        html = '<p data-lang="zh">涨了。2024 年 AI 芯片市场冲到了 1200 亿美元——增速远超预期，所有头部厂商都在加码，供应链全线吃紧。</p>'
        assert not vr.check_d1_sentence_length(html)

    def test_mid_only_sentences_fails(self):
        html = '<p data-lang="zh">市场规模在不断扩大。竞争格局也在变化。技术路线开始分化。</p>'
        assert len(vr.check_d1_sentence_length(html)) > 0


class TestD5TermVariety:
    def test_no_paragraphs_skips(self):
        assert not vr.check_d5_term_variety('<html></html>')

    def test_clean_text_passes(self):
        html = '<p data-lang="zh">市场增长很快。技术迭代不断。竞争格局清晰。</p>'
        assert not vr.check_d5_term_variety(html)

    def test_overused_terms_fails(self):
        text = '这个重要趋势非常重要，具有重要战略意义。这是重要的行业发展方向。'
        html = f'<p data-lang="zh">{text}</p>'
        assert len(vr.check_d5_term_variety(html)) > 0


class TestDataAnimSyntax:
    def test_valid_values_pass(self):
        assert not vr.check_data_anim_syntax('<div data-anim="fade-up"></div>')
        assert not vr.check_data_anim_syntax('<div data-anim="fade"></div>')
        assert not vr.check_data_anim_syntax('<div data-anim="slide-left"></div>')
        assert not vr.check_data_anim_syntax('<div data-anim="blur"></div>')
    def test_invalid_value_fails(self):
        assert len(vr.check_data_anim_syntax('<div data-anim="zoom-in"></div>')) > 0
    def test_no_data_anim_skips(self):
        assert not vr.check_data_anim_syntax('<div>plain</div>')
