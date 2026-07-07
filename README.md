# context2html — 通用内容可视化引擎

**Docs hierarchy:** `SKILL.md` (workflow + API) → `AGENTS.md` (agent quick ref) → `README.md` (this file, overview).

把文本内容自动转化为可视化 HTML 页面。支持报告、文章、文档、教程、笔记等多种内容类型。完整复用 [teach_more_pic](../teach_more_pic/) 的 29 个视觉组件体系 + 2 个自定义组件（GSAP #30、SVG.js #31）。

提供 **Python 框架 API**（`context2html/` 包）：组件注册表、模板渲染器、主题推荐、验证器——其他技能和 agent 可直接导入使用。

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

### Python 包安装（框架 API 需要）

```bash
cd context2html
uv pip install -e .
```

安装后可在 Python 中导入框架 API：

```python
from context2html.registry import ComponentRegistry
from context2html.renderer import TemplateRenderer
from context2html.theme import ThemeProvider
from context2html.validator import check_h1_count, check_bilingual
from context2html.markdown_utils import parse_front_matter
```

## 框架 API 速查

### 组件注册表

```python
reg = ComponentRegistry()
all = reg.list_components()                          # 全部 31 组件
compat = reg.list_components(content_type='report')   # 按内容类型过滤
c = reg.list_components(id=26)[0]                     # 按 ID 查询（返回 list）
deps = reg.resolve_dependencies([26, 28])             # 解析库依赖

# c.metadata  → .id, .name, .dependencies, .compat_types, .degrade_to, .requires_3d
# c.html / .css / .js  → 已提取的代码块（含子图表）
```

### 模板渲染器

```python
renderer = TemplateRenderer()
html = renderer.assemble(
    template_name='starter',           # 'starter' 或 'report-starter'
    components=[26, 17],               # 组件 ID 列表
    theme_name='warm'                  # 主题
)
# 返回完整 HTML，组件已插入、CSS 已合并、JS 已追加
```

### 主题提供器

```python
tp = ThemeProvider()
theme_list = tp.list_themes()                # 20 主题
theme = tp.get_theme('warm')                 # 按名称查询
best = tp.recommend_theme('report', '经济')   # 按内容类型+主题词推荐
# theme.accent, .bg, .text, .chart_colors, .recommend_for, .recommend_topics
```

### 验证器

```python
from context2html.validator import (
    check_h1_count, check_bilingual,
    check_svg_links, check_lib_deps,
    check_d1_sentence_length, check_d4_connectors,
    detect_content_type, check_content_type_valid,
    # ... 全部 30+ 检查函数
)
```

### 工具函数

```python
from context2html.markdown_utils import (
    parse_front_matter,           # YAML front matter 解析
    extract_code_block,           # 代码块提取（支持 multi=True）
    extract_js_from_md,           # JS 提取
)
```

完整工作流请参考 `SKILL.md`（示例工作流 + Framework API 参考）。

## 能力

**31 个通用视觉组件**（29 来自 teach_more_pic + 2 自定义），覆盖报告、文章、文档、教程、笔记等场景：

- **#1-7 核心**：SVG 流程图 / 角色卡片 / CSS 时间线 / CSS 条形图 / 对比表 / SVG 容器 / PPT 质感
- **#8-14 交互式**：折叠分步详解 / Tab 切换面板 / 图片对比滑块 / 交互式时间线 / 数据卡片网格 / 引文卡片 / 标注式图片
- **#15-29 数据与辅助**：状态链 / 数值滚动动画 / 标签徽章组 / 告警条 / 热力图 / 步骤指示器 / 信息面板 / 对比表增强版 / 灯箱 / ECharts 交互式图表 / Three.js 3D / D3.js 可视化 / ECharts GL 3D / 现代浏览器 API
- **#30 GSAP 滚动动画集**：5 种模式（fade / stagger / parallax / flip / zoom）
- **#31 SVG.js 动态图表**：4 种图表（动态柱状/多系列折线/流程图/进度环）

**20 品牌主题** — 38+ CSS 变量，`var(--accent/border/surface/...)` 自动跟随。**5 内容类型** — report/article/doc/tutorial/note，`data-content-type` 驱动布局。**中英双语** — 所有文本块需 `data-lang` 成对，L 键切换。

## 项目结构

