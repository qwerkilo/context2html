---
id: 29
name: ECharts GL 3D可视化
dependencies:
- echarts.min.js
- echarts-gl.min.js
compat_types:
- report
- article
- doc
degrade_to: '26'
requires_3d: true
---

### 29. ECharts GL 3D 可视化

> **🎯 效果**：WebGL 3D 图表——3D 柱状图、3D 散点图、3D 地球/地图、3D 曲面图。Canvas/JS 渲染，无需 CSS。需 `libs/echarts-gl.min.js`。

> 本组件无 CSS 代码块 —— ECharts GL 全部通过 Canvas/JS 渲染，无需独立 CSS。

基于 ECharts GL 扩展库，在标准 ECharts 基础上增加 WebGL 3D 渲染能力。支持 3D 柱状图、3D 散点图、3D 地球/地图和 3D 曲面图。

#### 前置依赖

```html
<!-- ECharts 基础库（必须） -->
<script src="libs/echarts.min.js"></script>
<!-- ECharts GL 扩展（必须） -->
<script src="libs/echarts-gl.min.js"></script>
```

#### 使用规则

- 所有 3D 系列类型都加 `gl` 后缀：`type: 'bar3D'`、`type: 'scatter3D'`、`type: 'map3D'`、`type: 'surface'`
- 3D 图表需要 `grid3D` 组件（而非普通 `grid`）定义三维坐标系
- GL 扩展自动检测 WebGL 支持，不支持时显示降级提示
- 每个容器必须有明确的 `width` 和 `height`（百分比或 px 均可）

#### 子类型

| 子类型 | 系列 type | 适用场景 |
|--------|-----------|---------|
| 3D 柱状图 | `bar3D` | 三维数据对比，高度 + 颜色双维度编码 |
| 3D 散点图 | `scatter3D` | 三维空间分布，适合聚类/异常检测 |
| 3D 地球 | `map3D` | 地理数据全球分布，可飞线动画 |
| 3D 曲面 | `surface` | 函数曲面/地形/连续场数据 |

#### 示例：3D 柱状图

```js
var chart = echarts.init(document.getElementById('my-chart'));
chart.setOption({
  grid3D: {
    viewControl: { autoRotate: true, distance: 120 },
    boxWidth: 80, boxHeight: 80, boxDepth: 80,
  },
  xAxis3D: { type: 'category', data: ['A','B','C','D','E'] },
  yAxis3D: { type: 'category', data: ['X','Y','Z'] },
  zAxis3D: { type: 'value' },
  series: [{
    type: 'bar3D',
    data: [[0,0,10],[1,0,25],[2,0,15],[3,0,30],[4,0,20],
           [0,1,18],[1,1,12],[2,1,28],[3,1,8],[4,1,22]],
    shading: 'lambert',
    itemStyle: { opacity: 0.8 },
    label: { show: true }
  }]
});
```

#### 示例：3D 地球

```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
chart.setOption({
  globe: {
    baseTexture: 'world.topo.bathy.200401.jpg', // 或使用动态纹理
    viewControl: { autoRotate: true, distance: 150 },
    shading: 'realistic',
  },
  series: [{
    type: 'scatter3D',
    coordinateSystem: 'globe',
    data: [[116.4,39.9,100],[121.5,25.0,80],[139.7,35.7,120]],
    symbolSize: 8,
    itemStyle: { color: gv('--accent'), opacity: 0.9 },
    label: { show: true, formatter: '{b}' }
  }]
});
```

#### 示例：3D 广东省地图

```html
<!-- GeoJSON 必须通过 <script> 标签加载（file:// 协议下 fetch 不可用） -->
<!-- libs/guangdong.js 格式：`window.__gdGeoJSON = {...GeoJSON...}` — 全局变量赋值 -->
<script src="libs/guangdong.js"></script>
<div id="gd-map" style="width:100%;height:600px;"></div>
```
```js
function gv(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
var geoJson = window.__gdGeoJSON; // 通过 <script> 注入的全局变量
echarts.registerMap('guangdong', geoJson);
var chart = echarts.init(document.getElementById('gd-map'));
chart.setOption({
  visualMap: {
    show: true, min: 0.1, max: 3.5,
    inRange: { color: [gv('--chart-3'),gv('--chart-4'),gv('--warning'),gv('--accent')] },
    seriesIndex: 0
  },
  series: [{
    type: 'map3D', map: 'guangdong',
    data: [{name:'深圳市',value:3.46},...],
    regionHeight: 1.5, // 地图挤压高度
    shading: 'lambert'
  }, {
    type: 'scatter3D',
    coordinateSystem: 'geo3D', // 叠加在 map3D 上层
    data: [{name:'深圳',value:[114.07,22.55,34600]},...],
    symbolSize: function(v){ return 6 + Math.sqrt(v[2]/10000)*4; },
    label: { show: true }
  }]
});
```
完整示例见 `examples/echarts-gl-map-demo.html`。

#### 实践要点

- **GeoJSON 加载**：必须通过 `<script>` 标签加载（转为 `.js` 文件 + 全局变量），`fetch()` 在 `file://` 协议下因 CORS 限制不可用
- **加载顺序**：`echarts.min.js` → `echarts-gl.min.js` → GeoJSON（如需）
- **map3D 属性**：只需 `regionHeight`（挤压高度），无需 `boxWidth`/`boxHeight`（仅 `grid3D`/`bar3D` 需要）
- **visualMap + map3D**：需显式指定 `seriesIndex: 0`，否则颜色映射可能不生效
- **scatter3D 叠加**：设置 `coordinateSystem: 'geo3D'` 可叠加在 `map3D` 之上做城市标注
- **region 名称匹配**：GeoJSON 中的 `name` 属性必须与 `data` 中的城市名完全一致（如"深圳市"而非"深圳"）

#### 降级说明

- **WebGL 不支持**：ECharts GL 自动降级为提示信息，不影响 ECharts 2D 部分
- **未加载 GL**：访问 `echarts` 对象时 GL 系列不存在，显示 `[ECharts] Unknown series bar3D` 警告但不崩溃
- **纹理缺失**：地球底图使用网络纹理，离线时可用纯色 `itemStyle.color` 替代
