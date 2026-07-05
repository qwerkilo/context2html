"""Shared validation helpers — barrel re-export module."""

import os
import re
import xml.etree.ElementTree as ET

from checks.svg import check_svg_links, check_svg_contrast

PASS = "[PASS]"
FAIL = "[FAIL]"

_VALID_GSAP_MODES = {"fade", "stagger", "parallax", "flip", "zoom"}

_RE_H1_TAG = re.compile(r"<h1[^>]*>")
_RE_H1_LANG = re.compile(r'<h1[^>]*data-lang=["\']([^"\']+)["\']')
_RE_A_HREF = re.compile(r'<a[^>]*href="([^"]+)"')
_RE_FOCUS_VISIBLE = re.compile(r":focus-visible")
_RE_TABULAR_NUMS = re.compile(r"tabular-nums")
_RE_ECHARTS_INIT = re.compile(r'echarts\.init\(')
_RE_ECHARTS_GL = re.compile(r'\b(?:bar3D|scatter3D|map3D)\b|[\'\"]globe[\'\"]|[\'\"]surface[\'\"]')
_RE_GSAP_USAGE = re.compile(r'data-gsap|gsap\.registerPlugin|gsap\.(to|from|fromTo)\b')
_RE_D3_USAGE = re.compile(r'd3\.(forceSimulation|hierarchy|sankey|select(?:All)?)\b')
_RE_SVGJS_USAGE = re.compile(r'\bSVG\(|\bSVG\.|draw\.SVG\b|svgdotjs')
_RE_GSAP_DATA = re.compile(r'data-gsap="([^"]*)"')
_RE_DATA_ANIM = re.compile(r'data-anim="([^"]+)"')
_RE_THREE_USAGE = re.compile(r'new THREE\.')
_RE_THREE_BARE = re.compile(r'\bTHREE\b')
_RE_SCRIPT_SRC = re.compile(r'<script\b[^>]*\bsrc="([^"]*)"[^>]*>', re.IGNORECASE)

_REPO_CDN = "cdn.jsdelivr.net/gh/qwerkilo/context2html"
_RE_LOADLIB = re.compile(r"__loadLib\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")

_VALID_DATA_ANIM = {'fade-up', 'fade', 'slide-left', 'blur'}


def check_h1_count(html):
    h1s = _RE_H1_TAG.findall(html)
    lang_h1s = _RE_H1_LANG.findall(html)
    if lang_h1s:
        if len(h1s) == len(set(lang_h1s)):
            return []
    if len(h1s) != 1:
        return [f"Found {len(h1s)} h1 tags (expected 1, or 1 per language with data-lang)"]
    return []


def check_relative_links(html):
    issues = []
    for href in _RE_A_HREF.findall(html):
        if href.startswith("/") or href.startswith("http"):
            issues.append(f"Absolute link found: {href} (use relative path)")
    return issues


def check_focus_visible(html):
    if not _RE_FOCUS_VISIBLE.search(html):
        return ["Missing :focus-visible outline rule"]
    return []


def check_tabular_nums(html):
    if not _RE_TABULAR_NUMS.search(html):
        return ["Missing font-variant-numeric: tabular-nums"]
    return []


def check_semantic_html(html):
    for tag in ("<article", "<section", "<nav", "<aside", "<main"):
        if tag in html:
            return []
    return ["No semantic HTML elements found (use <article>/<section>/<nav>/<aside>)"]


