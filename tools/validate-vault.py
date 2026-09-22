#!/usr/bin/env python3
"""Validate Knowledge Vault documents against the Nexus frontmatter contract.

Codifies, in one place, the rules stated in:
  - knowledge/specs/spec--system--document-frontmatter.md
  - knowledge/specs/spec--system--knowledge-vault.md   (naming convention)
  - knowledge/specs/spec--system--knowledge-visibility.md

Usage:
    tools/validate-vault.py                       # whole vault
    tools/validate-vault.py knowledge/specs       # a subtree
    tools/validate-vault.py path/to/doc.md        # one file
    tools/validate-vault.py --json                # machine-readable
    tools/validate-vault.py --strict              # warnings fail too
    tools/validate-vault.py --quiet               # findings only, no summary

Exit codes: 0 = no errors, 1 = errors found, 2 = bad invocation.

This tool NEVER edits a document. Per spec--system--knowledge-visibility.md
§"Override and Validation Rules" rule 4, invalid combinations are a judgement
call for a human or the agent — the tool surfaces them and stops there.

No third-party dependencies: the frontmatter parser below accepts exactly the
YAML subset the spec permits, which is stricter (and therefore more useful
here) than a general YAML parser.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

# --------------------------------------------------------------------------
# Contract — mirrors spec--system--document-frontmatter.md. Keep in sync.
# --------------------------------------------------------------------------

REQUIRED_FIELDS = ["type", "scope", "status", "created", "updated", "source_of_truth", "tags"]

# Fields that exist only on type: feedback (spec--system--feedback-channel.md).
FEEDBACK_FIELDS = {"kind", "nexus_version", "host", "touches", "delivered"}
FEEDBACK_REQUIRED = ["kind", "nexus_version", "host"]
FEEDBACK_KINDS = {"bug", "wish", "praise"}
FEEDBACK_SECTIONS = ["## What happened", "## What is proposed", "## Attachment"]

REGISTERED_FIELDS = (
    set(REQUIRED_FIELDS) | {"knowledge_visibility", "theme", "session_id", "governs"} | FEEDBACK_FIELDS
)

# type -> directories where that type may live
TYPE_DIRS = {
    "architecture": {"architecture"},
    "bug": {"bugs"},
    "decision": {"decisions", "business"},
    "feedback": {"feedback"},
    "glossary": {"glossary"},
    "index": {"index"},
    "invariant": {"invariants"},
    "pattern": {"patterns"},
    "plan": {"plans"},
    "prompt": {"runbooks"},
    "question": {"open-questions"},
    "runbook": {"runbooks"},
    "session": {"sessions"},
    "spec": {"specs"},
}

STATUSES = {"draft", "in-progress", "review", "approved", "deprecated"}
STATUS_SYNONYMS = {"accepted": "approved", "archived": "deprecated"}

VISIBILITIES = {"binding", "development", "historical"}

# Registered filename-prefix exceptions: prefix -> the type it stands for.
PREFIX_EXCEPTIONS = {"summary": "session", "adr": "decision"}

# <type>--<scope>--<name>.md, with optional generated --<date>[--<id8>] suffix.
NAME_RE = re.compile(
    r"^[a-z0-9]+--[a-z0-9-]+--[a-z0-9-]+(?:--\d{4}-\d{2}-\d{2}(?:--[0-9a-f]{8})?)?\.md$"
)
# Hand-authored documents use YYYY-MM-DD. Machine-generated ones (the session
# writer rewrites an archive several times a day) may carry a full timestamp.
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Link targets that are illustrative placeholders inside specs, not real paths.
LINK_PLACEHOLDERS = {"relative/path.md"}


class Finding:
    __slots__ = ("path", "line", "code", "level", "message")

    def __init__(self, path: str, line: int, code: str, level: str, message: str):
        self.path, self.line, self.code, self.level, self.message = path, line, code, level, message

    def as_dict(self) -> dict:
        return {
            "file": self.path,
            "line": self.line,
            "code": self.code,
            "level": self.level,
            "message": self.message,
        }

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.level.upper()} [{self.code}] {self.message}"


# --------------------------------------------------------------------------
# Frontmatter parsing (allowed subset only)
# --------------------------------------------------------------------------

def parse_frontmatter(block: str, offset: int) -> tuple[dict, dict, list[tuple[str, str]]]:
    """Parse the allowed YAML subset.

    Returns (values, line_numbers, errors). `values` maps key -> str | list[str].
    `line_numbers` maps key -> 1-based line in the file. `errors` is a list of
    (code, message) for constructs outside the permitted subset.
    """
    values: dict[str, object] = {}
    lines_at: dict[str, int] = {}
    errors: list[tuple[str, str]] = []
    current_key: str | None = None

    for i, raw in enumerate(block.split("\n")):
        lineno = offset + i
        if "\t" in raw:
            errors.append(("FM002", f"line {lineno}: tab character — YAML forbids tabs for indentation"))
            continue
        if not raw.strip():
            current_key = None
            continue

        if re.match(r"^\s*\*\s+", raw):
            errors.append((
                "FM002",
                f"line {lineno}: '*' bullet is not YAML — use '- item' or inline [a, b]",
            ))
            continue

        # Block sequence item. YAML permits these at the parent key's own
        # indentation, so leading whitespace is optional.
        m_item = re.match(r"^\s*-\s+(.*)$", raw)
        if m_item:
            if current_key is None:
                errors.append(("FM002", f"line {lineno}: list item with no parent key"))
                continue
            values.setdefault(current_key, [])
            if isinstance(values[current_key], list):
                values[current_key].append(m_item.group(1).strip())
            continue

        m_kv = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", raw)
        if not m_kv:
            errors.append(("FM002", f"line {lineno}: not a 'key: value' pair — {raw.strip()[:60]!r}"))
            continue

        key, val = m_kv.group(1), m_kv.group(2).strip()
        if key in values:
            errors.append(("FM003", f"line {lineno}: duplicate key {key!r}"))
        lines_at[key] = lineno
        if val == "":
            current_key = key
            values[key] = []
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            values[key] = [p.strip() for p in inner.split(",") if p.strip()] if inner else []
            current_key = None
        else:
            values[key] = val
            current_key = None

    return values, lines_at, errors


# --------------------------------------------------------------------------
# Document validation
# --------------------------------------------------------------------------

def validate_document(path: pathlib.Path, root: pathlib.Path, check_links: bool) -> list[Finding]:
    rel = path.relative_to(root).as_posix()
    out: list[Finding] = []

    def add(line: int, code: str, level: str, msg: str) -> None:
        out.append(Finding(rel, line, code, level, msg))

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        add(1, "IO001", "error", f"cannot read file: {exc}")
        return out

    m = FRONTMATTER_RE.match(text)
    if not m:
        add(1, "FM001", "error", "no YAML frontmatter block at the top of the file")
        return out

    values, lines_at, parse_errors = parse_frontmatter(m.group(1), offset=2)
    for code, msg in parse_errors:
        add(2, code, "error", msg)

    def ln(key: str) -> int:
        return lines_at.get(key, 2)

    # -- required fields ---------------------------------------------------
    for field in REQUIRED_FIELDS:
        if field not in values:
            add(2, "FM004", "error", f"missing required field {field!r}")

    # -- unregistered fields ----------------------------------------------
    for key in values:
        if key not in REGISTERED_FIELDS:
            add(
                ln(key),
                "FM005",
                "error",
                f"unregistered field {key!r} — register it in "
                "spec--system--document-frontmatter.md §'Registered extension fields' or remove it",
            )

    doc_type = values.get("type")
    status = values.get("status")
    visibility = values.get("knowledge_visibility")
    sot = values.get("source_of_truth")
    directory = path.parent.name

    # -- type --------------------------------------------------------------
    if isinstance(doc_type, str):
        if doc_type not in TYPE_DIRS:
            add(
                ln("type"), "FM006", "error",
                f"type {doc_type!r} is not in the enum ({', '.join(sorted(TYPE_DIRS))})",
            )
        elif directory not in TYPE_DIRS[doc_type]:
            add(
                ln("type"), "NM002", "error",
                f"type {doc_type!r} belongs in {'/, '.join(sorted(TYPE_DIRS[doc_type]))}/ "
                f"but the document is in {directory}/",
            )
    elif doc_type is not None:
        add(ln("type"), "FM006", "error", "type must be a scalar string")

    # -- status ------------------------------------------------------------
    if isinstance(status, str) and status not in STATUSES:
        hint = STATUS_SYNONYMS.get(status)
        suffix = f" — use {hint!r} instead" if hint else f" ({', '.join(sorted(STATUSES))})"
        add(ln("status"), "FM007", "error", f"status {status!r} is not in the enum{suffix}")

    # -- dates -------------------------------------------------------------
    for field in ("created", "updated"):
        val = values.get(field)
        if isinstance(val, str) and not DATE_RE.match(val):
            add(ln(field), "FM008", "error", f"{field} {val!r} is not ISO YYYY-MM-DD")
    created, updated = values.get("created"), values.get("updated")
    if (
        isinstance(created, str) and isinstance(updated, str)
        and DATE_RE.match(created) and DATE_RE.match(updated) and updated < created
    ):
        add(ln("updated"), "FM008", "error", f"updated ({updated}) is earlier than created ({created})")

    # -- source_of_truth ---------------------------------------------------
    if sot is not None and sot not in ("true", "false"):
        add(ln("source_of_truth"), "FM009", "error", f"source_of_truth must be true or false, got {sot!r}")

    # -- tags --------------------------------------------------------------
    if "tags" in values and not isinstance(values["tags"], list):
        add(ln("tags"), "FM010", "error", "tags must be a list: [a, b] or '- item' lines")

    # -- knowledge_visibility ---------------------------------------------
    if visibility is None:
        add(
            2, "FM100", "warning",
            "knowledge_visibility is absent — the conservative fallback applies; "
            "consider declaring it explicitly",
        )
    elif visibility not in VISIBILITIES:
        add(
            ln("knowledge_visibility"), "VS001", "error",
            f"knowledge_visibility {visibility!r} must be one of {', '.join(sorted(VISIBILITIES))}",
        )
    else:
        # Invalid combinations. Reported, never normalized.
        combos = [
            (visibility == "binding" and sot == "false", "binding requires source_of_truth: true"),
            (visibility == "historical" and sot == "true", "historical requires source_of_truth: false"),
            (visibility == "development" and sot == "true", "development requires source_of_truth: false"),
            (visibility == "binding" and status == "deprecated", "binding cannot have status: deprecated"),
            (
                visibility == "binding" and status in ("draft", "in-progress"),
                f"binding cannot have status: {status}",
            ),
        ]
        for bad, msg in combos:
            if bad:
                add(
                    ln("knowledge_visibility"), "VS002", "error",
                    f"invalid combination — {msg}. Resolve by correcting either the visibility "
                    "field or the workflow state; do not guess.",
                )

    # -- feedback notes (spec--system--feedback-channel.md) -----------------
    if doc_type == "feedback":
        for field in FEEDBACK_REQUIRED:
            if field not in values:
                add(2, "FB001", "error", f"feedback note is missing required field {field!r}")
        kind = values.get("kind")
        if isinstance(kind, str) and kind not in FEEDBACK_KINDS:
            add(ln("kind"), "FB002", "error", f"kind {kind!r} must be one of {', '.join(sorted(FEEDBACK_KINDS))}")
        for field in ("touches", "delivered"):
            if field in values and not isinstance(values[field], list):
                add(ln(field), "FB005", "error", f"{field} must be a list: [a, b] or '- item' lines")
        body = text[m.end():]
        for heading in FEEDBACK_SECTIONS:
            if not re.search(rf"(?m)^{re.escape(heading)}\s*$", body):
                add(2, "FB003", "error", f"feedback note lacks the fixed section {heading!r}")
    else:
        for key in sorted(FEEDBACK_FIELDS & set(values)):
            add(ln(key), "FB004", "error", f"field {key!r} is registered for type: feedback only")

    # -- filename ----------------------------------------------------------
    fname = path.name
    if not NAME_RE.match(fname):
        add(
            1, "NM001", "error",
            "filename does not match <type>--<scope>--<name>.md "
            "(optionally --<YYYY-MM-DD>[--<id8>] for generated documents)",
        )
    elif isinstance(doc_type, str):
        prefix = fname.split("--", 1)[0]
        if prefix != doc_type and PREFIX_EXCEPTIONS.get(prefix) != doc_type:
            add(
                1, "NM003", "error",
                f"filename prefix {prefix!r} disagrees with type {doc_type!r} — "
                "rename the file, correct the type, or register the prefix as an exception",
            )

    # -- relative links ----------------------------------------------------
    if check_links:
        body_offset = text[: m.end()].count("\n")
        for lm in LINK_RE.finditer(text):
            target = lm.group(1).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if target in LINK_PLACEHOLDERS:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                line = text[: lm.start()].count("\n") + 1
                add(max(line, body_offset), "LK001", "error", f"broken relative link -> {target}")

    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def collect(targets: list[str], root: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for t in targets:
        p = pathlib.Path(t)
        if not p.is_absolute():
            p = root / p
        if p.is_file() and p.suffix == ".md":
            files.append(p)
        elif p.is_dir():
            files += [f for f in sorted(p.rglob("*.md")) if ".obsidian" not in f.parts]
    return sorted(set(files))


# --------------------------------------------------------------------------
# Self-test — every rule must be proven to fire, and a good document must pass.
# --------------------------------------------------------------------------

GOOD = """---
type: spec
scope: system
status: approved
created: 2026-01-01
updated: 2026-01-02
source_of_truth: true
knowledge_visibility: binding
tags: [a, b]
---

