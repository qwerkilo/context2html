"""Validate a report HTML file against the report error checklist.
Usage: python validate-report.py <path-to-report.html>
"""

import re
import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _validate_common import (
    PASS, FAIL,
    check_svg_links, check_h1_count, check_relative_links,
    check_svg_contrast, check_focus_visible, check_tabular_nums,
    check_semantic_html, check_lib_deps, check_bilingual,
    check_gsap_modes, check_cross_refs, check_data_anim_syntax,
)


# ========== Report-specific checks ==========


def check_exec_summary(html):
    if not re.search(r'class="[^"]*\bexec-summary\b[^"]*"', html) and \
       not re.search(r"class='[^']*\bexec-summary\b[^']*'", html):
        return ["Missing .exec-summary section (required: key findings summary)"]
    return []


def check_report_chapters(html):
    chapters = re.findall(r'class="[^"]*report-chapter[^"]*"', html)
    if len(chapters) < 1:
        return [f"Found {len(chapters)} .report-chapter elements (expected at least 1)"]
    return []


def check_conclusion_page(html):
    if not re.search(r'class="[^"]*\bconclusion-page\b[^"]*"', html) and \
       not re.search(r"class='[^']*\bconclusion-page\b[^']*'", html):
        return ["Missing .conclusion-page section (required: conclusions & recommendations)"]
    return []


def check_report_footer(html):
    if not re.search(r'class="[^"]*\breport-footer\b[^"]*"', html) and \
       not re.search(r"class='[^']*\breport-footer\b[^']*'", html):
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


# ========== D1-D5 humanization checks ==========

_BANNED_STARTERS_ZH = ['首先', '其次', '最后', '综上所述', '值得注意的是', '此外', '另外']
_CONNECTORS_ZH = ['因此', '然而', '同时', '此外', '另外', '而且', '但是', '所以', '不过',
                  '总之', '例如', '比如', '特别是', '尤其是', '一方面', '另一方面', '也就是说']
_OVERUSED_TERMS_ZH = ['重要', '优势明显', '显著', '必不可少', '至关重要', '占据主导',
                      '不可或缺', '十分关键', '日益突出', '值得关注']


def _extract_para_texts(html, lang=None):
    """Extract plain text from <p data-lang="..."> blocks. If lang given, only that language."""
    texts = []
    lang_pat = lang if lang else r'(?:zh|en)'
    for m in re.finditer(rf'<p[^>]*data-lang="{lang_pat}"[^>]*>(.*?)</p>', html, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', m.group(1))
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = text.strip()
        if text:
            texts.append(text)
    return texts


def check_d4_connectors(html):
    issues = []
    texts = _extract_para_texts(html)
    if not texts:
        return []

    total_chars = sum(len(t) for t in texts)
    banned_seen = []

    for i, t in enumerate(texts):
        start = t[:20]
        for w in _BANNED_STARTERS_ZH:
            if start.startswith(w):
                banned_seen.append(f'第{i+1}段以"{w}"开头')
                break

    if banned_seen:
        issues.append(f'D4: 段落开头禁用连接词 — {"; ".join(banned_seen)}')

    connector_count = 0
    for t in texts:
        for w in _CONNECTORS_ZH:
            connector_count += t.count(w)

    if total_chars > 0:
        per_1k = connector_count / (total_chars / 1000)
        if per_1k > 6:
            issues.append(
                f'D4: 连接词频率 {per_1k:.1f}/千字（上限 6/千字，实际 {connector_count} 个/'
                f'{total_chars} 字）'
            )

    return issues


def check_d1_sentence_length(html):
    """D1: check Chinese text only (character-based length)."""
    issues = []
    texts = _extract_para_texts(html, lang='zh')
    if not texts:
        return []

    # Split on Chinese/English sentence boundaries
    sent_pat = re.compile(
        r'[^。！？.!?\n]+[。！？.!?\n]'
    )

    for i, t in enumerate(texts):
        sents = sent_pat.findall(t)
        sents = [s.strip() for s in sents if len(s.strip()) > 2]
        if len(sents) < 3:
            continue

        lengths = [len(s) for s in sents]
        has_short = any(l <= 10 for l in lengths)
        has_long = any(l >= 35 for l in lengths)

        problems = []

        # Check consecutive same-band sentences (all short or all long)
        if len(sents) >= 3:
            if all(l <= 15 for l in lengths):
                problems.append(
                    f'连续{len(sents)}句均为短句（{min(lengths)}-{max(lengths)}字）')
            elif all(l >= 30 for l in lengths):
                problems.append(
                    f'连续{len(sents)}句均为长句（{min(lengths)}-{max(lengths)}字）')

        # Check consecutive similar-length sentences (4+ in a row)
        for j in range(len(lengths) - 3):
            chunk = lengths[j:j+4]
            if max(chunk) - min(chunk) < 10:
                problems.append(f'句{j+1}-{j+4}长度过于接近'
                                f'（{",".join(str(x) for x in chunk)}字）')
                break

        if not has_short and not has_long:
            problems.append(
                f'所有句子均为中等长度（{min(lengths)}-{max(lengths)}字，'
                f'缺≤10短句+≥35长句）')

        if problems:
            label = f'第{i+1}段'
            issues.append(f'D1: {label} — {"；".join(problems)}')

    return issues


def check_d5_term_variety(html):
    issues = []
    texts = _extract_para_texts(html)
    if not texts:
        return []

    total_chars = sum(len(t) for t in texts)
    combined = ' '.join(texts)

    flagged = []
    for term in _OVERUSED_TERMS_ZH:
        count = combined.count(term)
        if count > 0:
            per_800 = count / max(total_chars / 800, 1)
            if per_800 >= 1:
                flagged.append(f'{term}×{count}')

    if flagged:
        issues.append(
            f'D5: 高频AI术语 — {"; ".join(flagged)}（每800字同术语≥1次'
            f' — 建议替换，参见 humanize_matrix.md 案例D5）'
        )

    return issues


def run_all(path):
    if not os.path.exists(path):
        print(f"{FAIL} File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    base_dir = os.path.dirname(path)

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
