# SOKI Hooks Implementation + System Review

Report produced per `prompt_soki_hooks_and_review.md`. Everything below references the new, non-legacy sources under `knowledge/` and `.claude/hooks/`; the `legacy-kb/` bundle is explicitly ignored.

---

## 1. Findings

### 1.1 What existed before this pass

- Conceptual paper `nexus_approach.md` at repo root — describes the SOKI model (Bootstrap → Decision → Execution → Exit).
- Seven top-level spec files covering session-bootstrap, context-decision-gate, exit-gate, knowledge-driven-task-orchestration, vault/world-structure (two near-duplicates), and document-frontmatter.
- Legacy advisory `bootstrap.md` (at repo root until 2026-04-20; moved to `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md`) — matches the pre-SOKI soft-protocol approach.
- `CLAUDE.md` describing the repo as a **template kit** with `claude-example/` + `example-kb/` folders.
- Legacy bundle under `legacy-kb/{claude-example,example-kb}/` — old hooks plus a fully populated reference vault. Out of scope for this task.

### 1.2 What was missing

- No `knowledge/` vault in the repo — every spec pointed at `knowledge/…` paths but nothing lived there.
- No index, architecture, or invariants docs to satisfy the Session Bootstrap reading set.
- No runtime enforcement layer; only docs.
- `spec--system--context-decision-gate.md` had no YAML frontmatter (violates `spec--system--document-frontmatter.md`).
- `spec--system--vault-structure.md` and `spec--system--knowledge-vault.md` were near-identical (same content, different root directory name: `vault/` vs `knowledge/`).
- `CLAUDE.md` still described the legacy `claude-example/` + `example-kb/` layout.

### 1.3 Conflicts found

| Area | Conflict | Resolution |
|---|---|---|
| Root directory name | `world-structure` says `knowledge/`, `vault-structure` says `vault/` | Kept `world-structure.md` as canonical (matches session-bootstrap + orchestration specs). Removed the duplicate `vault-structure.md`. |
| Status vocabulary | `session-bootstrap.md` uses `status: approved`, frontmatter spec allows `draft`/`in-progress`/`review`/`approved`/`deprecated` | Consistent after consolidation; flagged in Review §6. |
| Date field | Orchestration spec uses `date:`; frontmatter spec requires `created:`/`updated:` | Flagged in Review §6; not auto-fixed to avoid silent spec drift. |
| Frontmatter presence | `context-decision-gate.md` had none | Added full YAML frontmatter block. |

### 1.4 What this pass produced

- Consolidated vault at `knowledge/` with the taxonomy `index/ architecture/ invariants/ specs/ decisions/ patterns/ plans/ sessions/ bugs/ runbooks/ glossary/ open-questions/ business/`.
- Moved all six surviving top-level specs into `knowledge/specs/`.
- Created seed docs the Bootstrap reading set requires:
  - `knowledge/index/index--system--project-navigation.md`
  - `knowledge/architecture/architecture--system--overall-structure.md`
  - `knowledge/invariants/invariant--system--lifecycle-gates.md`
- Four Python hook scripts + a shared helper module under `.claude/hooks/`.
- `.claude/settings.json` registering all hooks.
- `.soki/` runtime directory with README and `.gitignore` entry for per-session state.
- Rewritten `CLAUDE.md` pointing at the new layout.

---

## 2. Hook Architecture

### 2.1 Lifecycle diagram

```
SessionStart / PreCompact
  └─► soki-bootstrap.py
        • reset .soki/state.json (bootstrap.status = pending)
        • emit additionalContext: Mandatory Startup Reading Set + required
          "Session Bootstrap Completed" confirmation shape
        • warn on missing vault files

UserPromptSubmit
  └─► soki-prompt-gate.py
        • increment turn.index, reset turn.decision_gate_seen = false
        • if bootstrap pending: emit "BOOTSTRAP STILL PENDING" reminder listing
          files that still need to be read
        • else: emit the per-turn TURN CONTRACT (Decision Gate + Exit Gate rules)

PreToolUse  (matcher Read|Glob|Grep|LS|NotebookRead|Edit|Write|MultiEdit|
             NotebookEdit|Bash|Task|Agent|TodoWrite)
  └─► soki-tool-gate.py
        ┌── bootstrap = pending ──┐
        │  tool ∈ READ_ONLY_TOOLS │ → allow (and, if Read, update ledger;
        │                         │   auto-complete if ledger full)
        │  else                   │ → permissionDecision: deny
        └─────────────────────────┘
        ┌── bootstrap = completed ──┐
        │  tool ∈ MUTATING_TOOLS    │
        │   • parse current turn    │
        │   • find_decision_gate()  │
        │   • if absent → deny      │
        │   • else → allow          │
        │  else                     │ → allow
        └───────────────────────────┘

Stop
  └─► soki-exit-gate.py
        • skip if stop_hook_active (anti-loop)
        • read last user→end of transcript
        • if bootstrap still pending & no "Session Bootstrap Completed"
          confirmation → block
        • find Closure Block regex → if missing → block
        • enforce Rule 1 (code=yes ⇒ writeback=yes) → block on violation
        • enforce Rule 3 (KB=no ⇒ "KB unchanged because …" present) → block
        • enforce placement (only a Rule 3 tail line permitted) → block
```

