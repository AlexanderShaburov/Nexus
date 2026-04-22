---
type: session
scope: [editor, navigation]
status: in-progress
date: 2026-04-17
source_of_truth: false
tags: [homepage, home-editor, alignment, resume]
---

# Session checkpoint — Homepage Editor alignment

## Where we are

**Alignment phase.** Plan is locked. Codebase survey is done. **No code written yet.**
Waiting on 8 answers from the user before starting Phase 0.

Session was paused because the user needed to restart their computer.

## Plan location

- Canonical (authoritative): `Docs/plans/2026-04-17-homepage-editor-FINAL.md`
- Original user-provided file at project root: `homepage_editor_plan.md`
- Superseded predecessor: `Docs/plans/2026-04-17-nome-page-editor-implementation.md`

## 8 open questions — must be answered before Phase 0 starts

1. **Phase 1 path.** Extend `StreamEditorSession` with `selectAndReturn(streamId)` (recommended — mirrors the EventPage pattern), or keep the inline-picker fallback option open?
2. **`streamSlug` vs `streamId`.** Pure field rename on HomeDoc, or is there a separate stream-id concept? Today the stream entity's identity IS the slug (`/api/public/streams/by-ids?ids=<slug>`).
3. **v1 size editing.** In or out? `HomeItem.size?: 'S'|'M'|'L'` exists; plan §7 omits a size control; previous plan had one.
4. **Save / Discard / Preview / Exit.** Confirm all four are in v1 (assumed; §7 is silent).
5. **§10 eventRef loading UX.** Show a skeleton placeholder per eventRef until `loadEventPagesOnce()` settles — correct reading?
6. **ESLint anti-regression rule.** `no-restricted-imports` / `no-restricted-syntax` in the existing flat config, scoped to homeEditor + HomeEventTile + useHomeFeed — acceptable?
7. **Plan placement.** Canonical plan now lives at `Docs/plans/2026-04-17-homepage-editor-FINAL.md`. OK?
8. **`useEventPageByEventId`** (legacy `eventId` resolver). Leave untouched; kill in Phase 6 when `HomeBlockTile` dies. OK?

## Codebase facts (verified 2026-04-17)

### HomeDoc state (today)

- Frontend: `apps/frontend/src/entities/homeDoc/homeDoc.types.ts`
  - `HomeItem` = `HomeStreamRef (streamSlug, size?, thumbOverrideUrl?)` | `HomeBlockRef (blockId, size?)`.
  - **No `eventRef` variant, no `streamId` field.**
- Backend: `apps/admin-backend/app/models/home_doc.py` — mirrors frontend; accepts only `streamSlug` and `blockRef`.
- `vault/json/public/home.json`: two `streamRef` items; no real `blockRef` present.

### Journey system

- `apps/frontend/src/shared/nav/journey.types.ts`
- `ReturnCommand` includes an orphaned `homeInsertBlock { kind }` (defined, never dispatched).
- **Missing** return commands: `homeInsertStream`, `homeInsertEvent`.
- `EditorKind` already includes `'home'`. `/admin/home` route is free.

### Stream editor — Phase 1 gate

- `apps/frontend/src/features/admin/streams/streamEditorSession/StreamEditorSession.context.tsx`
- Has `{ kind: 'select' }` screen mode and `{ editor:'stream', mode:'select' }` is a valid `ToAddress`.
- **Gap:** no `selectAndReturn(streamId)`. Only returns loot via `finalizeAfterSave → returnHome('stream', { ok:true, id })` in edit mode after save (~lines 620–627).
- **Recommended fix:** add `selectAndReturn` mirroring EventPage.

### Event page editor — ready

- `features/admin/eventPageEditor/session/EventPageEditorSession.context.tsx:409-415` — working `selectAndReturn(eventId)`.
- Click wire: `features/admin/eventPageEditor/ui/EventPageEditor.tsx:126`.
- Route `/admin/event-pages` mounted with its session provider.

### Phase 0 deletion targets

- File to delete: `apps/frontend/src/features/admin/shared/featureEventOnHome.ts`.
- Call sites to remove (button + call):
  - `apps/frontend/src/features/admin/eventPageEditor/ui/EventPageEditor.tsx:208`
  - `apps/frontend/src/features/admin/eventEditor/ui/EventEditor.tsx:154`

### Public feed & event resolver

