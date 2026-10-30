/* Editor core — pure decisions behind the in-report component editor.
 *
 * Nothing here touches the DOM.  The editor bootstrap (runtime/editor.js) only
 * paints what these functions decide, which keeps the risky part testable under
 * node:
 *
 *   slotShape(model)                     'series' | 'items' | 'empty'
 *   canConsume(componentId, model)       can this renderer read this slot?
 *   candidatesFor(model, currentId)      filtered, same-family-first list
 *   mappingPreview(fromId, toId, model)  what the swap shows and drops
 *   createHistory() / recordPatch() / canUndo() / undo()
 *   isEditableFlag(value)                the data-editable gate
 *   familyOf(componentId), componentIds
 *
 * Save pipeline (also pure, also DOM-free):
 *
 *   stripEditorUi(html)          drop every element marked data-ic-editor-ui
 *   clearEditingState(html)      drop the ic-editing class from <html>
 *   rebuildDataBlocks(html)      re-emit each slot's JSON in canonical form
 *   savedFileName(title)         the download name derived from <title>
 *   savedHtml(html, options)     the whole pipeline: UI out, doctype in
 *
 * Candidate order is the swap-cost heuristic from the spec: the current
 * component's family leads, so the least lossy option comes first.  An
 * unknown current id falls back to the slot's data shape (series → chart).
 */
