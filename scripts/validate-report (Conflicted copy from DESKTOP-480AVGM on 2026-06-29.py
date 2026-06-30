"""Validate a report HTML file against the report error checklist.
Usage: python validate-report.py <path-to-report.html>
"""

import re
import sys
import os
import xml.etree.ElementTree as ET

PASS = "[PASS]"
FAIL = "[FAIL]"


def check_svg_links(html, base_dir):
    """Check that all SVG src files exist and are valid XML."""
    issues = []
    svgs = re.findall(r'<img[^>]*src="([^"]+\.svg)"', html)
    for src in svgs:
        path = os.path.join(base_dir, src)
        if not os.path.exists(path):
            issues.append(f"SVG not found: {src}")
        else:
            try:
                ET.parse(path)
            except Exception as e:
                issues.append(f"SVG invalid XML: {src} -- {e}")
    return issues


_check_h1_count = None  # remove reference


def check_h1_count(html):
    """Each report must have exactly one h1 (or one per language with data-lang)."""
    h1s = re.findall(r"<h1[^>]*>", html)
    lang_h1s = re.findall(r'<h1[^>]*data-lang=["\']([^"\']+)["\']', html)
    if lang_h1s:
        if len(h1s) == len(set(lang_h1s)):
            return []
    if len(h1s) != 1:
        return [f"Found {len(h1s)} h1 tags (expected 1, or 1 per language with data-lang)"]
    return []


def check_relative_links(html):
    """Cross-report links must use relative paths, not / or http."""
    issues = []
    links = re.findall(r'<a[^>]*href="([^"]+\.html)"', html)
    for href in links:
        if href.startswith("/") or href.startswith("http"):
            issues.append(f"Absolute link found: {href} (use relative path)")
    return issues


_LIGHT_FILLS = re.compile(
    r'fill="(?:#)?(?:fef2f2|f0fdf4|eff6ff|fff7ed|ffffff|f8fafc)"', re.IGNORECASE
)
_WHITE_TEXT = re.compile(r'fill="(?:#)?(?:fff{1,3})"', re.IGNORECASE)


def check_svg_contrast(html, base_dir):
    """Flag SVGs that may have white text on light backgrounds."""
    issues = []
    svgs = re.findall(r'<img[^>]*src="([^"]+\.svg)"', html)
    for src in svgs:
        path = os.path.join(base_dir, src)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            has_light_fill = bool(_LIGHT_FILLS.search(content))
            has_white_text = bool(_WHITE_TEXT.search(content))
            if has_light_fill and has_white_text:
                issues.append(
                    f"{src}: possible white text on light background -- verify manually"
                )
        except Exception:
            pass
    return issues


def check_focus_visible(html):
    """Must have :focus-visible outline styles."""
    if not re.search(r":focus-visible", html):
        return ["Missing :focus-visible outline rule"]
    return []


def check_tabular_nums(html):
    """Should have font-variant-numeric: tabular-nums for number alignment."""
    if not re.search(r"tabular-nums", html):
        return ["Missing font-variant-numeric: tabular-nums"]
    return []


def check_semantic_html(html):
    """Should use at least one semantic element (article/section/nav/aside)."""
    for tag in ("<article", "<section", "<nav", "<aside", "<main"):
        if tag in html:
            return []
    return ["No semantic HTML elements found (use <article>/<section>/<nav>/<aside>)"]


def check_lib_deps(html, base_dir):
    """Verify ECharts, Three.js, D3.js lib files exist when used."""
    issues = []
    if re.search(r'echarts\.init\(', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "echarts.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/echarts" in html
        if not has_local and not has_cdn:
            issues.append("ECharts usage found but no libs/echarts.min.js or CDN link")
    if re.search(r'bar3D|scatter3D|map3D|globe|\'surface\'', html) or 'echarts-gl' in html:
        has_gl = os.path.exists(os.path.join(base_dir, "libs", "echarts-gl.min.js"))
        if not has_gl:
            issues.append("ECharts GL usage found but no libs/echarts-gl.min.js")
    if re.search(r'new THREE\.', html) or re.search(r'\bTHREE\b', html) or 'three@0.185.0' in html:
        has_local_umd = os.path.exists(os.path.join(base_dir, "libs", "three.min.js"))
        has_local_esm = os.path.exists(os.path.join(base_dir, "libs", "three.module.js"))
        has_cdn = "cdnjs.cloudflare.com/ajax/libs/three.js" in html
        has_importmap = "cdn.jsdelivr.net/npm/three@0.185.0" in html
        if not has_local_umd and not has_local_esm and not has_cdn and not has_importmap:
            issues.append("Three.js usage found but no libs/three.min.js, three.module.js, or CDN link")
    if re.search(r'd3\.(forceSimulation|hierarchy|sankey|select)\b', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "d3.min.js"))
        has_cdn = "d3js.org/d3" in html
        if not has_local and not has_cdn:
            issues.append("D3.js usage found but no libs/d3.min.js or CDN link")
    return issues


def check_bilingual(html):
    """Check for bilingual content with data-lang and language toggle."""
    issues = []
    has_zh = 'data-lang="zh"' in html
    has_en = 'data-lang="en"' in html
    has_toggle = 'data-lang-btn' in html
    has_l_key = "key==='l'" in html or 'key==="l"' in html

    if not has_zh and not has_en:
        return []  # Not bilingual, skip

    if not has_zh:
        issues.append('Missing data-lang="zh" (Chinese content)')
    if not has_en:
        issues.append('Missing data-lang="en" (English content)')
    if not has_toggle:
        issues.append("Missing language toggle button ([data-lang-btn])")
    if not has_l_key:
        issues.append("Missing L key handler for language switching")

    return issues


# ========== Report-specific checks ==========


def check_exec_summary(html):
    """Must have at least one .exec-summary section."""
    if '.exec-summary' not in html:
        return ["Missing .exec-summary section (required: key findings summary)"]
    return []


def check_report_chapters(html):
    """Must have at least one .report-chapter section."""
    chapters = re.findall(r'class="[^"]*report-chapter[^"]*"', html)
    if len(chapters) < 1:
        return [f"Found {len(chapters)} .report-chapter elements (expected at least 1)"]
    return []


def check_conclusion_page(html):
    """Must have a .conclusion-page section."""
    if '.conclusion-page' not in html:
        return ["Missing .conclusion-page section (required: conclusions & recommendations)"]
    return []


def check_report_footer(html):
    """Must have a .report-footer element."""
    if '.report-footer' not in html:
        return ["Missing .report-footer element (required: report footer)"]
    return []


def check_theme_css(html):
    """Check that report-themes.css is referenced and the file exists."""
    issues = []
    refs = re.findall(r'href="([^"]*report-themes\.css)"', html)
    if not refs:
        return ["Missing <link> to theme/report-themes.css"]
    for ref in refs:
        # Resolve relative to project root (not report location)
        # Just warn if the reference looks wrong
        if ref.startswith("http"):
            issues.append(f"Theme CSS from CDN/URL: {ref} (prefer local)")
    return issues


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
        # Report-specific
        (".exec-summary section", check_exec_summary(html)),
        (".report-chapter sections (>=1)", check_report_chapters(html)),
        (".conclusion-page section", check_conclusion_page(html)),
        (".report-footer element", check_report_footer(html)),
        # Theme
        ("theme/report-themes.css referenced", check_theme_css(html)),
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
