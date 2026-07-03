# context2html — 调研报告可视化

把调研内容/研究报告自动转化为可视化 HTML 报告。完整复用 [teach_more_pic](../teach_more_pic/) 的 29 个视觉组件体系 + 2 个自定义组件（GSAP #30、SVG.js #31）：SVG 流程图、ECharts、Three.js 3D、D3.js、CSS 条形图、时间线、对比表、GSAP 动画集等，新增报告专用模板和人类化写作约束。生成的报告支持 20 种品牌主题切换、中英双语、键盘导航。

> 本 skill 是 [teach_more_pic](../teach_more_pic/) 的兄弟技能——共用同一套视觉组件体系，差异化在报告场景（而非课程）。

## 安装

### 前提

本技能需要 [opencode](https://opencode.ai) 环境。已安装了以下 base skill：
- [teach_more_pic](https://github.com/qwerkilo/teach_more_pic) — 视觉组件来源（**必装**，本项目的 29 个组件来源于此）

### 发给 agent 安装

```
帮我安装以下技能：
1. teach_more_pic — https://github.com/qwerkilo/teach_more_pic
2. context2html — https://github.com/qwerkilo/context2html
都克隆到 ~/.agents/skills/ 目录下。
```

### 手动安装

```bash
cd ~/.agents/skills
git clone https://github.com/qwerkilo/teach_more_pic
git clone https://github.com/qwerkilo/context2html
```

### 通过 AGENTS.md 配置

在项目根目录的 `AGENTS.md` 中引用：

```
Skills: teach_more_pic, context2html
```

## 能力

**31 个视觉组件**（29 来自 teach_more_pic + 2 自定义，完整索引见 SKILL.md + `references/decision-guide.md`）优先选择 ECharts 交互式图表 #26 而非静态 HTML 表格：

- **#1-7 核心**：SVG 流程图 / 角色卡片 / CSS 时间线 / CSS 条形图 / 对比表 / SVG 容器 / PPT 质感（主题切换 + 语言切换 + 滚动动画 + 键盘导航 + 目录）
- **#8-14 交互式**：折叠分步详解 / Tab 切换面板 / 图片对比滑块 / 交互式时间线 / 数据卡片网格 / 引文卡片 / 标注式图片
- **#15-29 数据与辅助**：状态链 / 数值滚动动画 / **标签徽章组**（每章结尾必用，带 `#` 前缀） / 告警条 / 热力图 / 步骤指示器 / 信息面板 / 对比表增强版 / 灯箱 / **ECharts 交互式图表**（柱状/饼/折线/堆叠，需 `libs/echarts.min.js`） / **Three.js 3D**（3D 可视化，需 `libs/three.min.js`，含 Sprite 文字标签） / **D3.js 自定义图表**（力导向图/旭日图/桑基图，需 `libs/d3.min.js` + `d3-sankey.min.js`） / **ECharts GL 3D**（3D 柱状/散点/地球，需 `libs/echarts-gl.min.js`） / 现代浏览器 API（原生折叠/模态/幻灯片/Popover）
- **#30 GSAP 滚动动画集**：5 种模式（fade / stagger / parallax / flip / zoom），桌面端离线加载 `libs/gsap.min.js` + `libs/ScrollTrigger.min.js`，移动端自动降级 CDN
- **#31 SVG.js 动态图表**：4 种图表（动态柱状/多系列折线/流程图/进度环），轻量级（78KB），CSS 变量响应式 + 内置动画 `element.animate()`，需 `libs/svg.min.js`
- **20 品牌主题** — 38+ CSS 变量（含 `--chart-*` / `--shadow-*` / `--table-*` / `--tag-*` 等），`var(--accent/border/surface/...)` 自动跟随
- **主题切换动画** — 0.35s 平滑过渡，`prefers-reduced-motion` 自动禁用
- **9 种报告页面类型** — 封面 / 摘要 / 关键数字 / 目录 / 章节正文 / 对比分析 / 结论与建议 / 附录 / 页脚（`references/page-types.md` 含完整代码参考）
- **3D/GL 增强** — 8 个 3D 可视化场景（ECharts GL 3D 地球、Three.js 3D 柱状图、D3+Three 网络等）

## 使用方法

在 opencode 中同时激活两个 skill：

```
Skills: teach_more_pic, context2html
```

`teach_more_pic` 提供视觉组件源；`context2html` 负责报告流程编排和人类化写作约束。

```bash
# 验证报告 HTML
python scripts/validate-report.py examples/NNNN-report.html

# SVG XML 检查
python -c "import xml.etree.ElementTree as ET; ET.parse('path.svg')"

# 启动本地预览服务器
powershell -ExecutionPolicy Bypass -File templates/start-server.ps1
```

## 报告生成流程

0. **人类化写作约束** — Agent 遵循 SKILL.md 中 D1-D5 规则生成正文：句长分布多峰、段落结构轮换、信息密度交替、连接词压降到 ≤6/千字、术语变体 ≥1 处/800 字
1. **输入获取** — 从对话上下文或文件路径读取调研内容
2. **结构规划** — 设计章节大纲（推荐 3-6 章）、关键发现摘要（3-5 条）、标记可视化数据点
3. **组件选择** — 按 `references/decision-guide.md` 矩阵选型，对比分析优先 ECharts #26 交互式图表，次选 HTML 对比表 #5/#22，每 500 字 ≥1 视觉元素
4. **HTML 生成** — 从 `templates/report-starter.html` 复制骨架，填充中英双语正文，合并组件 CSS/JS
5. **验证输出** — run `scripts/validate-report.py`，**21 项硬性检查 + 3 项人类化建议（warning）** 全通过后交付。对比表响应式堆叠、内联 SVG 对比、ECharts 依赖路径、英文布局（overflow-wrap + table-layout:fixed）、ECharts Canvas 颜色用法、GSAP data-gsap 模式验证、章节交叉引用 `#chN`、data-anim 语法、D1 句长交替、D4 连接词控制、D5 术语变体均已覆盖

## 项目结构

```
├── SKILL.md                     ← 唯一入口，含 5 步工作流 + D1-D5 人类化写作指令
├── components/                  31 个视觉组件 .md（29来自 teach_more_pic + 2自定义 GSAP #30 + SVG.js #31）
├── templates/
│   ├── report-starter.html      报告骨架模板（9 种页面类型 + 工具栏 + 主题系统）
│   ├── flowchart-vertical.svg   SVG 模板——垂直流程图
│   ├── cycle-diagram.svg        SVG 模板——循环图
│   ├── comparison-side-by-side.svg   SVG 模板——并排对比
│   ├── timeline-horizontal.svg  SVG 模板——水平时间线
│   └── start-server.ps1/.sh     本地 HTTP 服务器启动脚本
├── scripts/
│   ├── _validate_common.py      共享验证核心（12 个共享 check_* 函数）
│   ├── validate-report.py       报告验证脚本（21 硬性 + 3 warning）
│   ├── validate-lesson.py       课程验证脚本（继承共享核心 + 课程专有检查）
│   ├── test_validate_report.py  报告验证测试（145 tests）
│   ├── test_validate_lesson.py  课程验证测试（107 tests）
│   ├── test_generate_theme_css.py  主题 CSS 测试（22 tests）
│   └── generate-theme-css.py    从 teach_more_pic DESIGN.md 自动生成主题 CSS（20 主题）
├── theme/
│   ├── report-themes.css        20 主题 CSS（自动生成，含 --chart-* / --shadow-* / --table-* 等 25+ CSS 变量）
│   └── theme-index.json         主题元数据索引
├── libs/                        外部库（echarts / echarts-gl / three / d3 / d3-sankey / gsap / ScrollTrigger / svg 离线包）
├── references/
│   ├── decision-guide.md        报告场景组件选择矩阵 + 主题推荐表
│   └── page-types.md            9 种页面类型 HTML/CSS 代码参考
├── examples/
│   ├── 0001-demo-report.html    全球 AI 芯片市场调研报告（示例 + humanize 参考）
│   ├── gsap-demo.html           GSAP 滚动动画集——5 种模式演示
│   └── report-themes.html       20 主题预览页（敲 T 键循环切换）
└── docs/
    ├── agents/                  工程技能配置（issue tracker / triage labels / domain docs）
    └── theme-index.md           主题元数据文档

### Magic UI 装饰效果（来自 teach_more_pic）

通过 `libs/magicui-effects.css` 共享 13 种 CSS 装饰效果：

| 效果 | CSS 类 | 说明 |
|---|---|---|
| 光泽扫光 | `.shiny-text` | 封面/标题光泽扫光动画 |
| 噪点纹理 | `.noise-overlay` | SVG feTurbulence 噪点叠加层 |
| 圆点网格 | `.dot-bg` | CSS radial-gradient 圆点背景 |
| 直线网格 | `.grid-bg` | CSS linear-gradient 双线网格背景 |
| 流星雨 | `.meteors-container` + `.meteor` | 封面装饰流星动画 |
| 边框发光 | `.border-glow` | conic-gradient 旋转边框 |
| 辉光悬停 | `.glare-hover` | 背景渐变过渡，鼠标悬停触发 |
| 渐变文字 | `.gradient-text` | 多色渐变流动动画 |
| 模糊淡入 | `data-anim="blur"` | 滚动模糊淡入（filter blur + opacity） |
| 霓虹卡片 | `.neon-card` | 霓虹渐变色边框 |
| 聚光灯卡片 | `.spotlight-card` | 鼠标追踪聚光灯效果 |
| 交互按钮 | `.interactive-btn` | 点击波纹扩散按钮 |
| 打字光标 | `.typing-cursor` | 闪烁打字光标 |

所有效果适配 CSS 变量（`var(--accent)`、`var(--surface)` 等），自动跟随主题切换。

## 人类化维度（D1-D5，自动化检查）

报告正文默认执行人类化写作约束（SKILL.md 中完整定义）：

| 维度 | 约束 | 自动化检查位置 |
|------|------|---------|
| D1-句长分布 | 每段 ≤10 字短句 + ≥35 字长句各 ≥1 | `validate-report.py:check_d1_sentence_length`（warning） |
| D2-段落结构 | 相邻段落使用不同结构模板（5 种轮换） | 人工检查（参考 `references/humanize_matrix.md`） |
| D3-信息密度 | 连续两段密度差 ≥ 15%，高-低-高交替 | 人工检查 |
| D4-连接词 | ≤6 个/千字，禁止段首 AI 高频词 | `validate-report.py:check_d4_connectors`（warning） |
| D5-术语变体 | 每 800 字 ≥ 1 处同义学术替代 | `validate-report.py:check_d5_term_variety`（warning） |

D1/D4/D5 三项已实现为 warning 级自动化检查（不阻断构建但提示需修复）。D2/D3 仍需人工 review。

## 依赖

- [teach_more_pic](https://github.com/qwerkilo/teach_more_pic) — 视觉组件来源（**必装**，29 个组件 + magicui-effects.css）
