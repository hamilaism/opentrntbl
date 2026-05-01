import { chromium } from 'playwright';
const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 720, height: 600 }, deviceScaleFactor: 2 });
const page = await ctx.newPage();
for (const m of ['light', 'dark']) {
  await page.goto(`http://localhost:6006/iframe.html?id=semantic-solid--button-states&viewMode=story&globals=color:${m}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  await page.screenshot({ path: `/tmp/qa-shots/solid-states-${m}.png`, fullPage: true });
  console.log(`✓ ${m}`);
}
await browser.close();
