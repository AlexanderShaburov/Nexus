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
- [Nexus Update](../specs/spec--system--nexus-update.md) — version identity, ownership manifest, install baseline, upstream cache, three-way table, `apply`, the core freeze in hosts, exit codes

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
- `nexus-update-check.py` — SessionStart; in a host with a baseline, one throttled `ls-remote` and one line of context when a newer Nexus tag exists (architecture §2e, spec [Nexus Update](../specs/spec--system--nexus-update.md) §7)

## Runtime (tools)

- `tools/validate-vault.py` — the vault rule set and its CLI. Holds the machine-checkable form of the frontmatter, naming and visibility contracts; `nexus-vault-validator.py` is a thin adapter over it. Run `python3 tools/validate-vault.py` before declaring a vault edit finished, `--selftest` after changing a rule.
- `tools/nexus-decide.py` — the Context Decision claim: the tool-carried form of the per-turn decision (context-decision-gate spec, Form A). Validates and prints; decides nothing. Design origin: [Plan: Context Decision claim](../plans/plan--system--context-decision-claim.md) (development class).
- `tools/nexus-update.py` — the updater: `manifest generate|verify` keeps `nexus.manifest.json` (the list of Nexus-owned paths) in sync with the tree; `baseline` records `.nexus/installed.json` in a host; `status` compares a host with its baseline; `check` asks upstream for a newer version; `plan` prints the three-way table; `apply` adopts a version with backups and validation; `--selftest` proves the rules. Architecture §2d. Contract: [Nexus Update](../specs/spec--system--nexus-update.md). Design origin: [Plan: Nexus self-update](../plans/plan--system--nexus-self-update.md) (development class).

## Plans (development class)

- [Context Decision claim via tool call](../plans/plan--system--context-decision-claim.md) — why the gate accepts a Bash claim alongside the text block; rollout order.
- [Nexus self-update](../plans/plan--system--nexus-self-update.md) — Phase 0 proposal: ownership manifest, three-way comparison, upstream fetch, SessionStart notifier, CLI, retrofit path, core freeze in hosts. Status: proposed.
- [Nexus feedback channel](../plans/plan--system--nexus-feedback-channel.md) — how hosts send observations about Nexus upstream without push rights: `feedback` notes in the host vault, local mailbox in the updater cache, deferred GitHub-issue transport. Status: proposed.

---

## Read-priority reminder for the agent

When consulting the vault, **do not** use `grep` as the primary tool. Use this index to locate the right document class first (invariant? spec? decision?), then read the document in full. Grep is a fallback, not a substitute for structural reading.
