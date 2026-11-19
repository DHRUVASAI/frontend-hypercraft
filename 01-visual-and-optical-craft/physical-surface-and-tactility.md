# Physical Surface Tactility, Concentric Geometry & Grounding Realism

## 1. 4-Layer Tactile Hardware Bevels
```css
.btn-hardware {
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.55) inset,     /* 1. Top specular rim highlight */
    0 -1.5px 0 rgba(0, 0, 0, 0.08) inset,        /* 2. Bottom physical bevel lip */
    0 1px 2px rgba(0, 0, 0, 0.06),               /* 3. Tight contact occlusion */
    0 4px 10px -4px rgba(0, 0, 0, 0.10);         /* 4. Soft ambient bounce */
  transition: transform 0.11s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.14s ease;
}
.btn-hardware:active {
  transform: translateY(1px) scale(0.985);
  box-shadow: 0 1.5px 2px rgba(0, 0, 0, 0.14) inset, 0 1px 2px rgba(0, 0, 0, 0.05);
}
```

## 2. Concentric Corner Continuity
Enforce $R_{\text{outer}} = R_{\text{inner}} + P_{\text{gap}}$ on all nested containers (tracks, pill docks, framed plinths). Example: `padding: 4px` + inner active tab `8px` → outer track `12px`.

## 3. Compositor-Safe Anti-Banding Micro-Grain (Static Tiled Data-URI)
Never apply a live full-viewport SVG `filter: url(#noise)` (forces continuous GPU shader repainting on scroll). Instead, tile a tiny `200×200` pre-encoded SVG `feTurbulence` data-URI as a static `background-image` on a `pointer-events: none; position: fixed;` pseudo-element at `2.0%–2.5%` opacity. The browser rasterizes the 200 px tile **once** and composites it cheaply while breaking 8-bit gradient banding.

## 4. Dual-Layer Grounding for Transparent Product Cutouts (`-nobg.png`)
1. **Tight Contact Occlusion:** Compact radial ellipse directly beneath the base/hem (`blur: 6px`, `opacity: 0.24`) anchoring physical weight.
2. **Soft Directional Cast Shadow:** Wider offset diffuse shadow (`translateY(14px)`, `blur: 24px`, `opacity: 0.11`) aligned with a top-down plinth spotlight gradient, plus restrained pointer tilt (`max ±6°`).
