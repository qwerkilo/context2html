---
title: context2html 页面类型参考
description: 报告模板中可用的 9 种页面类型及完整代码示例
---

# context2html 页面类型参考

## 0. 报告整体结构模板

一份完整 report.html 的 HTML 骨架，按顺序组合所有页面类型：

```html
<!DOCTYPE html>
<html data-theme="warm">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告标题</title>
  <!-- 主题 CSS（20 套主题，通过 T 键切换，由 theme/report-themes.css 管理） -->
  <link href="../theme/report-themes.css" rel="stylesheet">
  <style>
    /* ===== 通用布局 ===== */
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; background: var(--bg); color: var(--text); line-height: 1.7; font-variant-numeric: tabular-nums; }
    *:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    article, section, aside, nav, footer { margin: 3rem 0; }

    /* ===== 封面 ===== */
    .cover-page { position: relative; min-height: 70vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow: hidden; padding: 4rem 2rem; }
    .noise-overlay { position: absolute; inset: 0; pointer-events: none; }
    .noise-overlay svg { width: 100%; height: 100%; display: block; }
    .cover-badge { display: inline-block; padding: 0.3em 1em; border: 1px solid var(--accent); border-radius: 20px; font-size: 0.8rem; letter-spacing: 0.05em; margin-bottom: 1.5rem; }
    .shiny-text { background: linear-gradient(90deg, var(--accent), #fff, var(--accent)); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s ease-in-out infinite; }
    @keyframes shimmer { 0%,100% { background-position: 200% 0; } 50% { background-position: -200% 0; } }
    .cover-page h1 { font-size: 2.8rem; font-weight: 700; margin: 0.3em 0; line-height: 1.2; letter-spacing: -0.02em; }
    .cover-subtitle { font-size: 1rem; color: var(--muted); margin: 0.5em 0 1.5em; }
    .cover-hook { font-size: 0.85rem; color: var(--muted); }

    /* ===== 执行摘要 ===== */
    .exec-summary { margin: 2rem 0; padding: 1.5rem 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
    .exec-summary-item { display: flex; align-items: flex-start; gap: 0.8rem; margin: 1em 0; font-size: 0.95rem; }
    .exec-summary-item::before { content: '\25C6'; color: var(--accent); font-size: 0.7rem; flex-shrink: 0; margin-top: 0.3em; }

    /* ===== 关键数字 ===== */
    .key-numbers { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin: 2rem 0; }
    .kn-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem 1rem; text-align: center; transition: transform 0.2s; }
    .kn-card:hover { transform: translateY(-2px); }
    .kn-number { display: block; font-size: 2.2rem; font-weight: 700; color: var(--accent); line-height: 1.2; }
    .kn-label { display: block; font-size: 0.82rem; color: var(--muted); margin-top: 0.4em; }

    /* ===== 目录 ===== */
    .report-toc { margin: 2rem 0; padding: 1.5rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
    .report-toc ol { margin: 0; padding-left: 1.5em; }
    .report-toc li { margin: 0.5em 0; font-size: 0.9rem; }
    .report-toc a { color: var(--link); text-decoration: none; }
    .report-toc a:hover { opacity: 0.7; text-decoration: underline; }

    /* ===== 章节正文 ===== */
    .report-chapter { margin: 3rem 0; }
    .report-chapter h2 { font-size: 1.6rem; margin-bottom: 1rem; border-bottom: 2px solid var(--border); padding-bottom: 0.4em; }
    .report-chapter p { margin: 1em 0; }

    /* ===== 对比分析 ===== */
    .comparison-page { margin: 3rem 0; }

    /* ===== 结论与建议 ===== */
    .conclusion-page { margin: 3rem 0; padding: 1.5rem 2rem; background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: var(--radius); }
    .ccl-item { display: flex; align-items: flex-start; gap: 0.8rem; margin: 1em 0; font-size: 0.95rem; }
    .ccl-item::before { content: '\2192'; color: var(--accent); font-weight: bold; flex-shrink: 0; }

    /* ===== 附录 + 脚注 ===== */
    .appendix { margin: 3rem 0; padding: 1.5rem 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); font-size: 0.9rem; }
    .report-footer { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.78rem; color: var(--muted); text-align: center; }
  </style>
</head>
<body>

  <!-- ===== 封面页 ===== -->
  <article class="cover-page">...</article>

  <!-- ===== 执行摘要 ===== -->
  <section class="exec-summary">...</section>

  <!-- ===== 关键数字页 ===== -->
  <section class="key-numbers">...</section>

  <!-- ===== 目录页 ===== -->
  <nav class="report-toc">...</nav>

  <!-- ===== 章节正文 ===== -->
  <section class="report-chapter" id="ch1">...</section>
  <section class="report-chapter" id="chN">...</section>

  <!-- ===== 对比分析 ===== -->
  <section class="comparison-page">...</section>

  <!-- ===== 结论与建议 ===== -->
  <aside class="conclusion-page">...</aside>

  <!-- ===== 附录 + 脚注 ===== -->
  <section class="appendix">...</section>
  <footer class="report-footer">...</footer>

  <!-- PPT 质感 JS 已内置于 report-starter.html 模板中 -->
</body>
</html>
```

