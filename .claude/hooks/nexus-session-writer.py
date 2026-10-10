#!/usr/bin/env python3
"""Nexus session-writer hook (Stop event).

Reads the transcript for the current Claude Code session, extracts the
user-typed prompts and the assistant's text responses (filtering out
tool calls, tool results, thinking blocks, and system-reminder tags),
and writes a curated Markdown archive to knowledge/sessions/.

Idempotent per session: the same file is overwritten on every Stop
event. The filename incorporates an optional theme read from
.nexus/session-theme.txt; when the theme changes, the file is renamed
in place so history stays in a single document per session. The date
segment of the filename is fixed by the session's first archive: a
session that runs past midnight keeps its name (found live 2026-10-10
in a host, where the archive was renamed on the last Stop and the
summary written in the same session pointed at the old name).

Claude Code persists the final assistant record asynchronously, so a
Stop hook can read the transcript before the answer has landed. The
exit gate re-reads until it sees the Closure Block; this writer does the
same, with a bounded budget, before archiving (found 2026-10-03, and
again live on 2026-10-10: six of fifteen archives lacked their last
answer).

Silent by design: the hook emits nothing on stdout and must not
interfere with the exit gate, which is scheduled in the same Stop
event and runs alongside.

`--selftest` runs the hook against synthetic transcripts in a temporary
project directory and exits 0 only if every check passes.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import (  # noqa: E402
    project_dir,
    read_hook_input,
    find_closure_block,
    _role_of,
    _content_of,
)

SLUG_RE = re.compile(r"[^\w\-]+", re.UNICODE)
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL | re.IGNORECASE)
COMMAND_TAG_RE = re.compile(r"<command-[a-z-]+>.*?</command-[a-z-]+>", re.DOTALL | re.IGNORECASE)
ARCHIVE_DATE_RE = re.compile(r"--(\d{4}-\d{2}-\d{2})--[0-9a-f]{8}\.md$")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

# The final assistant record is flushed asynchronously; wait for it in small
# steps. A complete turn is detected on the first read and pays nothing. Only
# a turn whose answer is genuinely absent (the exit gate is blocking it, and a
# later Stop will rewrite the archive anyway) pays the full budget.
SETTLE_ATTEMPTS = 12
SETTLE_DELAY = 0.15


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


def turn_is_complete(turns: list[tuple[str, str]]) -> bool:
    """A finished turn ends with the Closure Block the exit gate requires."""
    return bool(turns) and find_closure_block(turns[-1][1]) is not None


def read_turns_settled(
    transcript_path: str,
    attempts: int = SETTLE_ATTEMPTS,
    delay: float = SETTLE_DELAY,
) -> list[tuple[str, str]]:
    turns = read_turns(transcript_path)
    for _ in range(attempts - 1):
        if not turns or turn_is_complete(turns):
            break
        time.sleep(delay)
        turns = read_turns(transcript_path)
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


def archive_date(prev: pathlib.Path, today: str) -> str:
    """The date segment of a session's archive is set once, at its first write.

    Taken from the filename the session already owns; from its `created:`
    when the name does not carry one; from today only for the first write.
    """
    m = ARCHIVE_DATE_RE.search(prev.name)
    if m:
        return m.group(1)
    m = DATE_PREFIX_RE.match(preserve_created(prev, ""))
    return m.group(0) if m else today


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

    turns = read_turns_settled(transcript_path)
    if not turns:
        return

    theme = read_theme()
    theme_slug = slugify(theme, default="unnamed")
    session_short = session_id[:8] if session_id != "unknown" else "unknown"
    today = datetime.date.today().isoformat()

    prev = read_previous_file(session_id)
    if prev is not None and not prev.exists():
        prev = None
    date_str = archive_date(prev, today) if prev is not None else today

    filename = f"session--{theme_slug}--{date_str}--{session_short}.md"
    sessions_dir = project_dir() / "knowledge" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    target = sessions_dir / filename

    if prev is not None:
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

    md = build_markdown(turns, theme, session_id, created_iso, now_iso, date_str)
    try:
        target.write_text(md, encoding="utf-8")
        write_previous_file(target, session_id)
    except OSError:
        return


# ---------------------------------------------------------------------------
# Self-test: synthetic transcripts in a temporary project directory.
# ---------------------------------------------------------------------------

CLOSURE = (
    "Closure Block:\n- code changed: no\n- KB changed: no\n"
    "- session log written: no\n- writeback evaluation performed: yes\n"
)


def _rec(role: str, text: str) -> str:
    if role == "user":
        return json.dumps({"type": "user", "message": {"role": "user", "content": text}})
    return json.dumps({"type": "assistant", "message": {
        "role": "assistant", "content": [{"type": "text", "text": text}]}})


def _run_hook(project: pathlib.Path, session_id: str, transcript: pathlib.Path) -> tuple[float, bytes]:
    import subprocess
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    payload = json.dumps({"session_id": session_id, "transcript_path": str(transcript),
                          "hook_event_name": "Stop", "cwd": str(project)})
    t0 = time.monotonic()
    out = subprocess.run([sys.executable, os.path.abspath(__file__)], input=payload.encode(),
                         capture_output=True, env=env, cwd=str(project), timeout=30)
    return time.monotonic() - t0, out.stdout


def _selftest() -> int:
    import tempfile
    import threading

    failures: list[str] = []

    def check(cond: bool, name: str) -> None:
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    sid = "sess0001-0000-0000-0000-000000000000"
    today = datetime.date.today().isoformat()

    with tempfile.TemporaryDirectory() as tmp:
        project = pathlib.Path(tmp)
        sessions = project / "knowledge" / "sessions"
        nexus = project / ".nexus"
        nexus.mkdir()
        (nexus / "session-theme.txt").write_text("alpha", encoding="utf-8")
        transcript = project / "t.jsonl"

        # 1. complete turn: archived on the first read, no wait, silent
        transcript.write_text(_rec("user", "hello") + "\n" + _rec("assistant", "answer one\n\n" + CLOSURE) + "\n",
                              encoding="utf-8")
        elapsed, stdout = _run_hook(project, sid, transcript)
        first = sessions / f"session--alpha--{today}--sess0001.md"
        check(first.exists(), "complete turn: archive written with today's date")
        check(stdout == b"", "complete turn: nothing on stdout")
        check(elapsed < 1.0, f"complete turn: no settle wait ({elapsed:.2f}s)")
        check("answer one" in first.read_text(encoding="utf-8"), "complete turn: answer archived")

        # 2. midnight: the session already owns an archive dated yesterday; the name is kept
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        old = sessions / f"session--alpha--{yesterday}--sess0001.md"
        first.rename(old)
        text = old.read_text(encoding="utf-8").replace(f"created: {today}", f"created: {yesterday}", 1)
        old.write_text(text, encoding="utf-8")
        (nexus / "session-file.txt").write_text(json.dumps({"session_id": sid, "path": str(old)}), encoding="utf-8")
        transcript.write_text(transcript.read_text(encoding="utf-8")
                              + _rec("user", "second") + "\n" + _rec("assistant", "answer two\n\n" + CLOSURE) + "\n",
                              encoding="utf-8")
        _run_hook(project, sid, transcript)
        archives = sorted(p.name for p in sessions.glob("session--*.md"))
        check(archives == [old.name], f"midnight: one archive, name kept ({archives})")
        body = old.read_text(encoding="utf-8")
        check(f"created: {yesterday}" in body, "midnight: created preserved")
        check("answer two" in body and f"# Session {yesterday}" in body, "midnight: content and heading date from the first write")
        marker = json.loads((nexus / "session-file.txt").read_text(encoding="utf-8"))
        check(marker["path"] == str(old), "midnight: marker still points at the kept name")

        # 3. theme change within the session: rename, date kept, still one file
        (nexus / "session-theme.txt").write_text("beta", encoding="utf-8")
        _run_hook(project, sid, transcript)
        renamed = sessions / f"session--beta--{yesterday}--sess0001.md"
        archives = sorted(p.name for p in sessions.glob("session--*.md"))
        check(archives == [renamed.name], f"theme change: renamed, date kept, one file ({archives})")

        # 4. another session with a marker left behind: new file, the old one untouched
        other = "sess0002-0000-0000-0000-000000000000"
        before = renamed.read_text(encoding="utf-8")
        t2 = project / "t2.jsonl"
        t2.write_text(_rec("user", "other hello") + "\n" + _rec("assistant", "other answer\n\n" + CLOSURE) + "\n",
                      encoding="utf-8")
        _run_hook(project, other, t2)
        fresh = sessions / f"session--beta--{today}--sess0002.md"
        check(fresh.exists(), "foreign marker: new session gets its own archive")
        check(renamed.read_text(encoding="utf-8") == before, "foreign marker: previous archive untouched")

        # 5. race: the final assistant record lands after the hook has started
        t3 = project / "t3.jsonl"
        t3.write_text(_rec("user", "race hello") + "\n", encoding="utf-8")
        late = "late answer\n\n" + CLOSURE

        def append_late() -> None:
            time.sleep(0.4)
            with open(t3, "a", encoding="utf-8") as fh:
                fh.write(_rec("assistant", late) + "\n")

        racer = "sess0003-0000-0000-0000-000000000000"
        th = threading.Thread(target=append_late)
        th.start()
        elapsed, _ = _run_hook(project, racer, t3)
        th.join()
        raced = sessions / f"session--beta--{today}--sess0003.md"
        check(raced.exists() and "late answer" in raced.read_text(encoding="utf-8"),
              f"race: late answer archived after {elapsed:.2f}s")

        # 6. answer never arrives: the wait is bounded and the turn is still archived
        t4 = project / "t4.jsonl"
        t4.write_text(_rec("user", "no answer") + "\n", encoding="utf-8")
        elapsed, _ = _run_hook(project, "sess0004-0000-0000-0000-000000000000", t4)
        budget = SETTLE_ATTEMPTS * SETTLE_DELAY + 2.0
        bounded = sessions / f"session--beta--{today}--sess0004.md"
        check(elapsed < budget, f"no answer: bounded wait ({elapsed:.2f}s < {budget:.1f}s)")
        check(bounded.exists() and "no answer" in bounded.read_text(encoding="utf-8"),
              "no answer: turn archived without an answer")

        # 7. empty payload stays silent (validation plan S4)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
        import subprocess
        out = subprocess.run([sys.executable, os.path.abspath(__file__)], input=b"{}",
                             capture_output=True, env=env, cwd=str(project), timeout=30)
        check(out.stdout == b"" and out.returncode == 0, "empty payload: silent, exit 0")

    print(f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(_selftest())
    try:
        main()
    except Exception:
        sys.exit(0)
