---
title: context2html 组件选择决策指南
description: 报告/文章/文档/教程/笔记场景下的视觉组件选择矩阵、CSS 变量参考与快速决策
---

# context2html 组件选择决策指南

## 快速决策树

```
需要展示什么?
├── 数据/数字
│   ├── 3D 多维数据 → Three.js 3D 柱状图 #27
│   ├── 柱状/饼图/折线 → ECharts #26（交互式）/ #24（轻量零依赖）
│   ├── 地理/矩阵密度 → 热力图 #19
│   ├── 力导向/桑基/旭日 → D3 力导向图 #28
│   └── 单数值/KPI → 数据卡片网格 #12 / 数值滚动 #16
├── 流程/时序
│   ├── 业务流程/架构图 → SVG 流程图 #1
│   ├── 时间线/发展历程 → CSS 时间线 #3 / 交互式时间线 #11
│   └── 项目进度/阶段 → 状态链 #15 / 步骤指示器 #20
├── 对比分析
│   ├── 数据点 3-10，需交互 → ECharts #26（⭐⭐⭐ 优先）
│   ├── 多维度/表格式对比 → 对比表增强版 #22
│   └── 简单双列对比 → 对比表 #5 / CSS 条形图 #4
├── 引用/说明
│   ├── 专家观点/数据来源 → 引文卡片 #13
│   ├── 截图/图片 → SVG Figure #6 / 标注式图片 #14
│   └── 风险提示 → 告警条 #18
├── 复杂概念
│   ├── 多步骤拆解 → 折叠式分步详解 #8
│   └── 多视角切换 → Tab 切换面板 #9
└── 每章结尾
    └── 关键词/分类 → 标签组 #17 (强制使用)
```

## 选择矩阵

报告/文章/文档/教程/笔记场景下的视觉组件选择矩阵

