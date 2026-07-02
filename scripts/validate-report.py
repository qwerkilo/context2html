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
    svgs = set(re.findall(r'<img[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<img[^>]*src=\'([^\']+\.svg(?:[?#][^\']*)?)\'', html))
    svgs.update(re.findall(r'<object[^>]*data="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<iframe[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<source[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    for src in svgs:
        if src.startswith(('http://', 'https://', 'data:')):
            continue
        path = os.path.join(base_dir, src)
        if not os.path.exists(path):
            issues.append(f"SVG not found: {src}")
        else:
            try:
                ET.parse(path)
            except Exception as e:
                issues.append(f"SVG invalid XML: {src} -- {e}")
    return issues




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
    links = re.findall(r'<a[^>]*href="([^"]+)"', html)
    for href in links:
        if href.startswith("/") or href.startswith("http"):
            issues.append(f"Absolute link found: {href} (use relative path)")
    return issues


_LIGHT_FILLS = re.compile(
    r'fill="(?:#)?(?:fef2f2|f0fdf4|eff6ff|fff7ed|ffffff|f8fafc)"', re.IGNORECASE
)
_WHITE_TEXT = re.compile(r'fill="(?:#)?(?:f{3}|f{6})"', re.IGNORECASE)


def _check_svg_content(content, issues, label):
    has_light_fill = bool(_LIGHT_FILLS.search(content))
    has_white_text = bool(_WHITE_TEXT.search(content))
    if has_light_fill and has_white_text:
        issues.append(
            f"{label}: possible white text on light background -- verify manually"
        )


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
            _check_svg_content(content, issues, src)
        except Exception:
            pass
    inline_svgs = re.findall(r'<svg[^>]*>(.*?)</svg>', html, re.DOTALL)
    for svg_content in inline_svgs:
        _check_svg_content(svg_content, issues, "Inline <svg>")
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


def _check_local_script_paths(html, base_dir, lib_name):
    """Verify any local <script src=...> referencing the lib resolves to a real file."""
    issues = []
    pattern = re.compile(
        r'<script\b[^>]*\bsrc="([^"]*)"[^>]*>', re.IGNORECASE)
    for m in pattern.finditer(html):
        src = m.group(1).strip()
        if not src or src.startswith(('http://', 'https://', '//', 'data:')):
            continue
        if lib_name not in src:
            continue
        if os.path.isabs(src):
            resolved = src
        else:
            resolved = os.path.normpath(os.path.join(base_dir, src))
        if not os.path.exists(resolved):
            issues.append(f"{lib_name} <script src=\"{src}\"> points to missing file -> {resolved}")
    return issues


def check_lib_deps(html, base_dir):
    """Verify ECharts, Three.js, D3.js lib files exist when used."""
    issues = []
    if re.search(r'echarts\.init\(', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "echarts.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/echarts" in html
        if not has_local and not has_cdn:
            issues.append("ECharts usage found but no libs/echarts.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "echarts"))
    if re.search(r'bar3D|scatter3D|map3D|[\'\"]globe[\'\"]|\'surface\'', html) or 'echarts-gl' in html:
        has_gl = os.path.exists(os.path.join(base_dir, "libs", "echarts-gl.min.js"))
        if not has_gl:
            issues.append("ECharts GL usage found but no libs/echarts-gl.min.js")
        issues.extend(_check_local_script_paths(html, base_dir, "echarts-gl"))
    if re.search(r'new THREE\.', html) or re.search(r'\bTHREE\b', html) or 'three@0.185.0' in html:
        has_local_umd = os.path.exists(os.path.join(base_dir, "libs", "three.min.js"))
        has_local_esm = os.path.exists(os.path.join(base_dir, "libs", "three.module.js"))
        has_cdn = "cdnjs.cloudflare.com/ajax/libs/three.js" in html
        has_importmap = "cdn.jsdelivr.net/npm/three@0.185.0" in html
        if not has_local_umd and not has_local_esm and not has_cdn and not has_importmap:
            issues.append("Three.js usage found but no libs/three.min.js, three.module.js, or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "three"))
    if re.search(r'd3\.(forceSimulation|hierarchy|sankey|select(?:All)?)\b', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "d3.min.js"))
        has_cdn = "d3js.org/d3" in html
        if not has_local and not has_cdn:
            issues.append("D3.js usage found but no libs/d3.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "d3"))
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


def check_theme_css(html, base_dir=None):
    """Check that report-themes.css is referenced and the file exists."""
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
    """Bar-fill elements must not exceed 100% width (would overflow container)."""
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
    """Comparison tables must collapse to stacked layout below 600px."""
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
    """English text is wider than Chinese — body needs overflow-wrap, tables need fixed layout."""
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
    """ECharts Canvas rendering ignores CSS var() — warn about direct var() usage in script."""
    issues = []
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        if ("'var(--" in s or '"var(--' in s) and 'echarts' in s:
                issues.append(
                    "ECharts script uses 'var(--xxx)' directly (Canvas2D ignores CSS var())"
                    " — use gv('--xxx') helper instead"
                )
                break
    return issues


def check_cross_refs(html):
    """Chapter cross-references should use the #chN anchor convention when used.

    Only flags refs that look like attempted chapter references (e.g. ch1-foo,
    chapter-1) but skip genuine non-chapter anchors like #chart-1 or #checklist.
    """
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
        # Report-specific
        (".exec-summary section", check_exec_summary(html)),
        (".report-chapter sections (>=1)", check_report_chapters(html)),
        (".conclusion-page section", check_conclusion_page(html)),
        (".report-footer element", check_report_footer(html)),
        # Theme
        ("theme/report-themes.css referenced", check_theme_css(html, base_dir)),
        # Visual contract
        ("Bar-fill width <= 100%", check_bar_fill_width(html)),
        ("Comparison table responsive (max-width 600-700px)", check_cmp_table_responsive(html)),
        ("English layout (overflow-wrap + table-layout:fixed)", check_english_layout(html)),
        ("ECharts var() not used directly in script", check_echarts_color_usage(html)),
        ("Chapter cross-refs use #chN anchors", check_cross_refs(html)),
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
