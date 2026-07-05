# context2html — 通用内容可视化引擎

把文本内容自动转化为可视化 HTML 页面。支持报告、文章、文档、教程、笔记等多种内容类型。完整复用 [teach_more_pic](../teach_more_pic/) 的 29 个视觉组件体系 + 2 个自定义组件（GSAP #30、SVG.js #31）：SVG 流程图、ECharts、Three.js 3D、D3.js、CSS 条形图、时间线、对比表、GSAP 动画集等，新增报告专用模板和人类化写作约束。生成的报告支持 20 种品牌主题切换、中英双语、键盘导航。

> 本 skill 是 [teach_more_pic](../teach_more_pic/) 的兄弟技能——共用同一套视觉组件体系，差异化在报告场景（而非课程）。通用化改造后，已扩展到文章、文档、教程、笔记等多种内容类型。

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

### Python 包安装（可选 — 框架 API 需要）

```bash
cd context2html
uv pip install -e .
# 然后可在 Python 中导入框架 API：
#   from context2html.registry import ComponentRegistry
#   from context2html.renderer import TemplateRenderer
#   from context2html.theme import ThemeProvider
```

## 能力

**31 个通用视觉组件**（29 来自 teach_more_pic + 2 自定义，完整索引见 SKILL.md + `references/decision-guide.md`），覆盖报告、文章、文档、教程、笔记等场景。优先选择 ECharts 交互式图表 #26 而非静态 HTML 表格：

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

# 框架 API 快速使用
python -c "
from context2html.registry import ComponentRegistry
reg = ComponentRegistry()
print(f'{len(reg.list_components())} components loaded')
print(f'#26 deps: {reg.resolve_dependencies([26])}')
"
```

## 快速开始（框架 API）

context2html 提供三个可编程模块，安装后可直接导入：

```python
from context2html.registry import ComponentRegistry
from context2html.theme import ThemeProvider
from context2html.renderer import TemplateRenderer
```

```bash
# 安装框架包
uv pip install -e .

# 查看组件
python -c "
from context2html.registry import ComponentRegistry
reg = ComponentRegistry()
print(f'{len(reg.list_components())} components loaded')
print(f'#26 deps: {reg.resolve_dependencies([26])}')
"
```

完整工作流请参考 `SKILL.md`（示例工作流 + Framework API 参考）。

## 项目结构

```
├── SKILL.md                     ← 入口文档（示例工作流 + Framework API 参考）
├── context2html/                ← Python 框架包
│   ├── __init__.py
│   ├── registry.py              组件注册表（按内容类型/依赖查询组件）
│   ├── renderer.py              模板渲染器（一键组装组件到模板）
│   └── theme.py                 主题提供器（程序化查询和推荐主题）
├── components/                  31 视觉组件 .md（所有组件含 YAML front matter 元数据）
├── templates/
│   ├── starter.html             通用骨架模板（report/article/doc/tutorial/note）
│   ├── report-starter.html      报告骨架模板
│   ├── base-styles.css          CSS 唯一源（用 sync-template-styles.py 同步）
│   ├── flowchart-vertical.svg   SVG 模板——垂直流程图
│   ├── cycle-diagram.svg        SVG 模板——循环图
│   ├── comparison-side-by-side.svg   SVG 模板——并排对比
│   ├── timeline-horizontal.svg  SVG 模板——水平时间线
│   └── start-server.ps1/.sh     本地 HTTP 服务器启动脚本
├── scripts/
│   ├── _validate_common.py      共享验证核心（12 个共享 check_* 函数）
│   ├── validate-report.py       报告验证脚本（21 硬性 + 3 warning）
│   ├── validate-lesson.py       课程验证脚本
│   ├── test_validate_report.py  报告验证测试（624 lines）
│   ├── test_validate_lesson.py  课程验证测试（452 lines）
│   ├── test_generate_theme_css.py  主题 CSS 测试（195 lines）
│   ├── test_checks_content_type.py 内容类型检查测试（256 lines）
│   ├── test_integration_report.py  集成测试（102 lines）
│   ├── test_registry.py         组件注册表测试（11 tests）
│   ├── test_renderer.py         模板渲染器测试（6 tests）
│   ├── test_theme.py            主题提供器测试（8 tests）
│   ├── extract-component.py     组件代码提取工具
│   ├── generate-theme-css.py    从 DESIGN.md 自动生成主题 CSS（20 主题）
│   └── sync-template-styles.py  同步 base-styles.css 到 HTML 模板
├── theme/
│   ├── report-themes.css        20 主题 CSS（自动生成）
│   ├── theme-index.json         主题元数据索引（含 recommend_for/recommend_topics）
│   └── <brand>/DESIGN.md        各品牌主题设计文件
├── libs/                        外部库离线包（CDN 优先，本地回退）
├── references/
│   ├── decision-guide.md        组件选择矩阵 + 主题推荐表
│   ├── humanize_matrix.md       D1-D5 人类化写作案例
│   └── page-types.md            9 种页面类型代码参考
├── examples/
│   ├── 0001-demo-report.html    全球 AI 芯片市场调研报告
│   ├── gsap-demo.html           GSAP 滚动动画集演示
│   ├── heatmap-demo.html        热力图演示（Canvas）
│   └── report-themes.html       20 主题预览页（敲 T 键循环切换）
├── docs/
│   └── agents/                  工程技能配置（issue tracker / triage labels / domain docs）
├── pyproject.toml               uv 包管理配置
└── uv.lock

