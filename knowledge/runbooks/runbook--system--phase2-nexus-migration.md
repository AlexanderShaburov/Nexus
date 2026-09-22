---
type: runbook
scope: system
status: deprecated
created: 2026-04-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: historical
tags:
  - system
  - nexus
  - migration
  - phase2
  - historical
---

## Relations

- implements:
  - [ADR — Rename SOKI to Nexus](../decisions/adr--system--rename-soki-to-nexus.md) — operationalized the rename decision.
- relates_to:
  - [Terminology Glossary](../glossary/glossary--system--terminology.md) — codified the canonical name retired by this runbook's execution.

---

# Phase 2 — Nexus Migration Runbook

> Historical record only.
> This runbook was used for the completed Phase 2 hard migration from SOKI to Nexus.
> Migration is already executed.
> Preserve for reference and audit; do not use as the active runtime procedure.

Operator-grade runbook for the hard rename of the SOKI runtime to Nexus.

Target end state: canonical prefix `nexus`, runtime dir `.nexus/`, hooks `nexus-*.py`, shared module `_nexus_common.py`, emitted strings `NEXUS ...`, no dual naming, no compatibility shim.

All paths are relative to `$CLAUDE_PROJECT_DIR` (repo root).

---

## 1. Preconditions

- [ ] `git status` is clean (no unstaged / uncommitted changes).
- [ ] No active Claude Code session is running against this repo. If one is, the hooks about to be renamed are currently enforcing; migrate from outside, or temporarily disable hooks via `mv .claude/settings.json .claude/settings.json.off` and restore after Commit 1 validation.
- [ ] A feature branch exists: `git checkout -b phase2/nexus-rename`.
- [ ] Bash, `python3`, `jq` (optional), and standard GNU `grep` are available.
- [ ] Operator has reviewed §2 "Do Not Touch".
- [ ] Operator has write access and the repo remote is known (no `git push` during runbook).

---

## 2. Do Not Touch

These files remain historical. Do not rename. Do not rewrite their bodies except where explicitly allowed.

| File | Allowed edit (if any) |
|---|---|
| `docs/COMM.log` | **None.** Conversation log. |
| `prompt_soki_hooks_and_review.md` | **None.** Historical task prompt. |
| `knowledge/decisions/adr--system--rename-soki-to-nexus.md` | Optional: append one dated line under "Phase 2 — Gradual Replacement" noting execution. Do not alter Context/Decision/Rationale. Filename stays. |
| `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` | Optional: update header prose only (lines 11–15). Do not edit the preserved-verbatim body below horizontal rules. |
| `legacy-kb/**` | **None.** Deprecated bundle. |
| `nexus_approach.md` | **None.** Already renamed Phase 1. |
| Historical narrative sections of `docs/nexus-implementation-report.md` (after rename) | §1, §2 intro, §3 table, §6, §7 — leave as historical record. |

---

## 3. Atomic Runtime Migration

**Rule:** §3.1 + §3.2 + §3.3 must land in a single commit (§3.4). Runtime state does not work in a partial state.

### 3.1 Rename operations

```bash
git mv .claude/hooks/_soki_common.py    .claude/hooks/_nexus_common.py
git mv .claude/hooks/soki-bootstrap.py  .claude/hooks/nexus-bootstrap.py
git mv .claude/hooks/soki-prompt-gate.py .claude/hooks/nexus-prompt-gate.py
git mv .claude/hooks/soki-tool-gate.py  .claude/hooks/nexus-tool-gate.py
git mv .claude/hooks/soki-exit-gate.py  .claude/hooks/nexus-exit-gate.py
git mv .soki .nexus
git mv SOKI_INSTALLATION_GUIDE.md NEXUS_INSTALLATION_GUIDE.md   # body rewrite in §5
git mv docs/soki-implementation-report.md docs/nexus-implementation-report.md   # body rewrite in §5
```

Note: the last two `git mv`s are for §5 but may be batched here to reduce commits if operator prefers a larger atomic change. Default runbook keeps §3 and §5 as separate commits.

### 3.2 Required content edits

Perform all edits before committing §3.

**File: `.claude/hooks/_nexus_common.py`**

| Locate | Replace |
|---|---|
| `"""Shared helpers for SOKI hooks.` (line 1) | `"""Shared helpers for Nexus hooks.` |
| `return project_dir() / ".soki" / "state.json"` | `return project_dir() / ".nexus" / "state.json"` |

