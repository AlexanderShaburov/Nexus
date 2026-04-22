---
type: session
scope: [editor, navigation]
status: active
date: 2026-04-17
source_of_truth: false
tags: [events, home-composer, bridge, journey]
---

# Event → Home integration bridge

Implementation session establishing the editorial bridge between Event/EventPage editors and the Home Composer, without introducing a new editor, a new HomeItem variant, or any architectural redesign.

## Goals

1. Homepage `EventCtaTile` deep-links to `/event/:eventPageId` when an EventPage references the tile's `eventId`; otherwise keeps inline enrollment.
2. Event editor and EventPage editor gain a **Feature on Home** action that adds the event to the homepage, reusing an existing `EventCtaBlock` when available.

## Architectural decisions

- **No new entity, no new HomeItem variant.** `HomeBlockRef { kind:'blockRef', blockId }` remains the sole way to attach a block to HomeDoc.
- **EventCtaBlock is the canonical homepage→event reference.** The bridge reuses any existing `EventCtaBlock` with matching `eventId` before creating a new one.
- **Feature-on-Home is a service action, not a Journey.** The user stays in the invoking editor; no cross-editor navigation happens. This does not violate `invariant--navigation--all-cross-editor-flows-use-journey.md` because that invariant governs navigational flows, not backend mutations.
- **Dedupe at two levels:** (1) block level — single `EventCtaBlock` per `eventId`; (2) HomeDoc level — single `HomeBlockRef` per `blockId`.
- **Deep-link resolution uses EventPage.eventId.** `EventPageData.eventId` is the field that links an EventPage to an Event; the homepage tile scans EventPages for `page.eventId === block.eventId`.

## Files changed

### New
- `apps/frontend/src/features/public/api/eventPagesModule.ts` — public singleton cache + `getEventPageByEventId(eventId)`.
- `apps/frontend/src/features/public/hooks/useEventPageByEventId.ts` — React hook that triggers `loadEventPagesOnce()` on mount and returns the matching EventPage.
- `apps/frontend/src/features/admin/shared/featureEventOnHome.ts` — service helper: find-or-create `EventCtaBlock`, dedupe & append `HomeBlockRef`, `PUT /api/admin/home`.

### Modified
- `apps/frontend/src/features/public/ui/HomeBlockTile/HomeBlockTile.tsx` — `EventCtaTile` wraps content in `<Link to="/event/:id">` when EventPage exists.
- `apps/frontend/src/features/public/ui/HomeBlockTile/HomeBlockTile.css` — styles for linked tile variant.
- `apps/frontend/src/features/admin/eventEditor/ui/EventEditor.tsx` — **Feature on Home** button in EventForm toolbar.
- `apps/frontend/src/features/admin/eventPageEditor/ui/EventPageEditor.tsx` — **Feature on Home** button in EditMode toolbar (disabled unless `draft.eventId` set and not dirty).

## Journey / invariants preserved

- Home Composer remains the canonical HomeDoc writer; the service helper mirrors its dedupe rule.
- No new EditorKind. No change to the ReturnCommand union.
- Feature-on-Home button is disabled while `isJourney === true` in both editors, so it cannot run mid-round-trip.
- EventPage editor additionally disables the button while `isDirty === true` to avoid featuring an event based on a draft that hasn't been persisted.

## Outcome semantics

`featureEventOnHome(eventId)` returns:
- `{ outcome: 'added', blockId, created: boolean }` — block (possibly new) now referenced on home.
- `{ outcome: 'already-featured', blockId }` — HomeDoc already has this blockId.
- `{ outcome: 'error', error }` — any step failed.

The caller surfaces these via `alert()`; no navigation.

## Verification

- `npm run type-check` — clean for new/modified files. The pre-existing `CatalogEditorPage.tsx:92` error is unchanged (unrelated; reproduced on baseline HEAD).
- `npm run lint` (eslint --max-warnings=0) — clean for all changed files.
- `npm run build` — blocked only by the same pre-existing error above.
- Runtime test: not performed in this session (no browser/dev server interaction available here). Manual proof checklist — see below.

## Manual proof checklist (for next session)

- [ ] Event Page exists → click homepage event tile → navigates to `/event/:pageId`.
- [ ] No Event Page for `block.eventId` → tile renders with inline enrollment (unchanged behavior).
- [ ] Event editor → Feature on Home (first time) → adds a new `EventCtaBlock` + appends `HomeBlockRef` → home.json shows new item.
- [ ] Event editor → Feature on Home (second time) → "Already featured on the homepage." alert; no duplicate.
- [ ] When an `EventCtaBlock` with the same `eventId` already exists → reused (not duplicated).
- [ ] EventPage editor → Feature on Home disabled when `eventId` missing; enabled after linking + save.
- [ ] Invoking Feature on Home does not corrupt the editor's draft/dirty state.
