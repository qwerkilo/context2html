"""context2html Validator — report validation API."""

from context2html.validator.common import (
    PASS, FAIL,
    check_h1_count, check_relative_links,
    check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_cross_refs, check_data_anim_syntax, check_gsap_modes,
)
from context2html.validator.svg import check_svg_links, check_svg_contrast
from context2html.validator.content_type import detect_content_type, check_content_type_valid
from context2html.validator.report import (
    check_exec_summary, check_report_chapters, check_conclusion_page,
    check_report_footer, check_theme_css, check_bar_fill_width,
    check_cmp_table_responsive, check_english_layout, check_echarts_color_usage,
    check_article_structure, check_doc_structure, check_tutorial_structure,
    check_note_structure,
    check_d4_connectors, check_d1_sentence_length, check_d5_term_variety,
    check_d2_paragraph_structure, check_d3_info_density,
)
