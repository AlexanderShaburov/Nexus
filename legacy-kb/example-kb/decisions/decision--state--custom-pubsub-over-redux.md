---
type: decision
scope: [state]
status: active
date: 2026-02-23
source_of_truth: false
tags: [stores, state-management]
---

# Custom pub/sub stores chosen over Redux/Zustand

## Context

The application needs state management for cross-screen data (catalogs, collections, sessions, Journey state). React Context alone is insufficient because it couples state to the React lifecycle.

## Decision

Use a custom `BaseStore` / `DataStore<T>` pub/sub system with `useSyncExternalStore` integration.

## Why

- Minimal overhead — no library dependency for a well-understood pattern
- Full control over subscription lifecycle
- External to React — stores survive component mount/unmount
- Natural fit for the bootstrap invariant (stores must be readable imperatively)
- Simple API: `get()`, `set()`, `clear()`, `subscribe()`, `getSnapshot()`

## How it works

- `BaseStore` provides subscribe/emit mechanism
- `DataStore<T>` adds typed get/set/clear on top
- `EditSessionsDataStore` manages draft/snapshot pairs per `EditorKey`
- React reads stores via `useStoreData()` (backed by `useSyncExternalStore`)
- During bootstrap, stores are read directly via `getSnapshot()` (no hooks)

## Alternatives considered

- **Redux** — too heavy for this project, adds boilerplate without proportional benefit
- **Zustand** — lighter than Redux but still an external dependency for what amounts to typed containers
- **Context-only state** — breaks across mounts, creates god-context anti-pattern
- **Router-only state** — insufficient for rich editor sessions and Journey tickets
