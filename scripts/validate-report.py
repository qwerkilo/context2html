"""Validate a report HTML file against the report error checklist.
Usage: python validate-report.py <path-to-report.html>
"""

import sys
import os
from dataclasses import dataclass, field

from context2html.validator import (
    PASS, FAIL,
    check_svg_links, check_h1_count, check_relative_links,
    check_svg_contrast, check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_gsap_modes, check_cross_refs, check_data_anim_syntax,
    detect_content_type, check_content_type_valid,
    check_exec_summary, check_report_chapters, check_conclusion_page,
    check_report_footer, check_theme_css, check_bar_fill_width,
    check_cmp_table_responsive, check_english_layout, check_echarts_color_usage,
    check_article_structure, check_doc_structure, check_tutorial_structure,
    check_note_structure,
    check_d4_connectors, check_d1_sentence_length, check_d5_term_variety,
    check_d2_paragraph_structure, check_d3_info_density,
)


@dataclass
class ValidationResult:
    content_type: str = ''
    checks: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    all_pass: bool = True


def build_checks(html, base_dir):
    ct = detect_content_type(html)

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

    if ct == 'report':
        checks += [
            (".exec-summary section", check_exec_summary(html)),
            (".report-chapter sections (>=1)", check_report_chapters(html)),
            (".conclusion-page section", check_conclusion_page(html)),
            (".report-footer element", check_report_footer(html)),
            ("Bar-fill width <= 100%", check_bar_fill_width(html)),
            ("Comparison table responsive (max-width 600-700px)", check_cmp_table_responsive(html)),
            ("English layout (overflow-wrap + table-layout:fixed)", check_english_layout(html)),
        ]

    if ct == 'article':
        checks += [("Article structure (<article> elements)", check_article_structure(html))]
    elif ct == 'doc':
        checks += [("Document structure (TOC <nav> with links)", check_doc_structure(html))]
    elif ct == 'tutorial':
        checks += [("Tutorial structure (step indicators)", check_tutorial_structure(html))]
    elif ct == 'note':
        checks += [("Note structure", check_note_structure(html))]

    checks += [
        ("ECharts var() not used directly in script", check_echarts_color_usage(html)),
        ("Chapter cross-refs use #chN anchors", check_cross_refs(html)),
        ("GSAP data-gsap mode valid", check_gsap_modes(html)),
        ("data-anim syntax valid", check_data_anim_syntax(html)),
    ]

    warnings = [
        ("D1 — 句长交替 (≤10字短句 + ≥35字长句)", check_d1_sentence_length(html)),
        ("D2 — 段落结构 (避免同结构相邻/总结句结尾/模板化开头)", check_d2_paragraph_structure(html)),
        ("D3 — 信息密度交替 (避免连续高密/低密段)", check_d3_info_density(html)),
        ("D4 — 连接词控制 (段落开头禁用 + ≤6/千字)", check_d4_connectors(html)),
        ("D5 — 术语变体 (同术语 ≤1次/800字)", check_d5_term_variety(html)),
    ]

    return ct, checks, warnings


def run_checks(html, base_dir):
    ct, checks, warnings = build_checks(html, base_dir)
    result = ValidationResult(content_type=ct)
    for label, issues in checks:
        result.checks.append((label, issues))
        if issues:
            result.all_pass = False
    for label, issues in warnings:
        result.warnings.append((label, issues))
    return result


def format_result(result):
    lines = [f"  Content type: {result.content_type}"]
    for label, issues in result.checks:
        if issues:
            lines.append(f"  {FAIL} {label}")
            for i in issues:
                lines.append(f"      {i}")
        else:
            lines.append(f"  {PASS} {label}")
    for label, issues in result.warnings:
        if issues:
            lines.append(f"  [!WRN] {label}")
            for i in issues:
                lines.append(f"      {i}")
        else:
            lines.append(f"  [PASS] {label}")
    lines.append("")
    if result.all_pass:
        lines.append(f" {PASS} All checks passed")
    else:
        lines.append(f" {FAIL} Some checks failed")
    return "\n".join(lines)


def run_all(path):
    if not os.path.exists(path):
        print(f"{FAIL} File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    base_dir = os.path.dirname(path)
    result = run_checks(html, base_dir)
    print(format_result(result))

    if not result.all_pass:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <report.html>")
        sys.exit(1)
    run_all(sys.argv[1])