**File: `.claude/hooks/nexus-bootstrap.py`**

| Locate | Replace |
|---|---|
| `"""SOKI: SessionStart + PreCompact hook.` | `"""Nexus: SessionStart + PreCompact hook.` |
| `from _soki_common import (` | `from _nexus_common import (` |
| `"=== SOKI SESSION BOOTSTRAP — MANDATORY ==="` | `"=== NEXUS SESSION BOOTSTRAP — MANDATORY ==="` |

**File: `.claude/hooks/nexus-prompt-gate.py`**

| Locate | Replace |
|---|---|
| `"""SOKI: UserPromptSubmit hook.` | `"""Nexus: UserPromptSubmit hook.` |
| `from _soki_common import (` | `from _nexus_common import (` |
| `TURN_CONTRACT = """=== SOKI TURN CONTRACT (per-turn) ===` | `TURN_CONTRACT = """=== NEXUS TURN CONTRACT (per-turn) ===` |
| `"=== SOKI BOOTSTRAP STILL PENDING ==="` | `"=== NEXUS BOOTSTRAP STILL PENDING ==="` |

**File: `.claude/hooks/nexus-tool-gate.py`**

| Locate | Replace |
|---|---|
| `"""SOKI: PreToolUse hook.` | `"""Nexus: PreToolUse hook.` |
| `from _soki_common import (` | `from _nexus_common import (` |
| `f"SOKI BOOTSTRAP PENDING: tool '{tool}' is BLOCKED. "` | `f"NEXUS BOOTSTRAP PENDING: tool '{tool}' is BLOCKED. "` |
| `f"SOKI DECISION GATE MISSING: tool '{tool}' is BLOCKED. "` | `f"NEXUS DECISION GATE MISSING: tool '{tool}' is BLOCKED. "` |

**File: `.claude/hooks/nexus-exit-gate.py`**

| Locate | Replace |
|---|---|
| `"""SOKI: Stop hook.` | `"""Nexus: Stop hook.` |
| `from _soki_common import (` | `from _nexus_common import (` |
| `"SOKI EXIT GATE: bootstrap is still pending. ...` | `"NEXUS EXIT GATE: bootstrap is still pending. ...` |
| `"SOKI EXIT GATE VIOLATION: Closure Block missing ...` | `"NEXUS EXIT GATE VIOLATION: Closure Block missing ...` |
| `emit_block("SOKI EXIT GATE VIOLATION:\n  - " + ...)` | `emit_block("NEXUS EXIT GATE VIOLATION:\n  - " + ...)` |

**File: `.claude/settings.json`**

Replace all 5 command paths:

| Old | New |
|---|---|
| `$CLAUDE_PROJECT_DIR/.claude/hooks/soki-bootstrap.py` (×2, SessionStart + PreCompact) | `$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-bootstrap.py` |
| `$CLAUDE_PROJECT_DIR/.claude/hooks/soki-prompt-gate.py` | `$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-prompt-gate.py` |
| `$CLAUDE_PROJECT_DIR/.claude/hooks/soki-tool-gate.py` | `$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-tool-gate.py` |
| `$CLAUDE_PROJECT_DIR/.claude/hooks/soki-exit-gate.py` | `$CLAUDE_PROJECT_DIR/.claude/hooks/nexus-exit-gate.py` |

Replace all 5 `statusMessage` values:

| Old | New |
|---|---|
| `SOKI bootstrap` | `Nexus bootstrap` |
| `SOKI re-bootstrap` | `Nexus re-bootstrap` |
| `SOKI turn contract` | `Nexus turn contract` |
| `SOKI tool gate` | `Nexus tool gate` |
| `SOKI exit gate` | `Nexus exit gate` |

**File: `.gitignore`**

| Old line | New line |
|---|---|
| `# SOKI runtime state (regenerated per session)` | `# Nexus runtime state (regenerated per session)` |
| `.soki/state.json` | `.nexus/state.json` |

**File: `.nexus/README.md`** (was `.soki/README.md`)

Rewrite body. Minimum target:

