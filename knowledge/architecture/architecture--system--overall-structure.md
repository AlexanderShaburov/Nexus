---
type: architecture
scope: system
status: approved
created: 2026-04-18
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [architecture, system, nexus, lifecycle, self-update]
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
- `nexus-tool-gate.py` — runs on `PreToolUse`. While bootstrap pending, only read-only tools (`Read`/`Glob`/`Grep`/`LS`/`NotebookRead`) are allowed, on any path — reads cannot mutate, so the gate constrains tool class, not location. Tracks read-ledger to auto-complete bootstrap. After bootstrap, non-read tools require a Decision Gate statement in the current turn, accepted in two forms checked in order: the per-turn flag already set; a **claim** (`python3 tools/nexus-decide.py ...`) read from `tool_input.command`; the `### Context Decision` text block read from the transcript. A malformed claim is denied with the defect named. In a host with a baseline (`.nexus/installed.json`), the editing tools are denied on a Nexus core path (every `replace` unit) unless `.nexus/unlock.txt` lists it; this **core freeze** is checked after the bootstrap gate and before the decision check, and is inactive in the template (spec `spec--system--nexus-update.md` §6).
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

### 2c. Context Decision claim (`tools/nexus-decide.py`)

The tool-carried form of the Context Decision (spec `spec--system--context-decision-gate.md`, Form A). The script validates its arguments with `parse_decision_claim_args` imported from `_nexus_common.py`, so the gate and the script share one parser, and prints the decision in the shape of the text block. It decides nothing and writes nothing. It exists because some Claude Code builds persist mid-turn assistant text as a paraphrased `thinking` block, which leaves the transcript-reading gate nothing to match; a tool call's parameters are persisted verbatim and reach the gate in `tool_input`. Stdlib only.

### 2d. Version identity and ownership manifest (`nexus.version`, `nexus.manifest.json`, `tools/nexus-update.py`)

