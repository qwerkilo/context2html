"""Sync base-styles.css back into template HTML <style> blocks."""
import re
import os


def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSS_PATH = os.path.join(BASE_DIR, 'templates', 'base-styles.css')
    TEMPLATES = [
        os.path.join(BASE_DIR, 'templates', 'starter.html'),
        os.path.join(BASE_DIR, 'templates', 'report-starter.html'),
    ]

    with open(CSS_PATH, 'r', encoding='utf-8') as f:
        css_content = f.read()

    for tpl_path in TEMPLATES:
        with open(tpl_path, 'r', encoding='utf-8') as f:
            html = f.read()

        def replace_style(m):
            tag_open = m.group(1)
            inner = m.group(2)
            lines = inner.split('\n')
            kept_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('/* =====') and ('同步自' in stripped or 'sync' in stripped.lower() or '同步' in stripped):
                    kept_lines.append(line)
                elif stripped == '':
                    kept_lines.append(line)
                else:
                    break
            new_inner = '\n'.join(kept_lines)
            if new_inner and not new_inner.endswith('\n'):
                new_inner += '\n'
            new_inner += css_content
            return f'{tag_open}\n{new_inner}\n</style>'

        new_html = re.sub(
            r'(<style[^>]*>)\s*\n?(.*?)\n?</style>',
            replace_style,
            html,
            count=1,
            flags=re.DOTALL,
        )

        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(new_html)

        print(f"  Synced: {os.path.basename(tpl_path)}")

    print("Done. Both templates synced from base-styles.css")


if __name__ == '__main__':
    main()
