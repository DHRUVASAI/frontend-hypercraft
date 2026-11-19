# Studio Three.js PBR, WebGPU/TSL, KTX2 VRAM & Disposal Pipeline (`r152–r181+`)

## 1. Verified Three.js Release Milestones & Color-Space Law
- **`r152+` Color Management:** `renderer.outputColorSpace = THREE.SRGBColorSpace`.
  - **Strict Texture Rule:** Base color (`map`), `emissiveMap`, and `sheenColorMap` MUST set `tex.colorSpace = THREE.SRGBColorSpace`. Data maps (`normalMap`, `roughnessMap`, `metalnessMap`, `bumpMap`, `aoMap`, `alphaMap`) MUST stay linear (`THREE.NoColorSpace`). Setting sRGB on a normal or roughness map silently corrupts PBR reflectance.
- **`r155+` Physically Based Lighting:** `useLegacyLights = false` (removed `r165`); lights use true SI candela/lux units and physically accurate inverse-square attenuation (`decay = 2`).
- **`r160+` AgX Tone Mapping:** `THREE.AgXToneMapping` (`mrdoob/three.js#27362`) desaturates extreme highlights naturally without ACESFilmic's red-to-orange / blue-to-purple hue skew.
- **`r170–r181+` `WebGPURenderer` & TSL (Three.js Shading Language):** Production-ready WebGPU backend with automatic WebGL2 fallback and async `await renderer.init()`. Write custom material hooks in JavaScript **TSL** (compiles automatically to both WGSL and GLSL) instead of fragile `onBeforeCompile` string-patching GLSL chunks.

## 2. Studio IBL Reflections & Telephoto Product Optics
- **Telephoto Compression (`camera.setFocalLength`):** Default 75° FOV distorts industrial products. Setting `camera.setFocalLength(85)` (35 mm default `filmGauge`; updates projection matrix automatically) yields exact vertical FOVs: **`13.21°` at 16:9**, **`17.56°` at 4:3**, **`23.27°` at 1:1**. Use `55–65 mm` for tabletop topologies and `85 mm` for studio hero hardware/textiles.
- **GGX Multi-Scattering & Charlie Sheen:** Three.js `MeshPhysicalMaterial` implements energy-conserving GGX multi-scattering (Turquin 2019 — preventing dark energy loss on rough metals) and Conty & Kulla (SIGGRAPH 2017) `KHR_materials_sheen` (`sheen: 0.85`, `sheenRoughness: 0.62`, temperature-shifted `sheenColor`) for realistic woven textiles.

## 3. GPU VRAM & Geometry Compression (KTX2/Basis Universal + Meshopt)
**The Hidden VRAM Trap:** A 150 KB JPEG at `2048×2048` decompresses on upload to **full uncompressed RGBA8 in GPU VRAM**: $2048 \times 2048 \times 4 = 16\,\text{MB}$ (+ mipmaps $= \mathbf{21.3\,\text{MB}}$ per texture!). Six uncompressed 2K maps crash mobile Safari tabs.
- **KTX2 + Basis Universal (`KTX2Loader`):** Transcodes directly into native hardware GPU block compression (ASTC on mobile, BC7 on desktop) so textures stay compressed in VRAM (`~4–8×` VRAM reduction):
  - Use **`ETC1S`** for albedo/diffuse maps (smallest download + VRAM).
  - Use **`UASTC`** for `normalMap`, `roughnessMap`, and `metalnessMap` (preserves smooth gradients without blocky normal artifacts).
- **Geometry Compression (`EXT_meshopt_compression` vs. Draco):** Prefer **Meshopt** for web interactive showcases—near-Draco gzip sizes with **5–10× faster WASM decode**, avoiding main-thread INP freezes.
- **Draw-Call Budget:** Target `< 50` draw calls on mobile / `< 100` on desktop via `InstancedMesh` (identical fasteners/nodes) or `BatchedMesh` (distinct geometries sharing one PBR material). Tighten directional shadow frustums tightly around the hero object (`±3–5` units, `1024×1024` shadow map) rather than spanning an entire scene.

## 4. Exact 3×3 Sobel Height-to-Tangent-Space-Normal Map Generator
A grayscale 2D `<canvas>` height drawing can drive `bumpMap`/`roughnessMap`, **never a `normalMap`** directly. Convert grayscale height to a linear tangent-space RGB normal map (`flat = rgb(128, 128, 255)`):
```js
export function heightCanvasToNormalTexture(THREE, heightCanvas, strength = 2.2) {
  const { width: w, height: h } = heightCanvas;
  const src = heightCanvas.getContext("2d").getImageData(0, 0, w, h).data;
  const out = document.createElement("canvas");
  out.width = w; out.height = h;
  const ctx = out.getContext("2d");
  const dstImg = ctx.createImageData(w, h);
  const dst = dstImg.data;
  const H = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const dx = (H(x+1,y-1) + 2*H(x+1,y) + H(x+1,y+1)) - (H(x-1,y-1) + 2*H(x-1,y) + H(x-1,y+1));
      const dy = (H(x-1,y+1) + 2*H(x,y+1) + H(x+1,y+1)) - (H(x-1,y-1) + 2*H(x,y-1) + H(x+1,y-1));
      const nx = -dx * strength, ny = -dy * strength, nz = 1.0;
      const inv = 1.0 / Math.hypot(nx, ny, nz);
      const i = (y * w + x) * 4;
      dst[i] = Math.round((nx * inv * 0.5 + 0.5) * 255);
      dst[i+1] = Math.round((ny * inv * 0.5 + 0.5) * 255);
      dst[i+2] = Math.round((nz * inv * 0.5 + 0.5) * 255);
      dst[i+3] = 255;
    }
  }
  ctx.putImageData(dstImg, 0, 0);
  const tex = new THREE.CanvasTexture(out);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.NoColorSpace;
  return tex;
}
```

## 5. Complete GPU Memory Disposal Traversal (Zero WebGL Leaks)
Always dispose `RoomEnvironment` and `PMREMGenerator` immediately after baking `envRT`, and run full traversal on component unmount:
```js
export function disposeThreeScene(scene, renderer, envRT) {
  scene.traverse((obj) => {
    if (obj.geometry) obj.geometry.dispose();
    const mats = Array.isArray(obj.material) ? obj.material : obj.material ? [obj.material] : [];
    for (const m of mats) {
      for (const val of Object.values(m)) {
        if (val && typeof val.dispose === "function" && val.isTexture) val.dispose();
      }
      m.dispose();
    }
  });
  envRT?.dispose();
  renderer.dispose();
}
```
