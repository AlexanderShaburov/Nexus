#!/usr/bin/env python3
"""Nexus: SessionStart hook — is a newer Nexus tagged upstream? (non-enforcing)

Contract: spec--system--nexus-update.md §7. This hook gates nothing, blocks
nothing, and is silent on every path but one: when the highest v* tag
upstream is newer than the version recorded in .nexus/installed.json, it emits
a single line of additionalContext naming both versions and the command that
shows what would change. Nothing is ever applied here.

Guarantees:
- no baseline (.nexus/installed.json absent) → exit 0, no output: the project
  was never baselined, and the installation guide, not every session start,
  is where that is explained;
- throttled: .nexus/update-check.json younger than 24 h is reused, no network;
- one network call, `git ls-remote --tags <url>`, 5 s timeout, no credential
  prompt (GIT_TERMINAL_PROMPT=0), no object fetch, no cache clone;
- any failure (offline, no credentials, no git, no tags, malformed files) is
  recorded in .nexus/update-check.json as `unreachable` / `no-tags` so the
  next 24 h stay quiet, and the hook exits 0 without output;
- exceptions are swallowed, like the session writer, so this hook can never
  interfere with the bootstrap hook scheduled on the same event.

The record it writes is the same shape `tools/nexus-update.py check` writes, so
either side can refresh it and `status` prints it.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import emit_context, project_dir, read_hook_input  # noqa: E402

INSTALLED_FILE = ".nexus/installed.json"
UPDATE_CHECK_FILE = ".nexus/update-check.json"
THROTTLE_SECONDS = 24 * 60 * 60
LS_REMOTE_TIMEOUT = 5
TAG_RE = re.compile(r"^([0-9a-f]{40})\s+refs/tags/v(\d+)\.(\d+)\.(\d+)$")
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def _now() -> datetime.datetime:
    return datetime.datetime.now().replace(microsecond=0)


def _semver(text: str) -> tuple[int, int, int] | None:
    m = SEMVER_RE.match((text or "").strip())
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def _load_json(path: pathlib.Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_record(path: pathlib.Path, record: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass


def _fresh(record: dict | None) -> bool:
    if not record:
        return False
    try:
        checked = datetime.datetime.fromisoformat(str(record.get("checked_at")))
    except ValueError:
        return False
    return (_now() - checked).total_seconds() < THROTTLE_SECONDS


def _ls_remote_highest_tag(url: str) -> tuple[str | None, str | None, str | None]:
    """Return (version, ref, commit) of the highest v* tag, or (None, None, error)."""
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    try:
        r = subprocess.run(["git", "ls-remote", "--tags", url], capture_output=True, text=True,
                           env=env, timeout=LS_REMOTE_TIMEOUT)
    except FileNotFoundError:
        return None, None, "git not installed"
    except subprocess.TimeoutExpired:
        return None, None, f"ls-remote timed out after {LS_REMOTE_TIMEOUT}s"
    if r.returncode != 0:
        return None, None, (r.stderr or "ls-remote failed").strip().splitlines()[-1][:200]
    best: tuple[tuple[int, int, int], str, str] | None = None
    for line in r.stdout.splitlines():
        m = TAG_RE.match(line.strip())
        if not m:
            continue
        ver = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
        if best is None or ver > best[0]:
            best = (ver, f"v{ver[0]}.{ver[1]}.{ver[2]}", m.group(1))
    if best is None:
        return None, None, "no v* tags upstream"
    return best[1][1:], best[1], best[2]


def main() -> int:
    inp = read_hook_input()
    event = inp.get("hook_event_name") or "SessionStart"
    root = project_dir()

    installed = _load_json(root / INSTALLED_FILE)
    if not installed:
        return 0
    have = _semver(str(installed.get("nexus_version", "")))
    url = (installed.get("upstream") or {}).get("url")
    if have is None or not url:
        return 0

    record_path = root / UPDATE_CHECK_FILE
    record = _load_json(record_path)
    if not _fresh(record):
        version, ref, error = _ls_remote_highest_tag(url)
        record = {
            "checked_at": _now().isoformat(),
            "status": "ok" if version else ("no-tags" if error and error.startswith("no v*") else "unreachable"),
            "upstream_version": version,
            "upstream_ref": ref,
            "upstream_commit": None,
            "via": "hook",
        }
        if error:
            record["error"] = error
        _write_record(record_path, record)

    if record.get("status") != "ok":
        return 0
    upstream = _semver(str(record.get("upstream_version", "")))
    if upstream is None or upstream <= have:
        return 0
    up_s = ".".join(map(str, upstream))
    have_s = ".".join(map(str, have))
    emit_context(event, (
        f"Nexus {up_s} is available upstream ({record.get('upstream_ref')}); this project has {have_s}. "
        "Run `python3 tools/nexus-update.py plan` to see what would change. Nothing has been applied."
    ))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 — silent by design; never interfere with bootstrap
        sys.exit(0)
