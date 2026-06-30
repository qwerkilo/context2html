---
name: context2html
description: >
  将调研内容/研究报告自动转化为可视化 HTML 报告。
  从对话上下文提取已有调研结果，或读取外部文件路径。
  完整复用 teach_more_pic 的 29 个视觉组件（SVG 流程图、ECharts、Three.js、D3.js 等）。
  Triggers: "报告", "调研", "research", "report", "生成报告", "把内容做成报告",
  "调研报告", "visual report", "可视化报告", "research report", "出报告".
disable-model-invocation: true
argument-hint: "调研内容描述或文件路径？"
---

# context2html — 调研报告可视化工具

将调研内容/研究报告自动转化为可视化 HTML 报告。完整复用 `teach_more_pic` 的 29 个视觉组件（SVG 流程图、ECharts、Three.js 3D、D3.js 力导向图等）和离线库。

## 前置条件

- 本 skill 的 `components/`、`libs/`、`templates/report-starter.html` 已就位
- `teach_more_pic` 的组件体系已复制到本项目

## 核心约定

- **无构建系统**：纯 HTML/CSS/JS，无 package.json、无 npm 命令。修改后直接浏览器打开。
- **中英双语**：所有文本必须同时包含中文和英文版本，通过 L 键或语言按钮切换。默认显示中文。
- SVG 中文字体需显式指定 font-family（含中文字体名）。
- **所有报告从 `templates/report-starter.html` 复制作为基础**。禁止从零生成 HTML 结构。
- 保留模板的完整 CSS 变量系统（`:root` + 20 个 `[data-theme]`）、工具栏（主题/语言/目录）、键盘快捷键（T/L/←→）。
- 视觉组件在模板预留的 `<!-- INSERT: 视觉组件 HTML -->` 注释处追加。

## 报告生成工作流

### Step 0: 输入获取

- 从对话上下文中提取已有调研内容
- 或读取用户提供的文件路径（Markdown/文本文件）
  · 文件路径不存在 → 提示用户检查路径 → 回退到对话内容直接提取
  · 文件格式不是 Markdown/纯文本 → 尝试用 `python -c "import docx"` 读取 .docx → 回退到请用户粘贴文本
- 确认以下信息：
  · 报告主题与目标受众
  · 关键数据点数量（影响组件选择策略）
  · 是否有明确的结论或建议需要突出
- 🛑 STOP：等待用户确认后再继续

### Step 1: 报告结构规划

- 根据内容量决定章节数（推荐 3-6 章）
  · 内容不足 3 章 → 展开 sub-section 细节，或合并为 2 章加附录
  · 内容超过 10 章 → 归类合并，使每章有独立论点
- 设计关键发现摘要（3-5 条）
- 标记适合可视化的数据点
- 🛑 STOP：展示章节大纲给用户确认。用户未确认不得推进。

### Step 2: 选择视觉组件

从组件索引按报告场景选择。完整选择矩阵见 `references/decision-guide.md`。

快速摘要：

| 报告内容类型 | 推荐组件 | 优先级 |
|------------|---------|--------|
| 数据对比（交互式） | ECharts #26 | ⭐⭐⭐ |
| 3D 数据分布 | Three.js 3D 柱状图 #27 | ⭐⭐⭐ |
| 3D 地理分布 | ECharts GL 3D 地球 #29 | ⭐⭐⭐ |
| 数据对比（基础/轻量） | CSS 条形图 #4 / 数据图表集 #24 | ⭐⭐⭐ |
| 人物/角色介绍 | 角色卡片 #2 | ⭐⭐ |
| 图片前后对比 | 图片对比滑块 #10 | ⭐⭐ |
| 数值高低分布 | 热力图 #19 | ⭐⭐ |
| 流程/架构 | SVG 流程图 #1 | ⭐⭐⭐ |
| 关键指标 | 数据卡片网格 #12 / 数值滚动 #16 | ⭐⭐⭐ |
| 时间线事件 | CSS 时间线 #3 / 交互式时间线 #11 | ⭐⭐ |
| 多维度对比 | 对比表增强版 #22 | ⭐⭐ |
| 来源引用 | 引文卡片 #13 | ⭐⭐ |
| 复杂概念分步 | 折叠分步 #8 / Tab 面板 #9 | ⭐⭐ |
| 关系网络 | D3 力导向图 #28 | ⭐ |
| 状态/进度 | 状态链 #15 / 步骤指示器 #20 | ⭐ |
| 提示/警告 | 告警条 #18 | ⭐ |
| 补充信息 | 信息面板 #21 | ⭐ |
| 标签/关键词 | 标签组 #17 | ⚠️ 每章结尾必用 |
| 图片说明 | SVG Figure #6 / 标注式图片 #14 | ⭐⭐ |
| 全屏展示 | 灯箱 #23 | ⭐ |

> **数据密集型报告优先使用 Three.js #27 和 ECharts GL #29** 提升视觉冲击力。

- 打开对应的 `components/NN-name.md` 读取完整 HTML/CSS/JS
- 每 500 字至少 1 个视觉元素，数据密集型章节可缩短至 300 字
- 🛑 STOP：展示组件选择清单给用户确认

