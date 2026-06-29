---
title: context2html 页面类型参考
description: 报告模板中可用的 8 种页面类型及代码示例
---

# context2html 页面类型参考

## 1. 封面页

报告标题页，包含摘要行 + 元数据。

### HTML

```html
<article class="cover-page">
  <div class="noise-overlay">
    <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
      <filter id="noise-filter"><feTurbulence type="fractalNoise" baseFrequency="0.4" numOctaves="6" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncR type="linear" slope="0.15"/><feFuncG type="linear" slope="0.15"/><feFuncB type="linear" slope="0.15"/></feComponentTransfer></filter>
      <rect width="100%" height="100%" filter="url(#noise-filter)" opacity="1"/>
    </svg>
  </div>
  <div class="meteors-container"></div>
  <div class="cover-badge shiny-text" data-lang="zh">调研报告</div>
  <div class="cover-badge shiny-text" data-lang="en">Research Report</div>
  <h1 data-lang="zh">报告标题</h1>
  <h1 data-lang="en">Report Title</h1>
  <p class="cover-subtitle" data-lang="zh">副标题 / 报告范围说明</p>
  <p class="cover-subtitle" data-lang="en">Subtitle / scope description</p>
  <p class="cover-hook" style="font-style:normal;font-size:0.85rem;color:var(--muted);" data-lang="zh">📅 2026-06  |  作者  |  数据来源</p>
  <p class="cover-hook" style="font-style:normal;font-size:0.85rem;color:var(--muted);" data-lang="en">📅 2026-06  |  Author  |  Data Source</p>
</article>
```

## 2. 摘要/关键发现页

### HTML

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

### CSS（已内置在 report-starter.html 中）

```css
.exec-summary { margin: 2rem 0; padding: 1.5rem 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
.exec-summary-item { display: flex; align-items: flex-start; gap: 0.8rem; margin: 1em 0; font-size: 0.95rem; }
.exec-summary-item::before { content: '◆'; color: var(--accent); font-size: 0.7rem; flex-shrink: 0; margin-top: 0.3em; }
```

## 3. 关键数字页

### HTML

```html
<section class="key-numbers">
  <div class="kn-card"><span class="kn-number" data-countup="100">0</span><span class="kn-label" data-lang="zh">指标名</span><span class="kn-label" data-lang="en">Metric</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="50">0</span><span class="kn-label" data-lang="zh">指标名</span><span class="kn-label" data-lang="en">Metric</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="75">0</span><span class="kn-label" data-lang="zh">指标名</span><span class="kn-label" data-lang="en">Metric</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="25">0</span><span class="kn-label" data-lang="zh">指标名</span><span class="kn-label" data-lang="en">Metric</span></div>
</section>
```

## 4. 目录页

### HTML

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

## 5. 章节正文页

### HTML

```html
<section class="report-chapter" id="ch1">
  <h2 data-lang="zh">第一章：章节标题</h2>
  <h2 data-lang="en">Chapter 1: Title</h2>
  <p data-lang="zh">正文内容...</p>
  <p data-lang="en">Body content...</p>
  <!-- INSERT: 视觉组件 HTML -->
</section>
```

## 6. 对比分析页

### HTML

```html
<section class="comparison-page">
  <h2 data-lang="zh">对比分析</h2>
  <h2 data-lang="en">Comparative Analysis</h2>
  <!-- INSERT: 对比表组件或对比表增强版组件 -->
</section>
```

## 7. 结论与建议页

### HTML

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

## 8. 附录页

### HTML

```html
<section class="appendix">
  <h2 data-lang="zh">附录</h2>
  <h2 data-lang="en">Appendix</h2>
  <p data-lang="zh"><strong>数据来源：</strong>列出所有数据来源</p>
  <p data-lang="en"><strong>Data Sources:</strong> List all data sources</p>
  <p data-lang="zh"><strong>方法说明：</strong>研究方法与局限</p>
  <p data-lang="en"><strong>Methodology:</strong> Research methods and limitations</p>
</section>
<footer class="report-footer">
  <p data-lang="zh">本报告由 context2html 自动生成  |  生成日期：2026-06-29</p>
  <p data-lang="en">Generated by context2html  |  Date: 2026-06-29</p>
</footer>
```

### 报告脚注 CSS

```css
.report-footer { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.78rem; color: var(--muted); text-align: center; }
```
