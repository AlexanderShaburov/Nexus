---
type: pattern
scope: [state, editor]
status: active
date: 2026-04-10
source_of_truth: false
tags: [stores, editing]
---

# Draft/Snapshot pattern for editor sessions

## Problem

Editors need to track in-progress changes, detect dirty state, support discard, and commit changes on save. This must work across mount/unmount cycles.

## Solution

Every editor session maintains two copies of its data in `EditSessionsDataStore`:

```
┌──────────┐    edit     ┌──────────┐    save     ┌──────────┐
│ Snapshot  │───────────▶│  Draft   │────────────▶│  Server  │
│ (saved)   │◀───────────│ (editing)│◀────────────│  (JSON)  │
└──────────┘   discard   └──────────┘   refresh   └──────────┘
```

- **Snapshot** = last persisted state
- **Draft** = current in-memory edits
- **isDirty** = `deepEqual(draft, snapshot) === false`
- **commit()** = promote draft → snapshot (called after successful API save)

## Store API

`EditSessionsDataStore` (location: `shared/state/editorSessionsData.store.ts`):

```ts
get<T>(key: EditorKey | undefined): DraftSnapshot<T> | undefined
ensure<T>(key: EditorKey, initial: DraftSnapshot<T>): DraftSnapshot<T>
saveDraft<T>(key: EditorKey, draft: T): void
setSnapshot<T>(key: EditorKey, snapshot: T): void
commit<T>(key: EditorKey): void       // draft becomes new snapshot
clear(key: EditorKey): void
clearKind(kind: EditorKind): void
```

Data shape: `DraftSnapshot<T> = { snapshot: T; draft: T; updatedAt: string }`

## React hook

```ts
const { storeData, setDraft, setSnapshot, commit, clear } = useSessionDataStore<T>(key);
```

## Keying

Sessions are keyed by `EditorKey = { kind: EditorKind; id: string }`.

## Where it applies

- Block editor, Stream editor, Catalog editor, Event editor, Media editor, EventPage editor, TextVisual editor

## Related

- [State management](../architecture/architecture--state--custom-pubsub-stores.md)
- [No global data in contexts](../invariants/invariant--state--no-global-data-in-react-contexts.md)
