---
type: invariant
scope: [state, editor]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, adr-002]
---

# Bootstrap must read external stores imperatively, not via hooks

## Rule

During editor mount/bootstrap, external stores must be read **directly** (imperatively), not via React hooks.

```ts
// CORRECT — imperative read during bootstrap
const ticket = journeySessionStore.peekNextTicketFor('blocks');
const snapshot = editSessionsDataStore.getSnapshot(key);

// WRONG — hook-based read during bootstrap
const ticket = usePeekTicket('blocks');  // may be stale on first render
```

## Why

Hook-based store subscriptions may reflect correct values only after subsequent render cycles. Bootstrap must compute correct initial mode/state on the **very first mount** — it cannot wait for a re-render.

## Where it applies

- Every editor's bootstrap/mount logic
- Journey ticket reading during initialization
- Initial state resolution in Context/Provider `useEffect` or constructor

## After bootstrap

After mount is complete, hooks are the correct way to subscribe to store updates for reactivity.

## Source

- Constitution §4.2: "During mount/bootstrap, read external stores directly"
- ADR-002: Bootstrap Rule
- `rules/CONSTITUTION.md`, `rules/ADR-002-editor-context-control-plane.md`

## Consequence of violation

- Editor opens in wrong mode (stale Journey ticket)
- Race condition between mount and first render
- Incorrect initial state leading to flash of wrong UI
