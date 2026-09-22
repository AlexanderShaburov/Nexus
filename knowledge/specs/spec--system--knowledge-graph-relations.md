---
type: spec
scope: system
status: approved
created: 2026-05-04
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [knowledge, graph, relations]
governs:
  - knowledge-graph
---

## Relations

- depends_on:
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — every document this spec governs lives in the vault structure defined there.
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — relation declarations sit alongside the mandatory frontmatter contract.
- constrains:
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — the Retrieve step must traverse declared relations as defined here.

---

# Knowledge Graph Relations Specification

## Purpose

Define how Knowledge Vault documents declare, maintain, and use relations
between knowledge artifacts.

## Core Principle

Every durable knowledge document MUST expose its meaningful relations
to other knowledge documents.

This requirement applies to all non-trivial knowledge documents,
including specifications.

A relation is valid only if it helps Claude:
- understand context;
- discover constraints;
- follow decisions;
- avoid contradiction;
- update durable knowledge correctly.

## Relation Types

- depends_on — this document cannot be correctly understood without the 
target.
- constrains — this document limits or governs the target.
- implements — this document describes implementation of a spec/decision.
- supersedes — this document replaces older knowledge.
- conflicts_with — this document contradicts or challenges another 
document.
- relates_to — weak relation; use sparingly.

## Required Section

Documents MUST include:

## Relations

- depends_on: [Document title](relative/path.md) — why this relation 
matters.
- constrains: ...
- supersedes: ...

Structural documents (e.g. index) MAY omit relations.
All other documents MUST include at least one valid relation.

## Relation Rules

Claude MUST NOT create relations by filename similarity alone.

Claude MUST create a relation only when:
- the target is explicitly mentioned;
- the target defines a concept used here;
- the target constrains this document;
- the target is superseded by this document;
- the target is required to understand the task context.

Claude SHOULD limit relations to 3–7 high-value links per document.
A document without relations is considered incomplete.

## Ingest Requirement

When ingesting a project into the Knowledge Vault, Claude MUST:

1. extract entities, modules, processes, decisions, constraints, and 
specs;
2. match them against existing Knowledge Vault documents;
3. propose candidate relations;
4. add validated relations to created or updated documents;
5. report unresolved entities as missing knowledge candidates.

## Sync Requirement

When updating durable knowledge, Claude MUST also evaluate whether 
relations
need to be added, removed, or corrected.
