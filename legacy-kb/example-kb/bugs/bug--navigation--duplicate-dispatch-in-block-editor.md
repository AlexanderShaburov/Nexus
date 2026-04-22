---
type: bug
scope: [navigation, editor]
status: fixed
date: 2026-04-12
source_of_truth: false
tags: [journey, block-editor, nested-journey]
---

# Duplicate dispatch in Block Editor caused stuck nested journey

## Symptom

Stream → Block (create) → pick art item → return to Block Editor → Apply/Save → editor stays on Block Editor instead of returning to Stream. Journey remains active, toolbar frozen.

## Root cause

When user clicks an art slot in the Block Editor, `handleEditHit` dispatches a Journey ticket to the Catalog via `dispatch(ticket, home)`. The click event propagated through the React component tree and triggered `handleEditHit` a second time before navigation completed. This pushed TWO Block→Catalog legs instead of one.

Session state: `[Stream→Block, Block→Catalog, Block→Catalog]` (3 legs instead of 2).

After Catalog return, `arrival` popped only one Block→Catalog leg. The second remained. When Apply/Save called `completeReturn`, it operated on the remaining Block→Catalog leg (returnTo: block) instead of the Stream→Block leg (returnTo: stream). `continueJourney` navigated to `block` (self) instead of `stream`.

## Fix

Added `dispatchPendingRef` (useRef) in `handleEditHit`. Set to `true` before `dispatch()`. Subsequent calls to `handleEditHit` are blocked. Ref resets on component remount (fresh instance after navigation).

## Additional fixes applied during investigation

- Removed defensive `journeySessionStore.clear()` in bootstrap return handler (was destroying parent journey leg)
- Imperative journey checks in `finalizeAfterSave`, `exit`, `onApply` (reads from store directly, not React closure)
- Early return after `returnHome` in `finalizeAfterSave` (prevents resetSession flash)

## Location

- Guard: `BlockEditorSession.context.tsx` — `dispatchPendingRef` + `handleEditHit`
- Other fixes: same file — `finalizeAfterSave`, `exit`, `onApply`, bootstrap return handler

## Lesson

Journey dispatch calls MUST be idempotent or guarded. Click events in deeply nested React component trees can fire handlers multiple times before navigation completes. Always guard `dispatch()` with a ref-based pending flag.
