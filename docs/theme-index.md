# context2html — 主题索引

共 20 个主题，由 `scripts/generate-theme-css.py` 从 teach_more_pic theme/DESIGN.md 自动生成。

## 主题一览

| 主题 | 主色 | 背景 | 字体 | 圆角 | 深色 | 推荐场景 |
|---|---|---|---|---|---|---|
| `warm` | `#c0392b` | #faf9f7 | Noto Serif CJK SC, Georgia, se… | 8px |  | 通用报告 |
| `airbnb` | `#ff385c` | #ffffff | 'Airbnb Cereal VF', Circular, … | 14px |  | 旅游、生活、消费市场 |
| `airtable` | `#181d26` | #ffffff | Haas, sans-serif… | 10px |  | SaaS、数据分析 |
| `apple` | `#0066cc` | #ffffff | SF Pro Text, system-ui, -apple… | 11px |  | 消费电子、产品评测 |
| `binance` | `#fcd535` | #ffffff | BinanceNova, sans-serif… | 6px |  | 金融、区块链、投资 |
| `bmw-m` | `#ffffff` | #000000 | BMWTypeNextLatin Light, BMWTyp… | 6px | ✅ | 汽车、高端制造、运动 |
| `claude` | `#cc785c` | #faf9f5 | StyreneB, Inter, sans-serif… | 8px |  | AI 产品、设计思考 |
| `cursor` | `#f54e00` | #f7f7f4 | 'CursorGothic', sans-serif… | 8px |  | 开发者工具、编程 |
| `dell-1996` | `#e91d2a` | #ffffff | Times New Roman… | 8px |  | 复古科技、怀旧 |
| `figma` | `#000000` | #ffffff | figmaSans… | 8px |  | 设计工具、创意行业 |
| `hp` | `#024ad8` | #ffffff | Forma DJR Micro… | 4px |  | 企业服务、打印/硬件 |
| `ibm` | `#0f62fe` | #ffffff | IBM Plex Sans… | 6px |  | 企业咨询、传统IT |
| `minimax` | `#0a0a0a` | #ffffff | DM Sans… | 8px |  | AI 公司、多媒体 |
| `nike` | `#111111` | #ffffff | Helvetica Now Text… | 24px |  | 运动、品牌、消费市场 |
| `notion` | `#5645d4` | #ffffff | Notion Sans… | 8px |  | 知识管理、生产力 |
| `nvidia` | `#76b900` | #ffffff | NVIDIA-EMEA… | 2px |  | 技术报告、GPU/芯片分析 |
| `spotify` | `#1ed760` | #121212 | "SpotifyMixUI",sans-serif… | 8px | ✅ | 音乐、流媒体、娱乐行业 |
| `tesla` | `#3e6ae1` | #ffffff | "Universal Sans Text",sans-ser… | 4px |  | 汽车、新能源、工程报告 |
| `x.ai` | `#ffffff` | #0a0a0a | universalSans, Inter, system-u… | 8px | ✅ | 前沿AI、深色科技 |
| `zapier` | `#ff4f00` | #fffefb | Inter, system-ui, sans-serif… | 12px |  | 自动化、SaaS 集成 |

## 主题切换方式

- **T 键**：循环切换
- **面板按钮**：点击主题色点切换
- **自动保存**：localStorage 记住选择

## 添加新主题

1. 在 teach_more_pic 的 `theme/` 下新建目录 + DESIGN.md
2. 运行 `python scripts/generate-theme-css.py`
3. 将生成的 CSS 提交到本仓库
