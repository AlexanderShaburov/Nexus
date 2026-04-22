---
type: invariant
scope: [architecture, ui]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, adr-002]
---

# UI components must not contain business logic

## Rule

All React components are the **view plane** — they render UI and delegate actions.

Components:
- MUST NOT contain domain decisions, navigation protocol decisions, or CRUD orchestration
- MUST receive data and handlers via props or context hooks
- MUST delegate all actions to context methods (the control plane)

## Where it applies

- All React components in `features/`, `pages/`, `shared/ui/`
- Every editor (Block, Stream, Catalog, Event, Media)

## What counts as business logic

- CRUD orchestration (load/save/create/update/delete sequencing)
- Journey integration (ticket creation, return handling, bootstrap decisions)
- Validation rules and guard logic (unsaved changes, destructive confirmations)
- Mode transitions and selection rules (what happens on click/menu action)

All of the above belongs in the editor's **Context/Provider** (control plane).

## What is allowed in components

- Rendering and layout
- Calling context-provided handlers (`onClick={() => ctx.onHit(item)}`)
- Local visual state (hover, animation, focus)
- Derived display values (formatting dates, joining strings)

## Source

- Constitution §3.3 (v3): "Components MUST NOT contain business logic"
- ADR-002: Editor Contexts as the Control Plane
- `rules/CONSTITUTION.md`, `rules/ADR-002-editor-context-control-plane.md`

## Consequence of violation

- Tight coupling between rendering and domain logic
- Duplicated logic across components
- Broken architecture boundaries (feature-sliced layers)
- Hard-to-test code (business logic buried in render trees)
