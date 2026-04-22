# Knowledge Sync Classification Specification

## Purpose

This specification defines how code, data, and documentation changes are classified
in terms of their **knowledge impact and synchronization requirements**.

The goal is to ensure that:

* architectural and behavioral changes are reflected in the Knowledge Vault;
* planning artifacts are consistently validated when required;
* knowledge, plans, and implementation remain synchronized;
* non-structural changes do not produce noise;
* sync-check tooling operates on **Vault-derived rules**, not path heuristics.

---

## Core Principle

A change is considered **knowledge-bearing** if it affects:

* system architecture;
* domain model;
* invariants or rules;
* cross-module protocols;
* data contracts;
* documented behavior;
* task intent, planning, or execution traceability (when applicable).

Plans are considered knowledge-bearing artifacts
**only when they are required by orchestration specification**.

Planning is NOT universally required.
When present, plans MUST be consistent and synchronized.

---

## Planning Responsibility Boundary

Plan requirement is defined by the orchestration specification.

Sync classification is responsible for:

* validating plan existence (if required);
* validating plan status;
* validating alignment with implementation and commits.

Sync classification MUST NOT:

* independently require plan creation;
* enforce planning based on ambiguity alone.

---

## Extended Principle: Planning Consistency

When a plan is required, the system MUST ensure:

* plan existence;
* plan status consistency;
* alignment between plan, implementation, and commits.

A task is considered **incomplete** if:

* a required plan is missing;
* plan status is not finalized;
* knowledge-bearing changes are not committed.

---

## Classification Model

All changes MUST be classified into one of four categories:

### 1. ALWAYS (Hard Fail)
Requires Knowledge Vault and/or Plan validation.

### 2. SOMETIMES (Soft Warning)
May require Knowledge Vault or Plan updates.

### 3. NEVER (Silent Pass)
No knowledge or plan impact.

### 4. SKIP (Mechanical Ignore)
Not relevant.

---

## Rule Group A — System Layers

| Layer          | Path                              | Classification | Notes |
|----------------|----------------------------------|----------------|------|
| Knowledge      | `knowledge/**`                   | ALWAYS         | Must stay consistent |
| Plans          | `knowledge/plans/**`             | ALWAYS         | Validate lifecycle if present |
| Rules          | `rules/**`                       | ALWAYS         | Source of invariants |
| Vault (media)  | `vault/**`                       | NEVER          | Binary/content |
| Docs (legacy)  | `Docs/**`                        | NEVER          | Deprecated |

---

## Plan Consistency Rules

### Plan Required

Sync-check MUST fail if:

* a plan is required by orchestration spec;
* AND no plan exists.

Sync-check MUST NOT require a plan independently.

If structured planning is detected in the task
AND no plan document exists
→ emit warning (not fail)

---

### Plan Absence Validity

Absence of a plan is valid if:

* orchestration spec does not require it;
* task is simple or direct;
* traceability is not lost.

In such cases, sync-check MUST NOT fail.

---

### Plan Status Validation

Sync-check MUST fail if:

* plan exists but has no status;
* plan remains `in_progress` after completion;
* plan is inconsistent with actual work.

---

### Plan–Implementation Alignment

Sync-check MUST warn or fail if:

* implementation exists but plan does not reflect it;
* plan says implemented but code is missing;
* implementation deviates without plan update.

---

### Plan–Commit Alignment

Sync-check MUST fail if:

* plan marked complete but no commits exist;
* knowledge changes are not committed;
* working tree is not clean.

---

## Conservative Classification

Ambiguous areas remain SOMETIMES.

Ambiguity MUST NOT force plan creation.

Instead:

* defer to orchestration spec;
* validate only if plan exists.

---

## Sync-Check Behavior

### ALWAYS

* block execution;
* require knowledge validation;
* require plan validation if applicable.

### SOMETIMES

* allow execution;
* emit warning;
* suggest validation.

### NEVER

* allow silently.

### SKIP

* ignore.

---

## Summary

This system ensures:

* Knowledge correctness
* Plan consistency (when required)
* Commit discipline

Plans are not enforced universally.

But when present, they MUST be:

* complete
* consistent
* aligned with implementation

Knowledge Vault remains the source of truth,
with plans as conditional intent artifacts.