### Step 2.5: 人类化写作（强制 — 生成内容前阅读）

**所有报告正文必须去 AI 味。** 以下规则基于 AIGC 检测系统的 5 个判定维度（D1-D5）。必须在写第一段正文之前逐条对照，边写边检查，不可后置补救。

| 维度 | 规则 | 执行检查 |
|------|------|---------|
| **D1-句长** | 禁止连续 3 句长度差 < 8 字；每段混入 ≤10 字短句 1-2 句 + ≥35 字长句 1-2 句 | 写完后扫一眼：最短句多短？最长句多长？ |
| **D2-段落结构** | 相邻段落不得用同一种结构模板。5 种模板轮换：数据驱动(数字→阐释)、对比判断(A→B→差异)、问题先行(提问→分析→结论)、观察收束(论证→判断→无总结)、叙事式(场景→要点) | 每章开头段落用不同模式 |
| **D3-信息密度** | 核心段密度 70%-85%（每个主张配数据）；过渡段 40%-50%（1-2 句即可）；连续两段密度差 ≥ 15% | 检查是否有"干巴巴罗列数据"或"空话连篇"的段落 |
| **D4-连接词** | 禁止段落开头用"首先/其次/最后/综上所述/此外/另外/值得注意的是"；每 1000 字连接词 ≤ 6 个 | 用上一段结论自然引出下一段，而非用连接词硬接 |
| **D5-术语变体** | 每 800 字至少 1 处同义替换："重要趋势"→"绕不开的方向"；"增长驱动"→"推力/支撑逻辑"；"占据主导"→"稳坐头把交椅"；"优势明显"→"拉开差距/强一截" | 检查是否通篇同一术语 |

英文文本同样适用 D1-D5：驻句（2-6 词）与复合句（30+ 词）交替；避免每句以 "The/This/These" 开头；删除 "Furthermore/Moreover/Notably" 等多余连接词。

工具：完成全文后对照 `references/humanize_matrix.md` 中的 20 条案例逐条微调。

- 🛑 STOP：已逐条确认 D1-D5 规则，理解每维度约束。用户确认后再开始正文写作。

### Step 3: 生成 HTML

1. 复制 `templates/report-starter.html` 为 `report-slug.html`
   · 模板路径不存在 → 检查 `templates/` 目录下文件名 → 从 teach_more_pic 重新复制
2. 🎨 **选择并设置主题** — 按决策指南 `theme 选择参考表` 选适合报告类型的主题：
   · 设置 `<html data-theme="xxx">` 为推荐主题
   · 确保 `<link href="../theme/report-themes.css">` 路径正确
   · 预览主题：打开 `examples/report-themes.html` 敲 T 键循环对比
3. 填充封面元数据（标题、日期、作者、数据来源）
4. 编写摘要 + 每章正文（中英双语 `data-lang="zh"` + `data-lang="en"`）— **写作时全程应用 Step 2.5 的 D1-D5 约束**
   🛑 STOP：展示正文框架 + 逐段 D1-D5 自检结果给用户确认。用户确认后再合并组件。
5. 从 `components/NN-name.md` 复制所选组件的 HTML + CSS + JS 合并到报告中：
   · 组件代码不兼容（缺 JS 依赖）→ 切换到简化版（纯 CSS 变体或文字替代）
   · 结构 HTML：复制文件中 ````html` 代码块
   · 组件 CSS：复制文件中 ````css` 代码块 → 合并到 `<style>` 中（按前缀分组）
   · 组件 JS：复制文件中 ````js` 代码块 → 合并到 `<script>` 中
6. 生成自动编号目录
7. 每章末尾追加标签组 #17

**合并组件 CSS 规则：**
1. 所有组件 CSS 放同一个 `<style>` 块中，按前缀分组
2. 组件类名使用唯一前缀（`dg-`、`sd-`、`tab-` 等），不会冲突
3. 重复的 `:root` 变量声明只需保留一份
4. `@media` 查询放各组件的 CSS 块末尾

**组件 JS 合并规则：**
- 组件 JS 放在 `<!-- ===== 组件 JS 从此处插入（可选） ===== -->` 注释之后
- PPT 增强 JS 始终最先加载

### Step 4: 验证

运行 `python scripts/validate-report.py report-slug.html` 检查：

- SVG 文件通过了 XML 验证
- 所有 SVG 文字颜色与背景有足够对比度
- SVG 中的中文渲染正常（font-family 包含中文字体）
- 条形图 width 百分比 < 100%
- 对比表在窄屏（<600px）下折叠为堆叠布局
- 中英文内容成对标记（`data-lang="zh"` + `data-lang="en"`）
- 语言切换按钮和 L 键快捷键存在
- `theme/report-themes.css` 存在且被引用
- 章节间交叉引用使用 `#chN` 锚点链接
- 人类化 D1-D5 自检：句长交替 ✓ 段落结构轮换 ✓ 信息密度交替 ✓ 连接词无滥用 ✓ 术语有变体 ✓

