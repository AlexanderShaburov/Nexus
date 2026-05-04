---
type: invariant
scope: system
status: approved
created: 2026-04-18
updated: 2026-05-04
source_of_truth: true
tags: [invariant, lifecycle, gates, nexus]
---

## Relations

- constrains:
  - [Session Bootstrap Specification](../specs/spec--system--session-bootstrap.md) — bootstrap is the first non-negotiable gate.
  - [Context Decision Gate Specification](../specs/spec--system--context-decision-gate.md) — the per-turn gate is non-negotiable.
  - [Exit Gate Specification](../specs/spec--system--exit-gate.md) — the closure gate is non-negotiable.
- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — runtime hooks realize these gates.

---

# Invariant: Lifecycle Gates

## Statement

The agent MUST pass through three gates in every session. These gates are **non-negotiable**.

1. **Session Bootstrap** — every session or post-compaction context MUST begin by reading the Mandatory Startup Reading Set and emitting the `Session Bootstrap Completed` confirmation block.
2. **Context Decision Gate** — every user turn MUST contain an explicit Context Decision statement (`KB consult required: YES | NO` with justification) before any mutating tool is invoked.
3. **Exit Gate** — every turn MUST end with a valid Closure Block. Dependency rules (code→writeback, knowledge-bearing→KB update) MUST be satisfied.

## Consequences of violation

- Bootstrap missing → mutating tools are blocked at PreToolUse.
- Decision Gate missing in the current turn → mutating tools are blocked at PreToolUse.
- Exit Gate missing or malformed → the Stop hook blocks turn completion and feeds a corrective prompt back.

## Amendment rule

This invariant MAY be relaxed only via a formal `decision--system--…` document that records the reasoning and trade-off. No temporary suspension is permitted.

## Pointer to enforcement

- `.claude/hooks/nexus-bootstrap.py`
- `.claude/hooks/nexus-prompt-gate.py`
- `.claude/hooks/nexus-tool-gate.py`
- `.claude/hooks/nexus-exit-gate.py`
