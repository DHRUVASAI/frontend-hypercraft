# Build Screenshots Capture Guide

Run the included Playwright capture harness locally (requires Node 18+ and Chromium):

```bash
npm install -D playwright
npx playwright install chromium
VE_V0_URL="https://venkateshwara-brown.vercel.app" \
KINETA_LOVABLE_URL="https://<your-lovable-url>" \
GARUDA_URL="http://localhost:8000" \
node scripts/capture-screenshots.mjs
```

This outputs calibrated `2×` Retina desktop (`1440×900`) and mobile (`390×844`) PNGs for all 5 builds directly into `docs/screenshots/`.