```markdown
# .nexus/ — Nexus Runtime State

This directory holds ephemeral per-session state for the Nexus enforcement hooks. It is regenerated at every `SessionStart` and is not a source of truth.

Contents:
- `state.json` — per-session runtime: bootstrap status, read-ledger, turn index, decision-gate flag.

Do not edit by hand. Do not check `state.json` into version control (a `.gitignore` entry is provided).

If `state.json` is missing or corrupt, the hooks will recreate it with `bootstrap.status = "pending"` on the next `SessionStart`. Force a reset by deleting it.
```

### 3.3 Runtime state cleanup

```bash
rm -rf .claude/hooks/__pycache__
rm -f  .nexus/state.json .soki/state.json 2>/dev/null
rmdir  .soki 2>/dev/null || true   # remove only if empty
chmod +x .claude/hooks/nexus-*.py
```

### 3.4 Commit boundary

```bash
git add .claude/hooks .claude/settings.json .gitignore .nexus
git status   # verify: no stray files; no stale .soki/ tracked
git commit -m "Phase 2: hard-rename SOKI runtime to Nexus (hooks, settings, .nexus/, gitignore)"
```

Run §7 validation (Runtime Validation block) before proceeding.

---

## 4. Documentation Coherence Pass

Single commit. All frontmatter `updated:` fields under `knowledge/` MUST be bumped to the Phase 2 execution date.

| File | Required change | Historical content allowed? |
|---|---|---|
| `CLAUDE.md` | Replace `Nexus (formerly SOKI)` intro wording with `Nexus`. Replace `.soki/` → `.nexus/`. Replace 5 hook filename refs (lines 27–30 currently list them with `.sh` extension — **fix to `.py`** at the same time). Replace `_soki_common.py` → `_nexus_common.py`. Replace `docs/soki-implementation-report.md` → `docs/nexus-implementation-report.md`. | No. |
| `README.md` | Title → `# Nexus Knowledge Runtime`. Replace all 7 × `.soki/` → `.nexus/` (incl. file tree + checklist at line 424 + code block at line 224). Replace hook filenames in file tree (lines 164–168) + `_soki_common.py`. Replace `.soki/README.md` refs. | No. |
| `knowledge/architecture/architecture--system--overall-structure.md` | Tag `soki` → `nexus`. Title drop `(formerly SOKI)`. Replace 5 × hook filenames. Replace 3 × `.soki/` → `.nexus/`. Replace `(enforced by soki-*.py)` → `(enforced by nexus-*.py)`. Bump `updated:`. | No. |
| `knowledge/index/index--system--project-navigation.md` | Line 15 drop `(formerly SOKI)`. Line 61 `.soki/` → `.nexus/`. Lines 63–66 hook filenames `soki-*` → `nexus-*`. Bump `updated:`. | No. |
| `knowledge/invariants/invariant--system--lifecycle-gates.md` | Tag `soki` → `nexus`. Lines 33–36 hook filenames. Bump `updated:`. | No. |
| `knowledge/glossary/glossary--system--terminology.md` | **Move** the `SOKI` row from "Legacy Aliases" table into "Retired Terms" table with rationale `"Fully migrated to Nexus on YYYY-MM-DD per Phase 2 (see adr--system--rename-soki-to-nexus.md)"`. Remove enumeration of retained SOKI locations — it is false post-Phase 2. Bump `updated:`. | No. |
| `.claude/skills/project-ingest/SKILL.md` | Line 11 drop `(formerly SOKI)`. | No. |
| `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` | OPTIONAL: header prose only (lines 11, 13, 15) — drop `(formerly SOKI)` / `pre-SOKI` transitional forms. Bump `updated:` only if edited. | **Yes, body is verbatim historical.** |
| `knowledge/decisions/adr--system--rename-soki-to-nexus.md` | OPTIONAL: under Phase 2 heading, append one line: `Executed YYYY-MM-DD, commits <sha1>..<sha4>`. | **Yes, body is historical record.** |

Commit:

```bash
git add CLAUDE.md README.md knowledge/ .claude/skills/project-ingest/SKILL.md
git commit -m "Phase 2: update active docs for Nexus runtime coherence"
```

Run §7 Grep Validation block.

---

## 5. Secondary File Renames

### 5.1 Installation guide

