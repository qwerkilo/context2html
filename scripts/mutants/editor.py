"""Mutants for the editor area."""

MUTANTS = [('preview: title claimed as displayed for every target',
  'runtime/editor-core.js',
  '    var titleUse = TITLE_CONSUMPTION[descriptor.id] || false;',
  '    var titleUse = true;',
  'scripts/test_editor_core.py'),
 ('editor: swap skips the on-demand library load',
  'runtime/editor-core.js',
  '    if (!library || settings.hasLibrary(library)) {',
  '    if (true) {',
  'scripts/test_editor_library.py')]
