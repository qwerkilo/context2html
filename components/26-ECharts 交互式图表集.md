### 26. ECharts 交互式图表集

> **🎯 效果**：Apache ECharts 渲染的高质量交互式图表，支持悬浮提示（tooltip）、自适应缩放（resize）、4 种图表——柱状图 / 饼图 / 折线图 / 堆叠面积图。颜色通过 `gv('--accent')` 读取 CSS 变量跟随主题。需 `libs/echarts.min.js`。

#### 前置依赖

ECharts 库需要独立下载到本地 `libs/` 目录。两种加载方式：

**离线加载（推荐）** — 在报告中使用前先准备好本地文件：

```bash
# PowerShell（Windows）
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js" -OutFile "libs/echarts.min.js"

# macOS / Linux
mkdir -p libs && curl -Lo libs/echarts.min.js https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js
```

```html
<!-- 报告中引用本地文件 -->
<script src="libs/echarts.min.js"></script>
```

**CDN 加载（备选）** — 需要网络，适合快速原型：

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

#### 26a — 纵向柱状图

```html
<div id="chart-bar" style="width:100%;height:350px;margin:1rem 0;"></div>
```

```css
#chart-bar { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var chart = echarts.init(document.getElementById('chart-bar'));
chart.setOption({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['中国','美国','日本','德国'], axisLabel: { color: gv('--muted') } },
  yAxis: { type: 'value', axisLabel: { color: gv('--muted') } },
  series: [{ type: 'bar', data: [17.7, 25.5, 4.2, 4.0], itemStyle: { color: gv('--accent') } }],
  grid: { left: 50, right: 20, top: 20, bottom: 40 }
});
```

#### 26b — 饼图

```html
<div id="chart-pie" style="width:100%;height:300px;margin:1rem 0;"></div>
```

```css
#chart-pie { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var pie = echarts.init(document.getElementById('chart-pie'));
pie.setOption({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie', radius: ['30%','60%'],
    data: [
      { value: 45, name: '消费', itemStyle: { color: gv('--accent') } },
      { value: 25, name: '投资', itemStyle: { color: gv('--success') } },
      { value: 20, name: '政府支出', itemStyle: { color: gv('--warning') } },
      { value: 10, name: '净出口', itemStyle: { color: gv('--error') } }
    ],
    label: { color: gv('--text') }
  }]
});
```

#### 26c — 折线图

```html
<div id="chart-line" style="width:100%;height:350px;margin:1rem 0;"></div>
```

```css
#chart-line { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var line = echarts.init(document.getElementById('chart-line'));
line.setOption({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['2020','2021','2022','2023','2024'], axisLabel: { color: gv('--muted') } },
  yAxis: { type: 'value', axisLabel: { color: gv('--muted') } },
  series: [{ type: 'line', data: [2.3, 5.1, 8.0, 3.5, 2.8], smooth: true, lineStyle: { color: gv('--accent'), width: 3 }, itemStyle: { color: gv('--accent') } }],
  grid: { left: 50, right: 20, top: 20, bottom: 40 }
});
```

#### 26d — 堆叠条形图

```html
<div id="chart-stacked" style="width:100%;height:350px;margin:1rem 0;"></div>
```

```css
#chart-stacked { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var stacked = echarts.init(document.getElementById('chart-stacked'));
stacked.setOption({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { textStyle: { color: gv('--text') } },
  xAxis: { type: 'value', axisLabel: { color: gv('--muted') } },
  yAxis: { type: 'category', data: ['2020','2021','2022','2023'], axisLabel: { color: gv('--muted') } },
  series: [
    { name: '农业', type: 'bar', stack: 'total', data: [15, 14, 13, 12], itemStyle: { color: gv('--chart-4') } },
    { name: '工业', type: 'bar', stack: 'total', data: [38, 40, 39, 37], itemStyle: { color: gv('--chart-3') } },
    { name: '服务业', type: 'bar', stack: 'total', data: [47, 46, 48, 51], itemStyle: { color: gv('--accent') } }
  ],
  grid: { left: 60, right: 30, top: 40, bottom: 30 }
});
```

#### 使用规则

- 每个图表需要唯一的 `id`（如 `chart-bar-1`、`chart-gdp`），多个图表时不可重复
- `height` 建议 250-400px，根据需要调整
- 颜色值用 `gv('--accent')` 调用主题变量，函数自动解析 CSS 变量为实际色值
- 数据中的中文标签需要确保 font-family 可渲染
- 如需响应式：`window.addEventListener('resize', function(){ chart.resize(); })`

#### 降级说明

- **JS 禁用时**：显示 `<div class="no-js-fallback"><p>图表加载需要 JavaScript</p></div>`
- **ECharts 未加载**：`echarts` 变量为 `undefined`，用 `typeof echarts !== 'undefined'` 保护
- **容器未渲染**：容器在 `DOMContentLoaded` 之后初始化，`chart.resize()` 在容器可见后调用
- **截图/打印**：ECharts 支持 `chart.getDataURL({type:'png'})` 导出为图片
