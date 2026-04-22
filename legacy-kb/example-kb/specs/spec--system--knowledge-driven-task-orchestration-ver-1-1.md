# Knowledge-Driven Task Orchestration Specification

## Purpose

This specification defines how Claude MUST process all non-trivial tasks
using the Knowledge Vault as the primary operational memory and operational
coordination layer.

The goal is to ensure that:

- Claude does not operate from scratch;
- relevant project knowledge is always retrieved before meaningful work begins;
- plans for non-trivial work are explicitly materialized and preserved;
- engineering work remains constrained by documented architecture,
  invariants, specs, and decisions;
- durable outcomes are written back into the Knowledge Vault;
- each task remains traceable across intent, execution, and outcome.

This specification governs how Claude must move from user request to
knowledge-grounded execution and then to durable knowledge closure.

---

## Core Principle

Claude MUST NOT operate from scratch.

For every non-trivial task, Claude MUST:

1. determine what kind of task it is;
2. retrieve the minimum relevant knowledge required to act safely;
3. derive binding constraints from retrieved knowledge;
4. create or update an explicit task plan when planning is required;
5. perform the work within the extracted constraints;
6. write back durable knowledge produced by the work;
7. produce a traceable closure report.

The Knowledge Vault is the source of truth, not the model's internal memory.

---

## Operational Model

Knowledge-driven task execution has three distinct layers:

1. **Knowledge Layer**  
   Existing project knowledge that constrains action:
   architecture, invariants, specs, decisions, patterns, bugs, sessions, indexes.

2. **Planning Layer**  
   The task-specific operational plan that defines intended work before or during
   execution.

3. **Outcome Layer**  
   Durable records of what actually happened:
   implementation changes, knowledge updates, sessions, bug records,
   spec/architecture updates, decisions, patterns.

Claude MUST preserve the distinction between these layers.

In particular:

- a **plan** is not the same as a **session note**;
- a **plan** describes intended work and evolving execution status;
- a **session** records what was actually done and learned;
- an **ADR / decision** records stable technical decisions;
- architecture and specs record durable project truth after the task.

---

## Task Lifecycle

Every non-trivial task MUST follow this lifecycle:

1. Task Intake
2. Task Classification
3. Knowledge Retrieval
4. Context Expansion
5. Constraint Extraction
6. Plan Determination
7. Plan Creation or Update
8. Engineering Work
9. Knowledge Writeback
10. Closure Report
11. Commit Discipline

Trivial tasks MAY use a reduced lifecycle when no architectural,
behavioral, or coordination risk is present.

---

## 1. Task Intake

Claude receives a prompt and MUST:

- restate the task internally;
- identify key entities, systems, domains, and affected surfaces;
- determine whether the task is trivial or non-trivial;
- determine whether the task implies implementation, analysis, planning,
  documentation, or architectural impact.

Trivial tasks MAY skip the full lifecycle only if all of the following are true:

- the change is local and low-risk;
- no documented invariant, architecture rule, or spec behavior is likely involved;
- no durable project knowledge is likely to be created or changed;
- no explicit planning artifact is needed.

All other tasks MUST follow the full lifecycle.

---

## 2. Task Classification

Claude MUST classify the task into one or more of the following categories:

- bugfix
- feature implementation
- refactor
- audit / analysis
- documentation update
- architecture change
- planning / design work

Task classification determines:

- retrieval depth;
- planning requirement;
- writeback expectations;
- whether a stable decision may need ADR treatment;
- whether user confirmation may be required.

Claude MUST use the most demanding applicable classification when multiple
categories apply.

---

## 3. Knowledge Retrieval

Claude MUST automatically retrieve relevant documents from the Knowledge Vault
before starting non-trivial work.

### Retrieval Strategy

Claude MUST use naming and index-guided retrieval first.

Primary retrieval should be guided by:

- task keywords;
- affected entities or subsystems;
- `index--system--project-navigation.md` and other routing/index documents.

Claude MUST prioritize the most authoritative documents first.

### Default Retrieval Priority

1. `index/`
2. `invariants/`
3. `architecture/`
4. `specs/`
5. `decisions/`
6. `patterns/`
7. `bugs/`
8. `sessions/`

### Retrieval Rules by Task Type

If the task is a bugfix:

- Claude MUST also inspect relevant `bugs/` records if they exist.

If the task affects ongoing or recently modified work:

- Claude SHOULD inspect recent `sessions/`.

If the task is architectural, multi-step, or likely to branch into alternatives:

- Claude MUST retrieve relevant `decisions/` and architecture constraints before
  planning implementation.

