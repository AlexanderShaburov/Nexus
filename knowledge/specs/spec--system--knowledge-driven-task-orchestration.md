---
type: spec
scope: system
status: active
date: 2026-04-17
source_of_truth: true
tags: [knowledge, orchestration]
---

# Knowledge-Driven Task Orchestration Specification

## Purpose

This specification defines how Claude MUST use the Knowledge Vault
as the primary source of project context and as the system of durable memory.

This specification DOES NOT define how Claude should think.

Claude’s internal reasoning, planning, and problem-solving processes
remain unchanged and MUST NOT be constrained or replaced by this document.

Instead, this specification defines mandatory requirements for:

- retrieving relevant project context before non-trivial work;
- grounding work in that context;
- synchronizing durable knowledge after work is completed.

The goal is to ensure that all work is:

- context-aware;
- consistent with project knowledge;
- traceable over time;
- reflected back into the Knowledge Vault when necessary.

---

## Core Principle

Claude MUST operate as a reasoning agent
that is grounded in project knowledge.

This means:

- Claude thinks, explores, and decides using its own reasoning abilities;
- BUT all non-trivial work MUST be grounded in retrieved project context;
- AND all durable changes MUST be synchronized back into the Knowledge Vault.

The Knowledge Vault is:

- the source of project context;
- the source of constraints and prior decisions;
- the destination for durable knowledge updates.

It is NOT:

- a replacement for reasoning;
- a forced execution pipeline;
- a substitute for exploration or planning.

---

## Knowledge Interaction Model

All non-trivial work must satisfy three obligations:

1. Retrieve — obtain relevant project context
2. Ground — apply that context during work
3. Sync — update durable knowledge after work

---

## 1. Retrieve (Context Acquisition)

Before performing non-trivial work, Claude MUST:

- identify relevant domains (architecture, features, systems);
- retrieve relevant documents from the Knowledge Vault;
- prioritize:
  - invariants
  - architecture
  - specs
  - decisions
  - patterns
  - sessions (if needed)

Claude MUST NOT proceed with non-trivial work without minimal sufficient context.

---

## 2. Ground (Context Application)

During work, Claude MUST:

- respect invariants and architectural constraints;
- follow specs for expected behavior;
- consider prior decisions and patterns;
- surface conflicts explicitly if they arise.

If a task appears to contradict existing knowledge:

- Claude MUST NOT silently ignore the conflict;
- Claude SHOULD surface and explain it.

---

## 3. Sync (Knowledge Writeback)

After completing work, Claude MUST evaluate whether knowledge changes occurred.

If yes, Claude MUST update appropriate sections:

- sessions/
- plans/
- specs/
- architecture/
- decisions/
- patterns/
- bugs/

Claude MUST ensure that durable knowledge reflects actual system state.

---

## Planning Artifacts

Plans are NOT a replacement for reasoning.

Plans are durable artifacts used to:

- preserve intent;
- track multi-step work;
- record execution status.

If a plan is expressed in structured form
AND the task is non-trivial,
Claude SHOULD materialize it as a Plan document.

If the response already contains:
- structured sections
- multi-step design
- migration rules
- phased execution

→ this qualifies as a plan
→ MUST be externalized

Claude SHOULD create or update a plan when:

- the task is multi-step;
- the solution is not trivial;
- future traceability is important.

Plan statuses MUST be explicit:

- proposed
- in_progress
- implemented
- rejected
- superseded

## Phase progression rule

For tasks executed under a phased plan, Claude MUST treat each phase boundary as a pause point.

After completing a phase, Claude MUST:

- report completion status,
- note deviations or unresolved items,
- wait for explicit user confirmation before starting the next phase.

Claude MUST NOT automatically advance from Phase N to Phase N+1 merely because no blockers were detected.

For non-phased or trivial work, this rule does not apply.
---

## Closure Requirement

For non-trivial tasks, Claude MUST produce a closure report.

Example format:

```
Task Closure Report

Task type:
- ...

Knowledge retrieved:
- ...

Constraints considered:
- ...

Changes made:
- ...

Knowledge updated:
- ...

Open items:
- ...
```

---

## Commit Discipline

Claude MUST ensure:

- all work is committed logically;
- knowledge updates are committed with related changes;
- no knowledge-bearing work is left uncommitted.

---

## Summary

Claude remains a reasoning agent.

This specification ensures that reasoning is:

- grounded in real project knowledge;
- consistent with system constraints;
- preserved in durable memory.

The Knowledge Vault is the system of context and memory,
not a replacement for thinking.
