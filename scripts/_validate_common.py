"""Shared validation functions for report and lesson HTML files."""

import os
import re
import xml.etree.ElementTree as ET

PASS = "[PASS]"
FAIL = "[FAIL]"

_LIGHT_FILLS = re.compile(
    r'fill="(?:#)?(?:fef2f2|f0fdf4|eff6ff|fff7ed|ffffff|f8fafc)"', re.IGNORECASE
)
_WHITE_TEXT = re.compile(r'fill="(?:#)?(?:f{3}|f{6})"', re.IGNORECASE)

_VALID_GSAP_MODES = {"fade", "stagger", "parallax", "flip", "zoom"}


def check_svg_links(html, base_dir):
    issues = []
    svgs = set(re.findall(r'<img[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<img[^>]*src=\'([^\']+\.svg(?:[?#][^\']*)?)\'', html))
    svgs.update(re.findall(r'<object[^>]*data="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<object[^>]*data=\'([^\']+\.svg(?:[?#][^\']*)?)\'', html))
    svgs.update(re.findall(r'<iframe[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<iframe[^>]*src=\'([^\']+\.svg(?:[?#][^\']*)?)\'', html))
    svgs.update(re.findall(r'<source[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"', html))
    svgs.update(re.findall(r'<source[^>]*src=\'([^\']+\.svg(?:[?#][^\']*)?)\'', html))
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
    h1s = re.findall(r"<h1[^>]*>", html)
    lang_h1s = re.findall(r'<h1[^>]*data-lang=["\']([^"\']+)["\']', html)
    if lang_h1s:
        if len(h1s) == len(set(lang_h1s)):
            return []
    if len(h1s) != 1:
        return [f"Found {len(h1s)} h1 tags (expected 1, or 1 per language with data-lang)"]
    return []


def check_relative_links(html):
    issues = []
    for href in re.findall(r'<a[^>]*href="([^"]+)"', html):
        if href.startswith("/") or href.startswith("http"):
            issues.append(f"Absolute link found: {href} (use relative path)")
    return issues


def _check_svg_content(content, issues, label):
    if bool(_LIGHT_FILLS.search(content)) and bool(_WHITE_TEXT.search(content)):
        issues.append(
            f"{label}: possible white text on light background -- verify manually"
        )


def check_svg_contrast(html, base_dir):
    issues = []
    for src in re.findall(r'<img[^>]*src="([^"]+\.svg)"', html):
        path = os.path.join(base_dir, src)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                _check_svg_content(f.read(), issues, src)
        except Exception:
            pass
    for svg_content in re.findall(r'<svg[^>]*>(.*?)</svg>', html, re.DOTALL):
        _check_svg_content(svg_content, issues, "Inline <svg>")
    return issues


def check_focus_visible(html):
    if not re.search(r":focus-visible", html):
        return ["Missing :focus-visible outline rule"]
    return []


def check_tabular_nums(html):
    if not re.search(r"tabular-nums", html):
        return ["Missing font-variant-numeric: tabular-nums"]
    return []


def check_semantic_html(html):
    for tag in ("<article", "<section", "<nav", "<aside", "<main"):
        if tag in html:
            return []
    return ["No semantic HTML elements found (use <article>/<section>/<nav>/<aside>)"]


def _check_local_script_paths(html, base_dir, lib_name):
    issues = []
    for m in re.finditer(r'<script\b[^>]*\bsrc="([^"]*)"[^>]*>', html, re.IGNORECASE):
        src = m.group(1).strip()
        if not src or src.startswith(('http://', 'https://', '//', 'data:')):
            continue
        if lib_name not in src:
            continue
        resolved = src if os.path.isabs(src) else os.path.normpath(os.path.join(base_dir, src))
        if not os.path.exists(resolved):
            issues.append(f"{lib_name} <script src=\"{src}\"> points to missing file -> {resolved}")
    return issues


