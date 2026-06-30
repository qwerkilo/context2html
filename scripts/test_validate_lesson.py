import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location("vl", os.path.join(os.path.dirname(__file__), "validate-lesson.py"))
vl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vl)


class TestH1Count:
    def test_exactly_one_passes(self):
        assert not vl.check_h1_count("<html><h1>Title</h1></html>")
    def test_zero_fails(self):
        assert len(vl.check_h1_count("<html></html>")) > 0
    def test_two_fails(self):
        assert len(vl.check_h1_count("<html><h1>A</h1><h1>B</h1></html>")) > 0


class TestRelativeLinks:
    def test_relative_passes(self):
        assert not vl.check_relative_links('<a href="0021-slug.html">link</a>')
    def test_absolute_slash_fails(self):
        assert len(vl.check_relative_links('<a href="/lessons/x.html">link</a>')) > 0
    def test_absolute_http_fails(self):
        assert len(vl.check_relative_links(
            '<a href="https://example.com/x.html">link</a>')) > 0


class TestQuizCorrectCount:
    def test_single_correct_passes(self):
        assert not vl.check_quiz_correct_count(
            '<div class="quiz-question"><button data-correct="true">A</button>'
            '<button data-correct="false">B</button></div>')
    def test_zero_correct_fails(self):
        assert len(vl.check_quiz_correct_count(
            '<div class="quiz-question"><button data-correct="false">A</button></div>')) > 0
    def test_two_correct_fails(self):
        assert len(vl.check_quiz_correct_count(
            '<div class="quiz-question"><button data-correct="true">A</button>'
            '<button data-correct="true">B</button></div>')) > 0
    def test_nested_divs_two_correct_fails(self):
        nested = '<div class="quiz-question"><div><button data-correct="true">A</button></div>' \
                 '<div><button data-correct="true">B</button></div></div>'
        assert len(vl.check_quiz_correct_count(nested)) > 0


class TestQuizCompleteness:
    def test_5_questions_passes(self):
        assert not vl.check_quiz_completeness(
            '<div class="quiz-question"><button class="quiz-option">A</button>'
            '<button class="quiz-option">B</button><button class="quiz-option">C</button></div>' * 5)
    def test_3_questions_fails(self):
        assert len(vl.check_quiz_completeness(
            '<div class="quiz-question"></div>' * 3)) > 0
    def test_wrong_options_count_fails(self):
        assert len(vl.check_quiz_completeness(
            '<div class="quiz-question"><button class="quiz-option">A</button>'
            '<button class="quiz-option">B</button></div>' * 5)) > 0
    def test_nested_divs_5_questions_passes(self):
        assert not vl.check_quiz_completeness(
            '<div class="quiz-question"><div><button class="quiz-option">A</button></div>'
            '<div><button class="quiz-option">B</button><button class="quiz-option">C</button></div></div>' * 5)
    def test_nested_divs_wrong_options_fails(self):
        assert len(vl.check_quiz_completeness(
            '<div class="quiz-question"><div><button class="quiz-option">A</button></div>'
            '<div><button class="quiz-option">B</button></div></div>' * 5)) > 0


class TestDataAnimSyntax:
    def test_valid_values_pass(self):
        assert not vl.check_data_anim_syntax('<div data-anim="fade-up"></div>')
    def test_invalid_value_fails(self):
        assert len(vl.check_data_anim_syntax('<div data-anim="zoom-in"></div>')) > 0
    def test_blur_is_valid(self):
        assert not vl.check_data_anim_syntax('<html><div data-anim="blur"></div></html>')
    def test_fade_up_is_valid(self):
        assert not vl.check_data_anim_syntax('<html><div data-anim="fade-up"></div></html>')
    def test_unknown_value_fails(self):
        assert len(vl.check_data_anim_syntax('<html><div data-anim="foobar"></div></html>')) > 0
    def test_shiny_text_class_detected(self):
        assert not vl.check_data_anim_syntax('<html><span class="shiny-text">hi</span></html>')
    def test_blur_in_list(self):
        assert not vl.check_data_anim_syntax(
            '<html><div data-anim="blur"></div><div data-anim="fade-up"></div></html>')


class TestPPTJS:
    def test_theme_nav_present_passes(self):
        assert not vl.check_ppt_js(
            '<html data-theme="warm"><h2>A</h2><h2>B</h2>'
            'key==="t" key==="ArrowRight" tp-btn-toggle tp-item</html>')
    def test_missing_T_key_fails(self):
        assert len(vl.check_ppt_js('<html data-theme="warm">tp-item</html>')) > 0


