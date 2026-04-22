---
type: invariant
scope: [ui, editor]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, adr-006]
---

# All editor actions must go through standard command surfaces

## Rule

Two standard UI mechanisms are allowed for editor actions:

1. **SingleEditorToolbar** — primary actions (Save, Apply, Exit, Create, Customize, Tags, Delete)
2. **Three-Dot Menu** — secondary actions for list items (Edit, Duplicate, Delete, Move)

No custom scattered action buttons outside these surfaces.

## SingleEditorToolbar

- Context provides handlers and capabilities
- UI decides which tools to show based on state
- Save vs Apply semantics are defined by Journey state (ADR-001)
- Must be consistent across all editors

## Three-Dot Menu

- Appears on list/grid item cards (block collection, stream list, home items)
- Contains contextual secondary actions
- Stops click propagation (does not trigger card selection)

## Where it applies

- Every admin editor (Block, Stream, Catalog, Event, Media)
- Both Select Mode (three-dot on cards) and Edit Mode (toolbar)

## Source

- Constitution §7: "No custom scattered action buttons"
- ADR-006: Standard Command Surfaces
- `rules/CONSTITUTION.md`, `rules/ADR-006-standard-command-surfaces.md`

## Consequence of violation

- Inconsistent UX across editors
- Action buttons scattered across screens
- Harder to maintain and extend
