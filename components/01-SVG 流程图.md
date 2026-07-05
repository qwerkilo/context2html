---
id: 1
name: SVG 流程图
dependencies: []
compat_types:
- report
- article
- doc
- tutorial
requires_3d: false
---

### 1. SVG 流程图（替换 ASCII 图）

> **🎯 效果**：彩色 SVG 流程图，节点带圆角矩形 + 阴影 + 箭头连线，颜色语义统一（蓝=资金流、橙=触发、红=崩溃、绿=恢复），节点内包含图标+标题+副标题，适配主题色。

用 `fireworks-tech-graph` 的 flat-icon style 创建。保存为独立 `.svg` 文件后内联到 HTML 中（而非 `<img>` 引用），用 `<figure class="svg-fig">` 包裹。

### 流程

1. 加载样式参考 `references/style-1-flat-icon.md`
2. 设计流程图，viewBox 约 700×N（按节点数量）
3. 颜色语义固定：
   - 🟦 **蓝色** (#2563eb / #eff6ff): 资金流、正常经济活动
   - 🟧 **橙色** (#d97706 / #fff7ed): 触发因素、转折点
   - 🟥 **红色** (#dc2626 / #fef2f2): 崩溃、负面循环
   - 🟩 **绿色** (#16a34a / #f0fdf4): 救助、恢复
4. 保存为独立 SVG 文件（保留磁盘文件便于复用）
5. 验证 XML：`python -c "import xml.etree.ElementTree as ET; ET.parse('path/to/your.svg')"`
6. 内联到 HTML

### SVG 模板结构

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

### 内联包裹结构

```html
<figure class="svg-fig">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 900">
    <!-- 完整 SVG 内容 -->
  </svg>
</figure>
```

### 可用模板

| 文件 | 用途 | 占位符 |
|------|------|--------|
| `templates/flowchart-vertical.svg` | 纵向流程图 | {TITLE} {HEIGHT} {LABEL} {DESC} |
| `templates/timeline-horizontal.svg` | 横向时间线，4-8 节点 | 同上 |
| `templates/cycle-diagram.svg` | 环形循环图，中心+周围 3-6 节点 | 同上 |
| `templates/comparison-side-by-side.svg` | 左右对比，A vs B | 同上 |

### SVG 文字颜色规则

| 填充背景 | 文字颜色 | 示例 |
|----------|---------|------|
| 饱和色（`#dc2626`、`#2563eb` 等） | `#fff` 白色 | 红/蓝/绿/橙色盒 |
| 淡色调（`#fef2f2`、`#eff6ff` 等） | `#1e293b` 深灰 | 浅红/浅蓝/浅绿/浅橙盒 |

### 使用规则

- 节点数 **3-8** 个，超过拆分多张图
- 始终包含颜色图例（legend）
- 内联 SVG 通过 `viewBox` 自动响应式缩放

### 降级说明

- **SVG 内联导致布局溢出**：给 `<svg>` 加 `max-width: 100%; height: auto;`
- **浏览器不支持 SVG**：提供 PNG 备选或文字说明
