#!/usr/bin/env node
/* Run the save pipeline the way a report does: no CommonJS, no require.
 *
 * The report inlines runtime/editor-core.js as a plain <script>, so the file
 * must resolve the slot runtime through globalThis.SlotRuntime.  Loading it in
 * a VM context with `module` undefined reproduces that branch, which is the
 * one the browser actually takes.
 *
 * Usage: echo '{"op":"savedHtml","args":["<html>…"]}' | node save-browser-runner.js
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RUNTIME_DIR = path.join(__dirname, '..', '..', 'runtime');

function loadEditorCore() {
  const sandbox = {};
  sandbox.globalThis = sandbox;
  sandbox.SlotRuntime = require(path.join(RUNTIME_DIR, 'slots.js'));
  vm.createContext(sandbox);
  const source = fs.readFileSync(path.join(RUNTIME_DIR, 'editor-core.js'), 'utf8');
  vm.runInContext(source, sandbox, { filename: 'editor-core.js' });
  return sandbox.SlotEditorCore;
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let request;
  try {
    request = JSON.parse(input);
  } catch (error) {
    process.stderr.write('invalid request JSON: ' + error.message + '\n');
    process.exit(2);
  }

  let result;
  try {
    const core = loadEditorCore();
    const fn = core[request.op];
    if (typeof fn !== 'function') {
      process.stderr.write('unknown browser save function: ' + request.op + '\n');
      process.exit(2);
    }
    result = fn.apply(null, request.args || []);
  } catch (error) {
    process.stderr.write(error.name + ': ' + error.message + '\n');
    process.exit(1);
  }
  process.stdout.write(JSON.stringify(result));
});
