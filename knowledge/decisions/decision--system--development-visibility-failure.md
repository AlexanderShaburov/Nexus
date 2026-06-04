---
type: decision
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [decision, governance, visibility, review, post-mortem]
---

## Relations

- relates_to:
  - [Review Classification Invariant](../invariants/invariant--system--review-classification.md) — the invariant introduced as a result of this decision.
  - [Knowledge Visibility Specification](../specs/spec--system--knowledge-visibility.md) — the mechanism introduced as a result of this decision.
  - [Architecture Review Specification](../specs/spec--system--architecture-review.md) — the workflow introduced as a result of this decision.
  - [Document Frontmatter Specification](../specs/spec--system--document-frontmatter.md) — extended to register the new field.
  - [Development Visibility Migration Runbook](../runbooks/runbook--system--development-visibility-migration.md) — operationalizes the migration for existing projects.

---

# Decision: Development-Phase Knowledge Visibility Failure

## Context

The Nexus Knowledge Vault originally distinguished documents along two axes:

- **workflow maturity** — captured by `status` (draft / in-progress / review / approved / deprecated);
- **authoritative status** — captured by `source_of_truth` (boolean).

This was sufficient for distinguishing "what is currently true" from "what is being worked on" at the level of individual documents. It was **not** sufficient for the question that review tooling and human reviewers actually ask:

> "When I look for missing specifications, which documents must I consider as already covering a topic?"

## Failure Mode Observed

In an active Nexus-based project, a reviewer was asked to identify missing specifications and architecture gaps. The reviewer consulted only documents satisfying `status: approved` AND `source_of_truth: true` (the binding set).

Outcome:

- the reviewer reported a list of "missing" specifications;
- subsequent inspection found that several of those topics were already substantially covered by architecture drafts, roadmap drafts, design proposals, and in-review specifications;
- these documents were known by name and were sometimes even referenced from binding documents, but were **not read** because they fell outside the binding set;
- the resulting recommendations would have caused duplicate design work and divergent design tracks;
- trust in review output degraded.

This is a **governance bug** in the Knowledge Vault model, not a bug in any individual document.

## Root Cause

The vault model conflated two separable concepts:

1. **Is this document authoritative?** (answered by `source_of_truth` / `status: approved`)
2. **Must this document be considered during review and gap analysis?** (was implicitly answered by the same criterion, which is wrong)

Active design work is, by definition, not yet authoritative. But it represents real coverage of topics and MUST influence "what is missing?" analysis. Treating "not authoritative" as "invisible to review" produces phantom gaps.

## Decision

Introduce a third, explicit axis: **knowledge visibility**, with three classes:

- **binding** — authoritative, implementation-binding.
- **development** — active design work; not binding, but VISIBLE to review.
- **historical** — superseded, archived, legacy; excluded from review by default.

The mechanism is a new optional-but-recommended frontmatter field `knowledge_visibility` with a conservative fallback mapping for documents that lack the field. See `specs/spec--system--knowledge-visibility.md`.

The behavioural consequence is captured as a non-negotiable invariant in `invariants/invariant--system--review-classification.md` and operationalized in `specs/spec--system--architecture-review.md` (dual analysis: Binding State + Development State, with four-way gap classification).

## Alternatives Considered

### A. Extend the `status` enum (rejected)

Add new status values such as `architecture_draft`, `roadmap_draft`, `design_proposal`, `pending_promotion`.

- ✗ Inflates the workflow-maturity enum with values that are really about review visibility.
- ✗ Forces existing documents to be retagged to retain the same review behaviour.
- ✗ Conflates two orthogonal axes that the failure mode just proved should be separated.

### B. Use the `tags` field (rejected)

Add tags like `draft-visible`, `roadmap-active`.

- ✗ `tags` is unstructured and not validated; visibility is a control concern that needs validation.
- ✗ No way to express the binding/development/historical trichotomy as an enum.

### C. Add a `lifecycle_state` field (rejected)

Proposed values: `authoritative | developing | review | superseded`.

- ✗ Overlaps with `status` in name and semantics; risks confusion.
- ✗ The four values do not cleanly map onto the three review-visibility classes.

### D. Add a `knowledge_visibility` field (chosen)

- ✓ Names exactly the concern it controls (review visibility), orthogonal to `status` and `source_of_truth`.
- ✓ Three values map directly onto the three review classes.
- ✓ Conservative fallback keeps existing documents working without retrofit.
- ✓ Explicit override is available where the fallback is ambiguous.
- ✓ Invalid combinations are detectable, not silently normalized.

## Consequences

- One new frontmatter field is registered (`knowledge_visibility`).
- One new invariant is introduced (`review-classification`).
- Two new specs are introduced (`knowledge-visibility`, `architecture-review`).
- The session-bootstrap protocol gains a STEP 3 ("ACTIVE DESIGN TRACKS") that points the agent at development documents before review tasks.
- A migration runbook is provided for existing Nexus-based projects (`runbooks/runbook--system--development-visibility-migration.md`).
- No existing document is forced to change. The fallback mapping treats any non-approved, non-deprecated document as `development`, which is the correct conservative default.

## Trade-offs

- **Cost:** one new field, two new specs, one new invariant, one new runbook. Total surface area is small.
- **Benefit:** phantom missing-spec findings stop. Review output becomes auditable. Existing drafts and roadmap work stop being invisible.
- **Risk avoided:** treating drafts as binding (rejected explicitly; the spec forbids it).

## Status

Approved 2026-06-04.

## See Also

- `invariants/invariant--system--review-classification.md`
- `specs/spec--system--knowledge-visibility.md`
- `specs/spec--system--architecture-review.md`
- `runbooks/runbook--system--development-visibility-migration.md`
- `../../docs/development-visibility-patch-report.md`
