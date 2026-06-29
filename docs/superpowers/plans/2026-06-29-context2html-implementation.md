# context2html 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个 Agent skill，将调研内容/研究报告自动转化为可视化 HTML 报告，完整复用 teach_more_pic 的 28 个视觉组件。

**架构：** 以 teach_more_pic 为资产来源，复制其 components/、libs/、SVG 模板，新增报告专用模板 report-starter.html（改造自 lesson-starter.html），编写 SKILL.md 定义报告生成工作流。

**技术栈：** 纯 HTML/CSS/JS，无构建系统。ECharts、Three.js、D3.js 离线包。

**源路径：** `C:\Users\qwerkilo\.agents\skills\teach_more_pic\`
**目标路径：** `G:\微云同步助手\491016762\GPT\skills\.agents\context2html\`

---

### 任务 1：复制 teach_more_pic 资产到本项目

**文件：**
- 创建：`components/`（28 个组件 markdown 文件）
- 创建：`libs/`（echarts/three/d3 离线包 + magicui-effects.css）
- 创建：`scripts/`（验证脚本 + 测试）
- 创建：`examples/`（示例文件）
- 创建：`templates/` 下的 SVG 模板

- [ ] **步骤 1：复制 components/ 目录**

```bash
Copy-Item -Recurse -LiteralPath "C:\Users\qwerkilo\.agents\skills\teach_more_pic\components" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\components"
```

验证：`Get-ChildItem "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\components" | Measure-Object | % { $_.Count }` → 28

- [ ] **步骤 2：复制 libs/ 目录**

```bash
Copy-Item -Recurse -LiteralPath "C:\Users\qwerkilo\.agents\skills\teach_more_pic\libs" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\libs"
```

验证：`Test-Path "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\libs\echarts.min.js"` → True

- [ ] **步骤 3：复制 scripts/ 目录**

```bash
Copy-Item -Recurse -LiteralPath "C:\Users\qwerkilo\.agents\skills\teach_more_pic\scripts" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\scripts"
```

- [ ] **步骤 4：复制 SVG 模板文件**

```bash
$src = "C:\Users\qwerkilo\.agents\skills\teach_more_pic\templates"
$dst = "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\templates"
Copy-Item -LiteralPath "$src\flowchart-vertical.svg" -Destination "$dst\flowchart-vertical.svg"
Copy-Item -LiteralPath "$src\cycle-diagram.svg" -Destination "$dst\cycle-diagram.svg"
Copy-Item -LiteralPath "$src\comparison-side-by-side.svg" -Destination "$dst\comparison-side-by-side.svg"
Copy-Item -LiteralPath "$src\timeline-horizontal.svg" -Destination "$dst\timeline-horizontal.svg"
Copy-Item -LiteralPath "$src\start-server.ps1" -Destination "$dst\start-server.ps1"
Copy-Item -LiteralPath "$src\start-server.sh" -Destination "$dst\start-server.sh"
```

- [ ] **步骤 5：复制 examples/ 目录**

```bash
Copy-Item -Recurse -LiteralPath "C:\Users\qwerkilo\.agents\skills\teach_more_pic\examples" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\examples"
```

- [ ] **步骤 6：创建 references/ 目录（留空，后续任务填充）**

```bash
New-Item -ItemType Directory -Path "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\references" -Force
```

- [ ] **步骤 7：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "feat: copy teach_more_pic assets (components/libs/scripts/templates/examples)"
```

---

### 任务 2：创建 report-starter.html 模板

**文件：**
- 创建：`templates/report-starter.html`
- 基础：`C:\Users\qwerkilo\.agents\skills\teach_more_pic\templates\lesson-starter.html`

改造清单：
1. 保留：CSS 变量系统 + 20 个 `[data-theme]` + 正文排版 + 动画 + Magic UI CSS + 底部工具栏 + PPT 质感 JS
2. 去掉：quiz-section 相关 CSS（`.quiz-section`、`.quiz-question`、`.quiz-option`、`.quiz-feedback`）
3. 去掉：`section-divider` 三幕分隔相关 CSS → 替换为 `report-chapter` 和 `exec-summary` 等报告用 CSS
4. 新增 CSS：`.exec-summary`、`.key-numbers`、`.report-toc`、`.report-chapter`、`.comparison-page`、`.conclusion-page`、`.appendix`、`.report-footer`
5. 重写 body 结构：去掉三幕 + 测验 + 总结卡片区域，替换为报告页面类型

