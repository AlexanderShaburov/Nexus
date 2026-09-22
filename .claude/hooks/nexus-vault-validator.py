#!/usr/bin/env python3
"""Nexus: PostToolUse hook — advisory Knowledge Vault validation.

Runs after a write to a document under knowledge/ and reports contract
violations while the edit is still in the agent's working context. It is
**advisory**: PostToolUse cannot undo the write, and this hook never blocks.
The write has already happened; the point is to surface the problem
immediately rather than at the next audit.

All rules live in tools/validate-vault.py — the CLI is the single source of
truth, this file is a thin event adapter. Never auto-corrects: per
spec--system--knowledge-visibility.md, resolution is a judgement call.

Silent when the document is clean.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _nexus_common import project_dir, read_hook_input  # noqa: E402

WATCHED_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def load_validator():
    path = project_dir() / "tools" / "validate-vault.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("nexus_vault_validator", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    inp = read_hook_input()
    if (inp.get("tool_name") or "") not in WATCHED_TOOLS:
        return 0

    file_path = (inp.get("tool_input") or {}).get("file_path") or ""
    if not file_path.endswith(".md"):
        return 0

    root = project_dir().resolve()
    try:
        target = pathlib.Path(file_path).resolve()
        rel = target.relative_to(root)
    except (OSError, ValueError):
        return 0
    if rel.parts[:1] != ("knowledge",) or not target.is_file():
        return 0

    validator = load_validator()
    if validator is None:
        return 0

    try:
        findings = validator.validate_document(target, root, check_links=True)
    except Exception:
        # Advisory only: a validator bug must never disrupt the session.
        return 0
    if not findings:
        return 0

    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    lines = [
        "=== NEXUS VAULT VALIDATION (advisory) ===",
        "",
        f"{rel.as_posix()} — {len(errors)} error(s), {len(warnings)} warning(s):",
        "",
    ]
    lines += [f"  {f.level.upper()} [{f.code}] line {f.line}: {f.message}" for f in findings]
    lines += [
        "",
        "Contract: knowledge/specs/spec--system--document-frontmatter.md",
        "Re-check with: python3 tools/validate-vault.py " + rel.as_posix(),
    ]
    if errors:
        lines += ["", "Fix the errors before ending this turn, or say why you are leaving them."]

    sys.stdout.write(json.dumps({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n".join(lines),
        },
    }) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
