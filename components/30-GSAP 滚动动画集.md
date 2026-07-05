---
id: 30
name: GSAP 滚动动画集
dependencies:
- gsap.min.js
- ScrollTrigger.min.js
compat_types:
- report
- article
- tutorial
requires_3d: false
---

### 30. GSAP 滚动动画集

> **🎯 效果**：基于 GSAP + ScrollTrigger 的 5 种滚动触发动画（fade / stagger / parallax / flip / zoom）。桌面端 `libs/` 离线加载，移动端 CDN 降级。每个模式独立触发，ease-out 缓动。

桌面端优先加载 `libs/` 离线包（无网络依赖），移动端自动切换 CDN 以减少离线包大小。

#### 加载策略

| 条件 | 加载源 |
|------|--------|
| 桌面端（默认） | `libs/gsap.min.js` + `libs/ScrollTrigger.min.js` |
| 移动端（触屏 + < 1024px） | CDN `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/` |

前置下载离线包：
```bash
mkdir -p libs && curl -Lo libs/gsap.min.js https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
curl -Lo libs/ScrollTrigger.min.js https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js
```

#### 动画模式

| `data-gsap` | 效果 | 适用场景 |
|-------------|------|---------|
| `fade` | 每个 item 独立渐入 + 上移 | 普通段落/卡片 |
| `stagger` | items 依次序错开渐入 | 列表/网格项 |
| `parallax` | items 以不同速度滚动 | 图片墙/多层级内容 |
| `flip` | 3D Y 轴翻转 | 卡片正面→反面展示 |
| `zoom` | 从 0.3 倍缩放入 | 重大数据/图表 |

#### HTML

```html
<div class="gsap-wrap" data-gsap="stagger">
  <div class="gsap-item" data-lang="zh">
    <h4>第一项</h4>
    <p>描述文字...</p>
  </div>
  <div class="gsap-item" data-lang="en">
    <h4>Item 1</h4>
    <p>Description...</p>
  </div>
  <div class="gsap-item" data-lang="zh">
    <h4>第二项</h4>
    <p>描述文字...</p>
  </div>
  <div class="gsap-item" data-lang="en">
    <h4>Item 2</h4>
    <p>Description...</p>
  </div>
  <!-- 更多 items -->
</div>
```

**注意：** `.gsap-item` 的直接子元素会被 GSAP 动画化。每个 item 可包含任意 HTML 内容。

#### CSS

```css
/* GSAP 滚动动画集 (#30) */
.gsap-wrap { margin: 2.5rem 0; }
.gsap-item { will-change: transform, opacity; backface-visibility: hidden; }

/* Fade / Stagger / Zoom — 初始隐藏 */
[data-gsap="fade"] .gsap-item,
[data-gsap="stagger"] .gsap-item,
[data-gsap="zoom"] .gsap-item {
  opacity: 0;
}

/* Flip — 3D 透视 */
[data-gsap="flip"] .gsap-item {
  perspective: 800px;
  opacity: 0;
}

/* Parallax — 无初始隐藏，GSAP 控制偏移 */
[data-gsap="parallax"] .gsap-item {
  will-change: transform;
}

/* 响应式间距 */
@media (max-width: 700px) {
  .gsap-wrap { margin: 1.5rem 0; }
}

/* 减少动效 */
@media (prefers-reduced-motion: reduce) {
  [data-gsap] .gsap-item {
    opacity: 1 !important;
    transform: none !important;
  }
}
```

#### JS

```js
<script>
(function(){
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('.gsap-item').forEach(function(el) {
      el.style.opacity = '1'; el.style.transform = 'none';
    });
    return;
  }

  var isMobile = ('ontouchstart' in window || navigator.maxTouchPoints > 0)
    && window.innerWidth < 1024;

  var baseURL = isMobile
    ? 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/'
    : 'libs/';

  var loaded = 0;
  var total = 2;

  function onLibLoad() {
    loaded++;
    if (loaded === total) initGSAP();
  }

  ['gsap.min.js', 'ScrollTrigger.min.js'].forEach(function(file) {
    var s = document.createElement('script');
    s.src = baseURL + file;
    s.onload = onLibLoad;
    s.onerror = function() {
      // CDN fallback if local fails
      if (!isMobile) {
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/' + file;
        s.onerror = null;
      }
    };
    document.head.appendChild(s);
  });

  function initGSAP() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    gsap.registerPlugin(ScrollTrigger);

    document.querySelectorAll('[data-gsap]').forEach(function(section) {
      var mode = section.dataset.gsap;
      var items = section.querySelectorAll('.gsap-item');
      if (!items.length) return;

      var defaults = { ease: 'power2.out', scrollTrigger: { trigger: section, start: 'top 82%' } };

      switch (mode) {
        case 'fade':
          items.forEach(function(el, i) {
            gsap.fromTo(el, { opacity: 0, y: 30 }, {
              opacity: 1, y: 0, duration: 0.7, delay: i * 0.1,
              scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none reverse' }
            });
          });
          break;

        case 'stagger':
          gsap.fromTo(items, { opacity: 0, y: 40 }, {
            opacity: 1, y: 0, duration: 0.6, stagger: 0.12,
            scrollTrigger: { trigger: section, start: 'top 80%' }
          });
          break;

        case 'parallax':
          items.forEach(function(el, i) {
            var speed = 0.08 + i * 0.06;
            gsap.to(el, {
              y: window.innerHeight * speed * 0.4, ease: 'none',
              scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
            });
          });
          break;

        case 'flip':
          items.forEach(function(el) {
            gsap.fromTo(el, { rotationY: -180, opacity: 0 }, {
              rotationY: 0, opacity: 1, duration: 0.9,
              scrollTrigger: { trigger: el, start: 'top 80%' }
            });
          });
          break;

        case 'zoom':
          items.forEach(function(el, i) {
            gsap.fromTo(el, { scale: 0.3, opacity: 0 }, {
              scale: 1, opacity: 1, duration: 0.8, delay: i * 0.1,
              scrollTrigger: { trigger: el, start: 'top 85%' }
            });
          });
          break;
      }
    });

    ScrollTrigger.refresh();
  }
})();
</script>
```
