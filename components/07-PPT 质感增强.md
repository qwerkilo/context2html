### 7. PPT 质感增强（纵向滚读 + 动画 + 主题切换）

> **🎯 效果**：20 主题切换（T 键循环 + 工具栏面板 + localStorage 持久化）、滚动入场动画（fade-up / fade / slide-left / blur 四种模式）、← → 键章节导航、浮动 TOC。所有能力内置在 `report-starter.html` 模板中。

在保持纵向滚读结构的基础上，添加 PPT 级的视觉品质。以下能力已内置在模板中（CSS + JS）。

#### 7.1 主题切换（T 键 + localStorage 持久化）

键盘按 `T` 键循环切换主题。所有主题 CSS 变量集中管理在 `theme/report-themes.css`（自动生成，禁止手改）。用户选择的主题自动保存到 `localStorage`，刷新页面后保留。

主题列表（20 个）：`warm`, `apple`, `minimax`, `nvidia`, `spotify`, `tesla`, `airbnb`, `airtable`, `binance`, `bmw-m`, `claude`, `cursor`, `dell-1996`, `figma`, `hp`, `ibm`, `nike`, `notion`, `x.ai`, `zapier`

完整实现见 `templates/report-starter.html` 的 JS 块（`tp-btn-toggle` 打开面板 → `tp-item` 主题选择 → T 键切换 + localStorage 持久化）。

主题 CSS 变更时运行 `python scripts/generate-theme-css.py` 重新生成。

#### 7.2 入场动画（滚动触发）

使用 IntersectionObserver 实现元素进入视口时播放动画。

```css
[data-anim] { opacity: 0; transform: translateY(var(--anim-y, 24px)); transition: opacity var(--anim-dur, 0.3s) ease-out, transform var(--anim-dur, 0.3s) ease-out; }
[data-anim].in-view { opacity: 1; transform: translateY(0); }
[data-anim="fade"] { transform: none; }
[data-anim="slide-left"] { transform: translateX(calc(var(--anim-y, 24px) * -1)); }
[data-anim="slide-left"].in-view { transform: translateX(0); }
@media (prefers-reduced-motion: reduce) { [data-anim] { opacity: 1; transform: none; transition: none; } }
```

需要动画的元素加 `data-anim="fade-up"`。JS：

```js
const obs = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) e.target.classList.add('in-view');
}));
document.querySelectorAll('[data-anim]').forEach(el => obs.observe(el));
```

使用规则：
- **h2 标题**：总是加 `data-anim="fade-up"`（进入视口时从下方滑入）
- **SVG 图 / 时间线 / 条形图**：总是加 `data-anim="fade-up"`
- **对比表**：加 `data-anim="fade"`
- **段落文本**：不加（太多段落同时动画反而眼花）
- 前 2 个视觉元素不用动画（首屏元素已在视口内）

#### 7.3 键盘章节导航（← → 键）

按 ← → 键跳转到上一个/下一个 h2 标题。

```js
document.addEventListener('keydown', e => {
  if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && !e.ctrlKey && !e.metaKey) {
    e.preventDefault();
    const sections = document.querySelectorAll('h2');
    const current = [...sections].findIndex(h2 => {
      const rect = h2.getBoundingClientRect();
      return rect.top >= 0 && rect.top < window.innerHeight / 2;
    });
    const next = e.key === 'ArrowRight' ? Math.min(current + 1, sections.length - 1) : Math.max(current - 1, 0);
    if (next >= 0 && sections[next]) sections[next].scrollIntoView({ behavior: 'smooth' });
  }
});
```

#### 7.4 内容密度规范（区别于纯 PPT）

纵向滚读的报告每屏要有"视觉呼吸"：
- 每两个 h2 之间至少插入 1 个视觉组件（SVG / 时间线 / 条形图 / 对比表）
- 连续文本不超过 4 段
- 段落中不使用过多的引用或信息框——每个 `.info-box` / `.warning-box` 之间至少隔 1 段
- 一个标准的 h2 章节体量："1-2 段引出 → 视觉组件 → 1-2 段深化"