class TestInlineSVG:
    def test_with_wrapper_passes(self):
        assert not vl.check_inline_svg('<figure class="svg-fig"><svg xmlns="..."></svg></figure>')
    def test_no_wrapper_fails(self):
        assert len(vl.check_inline_svg('<svg xmlns="..."></svg>')) > 0
    def test_icon_svg_passes(self):
        assert not vl.check_inline_svg(
            '<button><svg width="16" height="16" viewBox="0 0 20 20"></svg></button>')
    def test_24px_icon_passes(self):
        assert not vl.check_inline_svg(
            '<span><svg width="24" height="24" viewBox="0 0 24 24"></svg></span>')
    def test_28px_icon_passes(self):
        assert not vl.check_inline_svg(
            '<span><svg width="28" height="28" viewBox="0 0 24 24"></svg></span>')
    def test_pie_chart_in_figure_passes(self):
        assert not vl.check_inline_svg(
            '<figure class="svg-fig"><svg viewBox="0 0 100 100" width="240"></svg></figure>')
    def test_pie_chart_no_figure_fails(self):
        assert len(vl.check_inline_svg(
            '<svg viewBox="0 0 100 100" width="240"></svg>')) > 0
    def test_px_unit_icon_passes(self):
        assert not vl.check_inline_svg(
            '<svg width="24px" height="24px" viewBox="0 0 24 24"></svg>')
    def test_32px_icon_passes(self):
        assert not vl.check_inline_svg(
            '<span><svg width="32" height="32" viewBox="0 0 24 24"></svg></span>')
    def test_48px_icon_passes(self):
        assert not vl.check_inline_svg(
            '<span><svg width="48" height="48" viewBox="0 0 24 24"></svg></span>')
    def test_button_icon_40px_passes(self):
        assert not vl.check_inline_svg(
            '<button><svg width="40" height="40"></svg></button>')
    def test_anchor_icon_passes(self):
        assert not vl.check_inline_svg(
            '<a href="#"><svg width="32" height="32"></svg></a>')
    def test_summary_icon_passes(self):
        assert not vl.check_inline_svg(
            '<details><summary><svg width="20" height="20"></svg></summary></details>')
    def test_in_fenced_code_passes(self):
        html = '```html\n<svg viewBox="0 0 100 100" width="200"></svg>\n```'
        assert not vl.check_inline_svg(html)
    def test_60px_outside_icon_container_fails(self):
        assert len(vl.check_inline_svg(
            '<svg viewBox="0 0 100 100" width="60"></svg>')) > 0


class TestComponentConsistency:
    def test_lightbox_trigger_target_passes(self):
        assert not vl.check_component_consistency(
            '<span data-lbox="chart-1"></span><div id="lbox-chart-1"></div>')
    def test_lightbox_no_target_fails(self):
        assert len(vl.check_component_consistency(
            '<span data-lbox="chart-1"></span>')) > 0
    def test_panel_trigger_target_passes(self):
        assert not vl.check_component_consistency(
            '<span data-panel="glossary"></span><div id="panel-glossary"></div>')
    def test_panel_no_target_fails(self):
        assert len(vl.check_component_consistency(
            '<span data-panel="glossary"></span>')) > 0
    def test_popover_trigger_target_passes(self):
        assert not vl.check_component_consistency(
            '<button popovertarget="pop-1"></button><div id="pop-1" popover></div>')
    def test_popover_no_target_fails(self):
        assert len(vl.check_component_consistency(
            '<button popovertarget="pop-1"></button>')) > 0
    def test_dialog_with_close_passes(self):
        assert not vl.check_component_consistency(
            '<dialog><button onclick="this.closest(\'dialog\').close()">x</button></dialog>')
    def test_dialog_no_close_fails(self):
        assert len(vl.check_component_consistency('<dialog></dialog>')) > 0


class TestFocusVisible:
    def test_present_passes(self):
        assert not vl.check_focus_visible('<style>:focus-visible { outline: 2px solid red; }</style>')
    def test_missing_fails(self):
        assert len(vl.check_focus_visible('<style>body { color: red; }</style>')) > 0


