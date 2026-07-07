"""Shared utilities for parsing markdown front matter and code blocks."""

import re
import yaml


def parse_front_matter(text):
    """Parse YAML front matter from markdown text.
    Returns (dict, body) — dict is empty if no front matter found.
    """
    m = re.match(r'^---\s*\n(.*?)\n(?:---|\.\.\.)', text, re.DOTALL)
    if not m:
        return {}, text
    yaml_text = m.group(1)
    body = text[m.end():]
    try:
        result = yaml.safe_load(yaml_text)
        if isinstance(result, dict):
            return result, body
    except yaml.YAMLError:
        pass
    return {}, body


def extract_code_block(content, lang, multi=False):
    """Find fenced code blocks for a given language.
    Returns first block content (str) when multi=False.
    Returns list of all block contents (list[str]) when multi=True.
    """
    pattern = re.compile(
        r'^`{3}' + re.escape(lang) + r'\s*\n(.*?)\n^`{3}',
        re.MULTILINE | re.DOTALL
    )
    if multi:
        return [m.group(1).strip() for m in pattern.finditer(content)]
    m = pattern.search(content)
    if m:
        return m.group(1).strip()
    return None


def extract_js_from_md(content, multi=False):
    """Extract JS from markdown. Prefers ```js block, falls back to
    ```html block containing <script>.
    Returns str when multi=False.
    Returns list[str] when multi=True (consistent with extract_code_block).
    """
    js_blocks = extract_code_block(content, 'js', multi=True)
    if js_blocks:
        if multi:
            return js_blocks
        return '\n'.join(js_blocks)

    pattern = re.compile(
        r'^`{3}html\s*\n(.*?)\n^`{3}',
        re.MULTILINE | re.DOTALL
    )
    script_blocks = []
    for m in pattern.finditer(content):
        block = m.group(1)
        if '<script' in block:
            script_blocks.append(block.strip())

    if multi:
        return script_blocks
    return script_blocks[0] if script_blocks else ''
