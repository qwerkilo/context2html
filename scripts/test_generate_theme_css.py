import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location(
    "gc", os.path.join(os.path.dirname(__file__), "generate-theme-css.py"))
gc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gc)


class TestParseFrontMatter:
    def test_empty_string(self):
        assert gc.parse_front_matter("") == ({}, "")

    def test_no_front_matter(self):
        assert gc.parse_front_matter("plain text\ncontent") == ({}, "plain text\ncontent")

    def test_basic_yaml_colors(self):
        text = "---\ncolors:\n  primary: '#ff0000'\n  bg: '#ffffff'\n---\nbody"
        result, body = gc.parse_front_matter(text)
        assert result["colors"]["primary"] == "#ff0000"
        assert "body" in body

    def test_multiline_block(self):
        text = "---\ndescription: |\n  line1\n  line2\n---\n"
        result, _ = gc.parse_front_matter(text)
        assert "line1" in result.get("description", "")

    def test_list_value(self):
        text = "---\ntags: [a, b, c]\n---\n"
        result, _ = gc.parse_front_matter(text)
        assert result.get("tags") == ["a", "b", "c"]

    def test_dotdotend(self):
        text = "---\nkey: val\n...\nbody"
        result, body = gc.parse_front_matter(text)
        assert result.get("key") == "val"
        assert body.strip() == "body"


class TestHexToRgba:
    def test_full_hex(self):
        assert gc.hex_to_rgba("#ff0000", 0.5) == "rgba(255,0,0,0.5)"

    def test_shorthand_hex(self):
        assert gc.hex_to_rgba("#f00") == "rgba(255,0,0,0.15)"

    def test_invalid_hex(self):
        assert gc.hex_to_rgba("notcolor") == "notcolor"


class TestGetColor:
    def test_direct_match(self):
        assert gc.get_color({"primary": "#123"}, "primary") == "#123"

    def test_fallback_keys(self):
        assert gc.get_color({"accent": "#456"}, "primary", "accent") == "#456"

    def test_none_ignored(self):
        assert gc.get_color({"primary": "none"}, "primary", default="#999") == "#999"

    def test_default_returned(self):
        assert gc.get_color({}, "missing", default="#000") == "#000"


class TestMakeChartColors:
    def test_empty_palette_derives_from_accent(self):
        result = gc.make_chart_colors("#3366cc", {})
        assert len(result) == 4
        assert "rgb" in result[0]

    def test_uses_palette_colors(self):
        colors = {"accent-purple": "#7e57c2"}
        result = gc.make_chart_colors("#3366cc", colors)
        assert "#7e57c2" in result
        assert len(result) == 4
