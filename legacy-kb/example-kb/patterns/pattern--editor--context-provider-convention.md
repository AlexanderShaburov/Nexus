---
type: pattern
scope: [editor]
status: active
date: 2026-02-23
source_of_truth: false
tags: [react, convention]
---

# Context Provider Convention

## Problem

Editor contexts need a safe way to ensure they are only consumed within their provider boundary. Using a default value (e.g., `null`) would silently produce runtime errors when a component accidentally renders outside the provider.

## Solution

Create context with `undefined` default. Expose via a `useFeature()` hook that throws if used outside the provider.

```ts
// 1. Create context with undefined default
const BlockEditorContext = createContext<BlockEditorSession | undefined>(undefined);

// 2. Expose via hook that throws
export function useBlockEditor(): BlockEditorSession {
  const ctx = useContext(BlockEditorContext);
  if (!ctx) {
    throw new Error('useBlockEditor must be used within BlockEditorSessionProvider');
  }
  return ctx;
}

// 3. Provider wraps the route
export function BlockEditorSessionProvider({ children }: { children: ReactNode }) {
  // ... bootstrap, state, handlers ...
  return (
    <BlockEditorContext.Provider value={session}>
      {children}
    </BlockEditorContext.Provider>
  );
}
```

## Naming convention

| Element | Pattern | Example |
|---------|---------|---------|
| Context | `{Domain}EditorContext` | `BlockEditorContext` |
| Hook | `use{Domain}Editor()` | `useBlockEditor()` |
| Provider | `{Domain}EditorSessionProvider` | `BlockEditorSessionProvider` |
| Session type | `{Domain}EditorSession` | `BlockEditorSession` |

## Where it applies

- Every admin editor (Block, Stream, Catalog, Event, Media, EventPage)
- Auth context
- Any feature-scoped context

## Related

- [Editor architecture](../architecture/architecture--editor--dual-mode-context-control-plane.md)
- [No business logic in UI](../invariants/invariant--architecture--no-business-logic-in-ui.md)