#### 7.5 主题选择器按钮（UI 方式切换，替代纯键盘）

在页面右下角添加一个浮动的主题选择器。点击 <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="8"/><circle cx="10" cy="7" r="2" fill="currentColor"/><path d="M4 15l4-4"/></svg> 按钮打开主题面板，显示所有主题的名称和色点，当前主题高亮。比 19 个小圆点更易用。

HTML（放在 `<body>` 末尾，JS 之前）——使用组合工具栏（<svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="8"/><circle cx="10" cy="7" r="2" fill="currentColor"/><path d="M4 15l4-4"/></svg> 主题按钮 + <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 5h14M3 10h14M3 15h10"/></svg> 目录按钮）：
```html
<div class="ui-toolbar">
  <button class="tp-btn-toggle" aria-label="切换主题" title="切换主题"><svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="10" cy="10" r="8"/><circle cx="10" cy="7" r="2" fill="currentColor"/><path d="M4 15l4-4"/></svg></button>
  <button class="toc-btn" aria-label="目录" title="目录"><svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 5h14M3 10h14M3 15h10"/></svg></button>
</div>
<nav class="tp-panel">
  <div class="tp-grid" role="listbox" aria-label="选择主题">
    <button class="tp-item active" data-theme="warm" style="--tp-color:#c0392b;">暖色</button>
    <button class="tp-item" data-theme="apple" style="--tp-color:#0066cc;">Apple</button>
    <button class="tp-item" data-theme="minimax" style="--tp-color:#0a0a0a;">Minimax</button>
    <button class="tp-item" data-theme="nvidia" style="--tp-color:#76b900;">NVIDIA</button>
    <button class="tp-item" data-theme="spotify" style="--tp-color:#1ed760;">Spotify</button>
    <button class="tp-item" data-theme="tesla" style="--tp-color:#3e6ae1;">Tesla</button>
    <button class="tp-item" data-theme="airbnb" style="--tp-color:#ff385c;">Airbnb</button>
    <button class="tp-item" data-theme="airtable" style="--tp-color:#181d26;">Airtable</button>
    <button class="tp-item" data-theme="binance" style="--tp-color:#fcd535;">Binance</button>
    <button class="tp-item" data-theme="bmw-m" style="--tp-color:#ffffff;">BMW M</button>
    <button class="tp-item" data-theme="claude" style="--tp-color:#cc785c;">Claude</button>
    <button class="tp-item" data-theme="cursor" style="--tp-color:#f54e00;">Cursor</button>
    <button class="tp-item" data-theme="dell-1996" style="--tp-color:#e91d2a;">Dell 1996</button>
    <button class="tp-item" data-theme="figma" style="--tp-color:#000000;">Figma</button>
    <button class="tp-item" data-theme="hp" style="--tp-color:#024ad8;">HP</button>
    <button class="tp-item" data-theme="ibm" style="--tp-color:#0f62fe;">IBM</button>
    <button class="tp-item" data-theme="nike" style="--tp-color:#111111;">Nike</button>
    <button class="tp-item" data-theme="notion" style="--tp-color:#5645d4;">Notion</button>
    <button class="tp-item" data-theme="x.ai" style="--tp-color:#ffffff;">x.ai</button>
    <button class="tp-item" data-theme="zapier" style="--tp-color:#ff4f00;">Zapier</button>
  </div>
</nav>
<nav class="toc-panel"><ul class="toc-list"></ul></nav>
```