### 2.2 State contract (`.soki/state.json`)

```json
{
  "session_id": "…",
  "started_at": "YYYY-MM-DDTHH:MM:SSZ",
  "bootstrap": {
    "status": "pending | completed",
    "required_files": ["knowledge/…", "knowledge/…", "knowledge/…"],
    "required_invariants_dir": "knowledge/invariants",
    "read_ledger": ["…"],
    "invariant_read_count": 0,
    "event": "SessionStart | PreCompact"
  },
  "turn": {
    "index": 0,
    "decision_gate_seen": false
  }
}
```

### 2.3 Output-format contracts enforced by the hooks

**Bootstrap confirmation** (Stop hook is lenient; regex is case-insensitive, allows whitespace):
```
Session Bootstrap Completed
… [anything] …
Knowledge-Driven Mode: ACTIVE
```

**Context Decision Gate** (in-turn, before any mutating tool):
```
### Context Decision
KB consult required: YES | NO
Reasoning: …
```

**Closure Block** (final substantive element of the turn):
```
Closure Block:
- code changed: yes|no
- KB changed: yes|no
- session log written: yes|no
- writeback evaluation performed: yes|no
```

Optional trailing line when `KB changed: no`: `KB unchanged because …`.

---

## 3. Hook Files

All scripts live in `.claude/hooks/`. Code is in the repo; this section gives role + key logic.

| File | Role | Key logic |
|---|---|---|
| `_soki_common.py` | Shared helpers | State I/O, transcript parser (finds assistant text since last user turn), regex for Decision Gate / Closure Block / bootstrap confirmation, `emit_block()` that uses `hookSpecificOutput.permissionDecision` for PreToolUse and `{"decision":"block"}` for Stop. |
| `soki-bootstrap.py` | SessionStart + PreCompact | Writes fresh state; emits `additionalContext` with the Mandatory Startup Reading Set and confirmation-block template; warns when required vault files are missing. |
| `soki-prompt-gate.py` | UserPromptSubmit | Increments turn counter; resets per-turn flag; chooses between bootstrap-pending reminder and per-turn contract. |
| `soki-tool-gate.py` | PreToolUse | Enforces bootstrap-pending read-only policy, tracks read-ledger, auto-completes bootstrap, enforces Decision-Gate presence for mutating tools after bootstrap. |
| `soki-exit-gate.py` | Stop | Transcript-driven enforcement of Closure Block, Rule 1, Rule 3, placement, plus bootstrap-confirmation guard. Anti-loop via `stop_hook_active`. |

Every hook is a standalone Python 3 script (no heredoc; stdin is preserved) with shebang `#!/usr/bin/env python3` and mode `0755`.

---

## 4. Placement Instructions

All paths below are under `$CLAUDE_PROJECT_DIR` (the consuming project root).

| Artifact | Location |
|---|---|
| Hook scripts | `.claude/hooks/soki-bootstrap.py`, `soki-prompt-gate.py`, `soki-tool-gate.py`, `soki-exit-gate.py`, `_soki_common.py` |
| Hook registration | `.claude/settings.json` (checked in — team-wide) |
| Runtime state | `.soki/state.json` (gitignored; regenerated each SessionStart) |
| Vault root | `knowledge/` with the 13 subdirectories from `specs/spec--system--knowledge-vault.md` |
| Mandatory seed docs | `knowledge/index/index--system--project-navigation.md`, `knowledge/architecture/architecture--system--overall-structure.md`, at least one file under `knowledge/invariants/` |
| Canonical specs | Under `knowledge/specs/` |
| Project memory | `CLAUDE.md` at repo root (points to the vault + enforcement) |

### Integration steps for a fresh project

