// Coverage story — exercises defensive paths in _helpers.js that normal
// token stories never hit (null guards, unresolved aliases, optional fields).
// Also covers the devIcon(unknownName) → '' branch from icons.js.

import { getByPath, resolve, resolveToken, resolveTypography, dimValue, tokens } from './_helpers.js';
import { devIcon } from '../icons.js';

export default {
  title: 'Dev/Helpers',
  tags: ['!autodocs'],
  parameters: {
    layout: 'padded',
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } },
  },
};

// ---------------------------------------------------------------------------
// Edge cases — covers all null guards + optional typography fields
// ---------------------------------------------------------------------------

export const EdgeCases = {
  name: 'Edge cases (coverage)',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Exercises defensive branches in helpers: null guards, unresolved aliases, non-object token inputs, optional typography fields.' } },
  },
  render: () => {
    const cases = [
      // getByPath — null guard: node goes undefined mid-walk
      { label: 'getByPath("core.nonexistent.deep")', value: getByPath('core.nonexistent.deep') },

      // resolve — unresolved alias (node == null → return original string)
      { label: 'resolve("{nonexistent.token.path}")', value: resolve('{nonexistent.token.path}') },

      // resolveToken — non-object inputs (guards at top of function)
      { label: 'resolveToken(null)', value: resolveToken(null) },
      { label: 'resolveToken("raw string")', value: resolveToken('raw string') },
      // resolveToken — valid token, no modes arg → hits modes || activeModes() branch
      { label: 'resolveToken({ $type:"color", $value:"#fff" })', value: resolveToken({ $type: 'color', $value: '#fff' }) },

      // resolveTypography — with letterSpacing (if path not yet taken)
      {
        label: 'resolveTypography({ letterSpacing: "0.02em" })',
        value: resolveTypography({
          $type: 'typography',
          $value: { fontSize: '14px', lineHeight: '1.5', fontWeight: '400', fontFamily: 'system-ui', letterSpacing: '0.02em' },
        }),
      },

      // resolveTypography — empty $value (all else/if-not-taken branches)
      { label: 'resolveTypography({ $value: {} })', value: resolveTypography({ $type: 'typography', $value: {} }) },

      // dimValue — object form { value, unit } → CSS string
      { label: 'dimValue(core.dimension.10)', value: dimValue(tokens.core.dimension['10']) },
      // dimValue — plain string passthrough
      { label: 'dimValue({ $value: "50%" })', value: dimValue({ $value: '50%' }) },
      // dimValue — no $value key → node itself used (??  fallback branch)
      { label: 'dimValue({ value:1, unit:"rem" })', value: dimValue({ value: 1, unit: 'rem' }) },

      // resolveTypography — missing $value key → falls back to {}
      { label: 'resolveTypography({ $type only })', value: resolveTypography({ $type: 'typography' }) },

      // resolve color-mix with broken alias → node == null ternary branch
      { label: 'resolve color-mix with dead alias', value: resolve('color-mix(in srgb, {dead.alias} 50%, #fff 50%)') },

      // devIcon — unknown name → '' (branch not covered by Row stories)
      { label: 'devIcon("nonexistent")', value: `"${devIcon('nonexistent')}"` },
    ];

    const rows = cases.map(({ label, value }) => `
      <tr>
        <td style="padding:6px 12px;font-family:monospace;font-size:12px;color:#555;white-space:nowrap">${label}</td>
        <td style="padding:6px 12px;font-family:monospace;font-size:12px;font-weight:600">
          ${JSON.stringify(value)}
        </td>
      </tr>
    `).join('');

    return `
      <table style="border-collapse:collapse;font-family:system-ui;font-size:13px;background:#fff;border:1px solid #e5e5e5;border-radius:6px;overflow:hidden">
        <thead>
          <tr style="background:#f5f5f5">
            <th scope="col" style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#888">Call</th>
            <th scope="col" style="padding:8px 12px;text-align:left;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#888">Return value</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  },
};