- [ ] **步骤 1：复制 lesson-starter.html 为 report-starter.html**

```bash
Copy-Item -LiteralPath "C:\Users\qwerkilo\.agents\skills\teach_more_pic\templates\lesson-starter.html" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\templates\report-starter.html"
```

- [ ] **步骤 2：修改 CSS — 去掉 quiz 样式，保留组件 CSS**

打开 `templates/report-starter.html`，删除 quiz 相关 CSS（`.quiz-section` 到 `.quiz-feedback` 块，约第 218-226 行），保留其他全部样式。删除 summary-cards 相关 CSS（第 231-235 行）。

然后将 `section-divider` 相关 CSS（第 228-235 行）替换为报告专用页面类型 CSS。在组件 CSS 插入标记之前插入：

```css
/* ===== 报告专用页面类型 ===== */
/* 关键发现摘要 */
.exec-summary { margin: 2rem 0; padding: 1.5rem 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
.exec-summary h2 { border: none; margin-top: 0; }
.exec-summary-item { display: flex; align-items: flex-start; gap: 0.8rem; margin: 1em 0; font-size: 0.95rem; }
.exec-summary-item::before { content: '◆'; color: var(--accent); font-size: 0.7rem; flex-shrink: 0; margin-top: 0.3em; }

/* 关键数字页 */
.key-numbers { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin: 2rem 0; }
.kn-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; text-align: center; }
.kn-number { font-size: 2rem; font-weight: 800; color: var(--accent); display: block; font-variant-numeric: tabular-nums; }
.kn-label { font-size: 0.82rem; color: var(--muted); margin-top: 0.3em; display: block; }

/* 报告目录 */
.report-toc { margin: 2rem 0; padding: 1.5rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
.report-toc ol { margin: 0; padding-left: 1.5em; }
.report-toc li { margin: 0.5em 0; font-size: 0.9rem; }
.report-toc a { color: var(--link); text-decoration: none; transition: opacity 0.2s; }
.report-toc a:hover { opacity: 0.7; text-decoration: underline; }

/* 报告章节 */
.report-chapter { margin: 2.5rem 0; }
.report-chapter h2 { font-size: 1.4rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.3em; margin-top: 0; }

/* 对比分析页 */
.comparison-page { margin: 2.5rem 0; padding: 1.5rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }

/* 结论与建议 */
.conclusion-page { margin: 2.5rem 0; padding: 1.5rem 2rem; background: var(--surface); border-left: 4px solid var(--accent); border-radius: 0 var(--radius) var(--radius) 0; }
.conclusion-page h2 { border: none; margin-top: 0; }
.ccl-item { display: flex; align-items: flex-start; gap: 0.8rem; margin: 1em 0; font-size: 0.95rem; }
.ccl-item::before { content: '→'; color: var(--accent); font-weight: 700; flex-shrink: 0; }

/* 附录 */
.appendix { margin: 2rem 0; padding: 1rem 0; border-top: 1px solid var(--border); font-size: 0.85rem; color: var(--muted); }
.appendix h2 { border: none; font-size: 1rem; color: var(--text); }

/* 报告脚注 */
.report-footer { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.78rem; color: var(--muted); text-align: center; }
```

- [ ] **步骤 3：修改 body — 替换内容结构**

打开 `templates/report-starter.html`，将 body 内容（从 `<!-- ===== 封面页 ===== -->` 到 `</body>` 前）整体替换为报告骨架结构：