- Rename: `SOKI_INSTALLATION_GUIDE.md` → `NEXUS_INSTALLATION_GUIDE.md` (done in §3.1 if batched; otherwise `git mv` now).
- Body rewrite:
  - Title: `# Nexus Installation & Usage Guide`
  - All 4 × `.soki/` → `.nexus/` (lines 21, 37, 47, 80)
  - `.soki/state.json` → `.nexus/state.json` (line 80)
  - Drop transitional `(formerly SOKI)` phrasing.
- References that must be updated: **none found** in the tree — this file has no inbound links by filename. Confirm with: `grep -rn 'SOKI_INSTALLATION_GUIDE' . --include='*.md'` (expect empty).

### 5.2 Implementation report

- Rename: `docs/soki-implementation-report.md` → `docs/nexus-implementation-report.md`.
- Body rewrite policy:
  - **Rewrite** §4 Placement Instructions: all path refs `.soki/` → `.nexus/`, all hook filenames `soki-*` → `nexus-*`.
  - **Rewrite** §5 Validation Plan: every `.soki/state.json` → `.nexus/state.json`; every `.claude/hooks/soki-*.py` → `nexus-*.py`; every `# expect: "=== SOKI ...` → `# expect: "=== NEXUS ...`; `rm -f .soki/state.json` → `rm -f .nexus/state.json`.
  - **Rewrite** §8 Summary: present-tense sentences describing "the repository now ships" updated to Nexus names.
  - **Keep as historical** §1, §2 narrative, §3 table (historical snapshot), §6 review, §7 improvements.
  - **Append** new final section: `## 9. Phase 2 Migration — Executed YYYY-MM-DD` with commit SHAs of the Phase 2 commits.
- References that must be updated:
  - `CLAUDE.md` line 60 — **already handled in §4** pass (verify now).

Commit:

```bash
git add NEXUS_INSTALLATION_GUIDE.md docs/nexus-implementation-report.md
git status   # confirm old names are tracked as deletions, not stragglers
git commit -m "Phase 2: rename installation guide and implementation report"
```

---

## 6. Exact Execution Sequence

1. `git checkout -b phase2/nexus-rename`
2. Verify preconditions (§1 checklist).
3. Rename runtime files (§3.1 — the 6 `git mv`s for hooks + `.soki` → `.nexus`).
4. Edit `_nexus_common.py` (§3.2 table: docstring, `state_path()` constant).
5. Edit 4 × hook files (§3.2 tables: docstring + import + emitted strings).
6. Edit `.claude/settings.json` (§3.2: 5 commands + 5 statusMessages).
7. Edit `.gitignore` (§3.2: comment + pattern).
8. Rewrite `.nexus/README.md` (§3.2).
9. Delete stale pycache + state + empty `.soki/` dir (§3.3).
10. `chmod +x .claude/hooks/nexus-*.py`.
11. Run **Runtime Validation** block from §7. All checks must print `OK:`.
12. `git add` + commit (§3.4).
13. Edit active docs (§4 table: CLAUDE.md, README.md, architecture, index, invariant, glossary, skill).
14. Bump `updated:` frontmatter on every edited file under `knowledge/`.
15. Run **Grep Validation** block from §7. Only the residual-allowlist hits permitted.
16. `git add` + commit (§4 commit message).
17. `git mv SOKI_INSTALLATION_GUIDE.md NEXUS_INSTALLATION_GUIDE.md` (skip if done in §3.1).
18. `git mv docs/soki-implementation-report.md docs/nexus-implementation-report.md` (skip if done in §3.1).
19. Rewrite installation guide body (§5.1).
20. Rewrite implementation report active sections + append §9 (§5.2).
21. Verify `CLAUDE.md` pointer to implementation report resolves.
22. `git add` + commit (§5 commit message).
23. OPTIONAL (§4 optional rows + §2 allowed edits): dated notes in ADR + legacy-bootstrap decision. Commit separately as `Phase 2: historical record updates`.
24. Run **Final Validation** (§7 all blocks, including Hook Sanity).
25. Re-enable hook config if disabled in §1 (`mv .claude/settings.json.off .claude/settings.json`).
26. Open a Claude Code session in the repo; verify `=== NEXUS SESSION BOOTSTRAP` banner appears on SessionStart and `.nexus/state.json` is created.
27. Push branch + open PR.

---

## 7. Validation Commands

All commands assume `cd $CLAUDE_PROJECT_DIR`.

### 7.1 File existence / absence

