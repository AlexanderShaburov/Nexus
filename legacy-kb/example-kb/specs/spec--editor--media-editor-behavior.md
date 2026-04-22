---
type: spec
scope: [editor]
status: active
date: 2026-04-10
source_of_truth: false
tags: [media, behavior]
---

# Media editor behavior

## Picker mode (return-on-click)

Callers dispatch `buildMediaPickerTicket(callerEditor, callerObjectId)`. On arrival, bootstrap detects `destination.mode === 'select'` with no loot → enters PICK mode. Clicking an item immediately calls `returnHome('mediaItems', { ok: true, id, output })`. No form edit in picker.

## Upload-during-pick (nested journey)

From PICK mode, user clicks "Upload New" → dispatches to Hopper. On return, `processHopperReturn()` converts loot to `MediaItemData` draft → enters CREATE mode. After save, returns persisted ID (not temp) to original caller.

## Deletion behavior

If dependencies found → hard-block with dialog showing referenced entities. User must remove references in other editors first. No override available.

If no dependencies → `confirm()` dialog → DELETE API call → refresh store → return to select.

## Mode transitions

| From | Action | To |
|------|--------|----|
| select | click item | edit |
| select | Upload New | → Hopper (journey) |
| pick | click item | return loot immediately |
| pick | Upload New | → Hopper (journey) |
| pick | Cancel | return { ok: false } |
| create | save | pick (if journey) or select |
| edit | save | pick (if journey) or select |
| edit | back | pick (if journey) or select |

## Dirty / Valid checks

- `isDirty`: `JSON.stringify(draft) !== JSON.stringify(snapshot)`
- `isValid`: image source must exist (`media.sources.full` for images, `media.sources.url` for video)
- Save disabled if: `(!isDirty && !isCreate) || !isValid || isSaving`

## Related

- [Media editor structure](../architecture/architecture--editor--media-editor.md)
