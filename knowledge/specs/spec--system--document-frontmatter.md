---
type: spec
scope: system
status: approved
created: 2026-04-17
updated: 2026-04-22
source_of_truth: true
tags: [frontmatter, metadata, kb-system]
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
tags: [frontmatter, metadata, kb-system]
---
```

---

## Notes

Frontmatter is not optional metadata.

It is a **structural contract** that enables the knowledge-driven workflow.
