---
type: architecture
scope: [renderer]
status: active
date: 2026-04-10
source_of_truth: true
tags: [rendering, ui]
---

# Rendering system component hierarchy

## Core components (shared/ui/)

| Component | Purpose | Key props |
|-----------|---------|-----------|
| **GalleryBlockView** | Gallery block grid renderer | `block, resolveArt, onSlotClick?, renderEventSlot?, renderEmptySlot?, renderArtContent?, children?` |
| **ComposableBlockView** | Composable block slot renderer | `block, resolver, onSlotClick?, renderEmptySlot?, renderSlotOverlay?` |
| **RenderableView** | Polymorphic slot content renderer | `renderable, resolver, onClick?, imgStyle?` |
| **ArtPicture** | `<picture>` with AVIF → WebP → JPEG cascade | `sources, alt?, onClick?, loading?` |
| **Frame** | Aspect-ratio container | `mode ('embedded'\|'card'\|'thumbnail'), aspectRatio?, children` |
| **QuickView** | Floating metadata card (portal) | `art, anchorPoint, onClose, onViewFull` |
| **Lightbox** | Full-screen image viewer (portal) | `src, alt?, onClose` |
| **BlockThumbnail** | Scaled gallery preview (ResizeObserver) | wraps GalleryBlockView |

## RenderableView dispatch (by kind)

| Kind | Sub-component |
|------|--------------|
| `'art'` | ArtRenderableView (uses ArtPicture) |
| `'media'` | MediaRenderableView (video or image) |
| `'textVisual'` | TextVisualRenderableView (background + text box + overlay) |
| `'cta'` | CtaRenderableView (title + body + button) |

## Resolver interface

```ts
type RenderableResolver = {
  resolveArt: (artId: string) => ArtItemData | undefined;
  resolveMedia: (mediaId: string) => MediaItemData | undefined;
  resolveTextVisual: (id: string) => TextVisualData | undefined;
};
```

## Appearance style functions

Location: `shared/lib/appearance/applyAppearanceStyles.ts`

| Function | Output |
|----------|--------|
| `blockGridStyle()` | grid-template-columns, gap, align-items, aspect-ratio |
| `slotWrapperStyle()` | translateY (frame offset) |
| `slotImageStyle()` | scale + translate (pan/zoom) |

## Block dispatch per context

| Context | Entry component | Dispatches to |
|---------|----------------|---------------|
| **Public** | `features/public/ui/GalleryBlock` | ImageComponent, TextComponent, EventCtaView, ComposableBlockPublic |
| **Admin** | `features/admin/blocks/ui/SingleBlockEditor` | GalleryComponent, TextBlockComponent, CtaBlockComponent, EventCtaBlockComponent, ComposableBlockComponent |

## Gallery layout CSS

Location: `shared/galleryLayouts/galleryLayouts.css`

Mobile breakpoint (≤820px): all layouts collapse to single column.

## Related

- [Rendering behavior](../specs/spec--renderer--rendering-behavior.md)
