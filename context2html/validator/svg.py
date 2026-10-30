"""SVG-related validation checks — framework package."""

import os
import re

try:  # defusedxml guards against entity-expansion attacks on untrusted SVG
    from defusedxml import ElementTree as ET
except ImportError:  # pragma: no cover - optional dependency
    import xml.etree.ElementTree as ET

_LIGHT_FILLS = re.compile(
    r'fill="(?:#)?(?:fef2f2|f0fdf4|eff6ff|fff7ed|ffffff|f8fafc)"', re.IGNORECASE
)
_WHITE_TEXT = re.compile(r'fill="(?:#)?(?:f{3}|f{6})"', re.IGNORECASE)


def _safe_path(base_dir, src):
    """Resolve `src` under `base_dir`, or return None if it escapes it."""
    base = os.path.realpath(base_dir)
    path = os.path.realpath(os.path.join(base, src))
    try:
        if os.path.commonpath([base, path]) != base:
            return None
    except ValueError:  # different drives on Windows
        return None
    return path


_RE_IMG_SVG = re.compile(r'<img[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"')
_RE_IMG_SVG_S = re.compile(r"<img[^>]*src='([^']+\.svg(?:[?#][^']*)?)'")
_RE_OBJ_SVG = re.compile(r'<object[^>]*data="([^"]+\.svg(?:[?#][^"]*)?)"')
_RE_OBJ_SVG_S = re.compile(r"<object[^>]*data='([^']+\.svg(?:[?#][^']*)?)'")
_RE_IFRAME_SVG = re.compile(r'<iframe[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"')
_RE_IFRAME_SVG_S = re.compile(r"<iframe[^>]*src='([^']+\.svg(?:[?#][^']*)?)'")
_RE_SOURCE_SVG = re.compile(r'<source[^>]*src="([^"]+\.svg(?:[?#][^"]*)?)"')
_RE_SOURCE_SVG_S = re.compile(r"<source[^>]*src='([^']+\.svg(?:[?#][^']*)?)'")


def check_svg_links(html, base_dir):
    issues = []
    svgs = set(_RE_IMG_SVG.findall(html))
    svgs.update(_RE_IMG_SVG_S.findall(html))
    svgs.update(_RE_OBJ_SVG.findall(html))
    svgs.update(_RE_OBJ_SVG_S.findall(html))
    svgs.update(_RE_IFRAME_SVG.findall(html))
    svgs.update(_RE_IFRAME_SVG_S.findall(html))
    svgs.update(_RE_SOURCE_SVG.findall(html))
    svgs.update(_RE_SOURCE_SVG_S.findall(html))
    for src in svgs:
        if src.startswith(('http://', 'https://', 'data:')):
            continue
        path = _safe_path(base_dir, src)
        if path is None:
            issues.append(f"SVG path escapes report directory: {src}")
            continue
        if not os.path.exists(path):
            issues.append(f"SVG not found: {src}")
        else:
            try:
                ET.parse(path)
            except Exception as e:
                issues.append(f"SVG invalid XML: {src} -- {e}")
    return issues


def _check_svg_content(content, issues, label):
    if bool(_LIGHT_FILLS.search(content)) and bool(_WHITE_TEXT.search(content)):
        issues.append(
            f"{label}: possible white text on light background -- verify manually"
        )


def check_svg_contrast(html, base_dir):
    issues = []
    for src in re.findall(r'<img[^>]*src="([^"]+\.svg)"', html):
        path = _safe_path(base_dir, src)
        if path is None or not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                _check_svg_content(f.read(), issues, src)
        except Exception:
            pass
    for svg_content in re.findall(r'<svg[^>]*>(.*?)</svg>', html, re.DOTALL):
        _check_svg_content(svg_content, issues, "Inline <svg>")
    return issues
