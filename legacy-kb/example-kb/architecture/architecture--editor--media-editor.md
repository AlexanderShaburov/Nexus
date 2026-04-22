---
type: architecture
scope: [editor]
status: active
date: 2026-04-10
source_of_truth: true
tags: [media, editor]
---

# Media editor structure

## Screen modes

```ts
type ScreenMode = 'select' | 'edit' | 'create' | 'pick';
```

## Session interface

```ts
interface MediaEditorSession {
  mediaItems: MediaItemData[];
  filteredItems: MediaItemData[];
  allTags: string[];
  filter: MediaFilterState;
  updateFilter: (patch: Partial<MediaFilterState>) => void;
  screenMode: ScreenMode;
  draft: MediaItemData | undefined;
  isDirty: boolean;
  isValid: boolean;
  isLoading: boolean;
  isSaving: boolean;
  isJourney: boolean;
  deletionBlock: DeletionBlock | undefined;
  setDraftField: <K>(field: K, value: MediaItemData[K]) => void;
  save: () => Promise<void>;
  deleteItem: () => Promise<void>;
  dismissDeletionBlock: () => void;
  selectItem: (id: string) => void;
  onAdd: () => void;
  cancelPick: () => void;
  back: () => void;
}
```

## Filter model

```ts
interface MediaFilterState {
  kind?: MediaItemKind;
  lifecycle?: EntityLifecycle;
  tag?: string;
  search?: string;
}
```

AND semantics. Pure function.

## Dependency scanning targets

Scans two stores for MediaRef usage before deletion:
- `blocksCollectionStore`: composable block slots with `content.kind === 'media'`
- `eventPagesStore`: heroImage, experienceImages, resultsImages, featuredWorks[].image

## Component tree

```
MediaEditorSessionProvider
  └── MediaEditor (mode switch)
      ├── MediaPickMode (pick)
      ├── MediaSelectMode (select)
      └── MediaEditForm (edit/create)
```

## File structure

```
mediaEditor/
├── mediaEditorSession/MediaEditorSession.context.tsx
├── api/mediaItemsAdminApi.ts
├── logic/
│   ├── filterMediaItems.ts
│   ├── findMediaDependencies.ts
│   ├── hopperIntegration.ts
│   ├── newMediaItemFromHopperLoot.ts
│   ├── useMediaPicker.ts
│   └── __tests__/ (7 test files)
└── ui/ (MediaEditor, MediaSelectGrid, MediaFilterBar, MediaEditForm)
```

## Related

- [Media editor behavior](../specs/spec--editor--media-editor-behavior.md)
