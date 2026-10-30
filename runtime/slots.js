/* Slot runtime — the browser-side renderer for the 14 swappable components.
 *
 * Every render function is pure: a content model in, markup plus its JSON
 * data block out.  Nothing here reads the DOM, `window`, or any other global,
 * so the whole file runs under `node` and can also be inlined into a report.
 *
 * Public API (browser: `globalThis.SlotRuntime`, node: `require`):
 *   renderSlot(componentId, model, slotId?) -> {slotId, componentId, markup,
 *                                                dataBlock, fragment}
 *     `model` is an object or the raw JSON text of a data block.
 *   renderMarkup(componentId, model, slotId?)
 *   parseModel(text)     parse JSON while preserving int/float number kinds
 *   canonicalJson(model) canonical JSON exactly as Python's slots.py emits it
 *   normalizeContentModel(model)
 *   componentIds
 *   ContentModelError
 *
 * Canonical JSON rules (must match context2html/slots.py):
 *   - keys sorted by Unicode code point, compact separators for data blocks;
 *   - floats use Python `repr` formatting (3.0 keeps its `.0`, 1e-7 becomes
 *     `1e-07`, exponents are at least two digits);
 *   - `</` becomes `<\/`, U+2028 and U+2029 become their `\uXXXX` escapes;
 *   - the slot id is the first 8 hex characters of the SHA-1 of the UTF-8
 *     canonical JSON.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.SlotRuntime = api;
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var NUMBER_META = typeof Symbol === 'function'
    ? Symbol('slotNumberMeta')
    : '__slotNumberMeta__';

  var SLOT_ID = /^[A-Za-z0-9][A-Za-z0-9._:-]*$/;
  var HEX_COLOR = /^#[0-9A-Fa-f]{3,8}$/;
  var STRUCTURE_COLOR = /^(?:#[0-9A-Fa-f]{3,8}|var\(--[A-Za-z0-9_-]+\))$/;
  var COLOR_VARS = ['--accent', '--chart-3', '--chart-4',
    '--success', '--warning', '--error'];
  var ACCENT_TOKENS = {
    accent: true, success: true, warning: true, error: true,
    'chart-1': true, 'chart-2': true, 'chart-3': true, 'chart-4': true
  };
  var TAG_PALETTE = ['blue', 'red', 'green', 'orange', 'purple'];
  var CALLOUT_TYPES = {
    info: ['info', '💡'],
    warning: ['warning', '⚠️'],
    error: ['error', '❌'],
    success: ['success', '✅']
  };

  /* ------------------------------------------------------------------ *
   * Errors
   * ------------------------------------------------------------------ */

  function ContentModelError(field, message) {
    this.name = 'ContentModelError';
    this.field = field;
    this.message = field + ': ' + message;
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ContentModelError);
    }
  }
  ContentModelError.prototype = Object.create(Error.prototype);
  ContentModelError.prototype.constructor = ContentModelError;

  /* ------------------------------------------------------------------ *
   * Number formatting
   * ------------------------------------------------------------------ */

  function pythonFloatRepr(value) {
    if (Number.isNaN(value)) return 'NaN';
    if (value === Infinity) return 'Infinity';
    if (value === -Infinity) return '-Infinity';
    if (value === 0) return Object.is(value, -0) ? '-0.0' : '0.0';

    var sign = value < 0 ? '-' : '';
    var abs = Math.abs(value);
    var exponential = abs.toExponential();
    var parts = exponential.split('e');
    var mantissa = parts[0];
    var exponent = parseInt(parts[1], 10);
    var digits = mantissa.replace('.', '');
    var text;

    if (exponent >= -4 && exponent < 16) {
      if (exponent >= 0) {
        if (digits.length <= exponent + 1) {
          text = digits + repeat('0', exponent + 1 - digits.length) + '.0';
        } else {
          text = digits.slice(0, exponent + 1) + '.' + digits.slice(exponent + 1);
        }
      } else {
        text = '0.' + repeat('0', -exponent - 1) + digits;
      }
    } else {
      var head = digits.length > 1 ? digits.charAt(0) + '.' + digits.slice(1) : digits;
      var expSign = exponent < 0 ? '-' : '+';
      var expDigits = String(Math.abs(exponent));
      while (expDigits.length < 2) expDigits = '0' + expDigits;
      text = head + 'e' + expSign + expDigits;
    }
    return sign + text;
  }

  function repeat(text, count) {
    var out = '';
    for (var i = 0; i < count; i += 1) out += text;
    return out;
  }

  function roundHalfEven(value) {
    var floor = Math.floor(value);
    var difference = value - floor;
    if (difference > 0.5) return floor + 1;
    if (difference < 0.5) return floor;
    return floor % 2 === 0 ? floor : floor + 1;
  }

  function roundOneDecimal(value) {
    return roundHalfEven(value * 10) / 10;
  }

  function formatNumber(value) {
    if (typeof value === 'number') {
      if (Number.isInteger(value)) return String(value);
      return pythonFloatRepr(value);
    }
    return String(value);
  }

  function formatPercent(value) {
    if (Number.isInteger(value)) return String(value);
    return pythonFloatRepr(value);
  }

  function percent(value, maximum) {
    if (maximum <= 0) return 0;
    return roundOneDecimal(value / maximum * 100);
  }

  function intensity(value, lowest, highest) {
    if (highest <= lowest) return 2;
    return roundHalfEven((value - lowest) / (highest - lowest) * 4);
  }

  /* ------------------------------------------------------------------ *
   * Escaping
   * ------------------------------------------------------------------ */

  function escapeSlot(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeStructure(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  function scriptSafe(text) {
    return text
      .split('</').join('<\\/')
      .split('\u2028').join('\\u2028')
      .split('\u2029').join('\\u2029');
  }

  /* ------------------------------------------------------------------ *
   * Canonical JSON
   * ------------------------------------------------------------------ */

  function quoteJsonString(text) {
    var out = '"';
    for (var i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      var character = text.charAt(i);
      if (character === '"') out += '\\"';
      else if (character === '\\') out += '\\\\';
      else if (character === '\b') out += '\\b';
      else if (character === '\f') out += '\\f';
      else if (character === '\n') out += '\\n';
      else if (character === '\r') out += '\\r';
      else if (character === '\t') out += '\\t';
      else if (code < 0x20) {
        var hex = code.toString(16);
        while (hex.length < 4) hex = '0' + hex;
        out += '\\u' + hex;
      } else {
        out += character;
      }
    }
    return out + '"';
  }

  function compareCodePoints(left, right) {
    var i = 0;
    var j = 0;
    while (i < left.length && j < right.length) {
      var a = left.codePointAt(i);
      var b = right.codePointAt(j);
      if (a !== b) return a - b;
      i += a > 0xFFFF ? 2 : 1;
      j += b > 0xFFFF ? 2 : 1;
    }
    return (left.length - i) - (right.length - j);
  }

  function jsonNumber(value, kind) {
    if (kind === 'float') return pythonFloatRepr(value);
    if (kind === 'int') return String(value);
    if (!Number.isInteger(value)) return pythonFloatRepr(value);
    return String(value);
  }

  function stringifyJson(value, options) {
    var settings = options || {};
    var meta = settings.meta || null;
    var indent = settings.indent === undefined ? null : settings.indent;
    var sortKeys = Boolean(settings.sortKeys);

    function encode(current, parent, key, depth) {
      if (current === null) return 'null';
      var type = typeof current;
      if (type === 'string') return quoteJsonString(current);
      if (type === 'number') {
        var kind;
        if (parent && meta) {
          var kinds = meta.get(parent);
          if (kinds) kind = kinds.get(key);
        }
        return jsonNumber(current, kind);
      }
      if (type === 'boolean') return current ? 'true' : 'false';
      if (Array.isArray(current)) {
        if (current.length === 0) return '[]';
        var items = [];
        for (var index = 0; index < current.length; index += 1) {
          items.push(encode(current[index], current, index, depth + 1));
        }
        if (indent === null) return '[' + items.join(',') + ']';
        var itemPad = repeat(' ', indent * (depth + 1));
        var itemClose = repeat(' ', indent * depth);
        return '[\n' + itemPad + items.join(',\n' + itemPad) + '\n' + itemClose + ']';
      }
      if (type === 'object') {
        var keys = Object.keys(current);
        if (sortKeys) keys.sort(compareCodePoints);
        if (keys.length === 0) return '{}';
        var parts = [];
        for (var k = 0; k < keys.length; k += 1) {
          var name = keys[k];
          parts.push(
            quoteJsonString(name) + (indent === null ? ':' : ': ')
            + encode(current[name], current, name, depth + 1));
        }
        if (indent === null) return '{' + parts.join(',') + '}';
        var keyPad = repeat(' ', indent * (depth + 1));
        var objectClose = repeat(' ', indent * depth);
        return '{\n' + keyPad + parts.join(',\n' + keyPad) + '\n' + objectClose + '}';
      }
      return 'null';
    }

    return encode(value, null, null, 0);
  }

  /* ------------------------------------------------------------------ *
   * JSON parsing that remembers int vs float lexemes
   * ------------------------------------------------------------------ */

  function parseModel(text) {
    var position = 0;
    var meta = new WeakMap();

    function fail(message) {
      throw new SyntaxError(message + ' at position ' + position);
    }

    function skipWhitespace() {
      while (position < text.length && /\s/.test(text.charAt(position))) {
        position += 1;
      }
    }

    function attach(target, kinds) {
      if (kinds.size) meta.set(target, kinds);
    }

    function parseString() {
      if (text.charAt(position) !== '"') fail('expected a string');
      position += 1;
      var out = '';
      while (position < text.length) {
        var character = text.charAt(position);
        position += 1;
        if (character === '"') return out;
        if (character === '\\') {
          var escape = text.charAt(position);
          position += 1;
          if (escape === '"') out += '"';
          else if (escape === '\\') out += '\\';
          else if (escape === '/') out += '/';
          else if (escape === 'b') out += '\b';
          else if (escape === 'f') out += '\f';
          else if (escape === 'n') out += '\n';
          else if (escape === 'r') out += '\r';
          else if (escape === 't') out += '\t';
          else if (escape === 'u') {
            var hex = text.slice(position, position + 4);
            if (!/^[0-9A-Fa-f]{4}$/.test(hex)) fail('invalid unicode escape');
            out += String.fromCharCode(parseInt(hex, 16));
            position += 4;
          } else {
            fail('invalid escape');
          }
        } else {
          out += character;
        }
      }
      return fail('unterminated string');
    }

    function parseNumber() {
      var match = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/.exec(
        text.slice(position));
      if (!match) fail('invalid number');
      var raw = match[0];
      position += raw.length;
      var kind = (raw.indexOf('.') >= 0 || /[eE]/.test(raw)) ? 'float' : 'int';
      return { value: Number(raw), kind: kind };
    }

    function parseObject() {
      var object = {};
      var kinds = new Map();
      position += 1;
      skipWhitespace();
      if (text.charAt(position) === '}') {
        position += 1;
        attach(object, kinds);
        return object;
      }
      while (true) {
        skipWhitespace();
        var key = parseString();
        skipWhitespace();
        if (text.charAt(position) !== ':') fail('expected ":"');
        position += 1;
        var child = parseValue();
        object[key] = child.value;
        if (child.kind) kinds.set(key, child.kind);
        skipWhitespace();
        var next = text.charAt(position);
        position += 1;
        if (next === '}') break;
        if (next !== ',') fail('expected "," or "}"');
      }
      attach(object, kinds);
      return object;
    }

    function parseArray() {
      var array = [];
      var kinds = new Map();
      position += 1;
      skipWhitespace();
      if (text.charAt(position) === ']') {
        position += 1;
        attach(array, kinds);
        return array;
      }
      while (true) {
        var child = parseValue();
        array.push(child.value);
        if (child.kind) kinds.set(array.length - 1, child.kind);
        skipWhitespace();
        var next = text.charAt(position);
        position += 1;
        if (next === ']') break;
        if (next !== ',') fail('expected "," or "]"');
      }
      attach(array, kinds);
      return array;
    }

    function parseValue() {
      skipWhitespace();
      var character = text.charAt(position);
      if (character === '{') return { value: parseObject(), kind: null };
      if (character === '[') return { value: parseArray(), kind: null };
      if (character === '"') return { value: parseString(), kind: null };
      if (text.startsWith('true', position)) {
        position += 4;
        return { value: true, kind: null };
      }
      if (text.startsWith('false', position)) {
        position += 5;
        return { value: false, kind: null };
      }
      if (text.startsWith('null', position)) {
        position += 4;
        return { value: null, kind: null };
      }
      if (character === '-' || (character >= '0' && character <= '9')) {
        return parseNumber();
      }
      return fail('unexpected token');
    }

    var parsed = parseValue();
    skipWhitespace();
    if (position !== text.length) fail('trailing content');
    if (parsed.value === null || typeof parsed.value !== 'object' || Array.isArray(parsed.value)) {
      throw new SyntaxError('content model must be a JSON object');
    }
    Object.defineProperty(parsed.value, NUMBER_META, { value: meta });
    return parsed.value;
  }

  /* ------------------------------------------------------------------ *
   * Model validation and normalization (mirrors content_model.py)
   * ------------------------------------------------------------------ */

  function numberKind(meta, parent, key) {
    if (!meta || !parent) return undefined;
    var kinds = meta.get(parent);
    return kinds ? kinds.get(key) : undefined;
  }

  function recordKind(meta, parent, key, kind) {
    if (!kind) return;
    var kinds = meta.get(parent);
    if (!kinds) {
      kinds = new Map();
      meta.set(parent, kinds);
    }
    kinds.set(key, kind);
  }

  function requireString(source, key, path) {
    if (!(key in source)) throw new ContentModelError(path + key, 'missing field');
    var value = source[key];
    if (typeof value !== 'string' || value.trim() === '') {
      throw new ContentModelError(path + key, 'expected a non-empty string');
    }
    return value;
  }

  function optionalString(source, key, path) {
    if (!(key in source)) return '';
    var value = source[key];
    if (typeof value !== 'string') {
      throw new ContentModelError(path + key, 'expected a string');
    }
    return value;
  }

  function optionalList(source, key, path) {
    if (!(key in source)) return [];
    var value = source[key];
    if (!Array.isArray(value)) {
      throw new ContentModelError(path + key, 'expected a list');
    }
    return value;
  }

  function requireList(source, key, path) {
    if (!(key in source)) throw new ContentModelError(path + key, 'missing field');
    var value = source[key];
    if (!Array.isArray(value)) {
      throw new ContentModelError(path + key, 'expected a list');
    }
    return value;
  }

  function requireNumber(source, key, path) {
    if (!(key in source)) throw new ContentModelError(path + key, 'missing field');
    var value = source[key];
    if (typeof value !== 'number') {
      throw new ContentModelError(path + key, 'expected a number');
    }
    return value;
  }

  function normalizeModel(model) {
    if (model === null || typeof model !== 'object' || Array.isArray(model)) {
      throw new ContentModelError('content model', 'expected a JSON object');
    }
    var sourceMeta = model[NUMBER_META] || null;
    var meta = new WeakMap();

    var title = requireString(model, 'title', '');
    var subtitle = optionalString(model, 'subtitle', '');
    var titleEn = optionalString(model, 'title_en', '');
    var subtitleEn = optionalString(model, 'subtitle_en', '');
    var rawItems = optionalList(model, 'items', '');
    var rawSeries = optionalList(model, 'series', '');

    var items = [];
    for (var index = 0; index < rawItems.length; index += 1) {
      var raw = rawItems[index];
      var path = 'items[' + index + '].';
      if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) {
        throw new ContentModelError('items[' + index + ']', 'expected an object');
      }
      var item = {
        label: requireString(raw, 'label', path),
        value: requireNumber(raw, 'value', path),
        note: optionalString(raw, 'note', path),
        accent: optionalString(raw, 'accent', path)
      };
      var labelEn = optionalString(raw, 'label_en', path);
      var noteEn = optionalString(raw, 'note_en', path);
      if (labelEn) item.label_en = labelEn;
      if (noteEn) item.note_en = noteEn;
      recordKind(meta, item, 'value', numberKind(sourceMeta, raw, 'value'));
      items.push(item);
    }

    var series = [];
    for (var seriesIndex = 0; seriesIndex < rawSeries.length; seriesIndex += 1) {
      var rawSeriesItem = rawSeries[seriesIndex];
      var seriesPath = 'series[' + seriesIndex + '].';
      if (rawSeriesItem === null || typeof rawSeriesItem !== 'object'
          || Array.isArray(rawSeriesItem)) {
        throw new ContentModelError('series[' + seriesIndex + ']', 'expected an object');
      }
      var name = requireString(rawSeriesItem, 'name', seriesPath);
      var rawValues = requireList(rawSeriesItem, 'values', seriesPath);
      var values = [];
      var valueKinds = new Map();
      for (var valueIndex = 0; valueIndex < rawValues.length; valueIndex += 1) {
        var value = rawValues[valueIndex];
        if (typeof value !== 'number') {
          throw new ContentModelError(
            seriesPath + 'values[' + valueIndex + ']', 'expected a number');
        }
        values.push(value);
        var kind = numberKind(sourceMeta, rawValues, valueIndex);
        if (kind) valueKinds.set(valueIndex, kind);
      }
      if (items.length && values.length !== items.length) {
        throw new ContentModelError(
          seriesPath + 'values',
          'expected ' + items.length + ' values to match items, got ' + values.length);
      }
      if (valueKinds.size) meta.set(values, valueKinds);
      var seriesItem = { name: name, values: values };
      var nameEn = optionalString(rawSeriesItem, 'name_en', seriesPath);
      if (nameEn) seriesItem.name_en = nameEn;
      series.push(seriesItem);
    }

    var normalized = { title: title, subtitle: subtitle };
    if (titleEn) normalized.title_en = titleEn;
    if (subtitleEn) normalized.subtitle_en = subtitleEn;
    normalized.items = items;
    normalized.series = series;
    Object.defineProperty(normalized, NUMBER_META, { value: meta });
    return { model: normalized, meta: meta };
  }

  function normalizeContentModel(model) {
    return normalizeModel(model).model;
  }

  /* ------------------------------------------------------------------ *
   * SHA-1 (slot id derivation)
   * ------------------------------------------------------------------ */

  function utf8Bytes(text) {
    var bytes = [];
    for (var index = 0; index < text.length; index += 1) {
      var code = text.charCodeAt(index);
      if (code >= 0xD800 && code <= 0xDBFF && index + 1 < text.length) {
        var next = text.charCodeAt(index + 1);
        if (next >= 0xDC00 && next <= 0xDFFF) {
          code = 0x10000 + ((code - 0xD800) << 10) + (next - 0xDC00);
          index += 1;
        }
      }
      if (code < 0x80) {
        bytes.push(code);
      } else if (code < 0x800) {
        bytes.push(0xC0 | (code >> 6), 0x80 | (code & 0x3F));
      } else if (code < 0x10000) {
        bytes.push(0xE0 | (code >> 12), 0x80 | ((code >> 6) & 0x3F),
          0x80 | (code & 0x3F));
      } else {
        bytes.push(0xF0 | (code >> 18), 0x80 | ((code >> 12) & 0x3F),
          0x80 | ((code >> 6) & 0x3F), 0x80 | (code & 0x3F));
      }
    }
    return bytes;
  }

  function rotateLeft(value, bits) {
    return (value << bits) | (value >>> (32 - bits));
  }

  function sha1Hex(bytes) {
    var message = bytes.slice();
    var bitLength = bytes.length * 8;
    message.push(0x80);
    while (message.length % 64 !== 56) message.push(0);
    var high = Math.floor(bitLength / 0x100000000);
    var low = bitLength >>> 0;
    message.push((high >>> 24) & 255, (high >>> 16) & 255,
      (high >>> 8) & 255, high & 255);
    message.push((low >>> 24) & 255, (low >>> 16) & 255,
      (low >>> 8) & 255, low & 255);

    var h0 = 0x67452301;
    var h1 = 0xEFCDAB89;
    var h2 = 0x98BADCFE;
    var h3 = 0x10325476;
    var h4 = 0xC3D2E1F0;
    var words = new Array(80);

    for (var offset = 0; offset < message.length; offset += 64) {
      for (var word = 0; word < 16; word += 1) {
        words[word] = (message[offset + word * 4] << 24)
          | (message[offset + word * 4 + 1] << 16)
          | (message[offset + word * 4 + 2] << 8)
          | message[offset + word * 4 + 3];
      }
      for (word = 16; word < 80; word += 1) {
        words[word] = rotateLeft(
          words[word - 3] ^ words[word - 8] ^ words[word - 14] ^ words[word - 16], 1);
      }
      var a = h0;
      var b = h1;
      var c = h2;
      var d = h3;
      var e = h4;
      for (word = 0; word < 80; word += 1) {
        var f;
        var k;
        if (word < 20) {
          f = (b & c) | ((~b) & d);
          k = 0x5A827999;
        } else if (word < 40) {
          f = b ^ c ^ d;
          k = 0x6ED9EBA1;
        } else if (word < 60) {
          f = (b & c) | (b & d) | (c & d);
          k = 0x8F1BBCDC;
        } else {
          f = b ^ c ^ d;
          k = 0xCA62C1D6;
        }
        var temp = (rotateLeft(a, 5) + f + e + k + words[word]) | 0;
        e = d;
        d = c;
        c = rotateLeft(b, 30);
        b = a;
        a = temp;
      }
      h0 = (h0 + a) | 0;
      h1 = (h1 + b) | 0;
      h2 = (h2 + c) | 0;
      h3 = (h3 + d) | 0;
      h4 = (h4 + e) | 0;
    }

    return [h0, h1, h2, h3, h4].map(function (part) {
      var hex = (part >>> 0).toString(16);
      while (hex.length < 8) hex = '0' + hex;
      return hex;
    }).join('');
  }

  /* ------------------------------------------------------------------ *
   * Shared renderer helpers
   * ------------------------------------------------------------------ */

  var EMPTY_SLOT = '<div class="ic-empty" role="status">'
    + '<span data-lang="zh">暂无数据</span>'
    + '<span data-lang="en">No data</span>'
    + '</div>';

  var EMPTY_STRUCTURE = '<p class="ic-empty" data-lang="zh">暂无数据</p>'
    + '<p class="ic-empty" data-lang="en">No data</p>';

  function section(componentId, slotId, model, body) {
    return '<section class="ic-slot" data-slot="' + slotId + '" '
      + 'data-component="' + componentId + '" '
      + 'aria-label="' + escapeSlot(model.title) + '">\n'
      + body + '\n</section>\n';
  }

  function slot(componentId, slotId, body) {
    return '<section class="ic-slot" data-slot="' + slotId + '" '
      + 'data-component="' + componentId + '">\n'
      + body + '\n</section>';
  }

  function pair(tag, zh, en, attrs) {
    var english = en || zh;
    var suffix = attrs || '';
    return '<' + tag + suffix + ' data-lang="zh">' + escapeStructure(zh) + '</' + tag + '>'
      + '<' + tag + suffix + ' data-lang="en">' + escapeStructure(english) + '</' + tag + '>';
  }

  function inlinePair(zh, en) {
    var english = en || zh;
    return '<span data-lang="zh">' + escapeStructure(zh) + '</span>'
      + '<span data-lang="en">' + escapeStructure(english) + '</span>';
  }

  function structureAccent(item, fallback) {
    if (STRUCTURE_COLOR.test(item.accent) && item.accent.indexOf('\n') < 0) {
      return item.accent;
    }
    return fallback || '';
  }

  function accentCss(accent, index) {
    if (Object.prototype.hasOwnProperty.call(ACCENT_TOKENS, accent)) {
      return 'var(--' + accent + ')';
    }
    if (accent && HEX_COLOR.test(accent) && accent.indexOf('\n') < 0) {
      return accent;
    }
    return 'var(--chart-' + ((index % 4) + 1) + ')';
  }

  function progressState(value) {
    if (value >= 100) return 'done';
    if (value > 0) return 'current';
    return 'pending';
  }

  function itemEntries(model) {
    if (model.items.length) {
      return {
        entries: model.items.map(function (item) {
          return { label: item.label, value: item.value, note: item.note, accent: item.accent };
        }),
        field: 'items[{}].value'
      };
    }
    if (model.series.length) {
      return {
        entries: model.series[0].values.map(function (value, index) {
          return { label: String(index + 1), value: value, note: '', accent: '' };
        }),
        field: 'series[0].values[{}]'
      };
    }
    return { entries: null, field: '' };
  }

  /* ------------------------------------------------------------------ *
   * Chart family
   * ------------------------------------------------------------------ */

  function renderBarChart(model, slotId) {
    var source = itemEntries(model);
    var entries = source.entries;
    if (!entries) return section(4, slotId, model, EMPTY_SLOT);

    entries.forEach(function (entry, index) {
      if (entry.value < 0) {
        throw new ContentModelError(
          source.field.replace('{}', index), 'expected a non-negative number');
      }
    });
    var maximum = entries[0].value;
    entries.forEach(function (entry) {
      if (entry.value > maximum) maximum = entry.value;
    });

    var rows = entries.map(function (entry, index) {
      var width = percent(entry.value, maximum);
      return '  <div class="bar-item">\n'
        + '    <div class="bar-label">' + escapeSlot(entry.label) + '</div>\n'
        + '    <div class="bar-track">\n'
        + '      <div class="bar-fill" style="width:' + formatPercent(width) + '%; '
        + 'background:' + accentCss(entry.accent, index) + ';">'
        + escapeSlot(formatNumber(entry.value)) + '</div>\n'
        + '    </div>\n'
        + '  </div>';
    });
    return section(4, slotId, model,
      '  <div class="bar-chart">\n' + rows.join('\n') + '\n  </div>');
  }

  function renderStatusChain(model, slotId) {
    var entries = itemEntries(model).entries;
    if (!entries) return section(15, slotId, model, EMPTY_SLOT);

    var steps = entries.map(function (entry) {
      var status = entry.note
        ? '\n    <div class="sc-status">' + escapeSlot(entry.note) + '</div>'
        : '';
      return '  <div class="sc-step ' + progressState(entry.value) + '">\n'
        + '    <div class="sc-dot"></div>\n'
        + '    <div class="sc-label">' + escapeSlot(entry.label) + '</div>' + status + '\n'
        + '  </div>';
    });
    return section(15, slotId, model,
      '  <div class="status-chain">\n' + steps.join('\n') + '\n  </div>');
  }

  function renderHeatmap(model, slotId) {
    var rows;
    if (model.series.length) {
      rows = model.series.map(function (series) {
        return { name: series.name, values: series.values };
      });
    } else if (model.items.length) {
      rows = [{
        name: model.title,
        values: model.items.map(function (item) { return item.value; })
      }];
    } else {
      return section(19, slotId, model, EMPTY_SLOT);
    }

    var width = 0;
    rows.forEach(function (row) {
      if (row.values.length > width) width = row.values.length;
    });
    if (width === 0) return section(19, slotId, model, EMPTY_SLOT);

    var labels = model.items.map(function (item) { return item.label; });
    if (!labels.length) {
      labels = [];
      for (var index = 0; index < width; index += 1) labels.push(String(index + 1));
    }

    var numbers = [];
    rows.forEach(function (row) {
      row.values.forEach(function (value) { numbers.push(value); });
    });
    var lowest = numbers[0];
    var highest = numbers[0];
    numbers.forEach(function (value) {
      if (value < lowest) lowest = value;
      if (value > highest) highest = value;
    });

    var header = '    <div class="hm-row">\n'
      + '      <div class="hm-label"></div>\n'
      + labels.map(function (label) {
        return '      <div class="hm-hdr">' + escapeSlot(label) + '</div>';
      }).join('\n')
      + '\n    </div>';

    var bodyRows = rows.map(function (row) {
      var cells = row.values.map(function (value) {
        return '      <div class="hm-cell" data-l="'
          + intensity(value, lowest, highest) + '">'
          + escapeSlot(formatNumber(value)) + '</div>';
      }).join('\n');
      return '    <div class="hm-row">\n'
        + '      <div class="hm-label">' + escapeSlot(row.name) + '</div>\n'
        + cells + '\n'
        + '    </div>';
    });

    return section(19, slotId, model,
      '  <div class="heatmap">\n' + header + '\n' + bodyRows.join('\n') + '\n  </div>');
  }

  function renderStepIndicator(model, slotId) {
    var entries = itemEntries(model).entries;
    if (!entries) return section(20, slotId, model, EMPTY_SLOT);

    var steps = entries.map(function (entry, index) {
      return '  <div class="si-step ' + progressState(entry.value) + '">'
        + '<div class="si-num">' + (index + 1) + '</div>'
        + '<div class="si-label">' + escapeSlot(entry.label) + '</div></div>';
    });
    return section(20, slotId, model,
      '  <div class="step-indicator">\n' + steps.join('\n') + '\n  </div>');
  }

  function renderChartSet(model, slotId) {
    var source = itemEntries(model);
    var entries = source.entries;
    if (!entries) return section(24, slotId, model, EMPTY_SLOT);

    entries.forEach(function (entry, index) {
      if (entry.value < 0) {
        throw new ContentModelError(
          source.field.replace('{}', index), 'expected a non-negative number');
      }
    });
    var maximum = entries[0].value;
    entries.forEach(function (entry) {
      if (entry.value > maximum) maximum = entry.value;
    });

    var bars = entries.map(function (entry) {
      var height = percent(entry.value, maximum);
      return '      <div class="vc-bar" style="--h:' + formatPercent(height) + ';" '
        + 'data-label="' + escapeSlot(entry.label) + '">'
        + '<span class="vc-val">' + escapeSlot(formatNumber(entry.value)) + '</span></div>';
    });
    return section(24, slotId, model,
      '  <div class="vchart">\n'
      + '    <div class="vc-group">\n'
      + bars.join('\n') + '\n'
      + '    </div>\n'
      + '  </div>');
  }

  function valuesFromItems(items, meta) {
    var values = [];
    var kinds = new Map();
    items.forEach(function (item, index) {
      values.push(item.value);
      var kind = numberKind(meta, item, 'value');
      if (kind) kinds.set(index, kind);
    });
    if (kinds.size) meta.set(values, kinds);
    return values;
  }

  function echartsOption(model, meta) {
    var series = model.series.length
      ? model.series
      : [{ name: model.title, values: valuesFromItems(model.items, meta) }];
    var labels = model.items.map(function (item) { return item.label; });
    if (!labels.length) {
      var longest = 0;
      series.forEach(function (item) {
        if (item.values.length > longest) longest = item.values.length;
      });
      labels = [];
      for (var index = 0; index < longest; index += 1) labels.push(String(index + 1));
    }

    var title = { text: model.title };
    if (model.subtitle) title.subtext = model.subtitle;

    var option = {
      title: title,
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '@@GV_TEXT@@' } },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { color: '@@GV_MUTED@@' }
      },
      yAxis: { type: 'value', axisLabel: { color: '@@GV_MUTED@@' } },
      series: [],
      grid: { left: 60, right: 30, top: 60, bottom: 30 }
    };
    series.forEach(function (item, index) {
      var entry = { name: item.name, type: 'bar' };
      if (series.length > 1) entry.stack = 'total';
      entry.data = item.values;
      entry.itemStyle = { color: '@@GV_COLOR_' + index + '@@' };
      option.series.push(entry);
    });
    return option;
  }

  function substituteColors(optionJs) {
    var text = optionJs.split('"@@GV_TEXT@@"').join("gv('--text')");
    var muted = text.split('"@@GV_MUTED@@"').join("gv('--muted')");
    return muted.replace(/"@@GV_COLOR_(\d+)@@"/g, function (match, index) {
      return "gv('" + COLOR_VARS[parseInt(index, 10) % COLOR_VARS.length] + "')";
    });
  }

  function renderEcharts(model, slotId, meta) {
    if (!model.items.length && !model.series.length) {
      return section(26, slotId, model, EMPTY_SLOT);
    }

    var optionJs = stringifyJson(echartsOption(model, meta), {
      sortKeys: false,
      indent: 2,
      meta: meta
    });
    optionJs = substituteColors(optionJs);
    var lines = optionJs.split('\n');
    optionJs = [lines[0]].concat(lines.slice(1).map(function (line) {
      return '  ' + line;
    })).join('\n');

    return '<section class="ic-slot" data-slot="' + slotId + '" data-component="26">\n'
      + '  <div class="ic-chart" '
      + 'id="chart-' + slotId + '" style="width:100%;height:350px;margin:1rem 0;"></div>\n'
      + '  <div class="no-js-fallback"><p>图表加载需要 JavaScript</p></div>\n'
      + '</section>\n'
      + '<script>\n'
      + '(function () {\n'
      + '  var el = document.getElementById("chart-' + slotId + '");\n'
      + '  if (!el || typeof echarts === "undefined") return;\n'
      + '  function gv(n) { return getComputedStyle(document.documentElement)'
      + '.getPropertyValue(n).trim(); }\n'
      + '  var chart = echarts.init(el);\n'
      + '  chart.setOption(' + optionJs + ');\n'
      + '})();\n'
      + '<\/script>';
  }

  /* ------------------------------------------------------------------ *
   * Structure family
   * ------------------------------------------------------------------ */

  function renderDataCards(model, slotId) {
    if (!model.items.length) return slot(12, slotId, EMPTY_STRUCTURE);

    var cards = model.items.map(function (item) {
      var parts = ['<div class="dg-card" data-anim="fade-up">'];
      var color = structureAccent(item);
      var style = color ? ' style="color:' + color + '"' : '';
      parts.push('<div class="dg-value"' + style + '>'
        + escapeStructure(formatNumber(item.value)) + '</div>');
      if (item.note) {
        parts.push(pair('div', item.note, item.note_en, ' class="dg-unit"'));
      }
      parts.push(pair('div', item.label, item.label_en, ' class="dg-label"'));
      parts.push('</div>');
      return parts.join('');
    });

    return slot(12, slotId,
      '<div class="data-grid">' + cards.join('') + '</div>');
  }

  function renderRoleCards(model, slotId) {
    if (!model.items.length) return slot(2, slotId, EMPTY_STRUCTURE);

    var palette = ['#3b82f6', '#f59e0b', '#ef4444', '#10b981'];
    var cards = model.items.map(function (item, index) {
      var color = structureAccent(item, palette[index % palette.length]);
      var header = '<div class="role-header" style="background:' + color + ';color:#fff">'
        + inlinePair(item.label, item.label_en) + '</div>';
      var body = '';
      if (item.note) {
        body = '<div class="role-body">'
          + pair('p', item.note, item.note_en)
          + '</div>';
      }
      return '<div class="role-card">' + header + body + '</div>';
    });

    return slot(2, slotId,
      '<div class="role-grid">' + cards.join('') + '</div>');
  }

  function renderTimeline(model, slotId) {
    if (!model.items.length) return slot(3, slotId, EMPTY_STRUCTURE);

    var ordered = model.items.slice().sort(function (left, right) {
      return left.value - right.value;
    });
    var events = ordered.map(function (item) {
      var color = structureAccent(item);
      var classes = item.accent ? 'tl-dot major' : 'tl-dot';
      var style = color ? ' style="background:' + color + '"' : '';
      var parts = [
        '<div class="tl-item"><div class="' + classes + '"' + style + '></div>',
        pair('div', item.label, item.label_en, ' class="tl-date"')
      ];
      if (item.note) {
        parts.push(pair('div', item.note, item.note_en, ' class="tl-desc"'));
      }
      parts.push('</div>');
      return parts.join('');
    });

    return slot(3, slotId,
      '<div class="timeline">' + events.join('') + '</div>');
  }

  var CMP_ARROW = '<span class="cmp-arrow">↕</span>';

  var SORT_SCRIPT = '<script>\n'
    + '(function () {\n'
    + '  var table = document.getElementById("cmp-{slot_id}");\n'
    + '  if (!table) return;\n'
    + "  table.querySelectorAll('th[data-sort]').forEach(function (th) {\n"
    + '    th.addEventListener("click", function () {\n'
    + '      var body = table.tBodies[0];\n'
    + '      var rows = Array.prototype.slice.call(body.rows);\n'
    + '      var index = Array.prototype.indexOf.call(th.parentNode.children, th);\n'
    + '      var asc = !th.classList.contains("sorted-asc");\n'
    + '      table.querySelectorAll("th").forEach(function (cell) {\n'
    + '        cell.classList.remove("sorted-asc", "sorted-desc");\n'
    + '      });\n'
    + '      th.classList.add(asc ? "sorted-asc" : "sorted-desc");\n'
    + '      rows.sort(function (a, b) {\n'
    + '        var x = a.cells[index].textContent.trim();\n'
    + '        var y = b.cells[index].textContent.trim();\n'
    + '        var p = parseFloat(x);\n'
    + '        var q = parseFloat(y);\n'
    + '        if (!isNaN(p) && !isNaN(q)) return asc ? p - q : q - p;\n'
    + '        return asc ? x.localeCompare(y, "zh-CN") : y.localeCompare(x, "zh-CN");\n'
    + '      });\n'
    + '      rows.forEach(function (row) { body.appendChild(row); });\n'
    + '    });\n'
    + '  });\n'
    + '})();\n'
    + '<\/script>';

  function tableColumns(model) {
    if (model.series.length) {
      return model.series.map(function (series) {
        return [series.name, series.name_en || ''];
      });
    }
    return [['数值', 'Value']];
  }

  function tableHead(model, sortable) {
    var columns = tableColumns(model);
    if (sortable) {
      var first = '<th data-sort>' + inlinePair('维度', 'Dimension') + CMP_ARROW + '</th>';
      var cells = columns.map(function (column) {
        return '<th data-sort>' + inlinePair(column[0], column[1]) + CMP_ARROW + '</th>';
      }).join('');
      return '<tr>' + first + cells + '</tr>';
    }
    var plain = columns.map(function (column) {
      return '<th>' + inlinePair(column[0], column[1]) + '</th>';
    }).join('');
    return '<tr><th></th>' + plain + '</tr>';
  }

  function tableRows(model) {
    var rows = [];
    model.items.forEach(function (item, index) {
      var cells = ['<td data-label="维度">'
        + inlinePair(item.label, item.label_en) + '</td>'];
      if (model.series.length) {
        model.series.forEach(function (series) {
          cells.push('<td data-label="' + escapeStructure(series.name) + '">'
            + escapeStructure(formatNumber(series.values[index])) + '</td>');
        });
      } else {
        cells.push('<td data-label="数值">'
          + escapeStructure(formatNumber(item.value)) + '</td>');
      }
      rows.push('<tr>' + cells.join('') + '</tr>');
    });
    return rows.join('');
  }

  function tableMarkup(model, tableClass, tableAttrs, sortable) {
    return '<table class="' + tableClass + '"' + (tableAttrs || '') + '>'
      + '<thead>' + tableHead(model, sortable) + '</thead>'
      + '<tbody>' + tableRows(model) + '</tbody>'
      + '</table>';
  }

  function renderComparisonTable(model, slotId) {
    if (!model.items.length) return slot(5, slotId, EMPTY_STRUCTURE);

    var body = tableMarkup(model, 'cmp-table', '', false);
    if (model.subtitle) {
      body += pair('p', model.subtitle, model.subtitle_en, ' class="cmp-caption"');
    }
    return slot(5, slotId, body);
  }

  function renderComparisonTableEnhanced(model, slotId) {
    if (!model.items.length) return slot(22, slotId, EMPTY_STRUCTURE);

    var table = tableMarkup(
      model, 'cmp-table', ' data-sortable id="cmp-' + slotId + '"', true);
    var body = '<div class="cmp-wrap" data-anim="fade-up">\n' + table + '\n</div>\n'
      + SORT_SCRIPT.split('{slot_id}').join(slotId);
    if (model.subtitle) {
      body += '\n' + pair('p', model.subtitle, model.subtitle_en, ' class="cmp-caption"');
    }
    return slot(22, slotId, body);
  }

  function renderQuoteCard(model, slotId) {
    var quotes = model.items.length
      ? model.items.map(function (item) {
        return [item.label, item.label_en, item.note, item.note_en];
      })
      : [[model.title, model.title_en, model.subtitle, model.subtitle_en]];

    var cards = quotes.map(function (quote) {
      var parts = [
        '<div class="quote-card" data-anim="fade-up">',
        '<div class="qc-bar"></div>',
        '<div class="qc-body">',
        pair('p', quote[0], quote[1], ' class="qc-text"')
      ];
      if (quote[2]) {
        parts.push('<div class="qc-source">'
          + pair('span', quote[2], quote[3], ' class="qc-title"')
          + '</div>');
      }
      parts.push('</div></div>');
      return parts.join('');
    });

    return slot(13, slotId, cards.join(''));
  }

  function tagLabel(label) {
    return label.replace(/^\s+/, '').charAt(0) === '#' ? label : '# ' + label;
  }

  function tagClass(item, index) {
    if (TAG_PALETTE.indexOf(item.accent) >= 0) {
      return 'tag tag-' + item.accent;
    }
    return 'tag tag-' + TAG_PALETTE[index % TAG_PALETTE.length];
  }

  function renderTagGroup(model, slotId) {
    if (!model.items.length) return slot(17, slotId, EMPTY_STRUCTURE);

    var tags = model.items.map(function (item, index) {
      var classes = tagClass(item, index);
      var english = item.label_en ? tagLabel(item.label_en) : '';
      return pair('span', tagLabel(item.label), english, ' class="' + classes + '"');
    });

    return slot(17, slotId,
      '<div class="tag-group" data-anim="fade-up">' + tags.join('') + '</div>');
  }

  function renderCallouts(model, slotId) {
    if (!model.items.length) return slot(18, slotId, EMPTY_STRUCTURE);

    var bars = model.items.map(function (item) {
      var type = CALLOUT_TYPES[item.accent] || CALLOUT_TYPES.info;
      var paragraphs = [pair('p', item.label, item.label_en)];
      if (item.note) {
        paragraphs.push(pair('p', item.note, item.note_en));
      }
      return '<div class="callout callout-' + type[0] + '" data-anim="fade-up">'
        + '<div class="callout-icon">' + type[1] + '</div>'
        + '<div class="callout-body">' + paragraphs.join('') + '</div>'
        + '</div>';
    });

    return slot(18, slotId, bars.join(''));
  }

  var RENDERERS = {
    2: renderRoleCards,
    3: renderTimeline,
    4: renderBarChart,
    5: renderComparisonTable,
    12: renderDataCards,
    13: renderQuoteCard,
    15: renderStatusChain,
    17: renderTagGroup,
    18: renderCallouts,
    19: renderHeatmap,
    20: renderStepIndicator,
    22: renderComparisonTableEnhanced,
    24: renderChartSet,
    26: renderEcharts
  };

  /* ------------------------------------------------------------------ *
   * Public entry points
   * ------------------------------------------------------------------ */

  function canonicalJson(model) {
    var normalized = normalizeModel(model);
    return stringifyJson(normalized.model, {
      sortKeys: true,
      meta: normalized.meta
    });
  }

  function renderSlot(componentId, model, slotId) {
    var renderer = RENDERERS[componentId];
    if (!renderer) {
      throw new Error('unsupported component id: ' + JSON.stringify(componentId));
    }
    if (typeof model === 'string') model = parseModel(model);
    var normalized = normalizeModel(model);
    var canonical = stringifyJson(normalized.model, {
      sortKeys: true,
      meta: normalized.meta
    });

    var id = slotId;
    if (id === undefined || id === null) {
      id = 'slot-' + componentId + '-'
        + sha1Hex(utf8Bytes(canonical)).slice(0, 8);
    } else if (typeof id !== 'string' || id.indexOf('\n') >= 0 || !SLOT_ID.test(id)) {
      throw new Error('invalid slot id: ' + JSON.stringify(id));
    }

    var dataBlock = '<script type="application/json" data-slot="' + id + '">'
      + scriptSafe(canonical) + '<\/script>';
    var markup = renderer(normalized.model, id, normalized.meta);
    return {
      slotId: id,
      componentId: componentId,
      markup: markup,
      dataBlock: dataBlock,
      fragment: markup + '\n' + dataBlock + '\n'
    };
  }

  function renderMarkup(componentId, model, slotId) {
    return renderSlot(componentId, model, slotId).markup;
  }

  var ids = Object.keys(RENDERERS).map(Number);
  ids.sort(function (left, right) { return left - right; });

  return {
    renderSlot: renderSlot,
    renderMarkup: renderMarkup,
    parseModel: parseModel,
    canonicalJson: canonicalJson,
    normalizeContentModel: normalizeContentModel,
    componentIds: ids,
    ContentModelError: ContentModelError,
    __internal: {
      pythonFloatRepr: pythonFloatRepr,
      sha1Hex: sha1Hex,
      stringifyJson: stringifyJson
    }
  };
}));