```bash
set -e
for f in \
  .claude/hooks/_nexus_common.py \
  .claude/hooks/nexus-bootstrap.py \
  .claude/hooks/nexus-prompt-gate.py \
  .claude/hooks/nexus-tool-gate.py \
  .claude/hooks/nexus-exit-gate.py \
  .nexus/README.md \
  NEXUS_INSTALLATION_GUIDE.md \
  docs/nexus-implementation-report.md \
; do test -e "$f" || { echo "MISSING: $f"; exit 1; }; done
echo "OK: new files exist"

for f in \
  .claude/hooks/_soki_common.py \
  .claude/hooks/soki-bootstrap.py \
  .claude/hooks/soki-prompt-gate.py \
  .claude/hooks/soki-tool-gate.py \
  .claude/hooks/soki-exit-gate.py \
  .soki \
  SOKI_INSTALLATION_GUIDE.md \
  docs/soki-implementation-report.md \
; do test ! -e "$f" || { echo "STILL EXISTS: $f"; exit 1; }; done
echo "OK: old names absent"

for h in nexus-bootstrap nexus-prompt-gate nexus-tool-gate nexus-exit-gate; do
  test -x ".claude/hooks/$h.py" || { echo "NOT EXECUTABLE: $h"; exit 1; }
done
echo "OK: hook exec bits"
```

### 7.2 Import / compile check

```bash
python3 -c "
import sys; sys.path.insert(0, '.claude/hooks')
import _nexus_common
p = str(_nexus_common.state_path())
assert p.endswith('/.nexus/state.json'), p
print('OK: state_path =', p)
"

for h in nexus-bootstrap nexus-prompt-gate nexus-tool-gate nexus-exit-gate; do
  python3 -c "import py_compile; py_compile.compile('.claude/hooks/${h}.py', doraise=True)" \
    && echo "OK: compile $h" || { echo "FAIL compile: $h"; exit 1; }
done
```

### 7.3 Settings check

```bash
python3 - <<'PY'
import json, re, sys
cfg = json.load(open('.claude/settings.json'))
paths, msgs = [], []
for entries in cfg['hooks'].values():
    for e in entries:
        for h in e['hooks']:
            paths.append(h['command'])
            msgs.append(h.get('statusMessage',''))
bad_p = [p for p in paths if re.search(r'soki', p, re.I)]
bad_m = [m for m in msgs  if re.search(r'SOKI', m)]
assert not bad_p, f"SOKI in paths: {bad_p}"
assert not bad_m, f"SOKI in statusMessages: {bad_m}"
print("OK: settings.json paths =", len(paths), "; statusMessages =", len(msgs))
PY
```

### 7.4 Gitignore check

```bash
grep -qE '^\.nexus/state\.json$' .gitignore && echo "OK: .gitignore pattern"
! grep -iq soki .gitignore && echo "OK: no SOKI in .gitignore"
```

### 7.5 Grep validation — residual active `soki`

```bash
# Active code/config/runtime must have ZERO occurrences
RES=$(grep -riE 'soki|\.soki' .claude .nexus .gitignore 2>/dev/null || true)
[ -z "$RES" ] && echo "OK: no soki refs in active runtime" || { echo "FAIL — residual:"; echo "$RES"; exit 1; }

# Active docs: only allowlist files may contain soki
grep -rniE 'soki|\.soki' \
  --include='*.md' \
  --exclude-dir=legacy-kb \
  --exclude-dir=.git \
  . 2>/dev/null \
  | grep -vE '^\./docs/COMM\.log' \
  | grep -vE '^\./prompt_soki_hooks_and_review\.md' \
  | grep -vE '^\./knowledge/decisions/adr--system--rename-soki-to-nexus\.md' \
  | grep -vE '^\./knowledge/decisions/decision--system--advisory-bootstrap-legacy\.md' \
  | grep -vE '^\./knowledge/glossary/glossary--system--terminology\.md' \
  | grep -vE '^\./docs/nexus-implementation-report\.md' \
  || echo "OK: no residual soki refs outside allowlist"
# Any surviving lines above "OK:" are violations — review each.
```

### 7.6 Hook sanity — bootstrap + pending + mutate-blocked

