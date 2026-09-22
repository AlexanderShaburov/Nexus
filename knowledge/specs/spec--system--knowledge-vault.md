---
type: spec
scope: system
status: approved
created: 2026-04-18
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [knowledge-vault, structure, ontology, feedback]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — every vault document must satisfy the frontmatter contract.
- constrains:
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — the orchestration spec operates over this vault structure.
  - [Knowledge Graph Relations Specification](spec--system--knowledge-graph-relations.md) — the relation graph is layered on top of this structure.
- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — the vault is one of the runtime components.

---

# Knowledge Vault Specification

## Purpose

This document defines the **canonical structure of the project Knowledge Vault**.

It establishes:

- directory layout;
- semantic roles of each directory;
- allowed and forbidden content types;
- lifecycle of knowledge artifacts;
- rules for writing and reading documents.

This specification is **mandatory** for all agents and contributors.

---

## Core Principle

The vault is not a file system.

It is a **knowledge operating system**, where each directory represents a **semantic layer**.

Documents MUST be placed according to their meaning, not convenience.

---

## Root Structure

```
knowledge/
  .obsidian/
  architecture/
  bugs/
  business/
  decisions/
  feedback/
  glossary/
  index/
  invariants/
  open-questions/
  patterns/
  plans/
  runbooks/
  sessions/
  specs/
```

---

## Directory Specifications

---

### 📁 .obsidian/

#### Role
Obsidian configuration.

#### Allowed
- UI settings
- plugin configs

#### Forbidden
- any project knowledge

---

### 📁 architecture/

#### Role
Defines **system structure and design**.

#### Allowed
- components
- layers
- data models
- system boundaries

#### Forbidden
- behavior (belongs to specs)
- decisions (belongs to decisions)
- plans

---

### 📁 specs/

#### Role
Defines **expected system behavior**.

#### Allowed
- behavioral rules
- flows
- constraints on execution

#### Forbidden
- reasoning why (belongs to decisions)
- structural description (belongs to architecture)

---

### 📁 invariants/

#### Role
Defines **non-negotiable constraints**.

#### Rules
- MUST always be followed
- cannot be temporarily violated
- can only be changed via decision

---

### 📁 decisions/

#### Role
Stores **why the system is designed this way**.

#### Allowed
- alternatives
- reasoning
- trade-offs
- final decisions

---

### 📁 plans/

#### Role
Represents **future or in-progress work**.

#### Rules
- temporary
- not source of truth
- evolves into decisions or sessions

---

### 📁 sessions/

#### Role
Stores **execution traces of agent work**.

#### Rules
- written via Exit Gate
- must include:
  - actions
  - reasoning summary
  - outcomes

---

### 📁 feedback/

#### Role
Observations about the **Nexus system** made while using it in this project: bugs, wishes, praise. Written in the host, delivered upstream (`spec--system--feedback-channel.md`), never source of truth here.

#### Allowed
- `type: feedback` notes with `scope: nexus`

#### Forbidden
- anything about the project's own domain (that belongs to `bugs/`, `open-questions/`, `plans/`)
- edits to Nexus core files disguised as notes: a note *proposes*, the template *decides*

#### Note
Never owned or touched by the Nexus updater; the template's own `feedback/` holds only the format fixture.

---

### 📁 patterns/

#### Role
Reusable solutions.

#### Allowed
- conventions
- recurring approaches

---

### 📁 bugs/

#### Role
Tracks known issues.

#### Allowed
- bug descriptions
- reproduction steps

---

### 📁 open-questions/

#### Role
Unresolved problems.

#### Allowed
- questions
- uncertainties

---

### 📁 runbooks/

#### Role
Operational procedures.

#### Allowed
- deployment steps
- recovery procedures
- debugging guides

#### Note
Not conceptual knowledge — operational only.

---

### 📁 glossary/

#### Role
Defines domain terminology.

---

### 📁 index/

#### Role
Entry point to the vault.

#### Required file
- project navigation index

---

### 📁 business/

#### Role
Business context (optional).

#### Allowed
- stakeholders
- goals
- product definitions

---

## Lifecycle of Knowledge

```
plans → sessions → decisions
```

- plans define intent
- sessions capture execution
- decisions capture stable outcomes

---

## Read Priority

Agents MUST read in this order:

1. invariants
2. architecture
3. specs
4. decisions
5. others

---

## Writing Rules

Agents MUST:

- place documents in correct directory
- not mix concerns
- update `updated` field on change

---

## Naming Convention

All documents MUST follow:

```
<type>--<scope>--<name>.md
```

Lowercase, kebab-case. `<type>` MUST be one of the values enumerated in `spec--system--document-frontmatter.md` §"type", MUST equal the document's own `type:` field, and MUST match the directory's semantic role.

Examples:

- architecture--system--overall-structure.md
- spec--editor--media-editor-behavior.md
- decision--data--json-vault.md

### Generated document forms

Two classes of document in `sessions/` carry additional trailing segments because they are generated per occurrence:

- `session--<theme>--<YYYY-MM-DD>--<session-id8>.md` — written automatically by `nexus-session-writer.py`
- `summary--<theme>--<YYYY-MM-DD>.md` — hand-written session handoff summary

Both carry `type: session`. Full contract: `spec--system--document-frontmatter.md` §"Filename Contract".

---

## Validation Rules

A document is valid if:

- correct directory
- correct naming
- valid frontmatter
- matches semantic role

---

## Enforcement

Violations include:

- wrong directory
- mixed concerns
- missing frontmatter

Such documents are considered invalid.

---

## Summary

The vault is a structured system where:

- architecture defines WHAT EXISTS
- specs define HOW IT BEHAVES
- decisions define WHY
- invariants define WHAT MUST NEVER BREAK
- sessions define WHAT HAPPENED

This separation is mandatory for system integrity.
