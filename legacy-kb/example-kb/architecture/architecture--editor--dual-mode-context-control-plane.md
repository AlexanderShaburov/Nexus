---
type: architecture
scope: [editor]
status: active
date: 2026-04-10
source_of_truth: true
tags: [constitution, adr-002, adr-004]
---

# Editor architecture: dual mode + context as control plane

## Dual mode pattern

All editors (except Hopper) implement two modes:

1. **Select Mode** — grid of entity thumbnails (plus templates where applicable)
2. **Single Item Edit Mode** — focused editor for one item + metadata

Block editor adds a third mode: **Customize** (appearance editor, gallery blocks only).

Mode is managed as a **stack** (e.g., `['select', 'edit', 'customize']`). Escape pops the stack.

## Context = Control Plane

Each editor provides a Context/Provider (SessionProvider) that acts as the control plane.

| Responsibility | What it does |
|---------------|-------------|
| CRUD orchestration | load, save, create, update, delete sequencing |
| User action handling | onClick, onHit, menu action responses |
| Journey integration | ticket creation, return handling, bootstrap |
| Guards | unsaved changes confirmation, destructive action warnings |
| Bootstrap logic | initial state resolution from stores and Journey tickets |
| Mode management | screen mode stack transitions |
| Validation | isValid, isDirty, canSave computation |

## UI = Render Plane

Components receive data and handlers via props/hooks. They contain no domain logic.

## Actual editor implementations

Editors vary in complexity. The structure is NOT uniform across all editors.

| Editor | Session dir | Has bootstrap/ | Has guards/ | Has travel | Structure |
|--------|------------|----------------|-------------|------------|-----------|
| **blocks** | `blockEditorSession/` | Yes | No | Yes (.travel.ts) | Full (api, hooks, ui, utils) |
| **streams** | `streamEditorSession/` | Yes | Yes | No | Full (api, hooks, ui, utils) |
| **catalogEditor** | `catalogEditorSession/` | No | No | No (has journeyService.ts) | Standard (api, hooks, ui, utils) |
| **eventEditor** | `eventEditorSession/` | No | No | No | Minimal (api, ui) |
| **eventPageEditor** | `session/` | No | No | No | Standard (api, ui, __tests__) |
| **mediaEditor** | `mediaEditorSession/` | No | No | No | Standard (api, logic, ui) |
| **textVisualEditor** | `textVisualEditorSession/` | No | No | No | Minimal (api, ui) |
| **publicStream** | `publicStreamSession/` | No | No | No | Minimal (api, ui) |

**Only blocks and streams have bootstrap directories.** Other editors handle initialization inline in their context providers.

## EditorWorkspaceProvider

`EditorWorkspaceProvider` (aliased from `AdminDataPreloader`) is NOT a context provider. It is a side-effect wrapper that preloads 4 domain stores on mount:
- `refreshCatalog()` → catalogStore
- `refreshBlocksCollection()` → blocksCollectionStore
- `refreshStreamsIndex()` → streamsIndexStore
- `refreshMediaItems()` → mediaItemsStore

It does not provide any context value — it just ensures stores are populated before editors render.

## Related

- [No business logic in UI](../invariants/invariant--architecture--no-business-logic-in-ui.md)
- [Bootstrap reads stores imperatively](../invariants/invariant--state--bootstrap-reads-stores-imperatively.md)
- [Standard command surfaces](../invariants/invariant--ui--standard-command-surfaces-only.md)
- [Draft/snapshot pattern](../patterns/pattern--state--draft-snapshot.md)
