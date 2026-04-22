#!/usr/bin/env python3
"""Nexus: PreToolUse hook.

- While bootstrap is pending: allow read-family tools, block everything else.
  Track Reads of required files and auto-upgrade bootstrap status when complete.
- After bootstrap: for mutating tools, require a Context Decision Gate block
  in the current turn's transcript.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    MUTATING_TOOLS,
    READ_ONLY_TOOLS,
    REQUIRED_FILES,
    REQUIRED_INVARIANTS_DIR,
    bootstrap_complete,
    emit,
    emit_block,
    find_decision_gate,
    load_state,
    mark_bootstrap_if_complete,
    read_hook_input,
    read_transcript_current_turn,
    relpath_from_project,
    save_state,
)


def main() -> int:
    inp = read_hook_input()
    tool = inp.get("tool_name") or ""
    tool_input = inp.get("tool_input") or {}
    transcript_path = inp.get("transcript_path") or ""

    state = load_state()
    if not state or not state.get("bootstrap"):
        # No state yet — fail open. SessionStart will seed state next time.
        emit({"continue": True})
        return 0

    bs = state["bootstrap"]

    # ---- bootstrap-pending branch -------------------------------------------------
    if not bootstrap_complete(state):
        if tool in READ_ONLY_TOOLS:
            if tool == "Read":
                file_path = tool_input.get("file_path") or ""
                rel = relpath_from_project(file_path)
                ledger = bs.setdefault("read_ledger", [])
                if rel in REQUIRED_FILES and rel not in ledger:
                    ledger.append(rel)
                if rel.startswith(REQUIRED_INVARIANTS_DIR + "/") and rel.endswith(".md"):
                    bs["invariant_read_count"] = int(bs.get("invariant_read_count", 0)) + 1
                if mark_bootstrap_if_complete(state):
                    save_state(state)
                    emit({
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "allow",
                            "permissionDecisionReason": "Read allowed; bootstrap now COMPLETE.",
                        }
                    })
                    return 0
                save_state(state)
            emit({"continue": True})
            return 0

        reason = (
            f"NEXUS BOOTSTRAP PENDING: tool '{tool}' is BLOCKED. "
            "Finish Session Bootstrap first: read the Mandatory Startup Reading Set "
            "(invariants + architecture + orchestration spec + navigation index), "
            "then emit the 'Session Bootstrap Completed' confirmation block. "
            "Read/Glob/Grep/LS on knowledge/ are currently permitted."
        )
        emit_block(reason, hook_event="PreToolUse")
        return 0

    # ---- bootstrap-completed branch -----------------------------------------------
    if tool in MUTATING_TOOLS:
        turn_text = read_transcript_current_turn(transcript_path)
        decision = find_decision_gate(turn_text)
        if decision is None:
            reason = (
                f"NEXUS DECISION GATE MISSING: tool '{tool}' is BLOCKED. "
                "Before any mutating tool you MUST state, earlier in this turn:\n\n"
                "### Context Decision\nKB consult required: YES|NO\nReasoning: <why>\n\n"
                "If YES, name which KB documents you will read. If NO, justify and accept the risk."
            )
            emit_block(reason, hook_event="PreToolUse")
            return 0
        state.setdefault("turn", {})["decision_gate_seen"] = True
        save_state(state)

    emit({"continue": True})
    return 0


if __name__ == "__main__":
    sys.exit(main())
