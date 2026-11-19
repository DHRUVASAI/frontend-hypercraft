# Interaction Choreography, Frame-Rate-Independent Motion & W3C Web Audio 1.1

## 1. Frame-Rate-Independent Exponential Damping
Bare `current += (target - current) * 0.08` runs **2× faster on 120 Hz ProMotion screens** than on 60 Hz laptops. Use continuous-time exponential decay with clamped `dt` (prevents explosion after tab switch):
```js
export function damp(current, target, lambda, dt) {
  return current + (target - current) * (1 - Math.exp(-lambda * Math.min(dt, 0.05)));
}
```
*Verified invariance ($\lambda=8, t=0.5\,\text{s}$):* 60 Hz (`0.981684`) === 120 Hz (`0.981684`) === analytical $1 - e^{-4}$.

## 2. Exact 3-Step Magnifying Loupe Transform Matrix (High-DPI 2D Canvas)
To magnify around pointer `(px, py)` without drift (`zoom = 3.0` over `4×` macro base weave = `12×` effective optical scale):
```js
ctx.save();
ctx.beginPath();
ctx.arc(px, py, radius, 0, Math.PI * 2);
ctx.clip();
ctx.translate(px, py);
ctx.scale(zoom, zoom);
ctx.translate(-px, -py);
drawSpecimen(ctx);
ctx.restore();
drawMillimeterReticle(ctx, px, py, radius);
```

## 3. Scroll Choreography & 3D-to-2D Projected Callouts
- **Never hijack native scroll (`wheel` `preventDefault`)**: Compute normalized container ratio `clamp((scrollY - start) / travel, 0, 1)`, smooth via `damp()`, and let manual scrubbers override cleanly until scroll resumes.
- **3D → 2D HUD Projection:** Clone world anchor `v.project(camera)`. **Cull behind-camera anchors** (`if (v.z > 1) hide()`), then map `x = (v.x * 0.5 + 0.5) * width`, `y = (-v.y * 0.5 + 0.5) * height`.

## 4. Spec-Compliant W3C Web Audio 1.1 Synthesis
1. **`exponentialRampToValueAtTime(0, t)` throws a `RangeError`:** Always anchor with `setValueAtTime(0.0001, now)` first, ramp up to `maxGain`, and ramp down to `0.0001` (or use `setTargetAtTime(0, t, tau)`).
2. **Gesture Resume:** Call `if (ctx.state === "suspended") await ctx.resume();` inside the user click handler.
3. **Hard Acoustic Safety Cap:** Clamp master gain `≤ 0.12` (test benches) and `≤ 0.08` (UI chimes); couple `AnalyserNode` (`fftSize = 256`) RMS energy to visual canvas curves or 3D cone excursion.
