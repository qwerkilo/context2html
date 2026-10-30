"""Mutants for the trust-boundary and numeric-boundary guards."""

MUTANTS = [('echarts: inline option JSON stops escaping </script>',
  'context2html/slots.py',
  '    option_js = _script_safe(option_js)',
  '    option_js = option_js',
  'scripts/test_trust_boundary.py'),
 ('heatmap: equal min/max divides by zero instead of pinning to 2',
  'context2html/slots.py',
  '    if highest <= lowest:\n        return 2',
  '    if highest < lowest:\n        return 2',
  'scripts/test_chart_slots.py'),
 ('progress: exactly 100 counts as still in progress',
  'context2html/slots.py',
  "    if value >= 100:\n        return 'done'",
  "    if value > 100:\n        return 'done'",
  'scripts/test_chart_slots.py')]
