# Knowledge Sync Classification Specification

## Purpose

This specification defines how code, data, and documentation changes are classified
in terms of their **knowledge impact and synchronization requirements**.

The goal is to ensure that:

* architectural and behavioral changes are reflected in the Knowledge Vault;
* planning artifacts are consistently created, updated, and finalized;
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
* **task intent, planning, or execution traceability**.

A change is **not knowledge-bearing** if it affects only:

* presentation;
* styling;
* test verification;
* runtime artifacts;
* content within existing schemas.

---

## Extended Principle: Planning Consistency

In addition to knowledge classification, the system MUST ensure:

* plan existence for required tasks;
* plan status consistency;
* alignment between plan, implementation, and commits.

A task is considered **incomplete** if:

* required plan is missing;
* plan status is not finalized;
* knowledge-bearing changes are not committed.

---

## Classification Model

All changes MUST be classified into one of four categories:

### 1. ALWAYS (Hard Fail)

Changes that **always require Knowledge Vault and/or Plan validation or update**.

---

### 2. SOMETIMES (Soft Warning)

Changes that **may require Knowledge Vault or Plan updates**, depending on context.

---

### 3. NEVER (Silent Pass)

Changes that **never require Knowledge Vault or Plan updates**.

---

### 4. SKIP (Mechanical Ignore)

Changes that are **not relevant to classification**.

---

## Rule Group A — System Layers

| Layer          | Path                                                    | Classification | Notes                                      |
| -------------- | ------------------------------------------------------ | -------------- | ------------------------------------------ |
| Vault (media)  | `vault/arts/**`, `vault/hopper/**`, `vault/streams/**` | NEVER          | Binary assets                              |
| Vault (data)   | `vault/json/**`                                        | SOMETIMES      | Schema vs content not distinguishable      |
| Knowledge      | `knowledge/**`                                         | ALWAYS         | Must stay consistent                       |
| Plans          | `knowledge/plans/**`                                   | ALWAYS         | Plan lifecycle MUST be validated           |
| Rules          | `rules/**`                                             | ALWAYS         | Source of invariants                       |
| Docs (legacy)  | `Docs/**`                                              | NEVER          | Non-authoritative (deprecated for plans)   |
| Infrastructure | `docker/**`                                            | SOMETIMES      | May affect architecture                    |

---

## Rule Group B — Frontend Layering (FSD)

(unchanged except interpretation expanded)

| Path                                             | Classification | Rationale                                    |
| ------------------------------------------------ | -------------- | -------------------------------------------- |
| `entities/{art,block,stream,event,homeDoc}/**`   | ALWAYS         | Domain model is fixed and controlled         |
| `entities/* (non-domain)`                        | SOMETIMES      | Supporting contracts                         |
| `shared/nav/**`                                  | ALWAYS         | Journey protocol invariant                   |
| `shared/state/**`                                | ALWAYS         | Store hierarchy = architecture               |
| `features/*/session/**`, `features/*/context/**` | SOMETIMES      | Control plane logic                          |
| `features/*/api/**`                              | SOMETIMES      | API contracts                                |
| `features/*/ui/**`                               | NEVER          | UI only                                      |
| `shared/ui/**`                                   | NEVER          | UI primitives                                |
| `shared/galleryLayouts/**`                       | NEVER          | Presentation only                            |
| `shared/lib/**`                                  | SOMETIMES [C]  | Mixed logic                                  |
| `app/router.tsx`                                 | ALWAYS         | Architecture                                 |
| `app/** (excluding router)`                      | SOMETIMES      | Providers                                    |
| `pages/admin/**`                                 | SOMETIMES [C]  | Mixed                                        |
| `pages/public/**`                                | SOMETIMES [C]  | Mixed                                        |
| `*.css`                                          | NEVER          | Styling                                      |
| `*.test.ts`, `__tests__/**`                      | NEVER          | Tests                                        |

---

## Rule Group C — Backend

(без изменений по сути)