(function (root, factory) {
  'use strict';
  var api = factory(root);
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.SlotEditorCore = api;
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';

  var CHART = 'chart';
  var STRUCTURE = 'structure';

  /* Descriptor fields:
   *   needsItems  renderer produces nothing meaningful without items
   *   subtitle    true | 'empty-only' | false — shows model.subtitle
   *   itemValue   true | false | 'no-series' | 'status' | 'order'
   *   series      'all' | 'first' | 'none'
   *   nonNegative bar renderers reject negative numbers
   * Title consumption lives in TITLE_CONSUMPTION below: most renderers use
   * the title only as an aria-label, so the mapping preview must not claim it.
   */
  var DESCRIPTORS = {
    2: {
      id: 2, name: '角色卡片', family: STRUCTURE,
      needsItems: true, subtitle: false,
      itemLabel: true, itemValue: false, itemNote: true, itemAccent: true,
      series: 'none'
    },
    3: {
      id: 3, name: 'CSS 时间线', family: STRUCTURE,
      needsItems: true, subtitle: false,
      itemLabel: true, itemValue: 'order', itemNote: true, itemAccent: true,
      series: 'none'
    },
    4: {
      id: 4, name: 'CSS 条形图', family: CHART,
      needsItems: false, subtitle: false,
      itemLabel: true, itemValue: true, itemNote: false, itemAccent: true,
      series: 'first', nonNegative: true
    },
    5: {
      id: 5, name: '对比表', family: STRUCTURE,
      needsItems: true, subtitle: true,
      itemLabel: true, itemValue: 'no-series', itemNote: false, itemAccent: false,
      series: 'all'
    },
    12: {
      id: 12, name: '数据卡片网格', family: STRUCTURE,
      needsItems: true, subtitle: false,
      itemLabel: true, itemValue: true, itemNote: true, itemAccent: true,
      series: 'none'
    },
    13: {
      id: 13, name: '引用引文卡片', family: STRUCTURE,
      needsItems: false, subtitle: 'empty-only',
      itemLabel: true, itemValue: false, itemNote: true, itemAccent: false,
      series: 'none'
    },
    15: {
      id: 15, name: '状态链进度里程碑', family: CHART,
      needsItems: false, subtitle: false,
      itemLabel: true, itemValue: 'status', itemNote: true, itemAccent: false,
      series: 'first'
    },
    17: {
      id: 17, name: '标签徽章组', family: STRUCTURE,
      needsItems: true, subtitle: false,
      itemLabel: true, itemValue: false, itemNote: false, itemAccent: true,
      series: 'none'
    },
    18: {
      id: 18, name: '提示框告警条', family: STRUCTURE,
      needsItems: true, subtitle: false,
      itemLabel: true, itemValue: false, itemNote: true, itemAccent: true,
      series: 'none'
    },
    19: {
      id: 19, name: '热力图密度图', family: CHART,
      needsItems: false, subtitle: false,
      itemLabel: true, itemValue: 'no-series', itemNote: false, itemAccent: false,
      series: 'all'
    },
    20: {
      id: 20, name: '步骤指示器', family: CHART,
      needsItems: false, subtitle: false,
      itemLabel: true, itemValue: 'status', itemNote: false, itemAccent: false,
      series: 'first'
    },
    22: {
      id: 22, name: '对比表 增强版', family: STRUCTURE,
      needsItems: true, subtitle: true,
      itemLabel: true, itemValue: 'no-series', itemNote: false, itemAccent: false,
      series: 'all'
    },
    24: {
      id: 24, name: '数据图表集', family: CHART,
      needsItems: false, subtitle: false,
      itemLabel: true, itemValue: true, itemNote: false, itemAccent: false,
      series: 'first', nonNegative: true
    },
    26: {
      id: 26, name: 'ECharts 交互式图表集', family: CHART,
      needsItems: false, subtitle: true,
      itemLabel: true, itemValue: 'no-series', itemNote: false, itemAccent: false,
      series: 'all'
    }
  };

  var IDS = [2, 3, 4, 5, 12, 13, 15, 17, 18, 19, 20, 22, 24, 26];

  /* Only #26 renders through a third-party library; the other thirteen are
   * pure markup.  `global` is the name the library installs on globalThis. */
  var LIBRARIES = {
    26: { name: 'echarts.min.js', global: 'echarts' }
  };

  function libraryFor(componentId) {
    return LIBRARIES[componentId] || null;
  }

  /* Which components actually render the title.  Every other renderer only
   * uses it as the section's aria-label, which is not "displayed" content. */
  var TITLE_CONSUMPTION = {
    13: 'empty-only',
    26: true
  };

  var LABELS = {
    title: '标题',
    subtitle: '副标题',
    itemLabel: '条目标签',
    itemValue: '条目数值',
    itemNote: '条目备注',
    itemAccent: '强调色',
    seriesName: '系列名称',
    seriesValues: '系列数值',
    extraSeries: '第 2 条及之后的系列'
  };

  var FIELD_ORDER = [
    'title', 'subtitle', 'itemLabel', 'itemValue', 'itemNote', 'itemAccent',
    'seriesName', 'seriesValues', 'extraSeries'
  ];

  function familyOf(componentId) {
    var descriptor = DESCRIPTORS[componentId];
    return descriptor ? descriptor.family : null;
  }

  function items(model) {
    return (model && model.items) || [];
  }

  function series(model) {
    return (model && model.series) || [];
  }

  function seriesValueCount(model) {
    var total = 0;
    series(model).forEach(function (entry) {
      total += (entry.values || []).length;
    });
    return total;
  }

  function hasData(model) {
    return items(model).length > 0 || seriesValueCount(model) > 0;
  }

  function slotShape(model) {
    if (seriesValueCount(model) > 0) return 'series';
    if (items(model).length > 0) return 'items';
    return 'empty';
  }

  function entryValues(model) {
    if (items(model).length) {
      return items(model).map(function (item) { return item.value; });
    }
    var first = series(model)[0];
    return first ? (first.values || []).slice() : [];
  }

  function canConsume(componentId, model) {
    var descriptor = DESCRIPTORS[componentId];
    if (!descriptor) return false;
    if (descriptor.needsItems && !items(model).length) return false;
    if (!hasData(model) && componentId !== 13) return false;
    if (descriptor.series === 'first' && !entryValues(model).length) return false;
    if (descriptor.nonNegative) {
      var values = entryValues(model);
      for (var index = 0; index < values.length; index += 1) {
        if (values[index] < 0) return false;
      }
    }
    return true;
  }

  function preferredFamily(model) {
    return slotShape(model) === 'series' ? CHART : STRUCTURE;
  }

  function candidatesFor(model, currentComponentId) {
    /* Story 9: lead with the current component's family so the least lossy
     * swap is first.  An unknown current id falls back to the data shape. */
    var preferred = familyOf(currentComponentId) || preferredFamily(model);
    var currentFamily = familyOf(currentComponentId);
    var candidates = [];
    IDS.forEach(function (componentId) {
      if (componentId === currentComponentId) return;
      if (!canConsume(componentId, model)) return;
      var descriptor = DESCRIPTORS[componentId];
      candidates.push({
        id: componentId,
        name: descriptor.name,
        family: descriptor.family,
        sameFamily: descriptor.family === preferred,
        crossFamily: descriptor.family !== currentFamily
      });
    });
    candidates.sort(function (left, right) {
      if (left.sameFamily !== right.sameFamily) return left.sameFamily ? -1 : 1;
      if (left.family !== right.family) return left.family === CHART ? -1 : 1;
      return left.id - right.id;
    });
    return candidates;
  }

  function anyItemField(model, key) {
    return items(model).some(function (item) {
      return Boolean(item[key]);
    });
  }

  function presentFields(model) {
    var present = { title: true };
    if (model && model.subtitle) present.subtitle = true;
    if (items(model).length) {
      present.itemLabel = true;
      present.itemValue = true;
      if (anyItemField(model, 'note')) present.itemNote = true;
      if (anyItemField(model, 'accent')) present.itemAccent = true;
    }
    if (seriesValueCount(model) > 0) {
      present.seriesName = true;
      present.seriesValues = true;
    }
    return present;
  }

  function consumedFields(descriptor, model) {
    var consumed = {};
    var itemCount = items(model).length;
    var seriesCount = seriesValueCount(model);

    var titleUse = TITLE_CONSUMPTION[descriptor.id] || false;
    if (titleUse === true) consumed.title = true;
    else if (titleUse === 'empty-only' && !itemCount) consumed.title = true;

    if (descriptor.subtitle && model && model.subtitle
        && (descriptor.subtitle !== 'empty-only' || !itemCount)) {
      consumed.subtitle = true;
    }
    if (itemCount && descriptor.itemLabel) consumed.itemLabel = true;
    if (itemCount) {
      if (descriptor.itemValue === true) consumed.itemValue = true;
      else if (descriptor.itemValue === 'no-series' && !seriesCount) consumed.itemValue = true;
      else if (descriptor.itemValue === 'status' || descriptor.itemValue === 'order') {
        consumed.itemValue = true;
      }
    }
    if (itemCount && descriptor.itemNote && anyItemField(model, 'note')) {
      consumed.itemNote = true;
    }
    if (itemCount && descriptor.itemAccent && anyItemField(model, 'accent')) {
      consumed.itemAccent = true;
    }
    if (seriesCount && descriptor.series === 'all') {
      consumed.seriesName = true;
      consumed.seriesValues = true;
    }
    if (seriesCount && descriptor.series === 'first' && !itemCount) {
      consumed.seriesValues = true;
    }
    return consumed;
  }

  function fieldLabel(key, descriptor) {
    if (key === 'itemValue' && descriptor.itemValue === 'status') {
      return '条目数值（进度状态）';
    }
    if (key === 'itemValue' && descriptor.itemValue === 'order') {
      return '条目数值（排序依据）';
    }
    return LABELS[key];
  }

  function fieldList(fields, descriptor) {
    return FIELD_ORDER.filter(function (key) {
      return Boolean(fields[key]);
    }).map(function (key) {
      return fieldLabel(key, descriptor);
    });
  }

  function mappingPreview(fromComponentId, toComponentId, model) {
    var fromDescriptor = DESCRIPTORS[fromComponentId];
    var toDescriptor = DESCRIPTORS[toComponentId];
    if (!fromDescriptor || !toDescriptor) {
      throw new Error('unknown component id in mapping preview');
    }

    var present = presentFields(model);
    var consumed = consumedFields(toDescriptor, model);
    var displays = [];
    var drops = [];
    FIELD_ORDER.forEach(function (key) {
      if (!present[key]) return;
      if (consumed[key]) displays.push(fieldLabel(key, toDescriptor));
      else drops.push(fieldLabel(key, toDescriptor));
    });
    if (toDescriptor.series === 'first' && consumed.seriesValues
        && series(model).length > 1) {
      drops.push(LABELS.extraSeries);
    }

    var summary = '新组件显示：' + (displays.length ? displays.join('、') : '无可用内容');
    summary += '；将丢弃：' + (drops.length ? drops.join('、') : '无');

    return {
      from: {
        id: fromComponentId,
        name: fromDescriptor.name,
        family: fromDescriptor.family
      },
      to: {
        id: toComponentId,
        name: toDescriptor.name,
        family: toDescriptor.family
      },
      crossFamily: fromDescriptor.family !== toDescriptor.family,
      displays: displays,
      drops: drops,
      summary: summary
    };
  }

  function createHistory() {
    return { patches: [] };
  }

  function recordPatch(history, patch) {
    if (!patch || typeof patch !== 'object') {
      throw new Error('patch must be an object');
    }
    if (!patch.slotId) throw new Error('patch needs a slotId');
    if (!patch.to) throw new Error('patch needs a destination component');
    var patches = (history && history.patches ? history.patches : []).slice();
    patches.push(patch);
    return { patches: patches };
  }

  function canUndo(history) {
    return Boolean(history && history.patches && history.patches.length);
  }

  function undo(history) {
    if (!canUndo(history)) return null;
    var patches = history.patches.slice();
    var patch = patches.pop();
    return { history: { patches: patches }, patch: patch };
  }

  function isEditableFlag(value) {
    return value === 'true' || value === '';
  }

  /* ------------------------------------------------------------------ *
   * Swap orchestration
   *
   * A swap may need a library the report does not carry.  Only the browser
   * can fetch it, so the effects arrive as injected functions and the
   * decision stays testable under node:
   *
   *   hasLibrary(library)             is the global already defined?
   *   loadLibrary(library)            CDN-first load, resolves when ready
   *   render(componentId, model, id)  SlotRuntime.renderSlot
   *   commit(rendered)                put the markup into the document
   *
   * A failed load commits a readable failure state instead of an empty
   * chart.  A render failure is not a load failure, so it propagates.
   * ------------------------------------------------------------------ */

  function swapSlot(options) {
    var settings = options || {};
    var library = libraryFor(settings.componentId);

    function render() {
      var rendered = settings.render(
        settings.componentId, settings.model, settings.slotId);
      settings.commit(rendered);
      return {
        status: 'rendered',
        library: library ? library.name : null
      };
    }

    if (!library || settings.hasLibrary(library)) {
      return Promise.resolve().then(render);
    }
    return Promise.resolve()
      .then(function () { return settings.loadLibrary(library); })
      .then(render, function () {
        settings.commit(failureMarkup(settings));
        return { status: 'failed', library: library.name };
      });
  }

  function failureMarkup(settings) {
    return slotRuntime().renderLibraryFailure(
      settings.componentId, settings.model, settings.slotId);
  }

  /* ------------------------------------------------------------------ *
   * Save pipeline
   *
   * Saving is string surgery, not DOM surgery: the browser serializes the
   * document and these functions decide what the delivered file contains.
   * Keeping them here means the risky part — never shipping the live editor
   * chrome, never losing a data block — is testable under node.
   *
   * The scanner below is deliberately small: it only has to survive the
   * markup this project emits.  Raw-text elements (script/style/textarea/
   * title) are copied verbatim, so HTML-looking strings inside the inlined
   * runtime never look like tags.
   * ------------------------------------------------------------------ */

  var UI_ATTR = /\bdata-ic-editor-ui\b/i;
  var DOCTYPE = /^\s*<!doctype\b/i;
  var TAG_AT = /^<(\/?)([A-Za-z][^\s\/>]*)/;
  var RAW_TEXT = {
    script: true, style: true, textarea: true, title: true
  };
  var VOID = {
    area: true, base: true, br: true, col: true, embed: true, hr: true,
    img: true, input: true, link: true, meta: true, param: true,
    source: true, track: true, wbr: true
  };

  function tagEnd(html, index) {
    var quote = null;
    for (var cursor = index + 1; cursor < html.length; cursor += 1) {
      var character = html.charAt(cursor);
      if (quote) {
        if (character === quote) quote = null;
      } else if (character === '"' || character === "'") {
        quote = character;
      } else if (character === '>') {
        return cursor;
      }
    }
    return -1;
  }

  function tagAt(html, index) {
    if (html.charAt(index) !== '<') return null;
    var match = TAG_AT.exec(html.slice(index, index + 256));
    if (!match) return null;
    var end = tagEnd(html, index);
    if (end < 0) return null;
    var text = html.slice(index, end + 1);
    return {
      name: match[2].toLowerCase(),
      closing: match[1] === '/',
      end: end + 1,
      text: text,
      selfClosing: /\/\s*>$/.test(text)
    };
  }

  function commentEnd(html, index) {
    var end = html.indexOf('-->', index + 4);
    return end < 0 ? -1 : end + 3;
  }

  function findClosingTag(html, from, name) {
    var lower = html.toLowerCase();
    var needle = '</' + name;
    var cursor = from;
    while (true) {
      var at = lower.indexOf(needle, cursor);
      if (at < 0) return -1;
      var after = lower.charAt(at + needle.length);
      if (after === '' || /[\s>\/]/.test(after)) return at;
      cursor = at + needle.length;
    }
  }

  function hasEditorUiMarker(tagText) {
    return UI_ATTR.test(tagText);
  }

  /* Skip an element whose open tag ended at `from`, honouring same-name
   * nesting and raw-text children.  Unterminated markup drops the rest. */
  function skipElement(html, from, name) {
    var depth = 1;
    var cursor = from;
    while (cursor < html.length) {
      var lt = html.indexOf('<', cursor);
      if (lt < 0) return html.length;
      if (html.slice(lt, lt + 4) === '<!--') {
        var afterComment = commentEnd(html, lt);
        if (afterComment < 0) return html.length;
        cursor = afterComment;
        continue;
      }
      var tag = tagAt(html, lt);
      if (!tag) { cursor = lt + 1; continue; }
      if (tag.name === name) {
        if (tag.closing) {
          depth -= 1;
          if (depth === 0) return tag.end;
        } else if (!tag.selfClosing && !VOID[tag.name]) {
          depth += 1;
        }
      }
      cursor = tag.end;
      if (!tag.closing && !tag.selfClosing && RAW_TEXT[tag.name]) {
        var closeAt = findClosingTag(html, cursor, tag.name);
        cursor = closeAt < 0 ? html.length : closeAt;
      }
    }
    return html.length;
  }

  function stripEditorUi(html) {
    var text = String(html === undefined || html === null ? '' : html);
    var out = '';
    var cursor = 0;
    while (cursor < text.length) {
      var lt = text.indexOf('<', cursor);
      if (lt < 0) {
        out += text.slice(cursor);
        break;
      }
      out += text.slice(cursor, lt);
      if (text.slice(lt, lt + 4) === '<!--') {
        var afterComment = commentEnd(text, lt);
        if (afterComment < 0) {
          out += text.slice(lt);
          break;
        }
        out += text.slice(lt, afterComment);
        cursor = afterComment;
        continue;
      }
      if (text.slice(lt, lt + 2) === '<!') {
        var declarationEnd = text.indexOf('>', lt);
        if (declarationEnd < 0) {
          out += text.slice(lt);
          break;
        }
        out += text.slice(lt, declarationEnd + 1);
        cursor = declarationEnd + 1;
        continue;
      }
      var tag = tagAt(text, lt);
      if (!tag) {
        out += '<';
        cursor = lt + 1;
        continue;
      }
      if (!tag.closing && hasEditorUiMarker(tag.text)) {
        cursor = (tag.selfClosing || VOID[tag.name])
          ? tag.end
          : skipElement(text, tag.end, tag.name);
        continue;
      }
      out += tag.text;
      cursor = tag.end;
      if (!tag.closing && !tag.selfClosing && RAW_TEXT[tag.name]) {
        var closeAt = findClosingTag(text, cursor, tag.name);
        if (closeAt < 0) {
          out += text.slice(cursor);
          break;
        }
        out += text.slice(cursor, closeAt);
        cursor = closeAt;
      }
    }
    return out;
  }

  function clearEditingState(html) {
    var text = String(html === undefined || html === null ? '' : html);
    var root = /<html\b[^>]*>/i.exec(text);
    if (!root) return text;
    var tag = root[0];
    var attribute = /\sclass\s*=\s*(["'])(.*?)\1/i.exec(tag);
    if (!attribute) return text;
    var classes = attribute[2].split(/\s+/).filter(function (name) {
      return name && name !== 'ic-editing';
    });
    var replacement = classes.length ? ' class="' + classes.join(' ') + '"' : '';
    var cleaned = tag.slice(0, attribute.index) + replacement
      + tag.slice(attribute.index + attribute[0].length);
    return text.slice(0, root.index) + cleaned + text.slice(root.index + tag.length);
  }

  function withDoctype(html, doctype) {
    var text = String(html === undefined || html === null ? '' : html);
    if (DOCTYPE.test(text)) return text;
    return (doctype || '<!DOCTYPE html>') + '\n' + text;
  }

  /* The browser runtime is loaded alongside this file in a report, and
   * required lazily under node.  Canonical JSON must come from the same
   * implementation the generation path uses, so there is exactly one copy. */
  var cachedRuntime = null;

  function slotRuntime() {
    if (cachedRuntime) return cachedRuntime;
    if (typeof module === 'object' && module.exports && typeof require === 'function') {
      cachedRuntime = require('./slots.js');
    } else if (root) {
      cachedRuntime = root.SlotRuntime;
    }
    return cachedRuntime;
  }

  function isDataBlockTag(tagText) {
    if (!/^<script\b/i.test(tagText)) return false;
    var type = /\btype\s*=\s*(["'])(.*?)\1/i.exec(tagText);
    if (!type || type[2].toLowerCase() !== 'application/json') return false;
    return /\bdata-slot\s*=\s*(["'])(.*?)\1/i.test(tagText);
  }

  function sameJson(left, right) {
    if (left === right) return true;
    if (left === null || right === null) return false;
    if (typeof left !== 'object' || typeof right !== 'object') return false;
    if (Array.isArray(left) !== Array.isArray(right)) return false;
    var leftKeys = Object.keys(left);
    var rightKeys = Object.keys(right);
    if (leftKeys.length !== rightKeys.length) return false;
    for (var index = 0; index < leftKeys.length; index += 1) {
      var key = leftKeys[index];
      if (!Object.prototype.hasOwnProperty.call(right, key)) return false;
      if (!sameJson(left[key], right[key])) return false;
    }
    return true;
  }

  function rewriteDataBlock(tagText, body) {
    if (!isDataBlockTag(tagText)) return body;
    var api = slotRuntime();
    if (!api || typeof api.scriptSafe !== 'function') return body;
    var canonical;
    try {
      canonical = api.canonicalJson(body);
    } catch (error) {
      return body;
    }
    var original;
    var rebuilt;
    try {
      original = JSON.parse(body);
      rebuilt = JSON.parse(canonical);
    } catch (error) {
      return body;
    }
    /* canonicalJson drops fields the content model does not know.  Never
     * trade an unknown field for a tidier block; leave it for the validator. */
    if (!sameJson(original, rebuilt)) return body;
    return api.scriptSafe(canonical);
  }

  function rebuildDataBlocks(html) {
    var text = String(html === undefined || html === null ? '' : html);
    var out = '';
    var cursor = 0;
    while (cursor < text.length) {
      var lt = text.indexOf('<', cursor);
      if (lt < 0) {
        out += text.slice(cursor);
        break;
      }
      out += text.slice(cursor, lt);
      if (text.slice(lt, lt + 4) === '<!--') {
        var afterComment = commentEnd(text, lt);
        if (afterComment < 0) {
          out += text.slice(lt);
          break;
        }
        out += text.slice(lt, afterComment);
        cursor = afterComment;
        continue;
      }
      if (text.slice(lt, lt + 2) === '<!') {
        var declarationEnd = text.indexOf('>', lt);
        if (declarationEnd < 0) {
          out += text.slice(lt);
          break;
        }
        out += text.slice(lt, declarationEnd + 1);
        cursor = declarationEnd + 1;
        continue;
      }
      var tag = tagAt(text, lt);
      if (!tag) {
        out += '<';
        cursor = lt + 1;
        continue;
      }
      if (tag.closing || tag.selfClosing || tag.name !== 'script') {
        out += tag.text;
        cursor = tag.end;
        if (!tag.closing && !tag.selfClosing && RAW_TEXT[tag.name]) {
          var rawAt = findClosingTag(text, cursor, tag.name);
          if (rawAt < 0) {
            out += text.slice(cursor);
            break;
          }
          out += text.slice(cursor, rawAt);
          cursor = rawAt;
        }
        continue;
      }
      var closeAt = findClosingTag(text, tag.end, 'script');
      if (closeAt < 0) {
        out += tag.text + text.slice(tag.end);
        break;
      }
      var closeEnd = text.indexOf('>', closeAt) + 1;
      out += tag.text + rewriteDataBlock(tag.text, text.slice(tag.end, closeAt))
        + text.slice(closeAt, closeEnd);
      cursor = closeEnd;
    }
    return out;
  }

  function savedHtml(html, options) {
    var settings = options || {};
    var text = stripEditorUi(html);
    text = clearEditingState(text);
    text = rebuildDataBlocks(text);
    return withDoctype(text, settings.doctype);
  }

  function savedFileName(title) {
    var text = String(title === undefined || title === null ? '' : title);
    text = text.replace(/[\\/:*?"<>|\u0000-\u001f]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/^\.+/, '')
      .slice(0, 120)
      .trim();
    if (!text) text = 'report';
    if (!/\.html?$/i.test(text)) text += '.html';
    return text;
  }

  return {
    slotShape: slotShape,
    canConsume: canConsume,
    candidatesFor: candidatesFor,
    mappingPreview: mappingPreview,
    createHistory: createHistory,
    recordPatch: recordPatch,
    canUndo: canUndo,
    undo: undo,
    isEditableFlag: isEditableFlag,
    stripEditorUi: stripEditorUi,
    clearEditingState: clearEditingState,
    rebuildDataBlocks: rebuildDataBlocks,
    savedFileName: savedFileName,
    savedHtml: savedHtml,
    familyOf: familyOf,
    libraryFor: libraryFor,
    swapSlot: swapSlot,
    componentIds: IDS.slice()
  };
}));