```html
<!-- ===== 报告封面页 ===== -->
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
  <p class="cover-hook" data-lang="zh" style="font-style:normal;font-size:0.85rem;color:var(--muted);">📅 2026-06  |  作者  |  数据来源</p>
  <p class="cover-hook" data-lang="en" style="font-style:normal;font-size:0.85rem;color:var(--muted);">📅 2026-06  |  Author  |  Data Source</p>
</article>

<!-- ===== 摘要 / 关键发现 ===== -->
<section class="exec-summary">
  <h2 data-lang="zh">📋 关键发现</h2>
  <h2 data-lang="en">📋 Key Findings</h2>
  <div class="exec-summary-item" data-lang="zh">发现一：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 1: Summary of key conclusion</div>
  <div class="exec-summary-item" data-lang="zh">发现二：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 2: Summary of key conclusion</div>
  <div class="exec-summary-item" data-lang="zh">发现三：核心结论简述</div>
  <div class="exec-summary-item" data-lang="en">Finding 3: Summary of key conclusion</div>
</section>

<!-- ===== 关键数字（可选） ===== -->
<section class="key-numbers">
  <div class="kn-card"><span class="kn-number" data-countup="100">0</span><span class="kn-label" data-lang="zh">关键指标 1</span><span class="kn-label" data-lang="en">Metric 1</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="50">0</span><span class="kn-label" data-lang="zh">关键指标 2</span><span class="kn-label" data-lang="en">Metric 2</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="75">0</span><span class="kn-label" data-lang="zh">关键指标 3</span><span class="kn-label" data-lang="en">Metric 3</span></div>
  <div class="kn-card"><span class="kn-number" data-countup="25">0</span><span class="kn-label" data-lang="zh">关键指标 4</span><span class="kn-label" data-lang="en">Metric 4</span></div>
</section>

<!-- ===== 目录 ===== -->
<nav class="report-toc">
  <h2 data-lang="zh">目录</h2>
  <h2 data-lang="en">Table of Contents</h2>
  <ol>
    <li><a href="#ch1" data-lang="zh">第一章：章节标题</a><a href="#ch1" data-lang="en">Chapter 1: Title</a></li>
    <li><a href="#ch2" data-lang="zh">第二章：章节标题</a><a href="#ch2" data-lang="en">Chapter 2: Title</a></li>
    <li><a href="#ch3" data-lang="zh">第三章：章节标题</a><a href="#ch3" data-lang="en">Chapter 3: Title</a></li>
  </ol>
</nav>

<!-- ===== 第一章 ===== -->
<section class="report-chapter" id="ch1">
  <h2 data-lang="zh">第一章：章节标题</h2>
  <h2 data-lang="en">Chapter 1: Title</h2>
  <p data-lang="zh">正文内容...</p>
  <p data-lang="en">Body content...</p>
  <!-- INSERT: 视觉组件 HTML -->
</section>

<!-- ===== 第二章 ===== -->
<section class="report-chapter" id="ch2">
  <h2 data-lang="zh">第二章：章节标题</h2>
  <h2 data-lang="en">Chapter 2: Title</h2>
  <p data-lang="zh">正文内容...</p>
  <p data-lang="en">Body content...</p>
  <!-- INSERT: 视觉组件 HTML -->
</section>

<!-- ===== 第三章 ===== -->
<section class="report-chapter" id="ch3">
  <h2 data-lang="zh">第三章：章节标题</h2>
  <h2 data-lang="en">Chapter 3: Title</h2>
  <p data-lang="zh">正文内容...</p>
  <p data-lang="en">Body content...</p>
  <!-- INSERT: 视觉组件 HTML -->
</section>

<!-- INSERT: 更多章节 -->

<!-- ===== 对比分析（可选） ===== -->
<section class="comparison-page">
  <h2 data-lang="zh">对比分析</h2>
  <h2 data-lang="en">Comparative Analysis</h2>
  <!-- INSERT: 对比表/对比表增强版组件 -->
</section>

<!-- ===== 结论与建议 ===== -->
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

<!-- ===== 附录 ===== -->
<section class="appendix">
  <h2 data-lang="zh">附录</h2>
  <h2 data-lang="en">Appendix</h2>
  <p data-lang="zh"><strong>数据来源：</strong>列出所有数据来源</p>
  <p data-lang="en"><strong>Data Sources:</strong> List all data sources</p>
  <p data-lang="zh"><strong>方法说明：</strong>研究方法与局限</p>
  <p data-lang="en"><strong>Methodology:</strong> Research methods and limitations</p>
</section>

<!-- ===== 报告脚注 ===== -->
<footer class="report-footer">
  <p data-lang="zh">本报告由 context2html 自动生成  |  生成日期：2026-06-29</p>
  <p data-lang="en">Generated by context2html  |  Date: 2026-06-29</p>
</footer>
```

- [ ] **步骤 3（续）：修改模板标题**

