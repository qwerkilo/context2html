#!/usr/bin/env python3
"""
generate-theme-css.py — 从项目 theme/DESIGN.md 读取 YAML 设计 Token
（从 teach_more_pic 复制的副本），生成 report-themes.css 和 theme-index.json。

用法：
  python scripts/generate-theme-css.py

依赖：PyYAML (pip install pyyaml)，回退到内置 yaml 解析器
"""

import os
import re
import json
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 先找本地 theme/ 目录（已从 teach_more_pic 复制），再找同级 teach_more_pic 项目
LOCAL_THEME = os.path.join(PROJECT_DIR, "theme")
THEME_DIRS = [
    LOCAL_THEME,
    os.path.join(os.path.dirname(PROJECT_DIR), "teach_more_pic", "theme"),
]

THEME_DIR: str = ''
for p in THEME_DIRS:
    if os.path.isdir(p):
        THEME_DIR = p
        break

if not THEME_DIR:
    print("[ERROR] Cannot find theme directory in local project or teach_more_pic sibling.")
    sys.exit(1)

if THEME_DIR == LOCAL_THEME:
    print(f"[INFO] Using local theme/ directory ({len(os.listdir(THEME_DIR))} items)")
else:
    print(f"[INFO] Using teach_more_pic theme/ directory at {THEME_DIR}")

OUTPUT_DIR = os.path.join(PROJECT_DIR, "theme")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSS = os.path.join(OUTPUT_DIR, "report-themes.css")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "theme-index.json")

# YAML front matter 解析（使用 pyyaml 或内置回退）
def parse_front_matter(text):
    """解析 --- 包围的 YAML 头，返回 dict 和正文。"""
    m = re.match(r'^---\s*\n(.*?)\n(?:---|\.\.\.)', text, re.DOTALL)
    if not m:
        return {}, text
    yaml_text = m.group(1)
    body = text[m.end():]

    # Try PyYAML first
    try:
        import yaml
        result = yaml.safe_load(yaml_text)
        if isinstance(result, dict):
            return result, body
    except ImportError:
        pass

    # Fallback: section-based regex parser
    result = {}
    sections = split_yaml_sections(yaml_text)

    for key, val in sections:
        if isinstance(val, dict):
            result[key] = val
        elif isinstance(val, str):
            result[key] = val
        else:
            result[key] = val

    return result, body


def is_new_key(line):
    """Check if line looks like a new YAML key (not a URL or value with colons)."""
    stripped = line.strip()
    if '://' in stripped:
        return False
    # Must have ':' followed by space or end-of-string (YAML key pattern)
    return re.match(r'^[\w\-]+:', stripped)