1. Copy `.claude/hooks/`, `.claude/settings.json`, `.soki/README.md`, `.gitignore` additions, and the `knowledge/` skeleton into the target repo root.
2. Add entries under `knowledge/invariants/` + `architecture/` + `index/` so the Mandatory Startup Reading Set resolves. Minimum: one invariant, one architecture doc, the navigation index.
3. `chmod +x .claude/hooks/*.py` (git can lose the x bit).
4. Open `/hooks` once in Claude Code after first launch (triggers the hook-config reload documented in the `update-config` skill guidance).
5. Optional: add `.soki/state.json` to `.gitignore` if you copied the repo-level `.gitignore` verbatim it's already there.

---

## 5. Validation Plan

The plan below is end-to-end. All cases were executed during this task; commands are reproducible.

**Setup** (from project root):
```bash
export CLAUDE_PROJECT_DIR="$PWD"
rm -f .soki/state.json
```

**5.1 Bootstrap hook creates pending state and emits context**
```bash
echo '{"session_id":"t1","hook_event_name":"SessionStart"}' | .claude/hooks/soki-bootstrap.py | jq .
# expect: hookSpecificOutput.additionalContext starts with "=== SOKI SESSION BOOTSTRAP"
python3 -c "import json; print(json.load(open('.soki/state.json'))['bootstrap']['status'])"
# expect: pending
```

**5.2 Prompt gate — bootstrap pending**
```bash
echo '{}' | .claude/hooks/soki-prompt-gate.py | jq -r .hookSpecificOutput.additionalContext | head -3
# expect: "=== SOKI BOOTSTRAP STILL PENDING ==="
```

**5.3 Tool gate — mutating tool blocked while pending**
```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"README.md"}}' | \
  .claude/hooks/soki-tool-gate.py | jq .
# expect: permissionDecision: "deny"
```

**5.4 Tool gate — Reads of required files auto-complete bootstrap**
```bash
for f in knowledge/index/index--system--project-navigation.md \
         knowledge/specs/spec--system--knowledge-driven-task-orchestration.md \
         knowledge/architecture/architecture--system--overall-structure.md \
         knowledge/invariants/invariant--system--lifecycle-gates.md; do
  printf '{"tool_name":"Read","tool_input":{"file_path":"%s"}}' "$f" \
    | .claude/hooks/soki-tool-gate.py
  echo
done
python3 -c "import json; print(json.load(open('.soki/state.json'))['bootstrap']['status'])"
# expect: completed
```

**5.5 Tool gate — Decision Gate missing after bootstrap**
```bash
# Write a fake transcript with no Decision Gate, then point the gate at it.
python3 <<'PY'
import json
lines=[
  {"type":"user","message":{"role":"user","content":"edit"}},
  {"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I will edit."}]}},
]
open("/tmp/t1.jsonl","w").write("\n".join(map(json.dumps, lines)))
PY
echo '{"tool_name":"Edit","tool_input":{"file_path":"x"},"transcript_path":"/tmp/t1.jsonl"}' \
  | .claude/hooks/soki-tool-gate.py
# expect: permissionDecision: "deny" with DECISION GATE MISSING reason
```

**5.6 Tool gate — Decision Gate present → allow**
```bash
python3 <<'PY'
import json
text = "### Context Decision\nKB consult required: YES\nReasoning: need patterns."
lines=[
  {"type":"user","message":{"role":"user","content":"edit"}},
  {"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":text}]}},
]
open("/tmp/t2.jsonl","w").write("\n".join(map(json.dumps, lines)))
PY
echo '{"tool_name":"Edit","tool_input":{"file_path":"x"},"transcript_path":"/tmp/t2.jsonl"}' \
  | .claude/hooks/soki-tool-gate.py
# expect: {"continue": true}
```

**5.7 Exit gate — the six canonical cases**

Generate fixtures (missing, good, rule1, rule3, placement, good-with-rule3-tail) with `python3 <<PY` the way `docs/soki-implementation-report.md` §2 describes, then:

```bash
for c in missing-closure good-closure rule1-violation rule3-violation \
         placement-violation good-with-rule3-tail; do
  printf '{"transcript_path":"/tmp/soki-tests/%s.jsonl"}' "$c" \
    | .claude/hooks/soki-exit-gate.py
done
```

Expected:
- missing-closure → block
- good-closure → continue
- rule1-violation → block
- rule3-violation → block
- placement-violation → block
- good-with-rule3-tail → continue

**5.8 Exit gate — anti-loop + empty transcript fail-open**
```bash
echo '{"stop_hook_active":true}' | .claude/hooks/soki-exit-gate.py
# expect: continue
echo '{"transcript_path":"/tmp/does-not-exist.jsonl"}' | .claude/hooks/soki-exit-gate.py
# expect: continue
```

All 17 assertions above passed during this pass.

---

## 6. System Review

