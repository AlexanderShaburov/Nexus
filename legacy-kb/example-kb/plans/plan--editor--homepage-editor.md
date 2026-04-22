---
type: plan
scope: [editor, navigation]
status: in-progress
date: 2026-04-17
source_of_truth: true
tags: [homepage, home-editor, event-page, journey, migration, locked-plan]
---

# Homepage Editor — Final Implementation Plan (Locked)

> Status (2026-04-17): Locked. Phase 0 complete. Phase 1 in progress.
> Session checkpoint: `knowledge/sessions/session--editor--homepage-editor-alignment.md`.
> Superseded: `Docs/plans/2026-04-17-nome-page-editor-implementation.md`.
> This file is the working reference going forward.

## Alignment decisions (2026-04-17)

- **Phase 1 path**: extend `StreamEditorSession` with `selectAndReturn(streamId)`. No inline picker.
- **`streamSlug` → `streamId`**: field transition. `streamId` canonical, `streamSlug` legacy alias. No dual-identity.
- **`size` handling**: legacy. Removed from new Homepage Editor model, writes, and rendering. Read-tolerance on backend only during transition.
- **Capabilities**: Add stream, Add event, Reorder, Remove, Open item, Save, Discard, **Preview (renders full public homepage, not editor chrome)**, Exit.
- **Event loading UX**: no per-tile skeletons. Page-level loading gate — block event-tile rendering until `loadEventPagesOnce()` resolves.
- **Anti-regression ESLint**: `no-restricted-imports` / `no-restricted-syntax` scoped to homeEditor + HomeEventTile + useHomeFeed.
- **`useEventPageByEventId`**: leave untouched; delete in Phase 6 with `HomeBlockTile`.

## 1. Overview

Replace the legacy **Public Stream editor** with a proper **Homepage Editor**.

Homepage becomes a **singleton editor surface** that composes:

- Stream tiles
- Event tiles (canonical: EventPage)

---

## 2. Core Architectural Rules (Locked)

### Canonical Event Model

- Canonical event = `EventPageData`
- Event ID = `EventPageData.id`
- Homepage references **EventPage only**

```ts
type HomeEventRef = {
  kind: 'eventRef'
  eventPageId: string
}
```

(Size is intentionally omitted per alignment decision.)

### Forbidden (Strict)

- No `EventData`
- No `useEvent()`
- No `/api/public/events`
- No `events/catalog.json`
- No `Feature on Home`
- No block-level homepage composition

---

## 3. Homepage Composition Model

```ts
type HomeItem =
  | HomeStreamRef
  | HomeEventRef
  | HomeBlockRef // legacy (read-only)
```

### Composition Units

- streamRef
- eventRef (EventPage only)
- blocks are NOT exposed in editor UI

---

## 4. Data Model Rules

### StreamRef Transition

- Backend accepts on read:
  - `streamId` (canonical)
  - `streamSlug` (legacy alias, normalized on read)
- Frontend writes:
  - `streamId` only

### `size` Transition

- Backend tolerates legacy `size` on read (ignored).
- New editor never writes `size`.
- Rendering ignores `size`.

### Rule

- read-tolerant
- write-canonical
- no migration script

---

## 5. Migration Rules (v1)

### eventRef Validation

Decision tree:

1. `{ eventPageId }` exists and resolves → valid
2. `{ eventPageId }` missing in catalog → orphan → Remove only
3. `{ eventId }` legacy:
   - single match → Convert
   - none/multiple → Remove only
4. invalid shape → Remove only

### blockRef Handling

- `eventCta`:
  - matching EventPage → Convert
  - otherwise → Remove
- other blocks → Remove only

---

## 6. Orphan Handling

### Definition

Item is orphan if reference does not resolve.

### Admin UI

- Render `OrphanTileAdmin`
- Show:
  - "Missing — <id>"
- Actions:
  - Remove only

### Save Behavior

- Save NOT blocked
- Banner warning shown

### Public

- Orphans silently skipped

---

## 7. Editor Behavior

### Editor Type

- Singleton
- Edit-only
- No select mode

### Capabilities

- Add stream
- Add event
- Reorder
- Remove
- Open item
- Save
- Discard
- **Preview** — renders the full public homepage as the visitor would see it (not the editor chrome)
- Exit

---

## 8. Journey Integration

### Add Stream

homeInsertStream → stream editor (select) → return { id }

### Add Event

homeInsertEvent → eventPage editor (select) → return { id }

### Open Item

- openStreamItem → stream editor
- openEventItem → eventPage editor

---

## 9. Return Behavior

- Editor re-mounts on return
- Scroll NOT preserved (accepted v1 limitation)
- Draft state preserved

---

## 10. EventPage Loading (Critical)

- `useHomeFeed` calls `loadEventPagesOnce()` at mount.
- Page-level loading gate: homepage does not render event tiles until the load resolves.
- No per-tile skeletons.
- On failure:
  - stream tiles render
  - event tiles skipped

---

## 11. Phase 1 Gate

Must verify:

- stream editor supports select + return via `selectAndReturn(streamId)` returning `{ ok: true, id }` loot.

No inline-picker fallback in scope.

---

## 12. Anti-Regression Invariant

No new code may reference:

- `EventData`
- `useEvent()`
- `events/catalog.json`
- `/api/public/events`

Enforced by:

- ESLint rule (`no-restricted-imports` / `no-restricted-syntax`) scoped to `homeEditor`, `HomeEventTile`, `useHomeFeed`
- PR checklist
- unit test

---

## 13. Rollout Plan

Phase 0 — reset ✅ complete
Phase 1 — stream select gate ← current
Phase 2 — data model
Phase 3 — editor shell
Phase 4 — migration UI
Phase 5 — route switch
Phase 6 — cleanup legacy

---

## 14. Final Product Behavior

Editor workflow:

1. Open Homepage Editor
2. Add stream/event via Journey
3. Reorder tiles
4. Drill into items
5. Return
6. Save

No shortcuts, no legacy paths.
