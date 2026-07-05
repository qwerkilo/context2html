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


def extract_code_block(content, lang):
    """Find the first ```lang fenced code block, return its content."""
    pattern = re.compile(
        r'^`{3}' + re.escape(lang) + r'\s*\n(.*?)\n^`{3}',
        re.MULTILINE | re.DOTALL
    )
    m = pattern.search(content)
    if m:
        return m.group(1).strip()
    return None


def extract_js_from_md(content):
    """Extract JS from markdown. Prefers ```js block, falls back to
    ```html block containing <script>.
    """
    js = extract_code_block(content, 'js')
    if js:
        return js
    pattern = re.compile(
        r'^`{3}html\s*\n(.*?)\n^`{3}',
        re.MULTILINE | re.DOTALL
    )
    for m in pattern.finditer(content):
        block = m.group(1)
        if '<script' in block:
            return block.strip()
    return ''
