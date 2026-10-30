"""Mutants for the optional item-value guards (Python and browser twins)."""

MUTANTS = [
    ('optional value: item-value guard disabled',
     'context2html/content_model.py',
     "    for index, item in enumerate(model.items):\n"
     "        if item.value is None:\n"
     "            raise ContentModelError(f'items[{index}].value', 'missing field')",
     "    for index, item in enumerate(model.items):\n"
     "        if False:\n"
     "            raise ContentModelError(f'items[{index}].value', 'missing field')",
     'scripts/test_structure.py'),
    ('optional value: numbers guard disabled',
     'context2html/content_model.py',
     '    if model.series:\n'
     '        return\n'
     '    require_item_values(model)',
     '    if model.series:\n'
     '        return\n'
     '    return',
     'scripts/test_chart_slots.py'),
    ('optional value: browser item-value guard disabled',
     'runtime/slots.js',
     '      if (model.items[index].value === undefined) {',
     '      if (false) {',
     'scripts/test_js_parity.py'),
    ('optional value: browser numbers guard disabled',
     'runtime/slots.js',
     '  function requireNumbers(model) {\n'
     '    if (model.series.length) return;\n'
     '    requireItemValues(model);\n'
     '  }',
     '  function requireNumbers(model) {\n'
     '    if (model.series.length) return;\n'
     '    return;\n'
     '  }',
     'scripts/test_js_parity.py'),
]
