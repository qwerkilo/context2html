# context2html — 调研报告可视化 Skill 设计规格

## 概述

将调研内容/研究报告自动转化为可视化 HTML 报告的 Agent skill。完整复用 `teach_more_pic` 的 28 个视觉组件、离线库和模板基础设施，新增报告专用模板和工作流。

## 项目结构

```
context2html/
├── SKILL.md
├── README.md
├── templates/
│   └── report-starter.html      ← 从 lesson-starter.html 改造
├── components/                  ← 完整复制自 teach_more_pic
│   ├── 01-SVG 流程图.md ~ 29-ECharts GL 3D可视化.md
│   └── ... (28 个)
├── references/
│   ├── decision-guide.md        ← 报告场景组件选择映射（含 3D/GL）
│   └── page-types.md            ← 报告 8 种页面类型
├── libs/                        ← 完整复制（echarts/three/d3 离线包）
│   ├── echarts.min.js
│   ├── echarts-gl.min.js
│   ├── three.min.js
│   ├── three.module.js
│   ├── d3.min.js
│   ├── d3-sankey.min.js
│   └── magicui-effects.css
├── scripts/
│   └── validate-report.py
└── examples/
    └── 0001-demo-report.html
```

## 报告模板结构

继承 `lesson-starter.html` 的 CSS 变量系统、20 主题、PPT 质感 JS（T 键切换、键盘导航、语言切换），改造以下部分：

### 变更清单

| 课程模板元素 | 报告模板处理 |
|-------------|------------|
| `cover-page` | 保留 + 增加摘要行、元数据（日期/作者/来源） |
| 三幕 `section-divider` | → 替换为 `report-chapter`（可重复 N 章） |
| `summary-cards` (3 张) | → 替换为 `conclusion-page`（建议列表） |
| `quiz-section` (5 题) | ❌ 删除 |
| — | ✅ 新增 `exec-summary`（摘要/关键发现） |
| — | ✅ 新增 `key-numbers`（关键数字页，可选） |
| — | ✅ 新增 `report-toc`（自动编号目录） |
| — | ✅ 新增 `comparison-page`（对比分析页，可选） |
| — | ✅ 新增 `appendix`（附录：数据来源/方法说明） |
| — | ✅ 新增 `report-footer`（脚注） |

### 骨架结构

```html
<html lang="zh-CN" data-theme="warm">
<head>
  <style>
    /* 模板 CSS 变量 + 20 主题 + 正文排版（报告风格字重/行距） */
    /* ===== 组件 CSS 从此处插入（按前缀分组） ===== */
  </style>
</head>
<body>
  <article class="cover-page">        <!-- 标题 + 摘要行 + 元数据 -->
  <section class="exec-summary">       <!-- 关键发现摘要 -->
  <section class="key-numbers">        <!-- 关键数字（可选） -->
  <nav class="report-toc">            <!-- 自动编号目录 -->

  <section class="report-chapter">     <!-- 第一章 -->
    <h2>章节标题</h2>
    <p data-lang="zh">...</p>
    <p data-lang="en">...</p>
    <!-- INSERT: 视觉组件 HTML -->
  </section>

  <section class="report-chapter"> ... </section>  <!-- 更多章节 -->

  <section class="comparison-page">    <!-- 对比分析（可选） -->
  <aside class="conclusion-page">      <!-- 结论与建议 -->
  <section class="appendix">           <!-- 附录 -->
  <footer class="report-footer">       <!-- 脚注 -->

  <div class="ui-toolbar">             <!-- 保留 -->
  <!-- PPT 质感增强 JS（保留） -->
  <!-- ===== 组件 JS 从此处插入（可选） ===== -->
</body>
</html>
```

## 核心工作流（SKILL.md 流程）

### Step 0: 输入获取
- 从对话上下文中提取已有调研内容
- 或读取用户提供的文件路径
- 确认：报告主题、目标受众、关键数据点数量
- 🛑 STOP

### Step 1: 报告结构规划
- 决定章节数（推荐 3-6 章）
- 设计关键发现摘要
- 标记适合可视化的数据点
- 🛑 STOP

### Step 2: 选择视觉组件
- 从组件索引选择，按报告场景映射