Claude MUST NOT rely on memory alone.

---

## 4. Context Expansion

After initial retrieval, Claude MUST expand context enough to avoid acting on
partial knowledge.

Context expansion includes:

- following linked or referenced documents;
- identifying connected subsystems and dependent surfaces;
- reading invariants referenced by architecture;
- reading specs governing expected behavior;
- reading decisions affecting allowed approaches;
- reading patterns used in comparable implementations;
- reading bug records or sessions when they materially reduce risk.

Claude SHOULD stop expansion when the minimal safe execution context has been
reached.

Claude MUST avoid both:

- under-retrieval that causes unsafe implementation;
- over-retrieval that creates unnecessary noise without improving task safety.

---

## 5. Constraint Extraction

Claude MUST explicitly derive operational constraints from the retrieved
knowledge before performing non-trivial work.

These constraints include, where applicable:

- invariants that MUST NOT be violated;
- required protocols and workflows;
- architectural boundaries, layering rules, and dependency restrictions;
- expected behavior from specs;
- previously accepted technical decisions;
- reusable patterns that should be preferred over ad hoc invention.

Claude MUST treat extracted constraints as binding unless the task is explicitly
to change them.

If a task appears to require violating a documented invariant, architecture
rule, or decision, Claude MUST treat the task as a higher-order knowledge change,
not as ordinary implementation work.

---

## 6. Plan Determination

Claude MUST determine whether an explicit plan artifact is required.

A plan artifact is REQUIRED for any non-trivial task that is at least one of:

- feature implementation with multiple steps or phases;
- refactor affecting structure, ownership, or flow;
- architecture change;
- work involving multiple candidate approaches;
- work expected to span more than one meaningful implementation step;
- work where intent, sequencing, or acceptance status should remain visible later;
- audit or analysis expected to produce a proposed course of action.

A plan artifact MAY be omitted only when the non-trivial task is still narrow
enough that all of the following hold:

- work is operationally simple;
- there is no meaningful branching of approach;
- no future trace value would be lost by not preserving the plan;
- the session record alone is sufficient.

If there is doubt, Claude SHOULD create or update a plan.

---

## 7. Plan Creation or Update

When a plan is required, Claude MUST create or update a plan document before
or during execution early enough for the plan to guide the work.

### Role of the Plan

A plan is the durable record of intended work.

It exists to preserve:

- why the task exists;
- what problem is being solved;
- what constraints shape the solution;
- what approach is proposed;
- what alternatives were considered;
- what the current execution status is.

The plan is not a replacement for architecture, specs, decisions, or sessions.

### Plan Requirements

A valid plan MUST include, at minimum:

- task identity or title;
- current status;
- context / problem statement;
- goals or intended outcome;
- relevant constraints;
- proposed approach;
- implementation scope or phased breakdown when applicable;
- links to related knowledge documents.

Where relevant, a plan SHOULD also include:

- alternatives considered;
- explicit risks;
- open questions;
- completion criteria;
- reasons for rejection or abandonment if not implemented.

### Plan Status

Plan status MUST be explicit and updated as work progresses.

Recommended statuses:

- proposed
- in_progress
- implemented
- rejected
- superseded

Claude MUST update the plan status when execution materially changes its state.

### Planning Discipline

Claude MUST use the plan as the task-level operational reference during work.

If the chosen implementation path materially changes:

- the plan MUST be updated;
- or the deviation MUST be explicitly captured in the final outcome records.

Claude MUST NOT silently execute a materially different solution than the one
preserved in the plan.

---

## 8. Engineering Work

Claude performs the task while:

- respecting extracted constraints;
- following the active plan when one exists;
- avoiding invariant violations;
- reusing existing architectural solutions when applicable;
- preferring documented patterns over ad hoc design;
- preserving alignment between implementation, plan, and project knowledge.

If constraints are unclear, incomplete, or conflicting:

- Claude MUST explicitly note the conflict;
- Claude SHOULD inspect related decisions, sessions, or specs if available;
- Claude MAY request clarification when necessary.

If the task produces a new stable decision, Claude MUST treat this as a
potential decision-record update, not merely as implementation detail.

---

## 9. Knowledge Writeback

After completing the task, Claude MUST determine what durable knowledge
must be written back.

Writeback is not optional for non-trivial work; only the routing varies.

Claude MUST classify outcomes into one or more of the following destinations.

### Session

A session record is expected for almost all non-trivial tasks.

Write to `sessions/`:

- what was done;
- what knowledge was retrieved;
- what constraints shaped the work;
- what decisions or deviations occurred during execution;
- what remains unresolved.

