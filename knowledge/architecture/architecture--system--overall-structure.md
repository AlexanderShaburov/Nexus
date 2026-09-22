---
type: architecture
scope: system
status: approved
created: 2026-04-18
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [architecture, system, nexus, lifecycle]
---

## Relations

- depends_on:
  - [Knowledge Vault Specification](../specs/spec--system--knowledge-vault.md) — the vault is one of the components described here.
- implements:
  - [Session Bootstrap Specification](../specs/spec--system--session-bootstrap.md) — the bootstrap hook described here is the runtime realization of this spec.
  - [Context Decision Gate Specification](../specs/spec--system--context-decision-gate.md) — the prompt/tool gates here realize this spec.
  - [Exit Gate Specification](../specs/spec--system--exit-gate.md) — the stop hook here realizes this spec.
- relates_to:
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — the three non-negotiable gates this architecture enforces.

---

# Overall Structure (Nexus System)

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

Shell + Python scripts invoked by Claude Code at lifecycle events. They read and mutate `.nexus/state.json` and inject `additionalContext` / `decision: block` JSON to steer the agent.

- `nexus-bootstrap.py` — runs on `SessionStart` and `PreCompact`. Resets state, injects the Mandatory Startup Reading Set.
- `nexus-prompt-gate.py` — runs on `UserPromptSubmit`. Resets per-turn state and injects Decision Gate + Exit Gate reminders. Hard-blocks prompts while bootstrap is pending unless the prompt is a read-only KB query.
- `nexus-tool-gate.py` — runs on `PreToolUse`. While bootstrap pending, only read-only tools (`Read`/`Glob`/`Grep`/`LS`/`NotebookRead`) are allowed, on any path — reads cannot mutate, so the gate constrains tool class, not location. Tracks read-ledger to auto-complete bootstrap. After bootstrap, non-read tools require a Decision Gate statement in the current turn.
- `nexus-exit-gate.py` — runs on `Stop`. Parses transcript, validates Closure Block presence + field shape + dependency rules. Blocks completion with a `reason` on violation.

### 2a. Session Archival (`.claude/hooks/nexus-session-writer.py`)

A **non-enforcing** hook registered on the same `Stop` event as the exit gate. It is part of the runtime but not part of the enforcement layer: it evaluates no contract, emits nothing on stdout, and swallows its own exceptions so it can never block turn completion or interfere with `nexus-exit-gate.py`.

Behavior:

- reads the session transcript and reconstructs `(user prompt, assistant text)` turn pairs, discarding tool calls, tool results, thinking blocks, `<system-reminder>` and `<command-*>` tags;
- writes `knowledge/sessions/session--<theme>--<YYYY-MM-DD>--<session-id8>.md`, rewriting the same file in place on every `Stop` (idempotent per session);
- reads the theme from `.nexus/session-theme.txt` and tracks the current target in `.nexus/session-file.txt`; when the theme changes **within the same session** the existing file is renamed rather than duplicated, so one session stays one document. The marker is **session-scoped** (`{"session_id", "path"}`): it outlives the session that wrote it, so an unscoped marker would let the next session claim the previous session's archive and overwrite it. A rename requires a `session_id` match, and never clobbers an existing target;
- preserves the original `created:` value across rewrites and bumps `updated:`.

Emitted documents carry `type: session`, `status: draft`, `source_of_truth: false`, `knowledge_visibility: historical`. They are an audit trail, not authoritative knowledge, and are distinct from the hand-written `summary--<theme>--<date>.md` handoff documents.

### 2b. Vault Validation (`tools/validate-vault.py` + `.claude/hooks/nexus-vault-validator.py`)

The frontmatter contract is machine-checked rather than left to agent discipline. The rules had drifted from the vault for months before a manual audit caught it; this closes that loop.

