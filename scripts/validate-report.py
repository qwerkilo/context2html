"""Validate a report HTML file against the report error checklist.
Usage: python validate-report.py <path-to-report.html>
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _validate_common import (
    PASS, FAIL,
    check_svg_links, check_h1_count, check_relative_links,
    check_svg_contrast, check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_gsap_modes,
)


# ========== Report-specific checks ==========


def check_exec_summary(html):
    if '.exec-summary' not in html:
        return ["Missing .exec-summary section (required: key findings summary)"]
    return []


def check_report_chapters(html):
    chapters = re.findall(r'class="[^"]*report-chapter[^"]*"', html)
    if len(chapters) < 1:
        return [f"Found {len(chapters)} .report-chapter elements (expected at least 1)"]
    return []


def check_conclusion_page(html):
    if '.conclusion-page' not in html:
        return ["Missing .conclusion-page section (required: conclusions & recommendations)"]
    return []


def check_report_footer(html):
    if '.report-footer' not in html:
        return ["Missing .report-footer element (required: report footer)"]
    return []


def check_theme_css(html, base_dir=None):
    issues = []
    refs = re.findall(r'href="([^"]*report-themes\.css)"', html)
    if not refs:
        return ["Missing <link> to theme/report-themes.css"]
    for ref in refs:
        if ref.startswith("http"):
            issues.append(f"Theme CSS from CDN/URL: {ref} (prefer local)")
            continue
        if base_dir and not os.path.isabs(ref):
            resolved = os.path.normpath(os.path.join(base_dir, ref))
            if not os.path.exists(resolved):
                issues.append(f"Theme CSS link points to missing file: {ref} -> {resolved}")
    return issues


def check_bar_fill_width(html):
    issues = []
    overflow = []
    for pat in [
        r'class="[^"]*(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^"]*"[^>]*style="([^"]*)"',
        r'style="([^"]*)"[^>]*class="[^"]*(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^"]*"',
    ]:
        for m in re.finditer(pat, html):
            style = m.group(1)
            wm = re.search(r'width\s*:\s*(\d+(?:\.\d+)?)\s*%', style)
            if wm and float(wm.group(1)) > 100:
                overflow.append(f"{wm.group(1)}%")
    style_block = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    if style_block:
        css = style_block.group(1)
        for m in re.finditer(r'\.(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^{]*\{[^}]*width\s*:\s*(\d+(?:\.\d+)?)\s*%\s*;', css):
            if float(m.group(1)) > 100:
                overflow.append(f"{m.group(1)}% (CSS rule)")
    if overflow:
        issues.append(f"Bar-fill width exceeds 100%: {', '.join(overflow)}")
    return issues


def check_cmp_table_responsive(html):
    if '.cmp-table' not in html:
        return []
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    if not style_blocks:
        return [".cmp-table used but no <style> block found for responsive rules"]
    all_css = '\n'.join(style_blocks)
    narrow_breaks = list(re.finditer(
        r'@media\s*\([^)]*max-width\s*:\s*(\d+)px[^)]*\)\s*\{',
        all_css,
    ))
    covers_table = False
    for mb in narrow_breaks:
        bp = int(mb.group(1))
        if bp > 700:
            continue
        open_brace = mb.end()
        depth = 1
        cursor = open_brace
        max_depth = 100
        while cursor < len(all_css) and depth > 0 and max_depth > 0:
            ch = all_css[cursor]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            cursor += 1
        body = all_css[open_brace:cursor - 1]
        if '.cmp-table' in body:
            covers_table = True
            break
    if not covers_table:
        return [".cmp-table used but no @media (max-width: 700px) rule covers it (narrow screens won't stack)"]
    return []


def check_english_layout(html):
    issues = []
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    all_css = '\n'.join(style_blocks)
    if 'overflow-wrap: break-word' not in all_css and 'overflow-wrap:break-word' not in all_css:
        issues.append("Missing overflow-wrap: break-word on body (English text may overflow)")
    if '.cmp-table' in html:
        has_fixed = False
        for m in re.finditer(r'\.cmp-table[^{]*\{([^}]*)\}', all_css):
            if 'table-layout: fixed' in m.group(1) or 'table-layout:fixed' in m.group(1):
                has_fixed = True
                break
        if not has_fixed:
            issues.append(".cmp-table missing table-layout: fixed (English text may expand columns)")
    return issues


def check_echarts_color_usage(html):
    issues = []
    for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        if ("'var(--" in s or '"var(--' in s) and 'echarts' in s:
            issues.append(
                "ECharts script uses 'var(--xxx)' directly (Canvas2D ignores CSS var())"
                " — use gv('--xxx') helper instead"
            )
            break
    return issues


def check_cross_refs(html):
    bad_refs = []
    for ref in re.findall(r'href="#([^"#?]+)"', html):
        if re.match(r'^(?:ch\d+\D|chapter[\d-])', ref, re.IGNORECASE):
            bad_refs.append(ref)
    if bad_refs:
        return [f"Non-canonical chapter refs (expected #chN where N is a number): {', '.join(bad_refs)}"]
    return []


def run_all(path):
    if not os.path.exists(path):
        print(f"{FAIL} File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    base_dir = os.path.dirname(path)

    results = [
        ("SVG files exist & valid", check_svg_links(html, base_dir)),
        ("Exactly one <h1>", check_h1_count(html)),
        ("Relative links only", check_relative_links(html)),
        ("SVG text/background contrast", check_svg_contrast(html, base_dir)),
        (":focus-visible outline", check_focus_visible(html)),
        ("tabular-nums alignment", check_tabular_nums(html)),
        ("Semantic HTML elements", check_semantic_html(html)),
        ("Library deps (ECharts/Three.js)", check_lib_deps(html, base_dir)),
        ("Bilingual (data-lang zh/en + toggle)", check_bilingual(html)),
        (".exec-summary section", check_exec_summary(html)),
        (".report-chapter sections (>=1)", check_report_chapters(html)),
        (".conclusion-page section", check_conclusion_page(html)),
        (".report-footer element", check_report_footer(html)),
        ("theme/report-themes.css referenced", check_theme_css(html, base_dir)),
        ("Bar-fill width <= 100%", check_bar_fill_width(html)),
        ("Comparison table responsive (max-width 600-700px)", check_cmp_table_responsive(html)),
        ("English layout (overflow-wrap + table-layout:fixed)", check_english_layout(html)),
        ("ECharts var() not used directly in script", check_echarts_color_usage(html)),
        ("Chapter cross-refs use #chN anchors", check_cross_refs(html)),
        ("GSAP data-gsap mode valid", check_gsap_modes(html)),
    ]

    all_pass = True
    for label, issues in results:
        if issues:
            all_pass = False
            print(f"  {FAIL} {label}")
            for i in issues:
                print(f"      {i}")
        else:
            print(f"  {PASS} {label}")

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
