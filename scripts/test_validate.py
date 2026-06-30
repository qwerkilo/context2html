"""Unit tests for validate-lesson.py check functions."""
import sys, os, importlib.util
spec = importlib.util.spec_from_file_location("vl", os.path.join(os.path.dirname(__file__), "validate-lesson.py"))
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

# ==== check_h1_count ====
test("h1: exactly one passes", not v.check_h1_count("<html><h1>Title</h1></html>"))
test("h1: zero fails", len(v.check_h1_count("<html></html>")) > 0)
test("h1: two fails", len(v.check_h1_count("<html><h1>A</h1><h1>B</h1></html>")) > 0)

# ==== check_relative_links ====
test("rel links: relative passes", not v.check_relative_links('<a href="0021-slug.html">link</a>'))
test("rel links: absolute / fails", len(v.check_relative_links('<a href="/lessons/x.html">link</a>')) > 0)
test("rel links: absolute http fails", len(v.check_relative_links('<a href="https://example.com/x.html">link</a>')) > 0)

# ==== check_quiz_correct_count ====
test("quiz: single correct passes", not v.check_quiz_correct_count(
    '<div class="quiz-question"><button data-correct="true">A</button><button data-correct="false">B</button></div>'))
test("quiz: zero correct fails", len(v.check_quiz_correct_count(
    '<div class="quiz-question"><button data-correct="false">A</button></div>')) > 0)
test("quiz: two correct fails", len(v.check_quiz_correct_count(
    '<div class="quiz-question"><button data-correct="true">A</button><button data-correct="true">B</button></div>')) > 0)

# ==== check_quiz_completeness ====
test("quiz comp: 5 questions passes", not v.check_quiz_completeness(
    '<div class="quiz-question"><button class="quiz-option">A</button><button class="quiz-option">B</button><button class="quiz-option">C</button></div>' * 5))
test("quiz comp: 3 questions fails", len(v.check_quiz_completeness(
    '<div class="quiz-question"></div>' * 3)) > 0)
test("quiz comp: wrong options count fails", len(v.check_quiz_completeness(
    '<div class="quiz-question"><button class="quiz-option">A</button><button class="quiz-option">B</button></div>' * 5)) > 0)

# ==== check_data_anim_syntax ====
test("anim: valid values pass", not v.check_data_anim_syntax('<div data-anim="fade-up"></div>'))
test("anim: invalid value fails", len(v.check_data_anim_syntax('<div data-anim="zoom-in"></div>')) > 0)

# ==== check_ppt_js ====
test("ppt: theme+nav present passes", not v.check_ppt_js(
    '<html data-theme="warm"><h2>A</h2><h2>B</h2>'
    'key==="t" key==="ArrowRight" tp-btn-toggle tp-item</html>'))
test("ppt: missing T key fails", len(v.check_ppt_js(
    '<html data-theme="warm">tp-item</html>')) > 0)

# ==== check_inline_svg ====
test("inline svg: with wrapper passes", not v.check_inline_svg(
    '<figure class="svg-fig"><svg xmlns="..."></svg></figure>'))
test("inline svg: no wrapper fails", len(v.check_inline_svg('<svg xmlns="..."></svg>')) > 0)
test("inline svg: icon svg passes", not v.check_inline_svg(
    '<button><svg width="16" height="16" viewBox="0 0 20 20"></svg></button>'))
test("inline svg: 24px icon passes", not v.check_inline_svg(
    '<span><svg width="24" height="24" viewBox="0 0 24 24"></svg></span>'))
test("inline svg: 28px icon passes", not v.check_inline_svg(
    '<span><svg width="28" height="28" viewBox="0 0 24 24"></svg></span>'))
test("inline svg: pie chart in figure passes", not v.check_inline_svg(
    '<figure class="svg-fig"><svg viewBox="0 0 100 100" width="240"></svg></figure>'))
test("inline svg: pie chart no figure fails", len(v.check_inline_svg(
    '<svg viewBox="0 0 100 100" width="240"></svg>')) > 0)

# ==== check_component_consistency ====
test("lbox: trigger+target passes", not v.check_component_consistency(
    '<span data-lbox="chart-1"></span><div id="lbox-chart-1"></div>'))
test("lbox: trigger no target fails", len(v.check_component_consistency(
    '<span data-lbox="chart-1"></span>')) > 0)
test("panel: trigger+target passes", not v.check_component_consistency(
    '<span data-panel="glossary"></span><div id="panel-glossary"></div>'))
test("panel: trigger no target fails", len(v.check_component_consistency(
    '<span data-panel="glossary"></span>')) > 0)
test("popover: trigger+target passes", not v.check_component_consistency(
    '<button popovertarget="pop-1"></button><div id="pop-1" popover></div>'))
test("popover: trigger no target fails", len(v.check_component_consistency(
    '<button popovertarget="pop-1"></button>')) > 0)
test("dialog: with close passes", not v.check_component_consistency(
    '<dialog><button onclick="this.closest(\'dialog\').close()">x</button></dialog>'))
