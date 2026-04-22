---
type: invariant
scope: [architecture, data]
status: active
date: 2026-02-23
source_of_truth: true
tags: [constitution, domain-model]
---

# Domain entities are finite and controlled

## Rule

Adding a new **domain entity** requires an explicit decision (ADR). The Constitution recognizes 5 domain entities:

| Entity | Description |
|--------|-------------|
| **ArtItem** | Catalog item with metadata + media references |
| **Block** | Universal content container (gallery/text/cta/eventCta/composable) |
| **Stream** | Narrative composition of blocks |
| **Event** | Offline workshop/event entity |
| **HomeDoc** | Site portrait composed of HomeItems (singleton) |

## Non-entities (per Constitution)

- **Hopper** — pipeline/staging for media ingestion
- **HomeItem** — data structure inside HomeDoc
- Internal block sub-structures — parts of Block

## Entity layer vs domain entities

The `entities/` directory contains 12 modules, but not all are domain entities. The directory also houses:
- **Value types and shared domain models** (`common/`, `catalog/`, `renderable/`)
- **Utility entities** (`mediaItem/`, `textVisual/`) — not domain-level per Constitution
- **Pipeline types** (`hopper/`) — non-entity
- **Derived models** (`publicStream/`) — operational, not domain-level

The invariant applies to the **domain model** — what the Constitution considers first-class entities with lifecycle, identity, and persistence.

## Source

- Constitution §3.1: "Adding a new entity requires an explicit decision (ADR)"
- Constitution §3.2: Non-entities
- `rules/CONSTITUTION.md`

## Consequence of violation

- Hidden entities scattered inside components
- Uncontrolled model proliferation
- Broken domain boundaries
