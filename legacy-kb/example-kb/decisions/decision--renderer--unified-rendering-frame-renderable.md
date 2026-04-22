---
type: decision
scope: [renderer]
status: in-progress
date: 2026-02-23
source_of_truth: false
tags: [constitution, adr-005, rendering]
---

# Unified rendering model: Frame + Renderable

## Context

Rendering of core entities (Block, Stream thumbnail, ArtItem preview) drifted across screens. Styles and layout logic became duplicated and inconsistent across public pages, admin editors, and previews.

## Decision

Introduce a unified rendering system converging toward two concepts:

- **Frame** — container with consistent behavior (sizing, padding, click areas, aspect ratio)
- **Renderable** — contract describing what is rendered, in which mode, and with which appearance

## Current status (partial implementation)

### Completed
- Frame component at `shared/ui/Frame/` with modes: `embedded | card | thumbnail`
- ArtPicture component at `shared/ui/ArtPicture/` — shared `<picture>` replacing 4 duplicated render paths
- LAYOUT_SCHEME unified as single source of truth in `entities/block/block.types.ts`
- Unified `GalleryBlockView` at `shared/ui/GalleryBlockView/GalleryBlockView.tsx`
  - Used by: public ImageComponent, admin GalleryComponent (block + stream editors), BlockCustomizer
  - Props: `block, resolveArt, onSlotClick?, renderEventSlot?, renderEmptySlot?, renderArtContent?, children?, className?`
- Frame adopted in CollectionGrid (each block card wrapped in `<Frame mode="card" aspectRatio="4/3">`)

### Deferred
- Full Renderable type contract — will be introduced with custom appearance (colors, spacing)
- Frame adoption in stream thumbnails and public pages — incremental convergence per touch-and-converge

## Migration strategy

- No mandatory big-bang rewrite
- Any touched/new rendering code must converge toward Frame + Renderable
- Touch-and-converge: when modifying rendering code, align it with the unified model

## Appearance model

```ts
BlockAppearance {
  aspectRatio: number | 'auto';
  columnRatios: number[];
  verticalAlign: 'top' | 'center' | 'bottom';
  gap: number;
  slots: Record<ItemPosition, SlotAppearance>;
  blockCaption?: CaptionStyle;
}
```

Appearance is data-driven and user-editable (via Block Customizer).

## Source

- ADR-005: Unified Rendering Model (Frame + Renderable)
- `rules/ADR-005-unified-rendering-frame-renderable.md`

## Alternatives considered

- Screen-specific rendering (continues drift)
- Theme-only styling without per-object appearance (insufficient flexibility)
