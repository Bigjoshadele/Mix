# AutoMix — Visual Identity

## Concept

A software mastering rack, not a generic form. The subject is audio
hardware — a channel strip or mastering unit's front panel — so the UI
borrows its vocabulary: hairline section dividers, small-caps monospace
labels, an illuminated primary control, and a segmented LED meter instead
of a stock progress bar.

## Palette

| Token | Hex | Use |
|---|---|---|
| `bg` | `#17181B` | App background (charcoal, near-black) |
| `panel` | `#1D1F23` | Input fields, meter background |
| `hairline` | `#33353A` | Section dividers, unlit meter segments |
| `text-primary` | `#ECEAE4` | Headlines, field values |
| `text-muted` | `#8B8D93` | Section labels, status line |
| `amber` | `#E8A33D` | Primary action (Process button, low/mid meter) |
| `amber-dim` | `#6B5327` | Primary action, disabled state |
| `teal` | `#3ED6C0` | Secondary accent, meter mid-high |
| `red` | `#E5484D` | Meter peak / clip warning |

## Type

- **Display** — Segoe UI Semibold, 20pt. Used once, for the "AUTOMIX" wordmark.
- **Label** — Consolas 9pt, letter-spaced via CAPS. Section headers and
  the status line read like hardware silkscreen text.
- **Body** — Segoe UI 10pt. Field values, dropdown text.
- **Button** — Segoe UI Semibold 12pt. Only the Process button uses this
  weight at this size.

## Layout

Single column, fixed width, four horizontal sections separated by 1px
hairlines: Input → Genre → Output → Transport. No cards, no shadows, no
rounded panels — flat and structural, like a rack fascia.

## Signature element

The **segmented LED meter** (`LEDMeter` in `automix_gui.py`). 24
rectangles, amber → teal → red by position, sweeping while a mix
renders. It's both the header decoration at idle and the busy indicator
while processing — one motif instead of a generic spinner bolted onto a
generic layout.

## App icon

`assets/automix.ico` / `assets/icon.png` — a charcoal circular badge with
a 5-bar level meter. Regenerate with `python make_icon.py` after any
palette change.