```bash
set -e
export CLAUDE_PROJECT_DIR="$PWD"
rm -f .nexus/state.json

# a) bootstrap banner
echo '{"session_id":"v1","hook_event_name":"SessionStart"}' \
  | .claude/hooks/nexus-bootstrap.py \
  | python3 -c "import json,sys; d=json.load(sys.stdin); c=d['hookSpecificOutput']['additionalContext']; assert 'NEXUS SESSION BOOTSTRAP' in c; print('OK: bootstrap banner')"

# b) state pending
python3 -c "import json; assert json.load(open('.nexus/state.json'))['bootstrap']['status']=='pending'; print('OK: state pending')"

# c) prompt gate — pending reminder
echo '{}' | .claude/hooks/nexus-prompt-gate.py \
  | python3 -c "import json,sys; c=json.load(sys.stdin)['hookSpecificOutput']['additionalContext']; assert 'NEXUS BOOTSTRAP STILL PENDING' in c; print('OK: pending reminder')"

# d) tool gate — mutate blocked with Nexus wording
echo '{"tool_name":"Edit","tool_input":{"file_path":"README.md"}}' \
  | .claude/hooks/nexus-tool-gate.py \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['hookSpecificOutput']; assert d['permissionDecision']=='deny'; assert 'NEXUS BOOTSTRAP PENDING' in d['permissionDecisionReason']; print('OK: mutate-deny')"

# e) auto-complete bootstrap via 4 reads
for f in knowledge/index/index--system--project-navigation.md \
         knowledge/specs/spec--system--knowledge-driven-task-orchestration.md \
         knowledge/architecture/architecture--system--overall-structure.md \
         knowledge/invariants/invariant--system--lifecycle-gates.md; do
  printf '{"tool_name":"Read","tool_input":{"file_path":"%s"}}' "$f" \
    | .claude/hooks/nexus-tool-gate.py > /dev/null
done
python3 -c "import json; assert json.load(open('.nexus/state.json'))['bootstrap']['status']=='completed'; print('OK: auto-completed')"

# f) exit gate anti-loop
echo '{"stop_hook_active":true}' | .claude/hooks/nexus-exit-gate.py \
  | python3 -c "import json,sys; assert json.load(sys.stdin).get('continue') is True; print('OK: exit-gate anti-loop')"

rm -f .nexus/state.json
echo "OK: hook sanity suite PASSED"
```

### 7.7 `.nexus/state.json` recreation

```bash
rm -f .nexus/state.json
export CLAUDE_PROJECT_DIR="$PWD"
echo '{"session_id":"v2","hook_event_name":"SessionStart"}' \
  | .claude/hooks/nexus-bootstrap.py > /dev/null
test -f .nexus/state.json && echo "OK: .nexus/state.json recreated"
test ! -e .soki/state.json && echo "OK: no .soki/state.json leaked"
```

---

## 8. Rollback

Always work from the feature branch `phase2/nexus-rename`. Do not `git push --force` to shared branches.

### 8.1 Runtime migration failed (Commit 1)

```bash
# Revert the single runtime commit
git revert --no-edit <COMMIT_1_SHA>

# Clean runtime artifacts from the failed attempt
rm -rf .claude/hooks/__pycache__
rm -f  .nexus/state.json .soki/state.json

# Re-run §7.6 against the restored soki-* hook filenames (substitute names).
# If pre-migration hooks fire correctly: rollback successful.
```

If the working tree is mid-edit and no commit exists yet:

```bash
git restore --staged .
git restore .
git clean -fd .claude/hooks .nexus .soki
```

### 8.2 Docs pass failed (Commit 2)

```bash
git revert --no-edit <COMMIT_2_SHA>
# Runtime is unaffected. Re-edit docs and re-commit.
```

### 8.3 Guide/report rename failed (Commit 3)

```bash
git revert --no-edit <COMMIT_3_SHA>
# Runtime + active docs still point at renamed paths from Commit 2 —
# VERIFY BEFORE EXECUTION: after revert, check CLAUDE.md line 60 does
# not still reference docs/nexus-implementation-report.md if that file
# no longer exists. Fix forward if so.
```

### 8.4 Total abort

```bash
git checkout main
git branch -D phase2/nexus-rename
rm -rf .claude/hooks/__pycache__ .nexus/state.json
# .soki/state.json will regenerate on next SessionStart.
```

---

## 9. Final Success Criteria

