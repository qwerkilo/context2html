#!/usr/bin/env node
/* Drive one editor-core swap for the Python suite.
 *
 * Request JSON on stdin:
 *   {componentId, model, slotId, hasLibrary: bool, loadLibrary: 'ok'|'fail'}
 * Result JSON on stdout: {result, events, committed}
 *
 * `render` is the real SlotRuntime renderer, so `committed` is the markup a
 * report would show.  The loader stands in for the browser's CDN-first
 * `__loadLib`, which cannot run without a DOM.
 */
'use strict';

const path = require('path');

const core = require(path.join(__dirname, '..', '..', 'runtime', 'editor-core.js'));
const runtime = require(path.join(__dirname, '..', '..', 'runtime', 'slots.js'));

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

  const events = [];
  let committed = null;
  const swap = core.swapSlot({
    componentId: request.componentId,
    model: request.model,
    slotId: request.slotId,
    hasLibrary(library) {
      events.push('hasLibrary:' + library.name);
      return Boolean(request.hasLibrary);
    },
    loadLibrary(library) {
      events.push('loadLibrary:' + library.name);
      if (request.loadLibrary === 'fail') {
        return Promise.reject(new Error('network down'));
      }
      return Promise.resolve();
    },
    render(componentId, model, slotId) {
      events.push('render:' + componentId);
      return runtime.renderSlot(componentId, model, slotId);
    },
    commit(rendered) {
      events.push('commit');
      committed = rendered;
    }
  });

  Promise.resolve(swap).then(
    (result) => process.stdout.write(JSON.stringify({ result, events, committed })),
    (error) => {
      process.stderr.write((error && error.stack) || String(error));
      process.exit(1);
    });
});
