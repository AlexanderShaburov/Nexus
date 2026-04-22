---
type: architecture
scope: [editor]
status: active
date: 2026-04-10
source_of_truth: true
tags: [event, editor]
---

# Event system structure (Event + EventPage editors)

Two parallel, independent editors sharing `EditorKind = 'events'` but managing different entity types.

## Event Editor

Manages `EventData` — simple event records.

### Screen modes (simple state, no stack)

```ts
type ScreenMode = 'list' | 'edit' | 'create' | 'select';
```

### Draft model

Uses a **form draft** (`EventDraft`) separate from `EventData`:
- `eventToFormDraft(EventData) → EventDraft` (for editing)
- `formDraftToPayload(EventDraft) → CreateEventPayload` (for API)

```ts
interface EventDraft {
  id?: string;
  slug: string;
  titleEn: string;
  description: string;
  dateTime: string;
  durationMinutes: string;
  location: string;
  mapUrl: string;
  priceAmount: string;
  priceCurrency: string;
  status: EventStatus;
  streamSlug: string;
}
```

No dirty tracking. No outbound journeys (leaf editor).

## Event Page Editor

Manages `EventPageData` — preset-based page models (workshop, pleinAir, exhibition, minimal).

### Screen modes (stack-based)

```ts
modeStack: ScreenMode[] = ['select'];
type ScreenMode = 'select' | 'create' | 'edit' | 'preview';
```

### Draft model

Full `EventPageData` stored as-is. Field updates via `setDraftField(field: string, value: unknown)`.

Dirty tracking: `isDirty = JSON.stringify(draft) !== JSON.stringify(snapshot)`

### Field visibility

Per-preset visibility map (`fieldVisibility.ts`) controls form sections. 5 sections: content, logistics, cta, media, settings.

## Structural differences

| Aspect | Event Editor | Event Page Editor |
|--------|-------------|-------------------|
| Entity type | `EventData` (flat, ~10 fields) | `EventPageData` (union, 40+ fields) |
| Draft model | Form reduction (`EventDraft`) | Full entity stored as-is |
| Mode system | Simple state (no nesting) | Stack (supports edit ↔ preview) |
| Dirty tracking | None | JSON diff |
| Outbound journey | No (leaf editor) | Yes (media picker) |
| Creation | Form-based | Factory-based (preset) |

## File structure

```
eventEditor/
├── eventEditorSession/EventEditorSession.context.tsx
├── api/eventsAdminApi.ts
└── ui/

eventPageEditor/
├── session/EventPageEditorSession.context.tsx
├── api/eventPagesAdminApi.ts
├── ui/
└── __tests__/
```

## Related

- [Event system behavior](../specs/spec--editor--event-system-behavior.md)
