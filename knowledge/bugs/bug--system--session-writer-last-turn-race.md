---
type: bug
scope: system
status: draft
created: 2026-10-03
updated: 2026-10-03
source_of_truth: false
knowledge_visibility: development
theme: progressive-resolution
tags: [bug, session-writer, hooks, stop, transcript, race]
---

## Relations

- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2a describes the session writer whose read of the transcript races the final assistant record.

---

# Bug: session writer can miss the last assistant answer of a turn

**Status: open, parked by the operator on 2026-10-03 ("we will fix it later, not now").**

## Symptom

The session archive written by `.claude/hooks/nexus-session-writer.py` contains the user prompt of a turn but not the assistant's answer to it, although the answer is present in the Claude Code transcript as an ordinary `text` block.

Observed in session `410ccd3c` on 2026-10-03: turn 6 (a pure-text answer with no tool calls) was archived without its assistant text. The transcript record carrying that text has timestamp `16:43:22.238Z`; the archive's `updated:` is `16:43:22`, the same second.

## Cause

Both `Stop` hooks (`nexus-exit-gate.py`, `nexus-session-writer.py`) run concurrently, at the moment Claude Code appends the final assistant record to the transcript. The exit gate read the file after the record landed and found the Closure Block; the writer read it a moment earlier and reconstructed the turn with an empty answer. No parsing defect: the writer is correct, its read is just too early.

## Impact

Self-healing for every turn but the last: the writer rewrites the whole archive on each `Stop`, so a lagging answer appears one turn later. The **last turn of a session** has no later `Stop`, so its answer can be missing from the archive permanently. Archives from earlier sessions may already lack their final answer; worth a check.

## Workaround

Re-run the writer by hand with the payload Claude Code gives it (`session_id`, `transcript_path`, `hook_event_name: Stop`, `cwd`) and `CLAUDE_PROJECT_DIR` set; it is idempotent and rewrites the same file.

## Proposed fix (not applied)

In the writer: if the last reconstructed turn has a user prompt but an empty assistant answer, sleep briefly (1–2 s) and re-read the transcript, up to a small bounded number of attempts, before writing. Keeps the hook non-enforcing and silent; stays within the 15 s hook timeout. The architecture §2a text would then mention the retry.
