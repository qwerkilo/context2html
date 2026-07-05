"""Integration tests for validate-report.py entry point."""
import sys, os, importlib.util

spec = importlib.util.spec_from_file_location(
    "vr_main", os.path.join(os.path.dirname(__file__), "validate-report.py")
)
vr_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vr_main)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')


class TestRunAllIntegration:
    def test_demo_report_passes(self):
        """The demo report should pass all checks."""
        path = os.path.join(EXAMPLES_DIR, '0001-demo-report.html')
        assert os.path.exists(path)
        vr_main.run_all(path)

    def test_nonexistent_file_exits(self):
        """Non-existent file should sys.exit(1)."""
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), 'validate-report.py'),
             '/nonexistent/path.html'],
            capture_output=True, text=True
        )
        assert result.returncode == 1
        assert 'File not found' in result.stderr or 'File not found' in result.stdout

    def _write_with_theme_css(self, html, tmp_dir):
        """Write html to a temp file and create minimal theme CSS alongside it."""
        html_path = os.path.join(tmp_dir, 'report.html')
        theme_dir = os.path.join(tmp_dir, 'theme')
        os.makedirs(theme_dir, exist_ok=True)
        with open(os.path.join(theme_dir, 'report-themes.css'), 'w', encoding='utf-8') as f:
            f.write('/* stub */')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return html_path

    def test_starter_html_as_article(self):
        """starter.html with data-content-type='article' should pass article checks."""
        import tempfile, shutil
        path = os.path.join(BASE_DIR, 'templates', 'starter.html')
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        modified = html.replace('data-content-type="report"', 'data-content-type="article"')
        tmp_dir = tempfile.mkdtemp()
        try:
            html_path = self._write_with_theme_css(modified, tmp_dir)
            vr_main.run_all(html_path)
        finally:
            shutil.rmtree(tmp_dir)

    def test_starter_html_as_tutorial(self):
        """starter.html with data-content-type='tutorial' should pass tutorial checks."""
        import tempfile, shutil
        path = os.path.join(BASE_DIR, 'templates', 'starter.html')
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        modified = html.replace(
            'data-content-type="report"',
            'data-content-type="tutorial"'
        )
        # Add a step element so tutorial check passes
        modified = modified.replace(
            '</nav>',
            '</nav><div class="si-step active"><span class="si-num">1</span>Step</div>'
        )
        tmp_dir = tempfile.mkdtemp()
        try:
            html_path = self._write_with_theme_css(modified, tmp_dir)
            vr_main.run_all(html_path)
        finally:
            shutil.rmtree(tmp_dir)

    def test_relative_links_passes(self):
        """A simple report with only relative links should pass."""
        import tempfile, shutil
        html = """<!DOCTYPE html><html data-content-type="report"><head>
<link href="theme/report-themes.css" rel="stylesheet">
<style>body{overflow-wrap:break-word}:focus-visible{outline:2px solid red}body{font-variant-numeric:tabular-nums}</style>
</head><body>
<article class="cover-page"><h1 data-lang="zh">标题</h1><h1 data-lang="en">Title</h1></article>
<section class="exec-summary"><h2 data-lang="zh">摘要</h2><h2 data-lang="en">Summary</h2></section>
<section class="report-chapter" id="ch1"><h2 data-lang="zh">章节一</h2><h2 data-lang="en">Ch1</h2></section>
<aside class="conclusion-page"><h2 data-lang="zh">结论</h2><h2 data-lang="en">Conclusion</h2></aside>
<footer class="report-footer"><p data-lang="zh">页脚</p><p data-lang="en">Footer</p></footer>
<button data-lang-btn></button>
<script>
document.addEventListener('keydown',function(e){if(e.key==='l'){}})
</script>
</body></html>"""
        tmp_dir = tempfile.mkdtemp()
        try:
            html_path = self._write_with_theme_css(html, tmp_dir)
            vr_main.run_all(html_path)
        finally:
            shutil.rmtree(tmp_dir)
