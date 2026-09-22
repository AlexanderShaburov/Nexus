#!/usr/bin/env python3
"""Nexus updater — version identity, ownership manifest, baseline, check, plan and apply.

Phases 1–3 of knowledge/plans/plan--system--nexus-self-update.md; contract in
knowledge/specs/spec--system--nexus-update.md. Subcommands:

    manifest generate     (template) write nexus.manifest.json from the tree
    manifest verify       (template) regenerate in memory and diff; used by --selftest
    baseline              (host)     record .nexus/installed.json against an upstream ref
    status                (host)     compare every baselined unit with the working tree
    check                 (host)     is a newer Nexus available upstream? (network: fetch)
    plan                  (host)     the full three-way table: baseline / local / upstream
    apply                 (host)     adopt the target version; dry-run unless --apply
    feedback status|push  (host)     feedback notes about Nexus → the local mailbox in the cache
    feedback list|show|archive (template) triage the mailbox
    --selftest                       prove the rules, the extractors, the table, apply and feedback

Without --apply nothing in a host is written except .nexus/update-check.json
(`check`) and .nexus/installed.json (`baseline`). Stdlib only.

Exit codes: 0 ok / up to date, 1 findings reported (conflicts, unbaselined,
refused), 2 not a Nexus project, 3 upstream unreachable / ref or manifest
missing, 4 internal error, 5 validation failed, 6 no baseline.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import fnmatch
import hashlib
import importlib.util
import json
import os
import pathlib
import posixpath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Iterable

# --------------------------------------------------------------------------
# Constants — mirror plan--system--nexus-self-update.md §3, §4, §5
# --------------------------------------------------------------------------

VERSION_FILE = "nexus.version"
MANIFEST_FILE = "nexus.manifest.json"
INSTALLED_FILE = ".nexus/installed.json"
UNLOCK_FILE = ".nexus/unlock.txt"
UPDATE_CHECK_FILE = ".nexus/update-check.json"
MANIFEST_VERSION = 1
BASELINE_VERSION = 1

STRATEGIES = {
    "replace", "sections", "index-entries", "hooks-merge",
    "ensure-lines", "create-if-absent",
}
COMPARED_STRATEGIES = {"replace", "sections", "index-entries", "hooks-merge"}

# Group order is the order `apply` will write in (plan §7.4).
GROUP_ORDER = ["repo", "runtime", "vault-config", "vault", "instructions", "tools", "hooks"]

# Three-way classes (plan §7.1), in report order. The first three block `apply`.
PLAN_CLASSES = [
    "conflict", "unbaselined", "refused",
    "update", "add", "converged", "adopt",
    "customized", "removed-locally", "obsolete", "mode-drift", "unchanged",
]
BLOCKING_CLASSES = {"conflict", "unbaselined", "refused"}

NEVER_TOUCH = [
    ".nexus/state*.json",
    ".nexus/session-theme.txt",
    ".nexus/session-file.txt",
    ".nexus/installed.json",
    ".nexus/update-check.json",
    ".nexus/unlock.txt",
    ".claude/settings.local.json",
    "knowledge/sessions/**",
    "knowledge/business/**",
    "knowledge/feedback/**",
]

GITIGNORE_LINES = [".nexus/state*.json", ".nexus/backups/", ".nexus/update-check.json"]

# H2 sections of the template's CLAUDE.md that describe the template itself,
# not the protocol. Everything else in CLAUDE.md is Nexus-owned (plan §3.3).
CLAUDE_PROJECT_SECTIONS = {"## What this repository is"}

OBSIDIAN_SHARED = {"app.json", "appearance.json", "core-plugins.json", "graph.json"}

# Template history that is binding by frontmatter but is not part of running
# the system in a host (operator decision 2026-09-22, plan §12 Q8). Listed
# explicitly so the exclusion is visible; a frontmatter demotion would make
# the entry redundant.
TEMPLATE_HISTORY = {
    "knowledge/decisions/adr--system--rename-soki-to-nexus.md",
}

# Paths that never leave the template (plan §3.4 rule 5).
TEMPLATE_ONLY_PREFIXES = ("patches/", "legacy-kb/", "dist/", "docs/", "knowledge/sessions/",
                          "knowledge/business/", "knowledge/feedback/")
TEMPLATE_ONLY_FILES = {
    "README.md", "nexus_approach.md", VERSION_FILE, MANIFEST_FILE, ".DS_Store",
}

HOOK_CMD_RE = re.compile(r"/\.claude/hooks/(nexus-[A-Za-z0-9_-]+\.py)$")
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BULLET_RE = re.compile(r"^\s*[-*]\s+")

GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
GIT_TIMEOUT = 60
GUESS_COMMITS = 50


class UpdaterError(Exception):
    def __init__(self, message: str, code: int = 4):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_semver(text: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(text.strip())
    if not m:
        raise UpdaterError(f"not a semver version: {text.strip()!r}", 4)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def is_semver(text: str) -> bool:
    return bool(SEMVER_RE.match(text.strip()))


def matches_never_touch(rel: str, patterns: Iterable[str] = NEVER_TOUCH) -> bool:
    for pat in patterns:
        if pat.endswith("/**"):
            if rel == pat[:-3] or rel.startswith(pat[:-3] + "/"):
                return True
        elif fnmatch.fnmatchcase(rel, pat):
            return True
    return False


def normalize_text(data: bytes) -> bytes:
    """Line-level units: CRLF → LF, trailing whitespace per line and trailing newlines dropped."""
    text = data.decode("utf-8", errors="surrogateescape").replace("\r\n", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).encode("utf-8", errors="surrogateescape")


def now_iso() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def write_json_atomic(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_validator(root: pathlib.Path):
    """Reuse the frontmatter parser of tools/validate-vault.py (single parser, as the hooks do)."""
    path = root / "tools" / "validate-vault.py"
    if not path.is_file():
        raise UpdaterError(f"{path} is missing; manifest generation needs its frontmatter parser", 3)
    spec = importlib.util.spec_from_file_location("nexus_vault_validator", path)
    if spec is None or spec.loader is None:
        raise UpdaterError("cannot load tools/validate-vault.py", 4)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frontmatter_of(validator, text: str) -> dict:
    m = validator.FRONTMATTER_RE.match(text)
    if not m:
        return {}
    values, _lines, _errors = validator.parse_frontmatter(m.group(1), 2)
    return values


def visibility_class(fm: dict) -> str:
    """spec--system--knowledge-visibility.md: explicit field, else the fallback mapping."""
    explicit = fm.get("knowledge_visibility")
    if isinstance(explicit, str) and explicit in {"binding", "development", "historical"}:
        return explicit
    status = fm.get("status")
    sot = str(fm.get("source_of_truth", "")).lower() == "true"
    if status == "approved" and sot:
        return "binding"
    if status == "deprecated":
        return "historical"
    tags = fm.get("tags") or []
    if isinstance(tags, list) and {t.strip() for t in tags} & {"archived", "legacy", "superseded", "historical"}:
        return "historical"
    return "development"


# --------------------------------------------------------------------------
# Git and sources — where unit content comes from
# --------------------------------------------------------------------------

def git(repo: pathlib.Path | None, *args: str, timeout: int = GIT_TIMEOUT) -> str:
    cmd = ["git"] + (["-C", str(repo)] if repo is not None else []) + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=GIT_ENV, timeout=timeout)
    except FileNotFoundError:
        raise UpdaterError("git is not installed", 3)
    except subprocess.TimeoutExpired:
        raise UpdaterError(f"git {' '.join(args)} timed out after {timeout}s", 3)
    if r.returncode != 0:
        raise UpdaterError((r.stderr or r.stdout).strip() or f"git {' '.join(args)} failed", 3)
    return r.stdout


class WorkTree:
    """A directory on disk (the template checkout, or the host project)."""

    kind = "worktree"

    def __init__(self, root: pathlib.Path):
        self.root = root.resolve()

    def read(self, rel: str) -> bytes | None:
        p = self.root / rel
        if not p.is_file():
            return None
        return p.read_bytes()

    def mode(self, rel: str) -> str | None:
        p = self.root / rel
        if not p.is_file():
            return None
        return "755" if p.stat().st_mode & stat.S_IXUSR else "644"

    def describe(self) -> dict:
        info = {"url": str(self.root), "ref": "worktree", "commit": None}
        try:
            info["commit"] = git(self.root, "rev-parse", "HEAD").strip()
            url = git(self.root, "remote", "get-url", "origin").strip()
            if url:
                info["url"] = url
        except UpdaterError:
            pass
        return info


class GitRef:
    """A ref inside a local git repository (the cache clone or the template checkout)."""

    kind = "gitref"

    def __init__(self, repo: pathlib.Path, ref: str, url: str | None = None):
        self.repo = repo.resolve()
        self.ref = ref
        self.url = url
        try:
            self.commit = git(self.repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").strip()
        except UpdaterError as e:
            raise UpdaterError(f"ref {ref!r} not found in {self.repo}: {e}", 3)
        self._modes: dict[str, str] | None = None

    def read(self, rel: str) -> bytes | None:
        r = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"{self.commit}:{rel}"],
            capture_output=True, env=GIT_ENV, timeout=GIT_TIMEOUT,
        )
        if r.returncode != 0:
            return None
        return r.stdout

    def mode(self, rel: str) -> str | None:
        if self._modes is None:
            out = git(self.repo, "ls-tree", "-r", self.commit)
            self._modes = {}
            for line in out.splitlines():
                meta, _, path = line.partition("\t")
                m = meta.split()[0] if meta else ""
                self._modes[path] = "755" if m == "100755" else "644"
        return self._modes.get(rel)

    def describe(self) -> dict:
        info = {"url": self.url or str(self.repo), "ref": self.ref, "commit": self.commit}
        if not self.url:
            try:
                url = git(self.repo, "remote", "get-url", "origin").strip()
                if url:
                    info["url"] = url
            except UpdaterError:
                pass
        return info


# --------------------------------------------------------------------------
# Upstream cache (plan §5)
# --------------------------------------------------------------------------

def cache_root() -> pathlib.Path:
    env = os.environ.get("NEXUS_UPSTREAM_CACHE")
    if env:
        return pathlib.Path(env).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = pathlib.Path(xdg).expanduser() if xdg else pathlib.Path.home() / ".cache"
    return base / "nexus"


def cache_repo_for(url: str) -> pathlib.Path:
    """One bare clone per upstream URL; the default location is <cache>/template."""
    root = cache_root()
    default = root / "template"
    if default.is_dir():
        try:
            if git(default, "remote", "get-url", "origin").strip() == url:
                return default
        except UpdaterError:
            pass
        return root / f"template-{hashlib.sha1(url.encode()).hexdigest()[:8]}"
    return default


def ensure_cache(url: str, offline: bool = False) -> pathlib.Path:
    """Clone (bare) or fetch the upstream into the cache; return the repo path."""
    repo = cache_repo_for(url)
    if not repo.is_dir():
        if offline:
            raise UpdaterError(f"offline and no cache for {url} at {repo}", 3)
        repo.parent.mkdir(parents=True, exist_ok=True)
        tmp = repo.with_name(repo.name + ".partial")
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            git(None, "clone", "--bare", "--quiet", url, str(tmp), timeout=300)
            git(tmp, "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
            git(tmp, "fetch", "--quiet", "--tags", "--prune", "origin", timeout=300)
        except UpdaterError as e:
            shutil.rmtree(tmp, ignore_errors=True)
            raise UpdaterError(f"cannot clone {url}: {e}", 3)
        os.replace(tmp, repo)
        return repo
    if not offline:
        try:
            git(repo, "fetch", "--quiet", "--tags", "--prune", "origin", timeout=300)
        except UpdaterError as e:
            raise UpdaterError(f"cannot fetch {url}: {e}", 3)
    return repo


def is_local_dir(spec: str) -> bool:
    return pathlib.Path(spec).expanduser().is_dir()


def resolve_ref_name(repo: pathlib.Path, ref: str) -> str:
    """Accept tags, branches (also as origin/<b>), and commits; return something rev-parse likes."""
    for candidate in (ref, f"refs/tags/{ref}", f"refs/remotes/origin/{ref}", f"refs/heads/{ref}"):
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"],
                           capture_output=True, text=True, env=GIT_ENV, timeout=GIT_TIMEOUT)
        if r.returncode == 0:
            return candidate
    raise UpdaterError(f"ref {ref!r} not found in {repo}", 3)


def version_tags(repo: pathlib.Path) -> list[tuple[tuple[int, int, int], str]]:
    out = git(repo, "tag", "-l", "v*")
    tags = [(parse_semver(t), t) for t in out.split() if is_semver(t)]
    return sorted(tags)


def select_ref(repo: pathlib.Path, explicit: str | None) -> str:
    """Plan §5: the highest v* tag unless --ref says otherwise."""
    if explicit:
        return resolve_ref_name(repo, explicit)
    tags = version_tags(repo)
    if not tags:
        raise UpdaterError("upstream has no v* tags; pass --ref main (or a commit) explicitly", 3)
    return f"refs/tags/{tags[-1][1]}"


def display_ref(ref: str) -> str:
    for prefix in ("refs/tags/", "refs/remotes/origin/", "refs/heads/"):
        if ref.startswith(prefix):
            return ref[len(prefix):]
    return ref


def open_upstream(spec: str, ref: str | None, offline: bool = False) -> WorkTree | GitRef:
    """Local directory → its working tree (or a ref in it); anything else → the cache clone."""
    if is_local_dir(spec):
        p = pathlib.Path(spec).expanduser()
        if ref:
            return GitRef(p, resolve_ref_name(p, ref))
        return WorkTree(p)
    repo = ensure_cache(spec, offline=offline)
    chosen = select_ref(repo, ref)
    src = GitRef(repo, chosen, url=spec)
    src.ref = display_ref(chosen)
    return src


def upstream_version(source: WorkTree | GitRef) -> str | None:
    raw = source.read(VERSION_FILE)
    if raw is None:
        return None
    text = raw.decode("utf-8", errors="replace").strip()
    return text if is_semver(text) else None


# --------------------------------------------------------------------------
# Unit extraction — one function per strategy (plan §3.3)
# --------------------------------------------------------------------------

def h2_sections(text: str) -> list[tuple[str, str]]:
    """Split Markdown into (heading, content) pairs at H2 boundaries; code fences are skipped.

    Content includes the heading line. Text before the first H2 is returned under
    the heading "" and is never owned.
    """
    out: list[tuple[str, list[str]]] = [("", [])]
    in_fence = False
    for line in text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            out.append((line.rstrip(), [line]))
            continue
        out[-1][1].append(line)
    return [(h, "\n".join(body)) for h, body in out]


def units_sections(content: bytes | None, headings: list[str]) -> dict[str, bytes]:
    if content is None:
        return {}
    text = content.decode("utf-8", errors="surrogateescape")
    found: dict[str, list[str]] = {}
    for heading, body in h2_sections(text):
        if heading:
            found.setdefault(heading, []).append(body)
    units: dict[str, bytes] = {}
    for heading in headings:
        bodies = found.get(heading, [])
        if len(bodies) > 1:
            raise UpdaterError(f"heading {heading!r} appears {len(bodies)} times; refusing to guess", 1)
        if bodies:
            units[heading] = normalize_text(bodies[0].encode("utf-8", errors="surrogateescape"))
    return units


def units_index_entries(content: bytes | None, index_rel: str, owned: set[str]) -> dict[str, bytes]:
    if content is None:
        return {}
    text = content.decode("utf-8", errors="surrogateescape")
    base = posixpath.dirname(index_rel)
    units: dict[str, bytes] = {}
    seen: dict[str, int] = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        if not BULLET_RE.match(line):
            continue
        m = LINK_RE.search(line)
        if not m:
            continue
        target = m.group(1).split("#", 1)[0]
        if not target or "://" in target:
            continue
        resolved = posixpath.normpath(posixpath.join(base, target))
        if resolved not in owned:
            continue
        seen[target] = seen.get(target, 0) + 1
        units[target] = normalize_text(line.encode("utf-8", errors="surrogateescape"))
    dups = [k for k, n in seen.items() if n > 1]
    if dups:
        raise UpdaterError(f"index link target(s) appear more than once: {', '.join(dups)}", 1)
    return units


def units_hooks_merge(content: bytes | None) -> dict[str, bytes]:
    if content is None:
        return {}
    try:
        cfg = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise UpdaterError(f".claude/settings.json is not valid JSON: {e}", 1)
    units: dict[str, bytes] = {}
    for event, groups in (cfg.get("hooks") or {}).items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            for hook in group.get("hooks") or []:
                m = HOOK_CMD_RE.search(str(hook.get("command", "")))
                if not m:
                    continue
                key = f"{event}/{m.group(1)}"
                if key in units:
                    raise UpdaterError(f"hook {key} is registered twice; refusing to guess", 1)
                canon = json.dumps({"matcher": group.get("matcher", ""), "hook": hook},
                                   sort_keys=True, separators=(",", ":"))
                units[key] = canon.encode("utf-8")
    return units


def units_of(entry: dict, content: bytes | None, owned: set[str]) -> dict[str, bytes]:
    """Return {unit_id: content_bytes} for one manifest entry; whole-file units use the path as id."""
    strategy = entry["strategy"]
    path = entry["path"]
    if strategy == "replace":
        return {path: content} if content is not None else {}
    if strategy == "sections":
        return {f"{path}#{h}": c for h, c in units_sections(content, entry.get("sections", [])).items()}
    if strategy == "index-entries":
        return {f"{path}#{k}": c for k, c in units_index_entries(content, path, owned).items()}
    if strategy == "hooks-merge":
        return {f"{path}#{k}": c for k, c in units_hooks_merge(content).items()}
    return {}


# --------------------------------------------------------------------------
# Manifest generation (template side) — plan §3.4
# --------------------------------------------------------------------------

def _is_exec(p: pathlib.Path) -> bool:
    return bool(p.stat().st_mode & stat.S_IXUSR)


def generate_manifest(root: pathlib.Path) -> dict:
    root = root.resolve()
    version_file = root / VERSION_FILE
    if not version_file.is_file():
        raise UpdaterError(f"{VERSION_FILE} is missing at the template root", 3)
    version = version_file.read_text(encoding="utf-8").strip()
    parse_semver(version)
    validator = load_validator(root)
    entries: list[dict] = []

    def add(path: str, strategy: str, group: str, **extra) -> None:
        if matches_never_touch(path):
            return
        e = {"path": path, "strategy": strategy, "group": group}
        e.update(extra)
        entries.append(e)

    # Rule 1 — runtime code.
    for p in sorted((root / ".claude" / "hooks").glob("*.py")):
        add(f".claude/hooks/{p.name}", "replace", "hooks", mode="755" if _is_exec(p) else "644")
    for p in sorted((root / "tools").glob("*.py")):
        add(f"tools/{p.name}", "replace", "tools", mode="755" if _is_exec(p) else "644")
    skills = root / ".claude" / "skills"
    if skills.is_dir():
        for p in sorted(skills.rglob("*")):
            if p.is_file() and p.name not in TEMPLATE_ONLY_FILES:
                add(p.relative_to(root).as_posix(), "replace", "tools")

    # Rule 2 — binding system documents in the vault.
    index_path = "knowledge/index/index--system--project-navigation.md"
    for p in sorted((root / "knowledge").rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(TEMPLATE_ONLY_PREFIXES) or rel in TEMPLATE_HISTORY:
            continue
        fm = frontmatter_of(validator, p.read_text(encoding="utf-8", errors="surrogateescape"))
        if fm.get("scope") != "system" or visibility_class(fm) != "binding":
            continue
        if rel == index_path:
            add(rel, "index-entries", "vault")
        else:
            add(rel, "replace", "vault")

    # Rule 3 — shared Obsidian configuration.
    obsidian = root / "knowledge" / ".obsidian"
    if obsidian.is_dir():
        for p in sorted(obsidian.glob("*.json")):
            if p.name in OBSIDIAN_SHARED:
                add(f"knowledge/.obsidian/{p.name}", "create-if-absent", "vault-config")

    # Rule 4 — fixed entries.
    claude_md = root / "CLAUDE.md"
    if claude_md.is_file():
        headings = [h for h, _ in h2_sections(claude_md.read_text(encoding="utf-8"))
                    if h and h not in CLAUDE_PROJECT_SECTIONS]
        add("CLAUDE.md", "sections", "instructions", sections=headings)
    if (root / ".claude" / "settings.json").is_file():
        add(".claude/settings.json", "hooks-merge", "hooks")
    add(".gitignore", "ensure-lines", "repo", lines=list(GITIGNORE_LINES))
    if (root / ".nexus" / "README.md").is_file():
        add(".nexus/README.md", "create-if-absent", "runtime")
    if (root / "docs" / "nexus-implementation-report.md").is_file():
        add("docs/nexus-implementation-report.md", "replace", "vault")

    entries.sort(key=lambda e: e["path"])
    commit = None
    try:
        commit = git(root, "rev-parse", "HEAD").strip()
    except UpdaterError:
        pass
    return {
        "manifest_version": MANIFEST_VERSION,
        "nexus_version": version,
        "generated_from": commit,
        "generated_at": now_iso(),
        "entries": entries,
        "never_touch": list(NEVER_TOUCH),
    }


def manifest_problems(root: pathlib.Path, committed: dict | None = None) -> list[str]:
    """Regenerate in memory and compare; plus the structural assertions of plan §3.4."""
    root = root.resolve()
    problems: list[str] = []
    fresh = generate_manifest(root)
    if committed is None:
        mp = root / MANIFEST_FILE
        if not mp.is_file():
            return [f"{MANIFEST_FILE} is missing; run `manifest generate`"]
        committed = json.loads(mp.read_text(encoding="utf-8"))

    volatile = {"generated_from", "generated_at"}
    a = {k: v for k, v in fresh.items() if k not in volatile}
    b = {k: v for k, v in committed.items() if k not in volatile}
    if a.get("nexus_version") != b.get("nexus_version"):
        problems.append(f"nexus_version differs: file {b.get('nexus_version')!r} vs {VERSION_FILE} {a.get('nexus_version')!r}")
    fa = {e["path"]: e for e in a.get("entries", [])}
    fb = {e["path"]: e for e in b.get("entries", [])}
    for path in sorted(set(fa) | set(fb)):
        if path not in fb:
            problems.append(f"missing from committed manifest: {path}")
        elif path not in fa:
            problems.append(f"stale in committed manifest (no longer generated): {path}")
        elif fa[path] != fb[path]:
            problems.append(f"entry differs: {path}")
    if a.get("never_touch") != b.get("never_touch"):
        problems.append("never_touch list differs")

    # Structural assertions.
    owned = set(fb)
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        try:
            for key in units_hooks_merge(settings.read_bytes()):
                hook = key.split("/", 1)[1]
                if f".claude/hooks/{hook}" not in owned:
                    problems.append(f"registered hook has no replace entry: .claude/hooks/{hook}")
        except UpdaterError as e:
            problems.append(str(e))
    for e in fb.values():
        if e.get("strategy") not in STRATEGIES:
            problems.append(f"unknown strategy {e.get('strategy')!r} on {e['path']}")
        if matches_never_touch(e["path"], committed.get("never_touch", NEVER_TOUCH)):
            problems.append(f"entry matches never_touch: {e['path']}")
        if e.get("strategy") == "sections":
            content = (root / e["path"]).read_bytes() if (root / e["path"]).is_file() else None
            try:
                got = units_sections(content, e.get("sections", []))
            except UpdaterError as err:
                problems.append(str(err))
                got = {}
            for h in e.get("sections", []):
                if h not in got:
                    problems.append(f"{e['path']}: listed heading not found exactly once: {h!r}")
    return problems


# --------------------------------------------------------------------------
# Baseline and status (host side) — plan §4, §9
# --------------------------------------------------------------------------

def looks_like_nexus_project(project: pathlib.Path) -> list[str]:
    guards = [".claude/hooks/nexus-bootstrap.py", ".nexus", "knowledge"]
    return [g for g in guards if not (project / g).exists()]


def read_manifest_from(source: WorkTree | GitRef) -> dict:
    raw = source.read(MANIFEST_FILE)
    if raw is None:
        d = source.describe()
        raise UpdaterError(f"{MANIFEST_FILE} not found in upstream {d['url']} at {d['ref']}", 3)
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise UpdaterError(f"upstream manifest is not valid JSON: {e}", 3)
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise UpdaterError(f"unsupported manifest_version {manifest.get('manifest_version')!r}", 3)
    return manifest


def compute_baseline(project: WorkTree, upstream: WorkTree | GitRef, manifest: dict,
                     version: str) -> tuple[dict, dict]:
    """Return (installed.json dict, inventory) without touching any file."""
    owned = {e["path"] for e in manifest["entries"]}
    units: dict[str, dict] = {}
    inventory = {"identical": [], "customized": [], "absent": [], "refused": []}
    for entry in manifest["entries"]:
        if entry["strategy"] not in COMPARED_STRATEGIES:
            continue
        path = entry["path"]
        try:
            up_units = units_of(entry, upstream.read(path), owned)
        except UpdaterError as e:
            inventory["refused"].append(f"{path}: upstream: {e}")
            continue
        try:
            local_units = units_of(entry, project.read(path), owned)
        except UpdaterError as e:
            inventory["refused"].append(f"{path}: local: {e}")
            continue
        for uid, up_content in up_units.items():
            rec: dict = {"strategy": entry["strategy"], "sha256": sha256_bytes(up_content)}
            if entry.get("mode"):
                rec["mode"] = entry["mode"]
            local = local_units.get(uid)
            if local is None:
                inventory["absent"].append(uid)
                continue
            if local != up_content:
                rec["customized_at_baseline"] = True
                inventory["customized"].append(uid)
            else:
                inventory["identical"].append(uid)
            units[uid] = rec
    installed = {
        "baseline_version": BASELINE_VERSION,
        "nexus_version": version,
        "installed_at": now_iso(),
        "upstream": upstream.describe(),
        "origin": "baseline",
        "units": dict(sorted(units.items())),
    }
    return installed, inventory


def guess_ref(project: WorkTree, repo: pathlib.Path, url: str | None) -> list[tuple[int, int, str]]:
    """Score every v* tag and the last GUESS_COMMITS commits of main by identical units."""
    candidates: list[str] = [f"refs/tags/{t}" for _, t in version_tags(repo)]
    for branch in ("refs/remotes/origin/main", "refs/heads/main"):
        try:
            out = git(repo, "rev-list", f"-n{GUESS_COMMITS}", branch)
            candidates += [c for c in out.split() if c]
            break
        except UpdaterError:
            continue
    scores: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for ref in candidates:
        try:
            src = GitRef(repo, ref, url=url)
        except UpdaterError:
            continue
        if src.commit in seen:
            continue
        seen.add(src.commit)
        try:
            manifest = read_manifest_from(src)
        except UpdaterError:
            continue
        _, inv = compute_baseline(project, src, manifest, manifest.get("nexus_version", "0.0.0"))
        scores.append((len(inv["identical"]), -len(inv["customized"]), ref))
    scores.sort(reverse=True)
    return scores


def load_installed(project: pathlib.Path) -> dict:
    p = project / INSTALLED_FILE
    if not p.is_file():
        raise UpdaterError(f"{INSTALLED_FILE} is absent: run `baseline` first (plan §9)", 6)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise UpdaterError(f"{INSTALLED_FILE} is not valid JSON: {e}", 4)
    if data.get("baseline_version") != BASELINE_VERSION:
        raise UpdaterError(f"unsupported baseline_version {data.get('baseline_version')!r}", 4)
    return data


def load_unlock(project: pathlib.Path) -> list[str]:
    p = project / UNLOCK_FILE
    if not p.is_file():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def compute_status(project: WorkTree, installed: dict) -> dict:
    owned = {uid.partition("#")[0] for uid in installed["units"]}
    result = {"unchanged": [], "customized": [], "removed-locally": [], "mode-drift": [], "refused": []}
    cache: dict[str, dict[str, bytes] | UpdaterError] = {}
    for uid, rec in installed["units"].items():
        path = uid.partition("#")[0]
        if path not in cache:
            try:
                # One extraction per file: sections need the union of listed headings.
                headings = [u.partition("#")[2] for u, r in installed["units"].items()
                            if u.partition("#")[0] == path and r["strategy"] == "sections"]
                e = {"path": path, "strategy": rec["strategy"], "sections": headings}
                cache[path] = units_of(e, project.read(path), owned)
            except UpdaterError as err:
                cache[path] = err
        got = cache[path]
        if isinstance(got, UpdaterError):
            result["refused"].append(f"{uid}: {got}")
            continue
        local = got.get(uid)
        if local is None:
            result["removed-locally"].append(uid)
            continue
        if sha256_bytes(local) == rec["sha256"]:
            result["unchanged"].append(uid)
        else:
            result["customized"].append(uid)
        if rec.get("mode") and project.mode(path) not in (None, rec["mode"]):
            result["mode-drift"].append(uid)
    return result


# --------------------------------------------------------------------------
# Three-way comparison (plan §7.1)
# --------------------------------------------------------------------------

def classify(b: str | None, l: str | None, u: str | None) -> str | None:
    """One row of the decision table. None means 'not a unit of interest'."""
    if b is not None:
        if u is None:
            return "obsolete"
        if l is None:
            return "removed-locally"
        if l == b and u == b:
            return "unchanged"
        if l == b:
            return "update"
        if u == b:
            return "customized"
        if u == l:
            return "converged"
        return "conflict"
    if u is None:
        return None
    if l is None:
        return "add"
    if l == u:
        return "adopt"
    return "unbaselined"


def three_way(project: WorkTree, installed: dict, upstream: WorkTree | GitRef,
              manifest: dict) -> dict[str, list[dict]]:
    """Return {class: [row]} where row = {unit, path, strategy, baseline, local, upstream}."""
    rows: dict[str, list[dict]] = {c: [] for c in PLAN_CLASSES}
    baseline_units = installed["units"]
    owned = {e["path"] for e in manifest["entries"]}
    entries_by_path = {e["path"]: e for e in manifest["entries"]}
    seen_paths: set[str] = set()

    def row(uid: str, strategy: str, b: str | None, l: str | None, u: str | None) -> dict:
        return {"unit": uid, "path": uid.partition("#")[0], "strategy": strategy,
                "baseline": b, "local": l, "upstream": u}

    for entry in manifest["entries"]:
        path = entry["path"]
        seen_paths.add(path)
        strategy = entry["strategy"]
        if strategy == "create-if-absent":
            if project.read(path) is None:
                rows["add"].append(row(path, strategy, None, None, "-"))
            continue
        if strategy == "ensure-lines":
            local_text = (project.read(path) or b"").decode("utf-8", errors="replace")
            present = {ln.strip() for ln in local_text.splitlines()}
            for line in entry.get("lines", []):
                if line not in present:
                    rows["add"].append(row(f"{path}#{line}", strategy, None, None, "-"))
            continue
        if strategy not in COMPARED_STRATEGIES:
            continue

        try:
            up_units = units_of(entry, upstream.read(path), owned)
        except UpdaterError as e:
            rows["refused"].append({**row(path, strategy, None, None, None), "reason": f"upstream: {e}"})
            continue
        # Local extraction lists the union of target headings and baselined headings,
        # so a heading dropped upstream still surfaces as obsolete.
        local_entry = dict(entry)
        if strategy == "sections":
            extra = [u.partition("#")[2] for u in baseline_units
                     if u.partition("#")[0] == path and u.partition("#")[2] not in entry.get("sections", [])]
            local_entry["sections"] = list(entry.get("sections", [])) + extra
        try:
            local_units = units_of(local_entry, project.read(path), owned)
        except UpdaterError as e:
            rows["refused"].append({**row(path, strategy, None, None, None), "reason": f"local: {e}"})
            continue

        uids = set(up_units) | set(local_units) | {u for u in baseline_units if u.partition("#")[0] == path}
        for uid in sorted(uids):
            b = baseline_units.get(uid, {}).get("sha256")
            l = sha256_bytes(local_units[uid]) if uid in local_units else None
            u = sha256_bytes(up_units[uid]) if uid in up_units else None
            cls = classify(b, l, u)
            if cls is None:
                continue
            rows[cls].append(row(uid, strategy, b, l, u))
            if strategy == "replace" and entry.get("mode") and l is not None \
                    and project.mode(path) not in (None, entry["mode"]):
                rows["mode-drift"].append(row(uid, strategy, b, l, u))

    # Units baselined under paths the target manifest no longer lists at all.
    for uid, rec in baseline_units.items():
        path = uid.partition("#")[0]
        if path in seen_paths:
            continue
        l_content = project.read(path)
        rows["obsolete"].append(row(uid, rec["strategy"], rec["sha256"],
                                    sha256_bytes(l_content) if l_content is not None else None, None))
    return rows


def unit_diff(project: WorkTree, upstream: WorkTree | GitRef, manifest: dict, path: str) -> str:
    entry = next((e for e in manifest["entries"] if e["path"] == path), None)
    if entry is None:
        raise UpdaterError(f"{path} is not in the target manifest", 1)
    owned = {e["path"] for e in manifest["entries"]}
    lu = units_of(entry, project.read(path), owned)
    uu = units_of(entry, upstream.read(path), owned)
    out: list[str] = []
    for uid in sorted(set(lu) | set(uu)):
        a = lu.get(uid, b"").decode("utf-8", errors="replace").splitlines()
        b = uu.get(uid, b"").decode("utf-8", errors="replace").splitlines()
        if a == b:
            continue
        out += difflib.unified_diff(a, b, fromfile=f"local/{uid}", tofile=f"upstream/{uid}", lineterm="")
    return "\n".join(out)


def read_update_check(project: pathlib.Path) -> dict | None:
    p = project / UPDATE_CHECK_FILE
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


# --------------------------------------------------------------------------
# Apply — writers per strategy (plan §7.2–7.4, spec §8)
# --------------------------------------------------------------------------

STATE_FILE = ".nexus/state.json"
LIVE_SESSION_SECONDS = 60
WRITE_CLASSES = {"update", "add"}
RECORD_CLASSES = {"update", "add", "converged", "adopt"}
RESTORE_CLASSES = {"customized", "conflict", "removed-locally"}


def write_file_atomic(path: pathlib.Path, data: bytes, mode: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".nexus-tmp")
    tmp.write_bytes(data)
    if mode == "755":
        tmp.chmod(tmp.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    elif mode == "644":
        tmp.chmod(tmp.stat().st_mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    os.replace(tmp, path)


def set_mode(path: pathlib.Path, mode: str) -> None:
    cur = path.stat().st_mode
    if mode == "755":
        path.chmod(cur | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    else:
        path.chmod(cur & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def apply_sections(local: bytes | None, upstream: bytes | None, headings: list[str]) -> bytes:
    """Replace or append the listed H2 sections of a Markdown file with their upstream text."""
    text = (local or b"").decode("utf-8", errors="surrogateescape")
    up_units = units_sections(upstream, headings)
    parts = h2_sections(text)
    present = {h for h, _ in parts if h}
    out: list[str] = []
    for heading, body in parts:
        if heading in up_units:
            out.append(up_units[heading].decode("utf-8", errors="surrogateescape") + "\n")
        else:
            out.append(body)
    result = "\n".join(out)
    for heading in headings:
        if heading in up_units and heading not in present:
            result = result.rstrip("\n") + "\n\n" + up_units[heading].decode("utf-8", errors="surrogateescape") + "\n"
    if local is None:
        result = result.lstrip("\n")
    return result.encode("utf-8", errors="surrogateescape")


def _section_of_line(text: str, needle: str) -> str:
    """H2 heading under which `needle` (a full line, normalized) appears; '' when before any H2."""
    current = ""
    for heading, body in h2_sections(text):
        for line in body.split("\n"):
            if line.rstrip() == needle:
                return heading
        current = heading
    return current


def apply_index_entries(local: bytes | None, upstream: bytes | None, index_rel: str, owned: set[str],
                        keys: Iterable[str]) -> bytes:
    """Replace owned index lines in place; insert new ones after the last owned line of the same section."""
    text = (local or b"").decode("utf-8", errors="surrogateescape").replace("\r\n", "\n")
    up_text = (upstream or b"").decode("utf-8", errors="surrogateescape")
    up_units = units_index_entries(upstream, index_rel, owned)
    local_units = units_index_entries(local, index_rel, owned)
    lines = text.split("\n")
    keys = [k for k in keys if k in up_units]

    def key_of(line: str) -> str | None:
        if not BULLET_RE.match(line):
            return None
        m = LINK_RE.search(line)
        if not m:
            return None
        target = m.group(1).split("#", 1)[0]
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(index_rel), target))
        return target if resolved in owned else None

    # Replacements.
    for i, line in enumerate(lines):
        k = key_of(line)
        if k in keys and k in local_units:
            lines[i] = up_units[k].decode("utf-8", errors="surrogateescape")

    # Insertions, in upstream order.
    for k in keys:
        if k in local_units:
            continue
        new_line = up_units[k].decode("utf-8", errors="surrogateescape")
        section = _section_of_line(up_text, new_line)
        # Locate the section locally.
        start = end = None
        if section:
            for i, line in enumerate(lines):
                if start is None and line.rstrip() == section:
                    start = i
                    continue
                if start is not None and line.startswith("## "):
                    end = i
                    break
            if start is not None and end is None:
                end = len(lines)
        if start is None:
            # Section absent (or the line lives before any H2): append a section at EOF.
            while lines and lines[-1] == "":
                lines.pop()
            lines += ["", section, "", new_line] if section else ["", new_line]
            local_units[k] = b""
            continue
        # After the last owned line in the section, else after the last non-blank line of it.
        insert_at = None
        for i in range(end - 1, start, -1):
            if key_of(lines[i]) is not None:
                insert_at = i + 1
                break
        if insert_at is None:
            insert_at = end
            while insert_at - 1 > start and lines[insert_at - 1] == "":
                insert_at -= 1
        lines.insert(insert_at, new_line)
        local_units[k] = b""
    result = "\n".join(lines)
    if not result.endswith("\n"):
        result += "\n"
    return result.encode("utf-8", errors="surrogateescape")


def apply_hooks_merge(local: bytes | None, upstream: bytes | None, keys: Iterable[str]) -> bytes:
    """Make the listed nexus-* hook entries equal to upstream; foreign entries and order are kept."""
    cfg = json.loads(local.decode("utf-8")) if local else {}
    up = json.loads(upstream.decode("utf-8")) if upstream else {}
    hooks = cfg.setdefault("hooks", {})
    up_hooks = up.get("hooks") or {}
    for key in keys:
        event, _, name = key.partition("/")
        # Find the upstream entry.
        target = None
        for group in up_hooks.get(event) or []:
            for hook in group.get("hooks") or []:
                m = HOOK_CMD_RE.search(str(hook.get("command", "")))
                if m and m.group(1) == name:
                    target = (group.get("matcher", ""), hook)
        if target is None:
            continue
        matcher, hook = target
        # Remove the local entry wherever it sits.
        groups = hooks.setdefault(event, [])
        for group in groups:
            kept = []
            for h in group.get("hooks") or []:
                m = HOOK_CMD_RE.search(str(h.get("command", "")))
                if m and m.group(1) == name:
                    continue
                kept.append(h)
            group["hooks"] = kept
        hooks[event] = [g for g in groups if g.get("hooks")]
        # Add into a group with the same matcher, else a new group.
        for group in hooks[event]:
            if group.get("matcher", "") == matcher:
                group["hooks"].append(json.loads(json.dumps(hook)))
                break
        else:
            hooks[event].append({"matcher": matcher, "hooks": [json.loads(json.dumps(hook))]})
    return (json.dumps(cfg, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def apply_ensure_lines(local: bytes | None, lines_wanted: list[str]) -> bytes:
    text = (local or b"").decode("utf-8", errors="surrogateescape")
    present = {ln.strip() for ln in text.splitlines()}
    missing = [ln for ln in lines_wanted if ln not in present]
    if not missing:
        return (local or b"")
    if text and not text.endswith("\n"):
        text += "\n"
    if text:
        text += "\n"
    text += "# Nexus runtime (added by tools/nexus-update.py)\n" + "\n".join(missing) + "\n"
    return text.encode("utf-8", errors="surrogateescape")


def live_session_recent(project_root: pathlib.Path) -> bool:
    p = project_root / STATE_FILE
    if not p.is_file():
        return False
    import time
    return (time.time() - p.stat().st_mtime) < LIVE_SESSION_SECONDS


def run_post_apply_validation(project_root: pathlib.Path) -> list[str]:
    """spec §8: vault clean, validator selftest, hooks compile, settings.json sane."""
    problems: list[str] = []
    validator = project_root / "tools" / "validate-vault.py"
    if validator.is_file():
        for extra in ([], ["--selftest"]):
            r = subprocess.run([sys.executable, str(validator), "--root", str(project_root), *extra],
                               capture_output=True, text=True, cwd=str(project_root), timeout=300)
            if r.returncode != 0:
                problems.append(f"validate-vault.py {' '.join(extra) or '(vault)'} exit {r.returncode}: "
                                f"{(r.stdout + r.stderr).strip()[-400:]}")
    hooks_dir = project_root / ".claude" / "hooks"
    if hooks_dir.is_dir():
        import py_compile
        for f in sorted(hooks_dir.glob("*.py")):
            try:
                py_compile.compile(str(f), doraise=True)
            except py_compile.PyCompileError as e:
                problems.append(f"{f.relative_to(project_root)} does not compile: {e.msg[:200]}")
    settings = project_root / ".claude" / "settings.json"
    if settings.is_file():
        try:
            cfg = json.loads(settings.read_text(encoding="utf-8"))
            for event, groups in (cfg.get("hooks") or {}).items():
                for g in groups:
                    for h in g.get("hooks") or []:
                        cmd = str(h.get("command", "")).replace("$CLAUDE_PROJECT_DIR/", "")
                        if cmd.startswith(".claude/hooks/") and not (project_root / cmd).is_file():
                            problems.append(f"settings.json registers a missing hook: {cmd} ({event})")
        except json.JSONDecodeError as e:
            problems.append(f".claude/settings.json is not valid JSON after apply: {e}")
    return problems


def compute_apply(project: WorkTree, installed: dict, upstream: WorkTree | GitRef, manifest: dict,
                  rows: dict[str, list[dict]], restore: set[str]) -> tuple[list[dict], dict]:
    """Turn the three-way rows into per-file write operations and the next installed.json.

    Returns (ops, new_installed). Each op: {path, group, strategy, action, units, data, mode}.
    Nothing is written here.
    """
    entries = {e["path"]: e for e in manifest["entries"]}
    owned = set(entries)
    per_path: dict[str, dict] = {}

    def slot(path: str) -> dict:
        e = entries[path]
        return per_path.setdefault(path, {"path": path, "group": e.get("group", "vault"),
                                          "strategy": e["strategy"], "units": [], "restore": [],
                                          "mode_fix": False, "entry": e})

    for cls in WRITE_CLASSES:
        for r in rows[cls]:
            slot(r["path"])["units"].append(r["unit"])
    for cls in RESTORE_CLASSES:
        for r in rows[cls]:
            if r["path"] in restore and r["upstream"] is not None:
                s = slot(r["path"])
                s["units"].append(r["unit"])
                s["restore"].append(r["unit"])
    for r in rows["mode-drift"]:
        slot(r["path"])["mode_fix"] = True

    ops: list[dict] = []
    for path, s in per_path.items():
        e = s["entry"]
        strategy = s["strategy"]
        local = project.read(path)
        up = upstream.read(path)
        data: bytes | None = None
        if strategy == "replace":
            if s["units"]:
                data = up
        elif strategy == "sections":
            heads = [u.partition("#")[2] for u in s["units"]]
            data = apply_sections(local, up, heads)
        elif strategy == "index-entries":
            keys = [u.partition("#")[2] for u in s["units"]]
            data = apply_index_entries(local, up, path, owned, keys)
        elif strategy == "hooks-merge":
            keys = [u.partition("#")[2] for u in s["units"]]
            data = apply_hooks_merge(local, up, keys)
        elif strategy == "ensure-lines":
            data = apply_ensure_lines(local, e.get("lines", []))
        elif strategy == "create-if-absent":
            data = up if local is None else None
        if data is not None and data == local and not s["mode_fix"]:
            data = None
        if data is None and not s["mode_fix"]:
            continue
        ops.append({"path": path, "group": s["group"], "strategy": strategy,
                    "action": "create" if local is None else "write" if data is not None else "chmod",
                    "units": sorted(s["units"]), "restore": sorted(s["restore"]),
                    "data": data, "mode": e.get("mode"), "exists": local is not None})
    order = {g: i for i, g in enumerate(GROUP_ORDER)}
    ops.sort(key=lambda o: (order.get(o["group"], 99), o["path"]))

    # Next baseline: record upstream SHAs for written/converged/adopted units, drop obsolete ones.
    units = dict(installed["units"])
    for cls in RECORD_CLASSES:
        for r in rows[cls]:
            if r["strategy"] not in COMPARED_STRATEGIES or r["upstream"] is None:
                continue
            rec = {"strategy": r["strategy"], "sha256": r["upstream"]}
            mode = entries.get(r["path"], {}).get("mode")
            if mode:
                rec["mode"] = mode
            units[r["unit"]] = rec
    for cls in RESTORE_CLASSES:
        for r in rows[cls]:
            if r["path"] in restore and r["upstream"] is not None:
                rec = {"strategy": r["strategy"], "sha256": r["upstream"]}
                mode = entries.get(r["path"], {}).get("mode")
                if mode:
                    rec["mode"] = mode
                units[r["unit"]] = rec
    for r in rows["obsolete"]:
        units.pop(r["unit"], None)
    new_installed = {
        "baseline_version": BASELINE_VERSION,
        "nexus_version": manifest.get("nexus_version") or installed["nexus_version"],
        "installed_at": now_iso(),
        "upstream": upstream.describe(),
        "origin": "update",
        "units": dict(sorted(units.items())),
    }
    return ops, new_installed


# --------------------------------------------------------------------------
# Feedback channel — notes in a host, mailbox in the cache (spec--system--feedback-channel.md §4)
# --------------------------------------------------------------------------

FEEDBACK_DIR = "knowledge/feedback"
FEEDBACK_GLOB = "feedback--nexus--*.md"
INBOX_DIR = "inbox"
INBOX_ARCHIVE_DIR = "inbox-archive"
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
_VOLATILE_FM_KEYS = ("delivered", "updated")


def note_fingerprint(text: str) -> str:
    """SHA-256 of a note with the delivery-owned frontmatter lines removed, so a
    push does not change what the next push compares against."""
    m = FM_RE.match(text)
    if not m:
        return sha256_bytes(text.encode("utf-8", errors="surrogateescape"))
    kept: list[str] = []
    skipping = False
    for line in m.group(1).split("\n"):
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
            key = line.split(":", 1)[0]
            skipping = key in _VOLATILE_FM_KEYS
            if skipping:
                continue
        elif skipping and re.match(r"^\s*-\s+", line):
            continue
        else:
            skipping = False
        kept.append(line)
    body = text[m.end():]
    return sha256_bytes(("\n".join(kept) + "\n" + body).encode("utf-8", errors="surrogateescape"))


def set_frontmatter_fields(text: str, fields: dict[str, object]) -> str:
    """Rewrite scalar / list fields inside the frontmatter block, leaving everything else byte-identical."""
    m = FM_RE.match(text)
    if not m:
        raise UpdaterError("note has no frontmatter block", 1)
    lines = m.group(1).split("\n")
    out: list[str] = []
    done: set[str] = set()
    skipping = False

    def render(key: str, value: object) -> str:
        if isinstance(value, list):
            return f"{key}: [{', '.join(str(v) for v in value)}]"
        return f"{key}: {value}"

    for line in lines:
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
        if km:
            key = km.group(1)
            if key in fields:
                out.append(render(key, fields[key]))
                done.add(key)
                skipping = True
                continue
            skipping = False
            out.append(line)
            continue
        if skipping and re.match(r"^\s*-\s+", line):
            continue
        skipping = False
        out.append(line)
    for key, value in fields.items():
        if key in done:
            continue
        idx = next((i for i, ln in enumerate(out) if ln.startswith("tags:")), len(out))
        out.insert(idx, render(key, value))
    return "---\n" + "\n".join(out) + "\n---\n" + text[m.end():]


def load_notes(root: pathlib.Path) -> list[dict]:
    validator = load_validator(root)
    notes: list[dict] = []
    for p in sorted((root / FEEDBACK_DIR).glob(FEEDBACK_GLOB)):
        text = p.read_text(encoding="utf-8", errors="surrogateescape")
        fm = frontmatter_of(validator, text)
        title = next((ln[2:].strip() for ln in text.split("\n") if ln.startswith("# ")), p.stem)
        delivered = fm.get("delivered") or []
        if not isinstance(delivered, list):
            delivered = [str(delivered)]
        notes.append({
            "path": p, "rel": p.relative_to(root).as_posix(), "text": text, "fm": fm, "title": title,
            "host": str(fm.get("host") or root.name).strip(), "kind": str(fm.get("kind") or "?"),
            "version": str(fm.get("nexus_version") or "unknown"), "status": str(fm.get("status") or "?"),
            "delivered": delivered, "fingerprint": note_fingerprint(text),
        })
    return notes


def inbox_root() -> pathlib.Path:
    return cache_root() / INBOX_DIR


def archive_root() -> pathlib.Path:
    return cache_root() / INBOX_ARCHIVE_DIR


def _sidecars(host: str) -> list[dict]:
    found: list[dict] = []
    for base in (inbox_root(), archive_root()):
        d = base / host
        if not d.is_dir():
            continue
        for sc in d.glob("*.json"):
            try:
                data = json.loads(sc.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            data["_sidecar"] = sc
            found.append(data)
    return found


def note_is_pending(note: dict) -> tuple[bool, str]:
    """(pending, reason). A note is pending until a sidecar with its fingerprint exists."""
    receipts = [r for r in note["delivered"] if str(r).startswith("inbox:")]
    matches = [s for s in _sidecars(note["host"]) if s.get("path") == note["rel"]]
    if not receipts and not matches:
        return True, "never delivered"
    if not matches:
        return True, "receipt present but the mailbox has no copy (cache wiped?)"
    latest = max(matches, key=lambda s: s.get("pushed_at", ""))
    if latest.get("fingerprint") != note["fingerprint"]:
        return True, "changed since last delivery"
    return False, f"delivered {latest.get('pushed_at')}"


def push_note(root: pathlib.Path, note: dict, dry_run: bool) -> pathlib.Path:
    ts = datetime.datetime.now().replace(microsecond=0)
    stamp = ts.strftime("%Y-%m-%dT%H-%M-%S")
    dest_dir = inbox_root() / note["host"]
    dest = dest_dir / f"{stamp}--{note['path'].name}"
    if dry_run:
        return dest
    dest_dir.mkdir(parents=True, exist_ok=True)
    receipt = f"inbox:{ts.isoformat()}"
    new_text = set_frontmatter_fields(note["text"], {
        "delivered": list(note["delivered"]) + [receipt],
        "updated": ts.strftime("%Y-%m-%d"),
    })
    commit = None
    try:
        commit = git(root, "rev-parse", "HEAD").strip()
    except UpdaterError:
        pass
    sidecar = {
        "host": note["host"], "path": note["rel"], "commit": commit, "pushed_at": ts.isoformat(),
        "fingerprint": note["fingerprint"], "sha256": sha256_bytes(new_text.encode("utf-8", errors="surrogateescape")),
        "kind": note["kind"], "nexus_version": note["version"], "title": note["title"], "receipt": receipt,
    }
    dest.write_text(new_text, encoding="utf-8", errors="surrogateescape")
    dest.with_suffix(".json").write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp = note["path"].with_name(note["path"].name + ".nexus-tmp")
    tmp.write_text(new_text, encoding="utf-8", errors="surrogateescape")
    os.replace(tmp, note["path"])
    return dest


def inbox_entries(include_archive: bool = False) -> list[dict]:
    entries: list[dict] = []
    bases = [inbox_root()] + ([archive_root()] if include_archive else [])
    for base in bases:
        if not base.is_dir():
            continue
        for host_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            for md in sorted(host_dir.glob("*.md")):
                sc = md.with_suffix(".json")
                data: dict = {}
                if sc.is_file():
                    try:
                        data = json.loads(sc.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        data = {}
                entries.append({"file": md, "sidecar": sc if sc.is_file() else None, "host": host_dir.name,
                                "archived": base == archive_root(), **{k: data.get(k) for k in
                                ("kind", "nexus_version", "title", "pushed_at", "path", "commit")}})
    entries.sort(key=lambda e: (e["archived"], e.get("pushed_at") or "", e["file"].name))
    return entries


def inbox_summary() -> tuple[int, dict[str, int]]:
    per_host: dict[str, int] = {}
    for e in inbox_entries():
        per_host[e["host"]] = per_host.get(e["host"], 0) + 1
    return sum(per_host.values()), per_host


def _pick_entry(selector: str, entries: list[dict]) -> dict:
    if selector.isdigit():
        n = int(selector)
        if 1 <= n <= len(entries):
            return entries[n - 1]
        raise UpdaterError(f"no inbox entry #{n} (1..{len(entries)})", 1)
    for e in entries:
        if e["file"].name == selector or e["file"].name.endswith(f"--{selector}") or e["file"].name.endswith(f"--{selector}.md"):
            return e
    raise UpdaterError(f"no inbox entry matches {selector!r}", 1)


def cmd_feedback(args) -> int:
    action = args.feedback_action
    if action in ("status", "push"):
        root = pathlib.Path(args.project_root).resolve()
        if not (root / FEEDBACK_DIR).is_dir():
            print(f"{FEEDBACK_DIR}/ does not exist here; nothing to {action}.")
            return 0
        notes = load_notes(root)
        if not notes:
            print(f"no {FEEDBACK_GLOB} notes under {FEEDBACK_DIR}/")
            return 0
        pending = [(n, *note_is_pending(n)) for n in notes]
        if action == "status":
            print(f"=== feedback notes in {root.name} ({len(notes)}) — mailbox: {inbox_root()} ===")
            for n, is_pending, why in pending:
                flag = "PENDING " if is_pending else "delivered"
                print(f"  {flag}  {n['kind']:6} {n['status']:11} {n['rel']}  ({why})")
            return 0
        todo = [(n, why) for n, is_pending, why in pending if is_pending]
        if not todo:
            print(f"all {len(notes)} note(s) already delivered to {inbox_root()}")
            return 0
        for n, why in todo:
            dest = push_note(root, n, args.dry_run)
            verb = "WOULD DELIVER" if args.dry_run else "delivered"
            print(f"  [{verb}] {n['rel']}  →  {dest}  ({why})")
        if args.dry_run:
            print(f"\nDRY-RUN: {len(todo)} note(s) would be delivered; nothing written.")
        else:
            print(f"\n{len(todo)} note(s) delivered. Receipts appended to each note's `delivered:`; commit the notes.")
        return 0

    entries = inbox_entries(include_archive=getattr(args, "all", False))
    if action == "list":
        if not entries:
            print(f"inbox empty: {inbox_root()}")
            return 0
        print(f"=== Nexus feedback inbox: {inbox_root()} ===")
        for i, e in enumerate(entries, 1):
            mark = " (archived)" if e["archived"] else ""
            print(f"  {i:3}. {e['host']:14} {str(e.get('kind') or '?'):6} {str(e.get('nexus_version') or '?'):7} "
                  f"{str(e.get('pushed_at') or '')[:19]:19}  {e.get('title') or e['file'].name}{mark}")
        return 0
    if action == "show":
        e = _pick_entry(args.selector, entries)
        print(f"# {e['file']}\n")
        print(e["file"].read_text(encoding="utf-8", errors="surrogateescape"))
        return 0
    if action == "archive":
        live = [e for e in entries if not e["archived"]]
        if args.all_from:
            chosen = [e for e in live if e["host"] == args.all_from]
            if not chosen:
                print(f"no live inbox entries from {args.all_from!r}")
                return 0
        else:
            if not args.selector:
                raise UpdaterError("archive needs an entry number / name or --all-from <host>", 1)
            chosen = [_pick_entry(args.selector, live)]
        for e in chosen:
            dest_dir = archive_root() / e["host"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            for src in (e["file"], e["sidecar"]):
                if src is not None:
                    shutil.move(str(src), str(dest_dir / src.name))
            print(f"  archived  {e['host']}/{e['file'].name}")
        return 0
    raise UpdaterError(f"unknown feedback action {action!r}", 4)


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def _guard_project(project_root: pathlib.Path, force: bool = False) -> int | None:
    missing = looks_like_nexus_project(project_root)
    if missing and not force:
        print("ERROR: target does not look like a Nexus project. Missing: " + ", ".join(missing), file=sys.stderr)
        return 2
    return None


def _open_target(args, installed: dict | None) -> tuple[WorkTree | GitRef, dict, str]:
    """Resolve --upstream / --ref (falling back to the baseline's URL) into (source, manifest, version)."""
    spec = args.upstream or (installed or {}).get("upstream", {}).get("url")
    if not spec:
        raise UpdaterError("no upstream known: pass --upstream <url-or-path> (the baseline records it afterwards)", 3)
    source = open_upstream(spec, args.ref, offline=getattr(args, "offline", False))
    manifest = read_manifest_from(source)
    version = upstream_version(source) or manifest.get("nexus_version")
    if not version:
        raise UpdaterError("upstream carries no version; pass --version", 3)
    return source, manifest, version


def cmd_manifest(args) -> int:
    root = pathlib.Path(args.project_root).resolve()
    if args.action == "generate":
        manifest = generate_manifest(root)
        out = root / MANIFEST_FILE
        out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        by_strategy: dict[str, int] = {}
        for e in manifest["entries"]:
            by_strategy[e["strategy"]] = by_strategy.get(e["strategy"], 0) + 1
        print(f"wrote {MANIFEST_FILE}: Nexus {manifest['nexus_version']}, {len(manifest['entries'])} entries")
        for k in sorted(by_strategy):
            print(f"  {k:18} {by_strategy[k]}")
        problems = manifest_problems(root, manifest)
        if problems:
            print("structural problems:")
            for p in problems:
                print(f"  - {p}")
            return 5
        return 0
    problems = manifest_problems(root)
    if problems:
        print(f"{MANIFEST_FILE}: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 5
    print(f"{MANIFEST_FILE}: in sync with the tree")
    return 0


def cmd_baseline(args) -> int:
    project_root = pathlib.Path(args.project_root).resolve()
    rc = _guard_project(project_root, args.force)
    if rc:
        return rc
    target = project_root / INSTALLED_FILE
    if target.is_file() and not args.force:
        print(f"ERROR: {INSTALLED_FILE} already exists; pass --force to rewrite it", file=sys.stderr)
        return 1
    if not args.upstream:
        print("ERROR: --upstream <url-or-path-to-nexus> is required", file=sys.stderr)
        return 3
    project = WorkTree(project_root)

    if args.guess:
        if is_local_dir(args.upstream):
            repo = pathlib.Path(args.upstream).expanduser()
            url = None
        else:
            repo = ensure_cache(args.upstream, offline=args.offline)
            url = args.upstream
        scores = guess_ref(project, repo, url)
        if not scores:
            raise UpdaterError("no candidate ref carries a manifest; nothing to guess from", 3)
        print("=== baseline --guess: identical units per candidate ref ===")
        for identical, neg_custom, ref in scores[:5]:
            print(f"  {identical:4} identical  {-neg_custom:4} customized   {display_ref(ref)}")
        chosen = scores[0][2]
        upstream: WorkTree | GitRef = GitRef(repo, chosen, url=url)
        upstream.ref = display_ref(chosen)
        manifest = read_manifest_from(upstream)
        version = args.version or upstream_version(upstream) or manifest.get("nexus_version")
        print(f"  chosen: {upstream.ref} ({version})\n")
    else:
        upstream = open_upstream(args.upstream, args.ref, offline=args.offline)
        manifest = read_manifest_from(upstream)
        version = args.version or upstream_version(upstream) or manifest.get("nexus_version")
    if not version:
        raise UpdaterError("upstream carries no nexus_version; pass --version", 3)
    parse_semver(version)
    installed, inv = compute_baseline(project, upstream, manifest, version)

    print(f"=== Nexus baseline: {version} from {installed['upstream']['url']} @ {installed['upstream']['ref']} ===")
    print(f"  identical units:   {len(inv['identical'])}")
    print(f"  customized units:  {len(inv['customized'])}   (baseline = upstream; reported as customized from now on)")
    print(f"  absent locally:    {len(inv['absent'])}   (a later plan reports them as add)")
    print(f"  refused:           {len(inv['refused'])}")
    for uid in inv["customized"]:
        print(f"    customized  {uid}")
    for uid in inv["absent"]:
        print(f"    absent      {uid}")
    for msg in inv["refused"]:
        print(f"    refused     {msg}")
    if args.dry_run:
        print(f"\nDRY-RUN: {INSTALLED_FILE} not written.")
        return 1 if inv["refused"] else 0
    write_json_atomic(target, installed)
    print(f"\nwrote {INSTALLED_FILE} ({len(installed['units'])} units). Commit it with the project.")
    return 1 if inv["refused"] else 0


def cmd_status(args) -> int:
    project_root = pathlib.Path(args.project_root).resolve()
    rc = _guard_project(project_root)
    if rc:
        return rc
    installed = load_installed(project_root)
    project = WorkTree(project_root)
    st = compute_status(project, installed)
    unlock = load_unlock(project_root)
    last = read_update_check(project_root)
    if args.as_json:
        print(json.dumps({"nexus_version": installed["nexus_version"], "upstream": installed["upstream"],
                          "installed_at": installed["installed_at"], "status": st, "unlocked": unlock,
                          "last_check": last, "never_touch": NEVER_TOUCH}, indent=2))
        return 0
    up = installed["upstream"]
    print(f"=== Nexus {installed['nexus_version']} installed {installed['installed_at']} "
          f"from {up.get('url')} @ {up.get('ref')} ===")
    for cls in ("unchanged", "customized", "removed-locally", "mode-drift", "refused"):
        print(f"  {cls:16} {len(st[cls])}")
    for cls in ("customized", "removed-locally", "mode-drift", "refused"):
        for uid in st[cls]:
            print(f"    {cls:16} {uid}")
    print(f"  unlocked paths:  {len(unlock)}")
    for p in unlock:
        print(f"    unlocked         {p}")
    if last:
        print(f"  last check:      {last.get('checked_at')} → {last.get('status')}"
              + (f", upstream {last.get('upstream_version')}" if last.get("upstream_version") else ""))
    print("  never touched:   " + ", ".join(NEVER_TOUCH))
    return 0


def cmd_check(args) -> int:
    project_root = pathlib.Path(args.project_root).resolve()
    rc = _guard_project(project_root)
    if rc:
        return rc
    installed = load_installed(project_root)
    record = {"checked_at": now_iso(), "status": "unreachable", "upstream_version": None,
              "upstream_ref": None, "upstream_commit": None}
    try:
        source, manifest, version = _open_target(args, installed)
    except UpdaterError as e:
        record["error"] = str(e)
        write_json_atomic(project_root / UPDATE_CHECK_FILE, record)
        raise
    d = source.describe()
    record.update({"status": "ok", "upstream_version": version, "upstream_ref": d["ref"],
                   "upstream_commit": d["commit"]})
    write_json_atomic(project_root / UPDATE_CHECK_FILE, record)
    have = installed["nexus_version"]
    if args.as_json:
        print(json.dumps({"installed": have, "upstream": version, "ref": d["ref"], "commit": d["commit"],
                          "newer": parse_semver(version) > parse_semver(have)}, indent=2))
        return 0
    if parse_semver(version) > parse_semver(have):
        print(f"Nexus {version} is available upstream ({d['ref']}); this project has {have}.")
        print("Run `python3 tools/nexus-update.py plan` to see what would change. Nothing has been applied.")
    elif parse_semver(version) < parse_semver(have):
        print(f"Upstream {d['ref']} is Nexus {version}, older than the installed {have}.")
    else:
        print(f"Nexus {have} is up to date ({d['ref']}).")
    return 0


def cmd_plan(args) -> int:
    project_root = pathlib.Path(args.project_root).resolve()
    rc = _guard_project(project_root)
    if rc:
        return rc
    installed = load_installed(project_root)
    project = WorkTree(project_root)
    source, manifest, version = _open_target(args, installed)
    have = installed["nexus_version"]
    if parse_semver(version) < parse_semver(have) and not args.allow_downgrade:
        print(f"ERROR: upstream {source.describe()['ref']} is Nexus {version}, older than the installed {have}; "
              "pass --allow-downgrade to plan it anyway", file=sys.stderr)
        return 1

    if args.diff:
        text = unit_diff(project, source, manifest, args.diff)
        print(text if text else f"{args.diff}: local and upstream units are identical")
        return 0

    rows = three_way(project, installed, source, manifest)
    unlock = set(load_unlock(project_root))
    blocking = sum(len(rows[c]) for c in BLOCKING_CLASSES)
    if args.as_json:
        print(json.dumps({"installed": have, "target": version, "upstream": source.describe(),
                          "rows": rows, "unlocked": sorted(unlock), "blocking": blocking}, indent=2))
        return 1 if blocking else 0

    d = source.describe()
    print(f"=== Nexus update plan: {have} → {version} ({d['url']} @ {d['ref']}) ===")
    print("  " + "  ".join(f"{c}={len(rows[c])}" for c in PLAN_CLASSES if rows[c]))
    print()
    explain = {
        "conflict": "host and upstream both changed; nothing will be written (unlock + hand-merge, or --restore)",
        "unbaselined": "present locally without a baseline and differs from upstream; run baseline first",
        "refused": "cannot be parsed safely; left alone",
        "update": "untouched by the host, changed upstream; will be written",
        "add": "new upstream; will be created",
        "converged": "host already made the upstream change; baseline will be recorded",
        "adopt": "already identical to upstream; baseline will be recorded",
        "customized": "changed by the host, unchanged upstream; left alone",
        "removed-locally": "deleted by the host; left deleted (apply --restore recreates)",
        "obsolete": "dropped upstream; never deleted automatically",
        "mode-drift": "executable bit differs; apply restores it",
        "unchanged": "identical everywhere",
    }
    for cls in PLAN_CLASSES:
        if not rows[cls] or (cls == "unchanged" and not args.verbose):
            continue
        print(f"--- {cls} ({len(rows[cls])}): {explain[cls]}")
        for r in rows[cls]:
            mark = "  [unlocked]" if r["path"] in unlock else ""
            extra = f"  ({r['reason']})" if r.get("reason") else ""
            print(f"    {r['unit']}{mark}{extra}")
    if rows["unchanged"] and not args.verbose:
        print(f"--- unchanged ({len(rows['unchanged'])}): identical everywhere (--verbose lists them)")
    print()
    if blocking:
        print(f"{blocking} blocking row(s). `apply` will still update the clean rows and leave these alone.")
    else:
        print("No blocking rows. This was a plan; nothing has been written.")
    return 1 if blocking else 0


def cmd_apply(args) -> int:
    project_root = pathlib.Path(args.project_root).resolve()
    rc = _guard_project(project_root)
    if rc:
        return rc
    installed = load_installed(project_root)
    project = WorkTree(project_root)
    source, manifest, version = _open_target(args, installed)
    have = installed["nexus_version"]
    d = source.describe()
    if parse_semver(version) < parse_semver(have) and not args.allow_downgrade:
        print(f"ERROR: upstream {d['ref']} is Nexus {version}, older than the installed {have}; "
              "pass --allow-downgrade to apply it anyway", file=sys.stderr)
        return 1
    if args.apply and live_session_recent(project_root) and not args.in_session:
        print(f"ERROR: {STATE_FILE} changed in the last {LIVE_SESSION_SECONDS}s: a Claude Code session looks live, "
              "and apply rewrites the hooks that govern it. Run apply from a plain terminal, or pass "
              "--in-session and run /hooks immediately afterwards.", file=sys.stderr)
        return 6

    rows = three_way(project, installed, source, manifest)
    restore = set(args.restore or [])
    unknown = [p for p in restore if p not in {e["path"] for e in manifest["entries"]}]
    if unknown:
        print("ERROR: --restore path(s) not in the target manifest: " + ", ".join(unknown), file=sys.stderr)
        return 1
    ops, new_installed = compute_apply(project, installed, source, manifest, rows, restore)
    blocking = sum(len(rows[c]) for c in BLOCKING_CLASSES)
    hooks_touched = any(o["group"] == "hooks" for o in ops)
    mode = "APPLY" if args.apply else "DRY-RUN"

    print(f"=== Nexus apply: {have} → {version} ({d['url']} @ {d['ref']})  mode: {mode} ===")
    print("  " + "  ".join(f"{c}={len(rows[c])}" for c in PLAN_CLASSES if rows[c]))
    nothing_to_write = not ops and new_installed["units"] == installed["units"] and version == have
    print()
    verb = {"create": "created", "write": "written", "chmod": "chmod"} if args.apply else \
           {"create": "WOULD CREATE", "write": "WOULD WRITE", "chmod": "WOULD CHMOD"}
    for o in ops:
        tag = "  [restore]" if o["restore"] else ""
        detail = "" if o["strategy"] in ("replace", "create-if-absent") else f"  ({len(o['units'])} unit(s))"
        print(f"  [{verb[o['action']]:12}] {o['group']:12} {o['path']}{detail}{tag}")
    for cls in ("conflict", "unbaselined", "refused", "customized", "removed-locally", "obsolete"):
        for r in rows[cls]:
            if r["path"] in restore and cls in RESTORE_CLASSES:
                continue
            extra = f"  ({r['reason']})" if r.get("reason") else ""
            print(f"  [{cls:12}] {r['unit']}{extra}  (left alone)")

    if nothing_to_write:
        print("\nNothing to write: every unit is either current or deliberately left alone.")
        return 1 if blocking else 0
    if not args.apply:
        print(f"\nThis was a DRY-RUN: {len(ops)} file(s) would change. Re-run with --apply to write them.")
        return 1 if blocking else 0

    # Backups before the first write.
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = pathlib.Path(args.backup_dir).resolve() if args.backup_dir \
        else project_root / ".nexus" / "backups" / f"update-{version}-{ts}"
    for o in ops:
        if o["exists"]:
            dst = backup_dir / o["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(project_root / o["path"], dst)
    if (project_root / INSTALLED_FILE).is_file():
        (backup_dir / INSTALLED_FILE).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(project_root / INSTALLED_FILE, backup_dir / INSTALLED_FILE)

    # Writes, in group order; hooks last.
    for o in ops:
        target = project_root / o["path"]
        if o["data"] is not None:
            write_file_atomic(target, o["data"], o["mode"])
        elif o["mode"]:
            set_mode(target, o["mode"])
    write_json_atomic(project_root / INSTALLED_FILE, new_installed)

    print(f"\n  backup:    {backup_dir}")
    print(f"  baseline:  {INSTALLED_FILE} rewritten ({len(new_installed['units'])} units, Nexus {new_installed['nexus_version']})")
    problems = run_post_apply_validation(project_root)
    if problems:
        print("\nPOST-APPLY VALIDATION FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(f"Files are in place; restore from {backup_dir} or fix forward.", file=sys.stderr)
        return 5
    print("  validation: vault clean, validator selftest passed, hooks compile, settings.json sane")
    if hooks_touched:
        print("\nHooks were rewritten. In Claude Code, run:  /hooks")
    if blocking:
        print(f"\n{blocking} blocking row(s) were left alone (see above). Commit {INSTALLED_FILE} with the update.")
        return 1
    print(f"\nUpdate applied. Commit {INSTALLED_FILE} with the changed files.")
    return 0


# --------------------------------------------------------------------------
# Selftest — fixtures for the generation rules, every extractor, and §7.1
# --------------------------------------------------------------------------

_FM_BINDING = "---\ntype: {t}\nscope: system\nstatus: approved\ncreated: 2026-01-01\nupdated: 2026-01-01\nsource_of_truth: true\nknowledge_visibility: binding\ntags: [x]\n---\n\n# {t} {n}\n"
_FM_DEV = "---\ntype: plan\nscope: system\nstatus: draft\ncreated: 2026-01-01\nupdated: 2026-01-01\nsource_of_truth: false\ntags: [x]\n---\n\n# plan\n"
_FM_HIST = "---\ntype: decision\nscope: system\nstatus: deprecated\ncreated: 2026-01-01\nupdated: 2026-01-01\nsource_of_truth: false\ntags: [x]\n---\n\n# old\n"
_FM_SESSION = "---\ntype: session\nscope: system\nstatus: draft\ncreated: 2026-01-01\nupdated: 2026-01-01\nsource_of_truth: false\ntags: [x]\n---\n\n# s\n"
_FM_PROJECT = "---\ntype: spec\nscope: editor\nstatus: approved\ncreated: 2026-01-01\nupdated: 2026-01-01\nsource_of_truth: true\ntags: [x]\n---\n\n# editor\n"

_CLAUDE_MD = """# CLAUDE.md

## What this repository is

Project text that Nexus must never read.

## How work proceeds here

Protocol text.

```
## not a heading, inside a fence
```

## Writing rules (if you modify the vault)

More protocol.
"""

_INDEX_MD = """---
type: index
scope: system
status: approved
created: 2026-01-01
updated: 2026-01-01
source_of_truth: true
knowledge_visibility: binding
tags: [index]
---

# Index

- [Exit Gate](../specs/spec--system--exit-gate.md) — owned line
- [Editor](../specs/spec--editor--media.md) — project line
- `nexus-bootstrap.py` — no link, never a unit
"""

_SETTINGS = {
    "hooks": {
        "Stop": [{"matcher": "", "hooks": [
            {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-exit-gate.py", "timeout": 15},
            {"type": "command", "command": "$CLAUDE_PROJECT_DIR/scripts/project-hook.sh", "timeout": 5},
        ]}],
    }
}

SPEC_NAMES = ["exit-gate", "alpha", "beta", "gamma", "delta"]


def _w(root: pathlib.Path, rel: str, text: str, exec_bit: bool = False) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if exec_bit:
        p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _build_fixture(root: pathlib.Path, real_validator: pathlib.Path) -> None:
    _w(root, VERSION_FILE, "1.0.0\n")
    _w(root, ".claude/hooks/nexus-bootstrap.py", "#!/usr/bin/env python3\n", exec_bit=True)
    _w(root, ".claude/hooks/nexus-exit-gate.py", "#!/usr/bin/env python3\n", exec_bit=True)
    _w(root, ".claude/hooks/_nexus_common.py", "# common\n", exec_bit=True)
    _w(root, ".claude/skills/project-ingest/SKILL.md", "# skill\n")
    _w(root, ".claude/settings.json", json.dumps(_SETTINGS, indent=2) + "\n")
    _w(root, "tools/nexus-decide.py", "#!/usr/bin/env python3\n", exec_bit=True)
    shutil.copy2(real_validator, root / "tools" / "validate-vault.py")
    for n in SPEC_NAMES:
        _w(root, f"knowledge/specs/spec--system--{n}.md", _FM_BINDING.format(t="spec", n=n))
    _w(root, "knowledge/specs/spec--editor--media.md", _FM_PROJECT)
    _w(root, "knowledge/plans/plan--system--roadmap.md", _FM_DEV)
    _w(root, "knowledge/decisions/decision--system--old.md", _FM_HIST)
    _w(root, "knowledge/sessions/session--t--2026-01-01--deadbeef.md", _FM_SESSION)
    _w(root, "knowledge/index/index--system--project-navigation.md", _INDEX_MD)
    _w(root, "knowledge/.obsidian/app.json", "{}\n")
    _w(root, "knowledge/.obsidian/workspace.json", "{}\n")
    _w(root, "CLAUDE.md", _CLAUDE_MD)
    _w(root, ".gitignore", ".nexus/state*.json\n")
    _w(root, ".nexus/README.md", "# runtime\n")
    _w(root, "docs/nexus-implementation-report.md", "# report\n")
    _w(root, "README.md", "# template only\n")


def _git_commit_all(repo: pathlib.Path, message: str) -> None:
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message)


def _append(p: pathlib.Path, text: str) -> None:
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")


def selftest(real_root: pathlib.Path) -> int:
    failures: list[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="nexus-update-"))
    old_cache = os.environ.get("NEXUS_UPSTREAM_CACHE")
    os.environ["NEXUS_UPSTREAM_CACHE"] = str(tmp / "cache")
    try:
        template = tmp / "template"
        _build_fixture(template, real_root / "tools" / "validate-vault.py")

        # T1 — generation rules.
        m = generate_manifest(template)
        strat = {e["path"]: e["strategy"] for e in m["entries"]}
        check(strat.get(".claude/hooks/nexus-bootstrap.py") == "replace", "T1 hook is replace")
        check(next(e for e in m["entries"] if e["path"] == ".claude/hooks/nexus-bootstrap.py").get("mode") == "755", "T1 hook mode 755")
        check(strat.get("tools/nexus-decide.py") == "replace", "T1 tool is replace")
        check(strat.get(".claude/skills/project-ingest/SKILL.md") == "replace", "T1 skill is replace")
        check(strat.get("knowledge/specs/spec--system--exit-gate.md") == "replace", "T1 binding spec owned")
        check("knowledge/specs/spec--editor--media.md" not in strat, "T1 project doc not owned")
        check("knowledge/plans/plan--system--roadmap.md" not in strat, "T1 development doc not owned")
        check("knowledge/decisions/decision--system--old.md" not in strat, "T1 historical doc not owned")
        check("knowledge/sessions/session--t--2026-01-01--deadbeef.md" not in strat, "T1 session not owned")
        check(strat.get("knowledge/index/index--system--project-navigation.md") == "index-entries", "T1 index strategy")
        check(strat.get("knowledge/.obsidian/app.json") == "create-if-absent", "T1 obsidian shared config")
        check("knowledge/.obsidian/workspace.json" not in strat, "T1 obsidian workspace excluded")
        claude_entry = next(e for e in m["entries"] if e["path"] == "CLAUDE.md")
        check(claude_entry["strategy"] == "sections", "T1 CLAUDE.md sections")
        check(claude_entry["sections"] == ["## How work proceeds here", "## Writing rules (if you modify the vault)"], "T1 CLAUDE.md headings (project section and fenced text excluded)")
        check(strat.get(".claude/settings.json") == "hooks-merge", "T1 settings hooks-merge")
        check(strat.get(".gitignore") == "ensure-lines", "T1 gitignore ensure-lines")
        check(strat.get(".nexus/README.md") == "create-if-absent", "T1 runtime readme")
        check(strat.get("docs/nexus-implementation-report.md") == "replace", "T1 implementation report")
        check("README.md" not in strat and VERSION_FILE not in strat, "T1 template-only files excluded")
        check(m["nexus_version"] == "1.0.0", "T1 version copied from nexus.version")

        # T2 — unit extraction.
        owned = set(strat)
        sec = units_sections((template / "CLAUDE.md").read_bytes(), claude_entry["sections"])
        check(set(sec) == set(claude_entry["sections"]), "T2 sections extracted")
        check(b"inside a fence" in sec["## How work proceeds here"], "T2 fenced pseudo-heading stays in its section")
        check(b"Project text" not in b"".join(sec.values()), "T2 project section never read")
        idx = units_index_entries((template / "knowledge/index/index--system--project-navigation.md").read_bytes(),
                                  "knowledge/index/index--system--project-navigation.md", owned)
        check(list(idx) == ["../specs/spec--system--exit-gate.md"], "T2 index: only the owned link line")
        hk = units_hooks_merge((template / ".claude/settings.json").read_bytes())
        check(list(hk) == ["Stop/nexus-exit-gate.py"], "T2 hooks-merge: only the nexus hook")
        try:
            units_sections(b"## A\n\n## A\n", ["## A"])
            check(False, "T2 duplicate heading refused")
        except UpdaterError:
            pass
        check(normalize_text(b"a  \r\nb\n\n\n") == b"a\nb", "T2 normalization")
        check(matches_never_touch("knowledge/sessions/x.md") and matches_never_touch(".nexus/state 2.json")
              and not matches_never_touch("knowledge/specs/x.md"), "T2 never_touch matching")
        check(parse_semver("v1.2.3") == (1, 2, 3), "T2 semver")

        # T3 — verify: clean, then a registered hook without an entry.
        (template / MANIFEST_FILE).write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
        check(manifest_problems(template) == [], "T3 verify clean")
        cfg = json.loads((template / ".claude/settings.json").read_text())
        cfg["hooks"]["Stop"][0]["hooks"].append({"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-ghost.py"})
        (template / ".claude/settings.json").write_text(json.dumps(cfg, indent=2) + "\n")
        check(any("nexus-ghost.py" in p for p in manifest_problems(template)), "T3 verify catches unregistered hook")
        (template / ".claude/settings.json").write_text(json.dumps(_SETTINGS, indent=2) + "\n")

        # T4 — baseline and status on a host copy.
        host = tmp / "host"
        shutil.copytree(template, host)
        for rel in ("README.md", VERSION_FILE, MANIFEST_FILE):
            (host / rel).unlink()
        installed, inv = compute_baseline(WorkTree(host), WorkTree(template), m, "1.0.0")
        check(not inv["customized"] and not inv["absent"] and not inv["refused"], "T4 fresh copy: all identical")
        check("CLAUDE.md### How work proceeds here" in installed["units"], "T4 section unit recorded")
        check("knowledge/index/index--system--project-navigation.md#../specs/spec--system--exit-gate.md" in installed["units"], "T4 index unit recorded")
        check(".claude/settings.json#Stop/nexus-exit-gate.py" in installed["units"], "T4 hook entry unit recorded")
        write_json_atomic(host / INSTALLED_FILE, installed)
        st = compute_status(WorkTree(host), installed)
        check(len(st["unchanged"]) == len(installed["units"]) and not st["customized"], "T4 status all unchanged")

        spec = host / "knowledge/specs/spec--system--exit-gate.md"
        _append(spec, "\nhost edit\n")
        (host / ".claude/hooks/nexus-exit-gate.py").unlink()
        hook = host / ".claude/hooks/nexus-bootstrap.py"
        hook.chmod(hook.stat().st_mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH)
        cm = host / "CLAUDE.md"
        cm.write_text(cm.read_text().replace("Project text that Nexus must never read.", "Project text, edited by the host."))
        st = compute_status(WorkTree(host), installed)
        check(st["customized"] == ["knowledge/specs/spec--system--exit-gate.md"], "T4 edited spec is customized")
        check(st["removed-locally"] == [".claude/hooks/nexus-exit-gate.py"], "T4 deleted hook is removed-locally")
        check(st["mode-drift"] == [".claude/hooks/nexus-bootstrap.py"], "T4 chmod is mode-drift")
        check("CLAUDE.md### How work proceeds here" in st["unchanged"], "T4 project-section edit invisible")

        installed2, inv2 = compute_baseline(WorkTree(host), WorkTree(template), m, "1.0.0")
        check(inv2["customized"] == ["knowledge/specs/spec--system--exit-gate.md"], "T4 baseline marks the edit customized")
        check(installed2["units"]["knowledge/specs/spec--system--exit-gate.md"].get("customized_at_baseline") is True, "T4 customized_at_baseline flag")
        check(installed2["units"]["knowledge/specs/spec--system--exit-gate.md"]["sha256"]
              == installed["units"]["knowledge/specs/spec--system--exit-gate.md"]["sha256"], "T4 customized baseline SHA is upstream's")
        check(inv2["absent"] == [".claude/hooks/nexus-exit-gate.py"], "T4 baseline reports absent unit")
        shutil.rmtree(host)

        # T5 — GitRef source and the v1.0.0 tag.
        git(template, "init", "-q", "-b", "main")
        _git_commit_all(template, "fixture 1.0.0")
        git(template, "tag", "v1.0.0")
        ref = GitRef(template, "v1.0.0")
        check(ref.read(VERSION_FILE) == b"1.0.0\n", "T5 GitRef read")
        check(ref.mode(".claude/hooks/nexus-bootstrap.py") == "755", "T5 GitRef mode")
        check(ref.read("nope.txt") is None, "T5 GitRef missing path")
        check(read_manifest_from(ref)["nexus_version"] == "1.0.0", "T5 manifest read from ref")

        # T7 — every row of the three-way table, against a v1.1.0 fixture release.
        host = tmp / "host"
        shutil.copytree(template, host, ignore=shutil.ignore_patterns(".git"))
        for rel in ("README.md", VERSION_FILE, MANIFEST_FILE):
            (host / rel).unlink()
        installed, _ = compute_baseline(WorkTree(host), GitRef(template, "v1.0.0"), m, "1.0.0")
        write_json_atomic(host / INSTALLED_FILE, installed)

        # upstream 1.1.0 changes:
        _append(template / "knowledge/specs/spec--system--alpha.md", "\nupstream change\n")        # host untouched → update
        _append(template / "knowledge/specs/spec--system--beta.md", "\nupstream change\n")         # host edited differently → conflict
        _append(template / "knowledge/specs/spec--system--gamma.md", "\nsame change\n")            # host made the same change → converged
        _w(template, "knowledge/specs/spec--system--new.md", _FM_BINDING.format(t="spec", n="new"))  # → add
        _w(template, "knowledge/specs/spec--system--adopted.md", _FM_BINDING.format(t="spec", n="adopted"))  # host has identical → adopt
        _w(template, "knowledge/specs/spec--system--clash.md", _FM_BINDING.format(t="spec", n="clash"))      # host has different → unbaselined
        (template / "knowledge/specs/spec--system--delta.md").unlink()                             # → obsolete
        cm = template / "CLAUDE.md"
        cm.write_text(cm.read_text().replace("Protocol text.", "Protocol text, revised."))         # section → update
        _append(template / "knowledge/index/index--system--project-navigation.md",
                "- [Alpha](../specs/spec--system--alpha.md) — new owned line\n")                   # index line → add
        _w(template, VERSION_FILE, "1.1.0\n")
        (template / MANIFEST_FILE).write_text(json.dumps(generate_manifest(template), indent=2) + "\n")
        _git_commit_all(template, "fixture 1.1.0")
        git(template, "tag", "v1.1.0")

        # host-side changes:
        _append(host / "knowledge/specs/spec--system--beta.md", "\nhost change\n")
        _append(host / "knowledge/specs/spec--system--gamma.md", "\nsame change\n")
        _append(host / "knowledge/specs/spec--system--exit-gate.md", "\nhost only\n")               # → customized
        (host / "knowledge/specs/spec--system--delta.md").unlink()                                 # obsolete, also gone locally
        (host / "tools/nexus-decide.py").unlink()                                                  # → removed-locally
        _w(host, "knowledge/specs/spec--system--adopted.md", _FM_BINDING.format(t="spec", n="adopted"))
        _w(host, "knowledge/specs/spec--system--clash.md", "not the same\n")
        _append(host / "knowledge/index/index--system--project-navigation.md",
                "- [Ours](../specs/spec--editor--media.md) — project line stays invisible\n")
        hook = host / ".claude/hooks/nexus-bootstrap.py"
        hook.chmod(hook.stat().st_mode & ~stat.S_IXUSR)                                            # → mode-drift

        target = GitRef(template, "refs/tags/v1.1.0")
        m11 = read_manifest_from(target)
        rows = three_way(WorkTree(host), installed, target, m11)
        by = {c: sorted(r["unit"] for r in rs) for c, rs in rows.items()}
        check(by["update"] == ["CLAUDE.md### How work proceeds here", "knowledge/specs/spec--system--alpha.md"], f"T7 update rows: {by['update']}")
        check(by["conflict"] == ["knowledge/specs/spec--system--beta.md"], f"T7 conflict: {by['conflict']}")
        check(by["converged"] == ["knowledge/specs/spec--system--gamma.md"], f"T7 converged: {by['converged']}")
        check(by["customized"] == ["knowledge/specs/spec--system--exit-gate.md"], f"T7 customized: {by['customized']}")
        compared_adds = sorted(r["unit"] for r in rows["add"] if r["strategy"] in COMPARED_STRATEGIES)
        check(compared_adds == ["knowledge/index/index--system--project-navigation.md#../specs/spec--system--alpha.md",
                                "knowledge/specs/spec--system--new.md"], f"T7 add: {compared_adds}")
        check(by["adopt"] == ["knowledge/specs/spec--system--adopted.md"], f"T7 adopt: {by['adopt']}")
        check(by["unbaselined"] == ["knowledge/specs/spec--system--clash.md"], f"T7 unbaselined: {by['unbaselined']}")
        check(by["obsolete"] == ["knowledge/specs/spec--system--delta.md"], f"T7 obsolete: {by['obsolete']}")
        check(by["removed-locally"] == ["tools/nexus-decide.py"], f"T7 removed-locally: {by['removed-locally']}")
        check(by["mode-drift"] == [".claude/hooks/nexus-bootstrap.py"], f"T7 mode-drift: {by['mode-drift']}")
        check("knowledge/specs/spec--system--editor--media.md" not in str(by), "T7 project index line invisible")
        check(".claude/settings.json#Stop/nexus-exit-gate.py" in by["unchanged"], "T7 hook entry unchanged")
        check(len(by["refused"]) == 0, f"T7 no refusals: {by['refused']}")
        d = unit_diff(WorkTree(host), target, m11, "knowledge/specs/spec--system--beta.md")
        check("-host change" in d and "+upstream change" in d, "T7 plan --diff shows both sides")
        # ensure-lines and create-if-absent rows
        (host / "knowledge/.obsidian/app.json").unlink()
        rows2 = three_way(WorkTree(host), installed, target, m11)
        adds = {r["unit"] for r in rows2["add"]}
        check("knowledge/.obsidian/app.json" in adds, "T7 create-if-absent missing → add")
        check(".gitignore#.nexus/backups/" in adds, "T7 ensure-lines missing line → add")
        # bare-file sections: a heading the host renamed is 'removed-locally', not a crash
        cmh = host / "CLAUDE.md"
        cmh.write_text(cmh.read_text().replace("## Writing rules (if you modify the vault)", "## Writing rules"))
        rows3 = three_way(WorkTree(host), installed, target, m11)
        check("CLAUDE.md### Writing rules (if you modify the vault)" in {r["unit"] for r in rows3["removed-locally"]}, "T7 renamed heading is removed-locally")

        # T8 — cache clone from a file:// URL (a bare path would be read as a worktree), ref selection, check, guess.
        url = template.as_uri()
        repo = ensure_cache(url)
        check(repo.is_dir() and (repo / "HEAD").is_file(), "T8 bare cache created")
        check(select_ref(repo, None) == "refs/tags/v1.1.0", "T8 highest tag selected")
        check(display_ref(select_ref(repo, "main")) == "main", "T8 branch resolved")
        src = open_upstream(url, None)
        check(isinstance(src, GitRef) and src.ref == "v1.1.0" and upstream_version(src) == "1.1.0", "T8 open_upstream via cache")
        check(ensure_cache(url) == repo, "T8 fetch on existing cache is a no-op path")
        check(ensure_cache(url, offline=True) == repo, "T8 offline uses the cache")
        scores = guess_ref(WorkTree(host), repo, url)
        check(scores and display_ref(scores[0][2]) in {"v1.0.0"} or scores[0][0] >= scores[-1][0], f"T8 guess ranks refs: {[(s[0], display_ref(s[2])) for s in scores]}")
        try:
            ensure_cache(str(tmp / "nowhere"), offline=True)
            check(False, "T8 offline without cache raises")
        except UpdaterError as e:
            check(e.code == 3, "T8 offline error code 3")

        # T8b — check/plan through the CLI on the fixture host (output swallowed).
        import contextlib
        import io

        last_output = [""]

        def quiet_main(argv: list[str]) -> int:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = main(argv)
            last_output[0] = out.getvalue() + err.getvalue()
            return rc

        rc = quiet_main(["--project-root", str(host), "check", "--upstream", url])
        rec = read_update_check(host)
        check(rc == 0 and rec and rec["status"] == "ok" and rec["upstream_version"] == "1.1.0", "T8 check writes update-check.json")
        rc = quiet_main(["--project-root", str(host), "plan", "--upstream", url, "--json"])
        check(rc == 1, "T8 plan exits 1 with blocking rows")
        rc = quiet_main(["--project-root", str(host), "check", "--upstream", (tmp / "nowhere-url").as_uri()])
        rec = read_update_check(host)
        check(rc == 3 and rec and rec["status"] == "unreachable", "T8 unreachable check recorded in the cache file")

        # T9 — apply on the T7 host: writes the clean rows, leaves the rest, records the baseline.
        _w(host, "knowledge/specs/spec--system--clash.md", _FM_BINDING.format(t="spec", n="clash") + "\nhost version\n")
        backup = tmp / "backup"

        def tree_hash(root: pathlib.Path) -> str:
            h = hashlib.sha256()
            for p in sorted(root.rglob("*")):
                if p.is_file() and ".nexus" not in p.parts:
                    h.update(p.relative_to(root).as_posix().encode())
                    h.update(p.read_bytes())
                    h.update(b"x" if p.stat().st_mode & stat.S_IXUSR else b"-")
            return h.hexdigest()

        rc = quiet_main(["--project-root", str(host), "apply", "--upstream", url])          # dry-run
        check(rc == 1, "T9 dry-run exits 1 (blocking rows present)")
        check((host / "knowledge/specs/spec--system--alpha.md").read_text().count("upstream change") == 0, "T9 dry-run wrote nothing")
        rc = quiet_main(["--project-root", str(host), "apply", "--upstream", url, "--apply", "--backup-dir", str(backup)])
        check(rc == 1, f"T9 apply exits 1 (conflict + unbaselined left alone); rc={rc}\n{last_output[0]}")
        up11 = GitRef(template, "refs/tags/v1.1.0")
        rd = lambda rel: (host / rel).read_bytes()  # noqa: E731
        check(rd("knowledge/specs/spec--system--alpha.md") == up11.read("knowledge/specs/spec--system--alpha.md"), "T9 update written")
        check(b"host change" in rd("knowledge/specs/spec--system--beta.md"), "T9 conflict untouched")
        check(b"host only" in rd("knowledge/specs/spec--system--exit-gate.md"), "T9 customized untouched")
        check(b"host version" in rd("knowledge/specs/spec--system--clash.md"), "T9 unbaselined untouched")
        check((host / "knowledge/specs/spec--system--new.md").is_file(), "T9 add created")
        check(not (host / "knowledge/specs/spec--system--delta.md").exists(), "T9 obsolete not resurrected")
        check(not (host / "tools/nexus-decide.py").exists(), "T9 removed-locally stays removed")
        check((host / ".claude/hooks/nexus-bootstrap.py").stat().st_mode & stat.S_IXUSR, "T9 mode-drift fixed")
        cm_text = (host / "CLAUDE.md").read_text()
        check("Protocol text, revised." in cm_text and "Project text that Nexus must never read." in cm_text,
              f"T9 section replaced, project section kept:\n{cm_text}")
        check("## Writing rules\n" in cm_text and "## Writing rules (if you modify the vault)" not in cm_text, "T9 renamed heading left alone")
        idx_text = (host / "knowledge/index/index--system--project-navigation.md").read_text()
        check("spec--system--alpha.md) — new owned line" in idx_text and "project line stays invisible" in idx_text
              and idx_text.count("spec--system--exit-gate.md") == 1, "T9 index line inserted, project line kept")
        gi = (host / ".gitignore").read_text()
        check(".nexus/backups/" in gi and ".nexus/update-check.json" in gi and gi.count(".nexus/state*.json") == 1, "T9 ensure-lines appended once")
        check((host / "knowledge/.obsidian/app.json").is_file(), "T9 create-if-absent recreated")
        check((backup / "knowledge/specs/spec--system--alpha.md").is_file() and (backup / "CLAUDE.md").is_file()
              and (backup / INSTALLED_FILE).is_file(), "T9 backups taken before writing")
        inst = load_installed(host)
        check(inst["nexus_version"] == "1.1.0" and inst["origin"] == "update", "T9 baseline version bumped")
        check(inst["units"]["knowledge/specs/spec--system--alpha.md"]["sha256"] == sha256_bytes(up11.read("knowledge/specs/spec--system--alpha.md")), "T9 baseline records upstream sha for update")
        check(inst["units"]["knowledge/specs/spec--system--beta.md"]["sha256"] == installed["units"]["knowledge/specs/spec--system--beta.md"]["sha256"], "T9 conflict keeps old baseline")
        check("knowledge/specs/spec--system--adopted.md" in inst["units"] and "knowledge/specs/spec--system--clash.md" not in inst["units"], "T9 adopt recorded, unbaselined not")
        check("knowledge/specs/spec--system--delta.md" not in inst["units"], "T9 obsolete dropped from baseline")
        check("knowledge/specs/spec--system--gamma.md" in inst["units"]
              and inst["units"]["knowledge/specs/spec--system--gamma.md"]["sha256"] == sha256_bytes(up11.read("knowledge/specs/spec--system--gamma.md")), "T9 converged recorded")

        before = tree_hash(host)
        rc = quiet_main(["--project-root", str(host), "apply", "--upstream", url, "--apply", "--backup-dir", str(tmp / "backup2")])
        check(rc == 1 and tree_hash(host) == before, f"T9 second apply is a no-op (still reports the blocking rows); rc={rc}\n{last_output[0]}")
        rows_after = three_way(WorkTree(host), load_installed(host), up11, m11)
        check(not rows_after["update"] and not rows_after["add"] and not rows_after["mode-drift"], "T9 nothing left to write")

        rc = quiet_main(["--project-root", str(host), "apply", "--upstream", url, "--apply",
                         "--restore", "knowledge/specs/spec--system--beta.md", "--backup-dir", str(tmp / "backup3")])
        check(rd("knowledge/specs/spec--system--beta.md") == up11.read("knowledge/specs/spec--system--beta.md"), "T9 --restore overwrote the conflict")
        check(load_installed(host)["units"]["knowledge/specs/spec--system--beta.md"]["sha256"]
              == sha256_bytes(up11.read("knowledge/specs/spec--system--beta.md")), "T9 --restore recorded")
        check(b"host only" in rd("knowledge/specs/spec--system--exit-gate.md"), "T9 --restore is per path only")

        # live-session guard
        write_json_atomic(host / STATE_FILE, {"session_id": "x"})
        rc = quiet_main(["--project-root", str(host), "apply", "--upstream", url, "--apply", "--backup-dir", str(tmp / "backup4")])
        check(rc == 6, "T9 live session refused without --in-session")
        (host / STATE_FILE).unlink()

        # hooks-merge writer: upstream changes a nexus hook's timeout; a foreign hook survives.
        s2 = json.loads(json.dumps(_SETTINGS))
        s2["hooks"]["Stop"][0]["hooks"][0]["timeout"] = 30
        s2["hooks"]["Stop"].append({"matcher": "", "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-bootstrap.py"}]})
        merged = json.loads(apply_hooks_merge(json.dumps(_SETTINGS).encode(), json.dumps(s2).encode(),
                                              ["Stop/nexus-exit-gate.py", "Stop/nexus-bootstrap.py"]))
        cmds = [h["command"] for g in merged["hooks"]["Stop"] for h in g["hooks"]]
        check(any("project-hook.sh" in c for c in cmds), "T9 hooks-merge keeps the foreign hook")
        exit_hook = next(h for g in merged["hooks"]["Stop"] for h in g["hooks"] if "nexus-exit-gate" in h["command"])
        check(exit_hook["timeout"] == 30, "T9 hooks-merge takes the upstream entry")
        check(any("nexus-bootstrap.py" in c for c in cmds), "T9 hooks-merge adds a new nexus hook")
        check(units_hooks_merge(json.dumps(merged).encode()) == units_hooks_merge(json.dumps(s2).encode()), "T9 merged units equal upstream units")

        # T10 — feedback notes: push to the mailbox, receipts, re-push on change, list / show / archive, inbox notice.
        note_text = (
            "---\ntype: feedback\nscope: nexus\nstatus: draft\ncreated: 2026-01-03\nupdated: 2026-01-03\n"
            "source_of_truth: false\nknowledge_visibility: development\nkind: bug\nnexus_version: 1.0.0\n"
            "host: fixture-host\ntouches: [.claude/hooks/nexus-exit-gate.py]\ndelivered: []\ntags: [feedback, nexus]\n---\n\n"
            "# Exit gate too strict\n\n## What happened\n\nDenied.\n\n## What is proposed\n\nRelax.\n\n## Attachment\n\nnone\n"
        )
        _w(host, f"{FEEDBACK_DIR}/feedback--nexus--exit-gate-too-strict.md", note_text)
        _w(host, f"{FEEDBACK_DIR}/feedback--nexus--thanks.md",
           note_text.replace("kind: bug", "kind: praise").replace("delivered: []", "delivered:\n  - issue:#7")
                    .replace("# Exit gate too strict", "# Thanks"))
        check(note_fingerprint(note_text) == note_fingerprint(note_text.replace("delivered: []", "delivered: [inbox:x]")
                                                              .replace("updated: 2026-01-03", "updated: 2026-02-02")),
              "T10 fingerprint ignores delivered/updated")
        rewritten = set_frontmatter_fields(note_text.replace("delivered: []", "delivered:\n  - issue:#7"),
                                           {"delivered": ["issue:#7", "inbox:t"], "updated": "2026-02-02"})
        check("delivered: [issue:#7, inbox:t]" in rewritten and "updated: 2026-02-02" in rewritten
              and "  - issue:#7" not in rewritten and rewritten.endswith("none\n"), f"T10 frontmatter rewrite:\n{rewritten}")
        rc = quiet_main(["--project-root", str(host), "feedback", "status"])
        check(rc == 0 and last_output[0].count("PENDING") == 2, f"T10 status shows both pending:\n{last_output[0]}")
        rc = quiet_main(["--project-root", str(host), "feedback", "push", "--dry-run"])
        check(rc == 0 and not inbox_root().exists() and "delivered: []" in (host / FEEDBACK_DIR / "feedback--nexus--exit-gate-too-strict.md").read_text(),
              "T10 push --dry-run writes nothing")
        rc = quiet_main(["--project-root", str(host), "feedback", "push"])
        delivered = sorted((inbox_root() / "fixture-host").glob("*.md"))
        check(rc == 0 and len(delivered) == 2 and all(p.with_suffix(".json").is_file() for p in delivered), f"T10 push delivered two notes:\n{last_output[0]}")
        n1 = (host / FEEDBACK_DIR / "feedback--nexus--exit-gate-too-strict.md").read_text()
        check("delivered: [inbox:" in n1 and "updated: 2026-01-03" not in n1, "T10 receipt appended and updated bumped")
        n2 = (host / FEEDBACK_DIR / "feedback--nexus--thanks.md").read_text()
        check("delivered: [issue:#7, inbox:" in n2, "T10 existing receipts kept")
        rc = quiet_main(["--project-root", str(host), "feedback", "push"])
        check(rc == 0 and "already delivered" in last_output[0] and len(list((inbox_root() / "fixture-host").glob("*.md"))) == 2,
              "T10 second push is a no-op")
        p1 = host / FEEDBACK_DIR / "feedback--nexus--exit-gate-too-strict.md"
        p1.write_text(p1.read_text().replace("Relax.", "Relax the regex."))
        import time as _time
        _time.sleep(1.1)  # distinct timestamp prefix
        rc = quiet_main(["--project-root", str(host), "feedback", "push"])
        check(rc == 0 and len(list((inbox_root() / "fixture-host").glob("*.md"))) == 3, "T10 edited note delivered again")
        check(p1.read_text().count("inbox:") == 2, "T10 second receipt appended")
        rc = quiet_main(["--project-root", str(host), "feedback", "push"])
        check("already delivered" in last_output[0], "T10 no-op after re-delivery")
        total, per_host = inbox_summary()
        check(total == 3 and per_host == {"fixture-host": 3}, f"T10 inbox summary {total} {per_host}")
        rc = quiet_main(["feedback", "list"])
        check(rc == 0 and last_output[0].count("fixture-host") == 3 and "Thanks" in last_output[0], f"T10 list:\n{last_output[0]}")
        rc = quiet_main(["feedback", "show", "1"])
        check(rc == 0 and "## What happened" in last_output[0], "T10 show prints the note")
        rc = quiet_main(["feedback", "archive", "1"])
        check(rc == 0 and inbox_summary()[0] == 2 and len(list((archive_root() / "fixture-host").glob("*"))) == 2, "T10 archive moves note + sidecar")
        rc = quiet_main(["feedback", "archive", "--all-from", "fixture-host"])
        check(rc == 0 and inbox_summary()[0] == 0, "T10 archive --all-from empties the inbox")
        rc = quiet_main(["--project-root", str(host), "feedback", "push"])
        check("already delivered" in last_output[0], "T10 archived copies still count as delivered")
        rc = quiet_main(["feedback", "list", "--all"])
        check("(archived)" in last_output[0], "T10 list --all shows archived")
        # inbox notice from the real hook, run against the fixture template (manifest present, no baseline)
        _w(host, f"{FEEDBACK_DIR}/feedback--nexus--another.md", note_text.replace("too-strict", "another").replace("# Exit gate too strict", "# Another"))
        quiet_main(["--project-root", str(host), "feedback", "push"])
        hook = real_root / ".claude" / "hooks" / "nexus-update-check.py"
        if hook.is_file():
            r = subprocess.run([sys.executable, str(hook)], input='{"hook_event_name":"SessionStart"}', capture_output=True,
                               text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(template)}, timeout=30)
            check(r.returncode == 0 and "feedback inbox: 1 note" in r.stdout and "fixture-host (1)" in r.stdout,
                  f"T10 inbox notice in the template: {r.stdout[:200]!r} {r.stderr[:200]!r}")
            r = subprocess.run([sys.executable, str(hook)], input='{"hook_event_name":"SessionStart"}', capture_output=True,
                               text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(host)}, timeout=30)
            check(r.returncode == 0 and "feedback inbox" not in r.stdout, "T10 no inbox notice in a host")
    except UpdaterError as e:
        failures.append(f"unexpected UpdaterError during selftest: {e}")
    finally:
        if old_cache is None:
            os.environ.pop("NEXUS_UPSTREAM_CACHE", None)
        else:
            os.environ["NEXUS_UPSTREAM_CACHE"] = old_cache
        shutil.rmtree(tmp, ignore_errors=True)

    # T6 — the real template's manifest, when run inside it.
    if (real_root / MANIFEST_FILE).is_file():
        problems = manifest_problems(real_root)
        check(problems == [], "T6 real manifest in sync: " + "; ".join(problems))

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        print(f"selftest: {len(failures)} failure(s)")
        return 1
    print("selftest: all checks passed")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="nexus-update.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=os.environ.get("CLAUDE_PROJECT_DIR") or ".",
                    help="project (host or template) root; default: $CLAUDE_PROJECT_DIR or cwd")
    ap.add_argument("--selftest", action="store_true", help="run the fixtures and exit")
    sub = ap.add_subparsers(dest="command")

    m = sub.add_parser("manifest", help="template side: generate or verify nexus.manifest.json")
    m.add_argument("action", choices=["generate", "verify"])

    def upstream_opts(p: argparse.ArgumentParser) -> None:
        p.add_argument("--upstream", help="Nexus git URL (cached under ~/.cache/nexus) or a local checkout; "
                                          "default: the URL recorded in the baseline")
        p.add_argument("--ref", help="tag, branch or commit; default: highest v* tag")
        p.add_argument("--offline", action="store_true", help="use the cache without fetching")

    b = sub.add_parser("baseline", help="host side: record .nexus/installed.json against an upstream ref")
    upstream_opts(b)
    b.add_argument("--version", help="Nexus version to record; default: upstream's nexus.version")
    b.add_argument("--guess", action="store_true", help="score tags and recent commits, pick the best match")
    b.add_argument("--dry-run", action="store_true", help="print the inventory, write nothing")
    b.add_argument("--force", action="store_true", help="rewrite an existing baseline / skip the project guard")

    s = sub.add_parser("status", help="host side: compare baselined units with the working tree")
    s.add_argument("--json", dest="as_json", action="store_true")

    c = sub.add_parser("check", help="host side: is a newer Nexus available? (writes .nexus/update-check.json)")
    upstream_opts(c)
    c.add_argument("--json", dest="as_json", action="store_true")

    p = sub.add_parser("plan", help="host side: the three-way table baseline / local / upstream")
    upstream_opts(p)
    p.add_argument("--diff", metavar="PATH", help="print the local↔upstream diff of one owned path")
    p.add_argument("--allow-downgrade", action="store_true")
    p.add_argument("--verbose", action="store_true", help="also list unchanged units")
    p.add_argument("--json", dest="as_json", action="store_true")

    a = sub.add_parser("apply", help="host side: adopt the target version (dry-run unless --apply)")
    upstream_opts(a)
    a.add_argument("--apply", action="store_true", help="actually write (default: dry-run)")
    a.add_argument("--restore", action="append", metavar="PATH",
                   help="overwrite this customized / conflicting / deleted path with upstream (repeatable)")
    a.add_argument("--backup-dir", help="override .nexus/backups/update-<version>-<timestamp>")
    a.add_argument("--allow-downgrade", action="store_true")
    a.add_argument("--in-session", action="store_true",
                   help="proceed although a Claude Code session looks live (then run /hooks)")

    f = sub.add_parser("feedback", help="feedback notes: host side push/status, template side list/show/archive")
    fs = f.add_subparsers(dest="feedback_action")
    fs.add_parser("status", help="host: list notes and their delivery state")
    fp = fs.add_parser("push", help="host: copy undelivered / changed notes into the local mailbox")
    fp.add_argument("--dry-run", action="store_true")
    fl = fs.add_parser("list", help="template: list the mailbox")
    fl.add_argument("--all", action="store_true", help="include archived entries")
    fsh = fs.add_parser("show", help="template: print one entry")
    fsh.add_argument("selector", help="entry number from `list`, or file name / slug")
    fa = fs.add_parser("archive", help="template: move an entry to inbox-archive/")
    fa.add_argument("selector", nargs="?", help="entry number from `list`, or file name / slug")
    fa.add_argument("--all-from", metavar="HOST", help="archive every live entry from this host")
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        if args.selftest:
            return selftest(pathlib.Path(args.project_root).resolve())
        if args.command == "manifest":
            return cmd_manifest(args)
        if args.command == "baseline":
            return cmd_baseline(args)
        if args.command == "status":
            return cmd_status(args)
        if args.command == "check":
            return cmd_check(args)
        if args.command == "plan":
            return cmd_plan(args)
        if args.command == "apply":
            return cmd_apply(args)
        if args.command == "feedback":
            if not args.feedback_action:
                ap.parse_args(["feedback", "--help"])
            return cmd_feedback(args)
        ap.print_help()
        return 0
    except UpdaterError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