- [ ] `.nexus/` exists; `.soki/` does not.
- [ ] All 5 hook files renamed to `nexus-*` (plus `_nexus_common.py`); none remain under `soki-*`.
- [ ] `.claude/settings.json` contains no string matching `soki` (case-insensitive).
- [ ] `.gitignore` references `.nexus/state.json`; no `soki` strings.
- [ ] All 7 §7 validation blocks exit 0 with `OK:` lines.
- [ ] `CLAUDE.md` hook-list section uses `nexus-*.py` (and the preexisting `.sh` bug is fixed).
- [ ] `README.md`, `NEXUS_INSTALLATION_GUIDE.md`, architecture/index/invariant/glossary docs all reference Nexus paths.
- [ ] Grep for `soki`/`\.soki` across the tree returns only allowlist entries (§C below).
- [ ] A fresh Claude Code session in the repo shows `=== NEXUS SESSION BOOTSTRAP` banner.

---

## 10. Quick Operator Checklist

```
[ ]  branch: phase2/nexus-rename
[ ]  git mv 5 hooks + .soki → .nexus (§3.1)
[ ]  edit _nexus_common.py (state_path, docstring)
[ ]  edit 4 hooks (import + docstring + strings)
[ ]  edit settings.json (5 paths + 5 statusMessages)
[ ]  edit .gitignore
[ ]  rewrite .nexus/README.md
[ ]  rm -rf .claude/hooks/__pycache__ ; rm -f .nexus/state.json .soki/state.json
[ ]  chmod +x .claude/hooks/nexus-*.py
[ ]  run §7.1–§7.6    → COMMIT 1
[ ]  edit active docs (CLAUDE, README, arch, index, invariant, glossary, skill)
[ ]  bump updated: on every knowledge/ file edited
[ ]  run §7.5 grep    → COMMIT 2
[ ]  git mv guide + report ; rewrite bodies
[ ]  run §7.1 + §7.5  → COMMIT 3
[ ]  (optional) ADR + legacy-bootstrap dated notes → COMMIT 4
[ ]  open Claude Code session ; confirm NEXUS banner
[ ]  push + PR
```

---

## A. Runtime Rename Table

| Old | New | Type | Must Change In Same Commit? |
|---|---|---|---|
| `.claude/hooks/_soki_common.py` | `.claude/hooks/_nexus_common.py` | file + content (docstring, `state_path()`) | **Yes (Commit 1)** |
| `.claude/hooks/soki-bootstrap.py` | `.claude/hooks/nexus-bootstrap.py` | file + content (import, docstring, emitted strings) | **Yes (Commit 1)** |
| `.claude/hooks/soki-prompt-gate.py` | `.claude/hooks/nexus-prompt-gate.py` | file + content | **Yes (Commit 1)** |
| `.claude/hooks/soki-tool-gate.py` | `.claude/hooks/nexus-tool-gate.py` | file + content | **Yes (Commit 1)** |
| `.claude/hooks/soki-exit-gate.py` | `.claude/hooks/nexus-exit-gate.py` | file + content | **Yes (Commit 1)** |
| `.soki/` | `.nexus/` | directory | **Yes (Commit 1)** |
| `.soki/README.md` | `.nexus/README.md` | file + body rewrite | **Yes (Commit 1)** |
| `.soki/state.json` | — (deleted) | ephemeral state | **Yes (Commit 1)** |
| `.claude/settings.json` command paths (×5) | `…/nexus-*.py` | JSON edit | **Yes (Commit 1)** |
| `.claude/settings.json` statusMessages (×5) | `Nexus …` | JSON edit | **Yes (Commit 1)** |
| `.gitignore` pattern + comment | `.nexus/state.json` + `# Nexus …` | file edit | **Yes (Commit 1)** |
| `.claude/hooks/__pycache__/` | — (purged) | directory delete | **Yes (Commit 1)** |
| `SOKI_INSTALLATION_GUIDE.md` | `NEXUS_INSTALLATION_GUIDE.md` | file + body rewrite | No (Commit 3 OK) |
| `docs/soki-implementation-report.md` | `docs/nexus-implementation-report.md` | file + partial body rewrite | No (Commit 3 OK; CLAUDE.md pointer updated in Commit 2 — **verify pointer matches after Commit 3 lands**) |

## B. Active Docs Update Table

