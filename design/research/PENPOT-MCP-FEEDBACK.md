# Penpot MCP / Plugin SDK — Bug feedback

Bug feedback from integrating Claude Code (LLM with tool use) with the Penpot MCP server to automate a design system for an open-source firmware (`openTRNTBL`).

## Setup

| | |
|---|---|
| Penpot version | 2.15.0 (production, design.penpot.app) |
| MCP server | `@penpot/mcp@2.15.0-rc.2` (published 2026-04-28, tagged `latest`+`stable` but remains RC) |
| MCP mode | Remote (`https://design.penpot.app/mcp/stream?userToken=…`) |
| Client | Claude Code + Anthropic SDK (LLM with tool use) |
| Use case | Creation + maintenance of a multi-layer DS (core / primitives / semantic) with sets + Tokens Studio themes |

## Recap table

| ID | Bug | Severity | Reproduced in SDK | Workaround |
|---|---|---|---|---|
| A | `shape.applyToken(token)` rejects any color token with generic error | **Blocking** | Yes, 4 variants tested | LibraryColor.asFill() |
| B | `set.remove()` → `tokens.addSet({name: same})` rejects for collision | High | Yes | Detect and keep the existing set |
| C | `theme.activeSets` contains phantom entries `{id: "", name: null}` after drag-drop UI import | Medium | Yes | Drag-drop replace clean |
| D | `theme.addSet(set)` doesn't persist (regression of #8698?) | High | Yes | Drag-drop UI import (bypass SDK) |
| E | `set.addToken({...})` in loop: only the last walked persists | Blocking for bulk | Yes | Drag-drop UI import |

---

## Bug A — `applyToken` rejects any color token (CRITICAL, UNDOCUMENTED)

### Minimal reproduction

```javascript
// Setup: an active theme (Brand) that activates the core set
const tokens = penpot.library.local.tokens;
const core = tokens.sets.find(s => s.name === 'core');
const tok = core.tokens.find(t => t.name === 'palette.gold.50');
// tok = { id, name: 'palette.gold.50', type: 'color', value: '#563f00', description: '...' }

const r = penpot.createRectangle();
r.x = 100; r.y = 100;
r.resize(80, 80);

r.applyToken(tok, ['fill']);
// throws: [PENPOT PLUGIN] Value not valid: Field message is invalid: . Code: :error
```

### Tested variants (all fail)

| Signature | Result |
|---|---|
| `r.applyToken(tok, ['fill'])` | `Field message is invalid` |
| `r.applyToken(tok)` (default property) | `Field message is invalid` |
| `r.applyToken(tok, 'fill')` (string instead of array) | `Field message is invalid` (×2 in the message) |
| `tok.applyToShapes([r], ['fill'])` | `Doesn't support name: 0` |

### Details

- The token is validly retrieved (has an `id`, `type: 'color'`, `value: '#563f00'`)
- The parent set is active (`core.active === true` after activating the `Brand/Sonos-like` theme)
- The rectangle is validly created (appears on the canvas with a default fill)
- The bug is observed on the `libs&screens` file which contains 11 sets / 13 themes / 478 tokens imported via UI drag-drop

### Why it's blocking

The `applyToken` API is the **only** documented mechanism to programmatically link a shape to a design token. Without it, impossible to generate visual token documentation (swatches, samples) that remains linked to source values. We fall back to hex copy-paste (hardcoded values) or to native Penpot LibraryColors (which are NOT tokens).

### Suggestion

1. **Improve the error message**: "Field message is invalid" + `Code: :error` provides no actionable signal. Return at least the validation schema name and the path that failed.
2. **Document the types supported per shape type**: is `applyToken(colorToken, ['fill'])` supported on all shape types? If not, list the valid combinations.
3. **Check async race**, as in #8698 — the token may have an `id` but the state map hasn't propagated yet for the reverse-lookup (similar to proxy returns nil name).

---

## Bug B — `set.remove()` then `addSet({name: same})` rejects for collision

### Reproduction

```javascript
const tokens = penpot.library.local.tokens;

const old = tokens.sets.find(s => s.name === '__test_set');
if (old) old.remove();
// re-query
console.log(tokens.sets.find(s => s.name === '__test_set'));  // null (expected)

const set = tokens.addSet({ name: '__test_set' });
// throws: Field name is invalid: A collection with the same name already exists
```

### Details

- Confirmation that `remove()` "succeeded": the post-remove query no longer finds the set
- But `addSet` after fails with collision on the same name
- Hypothesis: async state race similar to #8698 — the remove isn't yet propagated to the backend when the addSet is validated

### Workaround

Before creating a set, check if it exists and reuse it instead of remove-then-add.

---

## Bug C — Phantom entries `{id: "", name: null}` in `theme.activeSets`

### Symptom

After a UI drag-drop import of a Tokens Studio JSON bundle (with `selectedTokenSets`), some themes have `activeSets` entries pointing to no existing set:

