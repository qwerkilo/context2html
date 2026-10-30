"""Guard the glossary against self-contradiction.

An entry's `_Avoid_` list names the words this project rejects for a concept.
If one of those rejected words is also a defined English name elsewhere in the
glossary, the document is telling a reader both "call it X" and "never call it
X" — which is how `editable report` ended up as a banned term while the public
API parameter was called `editable`.

The check is deliberately narrow: it compares defined English names against
avoided terms, so prose that merely mentions a word is not flagged.
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY = os.path.join(BASE_DIR, 'GLOSSARY.md')

_ENTRY = re.compile(r'^\*\*(?P<label>[^*]+)\*\*:\s*$')
_ENGLISH = re.compile(r'\(([^)]+)\)')
_AVOID = re.compile(r'^_Avoid_:\s*(?P<terms>.+)$')


def parse_glossary(text):
    """Return (defined_names, avoided_terms) as lowercase sets."""
    defined = set()
    avoided = set()
    current_defined = None
    for line in text.split('\n'):
        entry = _ENTRY.match(line)
        if entry:
            label = entry.group('label')
            english = _ENGLISH.search(label)
            current_defined = (english.group(1) if english else label).strip().lower()
            defined.add(current_defined)
            continue
        avoid = _AVOID.match(line)
        if avoid and current_defined:
            for term in avoid.group('terms').split(','):
                cleaned = term.strip().strip('`').strip()
                if cleaned:
                    avoided.add(cleaned.lower())
    return defined, avoided


class TestGlossaryConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(GLOSSARY, 'r', encoding='utf-8') as fh:
            cls.defined, cls.avoided = parse_glossary(fh.read())

    def test_glossary_is_not_empty(self):
        self.assertGreater(len(self.defined), 10)
        self.assertGreater(len(self.avoided), 10)

    def test_no_avoided_term_is_also_a_defined_name(self):
        collisions = sorted(self.defined & self.avoided)
        self.assertEqual(
            collisions, [],
            'these words are defined as a term and also listed as a word to '
            f'avoid: {collisions}')

    def test_parser_sees_the_known_terms(self):
        """A parser that silently matched nothing would pass the check above."""
        self.assertIn('visual report', self.defined)
        self.assertIn('html page', self.avoided)


if __name__ == '__main__':
    unittest.main()