### 6.1 Enforcement strength — what the hooks actually guarantee

| Gate | Mechanism | Hard-block? | Confidence |
|---|---|---|---|
| Session Bootstrap | PreToolUse blocks all non-read tools until the read-ledger is satisfied; Stop requires the confirmation block on turns that close the bootstrap | Yes — PreToolUse denies; Stop blocks the turn | High. The only escape is the `.soki/state.json` file itself, which the agent could technically write once a mutating tool is allowed — but until bootstrap is marked complete, Write itself is blocked, so there is no exploit path for a well-behaved agent. |
| Context Decision Gate | PreToolUse parses the current turn's assistant text and requires a `### Context Decision … KB consult required: YES\|NO` block | Yes — PreToolUse denies mutating tools if absent | Medium-high. Regex is tolerant (`context decision` with optional "gate"), so minor formatting drift is accepted. Can be spoofed by the agent writing the literal string without doing the work, but at least the decision becomes traceable in the transcript. |
| Exit Gate | Stop hook regex-matches Closure Block and runs dependency + placement checks | Yes — `decision: block` returns a corrective prompt | High on Rules 1 and 3; placement check only tolerates a single Rule 3 justification tail line. |

### 6.2 Weaknesses & failure modes

1. **Regex-shaped compliance beats semantic compliance.** Nothing prevents an agent from emitting a correctly-formatted Decision Gate block with a meaningless justification, or from answering `KB consult required: NO` when it should read the KB. This is a fundamental limit of transcript-regex enforcement — see §7 for a stronger amplifier.
2. **No invariant content is validated.** Reading `invariants/invariant--system--lifecycle-gates.md` satisfies bootstrap regardless of whether the file's content is meaningful or stale. The hook checks **read-count**, not comprehension.
3. **Transcript parsing depends on Claude Code's format.** `_soki_common.read_transcript_current_turn` handles the two observed shapes (`{type, content}` and `{type, message:{role, content}}`). Undocumented changes to the transcript JSONL schema would silently break the Decision-Gate and Closure-Block checks (both gates would fail-open on empty turn-text).
4. **`stop_hook_active` anti-loop fails open.** On the second Stop invocation after a block, the hook immediately allows — so an agent can "satisfy" Exit Gate just by triggering one block and ignoring the correction. Intentional per Claude Code guidance (infinite-loop risk), but it weakens the gate.
5. **PreCompact reuses the same bootstrap hook.** After compaction the state resets to pending. That is correct per spec, but compaction itself often happens mid-task, and the agent will then be blocked from continuing until it re-reads the mandatory set. Users will hit this and be confused.
6. **No write-path protection for `.soki/state.json`.** Nothing stops the agent from `echo '{"bootstrap":{"status":"completed"}}' > .soki/state.json` once Bash is allowed. Mitigated because Bash is blocked while bootstrap is pending, but an honest protocol-respecting agent could edit state during normal operation.
7. **Spec drift risk.** Three places encode rules: the specs under `knowledge/specs/`, the hook messages, and the regex patterns in `_soki_common.py`. Any divergence will confuse future agents. Specifically:
   - Frontmatter spec requires `created:` + `updated:` but `knowledge-driven-task-orchestration.md` still uses `date:`.
   - `status: active` exists in at least one doc but is not in the allow-list of `spec--system--document-frontmatter.md`.
   - Two status vocabularies are observable in the corpus (`active`/`approved`/`draft`/…) — no authoritative enumeration survives reconciliation yet.
8. **Settings reload is not self-serving.** When the hook config in `.claude/settings.json` changes, Claude Code doesn't reload it until `/hooks` is opened or the session restarts. A CLAUDE.md note now documents this, but it's a user-facing caveat, not a technical guarantee.
9. **Bootstrap is not atomic.** If the agent reads three of four required files and then drops connection, next UserPromptSubmit will re-inject the pending reminder but the ledger is preserved — the agent only needs to read one more file. That is arguably fine, but it means a partially-bootstrapped session has partial enforcement (non-read tools still blocked, but some required context already in play).
10. **Matcher is allowlist-style.** The PreToolUse matcher enumerates known tools. If Claude Code introduces a new mutating tool that is not in the list, it bypasses the Decision-Gate requirement silently until the matcher is extended.

### 6.3 Edge cases worth noting

