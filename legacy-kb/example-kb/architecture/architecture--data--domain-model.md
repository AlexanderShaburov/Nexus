---
type: architecture
scope: [data, architecture]
status: active
date: 2026-04-10
source_of_truth: true
tags: [constitution, domain-model]
---

# Domain model

## Entity relationships

```
                       ┌─────────────┐
                       │  HomeDoc     │
                       │  (singleton) │
                       └──────┬───────┘
                              │ references (by slug/id)
                ┌─────────────┴──────────────┐
                ▼                             ▼
         ┌────────────┐                ┌───────────┐
         │  Stream    │                │  Block     │
         │  (ordered  │──references───▶│  (gallery/ │
         │   blockIds)│  (by ID)       │   text/cta)│
         └────────────┘                └─────┬──────┘
                                             │ references (by ID)
                                ┌────────────┴────────────┐
                                ▼                         ▼
                         ┌───────────┐            ┌───────────┐
                         │  ArtItem  │            │  Event    │
                         │  (artwork)│            │ (workshop)│
                         └───────────┘            └───────────┘
```

All relationships are by-ID references, not containment. Stream stores `blockIds[]` (string array). Block stores `artId`, `eventId` (string fields).

## Domain entities (per Constitution)

| Entity | ID format | Lifecycle states | Storage |
|--------|----------|-----------------|---------|
| ArtItem | `art-YYYYMMDD-{base32(6)}` | template, draft, saved, published | `art_catalog.json` |
| Block | `block-{kind}-{layout?}-{uuid8}` | template, draft, saved | `block_collection.json` |
| Stream | `stream-YYYYMMDD-{base32(6)}` | draft, ready, archived | `streams/index.json` + individual files |
| Event | `event-YYYYMMDD-{base32(6)}` | draft, scheduled, closed | `events/catalog.json` |
| HomeDoc | (singleton) | N/A | `public/home.json` |

## Block type system (discriminated union on `blockKind`)

| Kind | Content | Key fields |
|------|---------|------------|
| `gallery` | Art image layouts | `layout`, `items[]` (GalleryBlockItem), `appearance?` |
| `text` | Localized title + body | `title`, `body`, `variant` (full/narrow/quote) |
| `cta` | Call-to-action | `title`, `body`, `buttonLabel`, `target` (CtaTarget) |
| `eventCta` | Single-event promo | `eventId`, `buttonLabel` |
| `composable` | Mixed-content slots | `layout`, `slots[]` (BlockSlot with Renderable), `appearance?` |

Gallery layouts: `single`, `pairHorizontal`, `pairVertical`, `triptychLeft`, `triptychRight`, `triptychHorizontal`.

## Entity modules in code

12 directories under `entities/`:

| Module | Primary exports | Notes |
|--------|----------------|-------|
| `art/` | `ArtItem` (class), `ArtItemData` | Class with `fromJSON()`/`toJSON()` |
| `block/` | `Block` (discriminated union), `BlockAppearance`, `LAYOUT_SCHEME` | Most complex entity |
| `catalog/` | `ArtCatalog` | Wrapper around ArtItemData records |
| `common/` | `Localized`, `Money`, `Dimensions`, `EntityLifecycle`, `ISODate` | Shared value types |
| `event/` | `EventData`, `EventPageData`, `EventPreset` | Includes event page presets |
| `homeDoc/` | `HomeDoc`, `HomeItem`, `HomeStreamRef`, `HomeBlockRef` | Singleton page model |
| `hopper/` | `HopperItem` | Minimal, no index.ts barrel |
| `mediaItem/` | `MediaItemData`, `MediaSources`, `MediaItemCatalog` | Utility entity |
| `publicStream/` | `PublicStream` (class), `PublicStreamData` | Class with `fromJSON()` |
| `renderable/` | `Renderable` (discriminated union), `RenderableResolver` | Content type system |
| `stream/` | `StreamData`, `StreamIndexItem`, `StreamsIndex` | Pure types |
| `textVisual/` | `TextVisualData`, `TextVisualCatalog` | Composable text content |

## Content reference types

- `artId: string` → ArtItem in catalog
- `eventId: string` → Event entity
- `MediaRef = string` → MediaItem ID
- `blockIds: string[]` → Block IDs in a Stream

## Related

- [Entities are finite and controlled](../invariants/invariant--architecture--entities-are-finite-and-controlled.md)
- [Overall structure](architecture--system--overall-structure.md)