---

## 1. 封面页

报告标题页，包含摘要行 + 元数据。**密度：稀疏** — 留白多、视觉呼吸感强，适合作为进入报告的仪式感入口。

**推荐配合组件：** PPT 质感增强 #7（流星动画 + 主题切换已内置在模板中），无需额外视觉组件穿插。

```html
<article class="cover-page">
  <div class="noise-overlay">
    <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
      <filter id="noise-filter"><feTurbulence type="fractalNoise" baseFrequency="0.4" numOctaves="6" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope="0.15"/><feFuncG type="linear" slope="0.15"/><feFuncB type="linear" slope="0.15"/></feComponentTransfer></filter>
      <rect width="100%" height="100%" filter="url(#noise-filter)" opacity="1"/>
    </svg>
  </div>
  <div class="cover-badge shiny-text" data-lang="zh">调研报告</div>
  <div class="cover-badge shiny-text" data-lang="en">Research Report</div>
  <h1 data-lang="zh">报告标题</h1>
  <h1 data-lang="en">Report Title</h1>
  <p class="cover-subtitle" data-lang="zh">副标题 / 报告范围说明</p>
  <p class="cover-subtitle" data-lang="en">Subtitle / scope description</p>
  <p class="cover-hook" data-lang="zh">📅 2026-06  |  作者  |  数据来源</p>
  <p class="cover-hook" data-lang="en">📅 2026-06  |  Author  |  Data Source</p>
</article>
```

---

## 2. 摘要 / 关键发现页

提炼报告的 3–5 条核心结论。**密度：中等** — 每条发现配一段话，不宜超过 5 条，保持可扫读。

**推荐配合组件：** 引文卡片 #13 引用支撑论据，标签组 #17 标注发现类型（技术/市场/竞争）。

```html
<section class="exec-summary">
  <h2 data-lang="zh">📋 关键发现</h2>
  <h2 data-lang="en">📋 Key Findings</h2>
  <div class="exec-summary-item" data-lang="zh">发现一：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 1: Summary</div>
  <div class="exec-summary-item" data-lang="zh">发现二：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 2: Summary</div>
  <div class="exec-summary-item" data-lang="zh">发现三：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 3: Summary</div>
</section>
```

---

## 3. 关键数字页

将核心指标平铺展示，适合快速浏览。**密度：稀疏** — 每个卡片只显示 1 个数字 + 标签，网格间距充足。

**推荐配合组件：** 数据卡片网格 #12（图标+数值+标签），数值滚动动画 #16（数字从 0 滚动到目标值），标签组 #17 标注指标分类。

```html
<section class="key-numbers">
  <div class="kn-card">
    <span class="kn-number" data-countup="100">0</span>
    <span class="kn-label" data-lang="zh">指标名</span>
    <span class="kn-label" data-lang="en">Metric</span>
  </div>
  <div class="kn-card">
    <span class="kn-number" data-countup="50">0</span>
    <span class="kn-label" data-lang="zh">指标名</span>
    <span class="kn-label" data-lang="en">Metric</span>
  </div>
  <div class="kn-card">
    <span class="kn-number" data-countup="75">0</span>
    <span class="kn-label" data-lang="zh">指标名</span>
    <span class="kn-label" data-lang="en">Metric</span>
  </div>
  <div class="kn-card">
    <span class="kn-number" data-countup="25">0</span>
    <span class="kn-label" data-lang="zh">指标名</span>
    <span class="kn-label" data-lang="en">Metric</span>
  </div>
</section>
```

---

## 4. 目录（自动生成）

### 工作原理

目录**不是预渲染的静态列表**。以下 `<nav class="report-toc">` 仅作为标题占位——实际内容由模板内置的 JS 自动生成：

```javascript
// 模板内置 — 自动编号目录逻辑
var tocList = document.querySelector('.toc-list');
if (tocList) {
  var headings = document.querySelectorAll('h2[data-lang]');
  headings.forEach(function(h, i) {
    var li = document.createElement('li');
    li.className = 'toc-item';
    li.textContent = h.textContent;
    li.addEventListener('click', function() {
      h.scrollIntoView({ behavior: 'smooth' });
    });
    tocList.appendChild(li);
  });
}
```

**规则：**
- JS 扫描 DOM 中所有 `<h2>` 元素，读取其 `data-lang` 属性
- 只显示与当前选中语言匹配的标题（切换语言时自动重建）
- 每个标题作为一个 `toc-item` 插入浮动面板
- 点击条目平滑滚动到对应 `<h2>` 位置
- 滚动时 `IntersectionObserver` 高亮当前可见章节

> **注意：** `<h2>` 的文本内容决定了目录项的文字。请确保每个 `<h2>` `data-lang="zh"` 和 `data-lang="en"` 填写完整可读的章节名。

```html
<nav class="report-toc">
  <h2 data-lang="zh">目录</h2>
  <h2 data-lang="en">Table of Contents</h2>
  <ol>
    <li><a href="#ch1" data-lang="zh">第一章：章节标题</a><a href="#ch1" data-lang="en">Chapter 1: Title</a></li>
    <li><a href="#ch2" data-lang="zh">第二章：章节标题</a><a href="#ch2" data-lang="en">Chapter 2: Title</a></li>
  </ol>
</nav>
```

