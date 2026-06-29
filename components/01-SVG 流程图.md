### 1. SVG 流程图（替换 ASCII 图）

用 `fireworks-tech-graph` 的 flat-icon style（Style 1）创建彩色流程图。

```
流程：
1. 加载样式参考: references/style-1-flat-icon.md
2. 设计的流程图，viewBox 约 700×N（按节点数量）
3. 颜色语义：
   - 蓝色 (#2563eb / #eff6ff): 资金流、正常经济活动
   - 橙色 (#d97706 / #fff7ed): 触发因素、转折点
   - 红色 (#dc2626 / #fef2f2): 崩溃、负面循环
   - 绿色 (#16a34a / #f0fdf4): 救助、恢复
4. 保存为 lessons/svg/NNNN-slug.svg（保留磁盘文件，便于复用/下载）
5. 验证: python -c "import xml.etree.ElementTree as ET; ET.parse('lessons/svg/NNNN-slug.svg')"
6. SVG 内容**内联**到 HTML 中（而非 `<img>` 引用），用 `<figure class="svg-fig">` 包裹：
```html
<figure class="svg-fig">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 900">
    <!-- 完整 SVG 内容 -->
  </svg>
</figure>
```
内联优势：支持 CSS 变量继承、响应式缩放（viewBox 自动适配）、可被 `<use>` 引用。
```

SVG 模板结构：
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 900">
  <defs>
    <marker id="arrow-{color}" .../>
    <filter id="shadow"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.1"/></filter>
  </defs>
  <style>
    text { font-family: "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", sans-serif; }
    .node-label { font-size: 14px; font-weight: 500; fill: #1e293b; }
    .sub-label { font-size: 12px; font-weight: 400; fill: #64748b; }
  </style>
  <rect width="700" height="900" fill="#ffffff" rx="12"/>
  <!-- ... nodes, arrows, legend ... -->
</svg>
```

关键样式：每个节点是一个 `g` 包裹的圆角 `rect` + 图标 + 标题 + 副标题。每个节点加 drop-shadow。

可复用的 SVG 骨架模板（在 `templates/` 目录下）：
- `templates/flowchart-vertical.svg` — 纵向流程图，填充 {TITLE} {HEIGHT} {LABEL} {DESC}
- `templates/timeline-horizontal.svg` — 横向时间线，适合 4-8 个时间节点
- `templates/cycle-diagram.svg` — 环形循环图，中心+周围 3-6 个节点
- `templates/comparison-side-by-side.svg` — 左右对比图，适合 A vs B 场景

使用方式：复制模板文件，用编辑替换占位符（{TITLE}、{LABEL} 等），按节点数调整 HEIGHT 和间距。

SVG 文字颜色规则（重要）：
- 深色填充盒（`#dc2626`、`#2563eb`、`#16a34a`、`#d97706` 等饱和色）→ 文字用白色 `#fff`
- 浅色填充盒（`#fef2f2`、`#f0fdf4`、`#eff6ff`、`#fff7ed` 等淡色调）→ 文字用深色 `#1e293b` 或 `#7f1d1d`（红色盒）/ `#1e40af`（蓝色盒）/ `#166534`（绿色盒）
- 禁止白色文字（`fill="#fff"`）出现在浅色背景（`#fef2f2` 等）上 → 完全不可读

使用规则：
- 节点数 3-8 个为宜，超过 8 个拆分为多张图
- 始终包含颜色图例（legend），帮助读者理解颜色语义
- 内联 SVG 通过 `viewBox` 自动响应式缩放

降级说明：
- **SVG 内联导致布局溢出**：给 `<svg>` 加 `max-width: 100%; height: auto;` 或改用 `<img src="NNNN-slug.svg">` 外部引用
- **浏览器不支持 SVG**（极旧浏览器）：提示文字或提供 PNG 备选