| 使用场景 | 适用 content-type | 推荐组件 | 优先级 | 失败模式 / 何时不用 |
|------------|---------|--------|-------------------|
| 数据对比（交互式 ECharts） | report, article | ECharts #26 | ⭐⭐⭐ | 数据点<3 时用 CSS 条形图 #4 更轻量；饼图>8 类别改条形图；需 `libs/echarts.min.js` |
| 数据对比（基础/轻量） | report, article | CSS 条形图 #4 / 数据图表集 #24 | ⭐⭐ | 零 JS 依赖；#24 含柱状/饼图/折线/堆叠；#4 适合水平对比 |
| 3D 数据分布 | report | Three.js 3D 柱状图 #27 | ⭐⭐⭐ | 维度≤2 时 ECharts 2D 更清晰；移动端性能敏感不适用；WebGL 不支持时无降级方案 |
| 3D 地理分布 | report | ECharts GL 3D 地球 #29 | ⭐⭐⭐ | 数据与地理无关时不适用；仅 1-2 个点数据时过重；浏览器不支持 WebGL 时需降级为 2D 地图 |
| 3D 散点/聚类 | report | ECharts GL 3D 散点图 #29 | ⭐⭐ | 数据点<20 时统计意义不足；无 GL 支持时用 2D 散点图 |
| 3D 趋势曲面 | report | ECharts GL 3D 曲面 #29 | ⭐⭐ | 数据非连续曲面时不适用；建议同时提供 2D 热力图 #19 作为降级 |
| 3D 关系网络 | report | Three.js + D3 组合 #27+#28 | ⭐⭐ | 节点<15 时 D3 力导向图 #28 足够；注意同时加载两个库的心理模型成本 |
| 3D 产品展示 | report | Three.js 3D 场景 #27 | ⭐⭐ | 只需图标/平面展示时不适用；需考虑加载时间（Three.js ~500KB） |
| 3D 堆叠对比 | report | ECharts GL 3D 柱状图 #29 | ⭐⭐ | 对比维度≤2 时 ECharts 2D 更直观；GL 库额外 300KB |
| 人物/角色介绍 | report, article, tutorial | 角色卡片 #2 | ⭐⭐ | 无人物介绍时不使用；网格布局自动适应 |
| 图片前后对比 | report, doc, tutorial | 图片对比滑块 #10 | ⭐⭐ | 需两张同尺寸图片；JS 拖拽交互 |
| 数值高低分布 | report | 热力图 #19 | ⭐⭐ | 矩阵<3×3 时信息量不足；纯 CSS 实现，无需外部依赖 |
| 流程/架构说明 | report, doc, tutorial | SVG 流程图 #1 | ⭐⭐⭐ | 步骤≤3 时纯文本即可；SVG 文件需检查 XML 合法性 |
| 时间线事件 | report, doc, article | CSS 时间线 #3 / 交互式时间线 #11 | ⭐⭐ | 事件≤2 时不适用；#11 需 JS 支持，降级为纯 CSS #3 |
| 关键指标 | report, article | 数据卡片网格 #12 / 数值滚动 #16 | ⭐⭐⭐ | 指标≤1 时不适用；滚动动画 #16 在 `prefers-reduced-motion` 时自动静音 |
| 多维度对比 | report, doc | 对比表增强版 #22 | ⭐⭐ | 对比项≤2 时普通列表即可；粘性表头在窄屏可能遮挡内容 |
| 来源引用 | report, article, doc, tutorial | 引文卡片 #13 | ⭐⭐ | 无需突出引用时不使用；过多引文卡片会降低正文可读性 |
| 复杂概念分步 | tutorial, doc, report | 折叠分步 #8 / Tab 面板 #9 | ⭐⭐ | 内容无需分步/分 Tab 时不适用；#8 所有折叠默认展开 |
| 关系网络 | report | D3 力导向图 #28 | ⭐ | 节点<5 时信息量不足；D3 ~300KB，轻量场景用 CSS 简化 |
| 状态/进度 | report, tutorial, doc | 状态链 #15 / 步骤指示器 #20 | ⭐ | 步骤≤2 时不适用；纯 CSS 零依赖 |
| 进度环/进度仪表 | report | SVG.js #31 | ⭐⭐ | 单指标可视化；进度<3 时不适用；需 libs/svg.min.js |
| 提示/警告 | report, doc | 告警条 #18 | ⭐ | 无需风险提示时不使用；4 种类型（info/warning/error/success） |
| 补充信息 | report, doc, article | 信息面板 #21 | ⭐ | 无需补充内容时不使用；窄屏需测试右侧抽屉是否遮挡正文 |
| 标签/关键词 | report, article, doc, tutorial | 标签组 #17 | ⚠️ 强制 | 每章结尾必须插入；5 色自动循环 |
| 图片说明 | report, doc, tutorial | SVG Figure #6 / 标注式图片 #14 | ⭐⭐ | 无需图片时不使用；#14 的标注点>8 个时视觉过载 |

## 使用规则

- **每 500 字至少 1 个视觉元素**，数据密集型章节可缩短到 300 字
- **数据密集型报告优先使用 Three.js #27 和 ECharts GL #29** 提升视觉冲击力
- 色彩语义全局统一：见下方"色彩语义"章节
- 所有组件代码在 `components/NN-name.md` 中
- 组件 CSS 合并到模板 `<style>` 中，按前缀分组
- 组件 JS 合并到报告末尾的 JS 块中
- **页面结构**：9 种标准页面（封面/摘要/关键数字/目录/章节/对比/结论/附录/脚注）详见 `references/page-types.md`
- **主题搭配**：主题选择见下方指南，所有主题 CSS 变量定义在 `theme/report-themes.css` 中（从 teach_more_pic 的 DESIGN.md 自动生成）
- **CSS 变量变更时**：`python scripts/generate-theme-css.py` 重新生成 `theme/report-themes.css`

## 组件密度计算公式

### 公式

```
ceil(总字数 / 500) = 报告最少组件数
```

数据密集型章节可降至 300 字/组件。

### 示例

