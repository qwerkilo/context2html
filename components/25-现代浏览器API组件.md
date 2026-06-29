### 25. 现代浏览器 API 组件（原生折叠 / 原生模态 / 幻灯片 / Popover）

利用现代浏览器（Chrome/Edge/Safari/Firefox）原生支持的 HTML5 API，实现零 JS 依赖或极少 JS 的组件。

#### 25a. 原生折叠（`<details><summary>`）

替代 #08 折叠分步详解。浏览器原生支持展开/收起、可访问性、键盘导航（Enter/Space），无需任何 JS。

颜色语义：
- `summary` 使用 `var(--accent)` 强调色左侧竖条
- 展开时 `details[open]` 改变背景色

HTML 结构：
```html
<div class="native-details" data-anim="fade-up">
  <details class="nd-item" open>
    <summary class="nd-summary"><span class="nd-num">1</span> 步骤标题</summary>
    <div class="nd-body"><p>展开的内容...</p></div>
  </details>
  <details class="nd-item">
    <summary class="nd-summary"><span class="nd-num">2</span> 步骤标题</summary>
    <div class="nd-body"><p>折叠的内容...</p></div>
  </details>
</div>
```

使用规则：
- `open` 属性控制初始展开状态，默认第一项展开
- 每个 `details` 独立开关，互不影响

CSS：
```css
.native-details { margin: 1.5rem 0; border: 1px solid var(--border); border-radius: var(--radius, 8px); overflow: hidden; }
.nd-item + .nd-item { border-top: 1px solid var(--border); }
.nd-summary { display: flex; align-items: center; gap: 0.7em; padding: 0.8em 1em; cursor: pointer; font-size: 0.95rem; font-weight: 500; color: var(--text); background: var(--surface); list-style: none; transition: background 0.2s ease-out; }
.nd-summary::-webkit-details-marker { display: none; }
.nd-summary::after { content: '+'; margin-left: auto; font-size: 1.2rem; color: var(--accent); transition: transform 0.25s ease-out; }
details[open] .nd-summary::after { transform: rotate(45deg); }
.nd-summary:hover { background: color-mix(in srgb, var(--accent) 5%, transparent); }
.nd-num { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: var(--accent); color: var(--accent-text); font-size: 0.8rem; font-weight: 700; flex-shrink: 0; }
details[open] .nd-summary { background: color-mix(in srgb, var(--accent) 8%, transparent); }
.nd-body { padding: 0 1em 1em 3.3em; font-size: 0.92rem; }
```

降级说明：**完全零 JS**。仅不支持 `list-style: none` 和 `::-webkit-details-marker` 的极旧浏览器会显示默认三角箭头，不影响功能。

#### 25b. 原生模态框（`<dialog>`）

替代 #23 全屏模态/灯箱。浏览器的 `<dialog>` 元素提供原生模态：`showModal()` 打开、ESC 关闭、自动焦点锁定、背景不可点击。

HTML 结构：
```html
<button class="dialog-btn" onclick="document.getElementById('dialog-1').showModal()">🔍 查看大图</button>

<dialog class="native-dialog" id="dialog-1" onclick="if(event.target===this)this.close()">
  <div class="nd-content">
    <button class="nd-close" onclick="this.closest('dialog').close()" aria-label="关闭">
      <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M5 5l10 10M15 5l-10 10"/></svg>
    </button>
    <img src="full-image.png" alt="大图">
  </div>
</dialog>
```

使用规则：
- 使用 `onclick="...showModal()"` 无需额外 JS
- 使用 `onclick="...close()"` 关闭
- ESC 键自动关闭（桌面端）
- 点击遮罩关闭：`<dialog onclick="if(event.target===this)this.close()">`（移动端无法按 ESC，必须加此逻辑）
- 关闭按钮始终保留，兼容所有设备

CSS：
```css
.native-dialog { border: none; border-radius: var(--radius, 8px); padding: 0; max-width: 90vw; max-height: 85vh; background: transparent; }
.native-dialog::backdrop { background: rgba(0,0,0,0.75); }
.nd-content { position: relative; display: flex; flex-direction: column; align-items: flex-end; }
.nd-content img { max-width: 100%; max-height: 80vh; border-radius: 4px; display: block; }
.nd-close { position: absolute; top: -2em; right: 0; background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; padding: 0.3em; opacity: 0.8; transition: opacity 0.2s; }
.nd-close:hover { opacity: 1; }
```

降级说明：
- **不支持 `<dialog>`**（IE11）：退化为普通内部内容显示
- **不支持 `::backdrop`**：无遮罩效果，模态框直接显示

#### 25c. CSS Scroll Snap 幻灯片

适合展示多张图片/卡片的轮播效果。纯 CSS 滑动吸附，无 JS。

HTML 结构：
```html
<div class="snap-scroll" data-anim="fade-up">
  <div class="ss-track">
    <div class="ss-slide" style="background:var(--accent);">幻灯片 1</div>
    <div class="ss-slide" style="background:var(--success);">幻灯片 2</div>
    <div class="ss-slide" style="background:var(--warning);">幻灯片 3</div>
    <div class="ss-slide" style="background:var(--error);">幻灯片 4</div>
  </div>
  <div class="ss-dots">
    <span class="ss-dot"></span>
    <span class="ss-dot"></span>
    <span class="ss-dot"></span>
    <span class="ss-dot"></span>
  </div>
</div>
```

使用规则：
- 幻灯片 3-8 张为宜
- 每张幻灯片宽高比推荐 16:9
- 支持鼠标拖拽和触摸滑动

CSS：
```css
.snap-scroll { margin: 1.5rem 0; }
.ss-track { display: flex; gap: 1em; overflow-x: auto; -webkit-overflow-scrolling: touch; scroll-snap-type: x mandatory; }
.ss-slide { min-width: 85%; min-height: 200px; border-radius: var(--radius, 8px); display: flex; align-items: center; justify-content: center; color: #fff; font-size: 1.2rem; font-weight: 600; scroll-snap-align: start; flex-shrink: 0; padding: 2em; }
```

#### 25d. Popover 提示（`popover` 属性）

使用 HTML `popover` 属性创建轻量级弹出提示。点击触发按钮弹出/收起，点击外部自动关闭。

HTML 结构：
```html
<button class="popover-trigger" popovertarget="pop-1">💡 什么是 MMT？</button>
<div id="pop-1" class="popover-box" popover>
  <p>现代货币理论（MMT）是一种认为主权货币发行国不会破产的非主流经济理论。</p>
</div>
```

使用规则：
- `popovertarget` 属性关联触发按钮和目标面板
- `popover` 属性声明弹出面板
- 点击外部区域自动关闭，无需 JS

CSS：
```css
.popover-trigger { display: inline; padding: 0.1em 0.4em; border: 1px dashed var(--accent); border-radius: 4px; background: transparent; color: var(--accent); cursor: pointer; font-size: inherit; font-family: inherit; }
.popover-box { border: 1px solid var(--border); border-radius: var(--radius, 8px); padding: 0.8em 1em; max-width: 280px; background: var(--bg); box-shadow: var(--shadow-sm, 0 2px 8px rgba(0,0,0,0.08)); font-size: 0.85rem; line-height: 1.5; }
.popover-box::backdrop { background: transparent; }
```

降级说明：
- **不支持 `popover`**（Firefox < 125）：按钮不可点击，内容不可见。确保弹出内容不是理解正文的必要前提。
- **不支持 `::backdrop`**：无影响