# Fine
"""

FEEDBACK_NOTE = """---
type: feedback
scope: nexus
status: draft
created: 2026-01-01
updated: 2026-01-02
source_of_truth: false
knowledge_visibility: development
kind: bug
nexus_version: 1.0.0
host: liquid-nexus
touches: [.claude/hooks/nexus-exit-gate.py]
delivered: []
tags: [feedback, nexus]
---

# Exit gate blocks a compliant closure

## What happened

The gate denied a valid block.

## What is proposed

Relax the regex.

## Attachment

none
"""

CASES: list[tuple[str, str, str, str]] = [
    # (expected code, directory, filename, content)
    ("FM001", "specs", "spec--system--x.md", "# no frontmatter\n"),
    ("FM002", "specs", "spec--system--x.md", GOOD.replace("tags: [a, b]", "tags:\n* a\n* b")),
    ("FM003", "specs", "spec--system--x.md", GOOD.replace("scope: system", "scope: system\nscope: other")),
    ("FM004", "specs", "spec--system--x.md", GOOD.replace("scope: system\n", "")),
    ("FM005", "specs", "spec--system--x.md", GOOD.replace("tags: [a, b]", "bogus: 1\ntags: [a, b]")),
    ("FM006", "specs", "spec--system--x.md", GOOD.replace("type: spec", "type: memo")),
    ("FM007", "specs", "spec--system--x.md", GOOD.replace("status: approved", "status: accepted")),
    ("FM008", "specs", "spec--system--x.md", GOOD.replace("created: 2026-01-01", "created: 01/01/2026")),
    ("FM008", "specs", "spec--system--x.md", GOOD.replace("updated: 2026-01-02", "updated: 2025-12-31")),
    ("FM009", "specs", "spec--system--x.md", GOOD.replace("source_of_truth: true", "source_of_truth: yes")),
    ("FM010", "specs", "spec--system--x.md", GOOD.replace("tags: [a, b]", "tags: notalist")),
    ("FM100", "specs", "spec--system--x.md", GOOD.replace("knowledge_visibility: binding\n", "")),
    ("VS001", "specs", "spec--system--x.md", GOOD.replace("binding", "public")),
    ("VS002", "specs", "spec--system--x.md", GOOD.replace("source_of_truth: true", "source_of_truth: false")),
    ("VS002", "specs", "spec--system--x.md", GOOD.replace("status: approved", "status: draft")),
    ("NM001", "specs", "Spec_System_X.md", GOOD),
    ("NM002", "plans", "spec--system--x.md", GOOD),
    ("NM003", "specs", "plan--system--x.md", GOOD),
    ("LK001", "specs", "spec--system--x.md", GOOD + "\n[gone](./nowhere.md)\n"),
    ("FB001", "feedback", "feedback--nexus--x.md", FEEDBACK_NOTE.replace("host: liquid-nexus\n", "")),
    ("FB002", "feedback", "feedback--nexus--x.md", FEEDBACK_NOTE.replace("kind: bug", "kind: rant")),
    ("FB003", "feedback", "feedback--nexus--x.md", FEEDBACK_NOTE.replace("## Attachment", "## Patch")),
    ("FB004", "specs", "spec--system--x.md", GOOD.replace("tags: [a, b]", "tags: [a, b]\nkind: bug")),
    ("FB005", "feedback", "feedback--nexus--x.md", FEEDBACK_NOTE.replace("touches: [.claude/hooks/nexus-exit-gate.py]", "touches: one-file")),
]

# Shapes that MUST validate clean.
CLEAN: list[tuple[str, str, str]] = [
    ("specs", "spec--system--x.md", GOOD),
    # unindented block sequence is valid YAML
    ("specs", "spec--system--x.md", GOOD.replace("tags: [a, b]", "tags:\n- a\n- b")),
    # registered prefix exceptions
    ("decisions", "adr--system--x.md", GOOD.replace("type: spec", "type: decision")),
    ("sessions", "summary--theme--2026-01-02.md",
     GOOD.replace("type: spec", "type: session")
         .replace("knowledge_visibility: binding", "knowledge_visibility: historical")
         .replace("source_of_truth: true", "source_of_truth: false")
         .replace("status: approved", "status: deprecated")),
    # generated session archive: 4 segments + ISO timestamps
    ("sessions", "session--theme--2026-01-02--deadbeef.md",
     GOOD.replace("type: spec", "type: session")
         .replace("created: 2026-01-01", "created: 2026-01-01T10:00:00")
         .replace("updated: 2026-01-02", "updated: 2026-01-02T11:30:00")
         .replace("knowledge_visibility: binding", "knowledge_visibility: historical")
         .replace("source_of_truth: true", "source_of_truth: false")
         .replace("status: approved", "status: deprecated")
         .replace("tags: [a, b]", "tags: [a, b]\ntheme: theme\nsession_id: deadbeef-1111")),
    # a well-formed feedback note
    ("feedback", "feedback--nexus--exit-gate-regex.md", FEEDBACK_NOTE),
]


def selftest() -> int:
    import shutil
    import tempfile

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="nexus-validate-"))
    failures = 0
    try:
        for code, directory, fname, content in CASES:
            d = tmp / "knowledge" / directory
            d.mkdir(parents=True, exist_ok=True)
            f = d / fname
            f.write_text(content, encoding="utf-8")
            codes = {x.code for x in validate_document(f, tmp, check_links=True)}
            if code not in codes:
                print(f"FAIL expected {code} for {directory}/{fname}, got {sorted(codes) or 'nothing'}")
                failures += 1
            f.unlink()

        for directory, fname, content in CLEAN:
            d = tmp / "knowledge" / directory
            d.mkdir(parents=True, exist_ok=True)
            f = d / fname
            f.write_text(content, encoding="utf-8")
            found = [x.render() for x in validate_document(f, tmp, check_links=True)]
            if found:
                print(f"FAIL expected clean for {directory}/{fname}:")
                for line in found:
                    print("      " + line)
                failures += 1
            f.unlink()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(CASES) + len(CLEAN)
    print(f"selftest: {total - failures}/{total} passed")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Knowledge Vault documents.")
    ap.add_argument("--selftest", action="store_true", help="prove every rule fires, then exit")
    ap.add_argument("targets", nargs="*", help="files or directories (default: knowledge/)")
    ap.add_argument("--json", action="store_true", dest="as_json", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true", help="findings only, no summary line")
    ap.add_argument("--no-links", action="store_true", help="skip relative-link checking")
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = pathlib.Path(args.root).resolve()
    targets = args.targets or [str(root / "knowledge")]
    files = collect(targets, root)
    if not files:
        if not args.quiet:
            print("no markdown documents found", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for f in files:
        findings += validate_document(f, root, check_links=not args.no_links)

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.as_json:
        print(json.dumps({
            "documents": len(files),
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [f.as_dict() for f in findings],
        }, indent=2, ensure_ascii=False))
    else:
        for f in sorted(findings, key=lambda x: (x.level != "error", x.path, x.line)):
            print(f.render())
        if not args.quiet:
            print(
                f"\n{len(files)} document(s): {len(errors)} error(s), {len(warnings)} warning(s)"
            )

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