将 `<title>XXXX 课标题</title>` 改为 `<title>报告标题 - 调研报告</title>`
将 `data-theme="warm"` 保留（与课程模板一致）

- [ ] **步骤 4：清理 body 中遗留的课程内容**

删除所有课程示例组件 HTML（角色卡片、状态链、条形图、时间线、折叠分步、引文卡片、Tab 面板、灯箱、步骤指示器等示例）。保留注释标记 `<!-- INSERT: 视觉组件 HTML -->` 和 `<!-- ===== 组件 JS 从此处插入（可选） ===== -->`。

- [ ] **步骤 5：删除 quiz JS**

删除 `<!-- ===== Quiz JS ===== -->` 到 `</script>` 整个块（约第 693-710 行）。

- [ ] **步骤 6：更新注释标记**

将模板中的 `<!-- INSERT: 视觉组件 HTML 从这里插入 -->` 注释保留。

- [ ] **步骤 7：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "feat: create report-starter.html template"
```

---

### 任务 3：创建报告场景 references

**文件：**
- 创建：`references/decision-guide.md` — 报告场景组件选择矩阵
- 创建：`references/page-types.md` — 报告 8 种页面类型

- [ ] **步骤 1：创建 reports/decision-guide.md**

写入报告场景组件选择矩阵（参考设计规格中的表格，含 3D/GL 场景映射），保留 "每 500 字至少 1 个视觉元素" 约束，包含 "数据密集型报告优先使用 Three.js #25 和 ECharts GL #28" 注释。

- [ ] **步骤 2：创建 reports/page-types.md**

写入 8 种报告页面类型的 HTML/CSS 代码：
1. 封面页（含摘要行 + 元数据）
2. 摘要/关键发现页
3. 关键数字页
4. 目录页（自动编号）
5. 章节正文页（含视觉组件插入标记）
6. 对比分析页
7. 结论与建议页
8. 附录页

每个页面类型包含完整的中英双语 HTML 结构 + CSS 代码（可复用到 report-starter.html 中）。

- [ ] **步骤 3：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "feat: add report references (decision-guide, page-types)"
```

---

### 任务 4：创建 SKILL.md

**文件：**
- 创建：`SKILL.md`

**设计说明：**
SKILL.md 是 context2html 的核心入口，定义：
1. skill 元数据（trigger、description、argument-hint）
2. 前置条件（引用 teach_more_pic 并说明组件来源）
3. 报告生成工作流（5 步：输入获取→结构规划→组件选择→生成 HTML→验证输出）
4. 组件选择矩阵（from references/decision-guide.md）
5. 报告模板说明（from templates/report-starter.html）
6. 页面类型参考（from references/page-types.md）
7. 视觉设计纪律（继承 teach_more_pic）
8. 反模式黑名单
9. 错误检查清单

- [ ] **步骤 1：创建 SKILL.md**

```yaml
---
name: context2html
description: >
  将调研内容/研究报告自动转化为可视化 HTML 报告。
  从对话上下文提取已有调研结果，或读取外部文件路径。
  完整复用 teach_more_pic 的 28 个视觉组件（SVG 流程图、ECharts、Three.js、D3.js 等）。
  Triggers: "报告", "调研", "research", "report", "生成报告", "把内容做成报告",
  "调研报告", "visual report", "可视化报告", "research report".
disable-model-invocation: true
argument-hint: "调研内容描述或文件路径？"
---
```

内容结构（约 300 行，完整工作流，每个步骤包含 🛑 STOP 关卡）：

**Step 0: 输入获取**
- 从对话上下文中提取已有调研内容，或读取用户提供的文件路径
- 确认：报告主题、目标受众、关键数据点数量
- 🛑 STOP：用户确认

**Step 1: 报告结构规划**
- 根据内容量决定章节数（推荐 3-6 章）
- 设计关键发现摘要（3-5 条）
- 标记哪些数据点适合可视化
- 🛑 STOP：展示章节大纲

**Step 2: 选择视觉组件**
- 完整组件选择矩阵（含 3D/GL 场景映射，28 个组件）
- "每 500 字至少 1 个视觉元素"
- "数据密集型报告优先使用 Three.js #25 和 ECharts GL #28"
- 🛑 STOP：组件清单确认

