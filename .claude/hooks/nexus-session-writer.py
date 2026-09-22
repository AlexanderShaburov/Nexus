#!/usr/bin/env python3
"""Nexus session-writer hook (Stop event).

Reads the transcript for the current Claude Code session, extracts the
user-typed prompts and the assistant's text responses (filtering out
tool calls, tool results, thinking blocks, and system-reminder tags),
and writes a curated Markdown archive to knowledge/sessions/.

Idempotent per session: the same file is overwritten on every Stop
event. The filename incorporates an optional theme read from
.nexus/session-theme.txt; when the theme changes, the file is renamed
in place so history stays in a single document per session.

Silent by design: the hook emits nothing on stdout and must not
interfere with the exit gate, which is scheduled in the same Stop
event and runs alongside.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    project_dir,
    read_hook_input,
    _role_of,
    _content_of,
)

SLUG_RE = re.compile(r"[^\w\-]+", re.UNICODE)
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL | re.IGNORECASE)
COMMAND_TAG_RE = re.compile(r"<command-[a-z-]+>.*?</command-[a-z-]+>", re.DOTALL | re.IGNORECASE)


def slugify(text: str, default: str = "unnamed", maxlen: int = 60) -> str:
    text = (text or "").strip().lower()
    text = SLUG_RE.sub("-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:maxlen] or default


def clean_user_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = SYSTEM_REMINDER_RE.sub("", text)
    text = COMMAND_TAG_RE.sub("", text)
    return text.strip()


def extract_user_prompt(msg: dict) -> str | None:
    content = _content_of(msg)
    if isinstance(content, str):
        cleaned = clean_user_text(content)
        return cleaned or None
    if isinstance(content, list):
        text_parts: list[str] = []
        has_tool_result = False
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_result":
                has_tool_result = True
                continue
            if btype == "text":
                text_parts.append(str(block.get("text", "")))
        if has_tool_result and not text_parts:
            return None
        cleaned = clean_user_text("\n".join(text_parts))
        return cleaned or None
    return None


def extract_assistant_text(msg: dict) -> str:
    content = _content_of(msg)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts).strip()
    return ""


def read_turns(transcript_path: str) -> list[tuple[str, str]]:
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    turns: list[tuple[str, str]] = []
    current_user: str | None = None
    current_assistant: list[str] = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = _role_of(entry)
                if role == "user":
                    prompt = extract_user_prompt(entry)
                    if prompt is None:
                        continue
                    if current_user is not None:
                        turns.append((current_user, "\n\n".join(current_assistant).strip()))
                    current_user = prompt
                    current_assistant = []
                elif role == "assistant":
                    text = extract_assistant_text(entry)
                    if text:
                        current_assistant.append(text)
    except OSError:
        return turns
    if current_user is not None:
        turns.append((current_user, "\n\n".join(current_assistant).strip()))
    return turns


def read_theme() -> str:
    marker = project_dir() / ".nexus" / "session-theme.txt"
    if not marker.exists():
        return ""
    try:
        return marker.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def read_previous_file(session_id: str) -> pathlib.Path | None:
    """Return the archive this *same* session already owns, if any.

    The marker is session-scoped on purpose. It outlives the session that
    wrote it, so an unscoped marker would make the next session treat the
    previous session's archive as its own stale filename and rename +
    overwrite it, destroying that session's log. Only a session_id match
    authorizes the rename.

    Legacy plain-path markers (no session_id) are ignored rather than
    trusted: their owner is unknown, so renaming is unsafe.
    """
    marker = project_dir() / ".nexus" / "session-file.txt"
    if not marker.exists():
        return None
    try:
        raw = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    if data.get("session_id") != session_id:
        return None
    path = data.get("path")
    return pathlib.Path(path) if path else None


def write_previous_file(path: pathlib.Path, session_id: str) -> None:
    marker = project_dir() / ".nexus" / "session-file.txt"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"session_id": session_id, "path": str(path)}, ensure_ascii=False),
        encoding="utf-8",
    )


def preserve_created(path: pathlib.Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return fallback
    m = re.search(r"^created:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def build_markdown(turns, theme, session_id, created_iso, updated_iso, date_str) -> str:
    lines: list[str] = ["---",
                        "type: session",
                        "scope: general",
                        "status: draft",
                        f"created: {created_iso}",
                        f"updated: {updated_iso}",
                        "source_of_truth: false",
                        "knowledge_visibility: historical",
                        "tags: [session, auto-log, transcript]"]
    if theme:
        lines.append(f"theme: {theme}")
    lines.append(f"session_id: {session_id}")
    lines.append("---")
    lines.append("")
    heading = f"# Session {date_str}"
    if theme:
        heading += f" — {theme}"
    lines.append(heading)
    lines.append("")
    lines.append("_Auto-generated by nexus-session-writer. Rewritten in place on each Stop event._")
    lines.append("")
    for i, (user_text, assistant_text) in enumerate(turns, 1):
        lines.append(f"## Turn {i}")
        lines.append("")
        lines.append("**User:**")
        lines.append("")
        lines.append(user_text.strip())
        lines.append("")
        if assistant_text:
            lines.append("**Assistant:**")
            lines.append("")
            lines.append(assistant_text.strip())
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = read_hook_input()
    session_id = str(payload.get("session_id") or "unknown")
    transcript_path = payload.get("transcript_path") or ""

    turns = read_turns(transcript_path)
    if not turns:
        return

    theme = read_theme()
    theme_slug = slugify(theme, default="unnamed")
    session_short = session_id[:8] if session_id != "unknown" else "unknown"
    today = datetime.date.today().isoformat()
    filename = f"session--{theme_slug}--{today}--{session_short}.md"
    sessions_dir = project_dir() / "knowledge" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    target = sessions_dir / filename

    prev = read_previous_file(session_id)
    if prev is not None and prev.exists():
        try:
            same = prev.resolve() == target.resolve()
        except OSError:
            same = False
        # Never clobber an existing archive that belongs to another session.
        if not same and not target.exists():
            try:
                prev.rename(target)
            except OSError:
                pass

    now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    created_iso = preserve_created(target, now_iso)

    md = build_markdown(turns, theme, session_id, created_iso, now_iso, today)
    try:
        target.write_text(md, encoding="utf-8")
        write_previous_file(target, session_id)
    except OSError:
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
