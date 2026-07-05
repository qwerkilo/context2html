"""Component Registry — parse and query visual components by metadata."""

import os
import yaml
import glob

from context2html.markdown_utils import parse_front_matter, extract_code_block, extract_js_from_md


COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'components')


class ComponentMeta:
    def __init__(self, id, name, dependencies=None, compat_types=None, degrade_to=None, requires_3d=False):
        self.id = id
        self.name = name
        self.dependencies = dependencies or []
        self.compat_types = compat_types or ['report']
        self.degrade_to = degrade_to
        self.requires_3d = requires_3d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id', 0),
            name=d.get('name', ''),
            dependencies=d.get('dependencies', []),
            compat_types=d.get('compat_types', ['report']),
            degrade_to=d.get('degrade_to'),
            requires_3d=d.get('requires_3d', False),
        )


class Component:
    def __init__(self, metadata, html, css, js):
        self.metadata = metadata
        self.html = html or ''
        self.css = css or ''
        self.js = js or ''

    @property
    def id(self):
        return self.metadata.id


class ComponentRegistry:
    def __init__(self, components_dir=None):
        self._dir = components_dir or COMPONENTS_DIR
        self._cache = None

    def _load_all(self):
        if self._cache is not None:
            return self._cache
        self._cache = []
        files = sorted(glob.glob(os.path.join(self._dir, '*.md')))
        for f in files:
            with open(f, 'r', encoding='utf-8') as fh:
                content = fh.read()
            meta, body = parse_front_matter(content)
            if not meta:
                continue
            html = extract_code_block(body, 'html') or ''
            css = extract_code_block(body, 'css') or ''
            js = extract_js_from_md(body)
            metadata = ComponentMeta.from_dict(meta)
            self._cache.append(Component(metadata, html, css, js))
        return self._cache

    def list_components(self, content_type=None):
        all_components = self._load_all()
        if content_type is None:
            return all_components
        return [c for c in all_components if content_type in c.metadata.compat_types]

    def get_component(self, id):
        all_components = self._load_all()
        for c in all_components:
            if c.metadata.id == id:
                return c
        return None

    def resolve_dependencies(self, component_ids):
        result = []
        seen = set()
        for cid in component_ids:
            comp = self.get_component(cid)
            if comp:
                for dep in comp.metadata.dependencies:
                    if dep not in seen:
                        seen.add(dep)
                        result.append(dep)
        return result
