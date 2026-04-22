#!/usr/bin/env python3
"""SOKI: Stop hook.

Parses the transcript for the current turn's assistant text and enforces:
- bootstrap-completion confirmation block (when bootstrap is still pending);
- Closure Block presence + field shape;
- dependency Rule 1 (code→writeback) and Rule 3 (no-writeback→justification);
- placement (Closure Block must be the final substantive element).
Blocks with decision=block on violation, so the agent is fed the reason back.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _soki_common import (  # noqa: E402
    emit,
    emit_block,
    find_bootstrap_confirmation,
    find_closure_block,
    load_state,
    read_hook_input,
    read_transcript_current_turn,
)


def main() -> int:
    inp = read_hook_input()
    if inp.get("stop_hook_active"):
        # Previously blocked; let the agent respond to avoid infinite loops.
        emit({"continue": True})
        return 0

    transcript_path = inp.get("transcript_path") or ""
    turn_text = read_transcript_current_turn(transcript_path)
    if not turn_text:
        # Can't verify — fail open so transcript-read issues don't deadlock the agent.
        emit({"continue": True})
        return 0

    state = load_state()
    bootstrap_pending = state.get("bootstrap", {}).get("status") != "completed"

    if bootstrap_pending and not find_bootstrap_confirmation(turn_text):
        emit_block(
            "SOKI EXIT GATE: bootstrap is still pending. Read the required files and emit the "
            "'Session Bootstrap Completed' confirmation block verbatim before ending this turn.",
            hook_event="Stop",
        )
        return 0

    m = find_closure_block(turn_text)
    if not m:
        emit_block(
            "SOKI EXIT GATE VIOLATION: Closure Block missing or malformed. End your response with:\n\n"
            "Closure Block:\n- code changed: yes|no\n- KB changed: yes|no\n"
            "- session log written: yes|no\n- writeback evaluation performed: yes|no\n\n"
            "Dependency rules apply (code=yes => writeback=yes; KB=no => include "
            "'KB unchanged because ...' justification).",
            hook_event="Stop",
        )
        return 0

    code_changed, kb_changed, session_logged, writeback = (g.lower() for g in m.groups())
    violations: list[str] = []

    if code_changed == "yes" and writeback != "yes":
        violations.append(
            "Rule 1 violation: 'code changed: yes' requires 'writeback evaluation performed: yes'."
        )
    if kb_changed == "no" and not re.search(r"(?i)\bkb\s+unchanged\s+because\b", turn_text):
        violations.append(
            "Rule 3 violation: 'KB changed: no' requires a 'KB unchanged because ...' justification "
            "earlier in the response."
        )

    tail = turn_text[m.end():]
    # Tolerate a single trailing Rule 3 justification line, nothing else.
    tail_after_just = re.sub(r"(?is)^\s*kb\s+unchanged\s+because[^\n]*\n?", "", tail, count=1)
    if tail_after_just.strip():
        violations.append(
            "Placement violation: the Closure Block must be the final substantive element; "
            "no content allowed after it except a single Rule 3 justification line."
        )

    if violations:
        emit_block("SOKI EXIT GATE VIOLATION:\n  - " + "\n  - ".join(violations), hook_event="Stop")
        return 0

    emit({"continue": True})
    return 0


if __name__ == "__main__":
    sys.exit(main())
