# Layout

Structural primitives for screen scaffolding — TitleBlock, SectionHeader,
WifiBar. Three small primitives, each with a controls-editable story.

## Primitives

- **TitleBlock** — H1 (screen title) + optional subtitle
- **SectionHeader** — H2 for sub-sections within a screen
- **WifiBar** — horizontal bar with signal indicator + SSID (dashboard header)

## What moved elsewhere

- **Brand** → `Primitives/Overview` — it's a lettering primitive, not
  screen-specific
- **Reconnect** → `Components/Row` (`Reconnect (spinner + message)` story) —
  it's a row-shaped composition (spinner in leading slot + message as
  title), not a unique Layout pattern
- **Screens (WiFi setup, Dashboard)** → `Patterns/Screens` — these are
  full-screen illustrative compositions, not reusable components

## Matrix — primitives × use case

| Primitive     | WiFi setup | Dashboard | Settings | Error / empty |
|---------------|------------|-----------|----------|---------------|
| TitleBlock    | ✓ | ✓ | ✓ | ✓ |
| SectionHeader | ✓ (sections) | ✓ (sections) | ✓ (panels) | _rare_ |
| WifiBar       | _n/a_ | ✓ | ✓ (inline in settings) | _n/a_ |

## Guidelines

- **Screen title is unique per screen** — no nested H1.
- **SectionHeader (H2) for sub-divisions** within a screen.
- **Page spacing is owned by `.page`** — `max-width: 480px`, `padding:
  0 20px 80px`. Don't stack primitives directly in body.
- **Don't composite screens from scratch** — see `Patterns/Screens` for
  canonical compositions. If a new layout pattern emerges (e.g. list-
  detail view), add a new primitive here rather than forking one screen.

## Related

- `Primitives/Overview` — Brand lettering, spinner, check, statusDot
- `Components/Row` — for the Reconnect row pattern
- `Patterns/Screens` — full-screen composition examples
