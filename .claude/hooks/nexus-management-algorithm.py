#!/usr/bin/env python3
"""Read-only UserPromptSubmit handler for the canonical management algorithm.

Delivered as two separately bounded parts to fit Claude Code's per-hook
10,000 character limit. Registered through the two launchers
nexus-algorithm-core.py and nexus-algorithm-reading.py, one hook entry each,
which is the unit the updater delivers to a host. Never writes Program
Counter or per-session gate state.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _nexus_common import emit_context, project_dir, read_hook_input  # noqa: E402

ALGORITHM = "knowledge/specs/spec--system--management-algorithm.md"
MAX_CHARS = 9800  # safety margin below Claude Code's 10,000-character limit
HEADINGS = (
    "## 1. Definitions",
    "## 2. The algorithm",
    "## 3. Reading the algorithm",
    "## 4. What this specification does not define",
)


def part_context(part: str) -> str:
    path = project_dir() / ALGORITHM
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return f"ALGORITHM UNAVAILABLE — {ALGORITHM}: {type(exc).__name__}: {exc}. Do not invent its contents."
    offsets = []
    for heading in HEADINGS:
        matches = list(re.finditer(r"(?m)^" + re.escape(heading) + r"(?:[ \t][^\n]*)?$", source))
        if len(matches) != 1:
            return f"ALGORITHM FORMAT ERROR — expected exactly one heading {heading!r} in {ALGORITHM}."
        offsets.append(matches[0].start())
    if offsets != sorted(offsets) or len(set(offsets)) != len(offsets):
        return "ALGORITHM FORMAT ERROR — §§1–4 are not in canonical order."
    if part == "core":
        text = source[offsets[0]:offsets[2]].rstrip()
        intro = (
            "=== NEXUS CANONICAL MANAGEMENT ALGORITHM — PART 1/2 ===\n"
            f"Source: {ALGORITHM}; verbatim §§1–2 (definitions, diagram).\n"
            "This is executable guidance to interpret with the saved Program Counter "
            "provided by the main UserPromptSubmit hook. Read PART 2/2 as well.\n\n"
        )
    elif part == "reading":
        text = source[offsets[2]:offsets[3]].rstrip()
        intro = (
            "=== NEXUS CANONICAL MANAGEMENT ALGORITHM — PART 2/2 ===\n"
            f"Source: {ALGORITHM}; verbatim §3 (reading and transition rules).\n"
            "Use together with PART 1/2 and the saved Program Counter. Both "
            "parts are delivered independently; ordering is not guaranteed.\n\n"
        )
    else:
        raise ValueError("invalid algorithm part")
    output = intro + text + "\n=== END NEXUS ALGORITHM PART ==="
    if len(output) > MAX_CHARS:
        return (
            f"ALGORITHM PART TOO LARGE — {part}: {len(output)} characters, "
            f"safe limit {MAX_CHARS}. Fix chunking before claiming the algorithm "
            "was delivered. Do not rely on a truncated preview."
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", required=True, choices=("core", "reading"))
    args = parser.parse_args()
    read_hook_input()  # consume the hook event payload; no shared state mutation
    emit_context("UserPromptSubmit", part_context(args.part))
    return 0


if __name__ == "__main__":
    sys.exit(main())
