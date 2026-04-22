---
type: spec
scope: [navigation]
status: active
date: 2026-04-10
source_of_truth: false
tags: [journey, guards]
---

# Journey guard behavior

## GuardedNavLink

On click: checks `journeySessionStore.hasActiveSession()`. If active → `confirm("A journey is currently active. Navigating away will abandon it. Continue?")`. If user confirms → clears session, re-triggers navigation. If declines → prevents navigation.

## useGuardedNavigate

Same pattern as GuardedNavLink but for programmatic `navigate()` calls. Returns early if user declines. Clears session before navigating if confirmed.

## useJourneyGuard(editorKind)

Returns `{ isInJourney, canStartDeletion(), guardAction() }`.

- `canStartDeletion()`: returns `{ allowed: false, reason }` if journey active, `{ allowed: true }` otherwise
- `guardAction(action, blockedMessage?)`: wraps an action, shows `alert()` if blocked by journey

Prevents destructive operations (deletion) during active journeys.

## Key behavior

Guards use browser `confirm()` / `alert()` dialogs. Navigation is NOT silently disabled — the user is prompted and can choose to abandon the journey.

## Related

- [Journey system structure](../architecture/architecture--navigation--journey-system.md)
