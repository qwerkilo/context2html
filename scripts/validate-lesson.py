"""Validate a lesson HTML file against teach_more_pic's error checklist.
Usage: python validate-lesson.py <path-to-lesson.html>
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
    check_cross_refs, check_data_anim_syntax,
)


def _extract_tag_blocks(html, tag, class_name):
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
    issues = []
    questions = _extract_tag_blocks(html, 'div', 'quiz-question')
    for i, q in enumerate(questions, 1):
        langs = re.findall(r'data-lang="([^"]+)"', q)
        if langs:
            langs = set(langs)
            for lang in langs:
                corrects = re.findall(
                    r'data-correct="true"[^>]*data-lang="' + lang + r'"|'
                    r'data-lang="' + lang + r'"[^>]*data-correct="true"', q
                )
                if len(corrects) != 1:
                    issues.append(f"Quiz Q{i} ({lang}): {len(corrects)} correct answers (expected 1)")
        else:
            corrects = re.findall(r'data-correct="true"', q)
            if len(corrects) != 1:
                issues.append(f"Quiz Q{i}: {len(corrects)} correct answers (expected 1)")
    return issues


def check_container_width(html):
    m = re.search(r"\.container\s*\{[^}]*max-width:\s*(\d+)", html)
    if m:
        w = int(m.group(1))
        if w < 700 or w > 800:
            return [f"Container max-width is {w}px (recommended 720-780)"]
    return []


def check_quiz_completeness(html):
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
                    r'class="[^"]*quiz-option[^"]*"[^>]*data-lang="' + lang + r'"|'
                    r'data-lang="' + lang + r'"[^>]*class="[^"]*quiz-option[^"]*"', q
                )
                if len(lang_opts) != 3:
                    issues.append(f"Quiz Q{i} ({lang}): {len(lang_opts)} options (expected 3)")
        else:
            if len(options) != 3:
                issues.append(f"Quiz Q{i}: {len(options)} options (expected 3)")
    return issues


def check_ppt_js(html):
    issues = []
    has_themes = bool(re.search(r"data-theme", html))
    if has_themes:
        if not re.search(r"key\s*===?\s*['\"]t['\"]", html, re.IGNORECASE):
            issues.append("Missing theme switching JS (T key handler)")
        if not re.search(r"tp-btn-toggle|tp-item", html):
            issues.append("Missing theme picker UI (.tp-btn-toggle / .tp-item elements)")

    has_sections = len(re.findall(r"<h2[^>]*>", html)) > 1
    if has_sections:
        if not re.search(
            r"key\s*===?\s*['\"]Arrow(?:Right|Left)['\"]", html, re.IGNORECASE
        ):
            issues.append("Missing keyboard navigation JS (arrow key handler)")
        if not re.search(
            r"data-lang-btn|key\s*===?\s*['\"]l['\"]", html, re.IGNORECASE
        ):
            issues.append("Missing language toggle (L key handler or [data-lang-btn])")
    return issues


_ICON_PARENT_TAGS = ('button', 'a', 'summary', 'label', 'input')
_ICON_WIDTH_THRESHOLD = 48


def _is_in_fenced_code(html, pos):
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
    issues = []
    has_figure = bool(re.search(r'class="[^"]*svg-fig[^"]*"', html))
    for m in re.finditer(r'<svg\b([^>]*)>', html):
        attrs = m.group(1)
        pos = m.start()
        if _is_in_fenced_code(html, pos):
            continue
        before = html[max(0, pos - 800):pos]
        if 'noise-overlay' in before:
            continue
        wm = re.search(r'width="(\d+)(?:px)?"', attrs)
        if wm and int(wm.group(1)) <= _ICON_WIDTH_THRESHOLD:
            continue
        tag_stack = []
        for am in re.finditer(r'</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>', before):
            tag = am.group(1).lower()
            self_close = am.group(2) == '/'
            if am.group(0).startswith('</'):
                if tag_stack and tag_stack[-1] == tag:
                    tag_stack.pop()
            elif not self_close and tag not in ('br', 'img', 'meta', 'link', 'input', 'hr'):
                tag_stack.append(tag)
        if any(t in _ICON_PARENT_TAGS for t in tag_stack):
            continue
        if not has_figure:
            issues.append("Inline <svg> found without .svg-fig wrapper")
            break
    return issues


def check_component_consistency(html):
    issues = []
    lbox_triggers = re.findall(r'data-lbox="([^"]+)"', html)
    for lid in lbox_triggers:
        if f'id="lbox-{lid}"' not in html:
            issues.append(f"Lightbox trigger data-lbox=\"{lid}\" has no matching #lbox-{lid}")
    panel_triggers = re.findall(r'data-panel="([^"]+)"', html)
    for pid in panel_triggers:
        if f'id="panel-{pid}"' not in html:
            issues.append(f"Info panel trigger data-panel=\"{pid}\" has no matching #panel-{pid}")
    popover_triggers = re.findall(r'popovertarget="([^"]+)"', html)
    for pid in popover_triggers:
        target = f'id="{pid}"'
        if target not in html:
            issues.append(f"Popover trigger popovertarget=\"{pid}\" has no matching element")
    dialogs = len(re.findall(r'<dialog[\s>]', html))
    close_methods = len(re.findall(r'close\(\)|showModal\(\)', html))
    if dialogs > 0 and close_methods == 0:
        issues.append("Found <dialog> without showModal() or close() calls")
    return issues


def check_spa_integration(html, path):
    issues = []
    filename = os.path.basename(path).lower()

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
            issues.append(f"Missing closing </section>")
        return issues

    if "graphdata" in html.lower():
        return []

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
    issues = []
    has_graphdata = 'graphData' in html and ('rawNodes' in html or 'const graphData' in html)
    has_bilingual = bool(re.search(r'(?:const|var|let)\s+rawNodes\s*=', html)) and bool(re.search(r'(?:const|var|let)\s+rawLinks\s*=', html))

    if not has_graphdata:
        return []

    if has_bilingual:
        node_ids = []
        rn_match = re.search(r'(?:const|var|let)\s+rawNodes\s*=\s*\[(.+?)\]', html, re.DOTALL)
        if not rn_match:
            issues.append("bilingual KG: missing 'rawNodes' array")
        else:
            rn_text = rn_match.group(1)
            rn_objs = re.findall(r'\{(.+?)\}', rn_text, re.DOTALL)
            for i, nobj in enumerate(rn_objs):
                if 'nameZh' not in nobj:
                    issues.append(f"rawNodes #{i+1}: missing 'nameZh'")
                if 'nameEn' not in nobj:
                    issues.append(f"rawNodes #{i+1}: missing 'nameEn'")
            cats = []
            cn_match = re.search(r'"zh"\s*:\s*\[([^\]]+)\]', html)
            if cn_match:
                cats = re.findall(r'"([^"]+)"', cn_match.group(1))
            sub_issues, node_ids = _check_kg_nodes(rn_text, cats)
            issues.extend(['bilingual KG: ' + s for s in sub_issues])

        rl_match = re.search(r'(?:const|var|let)\s+rawLinks\s*=\s*\[(.+?)\]', html, re.DOTALL)
        if not rl_match:
            issues.append("bilingual KG: missing 'rawLinks' array")
        else:
            sub_issues = _check_kg_links(rl_match.group(1), node_ids)
            issues.extend(['bilingual KG: ' + s for s in sub_issues])
        return issues

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
            ("Chapter cross-refs use #chN anchors", check_cross_refs(html)),
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
