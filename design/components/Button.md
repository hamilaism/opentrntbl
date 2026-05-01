# Button

Primitive button. Six semantic variants mapped to CSS classes kept for
`firmware/index.html` compatibility.

The live API table is in the **Docs** tab of `Components/Button`. This page
focuses on the matrices and guidelines.

## Variants

| Variant | Use case | CSS class | Canonical reference |
|---|---|---|---|
| `primary` | Main CTA per screen | `btn btn-1` | — |
| `secondary` | Equal-weight alternative | `btn btn-2` | — |
| `destructive` | Reversible destructive action | `btn btn-disconnect` | — |
| `toggle` | Binary on/off state | `btn-toggle` | — |
| `ghost` | Secondary action in a flow (no fill) | `btn-ghost` | shadcn, Chakra, Radix |
| `tonal` | Subtle fill, attached to content | `btn-tonal` | Material 3 |

## Props

```ts
type ButtonProps = {
  variant: 'primary' | 'secondary' | 'destructive' | 'toggle' | 'ghost' | 'tonal';
  label: string;
  disabled?: boolean;    // default false
  loading?: boolean;     // default false — primary / secondary / destructive
  toggled?: boolean;     // default false — toggle only
  fullWidth?: boolean;   // default varies by variant (see below)
};
```

### `fullWidth` defaults

| Variant | Default `fullWidth` |
|---|---|
| primary, secondary, destructive, toggle, ghost | `true` |
| tonal | `false` |

Override explicitly when you need a primary-inline (`fullWidth: false`) or
a tonal stretched (`fullWidth: true`). Don't do it often — the defaults
are what the rest of the portal expects.

## Matrix — variant × config state

Config states are **prop-driven**. Not all combinations are meaningful.

| Variant      | Default | Toggled | Disabled | Loading |
|--------------|---------|---------|----------|---------|
| primary      | ✓       | _n/a_   | ✓        | ✓       |
| secondary    | ✓       | _n/a_   | ✓        | ✓       |
| destructive  | ✓       | _n/a_   | ✓        | ✓       |
| toggle       | ✓ (off) | ✓ (on)  | ✓        | _rare_  |
| ghost        | ✓       | _n/a_   | _rare_   | _n/a_   |
| tonal        | ✓       | _n/a_   | _rare_   | _n/a_   |

Reading:
- `✓` — canonical use, ship it.
- `_n/a_` — prop has no visual effect on this variant.
- `_rare_` — legal but unusual; prefer another variant for this combo.

## Matrix — interaction states (CSS pseudo-classes)

Interaction states are **user-driven** (browser applies them based on
mouse/keyboard). They compose with config states. `:focus` is an
**independent toggle** that combines with `:hover` or `:active` (pressed).

| Variant      | `:hover` | `:active` (pressed) | `:focus` | `:focus + :hover` |
|--------------|----------|---------------------|----------|-------------------|
| primary      | `opacity: 0.85` | _not defined_ | _browser default_ | _browser default_ |
| secondary    | `bg: surface-hover` | _not defined_ | _browser default_ | combined |
| destructive  | `bg: red-bg` | _not defined_ | _browser default_ | combined |
| toggle (off) | `bg: surface-hover`, `border: text-3` | `scale(0.98) opacity: 0.8` | _browser default_ | combined |
| toggle (on)  | `opacity: 0.85` | _not defined_ | _browser default_ | combined |
| ghost        | _not defined_ | _not defined_ | _browser default_ | _browser default_ |
| tonal        | _not defined_ | _not defined_ | _browser default_ | _browser default_ |

Notes:
- `:focus` is not customized anywhere — relies on browser default outline.
  Future work: once the token/hover refactor lands (Donnie D'Amato pattern,
  `color-mix()` computed states), revisit this matrix.
- `ghost` and `tonal` hover styling is deferred to the same refactor —
  currently they fall through to browser default.

## Viewing interaction states in Storybook

No dedicated "interaction matrix" story. Instead, use the
**Pseudo-states toolbar toggle** on any variant story (Primary, Ghost,
etc.) to force `:hover`, `:focus`, or `:active` on the fly. Provided by
`storybook-addon-pseudo-states`.

## Guidelines

- **One primary per screen.** If you need two prominent CTAs, one is
  `primary`, the other `secondary`. Never two primary side-by-side.
- **`destructive` is reversible.** The red signals intentional — if the
  action is irreversible, add a confirmation step, don't just paint red.
- **`toggle` owns its binary state.** Don't stack `toggle` with
  `disabled + toggled` — confusing combo. If you need to freeze a toggle,
  hide it or re-render as a plain `toggled` label.
- **`ghost` inside text flows** — secondary actions like "Enter manually",
  "Rescan", "Change network". For page-level "Back" / "Cancel" actions,
  use `secondary`.
- **`tonal` for small actions attached to content** — share button next
  to a URL, copy button next to code. Not a first-class CTA.
- **`fullWidth` override sparingly.** The variant defaults encode the
  canonical use. Only override when the context truly demands it.
