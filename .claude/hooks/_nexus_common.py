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
import time
from typing import Any, Callable

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


def read_transcript_current_turn(
    transcript_path: str,
    until: "Callable[[str], Any] | None" = None,
    attempts: int = 4,
    delay: float = 0.08,
) -> str:
    """Return concatenated assistant text emitted since the most recent user message.

    The transcript is read from disk, but Claude Code persists the assistant's
    text blocks asynchronously: a Stop or PreToolUse hook can run before the
    block carrying the Closure Block / Context Decision has been flushed. The
    gates then see a non-empty-but-incomplete turn and block a compliant
    response.

    `until` is a predicate over the turn text. When supplied, the file is
    re-read up to `attempts` times until the predicate is satisfied. A
    compliant turn matches on the first read and pays nothing; only the
    genuinely-missing case pays the full (attempts-1) * delay budget, which
    at the defaults is 240 ms against a 15 s hook timeout.
    """
    for attempt in range(attempts):
        text = _read_transcript_once(transcript_path)
        if until is None or until(text):
            return text
        if attempt < attempts - 1:
            time.sleep(delay)
    return text


def _read_transcript_once(transcript_path: str) -> str:
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


# ---------------------------------------------------------------------------
# Context Decision claim (tool-carried form of the decision)
#
# The text form above depends on the assistant's text being persisted to the
# transcript verbatim. Some Claude Code builds persist mid-turn text as a
# paraphrased "narration" thinking block instead, and the gate then denies a
# compliant turn. Tool calls are persisted verbatim and arrive in tool_input,
# so a Bash call of fixed form is accepted as the decision. One parser serves
# both the gate (from the command line) and tools/nexus-decide.py (from argv).
# Contract: knowledge/specs/spec--system--context-decision-gate.md
# ---------------------------------------------------------------------------

DECISION_CLAIM_SCRIPT = "tools/nexus-decide.py"
DECISION_CLAIM_MIN_REASON = 15
DECISION_CLAIM_USAGE = (
    "python3 tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason \"<why>\"\n"
    "python3 tools/nexus-decide.py --kb NO --reason \"<why the KB is not needed and what risk is accepted>\""
)
_CLAIM_INTERPRETERS = {"python3", "python"}
_CLAIM_OPTIONS = {"--kb", "--reason", "--reads"}
_SHELL_PUNCTUATION = {";", "&", "&&", "|", "||", "<", ">", ">>", "<<", "(", ")"}