> 此静态 `<ol>` 是备用方案；主流设备上点击底部工具栏的「目录」按钮，浮动面板会展示 JS 自动生成的版本。

---

## 5. 章节正文页

报告主体。**密度：密集** — 可包含大段文字 + 多个视觉组件穿插。注意每 500 字至少 1 个视觉元素。

**推荐配合组件：** SVG 流程图 #1（流程说明）、CSS 时间线 #3（发展历程）、ECharts #24（数据图表）、Tab 面板 #9（多视角内容）、折叠分步 #8（复杂概念拆解）、热力图 #19（密度矩阵）、D3 力导向图 #27（关系网络）、Three.js #26（3D 展示）。

```html
<section class="report-chapter" id="ch1">
  <h2 data-lang="zh">第一章：章节标题</h2>
  <h2 data-lang="en">Chapter 1: Title</h2>
  <p data-lang="zh">正文内容...</p>
  <p data-lang="en">Body content...</p>
  <!-- INSERT: 视觉组件 HTML（根据决策指南选择） -->
  <!-- 每章结尾放置标签组 #17 -->
</section>
```

---

## 6. 对比分析页

**密度：中等偏密** — 对比表本身信息量大，但周边留白要保持。

**推荐配合组件：** 对比表 #5（通用多维度对比）、对比表增强版 #22（粘性表头 + 排序）、热力图 #19（数值高低着色）。

```html
<section class="comparison-page">
  <h2 data-lang="zh">对比分析</h2>
  <h2 data-lang="en">Comparative Analysis</h2>
  <!-- INSERT: 对比表组件 #5 或对比表增强版 #22 -->
</section>
```

---

## 7. 结论与建议页

**密度：中等偏疏** — 每项建议配 1–2 句话，不超过 5 条。

**推荐配合组件：** 引文卡片 #13 引用支撑论据，信息面板 #21 显示风险提示，告警条 #18 标注紧急程度，步骤指示器 #20 展示阶段性实施路径。

```html
<aside class="conclusion-page">
  <h2 data-lang="zh">结论与建议</h2>
  <h2 data-lang="en">Conclusions &amp; Recommendations</h2>
  <div class="ccl-item" data-lang="zh">建议一：具体行动方案</div>
  <div class="ccl-item" data-lang="en">Recommendation 1: Action plan</div>
  <div class="ccl-item" data-lang="zh">建议二：具体行动方案</div>
  <div class="ccl-item" data-lang="en">Recommendation 2: Action plan</div>
  <div class="ccl-item" data-lang="zh">建议三：具体行动方案</div>
  <div class="ccl-item" data-lang="en">Recommendation 3: Action plan</div>
</aside>
```

---

## 8. 附录 + 脚注

**密度：中等** — 列表式内容为主，适当留白确保可读性。

**推荐配合组件：** 标签组 #17 标注附录分类（数据来源/方法/术语），引文卡片 #13 列出参考文献，告警条 #18 提示局限性说明。

```html
<section class="appendix">
  <h2 data-lang="zh">附录</h2>
  <h2 data-lang="en">Appendix</h2>
  <p data-lang="zh"><strong>数据来源：</strong>列出所有数据来源</p>
  <p data-lang="en"><strong>Data Sources:</strong> List all data sources</p>
  <p data-lang="zh"><strong>方法说明：</strong>研究方法与局限</p>
  <p data-lang="en"><strong>Methodology:</strong> Research methods and limitations</p>
</section>

<!-- 报告脚注（紧接附录，共用间距） -->
<footer class="report-footer">
  <p data-lang="zh">本报告由 context2html 自动生成  |  生成日期：2026-06-29</p>
  <p data-lang="en">Generated by context2html  |  Date: 2026-06-29</p>
</footer>
```

---

## 密度对照速查

| 页面类型 | 密度 | 说明 |
|---------|------|------|
| 封面页 | 稀疏 | 大留白、少文字，仅标题/元数据 |
| 摘要/关键发现 | 中等 | 3–5 条，每条 1–2 句，可扫读 |
| 关键数字 | 稀疏 | 网格卡片，每卡仅数字+标签 |
| 目录 | 中等 | 列表形式，自动生成 |
| 章节正文 | 密集 | 正文 + 多个视觉组件穿插 |
| 对比分析 | 中等偏密 | 对比表信息量大，周围留白 |
| 结论与建议 | 中等偏疏 | ≤5 条，每项配 1–2 句 |
| 附录+脚注 | 中等 | 列表/段落混排 |

**视觉节奏建议：** 在密集页（章节正文）之间穿插稀疏页（关键数字、结论），形成「呼吸感」。连续 3 页以上密集正文会让读者疲劳。

---

> 完整组件索引（#1–#29）及选择矩阵见 `decision-guide.md`。
> 所有样式 CSS 变量由 `theme/report-themes.css` 管理（从 teach_more_pic 的 DESIGN.md 自动生成，禁止手改）。