test("dialog: no close fails", len(v.check_component_consistency(
    '<dialog></dialog>')) > 0)

# ==== check_focus_visible ====
test("focus-visible: present passes", not v.check_focus_visible(
    '<style>:focus-visible { outline: 2px solid red; }</style>'))
test("focus-visible: missing fails", len(v.check_focus_visible(
    '<style>body { color: red; }</style>')) > 0)

# ==== check_tabular_nums ====
test("tabular-nums: present passes", not v.check_tabular_nums(
    '<style>body { font-variant-numeric: tabular-nums; }</style>'))
test("tabular-nums: missing fails", len(v.check_tabular_nums(
    '<style>body { color: red; }</style>')) > 0)

# ==== check_semantic_html ====
test("semantic: article present passes", not v.check_semantic_html(
    '<html><article></article></html>'))
test("semantic: section present passes", not v.check_semantic_html(
    '<html><section></section></html>'))
test("semantic: nav present passes", not v.check_semantic_html(
    '<html><nav></nav></html>'))
test("semantic: none fails", len(v.check_semantic_html(
    '<html><div></div></html>')) > 0)

# ==== check_spa_integration ====
import tempfile

fd, spa_tmp = tempfile.mkstemp(suffix=".html")
os.close(fd)
with open(spa_tmp, "w") as f:
    f.write('<section class="lesson-view" id="lesson-42"><h1>Title</h1></section>')
test("spa: lesson with section passes", not v.check_spa_integration(
    '<section class="lesson-view" id="lesson-42"></section>', spa_tmp))
os.unlink(spa_tmp)

fd, spa_tmp2 = tempfile.mkstemp(suffix=".html")
os.close(fd)
with open(spa_tmp2, "w") as f:
    f.write('<p>No lesson section here</p>')
test("spa: missing id fails", len(v.check_spa_integration('<p>No section</p>', spa_tmp2)) > 0)
os.unlink(spa_tmp2)

# index.html SPA check
test("spa: index.html with sections passes", not v.check_spa_integration(
    '<section class="lesson-view" id="lesson-1"></section>'
    '<section class="lesson-view" id="lesson-2"></section>'
    '</section>', "C:/fake/index.html"))
test("spa: index.html missing sections fails", len(v.check_spa_integration(
    '<p>hello</p>', "C:/fake/index.html")) > 0)
test("spa: index.html duplicate id fails", len(v.check_spa_integration(
    '<section class="lesson-view" id="lesson-1"></section>'
    '<section class="lesson-view" id="lesson-1"></section>'
    '</section>', "C:/fake/index.html")) > 0)
test("spa: KG file skips SPA check", not v.check_spa_integration(
    'const graphData = {nodes:[]};', "C:/fake/kg-mine.html"))

# ==== check_kg_structure ====
test("kg: non-KG file skips", not v.check_kg_structure("<html><p>hello</p></html>", ""))
test("kg: minimal valid KG passes", not v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"第一课","category":"课程","weight":80}],'
    '"links": [{"source":"L1","target":"L1","relation":"自指"}]'
    '};', ""))
test("kg: missing categories fails", len(v.check_kg_structure(
    'const graphData = {'
    '"nodes": [{"id":"L1","name":"第一课","category":"课程","weight":80}],'
    '"links": [{"source":"L1","target":"L1","relation":"自指"}]'
    '};', "")) > 0)
test("kg: empty nodes fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [],'
    '"links": [{"source":"L1","target":"L1","relation":"自指"}]'
    '};', "")) > 0)
test("kg: missing links fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"第一课","category":"课程","weight":80}]'
    '};', "")) > 0)
test("kg: node missing id fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"name":"第一课","category":"课程","weight":80}],'
    '"links": [{"source":"","target":"","relation":"x"}]'
    '};', "")) > 0)
test("kg: node missing name fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","category":"课程","weight":80}],'
    '"links": [{"source":"L1","target":"L1","relation":"x"}]'
    '};', "")) > 0)
test("kg: duplicate node id fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"A","category":"课程","weight":50},{"id":"L1","name":"B","category":"课程","weight":60}],'
    '"links": [{"source":"L1","target":"L1","relation":"x"}]'
    '};', "")) > 0)
test("kg: link to unknown node fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"A","category":"课程","weight":50}],'
    '"links": [{"source":"L1","target":"NOEXIST","relation":"x"}]'
    '};', "")) > 0)
test("kg: invalid category on node fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"A","category":"系统","weight":50}],'
    '"links": [{"source":"L1","target":"L1","relation":"x"}]'
    '};', "")) > 0)
test("kg: weight over 100 fails", len(v.check_kg_structure(
    'const graphData = {'
    '"categories": ["课程"],'
    '"nodes": [{"id":"L1","name":"A","category":"课程","weight":150}],'
    '"links": [{"source":"L1","target":"L1","relation":"x"}]'
    '};', "")) > 0)
test("kg: bilingual format with nameZh/nameEn passes", not v.check_kg_structure(
    'var rawNodes=[{"id":"L1","nameZh":"课","nameEn":"Lesson","category":"课程","weight":50}];'
    'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
    'var catNames={"zh":["课程"],"en":["Course"]};'
    'var graphData={};', ""))
