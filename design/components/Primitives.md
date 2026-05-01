# Primitives

Tiny visual atoms reused across components. Rendered from small helper
functions in `design/components/primitives.js` — each returns an HTML
string (or DOMElement), no framework runtime required.

## Inventory

| Primitive     | Helper signature | Used in |
|---------------|------------------|---------|
| `spinner`     | `spinner({ small })` | Button (loading), Card (empty state), Reconnect |
| `statusDot`   | `statusDot()`    | StatusBadge |
| `check`       | `check({ on })`  | Card (selected trailing) |
| `brand`       | `brand({ prefix, accent })` | Layout (Brand primitive) |
| `brandBlock`  | `brandBlock(opts)` | Layout (full-width brand wrapper) |

## Spinner

Two sizes via `small` boolean. `small: true` is ~14px (inline in buttons);
default is ~18px (standalone).

## StatusDot

A bare `<span>` — `currentColor` inherits from the parent `.status` class.
Animation (`@keyframes pulse`) only fires when nested under `.status-play`.

## Check

Boolean state via `on`. The checkmark glyph is `::after content: '\2713'`
applied when `.check.on`.

## Brand

Configurable prefix + accent text for the logo lettering. `brandBlock` wraps
it with `.brand` class for the centering + padding.

## Icons

See the dedicated `Primitives/Icons` story for the full gallery and per-icon
controls.

## Guidelines

- **Primitives are never "composed" themselves** — they're the bottom of
  the dependency tree. If two primitives are always used together, merge
  them into a component, don't create a super-primitive.
- **No JSX / framework wrappers.** These are string templates. Consumers
  concat or innerHTML them.
- **Keep the API tiny.** If a primitive needs more than 2 props, it's
  probably a component in disguise — promote it to `Components/`.