| File | Required Update | Historical Content Allowed? |
|---|---|---|
| `CLAUDE.md` | Path + filename updates; fix preexisting `.sh` → `.py` bug on lines 27–30. | No |
| `README.md` | Title; 7 × `.soki/` → `.nexus/`; file-tree hook filenames; install + checklist. | No |
| `knowledge/architecture/architecture--system--overall-structure.md` | Tag + title + all hook-path + `.soki/` refs; bump `updated:`. | No |
| `knowledge/index/index--system--project-navigation.md` | Line 15 drop `(formerly SOKI)`; line 61 + lines 63–66; bump `updated:`. | No |
| `knowledge/invariants/invariant--system--lifecycle-gates.md` | Tag + lines 33–36; bump `updated:`. | No |
| `knowledge/glossary/glossary--system--terminology.md` | Move `SOKI` row from Legacy Aliases → Retired Terms; remove enumeration of retained-in locations; bump `updated:`. | No (row itself becomes a historical entry, but the table it lives in is active) |
| `.claude/skills/project-ingest/SKILL.md` | Line 11 drop `(formerly SOKI)`. | No |
| `NEXUS_INSTALLATION_GUIDE.md` (renamed) | Title; 4 × `.soki/` → `.nexus/`; drop transitional forms. | No |
| `docs/nexus-implementation-report.md` (renamed) | Rewrite §4, §5, §8; append §9 migration record. §1–§3, §6, §7 = historical narrative. | **Yes, §1–§3 + §6 + §7 remain verbatim.** |
| `knowledge/decisions/adr--system--rename-soki-to-nexus.md` | OPTIONAL: one dated line in Phase 2 section. | **Yes — filename + body are the ADR.** |
| `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` | OPTIONAL: header prose only. | **Yes — verbatim body preserved.** |

## C. Residual SOKI Allowlist

After Phase 2, `soki`/`SOKI`/`.soki` occurrences are **only** permitted in these locations:

| Location | Why Allowed After Phase 2 |
|---|---|
| `docs/COMM.log` | Conversation log. Rewriting falsifies history. |
| `prompt_soki_hooks_and_review.md` | Historical task prompt used to build the hooks. Filename is itself a historical marker. |
| `knowledge/decisions/adr--system--rename-soki-to-nexus.md` | ADR recording the rename decision. Filename slug `rename-soki-to-nexus` is semantic. |
| `knowledge/decisions/decision--system--advisory-bootstrap-legacy.md` | Preserved verbatim historical doc describing the pre-Nexus regime. |
| `knowledge/glossary/glossary--system--terminology.md` — "Retired Terms" row for `SOKI` | Explicit historical record: names the retired alias. |
| `docs/nexus-implementation-report.md` (renamed) — historical narrative sections (§1–§3, §6, §7) | These sections describe past state at the time of writing. Active sections (§4, §5, §8) must be Nexus-clean. |
| `legacy-kb/**` | Declared deprecated in `CLAUDE.md`. Out of scope. |

Any occurrence outside this allowlist is a Phase 2 defect.

---

## Notes and Uncertainties

- `VERIFY BEFORE EXECUTION`: after Commit 3, re-check that `CLAUDE.md` line ~60 points at `docs/nexus-implementation-report.md` (updated in Commit 2) and that the file now exists at that path. If the Commit 2 doc edit was skipped, Commit 3 will leave a broken pointer.
- `VERIFY BEFORE EXECUTION`: the ADR `knowledge/decisions/adr--system--rename-soki-to-nexus.md` has malformed YAML frontmatter (bulleted `tags:`). This is a preexisting issue — not fixed by this runbook. Operator may fix in a separate commit.
- `VERIFY BEFORE EXECUTION`: `legacy-kb/` was not scanned for `soki` references by this runbook's author. If it contains them, they are out of scope (deprecated bundle), but confirm with `grep -rni soki legacy-kb/ | head` and accept all hits as historical.
- `VERIFY BEFORE EXECUTION`: hooks must be reloaded in any live Claude Code session via `/hooks` after Commit 1 lands. Sessions opened before Commit 1 will continue to reference old paths in their in-memory hook config until reload or restart.
- Executable bits: `git` preserves the `+x` bit across `mv`. If the repo is checked out via an archive or on a filesystem that drops the bit, re-run `chmod +x .claude/hooks/nexus-*.py` before §7.6.
