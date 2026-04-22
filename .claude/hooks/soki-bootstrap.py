#!/usr/bin/env python3
"""SOKI: SessionStart + PreCompact hook.

Resets per-session state and injects the Mandatory Startup Reading Set into
the model context. No heredoc shenanigans — stdin is the real hook input JSON.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _soki_common import (  # noqa: E402
    REQUIRED_FILES,
    REQUIRED_INVARIANTS_DIR,
    emit_context,
    fresh_state,
    invariants_present,
    project_dir,
    read_hook_input,
    save_state,
)


def main() -> int:
    inp = read_hook_input()
    event = inp.get("hook_event_name") or "SessionStart"
    session_id = inp.get("session_id") or ""

    state = fresh_state(session_id)
    state["bootstrap"]["event"] = event
    save_state(state)

    root = project_dir()
    missing = [p for p in REQUIRED_FILES if not (root / p).is_file()]
    invariants = invariants_present()
    invariant_missing = len(invariants) == 0

    lines = [
        "=== SOKI SESSION BOOTSTRAP — MANDATORY ===",
        "",
        f"Event: {event}. This session is UNINITIALIZED.",
        "You MUST complete Session Bootstrap before performing any non-trivial work.",
        "",
        "STEP 1 — Read these files (use the Read tool) in this order:",
        f"  1. {REQUIRED_INVARIANTS_DIR}/ — read ALL invariants (use Glob then Read).",
        f"  2. {REQUIRED_FILES[2]}",
        f"  3. {REQUIRED_FILES[1]}",
        f"  4. {REQUIRED_FILES[0]}",
        "",
        "STEP 2 — Emit this exact confirmation block as plain text:",
        "",
        "  ---",
        "  Session Bootstrap Completed",
        "  Loaded:",
        "  - navigation index",
        "  - orchestration spec",
        "  - system architecture",
        "  - invariants",
        "  Operational Mode: Knowledge-Driven Mode: ACTIVE",
        "  ---",
        "",
        "ENFORCEMENT:",
        "- PreToolUse BLOCKS every non-read tool (Edit/Write/Bash/Task/...) until the required",
        "  files have been read. Read/Glob/Grep/LS on knowledge/ remain allowed during bootstrap.",
        "- UserPromptSubmit will keep reminding you until bootstrap is marked completed.",
        "",
        "SOURCE SPECS (ground truth for this protocol):",
        "  knowledge/specs/spec--system--session-bootstrap.md",
        "  knowledge/specs/spec--system--knowledge-driven-task-orchestration.md",
    ]
    if missing:
        lines += ["", "WARNING — these required vault files are MISSING:"]
        lines += [f"  - {p}" for p in missing]
        lines += ["You MUST create them (or fix the paths) before this protocol can be satisfied."]
    if invariant_missing:
        lines += ["", f"WARNING — {REQUIRED_INVARIANTS_DIR}/ is empty. At least one invariant is required."]

    emit_context(event, "\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
