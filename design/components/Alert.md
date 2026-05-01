# Alert

Standalone panel for contextual messages. Distinct from `Card` — uses its
own `.alert` CSS class with an integrated icon slot and internal padding.

Four semantic variants, each with its own icon background color and default
SVG icon.

## Variants

| Variant | Icon bg (token) | Default icon | Typical use case (openTRNTBL) |
|---|---|---|---|
| `warning` | `--status-warning-bg` | `warning` (triangle + !) | Network unreachable, weak signal, speaker disappeared |
| `error` | `--status-danger-bg` | `error` (circle + ×) | Stream failed, ALSA device missing, firmware update failed |
| `success` | `--status-success-bg` | `success` (check circle) | Settings saved, firmware update applied |
| `info` | `--status-info-bg` | `info` (circle + i) | Firmware update available, onboarding tips |

## Props

```ts
type AlertProps = {
  variant?: 'info' | 'warning' | 'error' | 'success';  // default 'warning'
  title?: string;        // optional, bold 15px, above body
  body: string;          // main text (14px), supports inline <strong>/<em>
  icon?: IconName;       // override — default per variant
};
```

## Matrix — variant × content layout

Title is optional. Body is always present. Icon defaults to the variant's
semantic icon, can be overridden.

| Variant | Body only | Title + body | Custom icon |
|---|---|---|---|
| warning | ✓ | ✓ | ✓ (any from ICONS map) |
| info | ✓ | ✓ | ✓ |
| error | ✓ | ✓ | ✓ |
| success | ✓ | ✓ | ✓ |

All 12 cells are legal.

## Matrix — interaction states

Alert is **read-only** — no hover, focus, pressed, or loading states. It's
a message, not an action. If you need a dismissable alert or one with an
action, compose Alert + Button within a Card (not a single-component
pattern yet).

## Guidelines

- **One Alert at a time per screen.** Stacking multiple alerts creates
  noise and hierarchy confusion. If you genuinely need multiple, reconsider
  the information architecture.
- **Body takes inline HTML** — use `<strong>` to emphasize a specific
  value (network name, speaker name). Keep tags minimal (bold, italic);
  the Alert isn't a full rich-text surface.
- **Title is optional.** Short alerts ("The network MyHomeWiFi is unreachable.")
  don't need a title. Multi-paragraph alerts benefit from one.
- **Variant semantic is fixed** — don't reuse warning for an info message
  just because orange "looks nice". Readers rely on color + icon to parse
  severity at a glance.
- **Don't add actions inside Alert today.** If you need "Retry" or
  "Dismiss", compose:
  ```
  <Card>
    <Alert variant="error" body="..." />
    <Row trailing="none" title="...">Retry button inside row</Row>
  </Card>
  ```
  Until we have a proper actionable-alert pattern, keep it manual.

## Related

- `StatusBadge` — for transient read-only status (playing, paused). Alert
  is for heavier messages with context; StatusBadge is for one-word state
  display.
- `Card` — the surface primitive. Alert is NOT a variant of Card — it's
  its own panel with its own CSS class.
