---
type: architecture
scope: system
status: approved
created: 2026-04-18
updated: 2026-04-22
source_of_truth: true
tags: [architecture, system, soki, lifecycle]
---

# Overall Structure (Nexus (formerly SOKI) System)

## Purpose

This document describes **what exists** in the Nexus system. It does not describe behavior (see specs) nor reasoning (see decisions).

---

## Components

### 1. Knowledge Vault (`knowledge/`)

A structured filesystem under `knowledge/` with one semantic role per directory (see `specs/spec--system--knowledge-vault.md`). Each document carries frontmatter defined by `specs/spec--system--document-frontmatter.md`.

Directories by role:

- `index/` — routing entry point
- `invariants/` — non-negotiable constraints
- `architecture/` — structural description (this file)
- `specs/` — behavioral contracts
- `decisions/` — rationale
- `patterns/`, `plans/`, `sessions/`, `bugs/`, `runbooks/`, `glossary/`, `open-questions/`, `business/`

### 2. Enforcement Runtime (`.claude/hooks/`)

Shell + Python scripts invoked by Claude Code at lifecycle events. They read and mutate `.soki/state.json` and inject `additionalContext` / `decision: block` JSON to steer the agent.

- `soki-bootstrap.py` — runs on `SessionStart` and `PreCompact`. Resets state, injects the Mandatory Startup Reading Set.
- `soki-prompt-gate.py` — runs on `UserPromptSubmit`. Resets per-turn state and injects Decision Gate + Exit Gate reminders. Hard-blocks prompts while bootstrap is pending unless the prompt is a read-only KB query.
- `soki-tool-gate.py` — runs on `PreToolUse`. While bootstrap pending, only `Read`/`Glob`/`Grep`/`LS` of `knowledge/` are allowed. Tracks read-ledger to auto-complete bootstrap. After bootstrap, non-read tools require a Decision Gate statement in the current turn.
- `soki-exit-gate.py` — runs on `Stop`. Parses transcript, validates Closure Block presence + field shape + dependency rules. Blocks completion with a `reason` on violation.

### 3. Runtime State (`.soki/`)

- `.soki/state.json` — per-session runtime state (bootstrap status, read-ledger, per-turn decision flag, prompt index). Ephemeral; regenerated at each `SessionStart`.
- `.soki/README.md` — explains the directory.

### 4. Project Instructions

- `CLAUDE.md` at project root — minimum project memory loaded automatically by Claude Code. It names the protocol and points to this architecture doc.

---

## Control Flow (lifecycle)

```
SessionStart / PreCompact
  └─> soki-bootstrap.py
        ├─ reset .soki/state.json (bootstrap = pending)
        └─ inject mandatory reading set into first turn context

UserPromptSubmit
  └─> soki-prompt-gate.py
        ├─ reset per-turn flags
        ├─ if bootstrap pending: inject bootstrap-first reminder
        └─ else: inject Decision Gate + Exit Gate contract

PreToolUse
  └─> soki-tool-gate.py
        ├─ if bootstrap pending: allow only read-tools on knowledge/
        ├─ if bootstrap pending and Read hits a required file: record; upgrade if complete
        └─ if bootstrap done and tool is mutating: require Decision Gate text in current turn

Stop
  └─> soki-exit-gate.py
        ├─ locate last user turn in transcript
        ├─ regex-match Closure Block in assistant text of that turn
        ├─ validate fields + dependency rules
        └─ block (decision=block) if violation
```

---

## Data Contracts

### State file shape (`.soki/state.json`)

```json
{
  "session_id": "...",
  "started_at": "ISO8601",
  "bootstrap": {
    "status": "pending | completed",
    "required_files": ["knowledge/index/...", "knowledge/specs/...", "knowledge/architecture/..."],
    "required_invariants_dir": "knowledge/invariants",
    "read_ledger": ["..."]
  },
  "turn": {
    "index": 0,
    "decision_gate_seen": false
  }
}
```

### Closure Block grammar (enforced by soki-exit-gate.py)

```
Closure Block:
- code changed: yes|no
- KB changed: yes|no
- session log written: yes|no
- writeback evaluation performed: yes|no
```

Dependency rules: if `code changed: yes` then `writeback evaluation performed: yes`. If `KB changed: no` the turn MUST include a justification (free-form text on a subsequent line starting with `KB unchanged because`).

### Decision Gate grammar (enforced by soki-tool-gate.py)

Must appear in the current turn's assistant text before any mutating tool call:

```
### Context Decision
KB consult required: YES | NO
Reasoning: <one or more sentences>
```

---

## Boundaries

What this system is NOT:
- It is not a planner. It does not decide task steps.
- It is not a code reviewer. It does not evaluate code correctness.
- It is not a permissions system. Tool permissions remain in `settings.local.json`.

What it is:
- A lifecycle enforcement layer that makes KB consultation, decision traceability, and writeback non-optional at session boundaries and turn boundaries.
