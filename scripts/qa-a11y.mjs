/**
 * Audit a11y violations across all stories using axe-core, in headless
 * Chromium driven by Playwright. Bypasses the addon — runs axe directly
 * against each story iframe.
 *
 * Usage:  node scripts/qa-a11y.mjs
 *
 * Output: prints a per-story summary and a per-rule aggregate.
 */

import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

const STORYBOOK = 'http://localhost:6006';
const OUT = '/tmp/qa-a11y';
await mkdir(OUT, { recursive: true });

// Load axe-core from npm — present as transitive dep via @storybook/addon-a11y
const AXE_PATH = new URL('../node_modules/axe-core/axe.min.js', import.meta.url).pathname;

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 480, height: 800 } });
const page = await ctx.newPage();

// Get story index
const idxResp = await page.goto(`${STORYBOOK}/index.json`);
const idx = await idxResp.json();
const stories = Object.entries(idx.entries)
  .filter(([id, e]) => e.type === 'story')
  .map(([id, e]) => ({ id, title: e.title, name: e.name }));

console.log(`Auditing ${stories.length} stories…`);

const allViolations = [];
const ruleCounts = new Map();

for (const story of stories) {
  const url = `${STORYBOOK}/iframe.html?id=${story.id}&viewMode=story`;
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(300);
    await page.addScriptTag({ path: AXE_PATH });
    const result = await page.evaluate(async () => {
      // Mirror the addon-a11y rule disables from .storybook/preview.js
      // (story-level structural rules don't apply to component previews)
      // eslint-disable-next-line no-undef
      return await axe.run(document, {
        resultTypes: ['violations'],
        rules: {
          'region':                { enabled: false },
          'landmark-one-main':     { enabled: false },
          'page-has-heading-one':  { enabled: false },
          'heading-order':         { enabled: false },
        },
      });
    });
    if (result.violations.length > 0) {
      for (const v of result.violations) {
        allViolations.push({ story: story.id, title: story.title, name: story.name, rule: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length });
        ruleCounts.set(v.id, (ruleCounts.get(v.id) || 0) + v.nodes.length);
      }
      console.log(`✗ ${story.id} — ${result.violations.length} violation(s)`);
    }
  } catch (e) {
    console.log(`! ${story.id} — error: ${e.message}`);
  }
}

console.log(`\n=== SUMMARY ===`);
console.log(`Total violations: ${allViolations.length} across ${new Set(allViolations.map(v => v.story)).size} stories`);
console.log(`\nBy rule:`);
for (const [rule, count] of [...ruleCounts.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${rule.padEnd(35)} ${count} node(s)`);
}

await writeFile(`${OUT}/violations.json`, JSON.stringify({ allViolations, ruleCounts: Object.fromEntries(ruleCounts) }, null, 2));
console.log(`\nFull report → ${OUT}/violations.json`);

await browser.close();