def parse_decision_claim_args(argv: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    """Validate claim arguments (everything after the script path).

    Returns (claim, None) when valid, (None, error) otherwise. `claim` is
    {"kb": "yes"|"no", "reason": str, "reads": [project-relative paths], "via": "claim"}.
    """
    kb: str | None = None
    reason: str | None = None
    reads: list[str] = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok not in _CLAIM_OPTIONS:
            return None, f"unexpected argument {tok!r}; only --kb, --reason, --reads are accepted"
        if tok == "--reads":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                reads.append(argv[i])
                i += 1
            continue
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            return None, f"{tok} requires a value"
        if tok == "--kb":
            kb = argv[i + 1]
        else:
            reason = argv[i + 1]
        i += 2

    if kb is None:
        return None, "--kb YES|NO is required"
    kb_norm = kb.strip().lower()
    if kb_norm not in ("yes", "no"):
        return None, f"--kb must be YES or NO, got {kb!r}"
    if reason is None or not reason.strip():
        return None, "--reason is required and must not be empty"
    reason = " ".join(reason.split())
    if len(reason) < DECISION_CLAIM_MIN_REASON:
        return None, (
            f"--reason is too short ({len(reason)} chars, minimum {DECISION_CLAIM_MIN_REASON}); "
            "state why the KB is or is not needed, and for NO what risk is accepted"
        )
    if kb_norm == "yes" and not reads:
        return None, "--kb YES requires --reads with at least one vault document to read"
    rel_reads: list[str] = []
    root = project_dir()
    for p in reads:
        rel = relpath_from_project(p)
        if not rel or not (root / rel).is_file():
            return None, f"--reads path {p!r} is not an existing file under the project"
        rel_reads.append(rel)
    return {"kb": kb_norm, "reason": reason, "reads": rel_reads, "via": "claim"}, None


def parse_decision_claim(command: str) -> tuple[dict[str, Any] | None, str | None]:
    """Recognise a Context Decision claim in a Bash command line.

    Returns (claim, None) for a well-formed claim, (None, error) when the
    command invokes the claim script but is malformed, and (None, None) when
    the command is not a claim at all.
    """
    import shlex

    if not command or "nexus-decide.py" not in command:
        return None, None
    if "\n" in command:
        return None, "a claim must be a single line"
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError as exc:
        return None, f"cannot parse command: {exc}"

    # Tolerate a leading `cd <dir> &&`: the Bash tool resets its cwd between calls.
    if len(tokens) >= 4 and tokens[0] == "cd" and tokens[2] == "&&":
        tokens = tokens[3:]

    idx = next((i for i, t in enumerate(tokens) if pathlib.PurePosixPath(t).name == "nexus-decide.py"), None)
    if idx is None:
        return None, "nexus-decide.py must be invoked directly"
    if not (idx == 0 or (idx == 1 and tokens[0] in _CLAIM_INTERPRETERS)):
        return None, "a claim must be a single command: [python3] tools/nexus-decide.py ..."
    if relpath_from_project(tokens[idx]) != DECISION_CLAIM_SCRIPT:
        return None, f"claim script must be {DECISION_CLAIM_SCRIPT} inside the project"

    args = tokens[idx + 1 :]
    for tok in args:
        if tok in _SHELL_PUNCTUATION:
            return None, f"shell operator {tok!r} is not allowed in a claim"
        if "$(" in tok or "`" in tok:
            return None, "command substitution is not allowed in a claim"
    return parse_decision_claim_args(args)


def find_closure_block(text: str):
    return CLOSURE_BLOCK_RE.search(text or "")


def find_bootstrap_confirmation(text: str) -> bool:
    return bool(BOOTSTRAP_CONFIRMATION_RE.search(text or ""))


def emit_and_exit(payload: dict[str, Any], code: int = 0) -> None:
    emit(payload)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Core freeze (spec--system--nexus-update.md §6)
#
# In a host project every unit with strategy "replace" in .nexus/installed.json
# is Nexus core. Hosts do not edit the core; the editing tools are denied on
# such paths unless the path is listed in .nexus/unlock.txt. The freeze is
# inactive when installed.json is absent, so it never applies in the template.
# ---------------------------------------------------------------------------

INSTALLED_FILE = ".nexus/installed.json"
UNLOCK_FILE = ".nexus/unlock.txt"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
FEEDBACK_DIR = "knowledge/feedback"


def core_paths() -> tuple[set[str], str]:
    """Return (frozen relative paths, installed nexus_version); empty set when no baseline."""
    p = project_dir() / INSTALLED_FILE
    if not p.is_file():
        return set(), ""
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set(), ""
    units = data.get("units") or {}
    paths = {uid for uid, rec in units.items()
             if isinstance(rec, dict) and rec.get("strategy") == "replace" and "#" not in uid}
    return paths, str(data.get("nexus_version") or "")


def unlocked_paths() -> set[str]:
    p = project_dir() / UNLOCK_FILE
    if not p.is_file():
        return set()
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")}


def core_freeze_reason(tool: str, tool_input: dict[str, Any]) -> str | None:
    """Deny reason when `tool` would edit a frozen core path; None otherwise."""
    if tool not in EDIT_TOOLS:
        return None
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        return None
    rel = relpath_from_project(file_path)
    frozen, version = core_paths()
    if rel not in frozen or rel in unlocked_paths():
        return None
    return (
        f"NEXUS CORE FILE: {rel} is owned by Nexus {version or '(version unknown)'}. "
        "Hosts do not edit the core. Record the change as a feedback note "
        f"({FEEDBACK_DIR}/) so it reaches Nexus upstream and comes back with the next update; "
        f"if it cannot wait, unlock the path by listing it in {UNLOCK_FILE} (operator decision) "
        "and expect `python3 tools/nexus-update.py status` to report it as customized from then on."
    )