CSS（放在报告 `<style>` 中）——工具栏 + 主题面板 + TOC 共用样式：
```css
.ui-toolbar { position: fixed; bottom: 20px; right: 20px; z-index: 999; display: flex; align-items: center; gap: 8px; padding: 6px 12px; background: var(--surface); backdrop-filter: blur(6px); border-radius: 20px; box-shadow: var(--shadow-sm); }
.tp-btn-toggle, .toc-btn { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 0 2px; line-height: 1; opacity: 0.6; transition: opacity 0.2s ease; color: var(--text); }
.tp-btn-toggle:hover, .toc-btn:hover { opacity: 1; }
.tp-panel { position: fixed; bottom: 70px; right: 20px; z-index: 998; background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.6em; box-shadow: var(--shadow-md); display: none; max-height: 50vh; overflow-y: auto; }
.tp-panel.open { display: block; }
.tp-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px; min-width: 180px; }
.tp-item { display: flex; align-items: center; gap: 6px; padding: 0.4em 0.6em; border: 1px solid transparent; border-radius: 6px; background: none; cursor: pointer; font-size: 0.82rem; color: var(--text); text-align: left; transition: background 0.15s ease; }
.tp-item:hover { background: color-mix(in srgb, var(--text) 6%, transparent); }
.tp-item.active { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 8%, transparent); font-weight: 600; }
.tp-item::before { content: ''; width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; background: var(--tp-color); border: 1px solid var(--border); }
.toc-btn { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 0 2px; line-height: 1; opacity: 0.6; transition: opacity 0.2s ease; color: var(--text); }
.toc-btn:hover { opacity: 1; }
.toc-panel { position: fixed; bottom: 70px; right: 20px; z-index: 998; background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.6em 0; box-shadow: var(--shadow-md); max-height: 50vh; overflow-y: auto; display: none; min-width: 160px; }
.toc-panel.open { display: block; }
.toc-list { list-style: none; margin: 0; padding: 0; }
.toc-item { padding: 0.4em 1em; font-size: 0.82rem; cursor: pointer; color: var(--muted); transition: color 0.15s ease, background 0.15s ease; }
.toc-item:hover { background: color-mix(in srgb, var(--text) 4%, transparent); color: var(--text); }
.toc-item.active { color: var(--accent); font-weight: 600; background: color-mix(in srgb, var(--accent) 4%, transparent); }
```

