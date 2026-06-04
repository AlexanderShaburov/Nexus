---
type: spec
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [spec, knowledge-visibility, lifecycle, frontmatter, review]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — this spec registers the `knowledge_visibility` field on top of the frontmatter contract.
- constrains:
  - [Architecture Review Specification](spec--system--architecture-review.md) — the review workflow ranges over the three classes defined here.
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — Retrieve must cover the binding AND development classes; historical is excluded by default.
- relates_to:
  - [Review Classification Invariant](../invariants/invariant--system--review-classification.md) — the non-negotiable rule this spec operationalizes.

---

# Knowledge Visibility Specification

## Purpose

Define the three **knowledge visibility classes** used to decide which documents must be considered during architecture review, gap analysis, roadmap planning, and missing-specification analysis.

This spec exists because the existing fields are insufficient on their own:

- `status` (draft / in-progress / review / approved / deprecated) describes **workflow maturity**.
- `source_of_truth` (boolean) describes **authoritative status**.

Neither directly answers the question that review tooling actually asks:
> **"Must this document be considered when assessing what exists or what is missing?"**

`knowledge_visibility` answers that question with one of three values.

---

## The Three Classes

### 1. Binding (Authoritative)

- Implementation-binding.
- Used for conformance checks.
- Treated as source of truth.

Required frontmatter shape for an **explicit** binding document:

```yaml
status: approved
source_of_truth: true
knowledge_visibility: binding
```

---

### 2. Development (Active Design)

- **Not** implementation-binding.
- Represents active design work that has not (yet) been promoted to authoritative status.
- **MUST be visible to** architecture reviews, gap analysis, roadmap planning, and "missing specification" analysis.

Typical documents:

- architecture drafts;
- roadmap drafts;
- design proposals;
- pending specifications;
- in-review documents;
- session-derived design documents.

Required frontmatter shape for an **explicit** development document:

```yaml
status: <draft | in-progress | review>
source_of_truth: false
knowledge_visibility: development
```

---

### 3. Historical

- Superseded, archived, or legacy.
- **Excluded** from review by default.
- Included only when explicitly requested (audit, archaeology, regression triage).

Required frontmatter shape for an **explicit** historical document:

```yaml
status: deprecated
source_of_truth: false
knowledge_visibility: historical
```

---

## Frontmatter Field

```yaml
knowledge_visibility: binding | development | historical
```

- Type: string enum, exactly one of the three values above.
- Cardinality: optional but **recommended** for new documents.
- Mutability: changes when the document is promoted, demoted, or retired. `updated:` MUST be bumped.

The field is registered as an allowed extension in `spec--system--document-frontmatter.md` per its Extension Policy.

---

## Fallback Mapping (when the field is absent)

If `knowledge_visibility` is absent, the visibility class is computed from existing fields. The mapping is conservative — anything not clearly binding and not clearly historical resolves to **development**, which guarantees that draft / in-review work remains visible to review:

| Condition (evaluated top to bottom; first match wins) | Inferred class |
|---|---|
| `status: approved` AND `source_of_truth: true` | binding |
| `status: deprecated` | historical |
| any tag in `{archived, legacy, superseded, historical}` | historical |
| otherwise (incl. `draft`, `in-progress`, `review`) | development |

Tooling and agents MUST apply this fallback consistently.

---

## Override and Validation Rules

1. An **explicit** `knowledge_visibility` value ALWAYS overrides the fallback mapping.
2. The following combinations are **invalid** and MUST be flagged as errors. They MUST NOT be silently normalized:
   - `knowledge_visibility: binding` with `source_of_truth: false`
   - `knowledge_visibility: historical` with `source_of_truth: true`
   - `knowledge_visibility: binding` with `status: deprecated`
   - `knowledge_visibility: binding` with `status: draft` or `status: in-progress`
   - `knowledge_visibility: development` with `source_of_truth: true`
3. Validation tooling (when present) MUST report invalid combinations as **errors**, not warnings.
4. Validation tooling MUST NOT auto-correct invalid combinations. Resolution is a human or agent judgement call: either correct the visibility field, or correct the workflow state (`status` / `source_of_truth`). The agent MUST surface the conflict and ask, not guess.
5. A missing `knowledge_visibility` field is NOT a validation error — the fallback applies. Surfacing a fix recommendation ("consider declaring `knowledge_visibility` explicitly") is permitted.

---

## Promotion and Demotion

- **Development → Binding**: promote only after the document has been reviewed and accepted. Set `status: approved`, `source_of_truth: true`, `knowledge_visibility: binding`. Bump `updated:`. If the new binding supersedes an older binding doc, add a `supersedes:` relation and demote the older doc to `historical`.
- **Binding → Historical**: only via a `decision--…` document that records the reason. Set `status: deprecated`, `source_of_truth: false`, `knowledge_visibility: historical`. Keep the file (do not delete).
- **Development → Historical**: when a draft is abandoned. Set `status: deprecated`, `source_of_truth: false`, `knowledge_visibility: historical`, and add a brief note to the body explaining why it was abandoned.

The agent MUST NOT promote a development document to binding without explicit user authorization.

---

## Examples

### Binding architecture document

```yaml
---
type: architecture
scope: system
status: approved
created: 2026-04-18
updated: 2026-05-04
source_of_truth: true
knowledge_visibility: binding
tags: [architecture, system]
---
```

### Development roadmap draft

```yaml
---
type: plan
scope: system
status: draft
created: 2026-06-04
updated: 2026-06-04
source_of_truth: false
knowledge_visibility: development
tags: [roadmap, draft, planning]
---
```

### Historical superseded decision

```yaml
---
type: decision
scope: system
status: deprecated
created: 2025-12-01
updated: 2026-06-04
source_of_truth: false
knowledge_visibility: historical
tags: [decision, superseded]
---
```

---

## What this spec does NOT do

- It does NOT change the meaning of `status` or `source_of_truth`.
- It does NOT introduce new directory roles in the vault.
- It does NOT promote any draft to authoritative status.
- It does NOT permit drafts to be relied on for conformance.

What it DOES do is make visible — to architecture review and gap analysis — work that was already present in the vault but was being skipped because it was not authoritative.
