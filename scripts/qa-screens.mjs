/**
 * QA visual capture — runs Playwright headless against the live Storybook
 * on :6006 and dumps screenshots of the key compositions for visual diff
 * against the pre-Storybook reference screenshots provided by the user.
 *
 * Usage:
 *   node scripts/qa-screens.mjs
 *
 * Output:
 *   /tmp/qa-shots/<story-id>__<mode>.png
 */

import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const STORYBOOK = 'http://localhost:6006';
const OUT = '/tmp/qa-shots';

const targets = [
  // Patterns — key compositions to compare against user references
  { id: 'patterns-screens--dashboard',  modes: { color: 'dark'  }, label: 'dashboard-dark' },
  { id: 'patterns-screens--dashboard',  modes: { color: 'light' }, label: 'dashboard-light' },
  { id: 'patterns-screens--wifi-setup', modes: { color: 'dark'  }, label: 'wifi-setup-dark' },
  { id: 'patterns-screens--wifi-setup', modes: { color: 'light' }, label: 'wifi-setup-light' },

  // Components — variant samplers
  { id: 'components-button--primary',           modes: { color: 'dark' }, label: 'btn-primary-dark' },
  { id: 'components-button--primary',           modes: { color: 'light' }, label: 'btn-primary-light' },
  { id: 'components-button--toggle-on',         modes: { color: 'dark' }, label: 'btn-toggle-on-dark' },
  { id: 'components-segmentedcontrol--bitrate', modes: { color: 'dark' }, label: 'segmented-bitrate-dark' },
  { id: 'components-segmentedcontrol--bitrate', modes: { color: 'light' }, label: 'segmented-bitrate-light' },
  { id: 'components-card--with-rows',           modes: { color: 'dark' }, label: 'card-rows-dark' },
  { id: 'components-card--with-rows',           modes: { color: 'light' }, label: 'card-rows-light' },
  { id: 'components-alert--warning',            modes: { color: 'dark' }, label: 'alert-warning-dark' },
  { id: 'components-alert--warning',            modes: { color: 'light' }, label: 'alert-warning-light' },
  { id: 'components-statusbadge--playing',      modes: { color: 'dark' }, label: 'status-playing-dark' },
];

await mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 480, height: 900 } });
const page = await ctx.newPage();

let ok = 0, fail = 0;
for (const t of targets) {
  const params = new URLSearchParams({
    id: t.id,
    viewMode: 'story',
    globals: Object.entries(t.modes).map(([k, v]) => `${k}:${v}`).join(','),
  });
  const url = `${STORYBOOK}/iframe.html?${params.toString()}`;
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500); // let fonts settle
    const path = `${OUT}/${t.label}.png`;
    await page.screenshot({ path, fullPage: true });
    console.log(`✓ ${t.label}`);
    ok++;
  } catch (e) {
    console.log(`✗ ${t.label}: ${e.message}`);
    fail++;
  }
}
console.log(`\nDone — ${ok} ok / ${fail} failed → ${OUT}/`);
await browser.close();
