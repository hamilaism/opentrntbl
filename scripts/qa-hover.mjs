/**
 * Capture Button/ToggleOn in 4 states (dark/light × default/hover) so the
 * user can visually verify the dark-mode hover/pressed expressions in
 * semantic.tokens.json.
 *
 * Output: /tmp/qa-shots/hover-{light,dark}-{default,hover,pressed}.png
 */

import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const STORYBOOK = 'http://localhost:6006';
const OUT = '/tmp/qa-shots';

await mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 480, height: 200 }, deviceScaleFactor: 2 });
const page = await ctx.newPage();

async function shot(mode, action, label) {
  const url = `${STORYBOOK}/iframe.html?id=components-button--toggle-on&viewMode=story&globals=color:${mode}`;
  await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(400);

  const btn = page.locator('button.btn-toggle.active').first();
  if (action === 'hover') {
    await btn.hover();
    await page.waitForTimeout(300);
  } else if (action === 'pressed') {
    await btn.hover();
    await page.mouse.down();
    await page.waitForTimeout(300);
  }

  const path = `${OUT}/hover-${mode}-${label}.png`;
  await page.screenshot({ path, fullPage: true });

  if (action === 'pressed') {
    await page.mouse.up();
  }
  console.log(`✓ ${label}-${mode}`);
}

for (const mode of ['light', 'dark']) {
  await shot(mode, 'default', 'default');
  await shot(mode, 'hover',   'hover');
  await shot(mode, 'pressed', 'pressed');
}

await browser.close();
console.log(`\nDone → ${OUT}/`);
