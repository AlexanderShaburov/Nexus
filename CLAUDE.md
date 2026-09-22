# CLAUDE.md

This file is the project-level memory loaded automatically by Claude Code. Keep it short: its job is to point the agent at the real sources of truth, not to duplicate them.

## What this repository is

This repository ships a **runtime enforcement system for the Nexus workflow**. It consists of:

- a populated Knowledge Vault under `knowledge/` (the ontology + canonical specs live there);
- a set of Claude Code hooks under `.claude/hooks/` that enforce the Nexus lifecycle gates (Bootstrap, Context Decision, Exit);
- per-session runtime state under `.nexus/` (regenerated automatically; do not commit `state.json`).

The conceptual background paper is `nexus_approach.md` at repo root. The original advisory-style `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` (moved from `bootstrap.md`) is **superseded** by `knowledge/specs/spec--system--session-bootstrap.md` and the hooks — kept only for historical reference.

Legacy template content under `legacy-kb/` is deprecated. Do not use it as a source of truth. When in doubt, follow `knowledge/` and `.claude/hooks/`.

## How work proceeds here

All non-trivial work is governed by three hook-enforced gates. The contract is:

1. **Session Bootstrap** (`SessionStart`, `PreCompact`). You MUST read the Mandatory Startup Reading Set and emit the `Session Bootstrap Completed` confirmation block. Until you do, PreToolUse BLOCKS every non-read tool.
2. **Context Decision Gate** (`UserPromptSubmit` + `PreToolUse`). Before any mutating tool (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Bash`, `Task`) you MUST state the Context Decision once in the turn, in one of two forms: preferably a **claim**, a Bash call `python3 tools/nexus-decide.py --kb YES|NO [--reads <vault-doc>...] --reason "<why>"` made as the first mutating call of the turn; or a `### Context Decision` text block with `KB consult required: YES|NO` and reasoning. PreToolUse BLOCKS the tool if neither is present in the current turn, and denies a malformed claim with the defect named. The claim is preferred because it is read from the tool call itself and survives transcript narration; the text form is the fallback.
3. **Exit Gate** (`Stop`). Every response MUST end with a valid `Closure Block` covering code-changed / KB-changed / session-log-written / writeback-evaluation-performed. The Stop hook parses the transcript and BLOCKS completion on violations.

The enforcement layer is:

- `.claude/hooks/nexus-bootstrap.py`
- `.claude/hooks/nexus-prompt-gate.py`
- `.claude/hooks/nexus-tool-gate.py`
- `.claude/hooks/nexus-exit-gate.py`
- `.claude/hooks/_nexus_common.py` (shared helpers)

Alongside them, two **non-enforcing** hooks run:

- `.claude/hooks/nexus-session-writer.py` — archives the session transcript to `knowledge/sessions/session--<theme>--<YYYY-MM-DD>--<session-id8>.md`. It strips tool calls, tool results, thinking blocks and system-reminder tags, keeping only user prompts and assistant text. It rewrites the same file in place on every `Stop`, renaming it when `.nexus/session-theme.txt` changes **within the same session**, so a session stays one document. The ownership marker `.nexus/session-file.txt` is session-scoped JSON — a different session never renames or overwrites an existing archive. Written docs carry `status: draft`, `source_of_truth: false`, `knowledge_visibility: historical` — they are an audit trail, never a source of truth. The hook is silent by design (no stdout, swallows its own exceptions) so it cannot interfere with the Exit Gate scheduled in the same event. It gates nothing and blocks nothing, and it has no spec by design: it enforces no contract, so there is no contract to mirror.

- `.claude/hooks/nexus-vault-validator.py` (`PostToolUse` on `Edit`/`Write`/`MultiEdit`/`NotebookEdit`) — after a write to a document under `knowledge/`, validates that one document against the frontmatter contract and reports findings as advisory context. Silent when clean. It never blocks (the write has already happened) and never auto-corrects. The rules live in `tools/validate-vault.py`, which is also the CLI: run `python3 tools/validate-vault.py` for the whole vault, `--selftest` to prove every rule still fires.

Hook config: `.claude/settings.json`. Runtime state: `.nexus/state.json` (gitignored), plus the session-writer's markers `.nexus/session-theme.txt` and `.nexus/session-file.txt`.

## Mandatory Startup Reading Set

Read these on every session start (Session Bootstrap):

1. Everything in `knowledge/invariants/`
2. `knowledge/architecture/architecture--system--overall-structure.md`
3. `knowledge/specs/spec--system--knowledge-driven-task-orchestration.md`
4. `knowledge/index/index--system--project-navigation.md`

## Read Priority (when consulting the vault)

`invariants → architecture → specs → decisions → patterns → plans → sessions → glossary`.

Use the navigation index (`knowledge/index/index--system--project-navigation.md`) to locate documents structurally. Grep is a fallback, not a primary lookup.

## Knowledge Visibility (review / gap-analysis)

When performing review-class tasks ("what specs are missing?", "what gaps remain?", "what should be implemented next?", "review this architecture", "create a roadmap"), the agent MUST follow `knowledge/specs/spec--system--architecture-review.md`: enumerate **Binding State** AND **Development State** before declaring any gap, and classify every finding as one of `Truly Missing` / `Exists As Draft` / `Exists But Not Normalized` / `Superseded Gap`.

The three visibility classes (binding / development / historical) and the optional `knowledge_visibility` frontmatter field are defined in `knowledge/specs/spec--system--knowledge-visibility.md`. The non-negotiable rule is `knowledge/invariants/invariant--system--review-classification.md` (auto-loaded at bootstrap).

Migration for existing Nexus-based projects: `knowledge/runbooks/runbook--system--development-visibility-migration.md`.

## Writing rules (if you modify the vault)

- Every document MUST satisfy `knowledge/specs/spec--system--document-frontmatter.md` (YAML block with `type`, `scope`, `status`, `created`, `updated`, `source_of_truth`, `tags`). That spec holds the closed enums for `type` and `status` and the list of registered extension fields — consult it rather than guessing a value.
- Directory choice MUST match semantic role per `knowledge/specs/spec--system--knowledge-vault.md`, and `type:` MUST agree with both the directory and the filename prefix.
- Filename convention: `<type>--<scope>--<name>.md`, lowercase, kebab-case. Session documents add trailing segments: `session--<theme>--<date>--<id8>.md` (generated by the session writer) and `summary--<theme>--<date>.md` (hand-written handoff).
- Bump `updated:` on any meaningful change.
- Before claiming a vault edit is done, run `python3 tools/validate-vault.py` (exit 0 = clean). The `PostToolUse` validator reports the file you just wrote; the CLI covers the whole vault, including links that your edit may have broken elsewhere.

## When editing hooks

- Hook text that references spec content MUST be mirrored in the corresponding spec (drift breaks coherence).
- After changes, run the validation plan in `docs/nexus-implementation-report.md` before claiming the hooks work.
