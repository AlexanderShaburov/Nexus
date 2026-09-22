# Nexus Hooks — Implementation Report & Validation Plan

Referenced by `CLAUDE.md` → *"When editing hooks: after changes, run the validation plan in `docs/nexus-implementation-report.md` before claiming the hooks work."*

This document is the acceptance procedure for `.claude/hooks/`. Run it after **any** change to a hook, to `_nexus_common.py`, or to the hook registration in `.claude/settings.json`.

---

## 1. What is implemented

| Hook | Event(s) | Role | Can block? |
|---|---|---|---|
| `nexus-bootstrap.py` | `SessionStart`, `PreCompact` | Resets `.nexus/state.json`, injects the Mandatory Startup Reading Set | no (injects context) |
| `nexus-prompt-gate.py` | `UserPromptSubmit` | Increments turn index, resets the per-turn decision flag, injects the turn contract | no (injects context) |
| `nexus-tool-gate.py` | `PreToolUse` | Bootstrap gate + Context Decision gate | **yes** (`permissionDecision: deny`) |
| `nexus-exit-gate.py` | `Stop` | Closure Block validation | **yes** (`decision: block`) |
| `nexus-session-writer.py` | `Stop` | Transcript archival to `knowledge/sessions/` | no (silent by design) |
| `nexus-vault-validator.py` | `PostToolUse` | Advisory frontmatter validation of the document just written | no (advisory only) |
| `_nexus_common.py` | — | Shared state I/O, transcript parsing, regexes | — |
| `tools/validate-vault.py` | — | Vault rule set + CLI; the validator hook is a thin adapter over it | — |
| `tools/nexus-decide.py` | — | Context Decision **claim** (Form A): validates and prints the decision; the tool gate recognises the call from `tool_input.command` via the shared parser in `_nexus_common.py` | — |

Contract sources of truth: `knowledge/specs/spec--system--session-bootstrap.md`, `spec--system--context-decision-gate.md`, `spec--system--exit-gate.md`. Structural description: `knowledge/architecture/architecture--system--overall-structure.md`.

---

## 2. Static checks

Run from the repo root. All must pass before any behavioral testing.

```bash
# S1 — every hook compiles
for f in .claude/hooks/*.py; do python3 -m py_compile "$f" && echo "OK $f" || echo "FAIL $f"; done

# S2 — executable bit + shebang on every entry-point hook
for f in .claude/hooks/nexus-*.py; do
  [ -x "$f" ] || echo "NOT EXECUTABLE: $f"
  head -1 "$f" | grep -q '^#!/usr/bin/env python3' || echo "BAD SHEBANG: $f"
done

# S3 — settings.json is valid JSON and every referenced hook file exists
python3 - <<'PY'
import json, os, re
cfg = json.load(open('.claude/settings.json'))
missing = []
for event, groups in cfg['hooks'].items():
    for g in groups:
        for h in g['hooks']:
            p = h['command'].replace('$CLAUDE_PROJECT_DIR/', '')
            print(f"{event:18} -> {p}")
            if not os.path.isfile(p):
                missing.append(p)
print("MISSING:", missing or "none")
PY

# S4 — no hook writes to stdout unless it intends to (session-writer must stay silent)
echo '{}' | .claude/hooks/nexus-session-writer.py | wc -c   # expect 0

# S5 — the vault rule set still catches everything it claims to
python3 tools/validate-vault.py --selftest

# S6 — the vault itself is clean
python3 tools/validate-vault.py

# S8 — the ownership manifest matches the tree, and the updater's rules still hold
python3 tools/nexus-update.py manifest verify
python3 tools/nexus-update.py --selftest
```

