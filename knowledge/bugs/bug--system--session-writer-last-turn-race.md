---
type: bug
scope: system
status: deprecated
created: 2026-10-03
updated: 2026-10-10
source_of_truth: false
knowledge_visibility: historical
theme: progressive-resolution
tags: [bug, session-writer, hooks, stop, transcript, race, fixed]
---

## Relations

- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2a describes the session writer whose read of the transcript races the final assistant record.

---

# Bug: session writer can miss the last assistant answer of a turn

**Status: fixed 2026-10-10.** Parked by the operator on 2026-10-03 ("we will fix it later, not now"); reopened on 2026-10-10 after the defect ate the decisive last turn of the second-layer experiment in Liquid_Nexus (the agent's answer to the operator's question about §0 of the process-space spec is absent from that host's archive), and confirmed live the same day in this repository: the answer of turn 4 of session `0e8f5901` (9198 characters, Closure Block included, transcript record timestamped 08:41:19.993Z) was missing from the archive written at 08:41:20. A scan of the fifteen archives then present found the last answer missing in six.

## Symptom

The session archive written by `.claude/hooks/nexus-session-writer.py` contains the user prompt of a turn but not the assistant's answer to it, although the answer is present in the Claude Code transcript as an ordinary `text` block.

Observed in session `410ccd3c` on 2026-10-03: turn 6 (a pure-text answer with no tool calls) was archived without its assistant text. The transcript record carrying that text has timestamp `16:43:22.238Z`; the archive's `updated:` is `16:43:22`, the same second.

## Cause

Both `Stop` hooks (`nexus-exit-gate.py`, `nexus-session-writer.py`) run concurrently, at the moment Claude Code appends the final assistant record to the transcript. The exit gate read the file after the record landed and found the Closure Block; the writer read it a moment earlier and reconstructed the turn with an empty answer. No parsing defect: the writer is correct, its read is just too early.

## Impact

Self-healing for every turn but the last: the writer rewrites the whole archive on each `Stop`, so a lagging answer appears one turn later. The **last turn of a session** has no later `Stop`, so its answer can be missing from the archive permanently. Archives from earlier sessions may already lack their final answer; worth a check.

## Workaround

Re-run the writer by hand with the payload Claude Code gives it (`session_id`, `transcript_path`, `hook_event_name: Stop`, `cwd`) and `CLAUDE_PROJECT_DIR` set; it is idempotent and rewrites the same file.

## Cause, verified 2026-10-10

The explanation above held. The exit gate had already been protected against the same race by `read_transcript_current_turn` in `_nexus_common.py`, which re-reads the transcript up to four times at 80 ms until the Closure Block appears; the writer read once. In the live case the gate found the block and did not block the turn, while the writer, started in the same instant, archived the turn without its answer.

Not this bug: four archives also lack answers to turns in the middle of a session. Checked against the transcript of `ab71248a`: those "turns" are synthetic user records (`/compact`, the post-compaction continuation summary, `<local-command-caveat>` and `<local-command-stdout>` blocks) that never have an answer. Nothing was lost there; the writer archives them as prompts, which is noise, not loss, and out of this fix's scope.

## Fix (applied 2026-10-10)

`nexus-session-writer.py` now reads the transcript through `read_turns_settled`: when the last reconstructed turn does not end with a Closure Block (the exit gate requires one on every completed turn, so its absence means the final record has not landed yet), it sleeps 150 ms and re-reads, up to 12 attempts. A complete turn is detected on the first read and pays nothing; only a turn whose answer never arrives (the exit gate is blocking it, and a later Stop rewrites the archive anyway) pays the full 1.65 s, within the 15 s hook timeout. The hook stays silent and non-enforcing.

## Verification

- `python3 .claude/hooks/nexus-session-writer.py --selftest`: the final record appended 0.4 s after the hook started is archived (observed 0.52 s); a turn whose answer never arrives is archived without it within the budget (observed 1.73 s); a complete turn pays no wait (0.06 s); stdout stays empty.
- Static plan of `docs/nexus-implementation-report.md` §2 (S1–S8) clean after the change.
- Live: the Stop of the turn that applied the fix is the first run of the new code in a real session; the archive of session `0e8f5901` must carry that turn's answer at the next Stop.

Archives written before the fix keep their gaps: the writer rewrites only the current session's file.