**Step 3: 生成 HTML**
- 参考 `templates/report-starter.html` 骨架
- 组件 CSS/HTML/JS 合并规则（与 teach_more_pic 完全相同）
- 中英双语 data-lang 成对标记

**Step 4: 验证**
- SVG XML 有效性
- 组件渲染
- 双语成对检查
- 链接完整性
- 🛑 STOP

**Step 5: 输出**
- 报告文件命名：`report-slug.html`
- 可选附带 `libs/` 目录

**反模式黑名单：**
- 组件数量不足 / 章节无视觉元素
- 硬编码颜色而非 CSS 变量
- 只写中文不写英文
- 缺少 PPT 质感（无主题切换/键盘导航/语言切换）

**错误检查清单：**
- [ ] SVG 文件通过 XML 验证
- [ ] 所有 SVG 文字有足够对比度
- [ ] SVG 中文正常渲染
- [ ] 中英文 data-lang 成对
- [ ] 语言切换按钮和 L 键存在

- [ ] **步骤 2：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "feat: create SKILL.md with report generation workflow"
```

---

### 任务 5：创建验证脚本和示例报告

**文件：**
- 创建：`scripts/validate-report.py`（从 validate-lesson.py 改造）
- 创建：`examples/0001-demo-report.html`

- [ ] **步骤 1：复制 validate-lesson.py → validate-report.py**

```bash
Copy-Item -LiteralPath "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\scripts\validate-lesson.py" -Destination "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\scripts\validate-report.py"
```

修改 validate-report.py：
- 去掉 quiz 相关检查（5 题/`data-correct` 检查）
- 去掉三幕结构检查
- 保留 SVG 验证、双语检查、CSS 变量检查、链接检查
- 新增报告专用检查：`.exec-summary` 存在性、`.report-chapter` 至少 1 个、`.conclusion-page` 存在性
- 修改错误信息从 "课程" → "报告"

- [ ] **步骤 2：创建示例报告 examples/0001-demo-report.html**

复制 `templates/report-starter.html` 到 `examples/0001-demo-report.html`，填入虚构的调研内容：
- 封面标题："全球 AI 芯片市场调研报告" / "Global AI Chip Market Research Report"
- 3 条关键发现摘要
- 4 个关键数字（市场规模、增速、头部企业份额、研发投入）
- 3 章正文（市场概况、竞争格局、技术趋势），每章包含至少 1 个视觉组件示例
- 结论与建议

- [ ] **步骤 3：验证示例报告**

```bash
python "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\scripts\validate-report.py" "G:\微云同步助手\491016762\GPT\skills\.agents\context2html\examples\0001-demo-report.html"
```

预期：所有检查通过。

- [ ] **步骤 4：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "feat: add validate-report.py and demo report example"
```

---

### 任务 6：更新 README.md

**文件：**
- 修改：`README.md`

- [ ] **步骤 1：改写 README.md**

```markdown
# context2html

把调研内容/研究报告转化成可视化 HTML 报告。

## 原理

完整复用 [teach_more_pic](../teach_more_pic/) 的 28 个视觉组件体系（SVG 流程图、ECharts、Three.js 3D、D3.js、CSS 条形图、时间线、对比表等），新增报告专用模板和工作流。生成的报告支持 20 种品牌主题切换、中英双语、键盘导航。

## 使用方式

加载此 skill 后，提供调研内容（对话中或文件路径），Agent 按 5 步工作流自动生成报告：

1. 输入获取 → 2. 结构规划 → 3. 组件选择 → 4. HTML 生成 → 5. 验证输出

## 目录结构

| 路径 | 说明 |
|------|------|
| `SKILL.md` | skill 主文件（Agent 入口） |
| `templates/report-starter.html` | 报告骨架模板 |
| `components/` | 28 个视觉组件（来自 teach_more_pic） |
| `libs/` | ECharts/Three.js/D3.js 离线包 |
| `references/` | 组件选择矩阵 + 页面类型 |
| `examples/` | 示例报告 |
| `scripts/validate-report.py` | 报告验证脚本 |
```

- [ ] **步骤 2：Commit**

```bash
cd "G:\微云同步助手\491016762\GPT\skills\.agents\context2html" && rtk git add -A && rtk git commit -m "docs: update README.md for context2html"
```
