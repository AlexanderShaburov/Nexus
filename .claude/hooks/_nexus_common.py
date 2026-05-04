"""Shared helpers for Nexus hooks.

Keeps scripts concise and JSON-handling robust across hooks.
Not a public API — consumed only by the .py wrappers in this directory.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys
from typing import Any, Iterable

REQUIRED_FILES = [
    "knowledge/index/index--system--project-navigation.md",
    "knowledge/specs/spec--system--knowledge-driven-task-orchestration.md",
    "knowledge/architecture/architecture--system--overall-structure.md",
]
REQUIRED_INVARIANTS_DIR = "knowledge/invariants"

# Tools allowed while bootstrap is pending (read-only vault traversal).
READ_ONLY_TOOLS = {"Read", "Glob", "Grep", "LS", "NotebookRead", "TodoWrite", "TaskList", "TaskGet", "TaskOutput"}

# Tools that mutate code / environment and REQUIRE a Decision Gate statement in the current turn.
MUTATING_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "Task", "Agent"}

# Regex: accept headings like "### Context Decision" or bold "**Context Decision:**" etc.
# The shape is lenient — we want to avoid false negatives — but must carry YES/NO.
DECISION_GATE_RE = re.compile(
    r"(?im)^\s*(?:#+\s*|\*+\s*)?context\s+decision(?:\s+gate)?\s*[:.]?\s*\*?\*?\s*\n"
    r"(?:[^\n]*\n){0,4}?"
    r"\s*\*?\*?kb\s+consult\s+required\*?\*?\s*[:=]\s*(yes|no)\b",
)

# Exit Gate Closure Block: tolerate bullet/dash prefixes and whitespace.
CLOSURE_BLOCK_RE = re.compile(
    r"(?is)closure\s+block\s*[:.]?\s*\n"
    r"[-*]\s*code\s+changed\s*[:=]\s*(yes|no)\s*\n"
    r"[-*]\s*kb\s+changed\s*[:=]\s*(yes|no)\s*\n"
    r"[-*]\s*session\s+log\s+written\s*[:=]\s*(yes|no)\s*\n"
    r"[-*]\s*writeback\s+evaluation\s+performed\s*[:=]\s*(yes|no)\b",
)

BOOTSTRAP_CONFIRMATION_RE = re.compile(
    r"(?is)session\s+bootstrap\s+completed.*?knowledge[- ]driven\s+mode\s*[:=]?\s*active",
)


def project_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def state_path() -> pathlib.Path:
    return project_dir() / ".nexus" / "state.json"


def read_hook_input() -> dict[str, Any]:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def load_state() -> dict[str, Any]:
    p = state_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict[str, Any]) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2))


def fresh_state(session_id: str) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "started_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "bootstrap": {
            "status": "pending",
            "required_files": REQUIRED_FILES,
            "required_invariants_dir": REQUIRED_INVARIANTS_DIR,
            "read_ledger": [],
            "invariant_read_count": 0,
        },
        "turn": {"index": 0, "decision_gate_seen": False},
    }


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload))
    sys.stdout.write("\n")


def emit_context(event_name: str, text: str) -> None:
    emit({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        },
    })


def emit_block(reason: str, hook_event: str | None = None) -> None:
    # PreToolUse supports hookSpecificOutput.permissionDecision; other events use decision=block.
    if hook_event == "PreToolUse":
        emit({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        })
    else:
        emit({"decision": "block", "reason": reason})


def relpath_from_project(path_str: str) -> str:
    """Normalize any absolute / relative path into a project-rooted relative path using forward slashes."""
    if not path_str:
        return ""
    p = pathlib.Path(path_str)
    root = project_dir().resolve()
    try:
        if p.is_absolute():
            rel = p.resolve().relative_to(root)
        else:
            rel = (root / p).resolve().relative_to(root)
        return rel.as_posix()
    except (ValueError, OSError):
        return p.as_posix().lstrip("./")


def is_under_knowledge(rel_path: str) -> bool:
    return rel_path.startswith("knowledge/")


def invariants_present() -> list[str]:
    inv = project_dir() / REQUIRED_INVARIANTS_DIR
    if not inv.is_dir():
        return []
    return sorted(f.name for f in inv.glob("*.md") if f.is_file())


def bootstrap_complete(state: dict[str, Any]) -> bool:
    return state.get("bootstrap", {}).get("status") == "completed"


def mark_bootstrap_if_complete(state: dict[str, Any]) -> bool:
    """Upgrade bootstrap.status to 'completed' iff the read-ledger covers required files and at least one invariant."""
    bs = state.setdefault("bootstrap", {})
    if bs.get("status") == "completed":
        return True
    read = set(bs.get("read_ledger", []))
    required = set(bs.get("required_files", REQUIRED_FILES))
    if not required.issubset(read):
        return False
    if bs.get("invariant_read_count", 0) < 1:
        return False
    bs["status"] = "completed"
    return True


def read_transcript_current_turn(transcript_path: str) -> str:
    """Return concatenated assistant text emitted since the most recent user message."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return ""
    try:
        with open(transcript_path) as f:
            msgs = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError):
        return ""
    # Find index of last user message.
    last_user_idx = -1
    for i, m in enumerate(msgs):
        if _role_of(m) != "user":
            continue
        c = m.get("message", {}).get("content") if isinstance(m.get("message"), dict) else m.get("content")
        if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            continue
        last_user_idx = i
    texts: list[str] = []
    for m in msgs[last_user_idx + 1 :]:
        if _role_of(m) != "assistant":
            continue
        content = _content_of(m)
        if isinstance(content, str):
            texts.append(content)
            continue
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    texts.append(str(c.get("text", "")))
    return "\n".join(texts)


def _role_of(msg: dict[str, Any]) -> str:
    t = msg.get("type")
    if t in ("user", "assistant"):
        return t
    inner = msg.get("message")
    if isinstance(inner, dict):
        return str(inner.get("role", ""))
    return ""


def _content_of(msg: dict[str, Any]) -> Any:
    if "content" in msg:
        return msg["content"]
    inner = msg.get("message")
    if isinstance(inner, dict):
        return inner.get("content")
    return None


def find_decision_gate(text: str) -> str | None:
    m = DECISION_GATE_RE.search(text or "")
    return m.group(1).lower() if m else None


def find_closure_block(text: str):
    return CLOSURE_BLOCK_RE.search(text or "")


def find_bootstrap_confirmation(text: str) -> bool:
    return bool(BOOTSTRAP_CONFIRMATION_RE.search(text or ""))


def emit_and_exit(payload: dict[str, Any], code: int = 0) -> None:
    emit(payload)
    sys.exit(code)
