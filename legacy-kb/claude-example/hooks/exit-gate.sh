#!/usr/bin/env bash
# exit-gate.sh — Exit Gate enforcer
# Hook: Stop
# Spec: spec--system--exit-gate.md
#
# Enforcement:
#   * Reads the session transcript (JSONL) pointed to by `transcript_path`
#     from the Stop hook JSON on stdin.
#   * Extracts the text of the most recent assistant message.
#   * Requires a "Closure Block:" at the tail of the message with all four
#     fields: code changed, KB changed, session log written, writeback
#     evaluation performed — each "yes" or "no".
#   * Enforces dependency rules 1, 2, 3 from the spec.
#   * On violation: exit 2 and write a descriptive reason to stderr.
#     Claude Code feeds stderr back to the agent and blocks stop, forcing
#     a corrective continuation.
#   * Respects `stop_hook_active` to prevent infinite recursion.
#
# Fail-open philosophy: malformed stdin / unreadable transcript / non-JSON
# lines are NOT enforcement-blocking (exit 0). Enforcement blocks only when
# the assistant text is readable AND the Closure Block is missing/invalid.

set -uo pipefail

INPUT="$(cat)"
export EXIT_GATE_INPUT="$INPUT"

python3 - <<'PY'
import os, json, re, sys

raw = os.environ.get("EXIT_GATE_INPUT", "")
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)  # fail-open: cannot parse hook input

# Recursion guard: if a previous Stop hook already ran and blocked, do not
# block again on the follow-up attempt that is specifically trying to close.
if data.get("stop_hook_active") is True:
    sys.exit(0)

transcript_path = data.get("transcript_path") or ""
if not transcript_path or not os.path.isfile(transcript_path):
    sys.exit(0)  # fail-open: cannot read transcript

# Walk transcript; remember the LAST assistant text-only message.
last_text = ""
try:
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if not isinstance(rec, dict):
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                # some transcript variants embed role at top level
                if rec.get("role") == "assistant":
                    msg = rec
                else:
                    continue
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            buf = []
            if isinstance(content, str):
                buf.append(content)
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        t = c.get("text") or ""
                        if t:
                            buf.append(t)
            text = "\n".join(buf).strip()
            if text:
                last_text = text
except Exception:
    sys.exit(0)

text = last_text or ""

errs = []

# Locate the "Closure Block:" header line.
header = re.search(r"(?im)^[ \t]*Closure[ \t]+Block[ \t]*:[ \t]*$", text)
body = ""
block_end = None
if not header:
    errs.append(
        "Closure Block is missing. It MUST be the final element of the "
        "response (per spec--system--exit-gate.md — Placement Rule)."
    )
else:
    # Walk lines after the header. The block is the run of bullet lines
    # ("- field: value") optionally separated by blank lines. The block
    # ends at the last consecutive bullet line.
    after = text[header.end():]
    lines = after.split("\n")
    # Compute cumulative character offsets so we can locate block_end.
    offsets = []
    pos = header.end()
    for ln in lines:
        offsets.append(pos)
        pos += len(ln) + 1  # +1 for the \n we split on
    bullet_re = re.compile(r"^\s*-\s*\S")
    last_bullet_idx = -1
    body_lines = []
    for i, ln in enumerate(lines):
        if bullet_re.match(ln):
            last_bullet_idx = i
            body_lines.append(ln)
        elif ln.strip() == "" and last_bullet_idx >= 0:
            # allow blank lines only AFTER we've seen bullets and BEFORE
            # the next bullet — don't advance last_bullet_idx
            continue
        else:
            # non-bullet, non-blank: either pre-block junk (skip) or
            # post-block content (break once bullets started)
            if last_bullet_idx >= 0:
                break
    body = "\n".join(body_lines)
    if last_bullet_idx >= 0:
        # block_end = offset of last bullet line + its length
        block_end = offsets[last_bullet_idx] + len(lines[last_bullet_idx])

# Extract field values.
field_patterns = {
    "code changed":                 r"^\s*-\s*code\s+changed\s*:\s*(yes|no)\b",
    "KB changed":                   r"^\s*-\s*KB\s+changed\s*:\s*(yes|no)\b",
    "session log written":          r"^\s*-\s*session\s+log\s+written\s*:\s*(yes|no)\b",
    "writeback evaluation performed": r"^\s*-\s*writeback\s+evaluation\s+performed\s*:\s*(yes|no)\b",
}
values = {}
if body:
    for name, pat in field_patterns.items():
        fm = re.search(pat, body, re.I | re.M)
        if not fm:
            errs.append(f"Closure Block missing required field: '{name}'.")
        else:
            values[name] = fm.group(1).lower()

# Dependency rules (only meaningful when fields are present).
if values.get("code changed") == "yes":
    if values.get("writeback evaluation performed") != "yes":
        errs.append(
            "Rule 1 violated: code changed=yes REQUIRES "
            "writeback evaluation performed=yes."
        )

if values.get("KB changed") == "no":
    # Rule 3: need explicit justification somewhere in the response.
    justification_markers = [
        r"not\s+knowledge[-\s]bearing",
        r"\bbecause\b",
        r"\bjustification\b",
        r"\brationale\b",
        r"no\s+writeback\b",
        r"\bwhy\b",
    ]
    if not any(re.search(p, text, re.I) for p in justification_markers):
        errs.append(
            "Rule 3 violated: KB changed=no REQUIRES explicit justification "
            "(why the change is not knowledge-bearing and why KB update is "
            "not required). Add a short rationale before the Closure Block."
        )

# Reject placement violations: any non-whitespace content AFTER the Closure Block.
if block_end is not None:
    tail = text[block_end:].strip()
    if tail:
        errs.append(
            "Placement violation: content appears AFTER the Closure Block. "
            "Per the spec, no content is allowed after the Closure Block."
        )

if errs:
    sys.stderr.write(
        "EXIT GATE FAILED — response is INVALID per spec--system--exit-gate.md\n\n"
    )
    for e in errs:
        sys.stderr.write(f"  * {e}\n")
    sys.stderr.write(
        "\nRequired Closure Block format (final element, no content after):\n\n"
        "    Closure Block:\n"
        "    - code changed: yes|no\n"
        "    - KB changed: yes|no\n"
        "    - session log written: yes|no\n"
        "    - writeback evaluation performed: yes|no\n\n"
        "Dependency rules:\n"
        "  * code changed=yes  -> writeback evaluation performed MUST be yes\n"
        "  * writeback=yes AND knowledge-bearing -> KB changed MUST be yes\n"
        "  * KB changed=no     -> explicit justification REQUIRED\n\n"
        "Do not stop. Emit the missing/corrected Closure Block and any "
        "required justification, then stop.\n"
    )
    sys.exit(2)

sys.exit(0)
PY