def _check_local_script_paths(html, base_dir, lib_name):
    issues = []
    for m in _RE_SCRIPT_SRC.finditer(html):
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
    has_repo_cdn = _REPO_CDN in html
    if _RE_ECHARTS_INIT.search(html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "echarts.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/echarts" in html or has_repo_cdn
        if not has_local and not has_cdn:
            issues.append("ECharts usage found but no libs/echarts.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "echarts"))
    if _RE_ECHARTS_GL.search(html) or 'echarts-gl' in html:
        has_gl = os.path.exists(os.path.join(base_dir, "libs", "echarts-gl.min.js"))
        if not has_gl:
            issues.append("ECharts GL usage found but no libs/echarts-gl.min.js")
        issues.extend(_check_local_script_paths(html, base_dir, "echarts-gl"))
    if _RE_THREE_USAGE.search(html) or _RE_THREE_BARE.search(html) or 'three@0.185.0' in html:
        has_local_umd = os.path.exists(os.path.join(base_dir, "libs", "three.min.js"))
        has_local_esm = os.path.exists(os.path.join(base_dir, "libs", "three.module.js"))
        has_cdn = "cdnjs.cloudflare.com/ajax/libs/three.js" in html or has_repo_cdn
        has_importmap = "cdn.jsdelivr.net/npm/three@0.185.0" in html
        if not has_local_umd and not has_local_esm and not has_cdn and not has_importmap:
            issues.append("Three.js usage found but no libs/three.min.js, three.module.js, or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "three"))
    if _RE_D3_USAGE.search(html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "d3.min.js"))
        has_cdn = "d3js.org/d3" in html or has_repo_cdn
        if not has_local and not has_cdn:
            issues.append("D3.js usage found but no libs/d3.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "d3"))
    if _RE_GSAP_USAGE.search(html):
        has_local_gsap = os.path.exists(os.path.join(base_dir, "libs", "gsap.min.js"))
        has_local_st = os.path.exists(os.path.join(base_dir, "libs", "ScrollTrigger.min.js"))
        has_cdn = bool(re.search(r'cdnjs\.cloudflare\.com/ajax/libs/gsap/\d+\.\d+\.\d+/', html)) or has_repo_cdn
        if not has_local_gsap and not has_cdn:
            issues.append("GSAP usage found but no libs/gsap.min.js or CDN link")
        if not has_local_st and not has_cdn:
            issues.append("GSAP usage found but no libs/ScrollTrigger.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "gsap"))
        issues.extend(_check_local_script_paths(html, base_dir, "ScrollTrigger"))
    if _RE_SVGJS_USAGE.search(html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "svg.min.js"))
        has_cdn = "cdn.jsdelivr.net/npm/@svgdotjs/svg.js" in html or "svgjs.in" in html or has_repo_cdn
        if not has_local and not has_cdn:
            issues.append("SVG.js usage found but no libs/svg.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "svg.min.js"))
    if has_repo_cdn:
        for m in _RE_LOADLIB.finditer(html):
            lib_name = m.group(1)
            local_path = os.path.join(base_dir, "libs", lib_name)
            if not os.path.exists(local_path):
                issues.append(
                    f"__loadLib references '{lib_name}' but local libs/{lib_name} not found"
                    f" (required for fallback)"
                )
    return issues


def check_bilingual(html):
    issues = []
    has_zh = 'data-lang="zh"' in html
    has_en = 'data-lang="en"' in html
    has_toggle = 'data-lang-btn' in html
    has_l_key = bool(re.search(
        r"e\.key\s*===\s*['\"]l['\"]",
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
    bad_refs = []
    for ref in re.findall(r'href="#([^"#?]+)"', html):
        if re.match(r'^(?:ch\d+\D|chapter[\d-])', ref, re.IGNORECASE):
            bad_refs.append(ref)
    if bad_refs:
        return [f"Non-canonical chapter refs (expected #chN where N is a number): {', '.join(bad_refs)}"]
    return []


def check_data_anim_syntax(html):
    bad = [a for a in _RE_DATA_ANIM.findall(html)
           if a not in _VALID_DATA_ANIM]
    if bad:
        return [f"Invalid data-anim values: {set(bad)} (valid: {', '.join(sorted(_VALID_DATA_ANIM))})"]
    return []


def check_gsap_modes(html):
    issues = []
    for m in _RE_GSAP_DATA.finditer(html):
        val = m.group(1)
        if val not in _VALID_GSAP_MODES:
            issues.append(f"Invalid data-gsap value \"{val}\" (valid: {', '.join(sorted(_VALID_GSAP_MODES))})")
    return issues
