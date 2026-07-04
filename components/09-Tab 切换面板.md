### 9. Tab 切换面板（替换平铺的多视角罗列）

> **🎯 效果**：左侧纵向药丸 Tab + 右侧内容区。选中 Tab 主题色填充 + 白色文字，未选中灰色描边。内容切换带 `fadeIn` 动画（0.3s）。窄屏自动折叠为顶部横向 Tab 栏。

当需要呈现同一主题的多个视角/维度时，用 Tab 面板替代一次性全部罗列。

### HTML

```html
<div class="tab-panel">
  <div class="tab-nav">
    <button class="tab-btn" data-tab="1" aria-selected="true">视角一</button>
    <button class="tab-btn" data-tab="2" aria-selected="false">视角二</button>
    <button class="tab-btn" data-tab="3" aria-selected="false">视角三</button>
  </div>
  <div class="tab-content">
    <div class="tab-pane active" data-tab="1" role="tabpanel"><p>视角一的内容...</p></div>
    <div class="tab-pane" data-tab="2" role="tabpanel"><p>视角二的内容...</p></div>
    <div class="tab-pane" data-tab="3" role="tabpanel"><p>视角三的内容...</p></div>
  </div>
</div>
```

### CSS

```css
.tab-panel {
  display: flex; gap: 0; margin: 1.5rem 0;
  border: 1px solid var(--border); border-radius: var(--radius, 8px); overflow: hidden;
}
.tab-nav {
  display: flex; flex-direction: column; gap: 4px;
  padding: 0.8em; background: var(--bg);
  border-right: 1px solid var(--border); min-width: 100px;
}
.tab-btn {
  display: block; width: 100%; padding: 0.55em 1em;
  border: 1px solid var(--border); border-radius: 6px;
  background: transparent; color: var(--text); cursor: pointer; text-align: left;
  font-size: 0.88rem; font-weight: 500; min-height: 44px;
  transition: all 0.2s ease;
}
.tab-btn:hover { background: rgba(0,0,0,0.03); }
.tab-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.tab-btn:active { transform: scale(0.97); }
.tab-btn[aria-selected="true"] {
  background: var(--accent); color: var(--accent-text); border-color: var(--accent);
}
.tab-content { flex: 1; padding: 1em 1.2em; background: var(--bg); }
.tab-pane { display: none; }
.tab-pane.active { display: block; animation: tabFadeIn 0.3s ease; }
@keyframes tabFadeIn { from { opacity: 0.4; } to { opacity: 1; } }

@media (max-width: 600px) {
  .tab-panel { flex-direction: column; }
  .tab-nav {
    flex-direction: row; overflow-x: auto;
    border-right: none; border-bottom: 1px solid var(--border); padding: 0.5em;
  }
  .tab-btn { white-space: nowrap; flex-shrink: 0; }
}
```

### JS

```html
<script>
(function(){document.querySelectorAll('.tab-panel').forEach(function(p){
var btns=p.querySelectorAll('.tab-btn');
btns.forEach(function(b){b.addEventListener('click',function(){
var t=this.dataset.tab;
btns.forEach(function(x){x.setAttribute('aria-selected','false');});
this.setAttribute('aria-selected','true');
p.querySelectorAll('.tab-pane').forEach(function(x){x.classList.remove('active');});
var a=p.querySelector('.tab-pane[data-tab="'+t+'"]');if(a)a.classList.add('active');});});});})();
</script>
```

### 布局参数

| 参数 | 值 | 说明 |
|------|-----|------|
| Tab 数 | 2-4 个 | 超过考虑换组件 |
| 方向 | 桌面左侧纵向 / 窄屏顶部横向 | <600px 自动切换 |
| 动画 | `tabFadeIn 0.3s` | `opacity: 0.4 → 1` |

### 降级说明

- **JS 未加载**：第一个 `tab-pane.active` 可见，其余隐藏——至少看到首视角
- **不支持 CSS animation**：直接显示，无淡入效果
