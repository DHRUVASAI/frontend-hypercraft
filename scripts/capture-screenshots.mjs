import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const TARGETS = [
  { name: 'venkateshwara-v0', url: process.env.VE_V0_URL || 'https://venkateshwara-brown.vercel.app' },
  { name: 'venkateshwara-direct', url: process.env.VE_DIRECT_URL || 'http://localhost:4173/ve.html' },
  { name: 'kineta-lovable', url: process.env.KINETA_LOVABLE_URL || 'http://localhost:4173/kineta-lovable' },
  { name: 'kineta-direct', url: process.env.KINETA_DIRECT_URL || 'http://localhost:4173/kineta.html' },
  { name: 'garuda-v4', url: process.env.GARUDA_URL || 'http://localhost:8000' },
];

mkdirSync('docs/screenshots', { recursive: true });
const browser = await chromium.launch();

for (const { name, url } of TARGETS) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: `docs/screenshots/${name}-desktop.png`, fullPage: false });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(400);
    await page.screenshot({ path: `docs/screenshots/${name}-mobile.png`, fullPage: false });
    console.log(`[OK] Captured ${name} (${url})`);
  } catch (err) {
    console.error(`[SKIP] Could not capture ${name} (${url}): ${err.message}`);
  } finally {
    await page.close();
  }
}
await browser.close();
