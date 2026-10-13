#!/usr/bin/env python3
"""Nexus: UserPromptSubmit turn contract and saved management position.

The canonical algorithm is injected by two independent, bounded read-only
handlers. Only this handler updates the per-turn runtime gate state.
"""

from __future__ import annotations

import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    REQUIRED_INVARIANTS_DIR,
    bootstrap_complete,
    charter_status,
    emit_context,
    fresh_state,
    load_state,
    process_documents,
    project_dir,
    read_hook_input,
    required_files,
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



# The algorithm is delivered by nexus-management-algorithm.py (two hooks).
MANAGEMENT_NAVIGATION = "process/navigation.md"

MANAGEMENT_INSTRUCTIONS = """=== NEXUS MANAGEMENT CONTEXT (every user turn) ===

You are participating in the Nexus management algorithm, not merely reading
background notes. The operator's latest message MUST be interpreted in the
context of the saved position and both canonical algorithm sections supplied
by companion UserPromptSubmit hooks (parts 1/2 and 2/2). Their arrival
order is unspecified; use both before making management decisions.

Before deciding what to do:
0) If Session Bootstrap is still pending, complete it before doing management work.
1) Identify the CURRENT operation from Program Counter; distinguish it from
   the project's Current Objective and the tasks inside that objective.
2) Use the algorithm's transition conditions and the current task/plan.
   Execute the operation that is due; do not skip a required evaluation or
   goal review. In particular, after either exit from block 5, carry out
   the corresponding evaluation (6a or 6b) AND the Project Goal review (7)
   before choosing another objective.
3) Classify the operator's message: a contribution to the ongoing operation,
   a request to perform work, a challenge/change to a prior decision, or a
   question that requires only an answer. A question alone does not authorize
   advancement, a new task, or a change of objective.
4) If a task/operation is completed or cannot proceed, evaluate that fact
   under the algorithm. Only when an actual transition occurs, update
   'Step:' and 'Came from:' in the ## Now section of process/navigation.md
   AT THAT TRANSITION, giving the new operation/objective and the reason.
   Do NOT advance the counter merely because a turn or session ended.
5) Only the operator can make the agreement/stop decisions reserved to them
   by the algorithm. Propose and explain when such a decision is needed.
6) If the saved state is absent, unreadable, or inconsistent with the project,
   report that and restore/check it as specified by node 0; never invent a
   plausible counter or silently overwrite a discrepancy.

The hook only READS project state. You, the main agent, are responsible for
recording real transitions. The algorithm is a working procedure, not a
permission to override explicit operator directions or other Nexus gates.
The normal Context Decision Gate and Exit Gate remain in effect.
"""


def _read_utf8(root: pathlib.Path, relpath: str) -> tuple[str | None, str | None]:
    """Read an explicit Nexus file without guessing alternative locations."""
    path = root / relpath
    try:
        return path.read_text(encoding="utf-8"), None
    except OSError as exc:
        return None, f"{relpath}: {type(exc).__name__}: {exc}"
    except UnicodeError as exc:
        return None, f"{relpath}: {type(exc).__name__}: {exc}"


def _now_fields(navigation: str) -> tuple[dict[str, str] | None, str | None]:
    """Read Step:, Came from: and Heading: from ## Now, not the Petri-net prose.

    A labelled line may be a bare paragraph (`Step: ...`) or a list item
    (`- Step: ...`, `* Step: ...`); both satisfy process-space §6. Returns the
    fields, or None with the precise defect: which label, and how many found.
    """
    now = re.search(r"(?m)^## Now\s*$", navigation)
    if not now:
        return None, "it has no '## Now' section"
    rest = navigation[now.end():]
    next_section = re.search(r"(?m)^## \S", rest)
    if next_section:
        rest = rest[:next_section.start()]
    fields: dict[str, str] = {}
    defects: list[str] = []
    for label in ("Step", "Came from", "Heading"):
        matches = re.findall(
            rf"(?m)^[ \t]*(?:[-*+][ \t]+)?{re.escape(label)}:[ \t]*(.*)$", rest
        )
        if not matches:
            defects.append(f"no '{label}:' line")
        elif len(matches) > 1:
            defects.append(f"{len(matches)} '{label}:' lines")
        elif not matches[0].strip():
            defects.append(f"an empty '{label}:' line")
        else:
            fields[label] = matches[0].strip()
    if defects:
        return None, "its ## Now has " + ", ".join(defects)
    return fields, None


