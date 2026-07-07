"""Report-specific validation checks and D1-D5 humanization checks — framework package."""
import re
import os
from functools import lru_cache

_RE_EXEC_SUMMARY = re.compile(r'class="[^"]*\bexec-summary\b[^"]*"')
_RE_REPORT_CHAPTER = re.compile(r'class="[^"]*report-chapter[^"]*"')
_RE_CONCLUSION = re.compile(r'class="[^"]*\bconclusion-page\b[^"]*"')
_RE_FOOTER = re.compile(r'class="[^"]*\breport-footer\b[^"]*"')
_RE_ARTICLE = re.compile(r'<article\b')
_RE_NAV_LINKS = re.compile(r'<nav\b[^>]*>.*?<a\b', re.DOTALL)
_RE_STEP_CLASS = re.compile(r'class="[^"]*\b(?:si-step|sc-step)\b[^"]*"')
_RE_THEME_CSS = re.compile(r'href="([^"]*report-themes\.css)"')
_RE_BAR_FILL = re.compile(r'class="[^"]*(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^"]*"[^>]*style="([^"]*)"')
_RE_BAR_FILL_REV = re.compile(r'style="([^"]*)"[^>]*class="[^"]*(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^"]*"')
_RE_STYLE_BLOCK = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL)
_RE_SCRIPT_BLOCK = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
_RE_PARA_ZH = re.compile(r'<p[^>]*data-lang="zh"[^>]*>(.*?)</p>', re.DOTALL)
_RE_PARA_EN = re.compile(r'<p[^>]*data-lang="en"[^>]*>(.*?)</p>', re.DOTALL)
_RE_PARA_ALL = re.compile(r'<p[^>]*data-lang="(?:zh|en)"[^>]*>(.*?)</p>', re.DOTALL)
_RE_HTML_TAG = re.compile(r'<[^>]+>')
_RE_CMP_TABLE_MEDIA = re.compile(r'@media\s*\([^)]*max-width\s*:\s*(\d+)px[^)]*\)\s*\{')
_RE_CMP_TABLE_RULE = re.compile(r'\.cmp-table[^{]*\{([^}]*)\}')
_RE_SENTENCE = re.compile(r'[^。！？.!?\n]+[。！？]|[^。！？.!?\n]+[.!?](?:\s|$)')
_RE_SUMMARY_ENDING = re.compile(r'这[显示表明说明证明反映代表意味着]+了')
_RE_DIGIT = re.compile(r'\d')
_RE_DATA_CLAIM = re.compile(r'(?:增长|下降|占比|达到|超过|突破|占比|营收|份额|规模|增速|率\s*[:：达为])')
_RE_BAR_CSS_WIDTH = re.compile(r'\.(?<![a-zA-Z0-9_-])bar-fill(?![-_])[^{]*\{[^}]*width\s*:\s*(\d+(?:\.\d+)?)\s*%\s*;')
_RE_CMP_TABLE = re.compile(r'.cmp-table')

_BANNED_STARTERS_ZH = ['首先', '其次', '最后', '综上所述', '值得注意的是', '此外', '另外',
                       '值得一提的是', '不可忽视的是', '毋庸置疑', '显而易见']
_CONNECTORS_ZH = ['因此', '然而', '同时', '此外', '另外', '而且', '但是', '所以', '不过',
                  '总之', '例如', '比如', '特别是', '尤其是', '一方面', '另一方面', '也就是说',
                  '换言之', '换句话说', '简而言之', '总的来说', '具体来说', '由此看来',
                  '从某种意义上说']
_OVERUSED_TERMS_ZH = ['重要', '优势明显', '显著', '必不可少', '至关重要', '占据主导',
                      '不可或缺', '十分关键', '日益突出', '值得关注',
                      '赋能', '落地', '闭环', '抓手', '维度',
                      '深化', '深耕', '精细化', '重塑', '重构']

_REPO_CDN = "cdn.jsdelivr.net/gh/qwerkilo/context2html"
_RE_THEME_LOADLIB = re.compile(r"__loadLib\s*\(\s*['\"]([^'\"]*report-themes\.css[^'\"]*)['\"]")


