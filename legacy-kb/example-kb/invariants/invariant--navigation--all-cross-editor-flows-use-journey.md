---
type: invariant
scope: [navigation, editor]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, adr-001]
---

# All cross-editor navigation with return semantics must use Journey

## Rule

Journey is the **only** allowed protocol for cross-editor navigation that requires:
- returning to the caller
- passing a result (selection/created entity)
- supporting deep nesting

No bypass via ad-hoc routing, query params, prop-drilling, or direct navigation.

## How Journey works

- One Journey = one JourneyTicket stored in an **external store** (JourneySessionStore, outside React)
- The ticket grows with legs/segments as the journey goes deeper
- Editors read the current ticket/leg from the store during bootstrap
- Ticket survives editor mount/unmount and route changes

## UX guardrails (implementation)

Navigation is NOT silently disabled during active Journey. Instead, three guard mechanisms intercept and prompt:

1. **GuardedNavLink** — wraps admin header NavLinks; shows `confirm()` dialog before allowing navigation away
2. **useGuardedNavigate** — wraps programmatic navigation with same confirm dialog
3. **useJourneyGuard** — blocks destructive actions (deletion) during active journey

The user CAN abandon a journey via confirmation, but is warned.

## Save vs Apply semantics (MUST)

- **Save** = persist current entity, remain in editor (no journey advancement)
- **Apply** = complete the current journey leg, persist if needed, return to caller with result

## Source

- Constitution §4.1 (v3)
- ADR-001: Journey as the Only Cross-Editor Navigation Protocol
- Guard implementations: `GuardedNavLink.tsx`, `useGuardedNavigate.ts`, `useJourneyGuard.ts`

## Consequence of violation

- Navigation state spaghetti (duplicated return logic, broken nesting)
- Journey state lost on mount/unmount
- Inconsistent user experience across editors
