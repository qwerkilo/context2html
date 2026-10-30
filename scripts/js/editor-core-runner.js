#!/usr/bin/env node
/* Run one pure editor-core function for the Python test suite.
 *
 * Usage: echo '{"op":"slotShape","args":[model]}' | node editor-core-runner.js
 *
 * The request is JSON on stdin; the function result is JSON on stdout.  Keeping
 * this runner dumb means every assertion lives in the Python tests, next to the
 * rest of the suite.
 */
'use strict';

const path = require('path');

const core = require(path.join(__dirname, '..', '..', 'runtime', 'editor-core.js'));

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
  const fn = core[request.op];
  if (fn === undefined) {
    process.stderr.write('unknown editor-core function: ' + request.op + '\n');
    process.exit(2);
  }
  let result;
  try {
    result = typeof fn === 'function' ? fn.apply(null, request.args || []) : fn;
  } catch (error) {
    process.stderr.write(error.name + ': ' + error.message + '\n');
    process.exit(1);
  }
  process.stdout.write(JSON.stringify(result));
});
