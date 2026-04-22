---
type: architecture
scope: [navigation, editor]
status: active
date: 2026-04-10
source_of_truth: true
tags: [constitution, adr-001, journey]
---

# Journey navigation system

## Ticket model

One Journey = one JourneyTicket, stored in JourneySessionStore (external, outside React).

Source: `shared/nav/journey.types.ts`

```ts
type JourneyTicket = {
  journeyId: string;
  destination: ToAddress;
  returnTo: ReturnAddress;
  phase: JourneyLeg;            // 'outbound' | 'return'
  nonce: string;
  createdAt: string;
  returnEffect: ReturnCommand | undefined;
  loot?: JumpResult;
};

type JumpResult =
  | { ok: true; id: string; output?: GridItem }
  | { ok: false; reason?: string };
```

## Return commands (11 variants)

Source: `shared/nav/journey.types.ts`

| Command | Key fields |
|---------|------------|
| `streamInsertBlock` | `streamId`, `insertAt`, `focus?` |
| `streamReplaceBlock` | `streamId`, `replaceBlockId`, `focus?` |
| `streamUpdateBlock` | `streamId`, `blockId`, `focus?` |
| `blockInsertArt` | `blockId`, `pendingSelection` |
| `blockUpdateArt` | `blockId`, `pendingSelection` |
| `blockSetEventId` | `blockId`, `position` |
| `blockSetEventBackground` | `blockId`, `position` |
| `createArtItem` | `itemId` |
| `dependencyResolved` | `targetId` |
| `streamSelectThumbnail` | `streamId` |
| `homeInsertBlock` | (none) |

## JourneySessionStore

Location: `shared/nav/journeySession.store.ts`
Does NOT extend BaseStore — implements own subscribe/emit.

```ts
class JourneySessionStore {
  // Session management
  startJourney(home, firstTicket): void;
  pushOutbound(ticket, home?): void;
  peekNextTicketFor(editor): JourneyTicket | undefined;
  arrival(editor): JourneyTicket | undefined;
  completeReturn(editor, loot): void;
  continueJourney(): NextAction;

  // State access
  hasActiveSession(): boolean;
  getActiveSession(): JourneySession | undefined;
  getCurrentHome(): JourneyHome | undefined;
  isEditorInJourney(editor): boolean;
  clear(): void;

  // Diagnostics
  getDiagnostics(): JourneyDiagnostic[];

  subscribe(fn): () => void;
}
```

## Transporter hooks

Location: `features/admin/shared/transporter/transporter.ts`

| Hook | Purpose |
|------|---------|
| `useDispatch()` | Initiate outbound journey leg |
| `useReturnHome()` | Return with result, trigger continueJourney |
| `useArrival()` | Declare arrival, consume ticket |
| `usePeekTicket(editor)` | Peek without consuming |
| `useJourneyStatus(editor)` | Reactive boolean via useSyncExternalStore |

## Navigation guard components

| Guard | Location | Mechanism |
|-------|----------|-----------|
| `GuardedNavLink` | `features/admin/shared/ui/adminHeader/` | Wraps NavLink |
| `useGuardedNavigate` | `features/admin/shared/hooks/` | Wraps useNavigate |
| `useJourneyGuard(editor)` | `features/admin/shared/hooks/` | Guards destructive actions |

## Related

- [Journey guard behavior](../specs/spec--navigation--journey-guard-behavior.md)
- [All cross-editor flows use Journey](../invariants/invariant--navigation--all-cross-editor-flows-use-journey.md)