| Path                           | Classification | Rationale            |
| ------------------------------ | -------------- | -------------------- |
| `admin-backend/app/models/**`  | ALWAYS         | API contracts        |
| `admin-backend/app/repos/**`   | ALWAYS         | Storage patterns     |
| `admin-backend/app/routers/**` | ALWAYS         | Endpoints            |
| `admin-backend/app/main.py`    | SOMETIMES      | Wiring               |

---

## Rule Group D — Domain and Protocol Invariants

(без изменений логики)

| Area            | Path                                           | Classification | Source |
| --------------- | ---------------------------------------------- | -------------- | ------ |
| Domain entities | `entities/{art,block,stream,event,homeDoc}/**` | ALWAYS         | invariants |
| Journey system  | `shared/nav/**`                                | ALWAYS         | invariants |
| State system    | `shared/state/**`                              | ALWAYS         | invariants |
| Data contracts  | backend                                        | ALWAYS         | decisions |

---

## Rule Group E — Documentation

### Updated Policy

Plans are NO LONGER treated as documentation noise.

| Pattern                                | Classification | Notes                                  |
| -------------------------------------- | -------------- | -------------------------------------- |
| `knowledge/plans/**`                   | ALWAYS         | Core planning system                   |
| `Docs/plans/**`                        | NEVER          | Deprecated                             |
| Blogs, logs, snapshots                 | NEVER          | Informational                          |
| Specs / architecture / contracts docs  | SOMETIMES      | May define behavior                    |
| Other Docs                             | SOMETIMES [C]  | Conservative default                   |

---

## Plan Consistency Rules (NEW)

These rules apply independently of path-based classification.

### Plan Required

Sync-check MUST fail if:

* task is classified as non-trivial;
* AND no plan exists when required by orchestration spec.

---

### Plan Status Validation

Sync-check MUST fail if:

* plan exists but has no status;
* plan is left in `in_progress` after task completion;
* plan is inconsistent with actual work.

---

### Plan–Implementation Alignment

Sync-check MUST warn or fail if:

* major implementation exists but plan does not reflect it;
* plan says implemented but code is missing;
* implementation deviates without plan update.

---

### Plan–Commit Alignment

Sync-check MUST fail if:

* plan step is marked completed but no commits exist;
* knowledge changes exist but are not committed;
* working tree is not clean after knowledge-bearing work.

---

## Conservative Classification [C]

(оставляем, но добавляем про планы)

Ambiguous areas remain SOMETIMES:

* `shared/lib/**`
* `pages/**`
* `vault/json/**`
* `docker/**`
* unspecified Docs

Additionally:

* ambiguity in planning necessity MUST resolve toward requiring a plan.

---

## Mechanical Rules (SKIP)

(без изменений)

---

## Sync-Check Behavior

### ALWAYS

* block execution;
* require Knowledge Vault validation/update;
* require Plan validation/update if applicable;
* require commit validation.

---

### SOMETIMES

* allow execution;
* emit warning;
* suggest checking:
  * knowledge updates
  * plan necessity
  * commit consistency

---

### NEVER

* allow execution silently.

---

### SKIP

* ignore.

---

## Explainability Requirement

Every classification MUST explain:

* which rule group triggered;
* whether plan validation was required;
* whether commit validation was required;
* which Vault document defines the rule.

---

## Limitations

* Path-based classification cannot detect:
  * missing plans;
  * plan correctness;
  * semantic alignment between plan and implementation;
* commit detection depends on external git state;
* some planning decisions remain heuristic.

---

## Future Improvements

* plan metadata validation (status, timestamps, links);
* commit-to-plan linking;
* semantic diff between plan and implementation;
* automatic detection of “non-trivial tasks”;
* linking plans ↔ ADR ↔ sessions automatically.

---

## Summary

This system extends classification from:

→ “Does this require knowledge update?”

to:

→ “Is knowledge, planning, implementation, and commits fully synchronized?”

The system enforces:

* Knowledge correctness
* Plan completeness
* Commit discipline

A task is considered complete only when:

* knowledge is updated;
* plan is valid and finalized;
* implementation is committed.

Knowledge Vault remains the source of truth,
but now includes **intent (plans)** in addition to structure and behavior.