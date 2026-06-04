---
type: spec
scope: system
status: approved
created: 2026-04-17
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [frontmatter, metadata, kb-system]
---

## Relations

- constrains:
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — every vault document must satisfy this contract.
- relates_to:
  - [Knowledge Graph Relations Specification](spec--system--knowledge-graph-relations.md) — relation declarations sit alongside frontmatter on every document.

---

# Document Frontmatter Specification

## Purpose

This document defines the **standardized YAML frontmatter structure** used across all knowledge base documents.

Frontmatter is a **mandatory control layer** for every document and is used for:
- classification
- routing
- validation
- lifecycle management
- knowledge synchronization

---

## Format

All documents MUST begin with a YAML frontmatter block:

```yaml
---
type: <string>
scope: <string>
status: <string>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
source_of_truth: <boolean>
tags: [<tag1>, <tag2>, ...]
---
```

---

## Fields Specification

### type (required)

Defines the document category.

Allowed values:
- spec
- plan
- invariant
- bug
- decision
- question
- index
- architecture

---

### scope (required)

Defines the domain or subsystem.

Examples:
- system
- backend
- frontend
- editor
- infrastructure
- domain-specific (project-defined)

---

### status (required)

Defines lifecycle state.

Allowed values:
- draft
- in-progress
- review
- approved
- deprecated

---

### created (required)

Format: YYYY-MM-DD

Represents initial creation date.

---

### updated (required)

Format: YYYY-MM-DD

Must be updated on every meaningful change.

---

### source_of_truth (required)

Boolean.

- true → canonical document
- false → derived/supporting document

---

### tags (optional but recommended)

List of keywords.

Used for:
- search
- grouping
- cross-linking

---

### knowledge_visibility (optional but recommended; extension field)

Defines the **review-visibility class** of the document — orthogonal to `status` (workflow maturity) and `source_of_truth` (authoritative status).

Allowed values:
- binding — implementation-binding, authoritative.
- development — active design work; not authoritative, but MUST be visible to architecture review, gap analysis, roadmap planning, and missing-spec analysis.
- historical — superseded, archived, or legacy; excluded from review by default.

When omitted, a conservative fallback applies (see `spec--system--knowledge-visibility.md` §"Fallback Mapping").

Invalid combinations (e.g. `knowledge_visibility: binding` with `source_of_truth: false`) MUST be flagged as errors and MUST NOT be silently normalized. Full rules: `spec--system--knowledge-visibility.md`.

---

## Rules

1. Frontmatter MUST be present in every document.
2. Field names are case-sensitive.
3. Unknown fields are not allowed unless explicitly extended by system spec.
4. Dates must follow ISO format.
5. source_of_truth must be explicitly set.

---

## Validation Rules

A document is considered valid if:

- All required fields are present
- All values match allowed formats
- type and status values are valid enums

---

## Extension Policy

Additional fields may be introduced only via:
- system-level spec update
- or project-level extension spec

---

## Example

```yaml
---
type: spec
scope: system
status: approved
created: 2026-04-17
updated: 2026-04-17
source_of_truth: true
knowledge_visibility: binding
tags: [frontmatter, metadata, kb-system]
---
```

### Example with development visibility

```yaml
---
type: plan
scope: system
status: draft
created: 2026-06-04
updated: 2026-06-04
source_of_truth: false
knowledge_visibility: development
tags: [roadmap, draft]
---
```

---

## Notes

Frontmatter is not optional metadata.

It is a **structural contract** that enables the knowledge-driven workflow.
