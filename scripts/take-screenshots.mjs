import { chromium } from 'playwright-core';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

mkdirSync('docs/screenshots', { recursive: true });

const targets = [
  {
    name: 'kineta',
    url: pathToFileURL(path.resolve('examples/kineta-acoustic-monolith.html')).href,
    waitMs: 3000,
  },
  {
    name: 'venkateshwara',
    url: pathToFileURL(path.resolve('examples/venkateshwara-textile-atelier.html')).href,
    waitMs: 3000,
  },
  {
    name: 'garuda',
    url: pathToFileURL('C:/Users/dhruv/Downloads/garuda-v4-fullstack/garuda-v4-fullstack/frontend/index.html').href,
    waitMs: 3000,
  },
  {
    name: 'venkateshwara-v0',
    url: 'https://venkateshwara-brown.vercel.app',
    waitMs: 3000,
  }
];

const browser = await chromium.launch({
  channel: 'chrome',
  headless: true,
  args: ['--allow-file-access-from-files', '--enable-webgl', '--ignore-gpu-blocklist']
});

for (const t of targets) {
  console.log(`Capturing ${t.name} from ${t.url}...`);
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  try {
    await page.goto(t.url, { waitUntil: 'load', timeout: 30000 });
    await page.waitForTimeout(t.waitMs);
    await page.screenshot({ path: `docs/screenshots/${t.name}-desktop.png`, fullPage: false });
    console.log(`  [OK] Saved docs/screenshots/${t.name}-desktop.png`);

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `docs/screenshots/${t.name}-mobile.png`, fullPage: false });
    console.log(`  [OK] Saved docs/screenshots/${t.name}-mobile.png`);
  } catch (err) {
    console.error(`  [ERR] Failed ${t.name}: ${err.message}`);
  } finally {
    await page.close();
  }
}

await browser.close();
console.log('Capture completed successfully.');
