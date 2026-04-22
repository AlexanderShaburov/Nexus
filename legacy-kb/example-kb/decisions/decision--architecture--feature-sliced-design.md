---
type: decision
scope: [architecture]
status: active
date: 2026-02-23
source_of_truth: false
tags: [constitution, frontend]
---

# Feature-Sliced Design is used for frontend structure

## Context

The project needs a scalable frontend architecture that prevents drift, especially when using coding agents. The codebase includes both a public gallery and an admin dashboard with multiple complex editors.

## Decision

Use Feature-Sliced Design with strict layering:

```
app → pages → features → entities
                 ↓
               shared
```

## Layer responsibilities

| Layer | Purpose | May depend on |
|-------|---------|---------------|
| `app/` | Entry point, routing, providers, layouts | pages, features, entities, shared |
| `pages/` | Route leaf components (lazy-loaded) | features, entities, shared |
| `features/` | Business logic (admin editors + public rendering) | entities, shared |
| `entities/` | Pure domain models and types (no UI, no React) | shared (types only) |
| `shared/` | Infrastructure: stores, nav, lib, ui primitives | nothing above it |

## Why

- Clear separation of concerns between domain, logic, and presentation
- Predictable structure (agent-friendly)
- Scalability — each editor is a self-contained feature
- Enforceable dependency rule (downward only)

## Path aliases

```
@/         → ./src
@/features → ./src/features
@/entities → ./src/entities
@/shared   → ./src/shared
```

## Alternatives considered

- Flat structure — no separation at scale
- Component-based only — mixes domain and UI
- Domain-driven frontend — too heavy for this project size

## Source

- Constitution §2: Layers
- `rules/CONSTITUTION.md`
