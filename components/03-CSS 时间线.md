### 3. CSS 时间线（替换事件表格）

用纯 CSS 竖直时间轴替代 HTML 表格中的事件列表：

```css
.timeline { position: relative; padding: 1em 0; margin: 1.5rem 0; }
.timeline::before {
  content: ''; position: absolute; left: 18px; top: 0; bottom: 0;
  width: 2px; background: #d0d0d0;
}
.tl-item { position: relative; padding: 0.6em 0 0.6em 3em; }
.tl-dot {
  position: absolute; left: 10px; width: 18px; height: 18px; border-radius: 50%;
  background: #c0392b; border: 3px solid #faf9f7; z-index: 1;
}
.tl-dot.major { width: 22px; height: 22px; left: 8px; } /* 关键事件的强调圆点 */
.tl-date { font-size: 0.8rem; font-weight: 700; color: #c0392b; }
.tl-desc { font-size: 0.9rem; margin-top: 0.1em; }
```

HTML 结构：
```html
<div class="timeline">
  <div class="tl-item">
    <div class="tl-dot"></div>
    <div class="tl-date">2006 年中</div>
    <div class="tl-desc">事件描述</div>
  </div>
  ...
</div>
```

使用规则：
- 事件 ≥ 5 个时使用，少于 5 个用编号列表或段落
- 关键事件加 `.tl-dot.major`（圆点放大 22px）
- 日期用强调色 `#c0392b`，随主题切换自动变化（使用 `var(--accent)`）

降级说明：
- **窄屏跑偏**：确保 `.tl-dot` 使用 `position: absolute` + `left` 固定，父容器 `.timeline` 不设 `overflow: hidden`
- **最后一个事件超出容器**：`.timeline` 底部 `padding` 留够 1em 以上
