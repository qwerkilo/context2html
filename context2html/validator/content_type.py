"""Content-type detection and validation."""
import re

_RE_DATA_CONTENT_TYPE = re.compile(r'data-content-type\s*=\s*["\'](\w+)["\']')


def detect_content_type(html):
    m = _RE_DATA_CONTENT_TYPE.search(html)
    return m.group(1) if m else 'report'


def check_content_type_valid(html):
    ct = detect_content_type(html)
    valid_types = ['report', 'article', 'doc', 'tutorial', 'note']
    if ct not in valid_types:
        return [f"Invalid data-content-type: '{ct}' (valid: {', '.join(valid_types)})"]
    return []