| 章节 | 字数 | 至少组件数 | 推荐组件 |
|------|------|-----------|---------|
| 第一章：市场规模 | 1,200 | 3 | 数据卡片网格 #12 + CSS 条形图 #4 + 数值滚动 #16 |
| 第二章：商业模式 | 900 | 2 | SVG 流程图 #1 + 标签组 #17 |
| 第三章：竞争分析 | 1,800 | 4 | 对比表增强版 #22 + 热力图 #19 + 引文卡片 #13 + 标签组 #17 |
| 第四章：风险与建议 | 600 | 2 | 告警条 #18 + 信息面板 #21 |
| **总计** | **4,500** | **11** | 每章结尾必含标签组 #17 |

> 每章结尾的标签组 #17 计入该章组件数，不额外增加字数负担。

## 色彩语义

| 角色 | CSS 变量 | 用途 |
|------|---------|------|
| 强调/品牌色 | `--accent` | 标题强调、链接、高亮 |
| 强调柔化 | `--accent-soft` | 卡片背景、hover 态 |
| 强调弱化 | `--accent-muted` | 分割线、辅助装饰 |
| 正向/增长 | `--success` | 增长数据、通过状态 |
| 警示/中性 | `--warning` | 阈值提醒、注意 |
| 风险/下降 | `--error` | 负增长、失败状态 |
| 图表序列 1-4 | `--chart-1` ~ `--chart-4` | 柱状/折线图序列色 |
| 内容背景 | `--bg` | 页面主背景 |
| 表面背景 | `--surface` | 卡片、面板 |
| 主文字 | `--text` | 正文阅读 |
| 次要文字 | `--muted` | 副标题、注释 |

**实际颜色值由所选主题决定**（见下方主题选择指南）。

## CSS 变量参考表

所有变量由 `theme/report-themes.css` 管理（从 teach_more_pic 的 DESIGN.md 自动生成）。页面和组件应仅使用变量，禁止硬编码色值。

| 变量名 | 作用域 | 默认值 | 用途说明 |
|--------|--------|-------|---------|
| `--accent` | 全局 | 主题决定 | 品牌强调色 |
| `--accent-soft` | 全局 | accent@15% | 卡片背景 |
| `--accent-muted` | 全局 | accent@8% | 分割线 |
| `--chart-1` ~ `--chart-4` | 全局 | 主题衍生 | 图表序列色 |
| `--success` | 全局 | 绿色系 | 正向指标 |
| `--warning` | 全局 | 橙色系 | 阈值提醒 |
| `--error` | 全局 | 红色系 | 负增长 |
| `--bg` | 全局 | off-white/off-black | 页面主体背景 |
| `--surface` | 全局 | 比 bg 亮/暗一度 | 卡片、面板背景 |
| `--text` | 全局 | high contrast | 正文、标题 |
| `--muted` | 全局 | low contrast | 副标题、脚注 |
| `--border` | 全局 | 中灰 | 分割线、卡片边框 |
| `--shadow-sm/md/lg` | 全局 | 1-16px | 阴影层次 |
| `--radius` | 全局 | 8-12px | 组件圆角 |
| `--blockquote-border` | 文章区 | accent 衍生 | 引用块左侧竖条 |
| `--blockquote-bg` | 文章区 | surface | 引用块背景 |
| `--table-stripe` | 表格 | 交替行色 | 表格斑马纹 |
| `--table-header-bg` | 表格 | surface 变体 | 表头背景 |
| `--tag-bg` | 标签组 | 5 色循环 | 标签背景 |
| `--tag-text` | 标签组 | 白/黑 | 标签文字色 |
| `--code-bg` | 代码块 | surface 变体 | 行内代码背景 |
| `--code-text` | 代码块 | text | 行内代码文字 |
| `--section-gap` | 章节 | 2-4rem | 章节间距 |
| `--toc-accent` | 目录 | accent 衍生 | 目录链接高亮 |
| `--h2-border` | 章节标题 | accent | 二级标题下边框 |

## 组件索引（31 个）

