"""Validate a report HTML file against the report error checklist.
Usage: python validate-report.py <path-to-report.html>
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _validate_common import (
    PASS, FAIL,
    check_svg_links, check_h1_count, check_relative_links,
    check_svg_contrast, check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_gsap_modes, check_cross_refs, check_data_anim_syntax,
)
from checks.content_type import detect_content_type, check_content_type_valid
from checks.report import (
    check_exec_summary, check_report_chapters, check_conclusion_page,
    check_report_footer, check_theme_css, check_bar_fill_width,
    check_cmp_table_responsive, check_english_layout, check_echarts_color_usage,
    check_article_structure, check_doc_structure, check_tutorial_structure,
    check_note_structure,
    check_d4_connectors, check_d1_sentence_length, check_d5_term_variety,
)


def run_all(path):
    if not os.path.exists(path):
        print(f"{FAIL} File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    base_dir = os.path.dirname(path)

    ct = detect_content_type(html)
    print(f"  Content type: {ct}")

    # 通用检查（所有类型）
    checks = [
        ("SVG files exist & valid", check_svg_links(html, base_dir)),
        ("Exactly one <h1>", check_h1_count(html)),
        ("Relative links only", check_relative_links(html)),
        ("SVG text/background contrast", check_svg_contrast(html, base_dir)),
        (":focus-visible outline", check_focus_visible(html)),
        ("tabular-nums alignment", check_tabular_nums(html)),
        ("Semantic HTML elements", check_semantic_html(html)),
        ("Library deps (ECharts/Three.js)", check_lib_deps(html, base_dir)),
        ("Bilingual (data-lang zh/en + toggle)", check_bilingual(html)),
        ("Content type valid", check_content_type_valid(html)),
        ("theme/report-themes.css referenced", check_theme_css(html, base_dir)),
    ]

    # report 类型专有检查
    if ct == 'report':
        checks += [
            (".exec-summary section", check_exec_summary(html)),
            (".report-chapter sections (>=1)", check_report_chapters(html)),
            (".conclusion-page section", check_conclusion_page(html)),
            (".report-footer element", check_report_footer(html)),
        ]

    # 数据可视化相关检查（report 强制）
    if ct == 'report':
        checks += [
            ("Bar-fill width <= 100%", check_bar_fill_width(html)),
            ("Comparison table responsive (max-width 600-700px)", check_cmp_table_responsive(html)),
            ("English layout (overflow-wrap + table-layout:fixed)", check_english_layout(html)),
        ]

    # 内容类型专有结构检查
    if ct == 'article':
        checks += [("Article structure (<article> elements)", check_article_structure(html))]
    elif ct == 'doc':
        checks += [("Document structure (TOC <nav> with links)", check_doc_structure(html))]
    elif ct == 'tutorial':
        checks += [("Tutorial structure (step indicators)", check_tutorial_structure(html))]
    elif ct == 'note':
        checks += [("Note structure", check_note_structure(html))]

    # 跨内容类型通用（技术正确性）
    checks += [
        ("ECharts var() not used directly in script", check_echarts_color_usage(html)),
        ("Chapter cross-refs use #chN anchors", check_cross_refs(html)),
        ("GSAP data-gsap mode valid", check_gsap_modes(html)),
        ("data-anim syntax valid", check_data_anim_syntax(html)),
    ]

    warnings = [
        ("D1 — 句长交替 (≤10字短句 + ≥35字长句)", check_d1_sentence_length(html)),
        ("D4 — 连接词控制 (段落开头禁用 + ≤6/千字)", check_d4_connectors(html)),
        ("D5 — 术语变体 (同术语 ≤1次/800字)", check_d5_term_variety(html)),
    ]

    all_pass = True
    for label, issues in checks:
        if issues:
            all_pass = False
            print(f"  {FAIL} {label}")
            for i in issues:
                print(f"      {i}")
        else:
            print(f"  {PASS} {label}")

    for label, issues in warnings:
        if issues:
            print(f"  [!WRN] {label}")
            for i in issues:
                print(f"      {i}")
        else:
            print(f"  [PASS] {label}")

    print()
    if all_pass:
        print(f" {PASS} All checks passed for {os.path.basename(path)}")
    else:
        print(f" {FAIL} Some checks failed")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <report.html>")
        sys.exit(1)
    run_all(sys.argv[1])
