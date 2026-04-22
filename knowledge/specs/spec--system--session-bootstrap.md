---
created: 2026-04-18
scope: system
source_of_truth: true
status: approved
tags:
- knowledge
- bootstrap
- session
type: spec
updated: 2026-04-19
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
