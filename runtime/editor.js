/* Editor bootstrap — the thin DOM layer behind the in-report editor.
 *
 * Loaded only in reports whose <html> carries data-editable="true"; every
 * decision (which candidates exist, what a cross-family swap drops, what undo
 * does) comes from SlotEditorCore, and every render comes from SlotRuntime.
 * This file only paints the toggle, the candidate panel and the tooltip.
 */
(function () {
  'use strict';

  var core = typeof globalThis !== 'undefined' ? globalThis.SlotEditorCore : null;
  var runtime = typeof globalThis !== 'undefined' ? globalThis.SlotRuntime : null;
  if (!core || !runtime) return;

  var doc = document;
  var root = doc.documentElement;
  if (!core.isEditableFlag(root.getAttribute('data-editable'))) return;

  var STYLE_ID = 'ic-editor-style';
  var state = {
    editing: false,
    history: core.createHistory(),
    panel: null,
    backdrop: null,
    hint: null,
    toggle: null,
    undo: null
  };

  var HINT_TEXT = '该组件不支持替换 / Not swappable';

  var CSS = [
    '.ic-editor-bar{position:fixed;top:14px;right:14px;z-index:10000;display:flex;',
    'gap:8px;align-items:center;font-family:inherit}',
    '.ic-editor-bar button{font:inherit;font-size:.85rem;line-height:1;padding:.55rem .9rem;',
    'border:1px solid var(--border,#d8d8d8);border-radius:999px;cursor:pointer;',
    'background:var(--surface,#fff);color:var(--text,#1a1a1a);',
    'box-shadow:0 4px 18px rgba(0,0,0,.16)}',
    '.ic-editor-bar button:hover{border-color:var(--accent,#c0392b);color:var(--accent,#c0392b)}',
    '.ic-editor-bar button:disabled{opacity:.45;cursor:not-allowed}',
    '.ic-editor-bar .ic-editor-undo{display:none}',
    '.ic-editing .ic-editor-bar .ic-editor-undo{display:inline-block}',
    '.ic-editor-bar .ic-editor-save{display:none}',
    '.ic-editing .ic-editor-bar .ic-editor-save{display:inline-block}',
    '.ic-editing [data-swap="unavailable"]{cursor:not-allowed}',
    '.ic-editor-backdrop{position:fixed;inset:0;z-index:10001;background:rgba(0,0,0,.35)}',
    '.ic-editor-panel{position:fixed;z-index:10002;top:50%;left:50%;',
    'transform:translate(-50%,-50%);width:min(540px,92vw);max-height:82vh;overflow:auto;',
    'box-sizing:border-box;padding:20px 22px;border-radius:14px;',
    'background:var(--surface,#fff);color:var(--text,#1a1a1a);',
    'border:1px solid var(--border,#d8d8d8);box-shadow:0 24px 70px rgba(0,0,0,.35);',
    'font-family:inherit}',
    '.ic-editor-panel h3{margin:0 0 4px;font-size:1.05rem}',
    '.ic-editor-sub{margin:0 0 14px;color:var(--muted,#777);font-size:.82rem}',
    '.ic-editor-list{display:grid;gap:8px;margin:0 0 4px}',
    '.ic-editor-candidate{display:flex;align-items:center;justify-content:space-between;',
    'gap:10px;width:100%;box-sizing:border-box;padding:.7rem .85rem;text-align:left;',
    'font:inherit;font-size:.9rem;border:1px solid var(--border,#d8d8d8);',
    'border-radius:10px;background:var(--surface,#fff);color:var(--text,#1a1a1a);',
    'cursor:pointer}',
    '.ic-editor-candidate:hover{border-color:var(--accent,#c0392b)}',
    '.ic-editor-badge{font-size:.7rem;color:var(--muted,#777);white-space:nowrap}',
    '.ic-editor-preview{margin:14px 0 4px;padding:12px 14px;border-radius:10px;',
    'background:rgba(127,127,127,.08);font-size:.85rem;line-height:1.6}',
    '.ic-editor-preview b{font-weight:600}',
    '.ic-editor-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px}',
    '.ic-editor-actions button{font:inherit;font-size:.85rem;padding:.55rem .9rem;',
    'border-radius:8px;border:1px solid var(--border,#d8d8d8);cursor:pointer;',
    'background:var(--surface,#fff);color:var(--text,#1a1a1a)}',
    '.ic-editor-actions .ic-editor-confirm{background:var(--accent,#c0392b);',
    'border-color:var(--accent,#c0392b);color:#fff}',
    '.ic-editor-tooltip{position:fixed;z-index:10003;pointer-events:none;',
    'padding:4px 8px;border-radius:6px;background:rgba(20,20,20,.9);color:#fff;',
    'font-size:.75rem;line-height:1.3;white-space:nowrap}'
  ].join('');

  function injectStyle() {
    if (doc.getElementById(STYLE_ID)) return;
    var style = doc.createElement('style');
    style.id = STYLE_ID;
    style.setAttribute('data-ic-editor-ui', 'true');
    style.textContent = CSS;
    doc.head.appendChild(style);
  }

  function buildBar() {
    var bar = doc.createElement('div');
    bar.className = 'ic-editor-bar';
    bar.id = 'ic-editor-bar';
    bar.setAttribute('data-ic-editor-ui', 'true');

    var toggle = doc.createElement('button');
    toggle.type = 'button';
    toggle.className = 'ic-editor-toggle';
    toggle.textContent = '编辑';
    toggle.setAttribute('aria-pressed', 'false');
    toggle.addEventListener('click', function () {
      setEditing(!state.editing);
    });

    var undo = doc.createElement('button');
    undo.type = 'button';
    undo.className = 'ic-editor-undo';
    undo.textContent = '撤销';
    undo.disabled = true;
    undo.addEventListener('click', undoLast);

    var save = doc.createElement('button');
    save.type = 'button';
    save.className = 'ic-editor-save';
    save.textContent = '保存';
    save.addEventListener('click', saveDocument);

    bar.appendChild(toggle);
    bar.appendChild(undo);
    bar.appendChild(save);
    doc.body.appendChild(bar);
    state.toggle = toggle;
    state.undo = undo;
  }

  function downloadHtml(html, fileName) {
    var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var link = doc.createElement('a');
    link.href = url;
    link.download = fileName;
    link.style.display = 'none';
    doc.body.appendChild(link);
    link.click();
    doc.body.removeChild(link);
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);
  }

  function saveDocument() {
    /* The delivered file must look read-only on open: savedHtml drops the
     * live editor chrome (bar, panel, tooltip, outline style) and the
     * ic-editing class, while the runtime and data-editable flag stay, so
     * reopening rebuilds exactly one toggle. */
    var html = core.savedHtml(doc.documentElement.outerHTML);
    downloadHtml(html, core.savedFileName(doc.title));
  }

  function updateUndo() {
    if (state.undo) state.undo.disabled = !core.canUndo(state.history);
  }

  function setEditing(on) {
    state.editing = on;
    root.classList.toggle('ic-editing', on);
    if (state.toggle) {
      state.toggle.textContent = on ? '退出编辑' : '编辑';
      state.toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    }
    if (!on) {
      closePanel();
      hideHint();
    }
  }

  function dataBlockFor(slot) {
    var slotId = slot.getAttribute('data-slot');
    return doc.querySelector(
      'script[type="application/json"][data-slot="' + slotId + '"]');
  }

  function readModel(slot) {
    var block = dataBlockFor(slot);
    if (!block) {
      throw new Error('missing data block for slot ' + slot.getAttribute('data-slot'));
    }
    return runtime.parseModel(block.textContent);
  }

  function removeSlotScripts(slot) {
    var block = dataBlockFor(slot);
    if (!block) return;
    var node = slot.nextSibling;
    while (node && node !== block) {
      var next = node.nextSibling;
      if (node.nodeType === 1 && node.tagName === 'SCRIPT') {
        node.parentNode.removeChild(node);
      }
      node = next;
    }
  }

  function currentLanguage() {
    try {
      var saved = localStorage.getItem('lang');
      if (saved === 'zh' || saved === 'en') return saved;
    } catch (error) {
      /* file:// or privacy mode: fall through to the visible pairing. */
    }
    var active = doc.querySelector('[data-lang].active');
    return active ? active.getAttribute('data-lang') : 'zh';
  }

  function applyLanguage(nodes) {
    var language = currentLanguage();
    nodes.forEach(function (node) {
      if (node.nodeType !== 1) return;
      if (node.hasAttribute('data-lang')) {
        node.classList.toggle('active', node.getAttribute('data-lang') === language);
      }
      Array.prototype.forEach.call(node.querySelectorAll('[data-lang]'), function (pair) {
        pair.classList.toggle('active', pair.getAttribute('data-lang') === language);
      });
    });
  }

  function reveal(nodes) {
    var targets = [];
    nodes.forEach(function (node) {
      if (node.nodeType !== 1) return;
      if (node.hasAttribute('data-anim')) targets.push(node);
      Array.prototype.forEach.call(node.querySelectorAll('[data-anim]'), function (item) {
        targets.push(item);
      });
    });
    if (!targets.length) return;
    var show = function () {
      targets.forEach(function (item) {
        item.classList.add('in-view');
      });
    };
    if (typeof requestAnimationFrame === 'function') requestAnimationFrame(show);
    else show();
  }

  function disposeChart(slot) {
    var chart = slot.querySelector('.ic-chart');
    var echarts = typeof globalThis !== 'undefined' ? globalThis.echarts : null;
    if (!chart || !echarts || !echarts.getInstanceByDom) return;
    var instance = echarts.getInstanceByDom(chart);
    if (instance) instance.dispose();
  }

  function replaceSlot(slot, componentId, model) {
    var slotId = slot.getAttribute('data-slot');
    var rendered = runtime.renderSlot(componentId, model, slotId);
    disposeChart(slot);
    removeSlotScripts(slot);

    var template = doc.createElement('template');
    template.innerHTML = rendered.markup;
    var fragment = doc.createDocumentFragment();
    var inserted = [];
    Array.prototype.forEach.call(template.content.childNodes, function (node) {
      var copy = doc.importNode(node, true);
      inserted.push(copy);
      fragment.appendChild(copy);
    });

    var parent = slot.parentNode;
    if (!parent) return;
    parent.insertBefore(fragment, slot);

    /* Imported script nodes are inert, and #22 keeps its sort script inside
     * the section.  Replace every inserted script with a fresh one so both
     * nested and sibling init scripts run after their markup is in the DOM. */
    inserted.forEach(function (node) {
      if (node.nodeType !== 1) return;
      var scripts = node.tagName === 'SCRIPT'
        ? [node]
        : Array.prototype.slice.call(node.querySelectorAll('script'));
      scripts.forEach(function (oldScript) {
        var script = doc.createElement('script');
        for (var index = 0; index < oldScript.attributes.length; index += 1) {
          var attribute = oldScript.attributes[index];
          script.setAttribute(attribute.name, attribute.value);
        }
        script.textContent = oldScript.textContent;
        oldScript.parentNode.replaceChild(script, oldScript);
      });
    });
    applyLanguage(inserted);
    reveal(inserted);

    parent.removeChild(slot);
  }

  function performSwap(slot, model, componentId) {
    if (!slot.isConnected) {
      closePanel();
      return;
    }
    var slotId = slot.getAttribute('data-slot');
    var fromId = Number(slot.getAttribute('data-component'));
    replaceSlot(slot, componentId, model);
    state.history = core.recordPatch(state.history, {
      slotId: slotId,
      from: fromId,
      to: componentId
    });
    updateUndo();
    closePanel();
  }

  function undoLast() {
    var result = core.undo(state.history);
    if (!result) return;
    state.history = result.history;
    updateUndo();
    closePanel();

    var patch = result.patch;
    var slot = doc.querySelector('.ic-slot[data-slot="' + patch.slotId + '"]');
    if (!slot) return;
    try {
      replaceSlot(slot, patch.from, readModel(slot));
    } catch (error) {
      /* A missing data block means the report was hand-edited; leave it alone. */
    }
  }

  function closePanel() {
    if (state.panel && state.panel.parentNode) state.panel.parentNode.removeChild(state.panel);
    if (state.backdrop && state.backdrop.parentNode) {
      state.backdrop.parentNode.removeChild(state.backdrop);
    }
    state.panel = null;
    state.backdrop = null;
  }

  function candidateButton(candidate, slot, model, fromId) {
    var button = doc.createElement('button');
    button.type = 'button';
    button.className = 'ic-editor-candidate';
    button.setAttribute('data-component', String(candidate.id));

    var name = doc.createElement('span');
    name.textContent = candidate.name;
    var badge = doc.createElement('span');
    badge.className = 'ic-editor-badge';
    var family = candidate.family === 'chart' ? '图表族' : '结构族';
    badge.textContent = candidate.crossFamily ? family + ' · 跨族' : family;
    button.appendChild(name);
    button.appendChild(badge);

    button.addEventListener('click', function () {
      if (candidate.crossFamily) showPreview(slot, model, fromId, candidate);
      else performSwap(slot, model, candidate.id);
    });
    return button;
  }

  function showPreview(slot, model, fromId, candidate) {
    var preview = core.mappingPreview(fromId, candidate.id, model);
    var panel = state.panel;
    if (!panel) return;

    var list = panel.querySelector('.ic-editor-list');
    if (list) list.style.display = 'none';
    var actions = panel.querySelector('.ic-editor-actions');
    if (actions) actions.parentNode.removeChild(actions);

    var box = doc.createElement('div');
    box.className = 'ic-editor-preview';
    var title = doc.createElement('p');
    title.innerHTML = '';
    title.textContent = '跨族互换预览：' + preview.from.name + ' → ' + preview.to.name;
    var shows = doc.createElement('p');
    shows.textContent = '将显示：' + (preview.displays.join('、') || '无可用内容');
    var drops = doc.createElement('p');
    drops.textContent = '将丢弃：' + (preview.drops.join('、') || '无');
    box.appendChild(title);
    box.appendChild(shows);
    box.appendChild(drops);
    panel.appendChild(box);

    var footer = doc.createElement('div');
    footer.className = 'ic-editor-actions';
    var cancel = doc.createElement('button');
    cancel.type = 'button';
    cancel.textContent = '取消';
    cancel.addEventListener('click', function () {
      if (box.parentNode) box.parentNode.removeChild(box);
      if (footer.parentNode) footer.parentNode.removeChild(footer);
      if (list) list.style.display = '';
    });
    var confirm = doc.createElement('button');
    confirm.type = 'button';
    confirm.className = 'ic-editor-confirm';
    confirm.textContent = '确认替换';
    confirm.addEventListener('click', function () {
      performSwap(slot, model, candidate.id);
    });
    footer.appendChild(cancel);
    footer.appendChild(confirm);
    panel.appendChild(footer);
  }

  function openPanel(slot) {
    closePanel();
    var model;
    try {
      model = readModel(slot);
    } catch (error) {
      return;
    }
    var fromId = Number(slot.getAttribute('data-component'));
    var candidates = core.candidatesFor(model, fromId);

    var backdrop = doc.createElement('div');
    backdrop.className = 'ic-editor-backdrop';
    backdrop.setAttribute('data-ic-editor-ui', 'true');
    backdrop.addEventListener('click', closePanel);

    var panel = doc.createElement('div');
    panel.className = 'ic-editor-panel';
    panel.setAttribute('data-ic-editor-ui', 'true');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.addEventListener('click', function (event) {
      event.stopPropagation();
    });

    var heading = doc.createElement('h3');
    heading.textContent = '选择替换组件';
    var subtitle = doc.createElement('p');
    subtitle.className = 'ic-editor-sub';
    subtitle.textContent = model.title;
    panel.appendChild(heading);
    panel.appendChild(subtitle);

    if (!candidates.length) {
      var empty = doc.createElement('p');
      empty.className = 'ic-editor-sub';
      empty.textContent = '没有能消费这份数据的候选组件。';
      panel.appendChild(empty);
    } else {
      var list = doc.createElement('div');
      list.className = 'ic-editor-list';
      candidates.forEach(function (candidate) {
        list.appendChild(candidateButton(candidate, slot, model, fromId));
      });
      panel.appendChild(list);
    }

    var actions = doc.createElement('div');
    actions.className = 'ic-editor-actions';
    var close = doc.createElement('button');
    close.type = 'button';
    close.textContent = '关闭';
    close.addEventListener('click', closePanel);
    actions.appendChild(close);
    panel.appendChild(actions);

    doc.body.appendChild(backdrop);
    doc.body.appendChild(panel);
    state.panel = panel;
    state.backdrop = backdrop;
  }

  function showHint(event) {
    hideHint();
    var hint = doc.createElement('div');
    hint.className = 'ic-editor-tooltip';
    hint.setAttribute('data-ic-editor-ui', 'true');
    hint.textContent = HINT_TEXT;
    doc.body.appendChild(hint);
    var left = event.clientX + 12;
    var top = event.clientY + 12;
    var width = hint.offsetWidth || 0;
    var height = hint.offsetHeight || 0;
    if (left + width > window.innerWidth - 8) left = window.innerWidth - width - 8;
    if (top + height > window.innerHeight - 8) top = event.clientY - height - 12;
    hint.style.left = Math.max(8, left) + 'px';
    hint.style.top = Math.max(8, top) + 'px';
    state.hint = hint;
  }

  function hideHint() {
    if (state.hint && state.hint.parentNode) state.hint.parentNode.removeChild(state.hint);
    state.hint = null;
  }

  doc.addEventListener('click', function (event) {
    if (!state.editing) return;
    if (event.target.closest('.ic-editor-panel')) return;
    var slot = event.target.closest('.ic-slot[data-slot]');
    if (!slot) return;
    event.preventDefault();
    event.stopPropagation();
    openPanel(slot);
  });

  doc.addEventListener('mouseover', function (event) {
    if (!state.editing) return;
    var target = event.target.closest('[data-swap="unavailable"]');
    if (!target) {
      hideHint();
      return;
    }
    showHint(event);
  });

  doc.addEventListener('mouseout', function (event) {
    if (!state.editing) return;
    var target = event.target.closest('[data-swap="unavailable"]');
    if (!target) return;
    if (event.relatedTarget && target.contains(event.relatedTarget)) return;
    hideHint();
  });

  doc.addEventListener('keydown', function (event) {
    if (!state.editing) return;
    if (!(event.ctrlKey || event.metaKey) || event.shiftKey) return;
    if (String(event.key).toLowerCase() !== 'z') return;
    var tag = event.target && event.target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || (event.target && event.target.isContentEditable)) {
      return;
    }
    event.preventDefault();
    undoLast();
  });

  injectStyle();
  buildBar();
  updateUndo();
}());
