import sys, os, re, importlib.util
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
    def test_short_hex_doesnt_crash(self):
        result = gc.make_chart_colors("#f00", {})
        assert len(result) == 4
        assert isinstance(result[0], str)
    def test_invalid_hex_doesnt_crash(self):
        result = gc.make_chart_colors("not-a-color", {})
        assert len(result) >= 2


class TestManualThemeVars:
    REQUIRED = [
        '--bg', '--text', '--accent', '--accent-text', '--accent-soft', '--accent-muted',
        '--surface', '--surface-raised', '--border', '--muted', '--link',
        '--success', '--warning', '--error',
        '--font', '--font-h', '--lh', '--radius',
        '--chart-1', '--chart-2', '--chart-3', '--chart-4',
        '--shadow-sm', '--shadow-md', '--shadow-lg',
        '--tag-bg', '--tag-text',
        '--table-stripe', '--table-header-bg',
        '--blockquote-border', '--blockquote-bg',
        '--code-bg', '--code-text',
        '--section-gap', '--h2-border', '--toc-accent',
    ]
    THEME_CSS_PATH = os.path.join(os.path.dirname(__file__), '..', 'theme', 'report-themes.css')

    @staticmethod
    def _get_theme_blocks():
        with open(TestManualThemeVars.THEME_CSS_PATH, 'r', encoding='utf-8') as f:
            css = f.read()
        blocks = {}
        for m in re.finditer(r'\[data-theme="([^"]+)"\]\s*\{(.*?)\}', css, re.DOTALL):
            blocks[m.group(1)] = m.group(2)
        return blocks

    def test_all_20_themes_present(self):
        blocks = self._get_theme_blocks()
        assert len(blocks) >= 20, f"Expected ≥20 themes, got {len(blocks)}"

    def test_spotify_has_all_vars(self):
        blocks = self._get_theme_blocks()
        for var in self.REQUIRED:
            assert var in blocks.get('spotify', ''), f"spotify missing {var}"

    def test_tesla_has_all_vars(self):
        blocks = self._get_theme_blocks()
        for var in self.REQUIRED:
            assert var in blocks.get('tesla', ''), f"tesla missing {var}"

    def test_warm_has_all_vars(self):
        blocks = self._get_theme_blocks()
        for var in self.REQUIRED:
            assert var in blocks.get('warm', ''), f"warm missing {var}"

    def test_airbnb_has_all_vars(self):
        blocks = self._get_theme_blocks()
        for var in self.REQUIRED:
            assert var in blocks.get('airbnb', ''), f"airbnb missing {var}"


class TestIsDark:
    def test_black_is_dark(self):
        assert gc.is_dark('#000000') == True
    def test_bright_yellow_is_not_dark(self):
        assert gc.is_dark('#FFD700') == False
    def test_white_is_not_dark(self):
        assert gc.is_dark('#FFFFFF') == False

class TestSplitYamlSections:
    def test_simple_pairs(self):
        result = gc.split_yaml_sections("a: 1\nb: 2")
        assert result == [("a", "1"), ("b", "2")]
    def test_double_dash_not_separator(self):
        result = gc.split_yaml_sections("a: --\nb: 2")
        assert len(result) == 2

class TestParseChildDict:
    def test_empty_list(self):
        assert gc.parse_child_dict([]) == {}
    def test_simple_kv(self):
        result = gc.parse_child_dict(['  key: value', '  foo: bar'])
        assert result == {'key': 'value', 'foo': 'bar'}
    def test_quoted_values(self):
        result = gc.parse_child_dict(['  key: "value"', "  foo: 'bar'"])
        assert result == {'key': 'value', 'foo': 'bar'}

class TestIsNewKey:
    def test_simple_key(self):
        assert gc.is_new_key('colors:')
    def test_url_is_not_key(self):
        assert not gc.is_new_key('https://example.com')
    def test_key_with_value(self):
        assert gc.is_new_key('description: A thing: nice')

class TestGenerateThemeCss:
    def test_generates_valid_css(self, tmp_path):
        d = tmp_path / "DESIGN.md"
        d.write_text("---\ncolors:\n  primary: '#c0392b'\n  bg: '#ffffff'\n  text: '#333333'\n---\n")
        css, meta = gc.generate_theme_css('test-theme', str(d))
        assert meta is not None
        assert '--bg: #ffffff' in css
        assert '--accent: #c0392b' in css
    def test_generates_without_palette(self, tmp_path):
        d = tmp_path / "DESIGN.md"
        d.write_text("---\ncolors:\n  primary: '#c0392b'\n  bg: '#ffffff'\n---\n")
        css, meta = gc.generate_theme_css('test-theme', str(d))
        assert meta is not None
        assert '--bg: #ffffff' in css
        assert '--accent-text' in css
    def test_no_front_matter_returns_none(self, tmp_path):
        d = tmp_path / "DESIGN.md"
        d.write_text("no front matter here\n")
        css, meta = gc.generate_theme_css('test-theme', str(d))
        assert css == ''
        assert meta is None
    def test_empty_colors_uses_defaults(self, tmp_path):
        d = tmp_path / "DESIGN.md"
        d.write_text("---\ncolors:\n  bg: '#111111'\n---\n")
        css, meta = gc.generate_theme_css('test-theme', str(d))
        assert meta is not None
        assert '--accent: #3366cc' in css
        assert '--bg: #111111' in css