def check_exec_summary(html):
    if not _RE_EXEC_SUMMARY.search(html):
        return ["Missing .exec-summary section (required: key findings summary)"]
    return []


def check_report_chapters(html):
    chapters = _RE_REPORT_CHAPTER.findall(html)
    if len(chapters) < 1:
        return [f"Found {len(chapters)} .report-chapter elements (expected at least 1)"]
    return []


def check_conclusion_page(html):
    if not _RE_CONCLUSION.search(html):
        return ["Missing .conclusion-page section (required: conclusions & recommendations)"]
    return []


def check_report_footer(html):
    if not _RE_FOOTER.search(html):
        return ["Missing .report-footer element (required: report footer)"]
    return []


def check_theme_css(html, base_dir=None):
    issues = []
    refs = _RE_THEME_CSS.findall(html)
    loadlib_refs = _RE_THEME_LOADLIB.findall(html)
    if not refs and not loadlib_refs:
        return ["Missing <link> or __loadLib to theme/report-themes.css"]
    for ref in refs:
        if ref.startswith("http"):
            if _REPO_CDN not in ref:
                issues.append(f"Theme CSS from external CDN/URL: {ref} (prefer repo CDN or local)")
            continue
        if base_dir and not os.path.isabs(ref):
            resolved = os.path.normpath(os.path.join(base_dir, ref))
            if not os.path.exists(resolved):
                issues.append(f"Theme CSS link points to missing file: {ref} -> {resolved}")
    for ref in loadlib_refs:
        if base_dir and not ref.startswith("http"):
            resolved = os.path.normpath(os.path.join(base_dir, ref))
            if not os.path.exists(resolved):
                issues.append(f"Theme CSS __loadLib points to missing file: {ref} -> {resolved}")
    return issues


def check_article_structure(html):
    if not _RE_ARTICLE.search(html):
        return ["Article type missing <article> elements (use <article> for content sections)"]
    return []


def check_doc_structure(html):
    if not _RE_NAV_LINKS.search(html):
        return ["Document type missing navigable table of contents (use <nav> with links)"]
    return []


def check_tutorial_structure(html):
    if not _RE_STEP_CLASS.search(html):
        return ["Tutorial type missing step indicators (use .si-bar or .sc-chain for steps)"]
    return []


def check_note_structure(html):
    return []


def check_bar_fill_width(html):
    issues = []
    overflow = []
    for pat in [_RE_BAR_FILL, _RE_BAR_FILL_REV]:
        for m in pat.finditer(html):
            style = m.group(1)
            wm = re.search(r'width\s*:\s*(\d+(?:\.\d+)?)\s*%', style)
            if wm and float(wm.group(1)) > 100:
                overflow.append(f"{wm.group(1)}%")
    all_css = _get_style_css(html)
    if all_css:
        for m in _RE_BAR_CSS_WIDTH.finditer(all_css):
            if float(m.group(1)) > 100:
                overflow.append(f"{m.group(1)}% (CSS rule)")
    if overflow:
        issues.append(f"Bar-fill width exceeds 100%: {', '.join(overflow)}")
    return issues


def check_cmp_table_responsive(html):
    if not _RE_CMP_TABLE.search(html):
        return []
    all_css = _get_style_css(html)
    if not all_css:
        return [".cmp-table used but no <style> block found for responsive rules"]
    narrow_breaks = list(_RE_CMP_TABLE_MEDIA.finditer(all_css))
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
    all_css = _get_style_css(html)
    if 'overflow-wrap: break-word' not in all_css and 'overflow-wrap:break-word' not in all_css:
        issues.append("Missing overflow-wrap: break-word on body (English text may overflow)")
    if _RE_CMP_TABLE.search(html):
        has_fixed = False
        for m in _RE_CMP_TABLE_RULE.finditer(all_css):
            if 'table-layout: fixed' in m.group(1) or 'table-layout:fixed' in m.group(1):
                has_fixed = True
                break
        if not has_fixed:
            issues.append(".cmp-table missing table-layout: fixed (English text may expand columns)")
    return issues


