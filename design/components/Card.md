# Card

Surface container primitive. Holds `Row`, `Alert`, `Input`, or custom
content. Minimal API — optional accessibility props only.

The live API table is in the **Docs** tab of `Components/Card`. This page
focuses on composition patterns, spacing, and accessibility.

## Props

```ts
type CardProps = {
  children: HTMLContent;           // required — the composed content
  role?: 'group' | 'region' | null;            // default null (presentational)
  ariaLabel?: string;                           // required if role is set
};
```

Card has **no visual props**. Variants, padding, borders — none of that.
The children own their layout.

## Accessibility

Card is purely presentational by default (`<div class="card">`). For
screen readers, this is invisible structure — each child (Row = button,
Input = form field, Alert = message) is announced individually.

**When to set `role`** :
- **`role="group"`** — Card groups related controls or fields (Sonos
  speaker pickers, WiFi network lists, settings panels). Pair with
  `ariaLabel` describing the group like `"Sonos speakers"`.
- **`role="region"`** — Card represents a significant page landmark
  (rare in the portal; use sparingly).
- **`role={null}`** (default) — purely decorative grouping. No impact on
  screen reader structure.

**Why not `role="list"`** : ARIA `list` semantics require `<li>` children
(or elements with `role="listitem"`). Our Row primitive renders as
`<button>` — using `role="list"` on the Card would trigger
`aria-required-children` violations in axe. `role="group"` is the
correct alternative for "a set of related buttons/controls".

**Why opt-in** : Card doesn't know what it contains, so it can't
auto-detect the right role. The developer declares intent explicitly.

Pairing with a visible heading (outside the Card) + `aria-labelledby`
pointing to the heading's `id` is even better than `ariaLabel` — the
screen reader announces the same text the sighted user reads. Left out
of the V1 API to keep it lean; add `ariaLabelledBy?: string` when
needed.

## Spacing

**Card does NOT own a margin.** Parents control spacing via CSS
`flex + gap` :

```css
.my-screen-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-default);   /* or any --spacing-* token */
}
```

```html
<div class="my-screen-section">
  <div class="card">…</div>
  <div class="card">…</div>
  <div class="card">…</div>
</div>
```

**Why** :
- No need to override `margin-bottom:0` on the last Card
- Parent controls density per context (list = tight, dashboard = loose)
- Modern CSS pattern, cleaner than legacy margin-collapse

## Composition patterns

### Card + multiple Rows (most common)

```html
<div class="card" role="group" aria-label="Sonos speakers">
  <button class="row">…</button>
  <button class="row">…</button>
</div>
```

Card's `overflow: hidden` clips the rows to the `radius-lg` corners.
Row-to-row separator (`.row + .row { border-top: 0.5px solid divider }`)
is automatic.

### Card + single Row

Same pattern with one Row. No visual gotcha — Card is still a Card.

### Card + Alert (not recommended)

`Alert` is a standalone panel with its own `.alert` class. Don't nest
an Alert inside a Card — use either one or the other.

### Card + Input (form pattern)

```html
<div class="card" role="group" aria-label="WiFi credentials">
  <div class="inp-group">
    <label class="inp-label" for="ssid">SSID</label>
    <input class="inp" id="ssid" type="text" />
  </div>
</div>
```

One Input per Card for simple forms. Stack multiple `.inp-group` inside
for grouped fields.

### Card + custom content

Card accepts arbitrary children as long as they own their padding and
layout. Good for one-off widgets (stream URL display, settings panel,
tokens viewer).

## Guidelines

- **No nested Cards.** Don't put a Card inside a Card. If you feel the
  need, your content probably needs a different primitive or a panel
  header.
- **Max-width is a child concern**, not a Card concern. Card fills its
  parent by default. The portal applies `.page { max-width: 480px }` at
  the page level.
- **Do NOT add `margin` to Card** via styles. Use `flex + gap` on the
  parent. This is intentional — see Spacing section.
- **Interactive rows** (`<button class="row">`) inside a Card with
  `role="group"` read naturally: "Sonos speakers group, 3 items, Row
  title 1, button, selected…"

## Related

- `Row` — list-item that goes inside Card.
- `Alert` — standalone panel (separate primitive, do NOT nest in Card).
- `Input` — form field, typically wrapped in a Card with `role="group"`.
