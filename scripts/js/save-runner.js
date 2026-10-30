#!/usr/bin/env node
/* Drive the save pipeline for the Python test suite.
 *
 * Usage: echo '{"op":"savedHtml","args":["<html>…"]}' | node save-runner.js
 *
 * Every op except `swap` is a pure function on runtime/editor-core.js, so the
 * assertions stay in Python next to the rest of the suite.  `swap` is test
 * scaffolding, not production code: it reproduces the DOM effect of
 * runtime/editor.js's replaceSlot — the slot's markup (and any init scripts
 * between it and its data block) is replaced, the data block is untouched.
 * That is the state a browser would serialize after a swap, which is what the
 * save pipeline receives in the browser.
 */
'use strict';

const path = require('path');

const core = require(path.join(__dirname, '..', '..', 'runtime', 'editor-core.js'));
const runtime = require(path.join(__dirname, '..', '..', 'runtime', 'slots.js'));

function applySwap(html, slotId, componentId) {
  const start = html.indexOf('<section class="ic-slot" data-slot="' + slotId + '"');
  if (start < 0) throw new Error('slot not found: ' + slotId);

  const blockTag = '<script type="application/json" data-slot="' + slotId + '">';
  const blockStart = html.indexOf(blockTag, start);
  if (blockStart < 0) throw new Error('data block not found: ' + slotId);

  const bodyStart = blockStart + blockTag.length;
  const bodyEnd = html.indexOf('</script>', bodyStart);
  if (bodyEnd < 0) throw new Error('unterminated data block: ' + slotId);

  const modelText = html.slice(bodyStart, bodyEnd);
  const rendered = runtime.renderSlot(componentId, modelText, slotId);
  return html.slice(0, start) + rendered.markup + '\n' + html.slice(blockStart);
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

  const args = request.args || [];
  let result;
  try {
    if (request.op === 'swap') {
      result = applySwap.apply(null, args);
    } else if (typeof core[request.op] === 'function') {
      result = core[request.op].apply(null, args);
    } else {
      process.stderr.write('unknown save function: ' + request.op + '\n');
      process.exit(2);
    }
  } catch (error) {
    process.stderr.write(error.name + ': ' + error.message + '\n');
    process.exit(1);
  }
  process.stdout.write(JSON.stringify(result));
});
