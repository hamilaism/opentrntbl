# Row

List item primitive. Always lives inside a `Card`. One component covers
speaker rows (Sonos, RCA), WiFi network rows, and informational rows.

The live API table is in the **Docs** tab of `Components/Row`. This page
focuses on the matrices and guidelines.

## Props

```ts
type RowProps = {
  title: string;
  subtitle?: string;         // empty = hidden
  icon?: IconName;           // undefined = no icon
  trailing?: 'none' | 'check' | 'signal';  // default 'none'
  selected?: boolean;        // trailing=check only
  loading?: boolean;
  secured?: boolean;         // trailing=signal only
  signal?: 0 | 1 | 2 | 3 | 4; // trailing=signal only
};
```

## Trailing composition

The `signal` trailing is not atomic — it composes three elements
automatically when set:

| Element | Condition |
|---------|-----------|
| 🔒 lock icon | `secured: true` |
| Signal bars | `signal` value (0–4) |
| Chevron `›` | always (implies click-to-drill-in) |

This matches the firmware's real WiFi row: `[lock if secured] [bars] [›]`.

## Matrix — trailing × config state

| Trailing | Default | Selected | Loading |
|----------|---------|----------|---------|
| none     | ✓       | _n/a_    | ✓       |
| check    | ✓       | ✓        | ✓       |
| signal   | ✓       | _n/a_    | ✓       |

`selected` is only meaningful for `trailing: 'check'`.

## Matrix — interaction states (CSS pseudo-classes)

Same for all trailing values (the `.row` class handles interactions).

| State    | Behavior                                              |
|----------|-------------------------------------------------------|
| `:hover` | `background: var(--surface-raised-background)` |
| `:active` (pressed) | _not customized_ |
| `:focus` | _browser default_ |
| `.loading` | `opacity: 0.5; pointer-events: none` |

Force interaction states in Storybook via the **Pseudo-states toolbar**.

## Guidelines

- **One Row inside a Card, minimum.** Single-row cards are fine, but
  you can also stack multiple rows — `.row + .row` draws a divider.
- **Icon is optional** — speaker rows have one (the `type` maps via
  `icons.js`), WiFi rows don't. Don't force an icon when the content is
  purely textual.
- **Subtitle is optional** — skip it when the title alone is self-
  explanatory. Don't fill the space with filler.
- **`signal` trailing is opinionated** — it assumes the row is clickable
  and navigates to a detail (hence the chevron). For purely
  informational rows with signal bars, use `trailing: 'none'` and place
  the bars in your own layout.
- **`check` is single-select or multi-select agnostic** — the row
  primitive only knows "selected or not". Multi-select logic (group
  speakers under the vinyl source) is managed by the parent.
- **`loading` is row-scoped** — if the whole list is loading, use
  `Card / Empty` (centered spinner) instead of every row with loading.
- **Never hard-code icons per speaker name.** Always route through the
  `icon` prop driven by speaker `type` from UPnP metadata.

## Related

- `Card` — the surface primitive that holds rows.
- `Alert` — standalone panel, not a row.
- See the `Gallery` story for all device icon types rendered as Rows (used
  to be a separate `SpeakerCard` component — dropped since it was a thin
  wrapper with no added value).
