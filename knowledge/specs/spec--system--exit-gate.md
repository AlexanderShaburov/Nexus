---
type: spec
scope: system
status: draft
created: 2026-04-18
updated: 2026-04-19
source_of_truth: true
tags: [knowledge, exit-gate, lifecycle, writeback]
---

# Exit Gate Specification

## Purpose

Exit Gate enforces proper completion of each task cycle.

It ensures that:
- meaningful changes are explicitly evaluated;
- knowledge is not lost between sessions;
- writeback decisions are made consciously;
- session traces are persisted.

Exit Gate closes the lifecycle loop:
→ Bootstrap → Decision → Execution → Exit

---

## Mandatory Rule

Before finishing any non-trivial response, the agent MUST execute Exit 
Gate.

The agent MUST NOT:
- finish a response without Exit Gate;
- defer Exit Gate execution;
- leave writeback decisions implicit.

If Exit Gate is missing:
→ the response is INVALID.

---

## Closure Block (Required Output)

The agent MUST produce a Closure Block at the end of the response:

```
Closure Block:
- code changed: yes/no
- KB changed: yes/no
- session log written: yes/no
- writeback evaluation performed: yes/no
```

---

## Field Definitions

### code changed

Indicates whether code was modified, created, or deleted.

### KB changed

Indicates whether the Knowledge Vault was updated.

### session log written

Indicates whether session trace was persisted.

### writeback evaluation performed

Indicates whether the agent evaluated if changes are knowledge-bearing.

---

## Dependency Rules

### Rule 1 — Code Change Requires Evaluation

If:
- code changed = yes

Then:
- writeback evaluation performed MUST be yes

---

### Rule 2 — Knowledge-Bearing Requires Writeback

If:
- writeback evaluation performed = yes
- and change is knowledge-bearing

Then:
- KB changed MUST be yes

---

### Rule 3 — No Writeback Requires Justification

If:
- KB changed = no

Then the agent MUST explicitly explain:
- why the change is not knowledge-bearing;
- why KB update is not required.

---

## Prohibited Behavior

The agent MUST NOT:

- skip writeback evaluation;
- leave KB decisions implicit;
- postpone writeback;
- provide empty or generic justifications.

Invalid examples:

- "KB not changed"
- "No need to update KB"

---

## Session Persistence

Exit Gate MUST ensure session trace persistence.

If session tracking exists, the agent MUST:

- create a session record if none exists;
- update the current session record;
- store:
  - decisions made
  - actions performed
  - key results

If session log is not written:
→ task is considered incomplete.

---

## Placement Rule

The Closure Block MUST:

- be the final element of the response;
- be clearly separated from the main content.

No content is allowed after the Closure Block.

---

## Enforcement

If any of the following is true:

- Closure Block is missing
- fields are incomplete
- dependency rules are violated
- justification is missing

→ the response is INVALID

---

## Relationship to Other Specs

Exit Gate MUST integrate with:

- Knowledge Sync Classification (for knowledge-bearing detection)
- Session Bootstrap (for lifecycle continuity)
- Context Decision Gate (for decision trace consistency)

---

## Summary

Exit Gate ensures that:

- work is not left open-ended;
- knowledge is captured and preserved;
- decisions are explicit and traceable;
- lifecycle is properly closed.

It is the final control point that guarantees system integrity.

