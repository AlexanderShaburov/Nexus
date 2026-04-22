# CLAUDE.md

This file is the project-level memory loaded automatically by Claude Code. Keep it short: its job is to point the agent at the real sources of truth, not to duplicate them.

## What this repository is

This repository ships a **runtime enforcement system for the Nexus (formerly SOKI) (Session-Oriented Knowledge Integration) workflow**. It consists of:

- a populated Knowledge Vault under `knowledge/` (the ontology + canonical specs live there);
- a set of Claude Code hooks under `.claude/hooks/` that enforce the Nexus lifecycle gates (Bootstrap, Context Decision, Exit);
- per-session runtime state under `.soki/` (regenerated automatically; do not commit `state.json`).

The conceptual background paper is `nexus_approach.md` at repo root. The original advisory-style `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` (moved from `bootstrap.md`) is **superseded** by `knowledge/specs/spec--system--session-bootstrap.md` and the hooks — kept only for historical reference.

Legacy template content under `legacy-kb/` is deprecated. Do not use it as a source of truth. When in doubt, follow `knowledge/` and `.claude/hooks/`.

## How work proceeds here

All non-trivial work is governed by three hook-enforced gates. The contract is:

1. **Session Bootstrap** (`SessionStart`, `PreCompact`). You MUST read the Mandatory Startup Reading Set and emit the `Session Bootstrap Completed` confirmation block. Until you do, PreToolUse BLOCKS every non-read tool.
2. **Context Decision Gate** (`UserPromptSubmit` + `PreToolUse`). Before any mutating tool (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Bash`, `Task`) you MUST emit a `### Context Decision` block with `KB consult required: YES|NO` and reasoning. PreToolUse BLOCKS the tool if missing from the current turn.
3. **Exit Gate** (`Stop`). Every response MUST end with a valid `Closure Block` covering code-changed / KB-changed / session-log-written / writeback-evaluation-performed. The Stop hook parses the transcript and BLOCKS completion on violations.

The enforcement layer is:

- `.claude/hooks/soki-bootstrap.sh`
- `.claude/hooks/soki-prompt-gate.sh`
- `.claude/hooks/soki-tool-gate.sh`
- `.claude/hooks/soki-exit-gate.sh`
- `.claude/hooks/_soki_common.py` (shared helpers)

Hook config: `.claude/settings.json`. Runtime state: `.soki/state.json` (gitignored).

## Mandatory Startup Reading Set

Read these on every session start (Session Bootstrap):

1. Everything in `knowledge/invariants/`
2. `knowledge/architecture/architecture--system--overall-structure.md`
3. `knowledge/specs/spec--system--knowledge-driven-task-orchestration.md`
4. `knowledge/index/index--system--project-navigation.md`

## Read Priority (when consulting the vault)

`invariants → architecture → specs → decisions → patterns → plans → sessions → glossary`.

Use the navigation index (`knowledge/index/index--system--project-navigation.md`) to locate documents structurally. Grep is a fallback, not a primary lookup.

## Writing rules (if you modify the vault)

- Every document MUST satisfy `knowledge/specs/spec--system--document-frontmatter.md` (YAML block with `type`, `scope`, `status`, `created`, `updated`, `source_of_truth`, `tags`).
- Directory choice MUST match semantic role per `knowledge/specs/spec--system--knowledge-vault.md`.
- Filename convention: `<type>--<scope>--<name>.md`, lowercase, kebab-case.
- Bump `updated:` on any meaningful change.

## When editing hooks

- Hook text that references spec content MUST be mirrored in the corresponding spec (drift breaks coherence).
- After changes, run the validation plan in `docs/soki-implementation-report.md` before claiming the hooks work.