class TestTabularNums:
    def test_present_passes(self):
        assert not vl.check_tabular_nums(
            '<style>body { font-variant-numeric: tabular-nums; }</style>')
    def test_missing_fails(self):
        assert len(vl.check_tabular_nums('<style>body { color: red; }</style>')) > 0


class TestSemanticHTML:
    def test_article_passes(self):
        assert not vl.check_semantic_html('<html><article></article></html>')
    def test_section_passes(self):
        assert not vl.check_semantic_html('<html><section></section></html>')
    def test_nav_passes(self):
        assert not vl.check_semantic_html('<html><nav></nav></html>')
    def test_none_fails(self):
        assert len(vl.check_semantic_html('<html><div></div></html>')) > 0


class TestSPAIntegration:
    def test_lesson_with_section_passes(self, tmp_path):
        f = tmp_path / "spa.html"
        f.write_text('<section class="lesson-view" id="lesson-42"><h1>Title</h1></section>')
        assert not vl.check_spa_integration(
            '<section class="lesson-view" id="lesson-42"></section>', str(f))
    def test_missing_id_fails(self, tmp_path):
        f = tmp_path / "spa.html"
        f.write_text('<p>No lesson section here</p>')
        assert len(vl.check_spa_integration('<p>No section</p>', str(f))) > 0
    def test_index_html_with_sections_passes(self, tmp_path):
        assert not vl.check_spa_integration(
            '<section class="lesson-view" id="lesson-1"></section>'
            '<section class="lesson-view" id="lesson-2"></section>'
            '</section>', str(tmp_path / "index.html"))
    def test_index_html_missing_sections_fails(self, tmp_path):
        assert len(vl.check_spa_integration(
            '<p>hello</p>', str(tmp_path / "index.html"))) > 0
    def test_index_html_duplicate_id_fails(self, tmp_path):
        assert len(vl.check_spa_integration(
            '<section class="lesson-view" id="lesson-1"></section>'
            '<section class="lesson-view" id="lesson-1"></section>'
            '</section>', str(tmp_path / "index.html"))) > 0
    def test_KG_file_skips_SPA_check(self, tmp_path):
        assert not vl.check_spa_integration(
            'const graphData = {nodes:[]};', str(tmp_path / "kg-mine.html"))


class TestKGStructure:
    def test_non_KG_file_skips(self):
        assert not vl.check_kg_structure("<html><p>hello</p></html>", "")
    def test_minimal_valid_passes(self):
        assert not vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"第一课","category":"课程","weight":80}],'
            '"links": [{"source":"L1","target":"L1","relation":"自指"}]};', "")
    def test_missing_categories_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"nodes": [{"id":"L1","name":"第一课","category":"课程","weight":80}],'
            '"links": [{"source":"L1","target":"L1","relation":"自指"}]};', "")) > 0
    def test_empty_nodes_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [],'
            '"links": [{"source":"L1","target":"L1","relation":"自指"}]};', "")) > 0
    def test_missing_links_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"A","category":"课程","weight":80}]};', "")) > 0
    def test_node_missing_id_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"name":"A","category":"课程","weight":80}],'
            '"links": [{"source":"","target":"","relation":"x"}]};', "")) > 0
    def test_node_missing_name_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","category":"课程","weight":80}],'
            '"links": [{"source":"L1","target":"L1","relation":"x"}]};', "")) > 0
    def test_duplicate_node_id_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"A","category":"课程","weight":50},'
            '{"id":"L1","name":"B","category":"课程","weight":60}],'
            '"links": [{"source":"L1","target":"L1","relation":"x"}]};', "")) > 0
    def test_link_to_unknown_node_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"A","category":"课程","weight":50}],'
            '"links": [{"source":"L1","target":"NOEXIST","relation":"x"}]};', "")) > 0
    def test_invalid_category_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"A","category":"系统","weight":50}],'
            '"links": [{"source":"L1","target":"L1","relation":"x"}]};', "")) > 0
    def test_weight_over_100_fails(self):
        assert len(vl.check_kg_structure(
            'const graphData = {'
            '"categories": ["课程"],'
            '"nodes": [{"id":"L1","name":"A","category":"课程","weight":150}],'
            '"links": [{"source":"L1","target":"L1","relation":"x"}]};', "")) > 0
    def test_bilingual_format_passes(self):
        assert not vl.check_kg_structure(
            'var rawNodes=[{"id":"L1","nameZh":"课","nameEn":"Lesson","category":"课程","weight":50}];'
            'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
            'var catNames={"zh":["课程"],"en":["Course"]};'
            'var graphData={};', "")
    def test_bilingual_missing_nameEn_fails(self):
        assert len(vl.check_kg_structure(
            'var rawNodes=[{"id":"L1","nameZh":"课","category":"课程","weight":50}];'
            'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
            'var catNames={"zh":["课程"],"en":["Course"]};'
            'var graphData={};', "")) > 0
    def test_bilingual_missing_nameZh_fails(self):
        assert len(vl.check_kg_structure(
            'var rawNodes=[{"id":"L1","nameEn":"Lesson","category":"课程","weight":50}];'
            'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
            'var catNames={"zh":["课程"],"en":["Course"]};'
            'var graphData={};', "")) > 0