| # | 组件 | 文件 | 说明 |
|---|---|---|---|
| 1 | SVG 流程图 | components/01-SVG 流程图.md | 四色语义流程图 |
| 2 | 角色卡片 | components/02-角色卡片.md | 网格化角色介绍 |
| 3 | CSS 时间线 | components/03-CSS 时间线.md | 垂直时间轴 |
| 4 | CSS 条形图 | components/04-CSS 条形图.md | 水平数据条 |
| 5 | 对比表 | components/05-对比表.md | 多维度 flex 对比 |
| 6 | SVG Figure | components/06-SVG Figure 包裹.md | 标准图片容器 |
| 7 | PPT 质感增强 | components/07-PPT 质感增强.md | 主题/动画/导航 |
| 8 | 折叠式分步详解 | components/08-折叠式分步详解.md | 复杂概念分步折叠 |
| 9 | Tab 切换面板 | components/09-Tab 切换面板.md | 垂直 Tab 切换 |
| 10 | 图片对比滑块 | components/10-图片对比滑块.md | before/after 对比 |
| 11 | 交互式时间线 | components/11-交互式时间线.md | 点击展开事件详情 |
| 12 | 数据卡片网格 | components/12-数据卡片网格.md | 图标+数值+标签 |
| 13 | 引用/引文卡片 | components/13-引用引文卡片.md | 左侧竖条+引文 |
| 14 | 标注式图片 | components/14-标注式图片.md | 图片数字标注 |
| 15 | 状态链 | components/15-状态链.md | 水平里程碑 |
| 16 | 数值滚动动画 | components/16-数值滚动动画.md | 0→N 滚动 |
| 17 | 标签/徽章组 | components/17-标签徽章组.md | 5 色药丸标签 |
| 18 | 提示框/告警条 | components/18-提示框告警条.md | 4 类型提示 |
| 19 | 热力图/密度图 | components/19-热力图密度图.md | 5 级矩阵 |
| 20 | 步骤指示器 | components/20-步骤指示器.md | 水平编号步骤 |
| 21 | 信息面板 | components/21-信息面板.md | 右侧滑入抽屉 |
| 22 | 对比表增强版 | components/22-对比表增强版.md | 粘性表头+排序 |
| 23 | 全屏模态/灯箱 | components/23-全屏模态灯箱.md | 点击放大 |
| 24 | 数据图表集 | components/24-数据图表集.md | 纯 CSS/SVG 图表 |
| 25 | 现代浏览器 API | components/25-现代浏览器API组件.md | 原生折叠/模态 |
| 26 | ECharts 交互式图表 | components/26-ECharts 交互式图表集.md | 柱状/饼图/折线图 |
| 27 | Three.js 3D 组件 | components/27-Three.js 3D组件.md | 3D 场景/柱状图 |
| 28 | D3.js 数据可视化 | components/28-D3.js 数据可视化.md | 力导向/旭日/桑基 |
| 29 | ECharts GL 3D 可视化 | components/29-ECharts GL 3D可视化.md | 3D柱状/散点/地球 |
| 30 | GSAP 滚动动画集 | components/30-GSAP 滚动动画集.md | 5 模式滚动动画 |
| 31 | SVG.js 动态图表 | components/31-SVG.js 动态图表.md | 轻量 SVG 动画（78KB）：柱状/折线/流程/进度环 |

## 主题选择指南

按报告类型推荐默认主题（可通过 T 键切换）。页面模板（封面/目录/章节/附录等 9 种结构）参见 `references/page-types.md`。

| 报告类型 | 推荐主题 | 备选 | 理由 |
|---------|---------|------|------|
| 技术/芯片/基础设施 | `nvidia` | `ibm` | 棱角分明、科技感强、低动效 |
| 消费电子/产品评测 | `apple` | `tesla` | 纯白画布、衬线字距、产品优先 |
| 金融/投资/加密货币 | `binance` | `notion` | 金色强调、高对比、数据驱动 |
| 娱乐/媒体/文化分析 | `spotify` | `airbnb` | 暗色沉浸、色彩活泼 |
| 企业咨询/传统IT | `ibm` | `hp` | 蓝色信任感、中性保守 |
| 高端制造/汽车 | `bmw-m` | `tesla` | 全黑画布、白色强调 |
| 设计工具/创意行业 | `figma` | `zapier` | 黑白编辑感、彩色区块 |
| AI 产品/前沿科技 | `x.ai` | `claude` | 深色、未来主义 |
| 运动/品牌/消费 | `nike` | `minimax` | 黑白色调、品牌一致 |
| 通用报告 | `warm`（默认） | `airtable` | 中性温暖、长文阅读不疲劳 |

