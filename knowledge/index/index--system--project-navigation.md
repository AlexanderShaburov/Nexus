---
type: index
scope: system
status: approved
created: 2026-04-18
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [index, navigation, routing]
---

# Project Navigation Index

This index is the entry point to the Knowledge Vault. It tells the agent **where to look first** when bootstrapping or when resolving a task.

The vault enforces the Nexus lifecycle (Bootstrap → Decision → Execution → Exit) via three gates. The hooks under `.claude/hooks/` implement those gates.

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
- [Knowledge Visibility](../specs/spec--system--knowledge-visibility.md) — the three review-visibility classes (binding / development / historical) and the `knowledge_visibility` field
- [Architecture Review](../specs/spec--system--architecture-review.md) — mandatory dual-analysis workflow (Binding State + Development State) and four-way gap classification

---

## Core Invariants

- [Lifecycle Gates](../invariants/invariant--system--lifecycle-gates.md) — Bootstrap, Decision Gate, Exit Gate are non-negotiable
- [Review Classification](../invariants/invariant--system--review-classification.md) — no gap may be reported without examining both binding and development knowledge; every gap must be classified

---

## Architecture

- [Overall Structure](../architecture/architecture--system--overall-structure.md) — how the Nexus system is composed

---

## Runtime (hooks)

Hooks live outside the vault under `.claude/hooks/` and operate against runtime state in `.nexus/`. Structural description: [Overall Structure](../architecture/architecture--system--overall-structure.md).

**Enforcement layer** — these realize the lifecycle gates; the specs are the contract, the hooks are the mechanism:

- `nexus-bootstrap.py` — SessionStart, PreCompact
- `nexus-prompt-gate.py` — UserPromptSubmit
- `nexus-tool-gate.py` — PreToolUse
- `nexus-exit-gate.py` — Stop

**Non-enforcing** — part of the runtime, but they gate nothing and block nothing:

- `nexus-session-writer.py` — Stop; archives the transcript to `sessions/` (architecture §2a)
- `nexus-vault-validator.py` — PostToolUse; advisory frontmatter validation of a document just written (architecture §2b)

## Runtime (tools)

- `tools/validate-vault.py` — the vault rule set and its CLI. Holds the machine-checkable form of the frontmatter, naming and visibility contracts; `nexus-vault-validator.py` is a thin adapter over it. Run `python3 tools/validate-vault.py` before declaring a vault edit finished, `--selftest` after changing a rule.

---

## Read-priority reminder for the agent

When consulting the vault, **do not** use `grep` as the primary tool. Use this index to locate the right document class first (invariant? spec? decision?), then read the document in full. Grep is a fallback, not a substitute for structural reading.