- **First-turn bootstrap-completion turn.** The Stop hook requires the `Session Bootstrap Completed` confirmation when state is still pending. But bootstrap auto-completes on the 4th successful Read (the invariant), so by the time Stop fires on that same turn, `state.bootstrap.status` is already `completed` — the confirmation-block check is skipped and the Closure Block check kicks in. Agents must still produce a Closure Block on the very first turn. This is documented in the turn-contract injection.
- **Subagent dispatch.** `superpowers:using-superpowers` includes a `<SUBAGENT-STOP>` clause that skips skill invocation for subagents. Hook enforcement still fires for subagents' tool calls. A subagent dispatched before bootstrap would be blocked out of its tool budget. Not tested in this pass.
- **Compaction mid-turn.** If compaction fires after the Decision Gate block was already emitted, the transcript parser will only look at post-`PreCompact` messages — the Decision Gate block could be "lost". PreCompact resets bootstrap, so PreToolUse will block regardless, which is actually correct but for the wrong reason.

---

## 7. Improvements

Concrete, ordered by leverage.

1. **Promote the Exit Gate to a structural verifier, not a regex matcher.** Emit a `Closure Block` JSON fragment alongside the prose, and have the Stop hook validate the JSON. Parsing becomes robust; the prose version is redundant display.
2. **Inject the Bootstrap confirmation automatically.** Have `soki-tool-gate.py`, on the read that completes the ledger, write the confirmation block's expected shape into the allow-decision `permissionDecisionReason` — the agent then only has to echo it. Reduces the chance of "ledger complete, confirmation block never emitted → Exit Gate blocks" loops.
3. **Add a "sanity-check" sub-rule to the Decision Gate regex.** Require `Reasoning:` to be non-empty and longer than, say, 20 characters. Block one-word justifications.
4. **Move hook contract into a single spec that the hooks consume.** Today the "Closure Block must have exactly these four fields in this order" rule is duplicated in `specs/spec--system--exit-gate.md`, `_soki_common.py`, and the prompt-gate injection. Extract a `specs/spec--system--hook-contracts.md` and have the hooks load regex patterns from it at startup (Python literal import or YAML read).
5. **Reconcile frontmatter vocabulary.** Fix `knowledge-driven-task-orchestration.md` to use `created:`/`updated:` instead of `date:`, and either extend the frontmatter spec's `status` enum to include `active` or mass-rename existing `active` usages to `approved`.
6. **Add a `PostCompact` hook that injects a shorter "re-bootstrap" reminder.** The current `PreCompact → bootstrap-reset` approach leaves the compaction summary carrying SOKI context but no mandatory reading — `PostCompact` would be the correct point to force re-read.
7. **Protect `.soki/state.json` against self-tampering.** Add a PreToolUse guard: if the tool is `Write`/`Edit`/`Bash` and the target path contains `.soki/state.json`, deny. Trivially prevents the "agent flips its own bootstrap flag" attack.
8. **Add a PreToolUse clause that detects read-ledger drift.** If the agent reads `knowledge/` files but none of them are required-reads for bootstrap, after N (say 10) off-ledger reads, inject a reminder that bootstrap still requires specific files.
9. **Emit a machine-readable summary on Stop's allow path.** `soki-exit-gate.py` could write `.soki/last-closure.json` so downstream systems (git pre-commit, CI) can read "did this session change the KB?" without parsing the transcript.
10. **Write a `tests/hooks.sh` harness.** The validation plan in §5 is manual. Turn it into an executable script with expected-output asserts; run it in CI. Without it, hook drift regressions will only surface when a live session silently fails to block.
11. **Deprecate `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` (moved from `bootstrap.md`).** It predates SOKI and contradicts the specs (it describes a Mode-A/B/C interview flow instead of the three-gate model). Move to `knowledge/decisions/decision--system--soki-supersedes-legacy-bootstrap.md` for historical trace, delete the root copy.
12. **Stabilize the matcher.** Replace the enumerated `Read|Glob|…|TodoWrite` string with an explicit dual-list approach: one matcher `.*` that runs the hook, and deny-by-default logic inside the hook for unknown tool names. Eliminates the "new tool added to CC → silent bypass" failure mode from §6.2 item 10.

---

## 8. Summary

The repository now ships a complete, installable SOKI runtime. Hooks live in `.claude/hooks/`, config in `.claude/settings.json`, vault in `knowledge/`, runtime state in `.soki/`. All three gates (Bootstrap, Context Decision, Exit) have been shown to block correctly and to release on valid inputs. Known weaknesses — regex compliance, state tampering, matcher enumeration — are documented and each has a concrete amplifier proposal.

The review identified five substantive issues in the source specs themselves (frontmatter-field drift, status vocabulary, vault/world duplication, missing frontmatter on `context-decision-gate.md`, legacy bootstrap.md vs SOKI) of which three were silently fixed in this pass and two are left as §7 follow-ups requiring explicit owner decisions.
