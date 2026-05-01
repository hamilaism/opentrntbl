// openTRNTBL — Token resolver helpers for Storybook stories.
//
// Loads the three source files (core, primitives, semantic) + icons,
// and resolves alias chains + mode overrides.
//
// Usage inside a story:
//   import { resolve, getByPath, tokens, activeModes } from './_helpers.js';
//   const hex = resolve('{semantic.surface.canvas}');

import core       from '../../tokens/src/core.tokens.json';
import primitives from '../../tokens/src/primitives-openTRNTBL.tokens.json';
import semantic   from '../../tokens/src/semantic.tokens.json';
import icons      from '../../tokens/src/icons.tokens.json';

// Flat merge — top-level keys "core", "primitives/openTRNTBL", "semantic", "icons"
export const tokens = {
  ...core,
  ...primitives,
  ...semantic,
  ...icons,
};

// Active modes read from <body data-*> set by .storybook/preview.js.
export function activeModes() {
  const b = document.body.dataset;
  return {
    color:    b.color    || 'light',
    contrast: b.contrast || 'default',
    vision:   b.vision   || 'default',
    density:  b.density  || 'default',
  };
}

// Walk a dotted path inside the tokens tree.
export function getByPath(path) {
  const parts = path.split('.');
  let node = tokens;
  for (const p of parts) {
    if (node == null) return null;
    node = node[p];
  }
  return node;
}

// Resolve a value recursively: alias strings, mode overrides, matrix colors, color-mix.
export function resolve(value, modes = null) {
  const active = modes || activeModes();

  // Alias string like "{semantic.surface.canvas}"
  if (typeof value === 'string' && value.startsWith('{') && value.endsWith('}')) {
    const path = value.slice(1, -1);
    const node = getByPath(path);
    if (node == null) return value; // unresolved, return as-is
    return resolveToken(node, active);
  }

  // color-mix() with alias inside — keep as CSS, but resolve aliases within
  if (typeof value === 'string' && value.startsWith('color-mix(')) {
    return value.replace(/\{([^}]+)\}/g, (m, path) => {
      const node = getByPath(path);
      return node == null ? m : resolveToken(node, active);
    });
  }

  // Matrix color value { colorSpace, components, hex, alpha }
  if (value && typeof value === 'object' && value.hex) {
    return value.hex;
  }

  // Literal (number, hex string, etc.)
  return value;
}

// Resolve a full token (node with $type + $value + potentially $extensions.modes).
export function resolveToken(token, modes = null) {
  if (!token || typeof token !== 'object') return token;
  if (!('$type' in token) && !('$value' in token)) {
    // A group. Return as-is (shouldn't usually happen during resolve).
    return token;
  }
  const active = modes || activeModes();
  let value = token.$value;

  // Apply mode overrides from com.opntrntbl.modes
  const overrides = token.$extensions?.['com.opntrntbl.modes'];
  if (overrides) {
    // Find best-matching override — we match any key whose axes all match active modes.
    for (const [key, override] of Object.entries(overrides)) {
      const terms = key.split('|'); // e.g. "color:dark|contrast:enhanced"
      const allMatch = terms.every(term => {
        const [axis, variant] = term.split(':');
        return active[axis] === variant;
      });
      if (allMatch) {
        value = override;
      }
    }
  }

  return resolve(value, active);
}

// Typography token resolves into a style object.
export function resolveTypography(token) {
  const v = token.$value || {};
  const style = {};
  if (v.fontSize)      style.fontSize      = resolve(v.fontSize);
  if (v.lineHeight)    style.lineHeight    = resolve(v.lineHeight);
  if (v.fontWeight)    style.fontWeight    = resolve(v.fontWeight);
  if (v.fontFamily) {
    const ff = resolve(v.fontFamily);
    style.fontFamily = Array.isArray(ff) ? ff.join(', ') : ff;
  }
  if (v.letterSpacing) style.letterSpacing = resolve(v.letterSpacing);
  return style;
}

// Apply dimension value: returns CSS string "1rem" or "16px"
export function dimValue(node) {
  const v = resolve(node.$value ?? node);
  if (v && typeof v === 'object' && 'value' in v && 'unit' in v) {
    return `${v.value}${v.unit}`;
  }
  return v;
}

// WCAG contrast ratio between two hex colors.
export function contrast(hex1, hex2) {
  const lum = (hex) => {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;
    const lin = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  };
  const l1 = lum(hex1);
  const l2 = lum(hex2);
  const hi = Math.max(l1, l2);
  const lo = Math.min(l1, l2);
  return (hi + 0.05) / (lo + 0.05);
}

export function wcagBadge(ratio) {
  if (ratio >= 7)   return { label: 'AAA',   color: '#0a8f3a' };
  if (ratio >= 4.5) return { label: 'AA',    color: '#4a9' };
  if (ratio >= 3)   return { label: 'AA UI', color: '#e85' };
  return { label: 'FAIL', color: '#c33' };
}
