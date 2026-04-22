---
type: invariant
scope: [state, editor]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, adr-003]
---

# No global data in React contexts — use external stores

## Rule

React Context is the **control plane** (orchestration, handlers, guards).
External stores are the **data plane** (persistent/cross-screen state).

- Contexts decide **what to do**
- Stores hold **what we know**
- A piece of state must have a **single source of truth** (no double-ownership)
- Context may keep derived/local UI state, but must NOT own global truth

## What belongs in external stores

- Journey stack/tickets
- Cross-editor session state (draft/snapshot per EditorKey)
- Global collections/lists (streams list, catalog list, blocks collection)
- Global UI settings (theme) where appropriate

## What belongs in contexts

- CRUD orchestration logic
- User action handlers
- Journey integration and guards
- Bootstrap logic
- Mode management (screen mode stack)

## Where it applies

- All editor contexts (Block, Stream, Catalog, Event, Media)
- All shared state that survives route changes or editor mount/unmount

## Source

- Constitution §5: "All shared/stateful data MUST live in external stores"
- ADR-003: External Stores as the Data Plane
- `rules/CONSTITUTION.md`, `rules/ADR-003-external-stores-data-plane.md`

## Consequence of violation

- "God-context" anti-pattern (context grows into a global database)
- State lost on unmount/remount
- Fragile mount/unmount flows
- Coupling to React lifecycle
