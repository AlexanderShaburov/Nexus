---
type: invariant
scope: [architecture]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, fsd]
---

# Dependencies flow downward only between layers

## Rule

```
app → pages → features → entities
                 ↓
               shared
```

- Dependencies go **downward only**
- `entities/` must not depend on React/UI, routing, or `features/`
- `shared/` must not become a feature-specific dumping ground
- No upward dependencies, no cross-layer violations

## Where it applies

- All import statements in frontend code
- Module boundaries between `app/`, `pages/`, `features/`, `entities/`, `shared/`

## Concrete rules

| Layer | May import from | Must NOT import from |
|-------|----------------|---------------------|
| `app/` | pages, features, entities, shared | — |
| `pages/` | features, entities, shared | app |
| `features/` | entities, shared | app, pages, other features (unless shared sub-module) |
| `entities/` | shared (types only) | app, pages, features |
| `shared/` | — | app, pages, features, entities |

## Source

- Constitution §2: "Dependencies go downward only"
- `rules/CONSTITUTION.md`

## Consequence of violation

- Circular dependencies
- Feature coupling (changes in one editor break another)
- Broken build and import resolution