```
├── SKILL.md                     ← 入口文档（示例工作流 + Framework API 参考）
├── context2html/                ← Python 框架包
│   ├── __init__.py
│   ├── registry.py              组件注册表
│   ├── renderer.py              模板渲染器
│   ├── theme.py                 主题提供器
│   ├── markdown_utils.py        YAML 解析 + 代码块提取
│   └── validator/               验证器（30+ 检查函数）
│       ├── __init__.py
│       ├── common.py           通用检查（h1/bilingual/lib-deps 等）
│       ├── svg.py              SVG 检查
│       ├── report.py           报告专有检查 + D1-D5
│       └── content_type.py     内容类型检测
├── components/                  31 视觉组件 .md（含 YAML front matter）
├── templates/                   模板（starter / report-starter / SVG 模板）
├── scripts/
│   ├── validate-report.py       报告验证 CLI（薄包装，导入 context2html.validator）
│   ├── validate-lesson.py       课程验证（独立于框架包）
│   ├── generate-theme-css.py    主题 CSS 生成器
│   ├── sync-template-styles.py  base-styles.css 同步
│   ├── extract-component.py     组件代码提取 CLI
│   ├── conftest.py              测试路径配置
│   └── test_*.py                453 个测试
├── theme/                       20 主题（report-themes.css + theme-index.json）
├── libs/                        外部库离线包（CDN 优先，本地回退）
├── references/                  组件选择矩阵 / 人类化案例 / 页面类型参考
├── examples/                    2 演示 HTML（0001-demo-report + report-themes）
├── docs/agents/                 工程技能配置
├── pyproject.toml               uv 包管理
└── uv.lock
```

## CDN + 本地回退策略

所有外部库（JS/CSS）默认从 jsDelivr CDN 加载，CDN 失败时自动回退本地文件：

```
CDN:    https://cdn.jsdelivr.net/gh/qwerkilo/context2html@main/libs/echarts.min.js
回退:    libs/echarts.min.js
```

- 模板内置 `__loadLib(name, fallbackPath)` 处理 CDN 优先加载
- `libs/` 和 `theme/` 目录保持存在（作为离线回退 + validator 检查）
- `validate-report.py` 支持混合模式：接受 CDN URL 作为有效来源，同时检查本地回退文件存在

## 人类化维度（D1-D5）

参见 `SKILL.md` Step 2.5。五项自动化检查通过 `validate-report.py` 输出 warning（D1 句长/D2 段落结构/D3 信息密度/D4 连接词/D5 术语变体）。D1-D5 词汇库（段首禁用词、连接词、高频 AI 黑话）在 `context2html/validator/report.py`。

## 更新日志

### 2026-07-07 — D2/D3 自动化 + 测试扩展

- **D2（段落结构）自动化** — 新增 `check_d2_paragraph_structure()`：检测 5 种段落模板轮换、相邻段落结构重复、段落密度差 ≥ 15%
- **D3（信息密度）自动化** — 新增 `check_d3_information_density()`：检测核心段密度 70%-85%、过渡段密度 40%-50%、连续两段密度差 ≥ 15%
- **验证器扩展** — `validate-report.py` 现在输出全部 5 项 D1-D5 warning
- **测试覆盖** — +10 D2/D3 单元测试，总数 453

### 2026-07-05 — 架构深化 + 框架完善

- **验证器迁移到框架包** — 所有 30+ 检查函数迁入 `context2html/validator/`，`from context2html.validator import check_bilingual` 可用
- **子图表提取修复** — `extract_code_block(multi=True)` 支持多块拼接，组件 #24/25/26/28/31 的子变体不再丢失
- **接口深化** — `ComponentRegistry` 从 3 方法减至 2 方法（`get_component` 合并入 `list_components(id=)`）
- **共享解析模块** — `context2html/markdown_utils.py` 合并三处重复的 YAML/代码块解析
- **generate-theme-css.py 重构** — 双 CSS 路径合并为单一 `build_theme_css()`
- **D1-D5 词汇扩展** — 段首禁用词 +4、连接词 +7、高频 AI 黑话 +10；humanize_matrix.md 25 条案例
- **`run_all` 拆分** — `run_checks` / `format_result` / CLI 三分离，`ValidationResult` dataclass
- **测试覆盖** — 443 tests（+67），含框架包 edge case + markdown_utils 多块提取 + validator 集成测试
- **文档整理** — AGENTS.md/SKILL.md/README.md 角色分离，docs hierarchy 导航

### 2026-07-04 — Framework v0.1.0 + 通用化

- **Python 框架包** — 新增 `context2html/` 包（registry/renderer/theme），`uv pip install -e .` 可安装
- **组件元数据** — 全部 31 个组件加 YAML front matter，`ComponentRegistry` 可按内容类型过滤、解析依赖
- **主题推荐** — `theme-index.json` 扩展 `recommend_for` / `recommend_topics`
- **SKILL.md 双层重构** — Framework API 参考 + 示例工作流
- **通用化改造** — 新增 `templates/starter.html` 通用骨架 + 5 种 `data-content-type` 布局
- **模板 CSS 统筹** — `base-styles.css` 作为唯一源，`sync-template-styles.py` 自动同步
- **CDN 优先 + 本地回退** — `__loadLib()` 处理 CDN→本地两级加载
- **测试覆盖** — 总测试数 293→376

## 依赖

- [teach_more_pic](https://github.com/qwerkilo/teach_more_pic) — 视觉组件来源（**必装**，29 个组件 + magicui-effects.css）