def check_echarts_color_usage(html):
    issues = []
    for s in _RE_SCRIPT_BLOCK.findall(html):
        if ("'var(--" in s or '"var(--' in s or '`var(--' in s) and 'echarts' in s:
            issues.append(
                "ECharts script uses 'var(--xxx)' directly (Canvas2D ignores CSS var())"
                " — use gv('--xxx') helper instead"
            )
            break
    return issues


@lru_cache(maxsize=4)
def _get_style_css(html):
    return '\n'.join(_RE_STYLE_BLOCK.findall(html))


@lru_cache(maxsize=4)
def _extract_para_texts(html, lang=None):
    texts = []
    pat = _RE_PARA_ZH if lang == 'zh' else (_RE_PARA_EN if lang == 'en' else _RE_PARA_ALL)
    for m in pat.finditer(html):
        text = _RE_HTML_TAG.sub('', m.group(1))
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
    issues = []
    texts = _extract_para_texts(html, lang='zh')
    if not texts:
        return []
    for i, t in enumerate(texts):
        sents = _RE_SENTENCE.findall(t)
        sents = [s.strip() for s in sents if len(s.strip()) > 2]
        if len(sents) < 3:
            continue
        lengths = [len(s) for s in sents]
        has_short = any(l <= 10 for l in lengths)
        has_long = any(l >= 35 for l in lengths)
        problems = []
        if len(sents) >= 3:
            if all(l <= 15 for l in lengths):
                problems.append(f'连续{len(sents)}句均为短句（{min(lengths)}-{max(lengths)}字）')
            elif all(l >= 30 for l in lengths):
                problems.append(f'连续{len(sents)}句均为长句（{min(lengths)}-{max(lengths)}字）')
        for j in range(len(lengths) - 3):
            chunk = lengths[j:j+4]
            if max(chunk) - min(chunk) < 10:
                problems.append(f'句{j+1}-{j+4}长度过于接近'
                                f'（{",".join(str(x) for x in chunk)}字）')
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


def check_d2_paragraph_structure(html):
    issues = []
    texts = _extract_para_texts(html)
    if not texts:
        return []

    if len(texts) >= 2:
        for i in range(len(texts) - 1):
            curr = texts[i][:40]
            nxt = texts[i + 1][:40]
            curr_is_data = bool(_RE_DIGIT.search(curr[:15]))
            nxt_is_data = bool(_RE_DIGIT.search(nxt[:15]))
            if curr_is_data and nxt_is_data and len(texts[i]) > 20 and len(texts[i+1]) > 20:
                issues.append(f'第{i+1}-{i+2}段相邻同结构（均以数据开头）')

    for i, t in enumerate(texts):
        last_60 = t[-60:]
        if _RE_SUMMARY_ENDING.search(last_60):
            issues.append(f'第{i+1}段以总结句结尾（"这...了"模式）')

    for i, t in enumerate(texts):
        if t.strip().startswith('综上所述'):
            issues.append(f'第{i+1}段以"综上所述"开头（禁止模板化总结）')

    return issues


def check_d3_info_density(html):
    issues = []
    texts = _extract_para_texts(html)
    if len(texts) < 2:
        return []

    densities = []
    for t in texts:
        if len(t) < 20:
            densities.append(None)
            continue
        sentences = [s.strip() for s in _RE_SENTENCE.findall(t) if len(s.strip()) > 5]
        if not sentences:
            densities.append(None)
            continue
        data_sentences = sum(1 for s in sentences if _RE_DIGIT.search(s) or _RE_DATA_CLAIM.search(s))
        ratio = data_sentences / len(sentences)
        densities.append(ratio)

    for i in range(len(densities) - 1):
        if densities[i] is None or densities[i+1] is None:
            continue
        d1, d2 = densities[i], densities[i+1]
        if d1 >= 0.6 and d2 >= 0.6:
            issues.append(f'第{i+1}-{i+2}段连续高密度（数据驱动句占比 {d1:.0%}+{d2:.0%}）')
        if d1 <= 0.2 and d2 <= 0.2:
            issues.append(f'第{i+1}-{i+2}段连续低密度（空泛句占比 {1-d1:.0%}+{1-d2:.0%}）')

    return issues
