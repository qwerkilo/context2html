---
id: 4
name: CSS 条形图
dependencies: []
compat_types:
- report
- article
- doc
requires_3d: false
---

### 4. CSS 条形图（替换纯文本统计）

> **🎯 效果**：水平条形图，左侧标签 + 彩色填充条 + 右侧数值。条带圆角（3px），填充色语义化（蓝=正常、橙=触发、红=负面、绿=正面）。条宽动画 `transition: width 1s ease`。

当需要展示数据对比时，用水平条形图让数字"可见"。

### CSS

```css
.bar-chart { margin: 1.2rem 0; }
.bar-item { display: flex; align-items: center; margin: 0.5em 0; }
.bar-label {
  width: 100px; flex-shrink: 0; font-size: 0.85rem;
  text-align: right; padding-right: 0.8em; color: var(--muted);
}
.bar-track {
  flex: 1; height: 1.6em; background: var(--surface);
  border-radius: 3px; overflow: hidden;
}
.bar-fill {
  height: 100%; border-radius: 3px; display: flex; align-items: center;
  padding: 0 0.5em; font-size: 0.8rem; color: var(--accent-text); font-weight: 600;
  min-width: 2.5em; justify-content: flex-end;
  transition: width 1s ease;
}
```

### HTML

```html
<div class="bar-chart">
  <div class="bar-item" data-anim="fade-up">
    <div class="bar-label">类别 A</div>
    <div class="bar-track">
      <div class="bar-fill" style="width:85%; background:#3b82f6;">85</div>
    </div>
  </div>
  <div class="bar-item" data-anim="fade-up">
    <div class="bar-label">类别 B</div>
    <div class="bar-track">
      <div class="bar-fill" style="width:60%; background:#f59e0b;">60</div>
    </div>
  </div>
  <div class="bar-item" data-anim="fade-up">
    <div class="bar-label">类别 C</div>
    <div class="bar-track">
      <div class="bar-fill" style="width:35%; background:#ef4444;">35</div>
    </div>
  </div>
</div>
```

### 布局参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 标签宽度 | 100px | `<600px` 窄屏自动 80px |
| 条高 | 1.6em | `min-width: 2.5em` 确保短条数值可见 |
| 动画 | `width 1s ease` | 配合 `data-anim` 进入视口触发 |

### 使用规则

- 数据先归一化到最大值，等比换算为百分比
- 颜色语义：🟦 蓝=正常 🟧 橙=触发 🟥 红=负面 🟩 绿=正面
- `min-width: 2.5em` 确保短条也有数值可见

### 降级说明

- **数值溢出条形**：加 `text-overflow: ellipsis` 截断
- **窄屏标签溢出**：`.bar-label` 设为 80px 或允许换行
