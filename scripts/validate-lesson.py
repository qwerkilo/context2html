"""Validate a lesson HTML file against teach_more_pic's error checklist.
Usage: python validate-lesson.py <path-to-lesson.html>
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
    svgs = set(re.findall(r'<img[^>]*src="([^"]+\.svg)"', html))
    svgs.update(re.findall(r'<object[^>]*data="([^"]+\.svg)"', html))
    svgs.update(re.findall(r'<iframe[^>]*src="([^"]+\.svg)"', html))
    svgs.update(re.findall(r'<source[^>]*src="([^"]+\.svg)"', html))
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


def _extract_tag_blocks(html, tag, class_name):
    """Extract balanced <tag class="...class_name...">...</tag> blocks via depth counting.

    A naive regex like `<tag ...>.*?</tag>` with DOTALL matches an inner closing tag
    when the block contains nested tags of the same type, producing wrong question
    bodies. This depth walker tolerates arbitrary nesting.
    """
    pattern = re.compile(
        r'<' + tag + r'\b[^>]*class="[^"]*\b' + re.escape(class_name) + r'\b[^"]*"[^>]*>',
        re.IGNORECASE,
    )
    blocks = []
    pos = 0
    while pos < len(html):
        m = pattern.search(html, pos)
        if not m:
            break
        depth = 1
        cursor = m.end()
        open_re = re.compile(r'<' + tag + r'(?=[\s>])', re.IGNORECASE)
        close_re = re.compile(r'</' + tag + r'\s*>', re.IGNORECASE)
        while cursor < len(html) and depth > 0:
            no = open_re.search(html, cursor)
            nc = close_re.search(html, cursor)
            if not nc:
                break
            if no and no.start() < nc.start():
                depth += 1
                cursor = no.end()
            else:
                depth -= 1
                cursor = nc.end()
        if depth == 0:
            blocks.append(html[m.start():cursor])
            pos = cursor
        else:
            break
    return blocks


def check_quiz_correct_count(html):
    """Each quiz question should have exactly one data-correct=true per language."""
    issues = []
    questions = _extract_tag_blocks(html, 'div', 'quiz-question')
    for i, q in enumerate(questions, 1):
        langs = re.findall(r'data-lang="([^"]+)"', q)
        if langs:
            langs = set(langs)
            for lang in langs:
                corrects = re.findall(
                    r'data-correct="true"[^>]*data-lang="' + lang + '"', q
                )
                if len(corrects) != 1:
                    issues.append(f"Quiz Q{i} ({lang}): {len(corrects)} correct answers (expected 1)")
        else:
            corrects = re.findall(r'data-correct="true"', q)
            if len(corrects) != 1:
                issues.append(f"Quiz Q{i}: {len(corrects)} correct answers (expected 1)")
    return issues


def check_h1_count(html):
    """Each lesson must have exactly one h1 (or one per language with data-lang)."""
    h1s = re.findall(r"<h1[^>]*>", html)
    lang_h1s = re.findall(r'<h1[^>]*data-lang=["\']([^"\']+)["\']', html)
    if lang_h1s:
        if len(h1s) == len(set(lang_h1s)):
            return []
    if len(h1s) != 1:
        return [f"Found {len(h1s)} h1 tags (expected 1, or 1 per language with data-lang)"]
    return []


def check_data_anim_syntax(html):
    """data-anim values should be valid."""
    valid = {"fade-up", "fade", "slide-left", "blur"}
    anims = re.findall(r'data-anim="([^"]+)"', html)
    bad = [a for a in anims if a not in valid]
    if bad:
        return [f"Invalid data-anim values: {set(bad)}"]
    return []


def check_container_width(html):
    """Container max-width should be between 700-800px."""
    m = re.search(r"\.container\s*\{[^}]*max-width:\s*(\d+)", html)
    if m:
        w = int(m.group(1))
        if w < 700 or w > 800:
            return [f"Container max-width is {w}px (recommended 720-780)"]
    return []


def check_relative_links(html):
    """Cross-lesson links must use relative paths, not / or http."""
    issues = []
    links = re.findall(r'<a[^>]*href="([^"]+\.html)"', html)
    for href in links:
        if href.startswith("/") or href.startswith("http"):
            issues.append(f"Absolute link found: {href} (use relative path)")
    return issues


def check_quiz_completeness(html):
    """Should have exactly 5 questions, each with 3 options per language."""
    issues = []
    questions = _extract_tag_blocks(html, 'div', 'quiz-question')
    if len(questions) != 5:
        issues.append(f"Found {len(questions)} quiz questions (expected 5)")
    for i, q in enumerate(questions, 1):
        options = re.findall(r'<button[^>]*class="[^"]*quiz-option[^"]*"', q)
        langs = re.findall(r'data-lang="([^"]+)"', q)
        if langs:
            langs = set(langs)
            for lang in langs:
                lang_opts = re.findall(
                    r'class="[^"]*quiz-option[^"]*"[^>]*data-lang="' + lang + '"', q
                )
                if len(lang_opts) != 3:
                    issues.append(f"Quiz Q{i} ({lang}): {len(lang_opts)} options (expected 3)")
        else:
            if len(options) != 3:
                issues.append(f"Quiz Q{i}: {len(options)} options (expected 3)")
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


def check_ppt_js(html):
    """Check for theme switching and keyboard nav JS."""
    issues = []
    has_themes = bool(re.search(r"data-theme", html))
    if has_themes:
        if not re.search(r"key\s*===?\s*['\"]t['\"]", html, re.IGNORECASE):
            issues.append("Missing theme switching JS (T key handler)")
        if not re.search(r"tp-btn-toggle|tp-item", html):
            issues.append("Missing theme picker UI (.tp-btn-toggle / .tp-item elements)")

    has_sections = len(re.findall(r"<h2[^>]*>", html)) > 1
    if has_sections and not re.search(
        r"key\s*===?\s*['\"]Arrow(?:Right|Left)['\"]", html, re.IGNORECASE
    ):
        issues.append("Missing keyboard navigation JS (arrow key handler)")
    return issues


_ICON_PARENT_TAGS = ('button', 'a', 'summary', 'label', 'input')
_ICON_WIDTH_THRESHOLD = 48


def _is_in_fenced_code(html, pos):
    """Return True when the position sits inside an open/unclosed ``` fenced block."""
    in_fence = False
    cursor = 0
    while cursor < pos:
        nxt = html.find('```', cursor)
        if nxt == -1 or nxt >= pos:
            break
        in_fence = not in_fence
        cursor = nxt + 3
    return in_fence


