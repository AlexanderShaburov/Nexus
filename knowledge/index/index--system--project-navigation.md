---
type: index
scope: system
status: approved
created: 2026-04-18
updated: 2026-04-22
source_of_truth: true
tags: [index, navigation, routing]
---

# Project Navigation Index

This index is the entry point to the Knowledge Vault. It tells the agent **where to look first** when bootstrapping or when resolving a task.

The vault enforces the Nexus (formerly SOKI) lifecycle (Bootstrap → Decision → Execution → Exit) via three gates. The hooks under `.claude/hooks/` implement those gates.

---

## Read Priority (canonical order)

1. **invariants/** — non-negotiable constraints (MUST never be violated)
2. **architecture/** — what exists (system structure)
3. **specs/** — how it behaves (rules, flows, gate contracts)
4. **decisions/** — why it is designed this way
5. **patterns/** — reusable approaches
6. **plans/** — in-progress intent
7. **sessions/** — execution traces from prior sessions
8. **glossary/** — domain terminology

`bugs/`, `open-questions/`, `runbooks/`, `business/` are consulted on demand.

---

## Canonical System Specs

These specs define how the vault itself and the agent lifecycle are enforced. They MUST be read during Session Bootstrap.

- [Knowledge-Driven Task Orchestration](../specs/spec--system--knowledge-driven-task-orchestration.md) — the Retrieve/Ground/Sync contract
- [Session Bootstrap](../specs/spec--system--session-bootstrap.md) — how a session must initialize
- [Context Decision Gate](../specs/spec--system--context-decision-gate.md) — the mandatory KB-use decision at every turn
- [Exit Gate](../specs/spec--system--exit-gate.md) — the mandatory Closure Block at end of every turn
- [Knowledge Vault](../specs/spec--system--knowledge-vault.md) — canonical folder layout and semantic roles
- [Document Frontmatter](../specs/spec--system--document-frontmatter.md) — YAML contract for every doc

---

## Core Invariants

- [Lifecycle Gates](../invariants/invariant--system--lifecycle-gates.md) — Bootstrap, Decision Gate, Exit Gate are non-negotiable

---

## Architecture

- [Overall Structure](../architecture/architecture--system--overall-structure.md) — how the Nexus system is composed

---

## Runtime (hooks)

Hooks live outside the vault under `.claude/hooks/` and operate against runtime state in `.soki/`. They are **the enforcement layer** for the specs above — the specs are the contract, the hooks are the mechanism.

- `soki-bootstrap.py` — SessionStart, PreCompact
- `soki-prompt-gate.py` — UserPromptSubmit
- `soki-tool-gate.py` — PreToolUse
- `soki-exit-gate.py` — Stop

---

## Read-priority reminder for the agent

When consulting the vault, **do not** use `grep` as the primary tool. Use this index to locate the right document class first (invariant? spec? decision?), then read the document in full. Grep is a fallback, not a substitute for structural reading.