def split_yaml_sections(text):
    """Split YAML by top-level keys. Returns list of (key, value_or_dict_or_string)."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line.strip().startswith('#'):
            i += 1
            continue
        stripped = line.strip()
        if ':' not in stripped:
            i += 1
            continue
        key, _, val = stripped.partition(':')
        key = key.rstrip()
        val = val.strip()

        # Empty value → child block follows
        if not val:
            child_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t') and is_new_key(next_line):
                    break
                if next_line.strip() and not next_line.strip().startswith('#'):
                    child_lines.append(next_line)
                i += 1
            children = parse_child_dict(child_lines)
            result.append((key, children))

        # | block → multi-line string
        elif val == '|':
            desc_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t') and (is_new_key(next_line) or next_line.strip().startswith('#') or next_line.startswith('---')):
                    break
                desc_lines.append(next_line.strip())
                i += 1
            result.append((key, ' '.join(desc_lines)))

        # > block → folded multi-line string
        elif val == '>':
            desc_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t') and (is_new_key(next_line) or next_line.strip().startswith('#')):
                    break
                desc_lines.append(next_line.strip())
                i += 1
            result.append((key, ' '.join(desc_lines)))

        # Regular scalar value
        else:
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            # Handle list values like [a, b, c]
            if val.startswith('[') and val.endswith(']'):
                try:
                    val = json.loads(val)
                except:
                    pass
            result.append((key, val))
            i += 1

    return result


def parse_child_dict(lines):
    """Parse indented child key-value pairs into a dict."""
    d = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' not in stripped:
            continue
        key, _, val = stripped.partition(':')
        key = key.rstrip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        d[key] = val
    return d


def get_color(colors, *keys, default=None):
    for k in keys:
        v = colors.get(k)
        if v and v != 'none':
            return v
    return default


def hex_to_rgba(hex_color, alpha=0.15):
    """Convert hex to rgba string."""
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c*2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'
    except:
        return hex_color


def make_chart_colors(accent, colors):
    """Generate 4 chart series colors from accent and available palette."""
    # Try to use semantic palette colors first
    palette = []
    for candidate in ['accent-purple', 'accent-magenta', 'accent-blue', 'accent-yellow',
                       'accent-green', 'accent-sunset', 'accent-dusk', 'accent-breeze',
                       'accent-twilight', 'block-lime', 'block-lilac', 'block-cream',
                       'block-pink', 'block-mint', 'block-coral', 'accent-yellow-pale',
                       'accent-green-pale', 'accent-purple-pale', 'accent-purple-deep']:
        if candidate in colors:
            palette.append(colors[candidate])
    # Add derived shades of accent
    accent_val = accent.lstrip('#')
    if len(accent_val) == 3:
        accent_val = ''.join(c*2 for c in accent_val)
    try:
        r, g, b = int(accent_val[0:2], 16), int(accent_val[2:4], 16), int(accent_val[4:6], 16)
        palette.extend([
            f'rgb({min(255,r+50)},{max(0,g-30)},{max(0,b-30)})',
            f'rgb({max(0,r-40)},{min(255,g+40)},{min(255,b+40)})',
        ])
    except (ValueError, IndexError):
        palette.extend(['#5470c6', '#91cc75'])
    if not palette:
        return ['#5470c6', '#91cc75', '#fac858', '#ee6666']
    # Pad to 4 distinct colors by deriving more accent variants
    while len(palette) < 4:
        try:
            r, g, b = int(accent_val[0:2], 16), int(accent_val[2:4], 16), int(accent_val[4:6], 16)
            n = len(palette)
            offset_r = min(255, max(0, r + (50 if n % 2 == 0 else -30)))
            offset_g = min(255, max(0, g + (40 if n < 3 else -50)))
            offset_b = min(255, max(0, b + (60 if n == 1 else -20)))
            palette.append(f'rgb({offset_r},{offset_g},{offset_b})')
        except:
            palette.extend(['#5470c6', '#91cc75', '#fac858'])
            break
    result = palette[:4]
    return result


def generate_theme_css(theme_name, design_md_path):
    """Read one DESIGN.md and return CSS and theme metadata."""
    with open(design_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter, _ = parse_front_matter(content)
    if not front_matter:
        # Try to extract colors directly from a simplified format
        return '', None

    colors = front_matter.get('colors', {})
    typography = front_matter.get('typography', {})
    rounded = front_matter.get('rounded', {})

    # === Extract core tokens ===
    accent = get_color(colors, 'primary', 'accent') or '#3366cc'
    accent_text = get_color(colors, 'on-primary', 'on-accent', 'accent-text') or '#ffffff'
    bg = get_color(colors, 'canvas', 'bg', 'background') or '#ffffff'
    text_color = get_color(colors, 'ink', 'body', 'text', 'text-color') or '#1a1a1a'
    surface = get_color(colors, 'surface-soft', 'surface', 'canvas-soft') or '#f5f5f5'
    border = get_color(colors, 'hairline', 'border', 'divider-soft') or '#dddddd'
    surface_raised = get_color(colors, 'surface-raised', 'surface-elevated',
                               'surface-card', 'canvas-card', 'surface-pearl') or '#ece6dd'
    muted = get_color(colors, 'mute', 'muted', 'body-mid', 'ink-muted-48',
                      'body-muted') or '#888888'
    link = get_color(colors, 'link', 'link-blue', 'primary-focus', 'primary') or accent
    success = get_color(colors, 'success', 'semantic-success', 'success-deep') or '#16a34a'
    warning = get_color(colors, 'warning', 'warning-bright') or '#d97706'
    error = get_color(colors, 'error', 'error-deep') or '#dc2626'

    # === Typography ===
    body_font = ''
    heading_font = ''
    line_height = '1.6'

    for role_key in ['body-md', 'body', 'body-lg', 'body-sm']:
        if role_key in typography:
            bf = typography[role_key].get('fontFamily', '')
            if bf:
                body_font = bf
            lh = typography[role_key].get('lineHeight', '')
            if lh:
                line_height = str(lh)
            break

    for role_key in ['display-xl', 'display-lg', 'display-md', 'hero-display', 'headline']:
        if role_key in typography:
            hf = typography[role_key].get('fontFamily', '')
            if hf:
                heading_font = hf
                break

    # === Radius ===
    radius = '8px'
    for rkey in ['md', 'sm', 'lg']:
        if rkey in rounded:
            rv = str(rounded[rkey])
            if rv and rv != '9999px':
                radius = rv
                break

    # === Chart colors ===
    chart_colors = make_chart_colors(accent, colors)

    # === Shadow ===
    shadow_sm = f'0 1px 3px {hex_to_rgba(text_color, 0.1)}'
    shadow_md = f'0 4px 12px {hex_to_rgba(text_color, 0.1)}'
    shadow_lg = f'0 8px 30px {hex_to_rgba(text_color, 0.12)}'

    # === Derived colors ===
    accent_soft = hex_to_rgba(accent, 0.12)
    accent_muted = hex_to_rgba(accent, 0.4)
    tag_bg = hex_to_rgba(accent, 0.1)
    tag_text = accent  # keep the accent for tags
    table_stripe = hex_to_rgba(text_color, 0.04)
    table_header_bg = hex_to_rgba(accent, 0.08)
    blockquote_border = f'4px solid {accent}'
    blockquote_bg = hex_to_rgba(accent, 0.06)
    code_bg = surface
    code_text = accent
    section_gap = '4rem'
    h2_border = f'2px solid {border}'
    toc_accent = accent

    # Build CSS
    css_lines = [f'/* ===== Theme: {theme_name} ===== */', f'[data-theme="{theme_name}"] {{']

    pairs = [
        ('--bg', bg),
        ('--text', text_color),
        ('--accent', accent),
        ('--accent-text', accent_text),
        ('--accent-soft', accent_soft),
        ('--accent-muted', accent_muted),
        ('--surface', surface),
        ('--surface-raised', surface_raised),
        ('--border', border),
        ('--muted', muted),
        ('--link', link),
        ('--success', success),
        ('--warning', warning),
        ('--error', error),
        ('--font', body_font),
        ('--font-h', heading_font),
        ('--lh', line_height),
        ('--body-size', '1rem'),
        ('--small-size', '0.85rem'),
        ('--radius', radius),
        ('--shadow-sm', shadow_sm),
        ('--shadow-md', shadow_md),
        ('--shadow-lg', shadow_lg),
        ('--chart-1', chart_colors[0]),
        ('--chart-2', chart_colors[1]),
        ('--chart-3', chart_colors[2]),
        ('--chart-4', chart_colors[3]),
        ('--tag-bg', tag_bg),
        ('--tag-text', tag_text),
        ('--table-stripe', table_stripe),
        ('--table-header-bg', table_header_bg),
        ('--blockquote-border', blockquote_border),
        ('--blockquote-bg', blockquote_bg),
        ('--code-bg', code_bg),
        ('--code-text', code_text),
        ('--section-gap', section_gap),
        ('--h2-border', h2_border),
        ('--toc-accent', toc_accent),
    ]

    for var, val in pairs:
        if var == '--font-h' and not val:
            val = body_font  # fallback to body font when heading font undefined
        if val:
            css_lines.append(f'  {var}: {val};')

    css_lines.append('}\n')

    metadata = {
        'name': theme_name,
        'accent': accent,
        'accent_text': accent_text,
        'bg': bg,
        'text': text_color,
        'font': body_font,
        'font_h': heading_font,
        'chart_colors': chart_colors,
        'radius': radius,
        'has_dark_bg': is_dark(bg),
    }

    return '\n'.join(css_lines), metadata


def is_dark(color):
    h = color.lstrip('#')
    if len(h) < 6:
        return False
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r * 0.299 + g * 0.587 + b * 0.114) < 128
    except:
        return False


def main():
    themes = []
    all_css_parts = []

    # 默认 warm 主题
    warm_css = '''/* ===== Theme: warm (default) ===== */
[data-theme="warm"] {
  --bg: #faf9f7; --text: #1a1a1a; --accent: #c0392b;
  --accent-text: #ffffff; --accent-soft: rgba(192,57,43,0.12); --accent-muted: rgba(192,57,43,0.4);
  --surface: #f5f0eb; --surface-raised: #ece6dd; --border: #ddd8d0;
  --muted: #888888; --link: #c0392b; --success: #16a34a; --warning: #d97706; --error: #dc2626;
  --font: "Noto Serif CJK SC",Georgia,"Times New Roman",serif;
  --font-h: "Noto Serif CJK SC",Georgia,"Times New Roman",serif;
  --lh: 1.8; --body-size: 1rem; --small-size: 0.85rem;
  --radius: 8px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08); --shadow-md: 0 4px 12px rgba(0,0,0,0.1); --shadow-lg: 0 8px 30px rgba(0,0,0,0.12);
  --chart-1: #c0392b; --chart-2: #e67e22; --chart-3: #2980b9; --chart-4: #27ae60;
  --tag-bg: rgba(192,57,43,0.1); --tag-text: #c0392b;
  --table-stripe: rgba(0,0,0,0.04); --table-header-bg: rgba(192,57,43,0.08);
  --blockquote-border: 4px solid #c0392b; --blockquote-bg: rgba(192,57,43,0.06);
  --code-bg: #f5f0eb; --code-text: #c0392b;
  --section-gap: 4rem; --h2-border: 2px solid #ddd8d0; --toc-accent: #c0392b;
}'''
    all_css_parts.append(warm_css)
    themes.append({
        'name': 'warm',
        'accent': '#c0392b',
        'accent_text': '#ffffff',
        'bg': '#faf9f7',
        'text': '#1a1a1a',
        'font': 'Noto Serif CJK SC, Georgia, serif',
        'font_h': 'Noto Serif CJK SC, Georgia, serif',
        'chart_colors': ['#c0392b', '#e67e22', '#2980b9', '#27ae60'],
        'radius': '8px',
        'has_dark_bg': False,
    })

    # 硬编码特殊主题（无 YAML front matter 的 DESIGN.md）
    MANUAL_THEMES = {
        'spotify': {
            'bg': '#121212', 'text': '#ffffff', 'accent': '#1ed760',
            'accent_text': '#000000', 'surface': '#181818', 'border': '#4d4d4d',
            'surface_raised': '#1f1f1f', 'muted': '#b3b3b3',
            'link': '#1ed760', 'success': '#1ed760', 'warning': '#ffa42b', 'error': '#f3727f',
            'font': '"SpotifyMixUI",sans-serif', 'font_h': '"SpotifyMixUITitle",sans-serif',
            'lh': '1.5', 'radius': '8px',
            'chart_colors': ['#1ed760', '#ffa42b', '#f3727f', '#b3b3b3'],
        },
        'tesla': {
            'bg': '#ffffff', 'text': '#171a20', 'accent': '#3e6ae1',
            'accent_text': '#ffffff', 'surface': '#f4f4f4', 'border': '#d0d1d2',
            'surface_raised': '#f4f4f4', 'muted': '#5c5e62',
            'link': '#3e6ae1', 'success': '#16a34a', 'warning': '#d97706', 'error': '#dc2626',
            'font': '"Universal Sans Text",sans-serif', 'font_h': '"Universal Sans Display",sans-serif',
            'lh': '1.43', 'radius': '4px',
            'chart_colors': ['#3e6ae1', '#16a34a', '#e82127', '#f4f4f4'],
        },
    }

    # 扫描主题目录
    theme_dirs = sorted([d for d in os.listdir(THEME_DIR)
                         if os.path.isdir(os.path.join(THEME_DIR, d))])

    for td in theme_dirs:
        design_md = os.path.join(THEME_DIR, td, 'DESIGN.md')
        if not os.path.isfile(design_md):
            print(f'  [SKIP] {td}/ — no DESIGN.md')
            continue

        css, meta = generate_theme_css(td, design_md)
        if css:
            all_css_parts.append(css)
            themes.append(meta)
            print(f'  [OK]   {td}/ — {meta["accent"]}')
        elif td in MANUAL_THEMES:
            m = MANUAL_THEMES[td]
            css_parts = [f'/* ===== Theme: {td} (manual) ===== */', f'[data-theme="{td}"] {{']
            c = m
            pairs = [
                ('--bg', c['bg']), ('--text', c['text']), ('--accent', c['accent']),
                ('--accent-text', c['accent_text']),
                ('--accent-soft', hex_to_rgba(c['accent'], 0.12)),
                ('--accent-muted', hex_to_rgba(c['accent'], 0.4)),
                ('--surface', c['surface']), ('--surface-raised', c['surface_raised']),
                ('--border', c['border']), ('--muted', c['muted']), ('--link', c['link']),
                ('--success', c['success']), ('--warning', c['warning']), ('--error', c['error']),
                ('--font', c['font']), ('--font-h', c['font_h']), ('--lh', c['lh']),
                ('--radius', c['radius']),
                ('--chart-1', c['chart_colors'][0]), ('--chart-2', c['chart_colors'][1]),
                ('--chart-3', c['chart_colors'][2]), ('--chart-4', c['chart_colors'][3]),
                ('--shadow-sm', f'0 1px 3px {hex_to_rgba(c["text"], 0.1)}'),
                ('--shadow-md', f'0 4px 12px {hex_to_rgba(c["text"], 0.1)}'),
                ('--shadow-lg', f'0 8px 30px {hex_to_rgba(c["text"], 0.12)}'),
                ('--tag-bg', hex_to_rgba(c['accent'], 0.1)),
                ('--tag-text', c['accent']),
                ('--table-stripe', hex_to_rgba(c['text'], 0.04)),
                ('--table-header-bg', hex_to_rgba(c['accent'], 0.08)),
                ('--blockquote-border', f'4px solid {c["accent"]}'),
                ('--blockquote-bg', hex_to_rgba(c['accent'], 0.06)),
                ('--code-bg', c['surface']),
                ('--code-text', c['accent']),
                ('--section-gap', '4rem'),
                ('--h2-border', f'2px solid {c["border"]}'),
                ('--toc-accent', c['accent']),
            ]
            for var, val in pairs:
                if val:
                    css_parts.append(f'  {var}: {val};')
            css_parts.append('}\n')
            gen_css = '\n'.join(css_parts)
            all_css_parts.append(gen_css)

            meta = {
                'name': td, 'accent': c['accent'], 'accent_text': c['accent_text'],
                'bg': c['bg'], 'text': c['text'], 'font': c['font'], 'font_h': c['font_h'],
                'chart_colors': c['chart_colors'],
                'radius': c['radius'], 'has_dark_bg': is_dark(c['bg']),
            }
            themes.append(meta)
            print(f'  [MANUAL] {td}/ — {c["accent"]}')
        else:
            print(f'  [WARN] {td}/ — no YAML front matter found')

    # 写入 CSS
    css_header = '''/* ===== context2html — Report Themes ===== */
/* Auto-generated by scripts/generate-theme-css.py */
/* Do not edit directly — edit theme/*/DESIGN.md and run generate-theme-css.py */

'''
    full_css = css_header + '\n'.join(all_css_parts)
    with open(OUTPUT_CSS, 'w', encoding='utf-8') as f:
        f.write(full_css)
    print(f'\n[OK] Written: {OUTPUT_CSS} ({len(themes)} themes)')

    # 写入 JSON 索引
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(themes, f, ensure_ascii=False, indent=2)
    print(f'[OK] Written: {OUTPUT_JSON}')

    # 生成 markdown 索引
    generate_markdown_index(themes)

    print('\nDone.')


def generate_markdown_index(themes):
    """Generate theme-index.md reference doc."""
    lines = [
        '# context2html — 主题索引\n',
        f'共 {len(themes)} 个主题，由 `scripts/generate-theme-css.py` 从 `theme/*/DESIGN.md` 自动生成。\n',
        '## 主题一览\n',
        '| 主题 | 主色 | 背景 | 字体 | 圆角 | 深色 | 推荐场景 |',
        '|---|---|---|---|---|---|---|',
    ]

    scene_suggestions = {
        'warm': '通用报告',
        'apple': '消费电子、产品评测',
        'nvidia': '技术报告、GPU/芯片分析',
        'spotify': '音乐、流媒体、娱乐行业',
        'tesla': '汽车、新能源、工程报告',
        'airbnb': '旅游、生活、消费市场',
        'airtable': 'SaaS、数据分析',
        'binance': '金融、区块链、投资',
        'bmw-m': '汽车、高端制造、运动',
        'claude': 'AI 产品、设计思考',
        'cursor': '开发者工具、编程',
        'dell-1996': '复古科技、怀旧',
        'figma': '设计工具、创意行业',
        'hp': '企业服务、打印/硬件',
        'ibm': '企业咨询、传统IT',
        'minimax': 'AI 公司、多媒体',
        'nike': '运动、品牌、消费市场',
        'notion': '知识管理、生产力',
        'x.ai': '前沿AI、深色科技',
        'zapier': '自动化、SaaS 集成',
    }

    for t in themes:
        name = t['name']
        accent = t.get('accent', '—')
        bg = t.get('bg', '—')
        font = t.get('font', '—')[:30]
        radius = t.get('radius', '—')
        dark = '✅' if t.get('has_dark_bg') else ''
        scene = scene_suggestions.get(name, '通用')
        lines.append(f'| `{name}` | `{accent}` | {bg} | {font}… | {radius} | {dark} | {scene} |')

    lines.extend([
        '',
        '## 主题切换方式',
        '',
        '- **T 键**：循环切换',
        '- **面板按钮**：点击主题色点切换',
        '- **自动保存**：localStorage 记住选择',
        '',
        '## 添加新主题',
        '',
        '1. 在 teach_more_pic 的 `theme/` 下新建目录 + DESIGN.md',
        '2. 运行 `python scripts/generate-theme-css.py`',
        '3. 将生成的 CSS 提交到本仓库',
        '',
    ])

    output_path = os.path.join(PROJECT_DIR, 'docs', 'theme-index.md')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] Written: {output_path}')


if __name__ == '__main__':
    main()