- `tools/validate-vault.py` is the **single source of truth for the rules** and the user-facing CLI. It codifies `spec--system--document-frontmatter.md`, the naming convention in `spec--system--knowledge-vault.md`, and the invalid-combination table in `spec--system--knowledge-visibility.md`. Stdlib only; its frontmatter parser accepts exactly the YAML subset the spec permits. Findings carry stable codes (`FM…` frontmatter, `VS…` visibility, `NM…` naming, `LK…` links). Errors exit 1, warnings exit 0 unless `--strict`. `--selftest` proves every rule fires against fixtures.
- `.claude/hooks/nexus-vault-validator.py` is a thin `PostToolUse` adapter for `Edit`/`Write`/`MultiEdit`/`NotebookEdit`. It validates the single document just written, if it lives under `knowledge/`, and injects the findings as `additionalContext` so the problem surfaces while the edit is still in working context. Silent when the document is clean.

The hook is **advisory and non-enforcing**. `PostToolUse` fires after the write, so it cannot prevent one; and neither layer ever edits a document — `spec--system--knowledge-visibility.md` rule 4 requires invalid combinations to be surfaced for judgement, not silently normalized.

### 3. Runtime State (`.nexus/`)

- `.nexus/state.json` — per-session runtime state (bootstrap status, read-ledger, per-turn decision flag, prompt index). Ephemeral; regenerated at each `SessionStart`. Gitignored.
- `.nexus/session-theme.txt` — optional single-line theme slug used by the session writer to name the archive file.
- `.nexus/session-file.txt` — JSON `{"session_id", "path"}` identifying the archive the session writer currently owns, so a theme change renames instead of forking, and a *different* session never renames it.
- `.nexus/README.md` — explains the directory.

### 4. Project Instructions

- `CLAUDE.md` at project root — minimum project memory loaded automatically by Claude Code. It names the protocol and points to this architecture doc.

---

## Control Flow (lifecycle)

```
SessionStart / PreCompact
  └─> nexus-bootstrap.py
        ├─ reset .nexus/state.json (bootstrap = pending)
        └─ inject mandatory reading set into first turn context

UserPromptSubmit
  └─> nexus-prompt-gate.py
        ├─ reset per-turn flags
        ├─ if bootstrap pending: inject bootstrap-first reminder
        └─ else: inject Decision Gate + Exit Gate contract

PreToolUse
  └─> nexus-tool-gate.py
        ├─ if bootstrap pending: allow only read-only tools (any path)
        ├─ if bootstrap pending and Read hits a required file: record; upgrade if complete
        └─ if bootstrap done and tool is mutating: require Decision Gate text in current turn

PostToolUse (Edit|Write|MultiEdit|NotebookEdit)
  └─> nexus-vault-validator.py   (non-enforcing, advisory)
        ├─ skip unless the written file is knowledge/**.md
        ├─ run tools/validate-vault.py rules on that one document
        └─ inject findings as additionalContext; silent when clean

Stop
  ├─> nexus-exit-gate.py
  │     ├─ locate last user turn in transcript
  │     ├─ regex-match Closure Block in assistant text of that turn
  │     ├─ validate fields + dependency rules
  │     └─ block (decision=block) if violation
  └─> nexus-session-writer.py   (non-enforcing, silent)
        ├─ reconstruct turn pairs from transcript
        ├─ rename prior archive if .nexus/session-theme.txt changed
        └─ rewrite knowledge/sessions/session--<theme>--<date>--<id8>.md
```

---

## Data Contracts

### State file shape (`.nexus/state.json`)

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

### Closure Block grammar (enforced by nexus-exit-gate.py)

```
Closure Block:
- code changed: yes|no
- KB changed: yes|no
- session log written: yes|no
- writeback evaluation performed: yes|no
```

Dependency rules: if `code changed: yes` then `writeback evaluation performed: yes`. If `KB changed: no` the turn MUST include a justification (free-form text on a subsequent line starting with `KB unchanged because`).

### Decision Gate grammar (enforced by nexus-tool-gate.py)

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
