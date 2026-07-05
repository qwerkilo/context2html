---
id: 3
name: CSS 时间线
dependencies: []
compat_types:
- report
- article
- tutorial
requires_3d: false
---

### 3. CSS 时间线（替换事件表格）

> **🎯 效果**：左侧竖线 + 圆点里程碑 + 日期 + 描述。关键事件放大圆点（22px），悬停时圆点发光放大。纯 CSS，无 JS。

当需要展示时间顺序的事件序列（5-10 个）时，用竖直时间线替代 HTML 表格或编号列表。

### CSS

```css
.timeline {
  position: relative; padding: 1em 0; margin: 1.5rem 0;
}
.timeline::before {
  content: ''; position: absolute; left: 18px; top: 0; bottom: 0;
  width: 2px; background: var(--border);
}
.tl-item { position: relative; padding: 0.6em 0 0.6em 3em; }
.tl-dot {
  position: absolute; left: 10px; width: 18px; height: 18px; border-radius: 50%;
  background: var(--accent); border: 3px solid var(--bg); z-index: 1;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.tl-item:hover .tl-dot {
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 25%, transparent);
  transform: scale(1.15);
}
.tl-dot.major {
  width: 22px; height: 22px; left: 8px;
}
.tl-date { font-size: 0.8rem; font-weight: 700; color: var(--accent); }
.tl-desc { font-size: 0.9rem; margin-top: 0.1em; color: var(--text); }
```

### HTML

```html
<div class="timeline">
  <div class="tl-item">
    <div class="tl-dot"></div>
    <div class="tl-date">2006 年中</div>
    <div class="tl-desc">事件描述</div>
  </div>
  <div class="tl-item">
    <div class="tl-dot major"></div>
    <div class="tl-date">2008 年 9 月</div>
    <div class="tl-desc">⚠️ 关键事件（放大圆点）</div>
  </div>
  <div class="tl-item">
    <div class="tl-dot"></div>
    <div class="tl-date">2009 年初</div>
    <div class="tl-desc">事件描述</div>
  </div>
</div>
```

### 布局参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 圆点直径 | 18px / 关键 22px | `.tl-dot` / `.tl-dot.major` |
| 竖线 | 2px `var(--border)` | `::before` 伪元素 |
| 悬停反馈 | 发光环 + 缩放 1.15× | 0.2s ease 过渡 |

### 使用规则

- 事件 **≥ 5** 个时使用，少于用编号列表
- 关键事件加 `.tl-dot.major`（圆点 22px）
- 日期用 `var(--accent)` 自动跟随主题

### 降级说明

- **窄屏跑偏**：`.tl-dot` 用 `position: absolute` + `left` 固定，父容器 `.timeline` 不设 `overflow: hidden`
- **最后一个事件超出容器**：`.timeline` 底部 `padding` 留够 1em
