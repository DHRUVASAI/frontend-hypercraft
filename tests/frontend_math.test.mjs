import test from 'node:test';
import assert from 'node:assert/strict';

const MAC_UNIFORM_RE = /^([0-9A-F]{2})([:-])(?:[0-9A-F]{2}\2){4}[0-9A-F]{2}$/;
const SLAP_QUADRANTS = ['ELI (x2)', 'SAI (x6)', 'AAI (xA)', 'Reserved (xE)'];

export function classifyMac(mac) {
  if (typeof mac !== 'string') return { valid: false, kind: 'invalid', reason: 'non-string' };
  const normalized = mac.trim().toUpperCase();
  if (!MAC_UNIFORM_RE.test(normalized)) {
    return { valid: false, kind: 'invalid', reason: 'malformed_or_mixed_separator' };
  }
  const sep = normalized[2];
  const bytes = normalized.split(sep).map((h) => parseInt(h, 16));
  if (bytes.every((b) => b === 0x00)) return { valid: false, kind: 'invalid', reason: 'unspecified' };
  if (bytes.every((b) => b === 0xff)) {
    return { valid: true, kind: 'broadcast', isUnicast: false, isMulticast: true, isLAA: null, slapQuadrant: null };
  }
  const b0 = bytes[0];
  if ((b0 & 0x01) !== 0) {
    return { valid: true, kind: 'multicast', isUnicast: false, isMulticast: true, isLAA: null, slapQuadrant: null };
  }
  const isLAA = (b0 & 0x02) !== 0;
  return {
    valid: true,
    kind: isLAA ? 'unicast-laa' : 'unicast-uaa',
    isUnicast: true,
    isMulticast: false,
    isLAA,
    slapQuadrant: isLAA ? SLAP_QUADRANTS[(b0 >> 2) & 0x03] : null,
  };
}

export function damp(current, target, lambda, dt) {
  return current + (target - current) * (1 - Math.exp(-lambda * Math.min(dt, 0.05)));
}

function parseHex(hex) {
  const m = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!m) throw new Error(`Invalid hex: ${hex}`);
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function wcagContrast(fgHex, bgHex) {
  const lum = (hex) => {
    const [r, g, b] = parseHex(hex).map((v) => {
      const s = v / 255;
      return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const l1 = lum(fgHex);
  const l2 = lum(bgHex);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

export function apcaContrast(txtHex, bgHex) {
  const yOf = (hex) => {
    const [r, g, b] = parseHex(hex).map((v) => (v / 255) ** 2.4);
    const y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b;
    return y < 0.022 ? y + (0.022 - y) ** 1.414 : y;
  };
  const yt = yOf(txtHex);
  const yb = yOf(bgHex);
  if (Math.abs(yb - yt) < 0.0005) return 0;
  if (yb > yt) {
    const sapc = (yb ** 0.56 - yt ** 0.57) * 1.14;
    return sapc < 0.1 ? 0 : (sapc - 0.027) * 100;
  }
  const sapc = (yb ** 0.65 - yt ** 0.62) * 1.14;
  return sapc > -0.1 ? 0 : (sapc + 0.027) * 100;
}

export function sobelHeightToNormal(heights, w, h, strength = 1.0) {
  const out = new Uint8ClampedArray(w * h * 4);
  const at = (x, y) => heights[((y + h) % h) * w + ((x + w) % w)];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const dx = (at(x + 1, y - 1) + 2 * at(x + 1, y) + at(x + 1, y + 1))
               - (at(x - 1, y - 1) + 2 * at(x - 1, y) + at(x - 1, y + 1));
      const dy = (at(x - 1, y + 1) + 2 * at(x, y + 1) + at(x + 1, y + 1))
               - (at(x - 1, y - 1) + 2 * at(x, y - 1) + at(x + 1, y - 1));
      let nx = -dx * strength, ny = -dy * strength, nz = 1.0;
      const len = Math.hypot(nx, ny, nz);
      nx /= len; ny /= len; nz /= len;
      const i = (y * w + x) * 4;
      out[i] = Math.round((nx * 0.5 + 0.5) * 255);
      out[i + 1] = Math.round((ny * 0.5 + 0.5) * 255);
      out[i + 2] = Math.round((nz * 0.5 + 0.5) * 255);
      out[i + 3] = 255;
    }
  }
  return out;
}

export function loupeTransform(x, y, px, py, zoom) {
  return [(x - px) * zoom + px, (y - py) * zoom + py];
}

test('MAC classification enforces uniform separators and exact IEEE 802.3/802c semantics', () => {
  assert.equal(classifyMac('3C:22:FB:11:22:33').kind, 'unicast-uaa');
  assert.equal(classifyMac('3C-22-FB-11-22-33').kind, 'unicast-uaa');
  const laa = classifyMac('DE:AD:BE:EF:00:01');
  assert.equal(laa.kind, 'unicast-laa');
  assert.equal(laa.slapQuadrant, 'Reserved (xE)');
  assert.equal(classifyMac('02:11:22:33:44:55').slapQuadrant, 'ELI (x2)');
  assert.equal(classifyMac('06:11:22:33:44:55').slapQuadrant, 'SAI (x6)');
  assert.equal(classifyMac('0A:11:22:33:44:55').slapQuadrant, 'AAI (xA)');

  const mcast = classifyMac('03:00:5E:00:00:01');
  assert.equal(mcast.kind, 'multicast');
  assert.equal(mcast.isLAA, null);

  const bcast = classifyMac('FF:FF:FF:FF:FF:FF');
  assert.equal(bcast.kind, 'broadcast');
  assert.equal(bcast.isLAA, null);

  assert.equal(classifyMac('AA:BB-CC:DD-EE:FF').valid, false);
  assert.equal(classifyMac('00:00:00:00:00:00').valid, false);
  assert.equal(classifyMac('ZZ:11:22:33:44:55').valid, false);
  assert.equal(classifyMac('AA:BB:CC:DD:EE').valid, false);
});

test('Exponential damping is frame-rate invariant across 60Hz and 120Hz', () => {
  let v60 = 0, v120 = 0;
  for (let i = 0; i < 60; i++) v60 = damp(v60, 1, 4.0, 1 / 60);
  for (let i = 0; i < 120; i++) v120 = damp(v120, 1, 4.0, 1 / 120);
  assert.ok(Math.abs(v60 - v120) < 1e-12);
});

test('Verified palette tokens pass both WCAG 2.1 AA and APCA 0.0.98G-4g targets', () => {
  assert.ok(wcagContrast('#16181D', '#F3F0EA') >= 15.0);
  assert.ok(apcaContrast('#16181D', '#F3F0EA') >= 95.0);
  assert.ok(wcagContrast('#C6CDD9', '#12151B') >= 11.0);
  assert.ok(apcaContrast('#C6CDD9', '#12151B') <= -75.0);
});

test('Sobel height-to-normal maps flat surface to tangent-space (128,128,255)', () => {
  const flat = new Float32Array(9).fill(0.5);
  const rgba = sobelHeightToNormal(flat, 3, 3, 2.0);
  assert.deepEqual([rgba[16], rgba[17], rgba[18], rgba[19]], [128, 128, 255, 255]);
});

test('Loupe 3-step transform preserves pointer as fixed point', () => {
  assert.deepEqual(loupeTransform(120, 80, 120, 80, 3.0), [120, 80]);
  assert.deepEqual(loupeTransform(130, 80, 120, 80, 3.0), [150, 80]);
});