## CDN + 本地回退策略

所有外部库（JS/CSS）默认从 jsDelivr CDN 加载，CDN 失败时自动回退本地文件：

```
CDN:    https://cdn.jsdelivr.net/gh/qwerkilo/context2html@main/libs/echarts.min.js
                                                          └─ theme/report-themes.css
回退:    libs/echarts.min.js 或 ../theme/report-themes.css（本地文件）
```

- 模板内置 `__loadLib(name, fallbackPath)` 处理 CDN 优先加载
- `libs/` 和 `theme/` 目录保持存在（作为离线回退 + validator 检查）
- `validate-report.py` 支持混合模式：接受 CDN URL 作为有效来源，同时检查本地回退文件存在

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

## 人类化维度（D1-D5）

参见 `SKILL.md` Step 2.5。三项自动化检查（D1/D4/D5）通过 `validate-report.py` 输出 warning，两项（D2/D3）需人工 review。

## 更新日志

### 2026-07-05 — Framework v0.1.0

- **Python 框架包** — 新增 `context2html/` 包（`registry.py` / `renderer.py` / `theme.py`），通过 `uv pip install -e .` 安装。其他技能可编程调用组件和主题
- **组件元数据** — 全部 31 个组件 .md 增加 YAML front matter，含 `id/name/dependencies/compat_types/degrade_to/requires_3d`。`ComponentRegistry` 可按内容类型过滤、解析依赖
- **模板渲染器** — `TemplateRenderer.assemble()` 一键将组件组装到模板，替代手动 copy-paste。支持两个模板（starter/report-starter）
- **主题推荐** — `theme/theme-index.json` 扩展 `recommend_for` / `recommend_topics` 字段。`ThemeProvider.recommend_theme()` 按内容类型和主题词推荐
- **SKILL.md 双层重构** — 拆分为 Framework API 参考 + 示例工作流。Agent 可跟随示例流或直接用 API 组合自己的流程
- **新测试 25 个** — registry（11）、renderer（6）、theme（8），覆盖框架模块公共 API
- **包管理** — 新增 `pyproject.toml`，零运行时依赖，仅 dev 依赖 pytest

### 2026-07-04

- **通用化改造** — 从"调研报告专用"升级为通用内容→HTML 引擎。新增 `templates/starter.html` 通用骨架 + `data-content-type` CSS 变量驱动 5 种布局（report/article/doc/tutorial/note），保留 `report-starter.html` 向后兼容
- **模板 CSS 提取** — 共享 CSS 抽到 `templates/base-styles.css` 作为唯一源，`scripts/sync-template-styles.py` 自动同步回 HTML 模板，消除 starter.html / report-starter.html 之间的 CSS 重复
- **验证器模块化** — `validate-report.py` 从 387 行精简为 42 行编排层；提取 `checks/content_type.py`（内容类型检测）和 `checks/report.py`（13 个检查 + D1-D5）；验证器按 `data-content-type` 动态加载检查规则
- **组件提取工具** — 新增 `scripts/extract-component.py`，从组件 .md 自动提取 HTML/CSS/JS 代码块，支持管道使用
- **测试覆盖提升** — 总测试数 293→376（+28%），覆盖 content-type 检查、结构检查、theme CSS 生成、集成测试、D1-D5 边缘情况
- **CDN 优先 + 本地回退** — 模板新增 `__loadLib()`，所有库（JS/CSS）优先从 jsDelivr CDN 加载，失败自动回退本地 `libs/` / `theme/`。验证器同步支持 CDN 路径识别
- **Bug 修复** — 8 项修复：L 键检测正则改进、GSAP CDN 版本硬编码改为通配、ECharts GL 检测加词边界、中文断句避免 A.I. 误断、ECharts var() 覆盖模板字符串、D1 连续相似长度全量报告、移除冗余 CSS transition、手动主题 --font-h 添加 fallback
- **性能优化** — 3 轮：验证器正则预编译 + `lru_cache` 缓存 `_extract_para_texts`/`_get_style_css`；主题 CSS 生成改用 `CSafeLoader`（54% 加速，1.0s → 0.46s）；消除 style 块重复扫描
- **GSAP demo 修复** — `examples/gsap-demo.html` 中脚本路径 `libs/` → `../libs/`（原路径解析到不存在的 `examples/libs/`），CDN 降级逻辑重建为统一回退
- **Heatmap demo 重写** — `examples/heatmap-demo.html`：Canvas 绘制蓝-白-红双向渐变热力图，修复 `vmin`/`vmax` 初始化 bug，内联 magicui-effects.css 避免 `file://` 协议下样式加载失败
- **组件说明优化** — 全部 31 个组件 .md 增加 `🎯 效果` 视觉预览头 + 布局参数表格 + 统一分层（效果→HTML→CSS→JS→参数表→规则→降级）
- **CSS 视觉增强** — 简单组件（#02-#06、#08-#20）新增悬停上浮 3px + 阴影加深 + `transition` 动效；同步更新 10 个对应的 demo HTML

## 依赖

- [teach_more_pic](https://github.com/qwerkilo/teach_more_pic) — 视觉组件来源（**必装**，29 个组件 + magicui-effects.css）
