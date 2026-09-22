#!/usr/bin/env python3
"""Nexus: Context Decision claim.

The first mutating tool call of a turn may be this script instead of a
"### Context Decision" text block. `nexus-tool-gate.py` recognises the call
from its command line (PreToolUse `tool_input.command`) and records the
decision in `.nexus/state.json`; the text block remains the fallback.

This script decides nothing and writes nothing. It validates its arguments
with the same parser the gate uses and prints the decision to the terminal,
so the decision stays visible on screen and in the transcript as a tool call.

Usage:
    tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason "<why>"
    tools/nexus-decide.py --kb NO --reason "<why the KB is not needed and what risk is accepted>"

Exit codes: 0 = valid claim printed, 2 = malformed claim.

Contract: knowledge/specs/spec--system--context-decision-gate.md
"""

from __future__ import annotations

import os
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
os.environ.setdefault("CLAUDE_PROJECT_DIR", str(_ROOT))
sys.path.insert(0, str(_ROOT / ".claude" / "hooks"))

from _nexus_common import DECISION_CLAIM_USAGE, parse_decision_claim_args  # noqa: E402


def main(argv: list[str]) -> int:
    claim, err = parse_decision_claim_args(argv)
    if claim is None:
        sys.stderr.write(f"nexus-decide: {err}\n\n{DECISION_CLAIM_USAGE}\n")
        return 2
    lines = ["### Context Decision", f"KB consult required: {claim['kb'].upper()}"]
    if claim["reads"]:
        lines.append("Reads:")
        lines += [f"- {p}" for p in claim["reads"]]
    lines.append(f"Reasoning: {claim['reason']}")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