def _saved_position(root: pathlib.Path) -> str:
    if not (root / "process/charter.md").is_file():
        return (
            "No process/charter.md: the second layer is not yet active. "
            "Do not invent a Current Objective. For management, begin "
            "with node 0: reconstruct any existing history, then form and "
            "agree the Project Goal (block 1)."
        )

    navigation, error = _read_utf8(root, MANAGEMENT_NAVIGATION)
    if error:
        return "PROGRAM COUNTER UNAVAILABLE — " + error
    fields, defect = _now_fields(navigation)
    if fields is None:
        return (
            "PROGRAM COUNTER UNAVAILABLE — process/navigation.md must have "
            "exactly one non-empty Step:, Came from: and Heading: in ## Now "
            f"(as bare lines or list items); {defect}. "
            "Inspect the project before restoring its state; do not guess."
        )

    # Canonical position stays in the EXISTING Step/Came from fields. Reusing
    # them avoids two conflicting copies of the Program Counter in navigation.
    step = fields["Step"]
    match = re.match(
        r"^(?P<node>(?:\d+(?:\.\d+)?[a-zA-Zа-яА-Я]?|[A-Z][A-Z0-9]*))"
        r"(?:\s+of\s+(?P<objective>[A-Za-z0-9_.-]+))?(?=\s|$)",
        step,
    )
    if match is None:
        return (
            f"PROGRAM COUNTER FORMAT UNCLEAR — Step: {step}\n"
            "Do not infer a node. Correct the format after checking the project."
        )

    objective = match.group("objective") or "none named (may be an outer-cycle operation)"
    # The task is not stored in the counter: it belongs to the iteration plan.
    in_progress = [p for p in process_documents() if p.startswith("process/iteration--")]
    contracts = ", ".join(in_progress) if in_progress else "none detected"
    heading_refs = re.findall(r"process/iteration--[A-Za-z0-9_.-]+\.md", fields["Heading"])
    if not in_progress and heading_refs:
        contracts = ", ".join(dict.fromkeys(heading_refs)) + " (referenced in Heading; state not verified)"

    approval = charter_status() or "unknown"
    return "\n".join([
        f"Charter approval status: {approval}" + (
            " — Project Goal is not recorded as agreed" if approval != "approved" else ""
        ),
        f"Program Counter (node): {match.group('node')}",
        f"Current Objective: {objective}",
        f"Step (verbatim): {step}",
        f"Last transition (verbatim): {fields['Came from']}",
        f"In-progress objective contracts (task detail lives there): {contracts}",
        "Note: a new user message/session does not itself change the counter.",
    ])


def management_context() -> str:
    root = project_dir()
    return "\n\n".join([
        MANAGEMENT_INSTRUCTIONS.strip(),
        "=== SAVED MANAGEMENT POSITION (from process/navigation.md) ===\n" + _saved_position(root),
        "=== END NEXUS TURN AND POSITION CONTEXT ===",
    ])



def bounded_main_context(value: str) -> str:
    """Never rely on Claude Code's 2k preview to deliver the counter."""
    if len(value) > 9800:
        return (
            "NEXUS MANAGEMENT CONTEXT TOO LARGE — saved Step/Came from or bootstrap "
            "detail exceeded the hook limit. Read process/navigation.md manually "
            "and do not claim that the hook delivered the complete state. "
            "The normal turn gate rules in CLAUDE.md still apply."
        )
    return value

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
        still_needed = [p for p in required_files(state) if p not in read]
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
        emit_context("UserPromptSubmit", bounded_main_context("\n".join(lines) + "\n\n" + management_context()))
        return 0

    emit_context("UserPromptSubmit", bounded_main_context(TURN_CONTRACT + "\n\n" + management_context()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
