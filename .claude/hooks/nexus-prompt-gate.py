#!/usr/bin/env python3
"""Nexus: UserPromptSubmit hook.

Increments per-turn index, resets Decision-Gate flag, and injects either a
bootstrap-pending reminder or the per-turn Decision-Gate + Exit-Gate contract.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    REQUIRED_FILES,
    REQUIRED_INVARIANTS_DIR,
    bootstrap_complete,
    emit_context,
    fresh_state,
    load_state,
    read_hook_input,
    save_state,
)


TURN_CONTRACT = """=== NEXUS TURN CONTRACT (per-turn) ===

1) CONTEXT DECISION GATE — before any mutating tool (Edit/Write/MultiEdit/NotebookEdit/Bash/Task)
   you MUST state the Context Decision once in this turn, in one of two forms:

   (a) claim — make this Bash call the FIRST mutating call of the turn (preferred; it is
       read from the tool call itself and survives transcript narration):

       python3 tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason "<why>"
       python3 tools/nexus-decide.py --kb NO --reason "<why the KB is not needed and what risk is accepted>"

   (b) plain text earlier in this turn:

       ### Context Decision
       KB consult required: YES | NO
       Reasoning: <why the KB is / is not needed; for NO, include what risks are accepted>

   PreToolUse BLOCKS mutating tools if neither form is present in the current turn, and
   BLOCKS a malformed claim with the reason. One decision per turn: later calls pass.

2) EXIT GATE — every response MUST end with this Closure Block, exactly:

   Closure Block:
   - code changed: yes|no
   - KB changed: yes|no
   - session log written: yes|no
   - writeback evaluation performed: yes|no

   Dependency rules:
   - code changed: yes  =>  writeback evaluation performed: yes
   - KB changed: no     =>  include a line starting with 'KB unchanged because ...' earlier in the response

   The Stop hook parses the transcript and BLOCKS completion if the Closure Block is missing,
   malformed, violates a dependency rule, or is followed by extra content.
"""


def main() -> int:
    inp = read_hook_input()
    session_id = inp.get("session_id") or ""

    state = load_state()
    if not state or not state.get("bootstrap"):
        state = fresh_state(session_id)

    state["turn"] = {
        "index": int(state.get("turn", {}).get("index", 0)) + 1,
        "decision_gate_seen": False,
    }
    save_state(state)

    if not bootstrap_complete(state):
        bs = state.get("bootstrap", {})
        read = set(bs.get("read_ledger", []))
        still_needed = [p for p in REQUIRED_FILES if p not in read]
        lines = [
            "=== NEXUS BOOTSTRAP STILL PENDING ===",
            "",
            "You have NOT finished Session Bootstrap. Non-read tools are BLOCKED.",
            "",
            "Still to read:",
        ] + [f"  - {p}" for p in still_needed]
        if bs.get("invariant_read_count", 0) < 1:
            lines += [f"  - at least one file under {REQUIRED_INVARIANTS_DIR}/"]
        lines += [
            "",
            "After reading, emit the 'Session Bootstrap Completed' block (see prior system notice).",
        ]
        emit_context("UserPromptSubmit", "\n".join(lines))
        return 0

    emit_context("UserPromptSubmit", TURN_CONTRACT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