```javascript
const theme = tokens.themes.find(t => t.group === 'Brand' && t.name === 'Sonos-like');
console.log(theme.activeSets);
// [
//   { id: "...real id...", name: "core" },
//   { id: "...real id...", name: "primitives/openTRNTBL" },
//   { id: "", name: null },          // ← PHANTOM
//   { id: "...real id...", name: "semantic-base" }
// ]
```

### Root cause identified on our side

Our bundle referenced in `selectedTokenSets` a set name (`icons` and `mode/light`) that was **empty** in the bundle (filtered at the edge). Penpot doesn't materialize an empty set → the reference remains, but without target.

### Expected behavior

Either:
- Penpot ignores `selectedTokenSets` pointing to a non-materialized set (silent drop, OK)
- Or Penpot creates the empty set when referenced (consistency)

Current: creates an orphan reference that remains displayed as an empty line in the TS panel and cannot be cleaned in the SDK (`theme.removeSet({id: "", name: null})` rejects `Value not valid` because it's not a valid TokenSet).

### Workaround

Regenerate the bundle without the dead reference on the source side, then re-drag-drop replace.

---

## Bug D — `theme.addSet(set)` doesn't persist (regression of #8698?)

Issue #8698 documents exactly this behavior and is marked **closed** (PR #8700) in March 2026. But we still observe it in Penpot **2.15.0** (April 2026), with the MCP `2.15.0-rc.2`.

### Reproduction

```javascript
const tokens = penpot.library.local.tokens;
const set = tokens.addSet({ name: '__bugcheck_set' });
['a', 'b', 'c'].forEach(n =>
  set.addToken({ name: n, type: 'color', value: '#'+n.repeat(6) })
);
const theme = tokens.addTheme({ group: 'BugCheck', name: '__bugcheck_theme' });
theme.addSet(set);

console.log({
  setTokens: set.tokens.length,           // observed: 1 (instead of 3) — bug E
  themeActive: theme.activeSets.length,   // observed: 0 (instead of 1) — bug D
});
```

### Hypothesis

Either PR #8700 wasn't cherry-picked into the 2.15 branch, or it introduces a regression specific to another case. To confirm with the Penpot team.

---

## Bug E — `addToken` in loop: only the last persists

Confirmed on Penpot 2.14.1 and 2.15.0. The code above (bug D) creates 3 tokens (`a`, `b`, `c`) but after inspection, `set.tokens` only contains `c` (the last walked). For bulk import, we are forced to go through UI drag-drop (which works well — so it's not a JSON parsing bug, just an SDK API one).

---

## General suggestions for the Penpot team

1. **End-to-end integration tests via plugin SDK**: the matrix `addSet` × `addToken` × `addTheme` × `addSet on theme` × `applyToken` currently has no E2E test (to our knowledge). Bugs A-E are all basic use cases that a minimal test would have caught.

2. **Actionable error messages**: `Value not valid: Field message is invalid: . Code: :error` is an empty string that provides no debugging signal. At minimum: field name + value received + value expected.

3. **Document the `applyToken` scope**: which token types × which shape types × which properties are supported in the plugin API? Currently the doc lists the properties (`'fill'`, `'strokeColor'`, etc.) but not the support matrix.

4. **MCP RC versions tagged `latest`+`stable`**: `@penpot/mcp@2.15.0-rc.2` is marked `latest` and `stable` on npm. It's to allow compat with Penpot 2.15 in prod, but for a user who runs `npx @penpot/mcp@latest`, they get an RC that contains these bugs without knowing it. Suggestion: tag as `latest` only the non-RC, keep `2.15.0-rc.2` accessible but under `next` or `beta`.

---

## Expected vs observed behavior (recap)

| Action | Expected | Observed (Penpot 2.15.0 + MCP 2.15.0-rc.2) |
|---|---|---|
| `shape.applyToken(colorToken, ['fill'])` | shape.fills attached to the token, getStyle reflects the resolved value | `Field message is invalid` |
| `set.remove()` then `addSet({name: same})` | Succeeds after remove | "A collection with the same name already exists" |
| Bundle JSON drag-drop with `selectedTokenSets` pointing to an empty set | Either empty set created, or ref ignored | Orphan reference `{id: "", name: null}` in theme |
| `theme.addSet(set)` after `tokens.addSet(...)` | Set active on the theme | `theme.activeSets.length === 0` |
| Loop `set.addToken({...})` × N | N tokens in `set.tokens` | Only the last walked persists |

## Global workaround adopted

1. **Initial setup**: UI drag-drop of a JSON bundle generated (by external Python script) instead of programmatic SDK
2. **Visual token documentation**: native Penpot LibraryColors (created via SDK, which works) instead of tokens. Trade-off: duplication maintained by sync script.
3. **Fine modifications**: not feasible programmatically. Drag-drop replace to rebase, or manual modifications via the TS panel in the UI.