The template carries a version and a machine-generated list of what it owns, so a host can later tell "delivered by Nexus" from "written by the project". Design: `plans/plan--system--nexus-self-update.md` (development class; the behavioural spec follows when the updater's compare and apply phases land).

- `nexus.version` — one line of semver; the single source of the version number. Template-only.
- `nexus.manifest.json` — every Nexus-owned path with an update strategy (`replace`, `sections`, `index-entries`, `hooks-merge`, `ensure-lines`, `create-if-absent`) and a `never_touch` list. Generated by `tools/nexus-update.py manifest generate` from the tree: runtime code, binding `scope: system` vault documents outside `sessions/`, shared Obsidian config, and fixed entries for `CLAUDE.md` (owned per H2 section, "What this repository is" excluded), `.claude/settings.json` (owned per `nexus-*` hook entry), `.gitignore` and `.nexus/README.md`. `manifest verify` regenerates in memory and fails on drift; `--selftest` runs it. Template-only.
- `tools/nexus-update.py` — the updater. Realized: `manifest generate|verify` (template), `baseline`, `status`, `check` and `plan` (host). `check` and `plan` reach upstream through a bare clone cached under `${NEXUS_UPSTREAM_CACHE:-~/.cache/nexus}/template`, read files with `git show`, default to the highest `v*` tag, and never check anything out into the host. `plan` computes the three-way table (baseline / local / upstream) per owned unit and writes nothing. `apply` (dry-run unless `--apply`) writes the clean rows with backups under `.nexus/backups/`, hooks last, rewrites the baseline and validates the result; it refuses while a Claude Code session looks live. Stdlib only; reuses the frontmatter parser of `tools/validate-vault.py`. Delivered to hosts as part of `tools/`. Contract: `specs/spec--system--nexus-update.md`.

### 2e. Update notifier (`.claude/hooks/nexus-update-check.py`)

A **non-enforcing** hook on `SessionStart` only, registered after `nexus-bootstrap.py`. In a host with a baseline it asks upstream, at most once per 24 h and with one `git ls-remote --tags` call bounded to 5 s, whether a newer `v*` tag exists, records the answer in `.nexus/update-check.json`, and emits one line of context only when the answer is yes. It never fetches objects, never touches the cache clone, never blocks, and stays silent on every failure and in the template. Contract: `specs/spec--system--nexus-update.md` §7. Applying an update stays an explicit operator command (§2d).

### 3. Runtime State (`.nexus/`)

- `.nexus/state.json` — per-session runtime state (bootstrap status, read-ledger, per-turn decision flag, prompt index). Ephemeral; regenerated at each `SessionStart`. Gitignored.
- `.nexus/session-theme.txt` — optional single-line theme slug used by the session writer to name the archive file.
- `.nexus/session-file.txt` — JSON `{"session_id", "path"}` identifying the archive the session writer currently owns, so a theme change renames instead of forking, and a *different* session never renames it.
- `.nexus/installed.json` — the install baseline: installed Nexus version, upstream ref, and the SHA-256 of every owned unit as delivered (a unit is a file, a `CLAUDE.md` section, an index line or a hook entry). Written only by `tools/nexus-update.py baseline` (and later `apply`). **Committed** with the host: it is shared state, not session state.
- `.nexus/unlock.txt` — operator-written list of core paths the host may edit; empty or absent by default. Read by `status` and by the tool gate's core freeze. Committed with the host when used.
- `.nexus/backups/update-<version>-<timestamp>/` — copies of every file `apply` modified, plus the previous `installed.json`. Gitignored.
- `.nexus/update-check.json` — record of the last upstream version check (`checked_at`, `status`, `upstream_version`, `upstream_ref`, `upstream_commit`, `via`), written by `tools/nexus-update.py check` and by `nexus-update-check.py` on every attempt, including failures. The notifier throttles on it (24 h). Gitignored.
- `.nexus/README.md` — explains the directory.

### 4. Project Instructions

- `CLAUDE.md` at project root — minimum project memory loaded automatically by Claude Code. It names the protocol and points to this architecture doc.

---

## Control Flow (lifecycle)

```
SessionStart / PreCompact
  ├─> nexus-bootstrap.py
  │     ├─ reset .nexus/state.json (bootstrap = pending)
  │     └─ inject mandatory reading set into first turn context
  └─> nexus-update-check.py   (SessionStart only; non-enforcing, silent)
        ├─ no .nexus/installed.json → exit
        ├─ .nexus/update-check.json younger than 24 h → reuse
        ├─ else one `git ls-remote --tags`, 5 s budget → record ok / no-tags / unreachable
        └─ newer v* tag than installed → one line of context; otherwise nothing

UserPromptSubmit
  └─> nexus-prompt-gate.py
        ├─ reset per-turn flags
        ├─ if bootstrap pending: inject bootstrap-first reminder
        └─ else: inject Decision Gate + Exit Gate contract

PreToolUse
  └─> nexus-tool-gate.py
        ├─ if bootstrap pending: allow only read-only tools (any path)
        ├─ if bootstrap pending and Read hits a required file: record; upgrade if complete
        ├─ if bootstrap done and tool edits a Nexus core path in a host
        │    (installed.json replace unit, not in unlock.txt) → deny (core freeze)
        └─ if bootstrap done and tool is mutating:
              ├─ turn.decision_gate_seen already true → allow
              ├─ Bash matching tools/nexus-decide.py claim → record decision, allow
              │    (malformed claim → deny with reason)
              ├─ "### Context Decision" text in current turn → record decision, allow
              └─ otherwise deny, showing both forms

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
    "decision_gate_seen": false,
    "decision": {"kb": "yes|no", "reason": "...", "reads": ["..."], "via": "claim"}
  }
}
```

`turn.decision` is present only after a decision was accepted in the turn; for the text form it is `{"kb": "...", "via": "text"}`.

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

One of the two forms must precede any other mutating tool call in the turn.

Form A, a claim, as the first mutating call of the turn (read from `tool_input.command`):

```
python3 tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason "<why>"
python3 tools/nexus-decide.py --kb NO --reason "<why the KB is not needed and what risk is accepted>"
```

Form B, a text block in the current turn's assistant text (read from the transcript; fallback):

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
