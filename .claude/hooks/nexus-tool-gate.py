#!/usr/bin/env python3
"""Nexus: PreToolUse hook.

- While bootstrap is pending: allow read-family tools, block everything else.
  Track Reads of required files and auto-upgrade bootstrap status when complete.
- After bootstrap: for mutating tools, require a Context Decision in the
  current turn. Two forms are accepted, checked in this order: the per-turn
  flag already set; a claim (`python3 tools/nexus-decide.py ...`) read from
  tool_input; the "### Context Decision" text block read from the transcript.
- Core freeze (hosts only): the editing tools are denied on a path that
  .nexus/installed.json records as a Nexus core file, unless the path is
  listed in .nexus/unlock.txt. Checked before the decision gate, so a denied
  core edit never consumes the turn's decision. Inactive without a baseline.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    DECISION_CLAIM_USAGE,
    MUTATING_TOOLS,
    READ_ONLY_TOOLS,
    REQUIRED_FILES,
    REQUIRED_INVARIANTS_DIR,
    bootstrap_complete,
    core_freeze_reason,
    emit,
    emit_block,
    find_decision_gate,
    load_state,
    mark_bootstrap_if_complete,
    parse_decision_claim,
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
            "Read-only tools (Read/Glob/Grep/LS/NotebookRead) remain permitted."
        )
        emit_block(reason, hook_event="PreToolUse")
        return 0

    # ---- bootstrap-completed branch -----------------------------------------------
    # 0. Core freeze: a host never edits a Nexus core file in place
    #    (spec--system--nexus-update.md §6). Bash writes are not caught here;
    #    `nexus-update.py status` remains the safety net.
    freeze = core_freeze_reason(tool, tool_input)
    if freeze is not None:
        emit_block(freeze, hook_event="PreToolUse")
        return 0

    if tool in MUTATING_TOOLS:
        turn = state.setdefault("turn", {})

        # 1. One decision per turn: once recorded, later mutating calls pass.
        if turn.get("decision_gate_seen"):
            emit({"continue": True})
            return 0

        # 2. Claim form: a Bash call of fixed form carries the decision in
        #    tool_input, which survives transcript narration (see plan
        #    plan--system--context-decision-claim). Malformed claims are denied.
        if tool == "Bash":
            claim, err = parse_decision_claim(tool_input.get("command") or "")
            if claim is not None:
                turn["decision_gate_seen"] = True
                turn["decision"] = claim
                save_state(state)
                emit({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": (
                            f"Context Decision claim accepted (KB consult required: {claim['kb'].upper()})."
                        ),
                    }
                })
                return 0
            if err is not None:
                emit_block(
                    f"NEXUS DECISION CLAIM MALFORMED: {err}.\n\nUsage:\n{DECISION_CLAIM_USAGE}",
                    hook_event="PreToolUse",
                )
                return 0

        # 3. Text fallback: the "### Context Decision" block in this turn's
        #    assistant text. Retry until visible: a text block emitted in the
        #    same assistant message as this tool call may not be on disk yet.
        turn_text = read_transcript_current_turn(
            transcript_path, until=lambda t: find_decision_gate(t) is not None
        )
        decision = find_decision_gate(turn_text)
        if decision is not None:
            turn["decision_gate_seen"] = True
            turn["decision"] = {"kb": decision, "via": "text"}
            save_state(state)
            emit({"continue": True})
            return 0

        # 4. Neither form present: deny, showing both.
        reason = (
            f"NEXUS DECISION GATE MISSING: tool '{tool}' is BLOCKED. "
            "Before any mutating tool you MUST state the Context Decision in this turn, "
            "in one of two forms:\n\n"
            "(a) claim via Bash, as the first mutating call of the turn (preferred; "
            "survives transcript narration):\n"
            f"{DECISION_CLAIM_USAGE}\n\n"
            "(b) plain text earlier in this turn:\n"
            "### Context Decision\nKB consult required: YES|NO\nReasoning: <why>\n\n"
            "If YES, name which KB documents you will read. If NO, justify and accept the risk."
        )
        emit_block(reason, hook_event="PreToolUse")
        return 0

    emit({"continue": True})
    return 0


if __name__ == "__main__":
    sys.exit(main())