class TestBilingual:
    def test_no_data_lang_skips(self):
        assert not vl.check_bilingual("<html><p>no lang attributes</p></html>")
    def test_zh_en_btn_key_passes(self):
        assert not vl.check_bilingual(
            '<html data-lang="zh"><span data-lang="zh">中</span><span data-lang="en">EN</span>'
            '<button data-lang-btn></button>key==="l"</html>')
    def test_missing_en_fails(self):
        assert len(vl.check_bilingual(
            '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0
    def test_missing_toggle_fails(self):
        assert len(vl.check_bilingual(
            '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>'
            'key==="l"</html>')) > 0
    def test_missing_l_key_fails(self):
        assert len(vl.check_bilingual(
            '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>'
            '<button data-lang-btn></button></html>')) > 0
    def test_td_with_data_lang_passes(self):
        assert not vl.check_bilingual(
            '<html><td data-lang="zh">中</td><td data-lang="en">EN</td>'
            '<button data-lang-btn></button>key==="l"</html>')
    def test_th_with_data_lang_passes(self):
        assert not vl.check_bilingual(
            '<html><th data-lang="zh">中</th><th data-lang="en">EN</th>'
            '<button data-lang-btn></button>key==="l"</html>')


class TestLibDeps:
    def test_no_echarts_three_js_passes(self):
        assert not vl.check_lib_deps('<html><p>hello</p></html>', '.')
    def test_echarts_CDN_passes(self):
        assert not vl.check_lib_deps(
            '<html><script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js">'
            '</script>echarts.init()</html>', '.')
    def test_three_js_CDN_passes(self):
        assert not vl.check_lib_deps(
            '<html><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js">'
            '</script>new THREE.Scene()</html>', '.')
    def test_echarts_local_passes(self):
        assert not vl.check_lib_deps('<html>echarts.init()</html>', '.')
    def test_three_js_local_passes(self):
        assert not vl.check_lib_deps('<html>new THREE.Scene()</html>', '.')
    def test_echarts_no_lib_fails(self):
        assert len(vl.check_lib_deps(
            '<html>echarts.init()</html>', 'C:\\nonexistent')) > 0
    def test_three_js_no_lib_fails(self):
        assert len(vl.check_lib_deps(
            '<html>new THREE.Scene()</html>', 'C:\\nonexistent')) > 0
    def test_d3_CDN_passes(self):
        assert not vl.check_lib_deps(
            '<html><script src="https://d3js.org/d3.v7.min.js">'
            '</script>d3.forceSimulation()</html>', '.')
    def test_d3_local_passes(self):
        assert not vl.check_lib_deps('<html>d3.select("body")</html>', '.')
    def test_d3_no_lib_fails(self):
        assert len(vl.check_lib_deps(
            '<html>d3.forceSimulation()</html>', 'C:\\nonexistent')) > 0
    def test_three_js_r185_importmap_passes(self):
        assert not vl.check_lib_deps(
            '<html>cdn.jsdelivr.net/npm/three@0.185.0/ new THREE.Scene()</html>', '.')
    def test_three_js_r185_importmap_as_CDN_passes(self):
        assert not vl.check_lib_deps(
            '<html>cdn.jsdelivr.net/npm/three@0.185.0/ new THREE.Scene()</html>',
            'C:\\nonexistent')
    def test_echarts_GL_passes(self):
        assert not vl.check_lib_deps(
            '<html>type: "bar3D" scatter3D map3D globe</html>', '.')
    def test_echarts_GL_no_lib_fails(self):
        assert len(vl.check_lib_deps(
            '<html>type: "bar3D"</html>', 'C:\\nonexistent')) > 0
