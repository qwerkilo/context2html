### 31. SVG.js 动态图表

基于 [SVG.js v3](https://svgjs.dev/) 的轻量级 SVG 操作库（~78KB minified）。链式 API、内置动画、CSS 变量继承。

**何时用 SVG.js：**
- 需要**自定义视觉风格**的 SVG 图（流程图、关系图、动画演示）
- 想要轻量级（78KB）但比手写 SVG 更强大的 API
- 需要**内置动画**（`element.animate(duration, easing)`）而无需引入 GSAP

**何时不用：**
- 标准数据图表 → 用 ECharts #26（更强大）
- 3D 可视化 → 用 Three.js #27
- 关系网络/力导向 → 用 D3 #28
- 静态流程图 → 用 SVG 流程图 #1

#### 前置依赖

```bash
mkdir -p libs && curl -Lo libs/svg.min.js \
  https://cdn.jsdelivr.net/npm/@svgdotjs/svg.js@3.2.4/dist/svg.min.js
```

```html
<!-- 报告中引用本地文件 -->
<script src="libs/svg.min.js"></script>
```

#### 31a — 动态柱状图

每个柱子从 0 高度动画到目标值，悬停时高亮。

```html
<div id="svgjs-bar" style="width:100%;height:300px;margin:1rem 0;"></div>
```

```css
#svgjs-bar { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var data = [
  { label: '中国', value: 17.7 },
  { label: '美国', value: 25.5 },
  { label: '日本', value: 4.2 },
  { label: '德国', value: 4.0 },
  { label: '英国', value: 3.3 }
];
var palette = [gv('--chart-1'), gv('--chart-2'), gv('--chart-3'), gv('--chart-4')];
var W = 600, H = 280, PAD = 40;
var chartW = W - PAD * 2, chartH = H - PAD * 2;
var maxVal = Math.max.apply(null, data.map(function(d){return d.value;}));
var bw = chartW / data.length * 0.7;
var gap = chartW / data.length * 0.3;

var draw = SVG().addTo('#svgjs-bar').size(W, H);
draw.viewbox(0, 0, W, H);

// 坐标轴
draw.line(PAD, H - PAD, W - PAD, H - PAD).stroke({ color: gv('--border'), width: 1 });
draw.line(PAD, PAD, PAD, H - PAD).stroke({ color: gv('--border'), width: 1 });

// 柱子
data.forEach(function(d, i) {
  var x = PAD + i * (bw + gap) + gap / 2;
  var h = (d.value / maxVal) * chartH;
  var y = H - PAD - h;
  var rect = draw.rect(bw, 0).move(x, H - PAD)
    .fill(palette[i % palette.length])
    .radius(4)
    .attr('opacity', 0.9);
  rect.animate(900, 0, 'now').during(function(t) {
    this.size(bw, t * h).move(x, H - PAD - t * h);
  });
  // 标签
  draw.text(d.label).move(x + bw / 2 - 12, H - PAD + 8)
    .font({ size: 12, family: 'sans-serif' }).fill(gv('--muted'));
  draw.text(String(d.value)).move(x + bw / 2 - 8, y - 16)
    .font({ size: 11, weight: 700 }).fill(gv('--text'));
});
```

#### 31b — 多系列折线图

```html
<div id="svgjs-line" style="width:100%;height:300px;margin:1rem 0;"></div>
```

```css
#svgjs-line { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var series = [
  { name: '实际', color: gv('--chart-1'), data: [3, 5, 8, 4, 9, 6] },
  { name: '预测', color: gv('--chart-2'), data: [null, null, null, 4, 7, 8] }
];
var W = 600, H = 280, PAD = 40;
var maxV = 10, minV = 0, stepX = (W - PAD * 2) / (series[0].data.length - 1);
var draw = SVG().addTo('#svgjs-line').size(W, H);
draw.viewbox(0, 0, W, H);

// 网格
for (var i = 0; i <= 5; i++) {
  var y = PAD + (chartH => chartH * i / 5)(H - PAD * 2);
  draw.line(PAD, y, W - PAD, y).stroke({ color: gv('--border'), width: 0.5, dasharray: '2,4' });
}

// 折线
series.forEach(function(s, si) {
  var path = '';
  s.data.forEach(function(v, i) {
    if (v == null) return;
    var x = PAD + i * stepX;
    var y = H - PAD - (v - minV) / (maxV - minV) * (H - PAD * 2);
    path += (path ? 'L' : 'M') + x + ',' + y + ' ';
  });
  if (path) {
    var line = draw.path(path).fill('none')
      .stroke({ color: s.color, width: 2.5, linecap: 'round', linejoin: 'round' });
    if (si === 1) line.attr('stroke-dasharray', '6,4');
    line.animate(1200).attr('stroke-dashoffset', 0).ease('<>');
    s.data.forEach(function(v, i) {
      if (v == null) return;
      var x = PAD + i * stepX;
      var y = H - PAD - (v - minV) / (maxV - minV) * (H - PAD * 2);
      draw.circle(5).center(x, y).fill(s.color)
        .attr('stroke', gv('--bg')).attr('stroke-width', 2);
    });
  }
});
```

#### 31c — 流程图（节点 + 连线）

节点从透明渐入，连线从起点动画延伸到终点。

```html
<div id="svgjs-flow" style="width:100%;height:240px;margin:1rem 0;"></div>
```

```css
#svgjs-flow { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var nodes = [
  { x: 80,  y: 110, label: '输入',   color: gv('--chart-3') },
  { x: 280, y: 110, label: '处理',   color: gv('--chart-1') },
  { x: 480, y: 110, label: '校验',   color: gv('--chart-2') },
  { x: 680, y: 110, label: '输出',   color: gv('--chart-4') }
];
var W = 760, H = 220;
var draw = SVG().addTo('#svgjs-flow').size(W, H);
draw.viewbox(0, 0, W, H);

// 连线（先画底层）
for (var i = 0; i < nodes.length - 1; i++) {
  var a = nodes[i], b = nodes[i + 1];
  var line = draw.line(a.x + 60, a.y, b.x - 60, b.y)
    .stroke({ color: gv('--border'), width: 2 });
  line.attr('stroke-dasharray', '0,200');
  line.animate(800, 200, 'now').ease('>').attr('stroke-dasharray', '200,0');
}

// 节点（后画覆盖连线端点）
nodes.forEach(function(n, i) {
  var g = draw.group();
  var rect = g.rect(120, 60).move(n.x - 60, n.y - 30)
    .fill(n.color).radius(8).attr('opacity', 0);
  rect.animate(500, i * 200, 'now').attr('opacity', 1);
  var txt = g.text(n.label).center(n.x, n.y)
    .font({ size: 14, weight: 700, family: 'sans-serif' })
    .fill(gv('--accent-text')).attr('opacity', 0);
  txt.animate(500, i * 200 + 100, 'now').attr('opacity', 1);
});
```

#### 31d — 进度环（环形）

围绕中心点绘制弧形，自动从 0 动画到目标百分比。

```html
<div id="svgjs-ring" style="width:200px;height:200px;margin:1rem auto;"></div>
```

```css
#svgjs-ring { background: var(--surface); border-radius: var(--radius); }
```

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var pct = 73;  // 目标百分比
var size = 180, strokeW = 14, r = (size - strokeW) / 2;
var cx = size / 2, cy = size / 2;
var circumference = 2 * Math.PI * r;

// 转换 pct → SVG arc path
function arcPath(p) {
  var angle = (p / 100) * 2 * Math.PI - Math.PI / 2;
  var x = cx + r * Math.cos(angle);
  var y = cy + r * Math.sin(angle);
  var large = p > 50 ? 1 : 0;
  return ['M', cx, cy - r, 'A', r, r, 0, large, 1, x, y].join(' ');
}

var draw = SVG().addTo('#svgjs-ring').size(size, size);
draw.viewbox(0, 0, size, size);
// 背景环
draw.circle(r * 2).center(cx, cy)
  .fill('none').stroke({ color: gv('--border'), width: strokeW });
// 进度环
var arc = draw.path(arcPath(0)).fill('none')
  .stroke({ color: gv('--accent'), width: strokeW, linecap: 'round' });
arc.animate(1400, 0, 'now').ease('>').plot(arcPath(pct));
// 中心数字
draw.text(String(pct) + '%').center(cx, cy)
  .font({ size: 32, weight: 800, family: 'sans-serif' }).fill(gv('--text'));
```

#### 使用规则

- **每个图表需要唯一 `id`**（如 `svgjs-bar-1`），多个图表时不可重复
- SVG.js 默认导出 `SVG()` 全局函数；与浏览器原生 `SVGElement` 接口不冲突
- 颜色全部用 `gv('--xxx')` 调用主题变量，函数自动解析 CSS 变量为实际色值
- 字号建议 11-14（标签）/ 14-32（数字），匹配报告正文字号梯度
- viewBox 设置为逻辑尺寸（如 `viewBox(0, 0, 600, 280)`），外层容器 CSS 控制实际渲染尺寸

#### 降级说明

- **JS 禁用时**：容器为空，显示 `<div class="no-js-fallback"><p>图表加载需要 JavaScript</p></div>`
- **SVG.js 未加载**：`SVG()` 函数为 `undefined`，用 `typeof SVG !== 'undefined'` 保护
- **容器未渲染**：SVG.js 在 `DOMContentLoaded` 之后初始化
- **resize**：SVG 是矢量自适应的，不需要 resize handler

#### 与其他组件的关系

| 组件 | 适用场景 | 区别 |
|------|---------|------|
| #1 SVG 流程图 | 静态流程图 | 纯手写 SVG，无动画 |
| #26 ECharts | 数据图表 | Canvas 渲染，更强大但不可缩放 |
| #27 Three.js | 3D 场景 | WebGL，复杂度高 |
| **#31 SVG.js** | **自定义动画 SVG** | **DOM 渲染，轻量（78KB），可缩放** |