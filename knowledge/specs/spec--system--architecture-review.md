---
type: spec
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [spec, review, architecture, gap-analysis, roadmap]
---

## Relations

- depends_on:
  - [Knowledge Visibility Specification](spec--system--knowledge-visibility.md) — defines the three classes this review workflow ranges over.
- constrains:
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — review tasks must complete the dual analysis before declaring any gap.
- relates_to:
  - [Review Classification Invariant](../invariants/invariant--system--review-classification.md) — the non-negotiable rule this spec operationalizes.
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — review traversal uses the vault structure defined there.

---

# Architecture Review Specification

## Purpose

Define the mandatory workflow when an agent is asked to perform a **review task** over the Knowledge Vault.

This spec exists to prevent a recurring failure: reviewers consult only authoritative documents, miss design work that already exists in drafts or proposals, and report phantom gaps. See `invariants/invariant--system--review-classification.md` for the non-negotiable rule, and `decisions/decision--system--development-visibility-failure.md` for the case note.

---

## Trigger Conditions

The dual-analysis workflow below is triggered by any user request that asks the agent to:

- enumerate missing knowledge ("what specs are missing?");
- assess architectural completeness ("what gaps remain?");
- generate or extend a roadmap ("what should be implemented next?");
- review an architecture ("review this architecture");
- identify what documents need to be written;
- audit conformance between code and knowledge.

When triggered, the agent MUST execute **both** Analysis A and Analysis B **before** producing any gap or roadmap output.

---

## Analysis A — Binding State

Enumerate, by topic, what is currently approved and authoritative.

Inclusion rule:

- documents with `knowledge_visibility: binding` (explicit), OR
- documents matching the binding fallback (`status: approved` AND `source_of_truth: true`).

Output format:

```
## Binding State
- <topic>: <doc title> (<relative path>) — <one-line summary>
- ...
```

---

## Analysis B — Development State

Enumerate, by topic, what active design work already exists, even if not promoted.

Inclusion rule:

- documents with `knowledge_visibility: development` (explicit), OR
- documents matching the development fallback (anything not classified as binding and not classified as historical).

Specifically including:

- architecture drafts;
- roadmap drafts;
- design proposals;
- pending specifications;
- in-review documents;
- session-derived design documents (`knowledge/sessions/`);
- in-progress plans (`knowledge/plans/`).

Output format:

```
## Development State
- <topic>: <doc title> (<relative path>) — <status> — <one-line summary>
- ...
```

Historical documents (`knowledge_visibility: historical`, or `status: deprecated`, or tagged `archived` / `legacy` / `superseded`) are **EXCLUDED** from both analyses unless the user explicitly requests them.

---

## Gap Classification

After both analyses are complete, the agent enumerates findings. Every finding MUST be classified as exactly one of:

### 1. Truly Missing

No binding document exists, no development document exists, no roadmap / architecture draft / proposal covers the topic.

→ **Recommendation:** create a new draft or spec.

### 2. Exists As Draft

A development-class document covers the topic but is not yet promoted to binding.

→ **Recommendation:** review, complete, and promote. **Do NOT create a parallel new draft.**

### 3. Exists But Not Normalized

Content covering the topic exists in architecture, roadmap, session, or proposal documents but has not been extracted into a formal specification.

→ **Recommendation:** extract into a `spec--…` document; link via `supersedes:` or `depends_on:` relations as appropriate.

### 4. Superseded Gap

The finding is invalid because a newer binding or development document already covers the topic.

→ **Action:** drop the finding from the gap list; optionally note that older expectations are now superseded.

---

## Required Review Output Format

A review response MUST contain, in order:

```
## Binding State
<enumeration per Analysis A>

## Development State
<enumeration per Analysis B>

## Gap Classification
- <finding 1>
  - Class: <Truly Missing | Exists As Draft | Exists But Not Normalized | Superseded Gap>
  - Evidence: <which binding/development docs were searched; one-line citation>
  - Recommendation: <next action>
- <finding 2>
  - ...
```

A reviewer MUST NOT emit a "Specification X is missing" line without:

1. listing it under one of the four classes, AND
2. citing evidence (which documents were searched).

---

## Anti-Patterns (INVALID review output)

- "Specification X is missing" without classification.
- A gap list that examined only `status: approved` documents.
- A gap list that ignored `knowledge_visibility: development` documents.
- A recommendation to create a new spec when an `Exists As Draft` finding applies.
- A review that bundles binding and development findings without distinguishing them.
- A review that silently includes historical documents in the binding state.

---

## Discovery Procedure

The agent SHOULD discover development documents via:

1. `knowledge/plans/` — roadmaps and in-progress intent.
2. `knowledge/sessions/` — session-derived design notes.
3. Any `knowledge/specs/` or `knowledge/architecture/` document where `status` is not `approved`, OR `knowledge_visibility: development`.
4. Any `knowledge/open-questions/` content relevant to the topic.
5. Any `knowledge/decisions/` document with `status` of `draft`, `in-progress`, or `review`.

Discovery MUST use the navigation index and declared relations first; grep is a fallback.

---

## Interaction with the Knowledge Graph

When traversing the knowledge graph during review (per `spec--system--knowledge-graph-relations.md`), the agent MUST follow relations into development-class documents and not stop at the binding boundary. A binding document that `relates_to` an in-review proposal MUST cause that proposal to be considered.

---

## Sync Obligation After Review

If the review produces or identifies new design work:

- An `Exists But Not Normalized` finding SHOULD lead to extraction into a `spec--…` document (development class, status `draft`).
- An `Exists As Draft` finding SHOULD lead to a recommendation that the user authorize promotion.
- A `Truly Missing` finding SHOULD lead to creation of a draft (development class), not directly to a binding spec.

In all cases the Sync obligation from `spec--system--knowledge-driven-task-orchestration.md` applies.
