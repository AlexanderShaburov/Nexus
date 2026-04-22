---

id: adr--system--rename-soki-to-nexus
type: decision
status: accepted
created: 2026-04-22
tags:

* system
* naming
* architecture
* knowledge-vault

---

# ADR — Rename SOKI to Nexus

## Context

The system currently referred to as **SOKI** represents the core mechanism 
for:

* knowledge-driven task orchestration
* structured interaction with the Knowledge Vault
* enforcement of architectural constraints and invariants
* integration of hooks, specs, and operational protocols

However, the name **SOKI**:

* is not self-explanatory
* lacks semantic clarity for new projects and contributors
* does not reflect the system’s role as a central coordination layer

At the current stage, the system is evolving into a reusable, portable 
architecture intended to be deployed across multiple projects.

This creates a need for a clearer, more expressive, and more stable 
canonical name.

---

## Decision

The system formerly known as **SOKI** is renamed to:

> **Nexus**

From this point forward:

* **Nexus** is the canonical name of the system
* **SOKI** is considered a legacy alias

---

## Rationale

The name **Nexus** was chosen because it:

* reflects the system’s role as a **central connection point** between:

  * knowledge
  * execution
  * constraints
  * agent behavior
* is **short, memorable, and semantically meaningful**
* scales well as a **product/system name**
* avoids ambiguity and improves communication

---

## Scope

### Included in rename

The following elements MUST adopt the new name **Nexus**:

* system-level documentation
* specifications (specs)
* onboarding and bootstrap descriptions
* index and navigation documents
* protocol descriptions
* conceptual references to the system

---

### Excluded from immediate rename

The following elements are NOT automatically renamed in this phase:

* file names and directory names
* script names
* hook identifiers
* internal string constants used by automation
* existing paths referenced in tooling

These elements may be migrated in a future phase if needed.

---

## Migration Strategy

### Phase 1 — Semantic Transition (current)

* Introduce **Nexus** as the canonical name

* Update key documents to use:

  > “Nexus (formerly SOKI)”

* Ensure all new documents use **Nexus**

* Preserve compatibility with existing references to **SOKI**

---

### Phase 2 — Gradual Replacement (future)

* Evaluate necessity of renaming:

  * files
  * scripts
  * directories
* Perform controlled updates only where safe
* Avoid breaking:

  * hooks
  * automation
  * path-based logic

---

### Phase 3 — Deprecation (optional)

* Remove references to **SOKI** once:

  * no active dependencies remain
  * all key documents and flows are migrated

---

## Consequences

### Positive

* improved clarity of system purpose
* better onboarding experience
* stronger conceptual model
* readiness for reuse across projects

---

### Risks

* temporary dual terminology (SOKI / Nexus)
* potential confusion if migration is inconsistent
* risk of breaking automation if renaming is done prematurely

---

## Constraints

* Do NOT perform global search-and-replace across the repository
* Do NOT rename paths or identifiers without explicit validation
* Maintain backward compatibility during transition phase

---

## Status

Accepted and effective immediately.

---

