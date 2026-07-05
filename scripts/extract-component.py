"""Extract HTML/CSS/JS code blocks from component .md files.
Usage:
  python extract-component.py HTML <component.md>   # Extract HTML
  python extract-component.py CSS <component.md>    # Extract CSS
  python extract-component.py JS <component.md>     # Extract JS
  python extract-component.py LIST                  # List all components
"""
import os
import sys
import glob
import re

from context2html.markdown_utils import extract_code_block, extract_js_from_md


def extract_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return extract_code_block(content, 'html') or ''


def extract_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return extract_code_block(content, 'css') or ''


def extract_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return extract_js_from_md(content)


def list_components():
    components_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'components')
    files = sorted(glob.glob(os.path.join(components_dir, '*.md')))
    results = []
    for f in files:
        basename = os.path.basename(f)
        match = re.match(r'(\d+)-(.+)\.md$', basename)
        if match:
            num = match.group(1)
            name = match.group(2).replace('-', ' ').title()
            results.append((num, name, basename))
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    mode = sys.argv[1].upper()

    if mode == 'LIST':
        components = list_components()
        if not components:
            print("No components found in components/")
            sys.exit(1)
        for num, name, fname in components:
            print(f"{num}: {name}  ({fname})")
        return

    if len(sys.argv) < 3:
        print("Usage: python extract-component.py HTML|CSS|JS <component.md>")
        sys.exit(1)

    filepath = sys.argv[2]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    mode_map = {
        'HTML': extract_html,
        'CSS': extract_css,
        'JS': extract_js,
    }

    extractor = mode_map.get(mode)
    if not extractor:
        print(f"Unknown mode: {mode}. Use HTML, CSS, JS, or LIST.")
        sys.exit(1)

    result = extractor(filepath)
    if not result:
        print(f"No {mode} block found in {os.path.basename(filepath)}")
        sys.exit(1)

    print(result)


if __name__ == '__main__':
    main()