- `apps/frontend/src/features/public/hooks/useHomeFeed.ts` — does NOT call `loadEventPagesOnce()`; does not resolve eventRef. Phase 2 adds both.
- `apps/frontend/src/features/public/api/eventPagesModule.ts` — exposes `loadEventPagesOnce`, `getEventPageByEventId`, `invalidateEventPagesCache`. Plan: add `getEventPageById(eventPageId)` (direct by page id).
- `apps/frontend/src/features/public/hooks/useEventPageByEventId.ts` — resolves by legacy `eventId`; used only by `HomeBlockTile`'s EventCtaTile. Leave untouched; kill in Phase 6.
- `HomeBlockTile` is the legacy public tile; no `HomeEventTile` / `HomeStreamTile` component exists.

### Admin route table (relevant)

- `/admin/home` — NOT mounted (free).
- `/admin/public-stream` — legacy `PublicStreamPage`, mounted.
- `/admin/event-pages` — mounted with `EventPageEditorSessionProvider`.
- `/admin/streams` — mounted with `StreamEditorSessionProvider`.

## Proposed phase approach (pending alignment)

- **Phase 0 — Reset.** Delete `featureEventOnHome.ts` + 2 call sites + buttons.
- **Phase 1 — Stream select gate.** Add `selectAndReturn(streamId)` to `StreamEditorSession`; wire select-mode click path; verify with throwaway dispatch.
- **Phase 2 — Data model + infra.** Extend `HomeItem` with `HomeEventRef`; rename `streamSlug → streamId` (read-tolerant). Update Pydantic. Add `homeInsertStream`/`homeInsertEvent` return commands; `@deprecated` on `homeInsertBlock`. Add `getEventPageById` to `eventPagesModule`. Update `useHomeFeed` to call `loadEventPagesOnce()` at mount and resolve eventRef. Ship `HomeEventTile`.
- **Phase 3 — Editor shell.** `features/admin/homeEditor/**` + `/admin/home` route. Session surface: `homeDoc, isLoading, isSaving, isDirty, isJourney, addStreamViaJourney, addEventViaJourney, openStreamItem, openEventItem, removeItem, reorderItems, save, discard, preview, exit` (+ `setItemSize` iff v1-in). Read-only → mutate → Journey add.
- **Phase 4 — Migration UI.** `LegacyBlockTileAdmin` (Convert/Remove per §5), `OrphanTileAdmin`, banner on dirty with orphans, manual validation pass.
- **Phase 5 — Route switch.** Admin nav rename; `/admin/public-stream → /admin/home` redirect; `publicStream/**` unmounted on disk.
- **Phase 6 — Cleanup (after stable cycle).** Delete `publicStream/**`, `HomeBlockTile`, `useEventPageByEventId` (iff no users), `homeInsertBlock`, `HomeBlockRef`. Tighten Pydantic. Knowledge writeback into `architecture--data--domain-model`, `architecture--navigation--journey-system`, new `spec--editor--homepage-editor-behavior`.

## Anti-regression rule (Phase 2 addition)

Scope ESLint restriction to:
- `src/features/admin/homeEditor/**`
- `src/features/public/ui/HomeEventTile/**`
- `src/features/public/hooks/useHomeFeed*`

Forbid imports referencing: `EventData`, `useEvent`, `events/catalog.json`, `/api/public/events`.

## Git state at save time

- Branch: `release-mvp`.
- Uncommitted edits (pre-existing, not from this session): `BlockEditorScreen`, `BlockEditorSession.context`, `EventEditor`, `EventPageEditor`, `HomeBlockTile`, `journeySession.store`, vault JSON files, `package.json`+lock, knowledge index.
- Untracked: `.claude/hooks/`, `.superpowers/`, `featureEventOnHome.ts`, `eventPagesModule.ts`, `useEventPageByEventId.ts`, several new `knowledge/` subtrees, new vault JSONs, new stream JSONs, two knowledge-sync-classification spec versions, two knowledge-driven-orchestration spec versions.
- No commits made in this session.

## Resume protocol

1. Re-read `Docs/plans/2026-04-17-homepage-editor-FINAL.md`.
2. Re-read this session doc.
3. Ask the user the 8 open questions verbatim.
4. Do NOT start coding until answered.
5. After answers, proceed Phase 0 → Phase 6, reporting at each gate.
