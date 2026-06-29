"""Unit tests for validate-report.py check functions."""
import sys, os, tempfile, importlib.util
spec = importlib.util.spec_from_file_location("vr", os.path.join(os.path.dirname(__file__), "validate-report.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

PASS = 0
FAIL = 0

def test(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")

# ==== check_report_sections (exec_summary, report_chapters, conclusion_page, report_footer) ====

test("exec_summary: present passes", not v.check_exec_summary(
    '<style>.exec-summary{}</style><div class="exec-summary"><p>Key findings</p></div>'))
test("exec_summary: missing fails", len(v.check_exec_summary(
    '<div class="summary">no exec here</div>')) > 0)
test("exec_summary: empty html fails", len(v.check_exec_summary(
    '')) > 0)

test("report_chapters: one chapter passes", not v.check_report_chapters(
    '<div class="report-chapter"><h2>Chapter 1</h2></div>'))
test("report_chapters: multiple chapters passes", not v.check_report_chapters(
    '<div class="report-chapter">A</div><div class="report-chapter">B</div>'))
test("report_chapters: none fails", len(v.check_report_chapters(
    '<div class="chapter">no report-chapter</div>')) > 0)
test("report_chapters: empty fails", len(v.check_report_chapters(
    '')) > 0)

test("conclusion_page: present passes", not v.check_conclusion_page(
    '<style>.conclusion-page{}</style><section class="conclusion-page"><p>Conclusion</p></section>'))
test("conclusion_page: missing fails", len(v.check_conclusion_page(
    '<section class="results">no conclusion</section>')) > 0)
test("conclusion_page: empty fails", len(v.check_conclusion_page(
    '')) > 0)

test("report_footer: present passes", not v.check_report_footer(
    '<style>.report-footer{}</style><footer class="report-footer"><p>Footer</p></footer>'))
test("report_footer: missing fails", len(v.check_report_footer(
    '<footer>no report-footer here</footer>')) > 0)
test("report_footer: empty fails", len(v.check_report_footer(
    '')) > 0)

# ==== check_bilingual_report ====

test("bilingual: no data-lang skips", not v.check_bilingual(
    '<html><p>no lang attributes</p></html>'))
test("bilingual: zh+en+btn+key passes", not v.check_bilingual(
    '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>'
    '<button data-lang-btn></button>key==="l"</html>'))
test("bilingual: missing zh fails", len(v.check_bilingual(
    '<html><span data-lang="en">EN</span><button data-lang-btn></button>key==="l"</html>')) > 0)
test("bilingual: missing en fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0)
test("bilingual: missing toggle fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>key==="l"</html>')) > 0)
test("bilingual: missing L key fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><span data-lang="en">EN</span><button data-lang-btn></button></html>')) > 0)
test("bilingual: both missing but no data-lang skips", not v.check_bilingual(
    '<html><p>no bilingual at all</p></html>'))
test("bilingual: single lang with toggle fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0)

# ==== check_theme_css_referenced ====

test("theme_css: link present passes", not v.check_theme_css(
    '<link href="theme/report-themes.css" rel="stylesheet">'))
test("theme_css: missing link fails", len(v.check_theme_css(
    '<link href="theme/other.css" rel="stylesheet">')) > 0)
test("theme_css: CDN link flagged", len(v.check_theme_css(
    '<link href="https://cdn.example.com/report-themes.css" rel="stylesheet">')) > 0)
test("theme_css: multiple refs OK", not v.check_theme_css(
    '<link href="theme/report-themes.css"><link href="theme/report-themes.css">'))
test("theme_css: empty html fails", len(v.check_theme_css('')) > 0)
test("theme_css: data uri not link fails", len(v.check_theme_css(
    '<style>@import "data:text/css,..."</style>')) > 0)
test("theme_css: relative path okay", not v.check_theme_css(
    '<link href="../theme/report-themes.css" rel="stylesheet">'))

# ==== check_report_svg (check_svg_links) ====

tmpdir = tempfile.mkdtemp()
valid_svg = os.path.join(tmpdir, "chart-ok.svg")
with open(valid_svg, "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"/></svg>')
invalid_svg = os.path.join(tmpdir, "chart-bad.svg")
with open(invalid_svg, "w") as f:
    f.write("not valid xml {{{")

test("svg links: no SVGs passes", not v.check_svg_links(
    '<html><p>no svg</p></html>', tmpdir))
test("svg links: valid SVG passes", not v.check_svg_links(
    f'<html><img src="chart-ok.svg"/></html>', tmpdir))
test("svg links: missing SVG fails", len(v.check_svg_links(
    '<html><img src="missing.svg"/></html>', tmpdir)) > 0)
test("svg links: invalid XML fails", len(v.check_svg_links(
    f'<html><img src="chart-bad.svg"/></html>', tmpdir)) > 0)
test("svg links: mixed valid+invalid fails", len(v.check_svg_links(
    f'<html><img src="chart-ok.svg"/><img src="missing.svg"/></html>', tmpdir)) > 0)
test("svg links: multiple valid passes", not v.check_svg_links(
    f'<html><img src="chart-ok.svg"/><img src="chart-ok.svg"/></html>', tmpdir))

# clean up SVG test files
for fname in ["chart-ok.svg", "chart-bad.svg"]:
    os.unlink(os.path.join(tmpdir, fname))
os.rmdir(tmpdir)

# ==== check_focus_visible ====

test("focus-visible: present passes", not v.check_focus_visible(
    '<style>:focus-visible { outline: 2px solid red; }</style>'))
test("focus-visible: missing fails", len(v.check_focus_visible(
    '<style>body { color: red; }</style>')) > 0)
test("focus-visible: in inline style passes", not v.check_focus_visible(
    '<html style="--focus-visible: 1px solid"><style>:focus-visible{}</style></html>'))
test("focus-visible: empty html fails", len(v.check_focus_visible('')) > 0)
test("focus-visible: only style comment passes", not v.check_focus_visible(
    '<!-- :focus-visible is important -->'))
test("focus-visible: with focus-visible class passes", not v.check_focus_visible(
    '<style>.custom:focus-visible { outline: 3px solid blue; }</style>'))

# ==== check_tabular_nums ====

test("tabular-nums: present passes", not v.check_tabular_nums(
    '<style>body { font-variant-numeric: tabular-nums; }</style>'))
test("tabular-nums: missing fails", len(v.check_tabular_nums(
    '<style>body { color: red; }</style>')) > 0)
test("tabular-nums: in shorthand passes", not v.check_tabular_nums(
    '<style>body { font: 16px/1.5 sans-serif; font-variant-numeric: tabular-nums; }</style>'))
test("tabular-nums: empty html fails", len(v.check_tabular_nums('')) > 0)
test("tabular-nums: multiple declarations passes", not v.check_tabular_nums(
    '<style>.a{font-variant-numeric:tabular-nums}.b{font-variant-numeric:normal}</style>'))
test("tabular-nums: in class attr passes", not v.check_tabular_nums(
    '<div class="tabular-nums-values">123</div>'))

# ==== check_semantic_html ====

test("semantic: article present passes", not v.check_semantic_html(
    '<html><article></article></html>'))
test("semantic: section present passes", not v.check_semantic_html(
    '<html><section></section></html>'))
test("semantic: nav present passes", not v.check_semantic_html(
    '<html><nav></nav></html>'))
test("semantic: aside present passes", not v.check_semantic_html(
    '<html><aside></aside></html>'))
test("semantic: main present passes", not v.check_semantic_html(
    '<html><main></main></html>'))
test("semantic: none fails", len(v.check_semantic_html(
    '<html><div></div></html>')) > 0)
test("semantic: empty fails", len(v.check_semantic_html('')) > 0)
test("semantic: multiple nested passes", not v.check_semantic_html(
    '<html><nav><article><section></section></article></nav></html>'))

# ==== check_h1_count ====

test("h1: exactly one passes", not v.check_h1_count("<html><h1>Title</h1></html>"))
test("h1: zero fails", len(v.check_h1_count("<html></html>")) > 0)
test("h1: two fails", len(v.check_h1_count("<html><h1>A</h1><h1>B</h1></html>")) > 0)
test("h1: bilingual with data-lang passes", not v.check_h1_count(
    '<html><h1 data-lang="zh">标题</h1><h1 data-lang="en">Title</h1></html>'))
test("h1: bilingual mismatch fails", len(v.check_h1_count(
    '<html><h1 data-lang="zh">标题</h1><h1 data-lang="zh">第二标题</h1></html>')) > 0)

# ==== check_relative_links ====

test("rel links: relative passes", not v.check_relative_links(
    '<a href="0021-slug.html">link</a>'))
test("rel links: absolute / fails", len(v.check_relative_links(
    '<a href="/reports/x.html">link</a>')) > 0)
test("rel links: absolute http fails", len(v.check_relative_links(
    '<a href="https://example.com/report.html">link</a>')) > 0)
test("rel links: no .html links passes", not v.check_relative_links(
    '<a href="https://example.com">link</a>'))
test("rel links: same-dir relative passes", not v.check_relative_links(
    '<a href="./sub/report.html">link</a>'))

# ==== check_svg_contrast ====

tmpdir2 = tempfile.mkdtemp()
safe_svg = os.path.join(tmpdir2, "safe.svg")
with open(safe_svg, "w") as f:
    f.write('<svg><rect fill="#333" width="100"/><text fill="#fff">white on dark</text></svg>')
risky_svg = os.path.join(tmpdir2, "risky.svg")
with open(risky_svg, "w") as f:
    f.write('<svg><rect fill="#fef2f2" width="100"/><text fill="#fff">white on light</text></svg>')

test("svg contrast: no SVGs passes", not v.check_svg_contrast(
    '<html><p>hello</p></html>', tmpdir2))
test("svg contrast: safe colors passes", not v.check_svg_contrast(
    f'<html><img src="safe.svg"/></html>', tmpdir2))
test("svg contrast: light fill + white text fails", len(v.check_svg_contrast(
    f'<html><img src="risky.svg"/></html>', tmpdir2)) > 0)
test("svg contrast: missing file no crash", not v.check_svg_contrast(
    '<html><img src="noexist.svg"/></html>', tmpdir2))
test("svg contrast: mixed safe+risky fails", len(v.check_svg_contrast(
    f'<html><img src="safe.svg"/><img src="risky.svg"/></html>', tmpdir2)) > 0)

for fname in ["safe.svg", "risky.svg"]:
    os.unlink(os.path.join(tmpdir2, fname))
os.rmdir(tmpdir2)

# ==== check_lib_deps ====

test("lib deps: no echarts/three.js passes", not v.check_lib_deps(
    '<html><p>hello</p></html>', '.'))
test("lib deps: echarts CDN passes", not v.check_lib_deps(
    '<html><script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>echarts.init()</html>', '.'))
test("lib deps: echarts local passes", not v.check_lib_deps(
    '<html>echarts.init()</html>', '.'))
test("lib deps: three.js CDN passes", not v.check_lib_deps(
    '<html><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>new THREE.Scene()</html>', '.'))
test("lib deps: three.js local passes", not v.check_lib_deps(
    '<html>new THREE.Scene()</html>', '.'))
test("lib deps: echarts no lib fails", len(v.check_lib_deps(
    '<html>echarts.init()</html>', 'C:\\nonexistent')) > 0)
test("lib deps: three.js no lib fails", len(v.check_lib_deps(
    '<html>new THREE.Scene()</html>', 'C:\\nonexistent')) > 0)
test("lib deps: d3.js CDN passes", not v.check_lib_deps(
    '<html><script src="https://d3js.org/d3.v7.min.js"></script>d3.forceSimulation()</html>', '.'))
test("lib deps: d3.js no lib fails", len(v.check_lib_deps(
    '<html>d3.select("body")</html>', 'C:\\nonexistent')) > 0)
test("lib deps: echarts GL no lib fails", len(v.check_lib_deps(
    '<html>type: "bar3D"</html>', 'C:\\nonexistent')) > 0)

# ==== Results ====
print(f"\n{PASS} passed, {FAIL} failed")
if FAIL > 0:
    sys.exit(1)
