---
type: index
scope: [system]
status: active
date: 2026-04-10
source_of_truth: true
tags: []
---

# Project Knowledge Index

Type-purity audited 2026-04-10. Architecture contains only structure. Behavior extracted to specs.

**Priority:** invariants → architecture → specs → decisions → patterns → glossary

---

## Invariants (8)

| Document | Rule |
|----------|------|
| [No business logic in UI](../invariants/invariant--architecture--no-business-logic-in-ui.md) | Components render only; logic in contexts |
| [All cross-editor flows use Journey](../invariants/invariant--navigation--all-cross-editor-flows-use-journey.md) | Journey is the only cross-editor nav protocol |
| [Downward-only dependencies](../invariants/invariant--architecture--downward-only-dependencies.md) | app → pages → features → entities ← shared |
| [No global data in React contexts](../invariants/invariant--state--no-global-data-in-react-contexts.md) | Context = control plane, Store = data plane |
| [Entities are finite and controlled](../invariants/invariant--architecture--entities-are-finite-and-controlled.md) | 5 domain entities; new ones require ADR |
| [Filtering must not mutate source](../invariants/invariant--data--filtering-must-not-mutate-source.md) | Filtering is always a derived view |
| [Bootstrap reads stores imperatively](../invariants/invariant--state--bootstrap-reads-stores-imperatively.md) | No hooks during mount/bootstrap |
| [Standard command surfaces only](../invariants/invariant--ui--standard-command-surfaces-only.md) | SingleEditorToolbar + ThreeDotMenu |

## Architecture (11) — structure only

### System
| Document | Scope |
|----------|-------|
| [Overall structure](../architecture/architecture--system--overall-structure.md) | Vault + Knowledge + Application layers |
| [Frontend layering](../architecture/architecture--system--frontend-layering.md) | FSD, routes, provider chains |
| [Auth structure](../architecture/architecture--system--authentication.md) | Components, session model, endpoints |
| [Hopper pipeline structure](../architecture/architecture--system--hopper-ingestion-pipeline.md) | Components, shipment union, filesystem |

### Editor
| Document | Scope |
|----------|-------|
| [Generic editor architecture](../architecture/architecture--editor--dual-mode-context-control-plane.md) | Dual mode, context, implementations table |
| [Media editor structure](../architecture/architecture--editor--media-editor.md) | Modes, session interface, components |
| [Event system structure](../architecture/architecture--editor--event-system.md) | Two editors, draft models, structural differences |

### Infrastructure
| Document | Scope |
|----------|-------|
| [Journey system](../architecture/architecture--navigation--journey-system.md) | Ticket model, return commands, store API, hooks |
| [Domain model](../architecture/architecture--data--domain-model.md) | Entities, relationships, block types, value types |
| [State management](../architecture/architecture--state--custom-pubsub-stores.md) | Store hierarchy, APIs, React hooks |
| [Rendering components](../architecture/architecture--renderer--component-hierarchy.md) | Component table, resolver, dispatch, appearance |

## Specs (6) — behavior

| Document | Behavior |
|----------|----------|
| [Media editor behavior](../specs/spec--editor--media-editor-behavior.md) | Picker flow, upload-during-pick, deletion, mode transitions |
| [Event system behavior](../specs/spec--editor--event-system-behavior.md) | Journey flows, media picker integration, factory creation |
| [Journey guard behavior](../specs/spec--navigation--journey-guard-behavior.md) | GuardedNavLink, useGuardedNavigate, useJourneyGuard |
| [Hopper ingestion behavior](../specs/spec--system--hopper-ingestion-behavior.md) | Upload flow, ArtItem path, MediaItem path |
| [Auth behavior](../specs/spec--system--authentication-behavior.md) | Login flow, session validation, RequireAuth |
| [Rendering behavior](../specs/spec--renderer--rendering-behavior.md) | Context-aware rendering, public interaction, mobile |

## Decisions (4)

| Document | Choice |
|----------|--------|
| [Feature-Sliced Design](../decisions/decision--architecture--feature-sliced-design.md) | FSD for frontend structure |
| [Custom pub/sub over Redux](../decisions/decision--state--custom-pubsub-over-redux.md) | Lightweight custom stores |
| [JSON vault, no database](../decisions/decision--data--json-vault-no-database.md) | Files as source of truth |
| [Unified rendering](../decisions/decision--renderer--unified-rendering-frame-renderable.md) | Frame + Renderable (in progress) |

## Patterns (2)

| Document | Pattern |
|----------|---------|
| [Draft/Snapshot](../patterns/pattern--state--draft-snapshot.md) | Two-copy editing with dirty detection |
| [Context Provider Convention](../patterns/pattern--editor--context-provider-convention.md) | undefined default + throwing hook |

## Glossary (1)

| Document | Coverage |
|----------|---------|
| [Domain terms](../glossary/glossary--system--domain-terms.md) | Entities, mechanisms, architecture, UI terms |

## Open Questions (2)

| Document | Issue |
|----------|-------|
| [Inconsistent optimistic concurrency](../open-questions/open_question--data--inconsistent-optimistic-concurrency.md) | Only 3/9 repos enforce version checks |
| [Entities layer violation](../open-questions/open_question--architecture--entities-layer-violation.md) | entities/common imports from shared/ui |

---

## Reading path

1. **Domain model** → entities and reference types
2. **State management** → stores and hooks
3. **Generic editor architecture** → dual mode, context pattern
4. **Specific editor** (architecture) → structure
5. **Specific editor** (spec) → behavior
6. **Journey system** → navigation structure + guard behavior
7. **Invariants** → before any structural change

## Source documents

| Document | Location |
|----------|---------|
| Constitution | `rules/CONSTITUTION.md` |
| ADRs | `rules/ADR-001..007.md` |
| Architecture spec | `Docs/ARCHITECTURE.md` |
| Block editor spec | `Docs/BLOCK_EDITOR_SPEC.md` |
| Event page spec | `Docs/EVENT_PAGE_MODEL_SPEC.md` |
| Media editor spec | `Docs/MEDIA_EDITOR_SPEC.md` |