Expected: S1 all `OK`; S2 no output; S3 `MISSING: none` and six registrations (`SessionStart`, `PreCompact`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`×2); S4 prints `0`; S5 all fixtures pass; S6 `0 error(s)` and exit 0; S8 `in sync with the tree` and `all checks passed`.

S8 fails whenever a hook, a `tools/*.py` file, a binding system document or an H2 heading of `CLAUDE.md` is added, removed or renamed without regenerating the manifest: run `python3 tools/nexus-update.py manifest generate` and commit `nexus.manifest.json` with the change. Bump `nexus.version` on release, then regenerate.

When a rule changes in `tools/validate-vault.py`, add the case that motivated the change to its `CASES` (must fire) or `CLEAN` (must not) list before declaring the fix good.

---

## 3. Regex fixtures

The two gate regexes in `_nexus_common.py` are the highest-risk surface: a false negative blocks a compliant agent, a false positive lets a violation through. Test them directly.

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, '.claude/hooks')
from _nexus_common import find_decision_gate, find_closure_block, find_bootstrap_confirmation

MUST_MATCH_DECISION = [
    "### Context Decision\nKB consult required: YES\nReasoning: x",
    "**Context Decision:**\nKB consult required: NO\nReasoning: x",
    "## Context Decision Gate\nSome preamble line\nKB consult required: yes",
]
MUST_NOT_MATCH_DECISION = [
    "I considered the context decision and decided no.",
    "### Context Decision\nReasoning: I skipped the KB.",
]
MUST_MATCH_CLOSURE = [
    "Closure Block:\n- code changed: no\n- KB changed: yes\n"
    "- session log written: yes\n- writeback evaluation performed: yes",
    "Closure Block\n* code changed: YES\n* KB changed: NO\n"
    "* session log written: NO\n* writeback evaluation performed: YES",
]
MUST_NOT_MATCH_CLOSURE = [
    "Closure Block:\n- code changed: no\n- KB changed: yes",          # truncated
    "- code changed: no\n- KB changed: no\n"                           # no header
    "- session log written: no\n- writeback evaluation performed: no",
]
fail = 0
for s in MUST_MATCH_DECISION:
    if find_decision_gate(s) is None: print("MISS decision:", s[:40]); fail += 1
for s in MUST_NOT_MATCH_DECISION:
    if find_decision_gate(s) is not None: print("FALSE POS decision:", s[:40]); fail += 1
for s in MUST_MATCH_CLOSURE:
    if not find_closure_block(s): print("MISS closure:", s[:40]); fail += 1
for s in MUST_NOT_MATCH_CLOSURE:
    if find_closure_block(s): print("FALSE POS closure:", s[:40]); fail += 1
assert find_bootstrap_confirmation(
    "Session Bootstrap Completed\nLoaded:\n- x\nOperational Mode: Knowledge-Driven Mode: ACTIVE")
print("FAILURES:", fail)
PY
```

Expected: `FAILURES: 0`.

When you change a regex, **add the case that motivated the change to the list above** before declaring the fix good.

### S7 — claim parser fixtures

The claim form exists because Claude Code 2.1.278 (observed 2026-09-22 with Fable 5.1) persists mid-turn assistant text as a paraphrased `thinking` block, so the regex above never sees the block. The parser is the second gate surface; a false positive lets an arbitrary command through as a "decision".

```bash
python3 - <<'PY'
import sys, os; os.environ.setdefault('CLAUDE_PROJECT_DIR', os.getcwd()); sys.path.insert(0, '.claude/hooks')
from _nexus_common import parse_decision_claim
SPEC = "knowledge/specs/spec--system--exit-gate.md"
CASES = [  # (command, expected: claim | error | none)
    (f'python3 tools/nexus-decide.py --kb YES --reads {SPEC} --reason "Changing the exit gate contract"', 'claim'),
    ('cd /any/where && python3 tools/nexus-decide.py --kb no --reason "Hook-only edit, risk: missing a spec"', 'claim'),
    ('./tools/nexus-decide.py --kb NO --reason "a; b && c are fine inside quotes"', 'claim'),
    ('ls -la', 'none'),
    ('python3 tools/nexus-decide.py --kb NO --reason "short"', 'error'),
    ('python3 tools/nexus-decide.py --kb MAYBE --reason "long enough reason here"', 'error'),
    ('python3 tools/nexus-decide.py --kb YES --reason "long enough reason here"', 'error'),          # YES needs --reads
    ('python3 tools/nexus-decide.py --kb YES --reads knowledge/nope.md --reason "long enough reason"', 'error'),
    ('python3 tools/nexus-decide.py --kb NO --reason "long enough reason here" && rm -rf x', 'error'),
    ('python3 tools/nexus-decide.py --kb NO --reason "long enough reason here"; echo hi', 'error'),
    ('python3 tools/nexus-decide.py --kb NO --reason "$(rm -rf x) long enough"', 'error'),
    ('echo x && python3 tools/nexus-decide.py --kb NO --reason "long enough reason here"', 'error'),
    ('python3 /tmp/nexus-decide.py --kb NO --reason "long enough reason here"', 'error'),
    ('python3 tools/nexus-decide.py --kb NO --reason "long enough reason here" extra', 'error'),
]
fail = 0
for cmd, want in CASES:
    claim, err = parse_decision_claim(cmd)
    got = 'claim' if claim else ('error' if err else 'none')
    if got != want: print("FAIL", want, "->", got, "|", cmd, "|", err); fail += 1
print("FAILURES:", fail)
PY
```

Expected: `FAILURES: 0`. When the recognition rules change, mirror the change in `spec--system--context-decision-gate.md` §Decision Forms and add the motivating case here.

---

## 4. Behavioral checks (live session)

These cannot be scripted; they require a real Claude Code session. Perform them in order in a scratch session.

| # | Action | Expected observable result |
|---|---|---|
| B1 | Start a fresh session; before reading anything, attempt `Bash(ls)` | Denied with `NEXUS BOOTSTRAP PENDING` |
| B2 | Read the four Mandatory Startup files (incl. ≥1 invariant) | `.nexus/state.json` → `bootstrap.status: completed`, `read_ledger` has 3 entries, `invariant_read_count ≥ 1` |
| B3 | Attempt `Bash(ls)` with no Context Decision in the turn | Denied with `NEXUS DECISION GATE MISSING` |
| B4 | Emit a Context Decision block, then attempt `Bash(ls)` | Allowed; `state.json` → `turn.decision_gate_seen: true`, `turn.decision.via: "text"`. If denied, see the narration note below before calling it a regression |
| B4a | In a fresh turn, call `Bash(python3 tools/nexus-decide.py --kb NO --reason "<15+ chars>")` as the first mutating call | Allowed with `Context Decision claim accepted`; the block is printed to the terminal; `state.json` → `turn.decision.via: "claim"` |
| B4b | In the same turn, `Edit` or `Write` a file | Allowed without a second claim |
| B4c | In a fresh turn, call the claim with `--reason "x"` | Denied with `NEXUS DECISION CLAIM MALFORMED: --reason is too short` |
| B5 | End a response with no Closure Block | Stop blocked with `NEXUS EXIT GATE VIOLATION: Closure Block missing or malformed` |
| B6 | End with `code changed: yes` + `writeback evaluation performed: no` | Stop blocked with `Rule 1 violation` |
| B7 | End with `KB changed: no` and no justification line | Stop blocked with `Rule 3 violation` |
| B8 | Put prose after the Closure Block | Stop blocked with `Placement violation` |
| B9 | End with a valid Closure Block | Stop passes on the **first** attempt |
| B10 | After any Stop, inspect `knowledge/sessions/` | One `session--<theme>--<date>--<id8>.md`, containing prompts + assistant text, **no** tool calls or system-reminders |
| B11 | Change `.nexus/session-theme.txt`, trigger another Stop | The existing archive is **renamed**, not duplicated; `created:` preserved |
| B12 | Start a *second* session in the same repo and let it reach Stop | The first session's archive is **untouched**; a new file appears alongside it |
| B13 | Write a document under `knowledge/` with a deliberate frontmatter error | Advisory `NEXUS VAULT VALIDATION` context appears naming the rule code; the write is **not** blocked |
| B14 | Write a clean document under `knowledge/`, and separately a file outside it | No validation output in either case |

### The transcript race (track B4, B9 and B12 carefully)

`nexus-exit-gate.py` and `nexus-tool-gate.py` read the transcript **from disk**, but Claude Code persists assistant text blocks asynchronously. A hook can run before the block carrying the Closure Block (B9) or the Context Decision (B4) has been flushed, making the gate block a compliant response.

Mitigation in place: `read_transcript_current_turn()` takes an `until` predicate and re-reads up to 4 times at 80 ms. A compliant turn matches on the first read and pays nothing; only a genuine violation pays the full ~240 ms. Verify the budget after touching that function:

```bash
python3 - <<'PY'
import sys, time, json, tempfile, os
sys.path.insert(0, '.claude/hooks')
from _nexus_common import read_transcript_current_turn, find_closure_block
GOOD = ("Closure Block:\n- code changed: no\n- KB changed: no\n"
        "- session log written: yes\n- writeback evaluation performed: yes")
def mk(text):
    fd, p = tempfile.mkstemp(suffix='.jsonl'); os.close(fd)
    with open(p, 'w') as f:
        f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                "content": [{"type": "text", "text": text}]}}) + "\n")
    return p
for label, body, want in (("hit", GOOD, 0.01), ("miss", "nothing", 0.20)):
    p = mk(body); t0 = time.time()
    read_transcript_current_turn(p, until=find_closure_block)
    el = time.time() - t0
    print(f"{label:5} elapsed={el:.3f}s", "OK" if (el < want if label == 'hit' else el > want) else "UNEXPECTED")
    os.unlink(p)
PY
```

The race cannot be eliminated while the transcript is read from disk — only made unobservable. If a gate still blocks a response you believe was compliant, replay the regex against the persisted transcript to tell a **real** regression from a residual race:

```bash
python3 - <<'PY'
import json, os, sys, glob
sys.path.insert(0, '.claude/hooks')
from _nexus_common import CLOSURE_BLOCK_RE, _role_of, _content_of
T = max(glob.glob(os.path.expanduser(
    '~/.claude/projects/*Liquid-Nexus/*.jsonl')), key=os.path.getmtime)
msgs = [json.loads(l) for l in open(T) if l.strip()]
texts = []
for m in msgs:
    if _role_of(m) != 'assistant': continue
    c = _content_of(m)
    if isinstance(c, str): texts.append(c)
    elif isinstance(c, list):
        texts += [str(x.get('text','')) for x in c
                  if isinstance(x, dict) and x.get('type') == 'text']
print("closure match:", bool(CLOSURE_BLOCK_RE.search("\n".join(texts))))
PY
```

If this prints `True` but the gate blocked, the block was a **false positive from the race**, not a format error. If it prints `False`, the agent really did emit a malformed block.

### Transcript narration (why the claim form exists)

Distinct from the race: in some Claude Code builds (2.1.278 with Fable 5.1, 2026-09-22) assistant text written in the same message as a tool call is persisted as a `thinking` block containing a one-sentence paraphrase, and no `text` block is written at all. Retrying does not help because the text never arrives. Symptom: B4 denied on every attempt while B9 passes, and the persisted record for the message is `thinking` + `tool_use` only. The claim form (B4a) is the remedy; the text form stays for environments that persist text normally.

---

---

## 5. Sign-off checklist

Do not claim the hooks work until all of these are true:

- [ ] Section 2 static checks S1–S6 and S8 pass
- [ ] Section 3 fixtures report `FAILURES: 0`, including S7
- [ ] Section 4 rows B1–B14 observed (B9 assessed against the race note, B4 against the narration note)
- [ ] Any hook text that quotes a contract is mirrored in the corresponding spec under `knowledge/specs/`
- [ ] `knowledge/architecture/architecture--system--overall-structure.md` still describes the actual set of registered hooks, with `updated:` bumped
- [ ] `.nexus/state.json` is gitignored and no stray `.nexus/state*.json` is staged