test("kg: bilingual missing nameEn fails", len(v.check_kg_structure(
    'var rawNodes=[{"id":"L1","nameZh":"课","category":"课程","weight":50}];'
    'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
    'var catNames={"zh":["课程"],"en":["Course"]};'
    'var graphData={};', "")) > 0)
test("kg: bilingual missing nameZh fails", len(v.check_kg_structure(
    'var rawNodes=[{"id":"L1","nameEn":"Lesson","category":"课程","weight":50}];'
    'var rawLinks=[{"source":"L1","target":"L1","relation":"x"}];'
    'var catNames={"zh":["课程"],"en":["Course"]};'
    'var graphData={};', "")) > 0)

# ==== check_bilingual ====
test("bilingual: no data-lang skips", not v.check_bilingual("<html><p>no lang attributes</p></html>"))
test("bilingual: zh+en+btn+key passes", not v.check_bilingual(
    '<html data-lang="zh"><span data-lang="zh">中</span><span data-lang="en">EN</span>'
    '<button data-lang-btn></button>key==="l"</html>'))
test("bilingual: missing en fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><button data-lang-btn></button>key==="l"</html>')) > 0)
test("bilingual: missing toggle fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><span data-lang="en">EN</span>key==="l"</html>')) > 0)
test("bilingual: missing l key fails", len(v.check_bilingual(
    '<html><span data-lang="zh">中</span><span data-lang="en">EN</span><button data-lang-btn></button></html>')) > 0)

# ==== check_lib_deps ====
test("lib deps: no echarts/three.js passes", not v.check_lib_deps(
    '<html><p>hello</p></html>', '.'))
test("lib deps: echarts CDN passes", not v.check_lib_deps(
    '<html><script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>echarts.init()</html>', '.'))
test("lib deps: three.js CDN passes", not v.check_lib_deps(
    '<html><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>new THREE.Scene()</html>', '.'))
test("lib deps: echarts local passes", not v.check_lib_deps(
    '<html>echarts.init()</html>', '.'))
test("lib deps: three.js local passes", not v.check_lib_deps(
    '<html>new THREE.Scene()</html>', '.'))
test("lib deps: echarts no lib fails", len(v.check_lib_deps(
    '<html>echarts.init()</html>', 'C:\\nonexistent')) > 0)
test("lib deps: three.js no lib fails", len(v.check_lib_deps(
    '<html>new THREE.Scene()</html>', 'C:\\nonexistent')) > 0)
test("lib deps: d3.js CDN passes", not v.check_lib_deps(
    '<html><script src="https://d3js.org/d3.v7.min.js"></script>d3.forceSimulation()</html>', '.'))
test("lib deps: d3.js local passes", not v.check_lib_deps(
    '<html>d3.select("body")</html>', '.'))
test("lib deps: d3.js no lib fails", len(v.check_lib_deps(
    '<html>d3.forceSimulation()</html>', 'C:\\nonexistent')) > 0)
test("lib deps: three.js r185 importmap passes", not v.check_lib_deps(
    '<html>cdn.jsdelivr.net/npm/three@0.185.0/ new THREE.Scene()</html>', '.'))
test("lib deps: three.js r185 importmap as CDN passes", not v.check_lib_deps(
    '<html>cdn.jsdelivr.net/npm/three@0.185.0/ new THREE.Scene()</html>', 'C:\\nonexistent'))
test("lib deps: echarts GL passes", not v.check_lib_deps(
    '<html>type: "bar3D" scatter3D map3D globe</html>', '.'))
test("lib deps: echarts GL no lib fails", len(v.check_lib_deps(
    '<html>type: "bar3D"</html>', 'C:\\nonexistent')) > 0)



# ==== magicui CSS effects ====
test("data-anim: blur is valid", not v.check_data_anim_syntax('<html><div data-anim="blur"></div></html>'))
test("data-anim: fade-up is still valid", not v.check_data_anim_syntax('<html><div data-anim="fade-up"></div></html>'))
test("data-anim: unknown value fails", len(v.check_data_anim_syntax('<html><div data-anim="foobar"></div></html>')) > 0)
test("magicui: shiny-text class detected", not v.check_data_anim_syntax('<html><span class="shiny-text">hi</span></html>'))

# ==== bilingual table-cell check ====
test("bilingual: td with data-lang passes", not v.check_bilingual('<html><td data-lang="zh">中</td><td data-lang="en">EN</td><button data-lang-btn></button>key==="l"</html>'))
test("bilingual: th with data-lang passes", not v.check_bilingual('<html><th data-lang="zh">中</th><th data-lang="en">EN</th><button data-lang-btn></button>key==="l"</html>'))
test("anim: blur is valid in list", not v.check_data_anim_syntax('<html><div data-anim="blur"></div><div data-anim="fade-up"></div></html>'))

# ==== Results ====
print(f"\n{PASS} passed, {FAIL} failed")
if FAIL > 0:
    sys.exit(1)
