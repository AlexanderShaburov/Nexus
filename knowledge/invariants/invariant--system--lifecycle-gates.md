---
type: invariant
scope: system
status: approved
created: 2026-04-18
updated: 2026-04-19
source_of_truth: true
tags: [invariant, lifecycle, gates, soki]
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

- `.claude/hooks/soki-bootstrap.py`
- `.claude/hooks/soki-prompt-gate.py`
- `.claude/hooks/soki-tool-gate.py`
- `.claude/hooks/soki-exit-gate.py`
