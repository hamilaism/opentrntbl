# SegmentedControl

Exclusive toggle group — Apple HIG style. Track with subtle border
around the group, inactive segments fully transparent, active segment
renders as a "floating tile" with a distinct background.

Exactly **one option is selected at a time**. Selection is controlled:
the parent owns `value`, the component emits click events.

The live API table is in the **Docs** tab of `Components/SegmentedControl`.
This page focuses on the matrices and guidelines.

## Anatomy

```
[Track: surface-canvas bg (light grey), 1px subtle border, rounded]
  ├─ [Active tile: surface-base bg (raised), box-shadow]   ← emerges from the track
  ├─ [Segment: transparent]   ← hover lightens, pressed fully lightens
  └─ [Segment: transparent]
```

**"Tile emerges from the track" metaphor**: the track is a greyed surface
(`surface-canvas`), inactive segments are transparent — they let the grey
of the track show through. The active segment is white raised
(`surface-base`) with a subtle floating shadow: it **emerges** from the
greyed background, like a depressed key rising back up. On hover over an
inactive segment, the background lightens partially (`color-mix` toward
`surface-base`); on pressed, it lightens fully — the tile gradually
forms under the finger. Consistent with iOS HIG (native segmented control).

**Why this over a flat inverted style**: the legacy version
(`.bitrate-btn.active` = accent gold fill) made the active option visually
dominate. The tile approach keeps all segments visually equivalent — the
active one is just placed slightly higher on the track.

## Props

```ts
type SegmentedControlProps = {
  options: Array<{ value: string | number; label: string }>;
  value: string | number;
  disabled?: boolean;    // permanent lock — feature intentionally unavailable
  loading?: boolean;     // transient lock — async operation in flight
};
```

## Matrix — option count × state

| Option count | Default | Disabled | Loading |
|---|---|---|---|
| 2 options | ✓ | ✓ | ✓ |
| 3 options | ✓ | ✓ | ✓ |
| 4 options (bitrate) | ✓ | ✓ | ✓ |
| 5–6 options | ✓ (getting cramped) | ✓ | ✓ |
| 7+ options | ❌ use a `<select>` dropdown instead |

## Matrix — interaction states per segment

| State | Active segment | Inactive segments |
|---|---|---|
| Default | `bg: surface-base`, box-shadow, `color: text-1` | `transparent`, `color: text-2` |
| `:hover` | _no change_ (already at the target) | `bg: color-mix(transparent, surface-base 50%)`, `color: text-1` |
| `:focus-visible` | outline inset (focus ring inside track) | outline inset (focus ring inside track) |
| `:active` (pressed) | _no change_ | `bg: surface-base` (full lighten) |
| `disabled` (group-level) | opacity 0.4, cursor not-allowed | opacity 0.4, cursor not-allowed |
| `loading` (group-level) | opacity 0.6, cursor wait | opacity 0.6, cursor wait |
| `contrast:enhanced` | + outline `1px solid border-default` (HC visibility patch) | _no change_ |

`disabled` and `loading` lock the whole group — you can't click individual
segments while either is active. They differ in **opacity** and **cursor**
to signal intent:

- `disabled` = colder, more permanent ("this is off")
- `loading` = transient ("something is happening, please wait")

## Disabled vs Loading — when to use which

- **`disabled`** — a feature that is not currently usable. Example: bitrate
  selector disabled when RCA output is active (no variable bitrate on
  analog output).
- **`loading`** — an async operation is in flight after user action.
  Example: user clicked a new bitrate, API call to `/api/settings/bitrate`
  is pending, prevent rapid re-clicks until the response arrives.

**Both true**: `loading` visual takes precedence (opacity 0.6, cursor
wait). Semantically confusing — avoid setting both.

## Guidelines

- **Options should be short and visually comparable.** Numbers
  (`128k` / `192k` / `320k`), short labels (`Day` / `Week` / `Month`),
  or status words. Avoid multi-word labels that wrap.
- **No icons in segments** — our design system doesn't support icon
  segments in V1. If you need iconic choices, compose them upstream
  (toolbar with `Button variant="ghost"` and manual active state).
- **Track border is part of the identity** — don't remove it thinking
  it's decorative. It's the visual cue that the segments are a cohesive
  group, not independent buttons.
- **Match segment widths via CSS flex if needed** — by default segments
  size to their content. For a uniform look (all segments same width),
  wrap with a `flex: 1` container class in your consumer.
- **Use `loading` for pessimistic UI** — lock the group during the API
  call, then update `value` on response. Don't optimistic-update + lock —
  if the API fails, you've shown a wrong state.

## CSS under the hood

Classes: `.seg-track` (group), `.seg-segment` (each option),
`.seg-segment.active` (selected). Plus attribute hooks
`.seg-track[aria-disabled="true"]` and `.seg-track[data-loading="true"]`
for the lock states.

## Related

- `Button` with `variant='toggle'` — for binary on/off (single option).
  SegmentedControl is for 3+ mutually-exclusive options.
- `Input type='number'` — for continuous numeric values that don't map
  to a small finite set.
