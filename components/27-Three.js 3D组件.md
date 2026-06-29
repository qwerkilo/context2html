### 27. Three.js 3D 组件

使用 Three.js 在课程中渲染 3D 场景，适合展示地理/贸易网络、三维数据可视化、结构/架构图。

#### 渲染后端策略

- **优先 WebGPU**：使用 `WebGPURenderer`（需浏览器支持 `navigator.gpu`）
- **回退 WebGL**：浏览器不支持 WebGPU 时自动降级为 `WebGLRenderer`
- **Three.js 版本**：固定在 r185（`three@0.185.0`）

#### 着色器策略

- **优先 TSL（Three Shading Language）**：使用 `three/tsl` 模块的函数式节点定义着色器效果（辉光、粒子、后处理、自定义材质等）
- **降级 WGSL**：TSL 无法实现的场景（外部 WGSL shader 集成），使用 `three/addons/renderers/webgpu/utils/WebGPUConstants.js` 编写裸 WGSL
- 一般 3D 柱状图等简单场景无需 TSL——TSL 仅在需要自定义着色器效果时使用

#### 前置依赖

```html
<!-- 方式一（推荐）：ES Module + ImportMap → WebGPU 优先 -->
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.185.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.185.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { WebGPURenderer } from 'three/addons/renderers/webgpu/WebGPURenderer.js';
// TSL 按需导入
import { Fn, uniform, time, color, uv } from 'three/tsl';
</script>

<!-- 方式二：WebGL 降级（传统 UMD） -->
<script src="libs/three.min.js"></script>
```

#### 使用规则

- Three.js 默认接管鼠标事件，与课程 `← →` 键盘导航冲突时需在场景容器上加 `tabindex` 隔离
- 每个场景唯一 `id`，`height` 建议 300-450px
- Three.js 渲染异步，用 `window.requestAnimationFrame` 循环
- 销毁：课程切换时需 `renderer.dispose()` 释放 GPU 资源
- 检测 WebGPU：`typeof navigator !== 'undefined' && navigator.gpu`
- importmap 方式下代码需放在 `<script type="module">` 中

#### 示例：3D 柱状图（数据可视化，WebGPU 优先）

```html
<div id="three-bar" style="width:100%;height:400px;margin:1rem 0;">
  <p>3D 场景加载中...</p>
</div>
```

```css
#three-bar { background: var(--surface); border-radius: var(--radius); }
```

```js
// 需要 importmap + type="module" 环境
var container = document.getElementById('three-bar');
if(container && navigator.gpu){
  import('three').then(function(THREE){
    import('three/addons/renderers/webgpu/WebGPURenderer.js').then(function(m){
      var WGR = m.WebGPURenderer;
      var scene = new THREE.Scene();
      scene.background = new THREE.Color(0xf5f0eb);
      var camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
      camera.position.set(5, 4, 8); camera.lookAt(0, 0, 0);
      var renderer = new WGR({ antialias: true });
      renderer.setSize(container.clientWidth, container.clientHeight);
      container.appendChild(renderer.domElement);

      var data = [3.2, 5.1, 2.8, 4.5, 3.9];
      var colors = [0xc0392b, 0xe67e22, 0x2ecc71, 0x3498db, 0x9b59b6];
      for(var i = 0; i < data.length; i++){
        var bar = new THREE.Mesh(
          new THREE.BoxGeometry(0.6, data[i], 0.6),
          new THREE.MeshLambertMaterial({ color: colors[i] })
        );
        bar.position.set((i - 2) * 1.2, data[i] / 2, 0);
        scene.add(bar);
      }

      var floor = new THREE.Mesh(
        new THREE.PlaneGeometry(8, 3),
        new THREE.MeshLambertMaterial({ color: 0xddd8d0, side: THREE.DoubleSide })
      );
      floor.rotation.x = -Math.PI / 2; floor.position.y = -0.05;
      scene.add(floor);

      var light = new THREE.DirectionalLight(0xffffff, 1);
      light.position.set(5, 10, 7);
      scene.add(light);
      scene.add(new THREE.AmbientLight(0xffffff, 0.4));

      function animate(){ requestAnimationFrame(animate); renderer.render(scene, camera); }
      animate();

      window.addEventListener('resize', function(){
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      });
    });
  });
}
```

#### TSL 使用示例（自定义发光效果）

```js
import { Fn, uniform, time, sin, positionLocal, color, vec3 } from 'three/tsl';

// TSL 节点：随时间变化的脉冲颜色
var pulseColor = Fn(function(){
  var t = time.mul(0.5);
  var r = sin(t).add(1).mul(0.5);
  var g = sin(t.add(2.094)).add(1).mul(0.5);
  var b = sin(t.add(4.189)).add(1).mul(0.5);
  return color(r, g, b);
});

// 应用于材质
var mat = new THREE.MeshLambertMaterial();
mat.colorNode = pulseColor;  // TSL 节点替代固定 color 属性
```

#### TSL → WGSL 降级条件

| 场景 | 使用 TSL？ | 使用 WGSL？ |
|------|-----------|------------|
| 自定义材质着色器（颜色/纹理组合） | ✅ | ❌ |
| 动态脉冲/渐变特效 | ✅ | ❌ |
| 粒子系统自定义 | ✅ | ❌ |
| 后处理（bloom/glow） | ✅ | ❌ |
| 外部第三方 shader 代码 | ❌ | ✅ |
| Compute shader 通用计算 | ❌ | ✅（需 `WebGPUComputeRenderer`） |

#### 动画

Three.js 动画使用标准的 `requestAnimationFrame` 循环，无需额外动画库。简单循环动画（平移/旋转/缩放）可直接在 rAF 中更新 `mesh.position`、`mesh.rotation` 等属性。

#### 降级说明

- **WebGPU 不支持**：自动降级为 WebGL（`THREE.WebGLRenderer`），功能保持一致，仅性能差异
- **Three.js 未加载**：用 `typeof THREE === 'undefined'` 保护（UMD 模式）或 `.catch()` 处理（ESM 模式）
- **键盘导航冲突**：在 Three.js 容器上设置 `onkeydown="e.stopPropagation()"`
- **性能**：移动端降低 `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`
- **WebGPU 不可用但 importmap 失败**：备选方案包括 `document.write('<script src="libs/three.min.js">')` 加载 UMD 版本
