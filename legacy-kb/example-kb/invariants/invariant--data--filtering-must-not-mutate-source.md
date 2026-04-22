---
type: invariant
scope: [data, editor]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution]
---

# Filtering must not mutate source data

## Rule

Filtering in Select Mode is always a **derived view**. It must NOT mutate the source-of-truth collection.

- Filter logic must be a pure function: `(items, filter) → filteredItems`
- The source collection remains unchanged
- Clearing filters restores the full view
- Must work consistently across all editors

## Where it applies

- Block editor Select Mode (filter by kind, layout, tags, art name)
- Stream editor Select Mode
- Catalog editor Select Mode
- Media editor Select Mode (filter by text search, tags, type)
- Any future editor with a grid/list view

## Source

- Constitution §8: "Filtering MUST NOT mutate source data"
- Constitution §4.4: "Filtering produces a derived view"
- `rules/CONSTITUTION.md`

## Consequence of violation

- Data loss (original collection modified by filters)
- Inconsistent state after clearing filters
- Items "disappearing" from the collection