def check_lib_deps(html, base_dir):
    issues = []
    if re.search(r'echarts\.init\(', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "echarts.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/echarts" in html
        if not has_local and not has_cdn:
            issues.append("ECharts usage found but no libs/echarts.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "echarts"))
    if re.search(r'bar3D|scatter3D|map3D|[\'\"]globe[\'\"]|[\'\"]surface[\'\"]', html) or 'echarts-gl' in html:
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
    if re.search(r'data-gsap|gsap\.registerPlugin|gsap\.(to|from|fromTo)\b', html):
        has_local_gsap = os.path.exists(os.path.join(base_dir, "libs", "gsap.min.js"))
        has_local_st = os.path.exists(os.path.join(base_dir, "libs", "ScrollTrigger.min.js"))
        has_cdn = "cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/" in html
        if not has_local_gsap and not has_cdn:
            issues.append("GSAP usage found but no libs/gsap.min.js or CDN link")
        if not has_local_st and not has_cdn:
            issues.append("GSAP usage found but no libs/ScrollTrigger.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "gsap"))
        issues.extend(_check_local_script_paths(html, base_dir, "ScrollTrigger"))
    if re.search(r'\bSVG\(|\bSVG\.|draw\.SVG\b|svgdotjs', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "svg.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/@svgdotjs/svg.js" in html or "svgjs.in" in html
        if not has_local and not has_cdn:
            issues.append("SVG.js usage found but no libs/svg.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "svg.min.js"))
    return issues


def check_bilingual(html):
    issues = []
    has_zh = 'data-lang="zh"' in html
    has_en = 'data-lang="en"' in html
    has_toggle = 'data-lang-btn' in html
    # Accept: key==='l', key==="l", e.key==='l', e.key === 'l' (with optional spaces)
    has_l_key = bool(re.search(
        r"(?:e\.?key|e\.?key\s*===?\s*)['\"]l['\"]",
        html, re.IGNORECASE
    )) or "key==='l'" in html or 'key==="l"' in html

    if not has_zh and not has_en:
        return []

    if not has_zh:
        issues.append('Missing data-lang="zh" (Chinese content)')
    if not has_en:
        issues.append('Missing data-lang="en" (English content)')
    if not has_toggle:
        issues.append("Missing language toggle button ([data-lang-btn])")
    if not has_l_key:
        issues.append("Missing L key handler for language switching")

    # Count zh/en occurrences to detect unbalanced pairs
    # Exclude data-lang on <html> tag (page language, not bilingual content)
    zh_count = len(re.findall(r'data-lang="zh"', html))
    en_count = len(re.findall(r'data-lang="en"', html))
    if re.search(r'<html[^>]*data-lang="zh"', html):
        zh_count -= 1
    if re.search(r'<html[^>]*data-lang="en"', html):
        en_count -= 1
    if has_zh and has_en and zh_count != en_count:
        issues.append(
            f"Unbalanced bilingual pairs: {zh_count} zh vs {en_count} en "
            "(each content block must have both language versions)"
        )

    return issues


def check_cross_refs(html):
    """Check that chapter cross-references use canonical #chN format."""
    bad_refs = []
    for ref in re.findall(r'href="#([^"#?]+)"', html):
        if re.match(r'^(?:ch\d+\D|chapter[\d-])', ref, re.IGNORECASE):
            bad_refs.append(ref)
    if bad_refs:
        return [f"Non-canonical chapter refs (expected #chN where N is a number): {', '.join(bad_refs)}"]
    return []


_VALID_DATA_ANIM = {'fade-up', 'fade', 'slide-left', 'blur'}


def check_data_anim_syntax(html):
    """Check that all data-anim values are valid CSS-recognized values."""
    bad = [a for a in re.findall(r'data-anim="([^"]+)"', html)
           if a not in _VALID_DATA_ANIM]
    if bad:
        return [f"Invalid data-anim values: {set(bad)} (valid: {', '.join(sorted(_VALID_DATA_ANIM))})"]
    return []


def check_gsap_modes(html):
    issues = []
    for m in re.finditer(r'data-gsap="([^"]*)"', html):
        val = m.group(1)
        if val not in _VALID_GSAP_MODES:
            issues.append(f"Invalid data-gsap value \"{val}\" (valid: {', '.join(sorted(_VALID_GSAP_MODES))})")
    return issues
