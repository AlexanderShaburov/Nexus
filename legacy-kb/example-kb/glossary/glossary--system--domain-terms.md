---
type: glossary
scope: [system]
status: active
date: 2026-04-10
source_of_truth: false
tags: [domain, terminology]
---

# Domain terms glossary

## Entities

| Term | Definition |
|------|-----------|
| **ArtItem** | A single artwork in the catalog. Includes media references, metadata (title, technique, dimensions, price, availability). The atomic unit of art content. |
| **Block** | Universal content container. Discriminated union: gallery (art layouts), text, cta, eventCta, composable. The atomic composition unit. |
| **Stream** | Narrative composition of blocks. An ordered list of block references forming a "story" or page. |
| **Event** | Offline workshop/event entity. Has its own lifecycle (draft → scheduled → closed) and can be embedded into blocks. |
| **HomeDoc** | Singleton. The curated "portrait of the site" composed of HomeItems referencing streams and blocks. |

## Non-entities

| Term | Definition |
|------|-----------|
| **Hopper** | Pipeline/staging area for media ingestion. Uploaded files land here before becoming ArtItems or MediaItems. NOT a domain entity. |
| **HomeItem** | Data structure inside HomeDoc. References a Stream thumbnail or Block preview. NOT an independent entity. |
| **MediaItem** | Reusable media asset (image/video) referenced by ID (MediaRef) from event pages, text visuals, and composable blocks. Utility entity. |
| **TextVisual** | Composable text content unit. Utility entity. |
| **EventPage** | Page rendering model for Events. Uses presets (workshop, pleinAir, exhibition, minimal) to define section composition. |

## Mechanisms

| Term | Definition |
|------|-----------|
| **Journey** | The only allowed protocol for cross-editor navigation with return semantics. Uses tickets stored in an external store. |
| **JourneyTicket** | A data object representing one journey. Contains destination, returnTo, returnEffect, and optional loot. Grows with legs/segments. |
| **Transporter** | React hooks layer for Journey integration (useDispatch, useReturnHome, useArrival). |
| **EditorKey** | Composite key `{ kind, id }` identifying an editor session in EditSessionsDataStore. |
| **ReturnCommand** | The action to execute when a Journey leg returns (e.g., `blockInsertArt`, `streamInsertBlock`). |
| **Loot / JumpResult** | The return value from a Journey: `{ ok: true, id }` or `{ ok: false, reason }`. |

## Architecture terms

| Term | Definition |
|------|-----------|
| **Control plane** | Editor Context/Provider. Owns CRUD orchestration, user action handling, Journey integration, guards, bootstrap. |
| **Data plane** | External stores. Hold persistent/cross-screen state (catalogs, sessions, Journey tickets). |
| **View plane** | UI components. Render-only, receive data via props, delegate actions to context. |
| **Frame** | Unified container component with consistent sizing/padding behavior. Modes: embedded, card, thumbnail. |
| **Renderable** | Discriminated union type (`entities/renderable/`) describing content that can fill a composable block slot. Kinds: art, cta, media, textVisual. |
| **Draft** | Current in-memory edits in an editor session. Stored in EditSessionsDataStore. |
| **Snapshot** | Last persisted state in an editor session. Draft is compared against snapshot to derive isDirty. |
| **EditorWorkspaceProvider** | Alias for AdminDataPreloader. NOT a context provider — a side-effect wrapper that preloads 4 domain stores on admin mount. |

## Content types

| Term | Definition |
|------|-----------|
| **GalleryLayout** | Layout variant for gallery/composable blocks: single, pairHorizontal, pairVertical, triptychLeft, triptychRight, triptychHorizontal. |
| **BlockAppearance** | Data-driven styling for gallery blocks: aspectRatio, gap, columnRatios, per-slot image pan/zoom, caption positioning. |
| **Localized** | `Partial<Record<'en'\|'ru'\|'it'\|'es'\|'pt', string>>`. All user-facing text uses this type. |
| **EntityLifecycle** | State progression: template → draft → saved → published. Not all entities use all states. |
| **Money** | `{ amount: number; currency: CurrencyName }`. Used for art pricing and event fees. |
| **EventPreset** | Event page layout preset: workshop, pleinAir, exhibition, minimal. Determines section composition. |
| **MediaRef** | `string` — a MediaItem ID used as a reference. Resolved at render time. |

## UI terms

| Term | Definition |
|------|-----------|
| **Select Mode** | Editor mode showing a grid of entity thumbnails for browsing and selection. |
| **Edit Mode** | Editor mode focused on a single entity for editing. |
| **Customize Mode** | Block editor sub-mode for appearance editing (gallery blocks only). |
| **SingleEditorToolbar** | Standard primary action surface in editors (Save, Apply, Exit, etc.). |
| **Three-Dot Menu** | Standard secondary action surface on list/grid items (Edit, Duplicate, Delete). |
| **Mode stack** | Array tracking current editor depth (e.g., `['select', 'edit', 'customize']`). Escape pops the stack. |