A session is the record of actual execution, not merely intended work.

### Plans

Update the relevant plan if one exists or was required.

Plan writeback MUST include, where applicable:

- current status;
- whether the plan was implemented, rejected, or superseded;
- material deviations from the original approach;
- references to resulting specs, ADRs, architecture updates, or sessions.

Claude MUST NOT leave a completed or abandoned plan in an ambiguous state.

### Bugs

Write to `bugs/` only if all of the following apply:

- a real defect was identified;
- root cause is understood;
- fix is defined or implemented;
- future recurrence is plausible enough that the record has durable value.

A bug record MUST include:

- symptom
- scope
- root cause
- fix
- prevention / pattern

### Specs

Update or create a spec if:

- expected behavior changed;
- behavior was clarified;
- edge cases became explicit;
- implementation exposed previously implicit behavioral rules that should now
  be durable.

### Architecture

Update architecture if:

- system structure changed;
- responsibilities changed;
- layering changed;
- boundaries, ownership, or data flow changed.

### Decisions (ADR)

Create or update a decision record if:

- a new stable technical decision was made;
- alternatives were meaningfully evaluated;
- a durable choice now constrains future work.

User confirmation MAY be required for major decisions.

### Patterns

Create or update a pattern if:

- a reusable implementation solution emerged;
- the solution has value beyond the immediate task.

---

## 10. Closure Report

Claude MUST produce a structured closure report for non-trivial tasks.

The closure report MUST preserve traceability across:

- task type;
- retrieved knowledge;
- extracted constraints;
- plan usage;
- implementation changes;
- knowledge writeback decisions;
- unresolved items.

### Required Format

```text
Task Closure Report

Task type:
- ...

Knowledge retrieved:
- documents:
  - ...

Constraints applied:
- ...

Plan:
- required: yes/no
- document: ...
- final status: ...

Changes made:
- ...

Knowledge updated:
- plans: yes/no
- sessions: yes/no
- bugs: yes/no
- specs: yes/no
- architecture: yes/no
- decisions: yes/no
- patterns: yes/no

Reasoning:
- why these updates were required or not required

Open items:
- ...
```

If no explicit plan was required, the report MUST make that omission explicit.

---

## 11. Commit Discipline

Claude MUST ensure:

- each logical unit of work is committed;
- knowledge updates are committed with the corresponding implementation changes;
- plan updates are committed with the work they govern when practical;
- no completed knowledge-bearing work remains uncommitted.

Final reporting MUST include:

```text
Commits:
- message 1
- message 2

Working tree:
- clean / not clean
```

---

## Interaction with Sync-Check

This specification works together with:

`spec--devops--knowledge-sync-classification.md`

### Responsibility Split

- Orchestration Spec → proactive operational behavior
- Sync-Check Spec → reactive completeness and guardrail behavior

This specification defines how Claude must work.
Sync-Check defines what Claude must not fail to persist.

If Sync-Check flags a possible omission:

- Claude MUST revisit plan state and knowledge writeback;
- Claude MUST update the relevant records;
- or Claude MUST explicitly justify why no update is required.

---

## Failure Modes to Avoid

Claude MUST avoid the following failure modes:

- implementing non-trivial work without retrieval;
- retrieving knowledge but failing to derive constraints;
- planning internally without persisting a required plan;
- performing materially different work without updating the plan;
- completing work without updating plan status;
- updating sessions but leaving intent/history untraceable;
- changing behavior or structure without updating specs or architecture;
- making stable decisions without decision capture;
- relying on internal memory instead of the Vault.

---

## Limitations

- retrieval quality depends on naming quality, routing quality, and index coverage;
- not all relevant documents may be discovered automatically;
- some routing and writeback decisions still require human judgment;
- plans and sessions may grow rapidly without archival discipline;
- excessive planning for narrow work can create unnecessary overhead.

---

## Future Improvements

- semantic retrieval in addition to naming and index routing;
- stronger structured metadata for document routing;
- explicit cross-links between plans, sessions, ADRs, specs, and architecture;
- plan templates with required fields and status validation;
- archival rules for implemented, rejected, and superseded plans;
- tighter integration with version control and task tracking.

---

## Summary

Claude MUST operate as a knowledge-driven agent.

Non-trivial tasks are not solved in isolation.
They move through retrieval, constraint grounding, explicit planning when
required, disciplined execution, and durable writeback.

Every meaningful task must leave a trace across:

- what was known,
- what was intended,
- what was done,
- and what became durable project knowledge.

The Knowledge Vault is the system's persistent intelligence layer and
operational memory.
