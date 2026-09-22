#!/usr/bin/env python3
"""Nexus one-file bootstrap: install, retrofit or update Nexus in the current directory.

    python3 nexus.py            # dry-run: shows what would change
    python3 nexus.py --apply    # writes, with backups

or, without copying anything first:

    curl -fsSL https://raw.githubusercontent.com/AlexanderShaburov/Nexus/main/nexus.py | python3 - --apply

What it does, and nothing more:
  1. makes sure `git` exists;
  2. clones (bare) or fetches the Nexus repository into the local cache
     (${NEXUS_UPSTREAM_CACHE:-~/.cache/nexus}/template), never into this directory;
  3. picks the highest v* tag (or --ref);
  4. extracts tools/nexus-update.py from that tag into a temporary file and runs
     `nexus-update.py up` here, passing every argument through.

`up` decides: no Nexus here → install; Nexus without .nexus/installed.json →
retrofit (guess the installed version, record it, update); baseline → update.
Dry-run by default. After a first install the project carries its own
tools/nexus-update.py and `python3 tools/nexus-update.py up` does the same.

Stdlib only. Template-only file: it is not delivered to hosts.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_UPSTREAM = "https://github.com/AlexanderShaburov/Nexus.git"
UPDATER_PATH = "tools/nexus-update.py"
SEMVER_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def die(msg: str, code: int = 3) -> None:
    print(f"nexus.py: {msg}", file=sys.stderr)
    sys.exit(code)


def git(repo: pathlib.Path | None, *args: str, timeout: int = 300) -> str:
    cmd = ["git"] + (["-C", str(repo)] if repo is not None else []) + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=GIT_ENV, timeout=timeout)
    except FileNotFoundError:
        die("git is not installed")
    except subprocess.TimeoutExpired:
        die(f"git {' '.join(args)} timed out")
    if r.returncode != 0:
        die((r.stderr or r.stdout).strip() or f"git {' '.join(args)} failed")
    return r.stdout


def cache_root() -> pathlib.Path:
    env = os.environ.get("NEXUS_UPSTREAM_CACHE")
    if env:
        return pathlib.Path(env).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = pathlib.Path(xdg).expanduser() if xdg else pathlib.Path.home() / ".cache"
    return base / "nexus"


def cache_repo_for(url: str) -> pathlib.Path:
    root = cache_root()
    default = root / "template"
    if default.is_dir():
        r = subprocess.run(["git", "-C", str(default), "remote", "get-url", "origin"],
                           capture_output=True, text=True, env=GIT_ENV)
        if r.returncode == 0 and r.stdout.strip() == url:
            return default
        return root / f"template-{hashlib.sha1(url.encode()).hexdigest()[:8]}"
    return default


def ensure_cache(url: str, offline: bool) -> pathlib.Path:
    repo = cache_repo_for(url)
    if not repo.is_dir():
        if offline:
            die(f"offline and no cache for {url} at {repo}")
        repo.parent.mkdir(parents=True, exist_ok=True)
        tmp = repo.with_name(repo.name + ".partial")
        shutil.rmtree(tmp, ignore_errors=True)
        git(None, "clone", "--bare", "--quiet", url, str(tmp))
        git(tmp, "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
        git(tmp, "fetch", "--quiet", "--tags", "--prune", "origin")
        os.replace(tmp, repo)
    elif not offline:
        git(repo, "fetch", "--quiet", "--tags", "--prune", "origin")
    return repo


def select_ref(repo: pathlib.Path, explicit: str | None) -> str:
    if explicit:
        for cand in (explicit, f"refs/tags/{explicit}", f"refs/remotes/origin/{explicit}"):
            r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}"],
                               capture_output=True, text=True, env=GIT_ENV)
            if r.returncode == 0:
                return cand
        die(f"ref {explicit!r} not found upstream")
    tags = [(tuple(int(x) for x in m.groups()), t) for t in git(repo, "tag", "-l", "v*").split()
            if (m := SEMVER_RE.match(t))]
    if not tags:
        die("upstream has no v* tags; pass --ref main")
    return f"refs/tags/{max(tags)[1]}"


def main(argv: list[str]) -> int:
    # Only the arguments nexus.py itself needs are parsed here; everything is passed on to `up`.
    upstream = DEFAULT_UPSTREAM
    ref: str | None = None
    offline = False
    project_root = "."
    passthrough: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        if a == "--upstream" and i + 1 < len(argv):
            upstream = argv[i + 1]; passthrough += [a, argv[i + 1]]; i += 2; continue
        if a == "--ref" and i + 1 < len(argv):
            ref = argv[i + 1]; passthrough += [a, argv[i + 1]]; i += 2; continue
        if a == "--project-root" and i + 1 < len(argv):
            project_root = argv[i + 1]; i += 2; continue
        if a == "--offline":
            offline = True
        passthrough.append(a)
        i += 1

    if pathlib.Path(upstream).expanduser().is_dir():
        # A local checkout: read the updater from its working tree (or --ref inside it).
        repo = pathlib.Path(upstream).expanduser().resolve()
        if ref:
            chosen = select_ref(repo, ref)
            updater_src = git(repo, "show", f"{chosen}:{UPDATER_PATH}")
            label = chosen
        else:
            updater_src = (repo / UPDATER_PATH).read_text(encoding="utf-8")
            label = "worktree"
    else:
        repo = ensure_cache(upstream, offline)
        chosen = select_ref(repo, ref)
        updater_src = git(repo, "show", f"{chosen}:{UPDATER_PATH}")
        label = chosen
    if "def cmd_up(" not in updater_src:
        die(f"{UPDATER_PATH} at {label.replace('refs/tags/', '')} predates the installer (no `up` subcommand). "
            "Use a release that carries it (v1.2.0 or later), or pass --ref main.")
    print(f"nexus.py: running {UPDATER_PATH} from {upstream} @ {label.replace('refs/tags/', '')}\n", flush=True)

    with tempfile.TemporaryDirectory(prefix="nexus-bootstrap-") as td:
        updater = pathlib.Path(td) / "nexus-update.py"
        updater.write_text(updater_src, encoding="utf-8")
        cmd = [sys.executable, str(updater), "--project-root", project_root, "up", *passthrough]
        return subprocess.call(cmd, env=GIT_ENV)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
