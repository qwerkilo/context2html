"""Mutants for the slots area."""

MUTANTS = [('bar chart: empty-state guard disabled',
  'context2html/slots.py',
  '    entries, field = _item_entries(model)\n'
  '    if entries is None:\n'
  '        return _section(4, slot_id, model, _empty_state())',
  '    entries, field = _item_entries(model)\n'
  '    if False:\n'
  '        return _section(4, slot_id, model, _empty_state())',
  'scripts/test_chart_slots.py'),
 ('runtime: script-closer escaping disabled',
  'runtime/slots.js',
  "      .split('</').join('<\\\\/')",
  "      .split('</').join('</')",
  'scripts/test_js_parity.py'),
 ('charts: bilingual pair falls back to Chinese in both slots',
  'context2html/slots.py',
  'f\'<span data-lang="en">{_escape(en or zh)}</span>\'',
  'f\'<span data-lang="en">{_escape(zh)}</span>\'',
  'scripts/test_chart_slots.py')]
