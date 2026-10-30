"""Documented check counts must equal what the validator actually runs.

Every doc that states the numbers must use one of the canonical phrasings:
  - Chinese: "<N> 项硬性检查 + <M> 项人类化警告"
  - English: "<N> hard checks + <M> humanization warnings"
so this test can parse them and compare against build_checks().
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

import importlib.util

_ROOT = os.path.join(os.path.dirname(__file__), '..')
_spec = importlib.util.spec_from_file_location(
    'validate_report', os.path.join(_ROOT, 'scripts', 'validate-report.py'))
vr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vr)

DEMO = os.path.join(_ROOT, 'examples', '0001-demo-report.html')

_ZH = re.compile(r'(\d+)\s*项硬性检查\s*\+\s*(\d+)\s*项人类化警告')
_EN = re.compile(r'(\d+)\s*hard checks\s*\+\s*(\d+)\s*humanization warnings')

DOCS = ['SKILL.md', 'AGENTS.md', 'GLOSSARY.md', 'README.md']


def _actual():
    with open(DEMO, 'r', encoding='utf-8') as fh:
        html = fh.read()
    _, checks, warnings = vr.build_checks(html, os.path.dirname(DEMO))
    return len(checks), len(warnings)


def test_actual_counts_are_stable():
    hard, warn = _actual()
    assert hard == 22, f'report type has {hard} hard checks (update docs + this test)'
    assert warn == 5, f'{warn} humanization warnings (update docs + this test)'


def test_docs_state_correct_counts():
    hard, warn = _actual()
    failures = []
    for name in DOCS:
        path = os.path.join(_ROOT, name)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        found = _ZH.findall(text) + _EN.findall(text)
        for h, w in found:
            if (int(h), int(w)) != (hard, warn):
                failures.append(
                    f'{name}: states {h} hard + {w} warnings, actual is {hard} + {warn}')
    assert not failures, '\n'.join(failures)
