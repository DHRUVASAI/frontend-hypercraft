# Color Science: OKLCH, W3C WCAG 2.x, Draft APCA `0.0.98G-4g` & CVD Safety

> **Mandatory Accessibility & Standards Qualification:**
> 1. **WCAG Is a W3C Technical Recommendation, Not a Statute:** W3C WCAG itself is not a law. Specific laws and regulations **incorporate or reference particular WCAG versions** by jurisdiction:
>    - **US DOJ ADA Title II (2024 Final Rule):** References **WCAG 2.1 Level AA**.
>    - **US Revised Section 508:** References **WCAG 2.0 Level AA**.
>    - **European Union (EN 301 549 v3.2.1 / European Accessibility Act):** References **WCAG 2.1 Level AA**.
>    - **India GIGW 3.0 / IS 17802:** References **WCAG 2.1 Level AA**.
>    - **WCAG 2.2 Level AA** is the latest W3C Recommendation (recommended engineering target for new builds), though not yet uniformly incorporated into every jurisdiction's regulations.
>    - Under WCAG 2.0/2.1/2.2 AA, minimum contrast is `>= 4.5:1` for normal text, `>= 3.0:1` for large text (SC 1.4.3), and `>= 3.0:1` for non-text UI components/graphical objects (SC 1.4.11 in 2.1+).
> 2. **Candidate / Draft Status (`APCA-W3 0.0.98G-4g`):** APCA is a research/candidate perceptual contrast algorithm under evaluation for the **WCAG 3.0 Working Draft** and remains subject to revision. Passing APCA alone does **not** satisfy regulations that reference WCAG 2.0 or 2.1 Level AA. Use APCA **alongside** WCAG 2.1 AA—especially to catch dark-mode legibility failures that polarity-blind WCAG 2.x misses.
> 3. **No Flat Cutoff:** APCA $L^c$ is strictly **font-size, font-weight, and polarity dependent** (lookup matrix, not a single pass/fail number):
>    - **`|Lc| >= 90`:** Preferred for fluent body text (`14–16 px`, weight `400`).
>    - **`|Lc| >= 75`:** Minimum for body-text columns at standard weights (`18 px / 400` or `16 px / 500`).
>    - **`|Lc| >= 60`:** Content/UI labels only at heavier or larger sizes (`24 px / 400` or `16 px / 700`).
>    - **`|Lc| >= 45`:** Large display headlines (`>= 36 px / 400`) or large non-text UI elements only.
> 4. **WCAG 1.4.1 (Use of Color):** Never encode state by hue or contrast alone—always pair color with icons, labels, or structural cues.

## 1. Why HSL Fails and OKLCH Succeeds (W3C CSS Color Level 4)
In cylindrical HSL, perceived luminance varies by up to **13x** across hues at constant `L = 50%` (`hsl(60, 100%, 50%)` yellow has $Y = 0.928$, while `hsl(240, 100%, 50%)` blue has $Y = 0.072$). **OKLCH** (Bjorn Ottosson, 2020) separates **Perceptual Lightness $L \in [0, 1]$**, **Perceptual Chroma $C \in [0, \sim 0.37]$**, and **Hue Angle $H \in [0^\circ, 360^\circ)$**.

### Dual-Verified Palette (Passing WCAG 2.1 AA/AAA + APCA `0.0.98G-4g` Targets)
*Dark semantic accents (`|Lc| 60.7–65.8`) are designated for bold `>= 14–16 px` UI badges/headings and non-text borders; body prose uses Primary Ink (`|Lc| 93.4`) or Muted Body (`|Lc| 75.1`).*

| Role | Daylight Token (on `#F3F0EA`) | WCAG 2.1 | APCA $L^c$ | OKLCH `(L, C, H)` | Night Ops Token (on `#12151B`) | WCAG 2.1 | APCA $L^c$ | OKLCH `(L, C, H)` |
|---|---|---|---|---|---|---|---|---|
| **Primary Ink** | `#16181D` | **15.61:1** | **+95.8** | `(0.209, 0.010, 268.2°)` | `#ECEAE4` | **15.19:1** | **-93.4** | `(0.937, 0.008, 91.5°)` |
| **Muted Body** | `#4E5563` | **6.59:1** | **+77.3** | `(0.449, 0.025, 264.3°)` | `#C6CDD9` | **11.43:1** | **-75.1** | `(0.847, 0.018, 261.3°)` |
| **Cobalt Accent (UI/Bold)** | `#1E4FD6` | **5.87:1** | **+73.3** | `(0.488, 0.213, 264.3°)` | `#8CB4FC` | **8.75:1** | **-60.7** | `(0.769, 0.113, 261.7°)` |
| **Safe Emerald (UI/Bold)** | `#117750` | **4.89:1** | **+68.5** | `(0.505, 0.107, 160.9°)` | `#4DD2A0` | **9.61:1** | **-65.8** | `(0.778, 0.137, 164.6°)` |
| **Alert Vermilion (UI/Bold)** | `#C53624` | **4.70:1** | **+66.5** | `(0.548, 0.183, 30.7°)` | `#F79B8E` | **8.73:1** | **-60.7** | `(0.780, 0.113, 28.6°)` |

## 2. Exact APCA-W3 `0.0.98G-4g` Reference Implementation
Constants frozen in `apca-w3` (`0.0.98G-4g`): $R_{\text{co}} = 0.2126729$, $G_{\text{co}} = 0.7151522$, $B_{\text{co}} = 0.0721750$, $\text{mainTRC} = 2.4$, soft black clamp at $Y < 0.022$ with exponent $1.414$, polarity exponents (`0.56`/`0.57` normal; `0.65`/`0.62` reverse), `scale = 1.14`, `loOffset = 0.027`. Executable tests live in `tests/frontend_math.test.mjs` and `tests/test_domain_algorithms.py`.

## 3. Wide-Gamut Display-P3 & CVD Engineering (Machado et al. 2009)
- Define safe sRGB hex fallbacks first, then progressively enhance inside `@media (color-gamut: p3)` using `oklch(...)` (CSS Color 4 chroma-reduction gamut mapping preserves $L$ and $H$ on sRGB panels).
- Under Machado (2009) protanopia/deuteranomaly matrices, red and green merge into similar luminance unless separated by both lightness and redundant geometry (icons + spatial placement + text labels).
- **Anti-Slop Ban List:** Zero pure `#000000` canvases, zero neon outer glows, zero gradient-clipped headlines, zero card-wide glassmorphism spam, zero consecutive identical 3/4-column icon-card grids.
