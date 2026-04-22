---
type: spec
scope: [editor]
status: active
date: 2026-04-10
source_of_truth: false
tags: [event, behavior]
---

# Event system behavior

## Event Editor flows

### Journey inbound (select mode)

- Inbound ticket with `mode: 'select'` → show event list
- Clicking an event calls `selectAndReturn(eventId)` → `returnHome('events', { ok: true, id })`
- Cancel → `returnHome('events', { ok: false })`

### Create flow

- `createNew()` → empty `EventDraft` with status 'draft' → mode 'create'
- Title changes auto-generate slug
- Save → POST `/admin/events` → refresh → return to list (or returnHome if journey)

### Edit flow

- `selectEvent(id)` → convert `EventData` to `EventDraft` → set snapshot → mode 'edit'
- Save → PUT `/admin/events/{id}` → refresh

## Event Page Editor flows

### Media picker integration

Uses module-level `_pendingMediaField` to survive component unmount during picker journey:

1. `pickMedia(targetField)` → save `_pendingMediaField`, persist draft, dispatch to media editor
2. Media editor returns with loot
3. Bootstrap restores draft, applies `draft[targetField] = loot.id`
4. Draft cleanup is intentionally skipped when `_pendingMediaField` is set

### Factory creation

`createEventPage(preset)` produces new `EventPageData` with preset defaults.
Mode stack transitions: `['select', 'create']` → `['select', 'edit']` (create replaced by edit).

### Preview

Push 'preview' onto mode stack from edit. Pop returns to edit. Preview renders current draft (including unsaved changes).

## Related

- [Event system structure](../architecture/architecture--editor--event-system.md)