· 验证失败 → 对照"失败模式与异常处理"表锁定具体问题 → 修复 → 重新验证
· 连续 3 轮验证仍不通过 → 降级为纯文字报告输出（不附加视觉组件）

- 🛑 STOP：所有验证通过后再继续

### Step 5: 输出

- 报告文件：`report-slug.html`
- 首次使用时复制 `libs/` 目录到报告同级目录（echarts/three/d3 离线包）
- 可选：运行 `powershell -ExecutionPolicy Bypass -File templates/start-server.ps1` 启动本地服务器预览

## 文件资源速查

| 路径 | 用途 | 工作流中引用处 |
|------|------|--------------|
| `templates/report-starter.html` | 报告骨架模板（所有报告的起点） | Step 3 |
| `components/NN-name.md` | 组件代码（29 个） | Step 2/3 |
| `references/decision-guide.md` | 组件选择矩阵 | Step 2 |
| `references/page-types.md` | 9 种页面类型代码参考 | Step 3 |
| `libs/` | 离线包（echarts/three/d3） | Step 5 |
| `templates/start-server.ps1` | 本地 HTTP 服务器启动脚本 | Step 5 |
| `templates/flowchart-vertical.svg` | 垂直流程图模板 | Step 2/3 |
| `theme/report-themes.css` | 20 主题 CSS（自动生成，不可直接编辑） | Step 3 |
| `scripts/generate-theme-css.py` | 从 DESIGN.md 重新生成主题 CSS | 主题变更时 |
| `examples/report-themes.html` | 20 主题预览页 | Step 2/3 |
| `templates/cycle-diagram.svg` | 循环图模板 | Step 2/3 |
| `templates/timeline-horizontal.svg` | 水平时间线 SVG 模板 | Step 2/3 |

## 视觉设计纪律

- **最多 1 个强调色**，饱和度 < 80%。禁止 AI 默认的紫/蓝渐变
- **禁止热暖系蜡笔色默认**（#f5f1ea 等米白背景、#b08947 等黄铜强调色）
- **禁止纯黑 `#000000`**，用 off-black（zinc-950、`#1a1a1a`）；**禁止纯白 `#ffffff`**，用 off-white
- 渐变文本只用于极小标题，禁止大标题全渐变
- 一页只用一个字体族
- **到报告模板的 `templates/report-starter.html` 中去取最新的 CSS 变量和组件 CSS**，不要从其他源复制。

## 反模式黑名单

| # | 反模式 | 为什么 | 替代做法 |
|---|--------|--------|---------|
| 1 | 视觉组件不足 / 连续 500+ 字无视觉元素 | 读者疲劳 | 每 500 字至少 1 个视觉元素 |
| 2 | 硬编码颜色而非 CSS 变量 | 主题切换后颜色不变 | 全部用 `var(--accent)` 等 |
| 3 | 只写中文不写英文 | 违反双语约定 | 成对 `data-lang` |
| 4 | 编造数据/引文 | 损害可信度 | 模拟数据标注 `mock-data` 类 |
| 5 | 缺少 PPT 质感（无主题切换/键盘导航） | 交互体验差 | report-starter.html 已内置 |
| 6 | 图表库只加载部分依赖 | 一种图表空白 | 用到几个库就加载几个 libs 文件 |
| 7 | 从零写 HTML 而非复制模板 | 丢失 CSS 变量/主题系统 | 始终从 report-starter.html 复制 |

## 先决条件检查（在 Step 4 使用而不是手动逐项核对）

运行 `python scripts/validate-report.py report-slug.html` 会自动执行全部检查（含 SVG 验证、中文渲染、对比表窄屏折叠、中英双语配对、条形图不溢出、章节交叉引用 `#chN` 等 17 项）。手动核对见 Step 4 验证清单。

## 失败模式与异常处理

| 触发条件 | 一线修复 | 仍失败兜底 |
|---------|---------|-----------|
| SVG 空白/排版错乱 | 检查 XML 语法、viewBox 与 width/height 比例 | 降级为 `<img>` 外部引用 |
| SVG 中文不渲染 | font-family 加中文字体 | 内联 font-family |
| 条形图溢出容器 | 检查 `bar-fill` width ≤ 100% | `text-overflow: ellipsis` |
| 主题切换后颜色不变 | 用 `var(--accent)` 而非固定色 | `border-bottom-color: var(--accent)` |
| ECharts/Three/D3 空白 | 对应 lib 未加载 | 复制 `libs/` 下文件到报告同级 |
| Three.js WebGPU 空白 | importmap 路径错误 | 降级为 `libs/three.min.js` UMD |
| 语言切换错位 | 中英文段落数不一致 | 确保两版本段落数相同 |
| 数据点超过 10 个 | 用 ECharts #24 分批展示 | 分多个子图表逐组呈现 |
| 用户只提供单语言输入 | 根据内容语种补充翻译另一版本 | 标注 `machine-translated` |
| 浏览器缓存旧 JS | Ctrl+F5 强制刷新 | 注销浏览器缓存 |