完整 20 主题色板预览：`examples/report-themes.html`。主题 CSS 变量由 `theme/report-themes.css` 自动生成。

## 交付前验证清单

生成报告 HTML 后，必须通过 `python scripts/validate-report.py path/to/report.html` 验证。以下是验证器检查的 22 项硬性检查 + 3 项人类化建议（warning，不计入失败）：

| # | 检查项 | 失败时处理 |
|---|--------|-----------|
| 1 | SVG 文件存在且 XML 合法 | 修复 SVG 路径或 XML 语法 |
| 2 | `<h1>` 个数 1 或 2（中英双语） | 删除多余 h1 或补全双语 |
| 3 | 所有链接为相对路径 | 把 `/absolute/path` 改为相对路径 |
| 4 | SVG 文本/背景对比度 ≥ 3:1 | 修改 SVG 中的浅色文字颜色 |
| 5 | `:focus-visible` 样式存在 | 在 `<style>` 中添加 focus-visible 样式 |
| 6 | `font-variant-numeric: tabular-nums` | 在 body 样式中添加 |
| 7 | 语义 HTML 元素（article/section/nav） | 将 `<div>` 替换为语义元素 |
| 8 | 外链库（ECharts/Three/D3）本地文件存在 | 确认 `libs/` 目录包含所需文件 |
| 9 | 中英双语 `data-lang` 配对 + 切换按钮 + L 键 | 补全缺少的 data-lang 属性或监听器 |
| 10 | `.exec-summary` 存在 | 添加关键发现摘要段 |
| 11 | `.report-chapter` 至少一个 | 报告必须包含正文章节 |
| 12 | `.conclusion-page` 存在 | 添加结论与建议段 |
| 13 | `.report-footer` 存在 | 添加脚注区域 |
| 14 | `theme/report-themes.css` 被引用且文件存在 | 在 `<head>` 中添加 `<link>` 引用，确认文件复制到目标位置 |
| 15 | `.bar-fill` width 不超过 100% | 检查条形图数据值，修正超过 100% 的设置 |
| 16 | `.cmp-table` 在 ≤700px 屏幕下有响应式规则 | 在 `<style>` 中添加 `@media (max-width: 700px)` 规则覆盖 `.cmp-table` |
| 17 | 英文排版（overflow-wrap + table-layout:fixed） | 在 body 中加 `overflow-wrap: break-word`；`.cmp-table` 加 `table-layout: fixed` |
| 18 | ECharts 不使用 `var()` 直接设色 | 用 `gv('--xxx')` 辅助函数替代 `var(--xxx)` |
| 19 | 章节交叉引用使用 `#chN` 锚点 | 把 `href="#chapter-name"` 改为 `#chN` |
| 20 | GSAP `data-gsap` 模式值有效 | 仅允许 fade/stagger/parallax/flip/zoom |
| 21 | `data-anim` 语法有效 | 仅允许 fade-up/fade/slide-left/blur |
| — | **D1 句长交替（warning）** | 每段混入 ≤10 字短句 1-2 + ≥35 字长句 1-2 |
| — | **D4 连接词控制（warning）** | 段落开头禁用"首先/其次/值得注意的是"；≤6 个/千字 |
| — | **D5 术语变体（warning）** | 每 800 字替换同义术语（"重要"→"关键/绕不开/真正"） |

## 视觉设计纪律

- 最多 1 个强调色，饱和度 < 80%
- 禁止纯黑/纯白，用 off-black/off-white
- 禁止热暖系蜡笔色默认
- 全部使用 CSS 变量（`var(--accent)` 等）
- 主题变量由 `theme/report-themes.css` 管理（从 teach_more_pic 的 DESIGN.md 自动生成，禁止手改）
- 页面结构复用 `references/page-types.md` 中的 9 种标准模板，不要自创页面布局
