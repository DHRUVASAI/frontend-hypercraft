# Core Web Vitals, INP Task Yielding & Fault-Isolated Resilience

## 1. Official Core Web Vitals 75th-Percentile Budgets (`web.dev`)
| Vital | Good | Poor | Engineering Mechanisms |
|---|---|---|---|
| **LCP** | **≤ 2.5 s** | > 4.0 s | Zero fake preloaders; `<img fetchpriority="high">` on hero fallback plate; preload 1–2 above-the-fold WOFF2 fonts; isolate WebGL async load. |
| **INP** | **≤ 200 ms** | > 500 ms | Decompose into **Input Delay + Processing Duration + Presentation Delay**; break any >50 ms long task with `scheduler.yield()`. |
| **CLS** | **≤ 0.10** | > 0.25 | Explicit `aspect-ratio`/`width`/`height` on media & canvases; CSS `@font-face` metric overrides (`size-adjust`, `ascent-override`); `tabular-nums`. |

## 2. Breaking Long Tasks for Sub-100ms INP (`scheduler.yield()`)
When clicking a filter, running a client-side dataset pass, or updating 100+ DOM nodes, paint the immediate active state first, then yield back to the browser compositor before heavy work:
```js
export const yieldToMain = () =>
  "scheduler" in globalThis && "yield" in globalThis.scheduler
    ? globalThis.scheduler.yield()
    : new Promise((resolve) => setTimeout(resolve, 0));

async function handleHeavyAction(items) {
  setButtonActiveUI();           // Immediate visual feedback (< 16 ms)
  await yieldToMain();           // Let browser paint before processing
  for (let i = 0; i < items.length; i += 25) {
    processChunk(items.slice(i, i + 25));
    await yieldToMain();
  }
}
```

## 3. Modern Rendering & Thread Offloading Primitives
- **`content-visibility: auto` + `contain-intrinsic-size: auto 600px`:** Skips off-screen layout/paint for long editorial chapters below the fold (cuts initial style/layout time dramatically with zero CLS when intrinsic height is provided).
- **OffscreenCanvas + Web Worker:** Move heavy 60 FPS 2D audio FFT analyzers or particle/cloth physics off the main thread via `canvas.transferControlToOffscreen()` so UI clicks stay locked at `< 30 ms` INP.
- **Strict Frame-1 Sync/Async Isolation:** Bind all UI controls synchronously on `DOMContentLoaded`; isolate Three.js inside an async `try/catch` with `webglcontextlost` recovery and instant 2D Canvas fallback.
- **DPR & Visibility Gating:** Clamp `Math.min(devicePixelRatio, 2)` (cuts 3× mobile fragment load by **55.6%**), pause `requestAnimationFrame` via `IntersectionObserver` + `visibilitychange`, and honor `prefers-reduced-motion: reduce`.