JS（在 PPT 运行时模板中整合）——主题选择器 + TOC 处理：
```js
try{document.querySelectorAll('.tp-btn').forEach(function(b){b.addEventListener('click',function(){
var th=this.dataset.theme;d.dataset.theme=th;i=t.indexOf(th);
document.querySelectorAll('.tp-btn').forEach(function(x){x.classList.toggle('active',x.dataset.theme===th);});});});
}catch(e){}
try{var tl=document.querySelector('.toc-list');if(tl){var h2s=document.querySelectorAll('h2');
h2s.forEach(function(h,i){var li=document.createElement('li');li.className='toc-item';li.textContent=h.textContent;
li.addEventListener('click',function(){h.scrollIntoView({behavior:'smooth'});
document.querySelector('.toc-panel').classList.remove('open');});tl.appendChild(li);});
document.querySelector('.toc-btn').addEventListener('click',function(){
document.querySelector('.toc-panel').classList.toggle('open');});
var to=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){
var idx=Array.from(h2s).indexOf(e.target);
document.querySelectorAll('.toc-item').forEach(function(x,i){x.classList.toggle('active',i===idx);});}});},
{rootMargin:'-80px 0px -60% 0px'});h2s.forEach(function(h){to.observe(h);});
document.addEventListener('click',function(e){if(!e.target.closest('.ui-toolbar')&&!e.target.closest('.toc-panel')){
document.querySelector('.toc-panel').classList.remove('open');}});}
}catch(e){}

#### 7.6 JS 运行时模板

报告末尾的 `<script>` 块追加：

```html
<script>
// PPT 质感增强 — 含降级处理
(function(){var t=['warm','apple','minimax','nvidia','spotify','tesla','airbnb','airtable','binance','bmw-m','claude','cursor','dell-1996','figma','hp','ibm','nike','notion','x.ai','zapier'];try{var s=localStorage.getItem('theme');if(s&&t.indexOf(s)>-1){document.documentElement.dataset.theme=s;}}catch(e){}
var i=t.indexOf(document.documentElement.dataset.theme);if(i<0)i=0;var d=document.documentElement;
try{document.querySelectorAll('.tp-item').forEach(function(b){b.addEventListener('click',function(){
var th=this.dataset.theme;d.dataset.theme=th;i=t.indexOf(th);
try{localStorage.setItem('theme',th);}catch(e){}
document.querySelectorAll('.tp-item').forEach(function(x){x.classList.toggle('active',x.dataset.theme===th);});
document.querySelector('.tp-panel').classList.remove('open');});});
}catch(e){}
try{document.querySelector('.tp-btn-toggle').addEventListener('click',function(){
document.querySelector('.tp-panel').classList.toggle('open');});
}catch(e){}
try{document.addEventListener('keydown',function(e){if(e.key==='t'&&!e.ctrlKey&&!e.metaKey){i=(i+1)%t.length;d.dataset.theme=t[i];
try{localStorage.setItem('theme',t[i]);}catch(e){}
document.querySelectorAll('.tp-item').forEach(function(x){x.classList.toggle('active',x.dataset.theme===t[i]);});}});
}catch(e){} // 主题切换降级：静默失败
// 点击外部关闭主题面板
try{document.addEventListener('click',function(e){if(!e.target.closest('.ui-toolbar')&&!e.target.closest('.tp-panel')){
document.querySelector('.tp-panel').classList.remove('open');}});
}catch(e){}
try{var tl=document.querySelector('.toc-list');if(tl){var h2s=document.querySelectorAll('h2');
h2s.forEach(function(h,i){var li=document.createElement('li');li.className='toc-item';li.textContent=h.textContent;
li.addEventListener('click',function(){h.scrollIntoView({behavior:'smooth'});
document.querySelector('.toc-panel').classList.remove('open');});tl.appendChild(li);});
document.querySelector('.toc-btn').addEventListener('click',function(){
document.querySelector('.toc-panel').classList.toggle('open');});
var to=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){
var idx=Array.from(h2s).indexOf(e.target);
document.querySelectorAll('.toc-item').forEach(function(x,i){x.classList.toggle('active',i===idx);});}});},
{rootMargin:'-80px 0px -60% 0px'});h2s.forEach(function(h){to.observe(h);});
document.addEventListener('click',function(e){if(!e.target.closest('.ui-toolbar')&&!e.target.closest('.toc-panel')){
document.querySelector('.toc-panel').classList.remove('open');}});}
}catch(e){} // 浮动目录降级：静默失败
try{var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)e.target.classList.add('in-view');});});
document.querySelectorAll('[data-anim]').forEach(function(el){o.observe(el);});
}catch(e){document.querySelectorAll('[data-anim]').forEach(function(el){el.style.opacity='1';el.style.transform='none';});
} // IntersectionObserver 降级：直接显示所有元素
try{var s=document.querySelectorAll('h2');
document.addEventListener('keydown',function(e){if((e.key==='ArrowRight'||e.key==='ArrowLeft')&&!e.ctrlKey&&!e.metaKey){e.preventDefault();
var c=Array.from(s).findIndex(function(h){var r=h.getBoundingClientRect();return r.top>=0&&r.top<window.innerHeight/2;});
var n=e.key==='ArrowRight'?Math.min(c+1,s.length-1):Math.max(c-1,0);if(n>=0&&s[n])s[n].scrollIntoView({behavior:'smooth'});
}});}catch(e){} // 键盘导航降级：静默失败
})();
</script>
```

降级说明：
- **IntersectionObserver 不支持的浏览器**（IE11、旧 Safari）：catch 块将所有 `[data-anim]` 元素的 opacity 设为 1、transform 取消，用户看到的是静态完整页面
- **smooth scroll 不支持**：浏览器自动降级为 instant scroll
- **T 键切主题不支持**：静默失败，用户停留在默认主题
- 降级设计的核心原则：**JS 增强不影响基本可用性**——所有降级情况下，报告内容仍然是完整可读的

/* ===== 主题切换过渡动画 ===== */
body { transition: background-color 0.35s ease-out, color 0.35s ease-out; }
body, body * { transition: background-color 0.35s ease-out, color 0.35s ease-out, border-color 0.35s ease-out, box-shadow 0.35s ease-out; }
@media (prefers-reduced-motion: reduce) { body, body * { transition: none !important; } }