def check_inline_svg(html):
    """Inline SVGs must be wrapped in .svg-fig figure, excluding icon SVGs."""
    issues = []
    has_figure = bool(re.search(r'class="[^"]*svg-fig[^"]*"', html))
    for m in re.finditer(r'<svg\b([^>]*)>', html):
        attrs = m.group(1)
        pos = m.start()
        if _is_in_fenced_code(html, pos):
            continue
        before = html[max(0, pos - 200):pos]
        if 'noise-overlay' in before:
            continue
        wm = re.search(r'width="(\d+)(?:px)?"', attrs)
        if wm and int(wm.group(1)) <= _ICON_WIDTH_THRESHOLD:
            continue
        last_open = None
        for am in re.finditer(r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>', before):
            tag = am.group(1).lower()
            if am.group(2) == '/':
                continue
            if tag in _ICON_PARENT_TAGS:
                last_open = tag
        if last_open is not None:
            continue
        if not has_figure:
            issues.append("Inline <svg> found without .svg-fig wrapper")
            break
    return issues



def check_component_consistency(html):
    """Check that component HTML attributes have matching target elements."""
    issues = []
    # Lightbox: data-lbox="X" must have corresponding id="lbox-X"
    lbox_triggers = re.findall(r'data-lbox="([^"]+)"', html)
    for lid in lbox_triggers:
        if f'id="lbox-{lid}"' not in html:
            issues.append(f"Lightbox trigger data-lbox=\"{lid}\" has no matching #lbox-{lid}")
    # Info panel: data-panel="X" must have corresponding id="panel-X"
    panel_triggers = re.findall(r'data-panel="([^"]+)"', html)
    for pid in panel_triggers:
        if f'id="panel-{pid}"' not in html:
            issues.append(f"Info panel trigger data-panel=\"{pid}\" has no matching #panel-{pid}")
    # Popover: popovertarget="X" must have matching id="X" with popover attribute
    popover_triggers = re.findall(r'popovertarget="([^"]+)"', html)
    for pid in popover_triggers:
        target = f'id="{pid}"'
        if target not in html:
            issues.append(f"Popover trigger popovertarget=\"{pid}\" has no matching element")
        elif f'popover' not in html:
            pass  # popover content may not be in same file
    # Dialog: <dialog> should have close mechanism
    dialogs = len(re.findall(r'<dialog[\s>]', html))
    close_methods = len(re.findall(r'close\(\)|showModal\(\)', html))
    if dialogs > 0 and close_methods == 0:
        issues.append("Found <dialog> without showModal() or close() calls")
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


def check_spa_integration(html, path):
    """Check lesson HTML has proper SPA section structure."""
    issues = []
    filename = os.path.basename(path).lower()

    # If this is index.html, check section structure
    if filename == "index.html":
        sections = re.findall(
            r'<section\s+class="([^"]*)"\s+id="lesson-(\d+)"[^>]*>', html
        )
        if not sections:
            return ["index.html: no <section class=\"...\" id=\"lesson-NNN\"> found"]
        ids = []
        for cls, sid in sections:
            if "lesson-view" not in cls:
                issues.append(f"Section lesson-{sid}: missing class=\"lesson-view\"")
            if sid in ids:
                issues.append(f"Duplicate section id=\"lesson-{sid}\"")
            ids.append(sid)
            if f'</section>' not in html:
                issues.append(f"Section lesson-{sid}: missing closing </section>")
        return issues

    # For regular lesson HTML files (not KG, not template)
    if "graphdata" in html.lower():
        return []  # KG files skip SPA check

    m = re.search(r'id="lesson-(\d+)"', html)
    if not m:
        return ["Missing id=\"lesson-NNN\" in lesson HTML"]
    sid = m.group(1)
    m2 = re.search(r'<section\b[^>]*\bid="lesson-' + sid + r'"[^>]*>', html)
    if not m2:
        return [f"Missing <section> wrapper for id=\"lesson-{sid}\""]
    if '</section>' not in html:
        return ["Missing closing </section>"]
    return issues


def _check_kg_nodes(nodes_text, cats, require_name=True):
    """Shared node validation (old and new format)."""
    issues = []
    node_ids = []
    node_objs = re.findall(r'\{(.+?)\}', nodes_text, re.DOTALL)
    if len(node_objs) < 1:
        issues.append("nodes array is empty (need at least 1)")
    else:
        weights = []
        for i, nobj in enumerate(node_objs):
            has_id = '"id"' in nobj
            has_cat = '"category"' in nobj or ('"categoryZh"' in nobj and '"categoryEn"' in nobj)
            if require_name and '"name"' not in nobj and '"nameZh"' not in nobj:
                issues.append(f"Node #{i+1}: missing 'name' (or 'nameZh'/'nameEn' for bilingual)")
            if not has_id:
                issues.append(f"Node #{i+1}: missing 'id'")
            if not has_cat:
                issues.append(f"Node #{i+1}: missing 'category' (or 'categoryZh'/'categoryEn' for bilingual)")
            nid = re.search(r'"id"\s*:\s*"([^"]+)"', nobj)
            if nid:
                if nid.group(1) in node_ids:
                    issues.append(f"Duplicate node id=\"{nid.group(1)}\"")
                node_ids.append(nid.group(1))
                ncat = re.search(r'"category"\s*:\s*"([^"]+)"', nobj)
                if ncat and cats and ncat.group(1) not in cats:
                    issues.append(f"Node \"{nid.group(1)}\": category \"{ncat.group(1)}\" not in categories list")
            nwt = re.search(r'"weight"\s*:\s*(\d+)', nobj)
            if nwt:
                weights.append(int(nwt.group(1)))
        if weights:
            if max(weights) > 100:
                issues.append("Some node weights exceed 100")
            if min(weights) < 0:
                issues.append("Negative node weights found")
    return issues, node_ids


def _check_kg_links(links_text, node_ids):
    """Shared link validation."""
    issues = []
    link_objs = re.findall(r'\{(.+?)\}', links_text, re.DOTALL)
    if len(link_objs) < 1:
        issues.append("links array is empty (need at least 1)")
    else:
        for i, lobj in enumerate(link_objs):
            has_src = '"source"' in lobj
            has_tgt = '"target"' in lobj
            has_rel = '"relation"' in lobj
            if not has_src:
                issues.append(f"Link #{i+1}: missing 'source'")
            if not has_tgt:
                issues.append(f"Link #{i+1}: missing 'target'")
            if not has_rel:
                issues.append(f"Link #{i+1}: missing 'relation'")
            lsrc = re.search(r'"source"\s*:\s*"([^"]+)"', lobj)
            ltgt = re.search(r'"target"\s*:\s*"([^"]+)"', lobj)
            if lsrc and lsrc.group(1) not in node_ids:
                issues.append(f"Link #{i+1}: source \"{lsrc.group(1)}\" references unknown node")
            if ltgt and ltgt.group(1) not in node_ids:
                issues.append(f"Link #{i+1}: target \"{ltgt.group(1)}\" references unknown node")
    return issues


def check_kg_structure(html, path):
    """Validate knowledge graph data structure (old + bilingual format)."""
    issues = []
    has_graphdata = 'graphData' in html and ('rawNodes' in html or 'const graphData' in html)
    has_bilingual = bool(re.search(r'(?:const|var|let)\s+rawNodes\s*=', html)) and bool(re.search(r'(?:const|var|let)\s+rawLinks\s*=', html))

    if not has_graphdata:
        return []

    # ===== New bilingual format (rawNodes with nameZh/nameEn) =====
    if has_bilingual:
        # Check rawNodes
        rn_match = re.search(r'(?:const|var|let)\s+rawNodes\s*=\s*\[(.+?)\]', html, re.DOTALL)
        if not rn_match:
            issues.append("bilingual KG: missing 'rawNodes' array")
        else:
            rn_text = rn_match.group(1)
            # Check for nameZh + nameEn on each node
            rn_objs = re.findall(r'\{(.+?)\}', rn_text, re.DOTALL)
            for i, nobj in enumerate(rn_objs):
                if 'nameZh' not in nobj:
                    issues.append(f"rawNodes #{i+1}: missing 'nameZh'")
                if 'nameEn' not in nobj:
                    issues.append(f"rawNodes #{i+1}: missing 'nameEn'")
            # Extract categories from catNames
            cats = []
            cn_match = re.search(r'"zh"\s*:\s*\[([^\]]+)\]', html)
            if cn_match:
                cats = re.findall(r'"([^"]+)"', cn_match.group(1))
            sub_issues, node_ids = _check_kg_nodes(rn_text, cats)
            issues.extend(['bilingual KG: ' + s for s in sub_issues])

        # Check rawLinks
        rl_match = re.search(r'(?:const|var|let)\s+rawLinks\s*=\s*\[(.+?)\]', html, re.DOTALL)
        if not rl_match:
            issues.append("bilingual KG: missing 'rawLinks' array")
        else:
            sub_issues = _check_kg_links(rl_match.group(1), node_ids if 'node_ids' in dir() else [])
            issues.extend(['bilingual KG: ' + s for s in sub_issues])
        return issues

    # ===== Old inline format (const graphData = { ... }) =====
    cats = []
    cat_match = re.search(r'"categories"\s*:\s*\[([^\]]+)\]', html)
    if not cat_match:
        issues.append("graphData: missing 'categories' array")
    else:
        cats = re.findall(r'"([^"]+)"', cat_match.group(1))
        if len(cats) < 1:
            issues.append("graphData: 'categories' array is empty")

    nodes_match = re.search(r'"nodes"\s*:\s*\[(.+?)\]', html, re.DOTALL)
    if not nodes_match:
        issues.append("graphData: missing 'nodes' array")
        return issues

    sub_issues, node_ids = _check_kg_nodes(nodes_match.group(1), cats)
    issues.extend(['graphData: ' + s for s in sub_issues])

    links_match = re.search(r'"links"\s*:\s*\[(.+?)\]', html, re.DOTALL)
    if not links_match:
        issues.append("graphData: missing 'links' array")
        return issues

    sub_issues = _check_kg_links(links_match.group(1), node_ids)
    issues.extend(['graphData: ' + s for s in sub_issues])

    return issues


def check_bilingual(html):
    """Check for bilingual content with data-lang and language toggle."""
    issues = []
    has_zh = 'data-lang="zh"' in html
    has_en = 'data-lang="en"' in html
    has_toggle = 'data-lang-btn' in html
    has_l_key = "key==='l'" in html or 'key==="l"' in html

    if not has_zh and not has_en:
        return []  # Not bilingual, skip (legacy lessons)

    if not has_zh:
        issues.append("Missing data-lang=\"zh\" (Chinese content)")
    if not has_en:
        issues.append("Missing data-lang=\"en\" (English content)")
    if not has_toggle:
        issues.append("Missing language toggle button ([data-lang-btn])")
    if not has_l_key:
        issues.append("Missing L key handler for language switching")

    return issues


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
    if re.search(r'bar3D|scatter3D|map3D|globe|\'surface\'', html) or 'echarts-gl' in html:
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
    if re.search(r'd3\.(forceSimulation|hierarchy|sankey|select)\b', html):
        has_local = os.path.exists(os.path.join(base_dir, "libs", "d3.min.js"))
        has_cdn = "d3js.org/d3" in html
        if not has_local and not has_cdn:
            issues.append("D3.js usage found but no libs/d3.min.js or CDN link")
        issues.extend(_check_local_script_paths(html, base_dir, "d3"))
    return issues


def run_all(path):
    if not os.path.exists(path):
        print(f"{FAIL} File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    base_dir = os.path.dirname(path)
    is_kg = "graphdata" in html.lower()
    basename = os.path.basename(path).lower()
    is_index = basename == "index.html" or basename.startswith("index-")

    results = [
        ("SVG files exist & valid", check_svg_links(html, base_dir)),
    ]

    # KG files and index.html skip lesson-specific checks
    if not is_kg and not is_index:
        results += [
            ("Quiz: exactly 1 correct per question", check_quiz_correct_count(html)),
            ("Quiz: 5 questions x 3 options", check_quiz_completeness(html)),
            ("Exactly one <h1>", check_h1_count(html)),
            ("data-anim syntax valid", check_data_anim_syntax(html)),
            ("Container width in range", check_container_width(html)),
            ("Relative links only", check_relative_links(html)),
            ("SVG text/background contrast", check_svg_contrast(html, base_dir)),
            ("PPT JS (theme + nav) present", check_ppt_js(html)),
            ("Inline SVG in .svg-fig", check_inline_svg(html)),
            ("Component consistency", check_component_consistency(html)),
            (":focus-visible outline", check_focus_visible(html)),
            ("tabular-nums alignment", check_tabular_nums(html)),
            ("Semantic HTML elements", check_semantic_html(html)),
            ("Library deps (ECharts/Three.js)", check_lib_deps(html, base_dir)),
            ("Bilingual (data-lang zh/en + toggle)", check_bilingual(html)),
            ("SPA integration (lesson-view section)", check_spa_integration(html, path)),
        ]
    else:
        if is_kg:
            results += [("Library deps (ECharts/Three.js)", check_lib_deps(html, base_dir))]
        if is_index:
            results += [("SPA integration (lesson-view section)", check_spa_integration(html, path))]

    results += [("Knowledge graph structure", check_kg_structure(html, path))]

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
        print(f"Usage: python {sys.argv[0]} <lesson.html>")
        sys.exit(1)
    run_all(sys.argv[1])
