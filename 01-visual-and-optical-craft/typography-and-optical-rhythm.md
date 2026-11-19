# Typography, Fluid Scales & Zero-CLS Webfont Engineering

## 1. Typographic Hierarchy & Measure (Bringhurst Standard)
- **Fluid Display Scale:** Use `clamp(min, preferred, max)` with `rem + vw` (never `vw` alone, which breaks browser zoom accessibility per WCAG 1.4.4 Resize Text):
  ```css
  .hero-h1 {
    font-size: clamp(2.125rem, 1.35rem + 2.6vw, 3.35rem);
    line-height: 1.07;
    letter-spacing: -0.028em;
    font-optical-sizing: auto;
    text-wrap: balance;
  }
  ```
- **Optimal Measure:** Constrain narrative prose to **`45ch–65ch`** (`max-width: 56ch`, `line-height: 1.5–1.6`, `text-wrap: pretty`).
- **x-Height Legibility Compensation:** APCA font lookup tables calibrate against Helvetica/Inter (`x-height ≈ 0.52`). Low x-height editorial serifs (Cormorant Garamond `~0.42`, Newsreader `~0.46`) require `+12%–18%` larger `font-size` for equivalent scanning speed.
- **OpenType Numeric Discipline:** Lock fixed-width figures and slashed zeroes on all live counters, prices, MACs, hashes, and Hz readouts:
  ```css
  .mono-metric {
    font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums lining-nums;
    font-feature-settings: "tnum" 1, "zero" 1;
  }
  ```

## 2. Zero-CLS Webfont Fallback Metric Overrides
Swapping a system fallback (`Arial`/`Georgia`) to a loaded webfont (`Inter`/`Newsreader`) is a top cause of **CLS > 0.10**. Match the fallback font's exact glyph box via CSS `@font-face` metric overrides so layout never shifts by even 1 pixel on font load:
```css
@font-face {
  font-family: "Inter Fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}
body { font-family: "Inter", "Inter Fallback", system-ui, sans-serif; }
```
Pair with `font-display: swap;` and `<link rel="preload" as="font" type="font/woff2" crossorigin>` strictly for the 1–2 above-the-fold weights (never preload 8 weights).
