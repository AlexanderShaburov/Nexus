---
created: 2026-04-18
scope: system
source_of_truth: true
knowledge_visibility: binding
status: approved
tags:
- knowledge
- bootstrap
- session
type: spec
updated: 2026-06-04
---

## Relations

- depends_on:
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — bootstrap is the entry mechanism for the Retrieve obligation.
- relates_to:
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — bootstrap is the first non-negotiable gate.
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — bootstrap is realized by the SessionStart hook described there.

---

## BOOTSTRAP EXECUTION --- REQUIRED

You are REQUIRED to execute this protocol immediately.

Before performing ANY actions, you MUST:

1.  Read this entire document.
2.  Execute all steps defined in **Mandatory Startup Reading Set**.
3.  Confirm that the Knowledge Vault has been loaded as the primary
    context.
4.  Enter Knowledge-Driven Mode.

You MUST NOT:

-   skip any step;
-   partially execute bootstrap;
-   begin task execution before bootstrap completion;
-   rely on prior memory instead of loaded knowledge.

If bootstrap is not completed, all subsequent actions are considered
invalid.

Proceed with bootstrap execution now.

------------------------------------------------------------------------

# Session Bootstrap Specification

## Purpose

Session Bootstrap is a deterministic initialization protocol.

It ensures that every session begins with:

-   canonical project context;
-   validated knowledge sources;
-   enforced behavioral rules.

------------------------------------------------------------------------

## Trigger

Session Bootstrap MUST execute:

-   at session start;
-   after context compaction.

It executes exactly once per session.

------------------------------------------------------------------------

## Mandatory Startup Reading Set

### System Entry Points

-   knowledge/index/index--system--project-navigation.md
-   knowledge/specs/spec--system--knowledge-driven-task-orchestration.md
-   knowledge/architecture/architecture--system--overall-structure.md

### Canonical Constraints

-   knowledge/invariants/

All invariants MUST be treated as non-negotiable constraints.

------------------------------------------------------------------------

## STEP 3 — ACTIVE DESIGN TRACKS (advisory; required when performing review tasks)

Before performing **architecture review**, **gap analysis**, **roadmap
planning**, or **missing-spec analysis**, the agent MUST also discover and
consider documents in the **development** visibility class. These documents
are **not** authoritative, but they must be visible to review so that
already-drafted work is not reported as missing.

Sources of development-class documents:

-   `knowledge/plans/` — roadmap drafts and in-progress intent.
-   `knowledge/sessions/` — session-derived design notes.
-   any document with `status` of `draft`, `in-progress`, or `review`.
-   any document with `knowledge_visibility: development`.

Workflow contract for review tasks:

-   `knowledge/specs/spec--system--architecture-review.md` — mandatory dual
    analysis (Binding State + Development State) with four-way gap
    classification.

Non-negotiable rule:

-   `knowledge/invariants/invariant--system--review-classification.md` — no
    gap may be reported without examining both binding and development
    knowledge.

Classification mechanism:

-   `knowledge/specs/spec--system--knowledge-visibility.md` — the three
    visibility classes and the fallback mapping.

This step is advisory at session start (it does not block bootstrap
completion), but it is **required** whenever a review-class task is
triggered. The Mandatory Startup Reading Set above is unchanged; this
section names additional discovery the agent owes the review surface.

------------------------------------------------------------------------

## Operational Mode

After loading all required documents, the agent enters Knowledge-Driven
Mode.

### Rules

-   Knowledge Vault is the source of truth
-   Memory is non-authoritative
-   All work must be grounded in retrieved context

------------------------------------------------------------------------

## Completion Confirmation

The agent MUST produce:

Session Bootstrap Completed

Loaded: - navigation index - orchestration spec - system architecture -
invariants

Operational Mode: - Knowledge-Driven Mode: ACTIVE
