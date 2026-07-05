"""Tests for context2html.markdown_utils."""
from context2html.markdown_utils import parse_front_matter, extract_code_block, extract_js_from_md


class TestParseFrontMatter:
    def test_empty_string(self):
        result, body = parse_front_matter("")
        assert result == {}
        assert body == ""

    def test_no_front_matter(self):
        result, body = parse_front_matter("plain text\nno front matter")
        assert result == {}
        assert "plain" in body

    def test_basic_yaml(self):
        text = "---\nid: 26\nname: test\n---\nbody here"
        result, body = parse_front_matter(text)
        assert result["id"] == 26
        assert result["name"] == "test"
        assert body.strip() == "body here"

    def test_yaml_with_list(self):
        text = "---\ndeps: [a, b, c]\n---\nbody"
        result, body = parse_front_matter(text)
        assert result["deps"] == ["a", "b", "c"]

    def test_invalid_yaml_returns_empty(self):
        text = "---\n: invalid yaml\n:\n---\nbody"
        result, body = parse_front_matter(text)
        assert result == {}

    def test_dot_dot_dot_separator(self):
        text = "---\nkey: val\n...\nbody"
        result, body = parse_front_matter(text)
        assert result.get("key") == "val"

    def test_only_dashes_no_yaml(self):
        text = "---\nbody after"
        result, body = parse_front_matter(text)
        # lone dashes with no closing ---: the regex requires closing --- or ...
        # so this is treated as no front matter
        assert result == {}


class TestExtractCodeBlock:
    def test_simple_html_block(self):
        md = "```html\n<div>hello</div>\n```"
        assert extract_code_block(md, "html") == "<div>hello</div>"

    def test_no_block(self):
        md = "plain text"
        assert extract_code_block(md, "html") is None

    def test_first_block_returned(self):
        md = "```html\n<div>1</div>\n```\n\n```html\n<div>2</div>\n```"
        assert extract_code_block(md, "html") == "<div>1</div>"

    def test_css_block(self):
        md = "```css\n.foo { color: red; }\n```"
        assert extract_code_block(md, "css") == ".foo { color: red; }"


class TestExtractJsFromMd:
    def test_explicit_js_block(self):
        md = "```js\nvar x = 1;\n```"
        assert extract_js_from_md(md) == "var x = 1;"

    def test_html_block_with_script(self):
        md = "```html\n<script>var x = 1;</script>\n```"
        assert "<script>" in extract_js_from_md(md)

    def test_no_js_found(self):
        md = "plain text\n```css\na {}\n```"
        assert extract_js_from_md(md) == ""

    def test_js_block_preferred_over_html(self):
        md = "```js\nvar y = 2;\n```\n```html\n<script>var x = 1;</script>\n```"
        assert extract_js_from_md(md) == "var y = 2;"
