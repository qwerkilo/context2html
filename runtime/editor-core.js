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
 * Family membership is the swap-cost heuristic from the spec: chart-family
 * renderers lead when the slot carries series, structure-family renderers lead
 * when it only carries items.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    root.SlotEditorCore = api;
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var CHART = 'chart';
  var STRUCTURE = 'structure';

  /* Descriptor fields:
   *   needsItems  renderer produces nothing meaningful without items
   *   subtitle    renderer shows model.subtitle
   *   itemValue   true | false | 'no-series' | 'status' | 'order'
   *   series      'all' | 'first' | 'none'
   *   nonNegative bar renderers reject negative numbers
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
      needsItems: false, subtitle: true,
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
    var preferred = preferredFamily(model);
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
    var consumed = { title: true };
    var itemCount = items(model).length;
    var seriesCount = seriesValueCount(model);

    if (descriptor.subtitle && model && model.subtitle) consumed.subtitle = true;
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
    familyOf: familyOf,
    componentIds: IDS.slice()
  };
}));