| 报告内容类型 | 推荐组件 | 优先级 |
|------------|---------|--------|
| 数据对比（柱状/折线/饼图） | ECharts #24 | ⭐⭐⭐ |
| 3D 数据分布 | Three.js 3D 柱状图 #25 | ⭐⭐⭐ |
| 3D 地理分布 | ECharts GL 3D 地球 #28 | ⭐⭐⭐ |
| 3D 散点/聚类 | ECharts GL 3D 散点图 #28 | ⭐⭐ |
| 3D 趋势曲面 | ECharts GL 3D 曲面 #28 | ⭐⭐ |
| 3D 关系网络 | Three.js + D3 组合 #25+#27 | ⭐⭐ |
| 3D 产品展示 | Three.js 3D 场景 #25 | ⭐⭐ |
| 数据故事动画 | Three.js TSL #25 | ⭐ |
| 3D 堆叠对比 | ECharts GL 3D 柱状图 #28 | ⭐⭐ |
| 数值高低分布 | 热力图 #19 | ⭐⭐ |
| 流程/架构说明 | SVG 流程图 #1 | ⭐⭐⭐ |
| 时间线事件 | CSS 时间线 #3 / 交互式时间线 #11 | ⭐⭐ |
| 关键指标 | 数据卡片网格 #12 / 数值滚动 #16 | ⭐⭐⭐ |
| 多维度对比 | 对比表增强版 #22 | ⭐⭐ |
| 来源引用 | 引文卡片 #13 | ⭐⭐ |
| 复杂概念分步 | 折叠分步 #8 / Tab 面板 #9 | ⭐⭐ |
| 关系网络 | D3 力导向图 #27 | ⭐ |
| 状态/进度 | 状态链 #15 / 步骤指示器 #20 | ⭐ |
| 提示/警告 | 告警条 #18 | ⭐ |
| 补充信息 | 信息面板 #21 | ⭐ |
| 标签/关键词 | 标签组 #17（每章结尾必用） | ⚠️ 强制 |
| 图片说明 | SVG Figure #6 / 标注式图片 #14 | ⭐⭐ |

- 每 500 字至少 1 个视觉元素
- 数据密集型报告优先使用 Three.js #25 和 ECharts GL #28
- 🛑 STOP

### Step 3: 生成 HTML
- 复制 `templates/report-starter.html`
- 填充封面元数据
- 编写摘要 + 每章正文（中英双语 data-lang）
- 嵌入选定组件（与 teach_more_pic 完全相同的合并规则）
- 生成自动编号目录

### Step 4: 验证
- SVG XML 有效性
- 组件渲染检查
- 双语成对检查
- 链接完整性
- 🛑 STOP

### Step 5: 输出
- 生成 `report-slug.html`
- 可选附带 `libs/` 目录

## 与 teach_more_pic 的差异

| 维度 | teach_more_pic | context2html |
|------|---------------|--------------|
| 触发词 | 课程/教学/lesson | 报告/调研/research/report |
| 前置步骤 | grill-me 需求拷问 | 输入获取（读取已有内容） |
| 叙事 | 三幕故事 | 报告章节（3-6 章） |
| 页面类型 | 封面/三幕/总结/测验 | 封面/摘要/目录/章节/结论/附录 |
| 组件 | 28 个 | 完全相同（复用） |
| 每章约束 | 每课最少 6 组件 | 每 500 字至少 1 视觉元素 |
| 验证 | 课程验证脚本 | 报告验证脚本 |
| 后续 | SPA 集成 + KG | 无 SPA/KG |
| 语言 | 中英双语 | 中英双语（继承） |

## 复用策略

- `components/`：完整复制 teach_more_pic 的 28 个组件 markdown 文件
- `templates/report-starter.html`：从 `lesson-starter.html` 改造，保留 CSS 变量/主题/PPTJS
- `libs/`：完整复制（echarts/three/d3 离线包 + magicui-effects.css）
- `references/decision-guide.md`：改写为报告场景选择矩阵
- `references/page-types.md`：改写为报告 8 种页面类型
- `scripts/validate-report.py`：从 `validate-lesson.py` 改造，去掉课程专用检查项

## 视觉设计纪律

继承 teach_more_pic 的全部纪律：
- 最多 1 个强调色，饱和度 < 80%
- 禁止纯黑/纯白
- 禁止热暖系蜡笔色默认
- 颜色语义：蓝=正常，橙=触发，红=崩溃，绿=救助
- 所有颜色使用 CSS 变量（`var(--accent)` 等）
- 渐变文本只用于极小标题
