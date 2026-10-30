#!/usr/bin/env node
/* Render one golden fixture through the browser runtime.
 *
 * Usage: node scripts/js/render-fixture.js <componentId> <modelPath>
 *
 * Writes the slot fragment (markup, newline, data block, newline) to stdout
 * with no extra newline, so a Python caller can compare it byte for byte.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const runtimePath = path.join(__dirname, '..', '..', 'runtime', 'slots.js');
const runtime = require(runtimePath);

const componentId = Number(process.argv[2]);
const modelPath = process.argv[3];

if (!Number.isInteger(componentId) || !modelPath) {
  process.stderr.write('usage: node scripts/js/render-fixture.js <componentId> <modelPath>\n');
  process.exit(2);
}

const text = fs.readFileSync(modelPath, 'utf8');
const model = runtime.parseModel(text);
const slot = runtime.renderSlot(componentId, model);
process.stdout.write(slot.fragment);
