---
type: spec
scope: [renderer]
status: active
date: 2026-04-10
source_of_truth: false
tags: [rendering, behavior]
---

# Rendering behavior

## Context-aware rendering (parent prop)

Components change behavior via `parent` prop (`BlockParent`):
- `'editor'` → interactive slots, click handlers active, empty slots show clickable placeholders
- `'grid'` → read-only preview in collection grid
- `'streamEditor'` → read-only in stream block list
- Thumbnail mode (`.block--thumb` CSS class) → skips mobile responsive overrides

## Public gallery interaction

1. Click art slot → show QuickView panel (floating metadata card at click position)
2. "View full" in QuickView → hide QuickView, show Lightbox with full-size image
3. Close Lightbox → return to gallery context

QuickView is a portal to `document.body`. Only one instance at a time (singleton). Scroll fades QuickView out. Escape closes it.

## Admin gallery interaction

Clicking a slot in editor mode dispatches a Hit event. The context handles the hit (e.g., dispatching Journey to Catalog for art selection).

## Content reference resolution

GalleryBlockView and ComposableBlockView accept resolver functions to decouple rendering from data source. Resolution is deferred — components render what the resolver returns; `undefined` means the referenced entity is not loaded.

## Mobile responsive behavior

At ≤820px breakpoint:
- All multi-column layouts collapse to single column
- Custom appearance `columnRatios` overrides are disabled (`grid-template-columns: 1fr !important`)
- Aspect ratio unset
- Thumbnail mode (`.block--thumb`) skips these overrides

## Related

- [Rendering component hierarchy](../architecture/architecture--renderer--component-hierarchy.md)
