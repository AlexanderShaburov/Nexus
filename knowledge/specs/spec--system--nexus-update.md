---
type: spec
scope: system
status: approved
created: 2026-09-22
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
theme: nexus-self-update
governs: [nexus.version, nexus.manifest.json, nexus.py, tools/nexus-update.py, .claude/hooks/nexus-update-check.py, .nexus/installed.json, .nexus/update-check.json, .nexus/unlock.txt]
tags: [spec, self-update, manifest, baseline, three-way, cli]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — `scope: system` and the visibility class decide which vault documents Nexus owns.
  - [Knowledge Visibility Specification](spec--system--knowledge-visibility.md) — the fallback mapping is applied verbatim when `knowledge_visibility` is absent.
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — `sessions/`, `business/` and `feedback/` are project directories and are never owned.
- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2d and §3 describe the files this spec governs.
  - [Plan: Nexus self-update](../plans/plan--system--nexus-self-update.md) — design origin (development class).
  - [Context Decision Gate Specification](spec--system--context-decision-gate.md) — the core freeze (§6) runs in the same PreToolUse hook, before the decision check.
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — updating the runtime rewrites the hooks that enforce the gates; hence "never automatic".

---

# Nexus Update Specification

## Purpose

Define how a host project learns that a newer Nexus exists, sees what would change, and adopts it, without touching anything the project owns. This document is the behavioural contract for `tools/nexus-update.py`, for the core freeze in `nexus-tool-gate.py` and for the notifier `nexus-update-check.py`. Every section is realized; `--selftest` and the implementation report's piped-JSON rows prove it.

---

## 1. Version identity

- `nexus.version` at the template root holds one semver line and is the only source of the version number. Template-only.
- A release is a git tag `v<semver>` on the commit whose `nexus.version` carries that number. The updater's default target is the **highest `v*` tag**; a branch or commit is used only when passed explicitly (`--ref`).
- A host records its installed version in `.nexus/installed.json` (§3). Comparison is semver; a target older than the installed version is refused unless `--allow-downgrade`.

---

## 2. Ownership manifest

`nexus.manifest.json` at the template root lists every path Nexus owns. It is **generated** (`manifest generate`), never hand-edited, and `manifest verify` MUST report it in sync with the tree before a release is tagged.

### 2.1 Generation rules (in order)

1. `.claude/hooks/*.py`, `tools/*.py`, every file under `.claude/skills/` → `replace`; `.py` and `.sh` files record `mode: 755` when executable in the template.
2. `knowledge/**/*.md` outside `sessions/`, `business/`, `feedback/` with `scope: system` and visibility class **binding** (explicit or by fallback) → `replace`; the navigation index → `index-entries`. Historical and development documents are not delivered. The generator carries an explicit exclusion list for template history that is binding by frontmatter (currently the rename ADR).
3. `knowledge/.obsidian/{app,appearance,core-plugins,graph}.json` → `create-if-absent`.
4. Fixed entries: `CLAUDE.md` → `sections` (every H2 heading of the template's `CLAUDE.md` except "What this repository is"); `.claude/settings.json` → `hooks-merge`; `.gitignore` → `ensure-lines` with the Nexus runtime patterns; `.nexus/README.md` → `create-if-absent`; `docs/nexus-implementation-report.md` → `replace`.
5. Never delivered: `patches/`, `legacy-kb/`, `dist/`, `docs/` (except the report), `README.md`, `nexus_approach.md`, `nexus.version`, `nexus.manifest.json`.

Any path matching `never_touch` is dropped even if a rule selects it.

### 2.2 Strategies and units

A **unit** is the thing compared and, later, written. Whole-file strategies have one unit whose id is the path; the others have one unit per key, id `path#key`.

| Strategy | Unit | Key | Content hashed |
|---|---|---|---|
| `replace` | the file | — | raw bytes |
| `sections` | one H2 section of `CLAUDE.md` | heading line | heading through the line before the next H2 (code fences do not start sections), normalized |
| `index-entries` | one entry line of the navigation index: a bullet whose **leading** element is a Markdown link, i.e. the dash is followed directly by the bracketed title and its target | that link's target, as written | the line, normalized. Bullets that only mention a document later in the line are prose, not units |
| `hooks-merge` | one hook entry of `.claude/settings.json` | `<event>/<nexus-*.py basename>` | canonical JSON of `{matcher, hook}` |
| `ensure-lines` | one line of `.gitignore` | the line | presence only |
| `create-if-absent` | the file | — | presence only |

Normalization for line-level units: CRLF → LF, trailing whitespace per line removed, trailing blank lines removed. Whole files are hashed as-is.

A `sections` heading found twice, an index link target found twice, a hook registered twice, or a `settings.json` that is not valid JSON makes that path **refused**: it is reported and never written.

### 2.3 `never_touch`

`.nexus/state*.json`, `.nexus/session-theme.txt`, `.nexus/session-file.txt`, `.nexus/installed.json`, `.nexus/update-check.json`, `.nexus/unlock.txt`, `.claude/settings.local.json`, `knowledge/sessions/**`, `knowledge/business/**`, `knowledge/feedback/**`. Invisible to every subcommand except `status`, which prints the list.

---

## 3. Install baseline

`.nexus/installed.json` in a host: `baseline_version`, `nexus_version`, `installed_at`, `upstream {url, ref, commit}`, `origin` (`baseline` | `install` | `update`), and `units`: one record per compared unit with `strategy`, `sha256` of the content **as delivered upstream**, optional `mode`, optional `customized_at_baseline: true`.

Rules:

- Written only by `baseline` and `apply` (*realized*; a future `install` is the same engine). Atomic write (temp + rename).
- **Committed** by the host. It is shared repository state, not session state.
- `baseline` never modifies any other file. A unit whose local content differs from upstream is recorded with the **upstream** SHA and `customized_at_baseline`, so the first `plan` reports it as `customized`, never as a clean update. Units absent locally are not recorded.
- `baseline --guess` scores every `v*` tag and the last 50 commits of `main` by identical units and picks the best; the scores are printed so the operator can confirm.

---

## 4. Upstream access

- `--upstream` accepts a git URL or a local directory. A directory is read as a working tree (or as `--ref` inside it); a URL is cloned **bare** into `${NEXUS_UPSTREAM_CACHE:-${XDG_CACHE_HOME:-~/.cache}/nexus}/template` and refreshed with `git fetch --tags --prune`. One cache serves every project on the machine. A second URL gets its own directory.
- Files are read with `git show <commit>:<path>`; nothing is checked out into the host.
- Every git call runs with `GIT_TERMINAL_PROMPT=0` and a timeout, so no subcommand can hang on a credential prompt. `--offline` uses the cache without fetching. An unreachable upstream is exit 3 with the reason; it never leaves a partial cache behind.
- Once a baseline exists, `--upstream` defaults to the URL recorded in it.

---

## 5. Three-way comparison (`plan`, *realized*)

For every unit of the **target** manifest, with B = baseline SHA, L = local SHA, U = upstream SHA:

| B | L | U | Class | `apply` will |
|---|---|---|---|---|
| present | = B | = B | `unchanged` | nothing |
| present | = B | ≠ B | `update` | write U, record U |
| present | ≠ B | = B | `customized` | nothing; listed |
| present | ≠ B | = L | `converged` | record U |
| present | ≠ B | ≠ B, ≠ L | `conflict` | nothing; **blocking** |
| present | absent | present | `removed-locally` | nothing (`--restore` recreates) |
| present | any | absent | `obsolete` | nothing; never deleted automatically |
| absent | absent | present | `add` | write U, record U |
| absent | present | = L | `adopt` | record U |
| absent | present | ≠ L | `unbaselined` | nothing; **blocking** |

Plus `mode-drift` (a `replace` unit whose executable bit differs from the manifest) and `refused` (§2.2, **blocking**). `create-if-absent` and `ensure-lines` units appear only as `add` when missing. Units baselined under a path the target manifest no longer lists are `obsolete`.

`plan` writes nothing. Exit 0 when no blocking rows, 1 otherwise. `plan --diff <path>` prints the unified diff of that path's units, local against upstream. `plan --json` emits every row with all three SHAs.

---

## 6. Core freeze in hosts (*realized*)

Every unit with strategy `replace` in `installed.json` is Nexus core. `nexus-tool-gate.py` denies `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on a core path unless the path is listed in `.nexus/unlock.txt` (operator-written, one relative path per line, `#` comments allowed). The check runs after the bootstrap gate and **before** the Context Decision check, so a denied core edit never consumes the turn's decision. The denial names the file, the installed version, the feedback directory (`knowledge/feedback/`) as the intended route, and the unlock file as the escape hatch. The freeze is inactive when `installed.json` is absent, so it never applies in the template. Bash writes are not caught; `status` and `plan` remain the safety net. Recognition lives in `core_freeze_reason` in `_nexus_common.py`; `status` prints the unlock list.

---

## 7. `check` and the SessionStart notifier (*realized*)

`check` resolves the target ref, reads its version, writes `.nexus/update-check.json` (`checked_at`, `status` ok|unreachable|no-tags, `upstream_version`, `upstream_ref`, `upstream_commit`, `error`, `via` cli|hook) and prints one of: newer available, up to date, or older. It always records the attempt, including failures, so the notifier can throttle on it. Exit 0 on a completed comparison, 3 when upstream is unreachable.

`.claude/hooks/nexus-update-check.py` is a **non-enforcing** hook registered on `SessionStart` only (not `PreCompact`), after `nexus-bootstrap.py`. Its whole contract:

1. No `.nexus/installed.json`, or one without a version or upstream URL → exit 0, no output about updates. The freeze and the update notice both switch on with the baseline, so the template never sees either. In the template itself (no baseline, `nexus.manifest.json` present) the hook instead reports the feedback mailbox, per `spec--system--feedback-channel.md` §4.
2. `.nexus/update-check.json` younger than 24 h → reused; no network.
3. Otherwise exactly one network call, `git ls-remote --tags <upstream url>`, with a 5 s timeout and `GIT_TERMINAL_PROMPT=0`: no fetch, no clone, no credential prompt. The highest `v*` tag gives the version; the record is written with `status` `ok`, `no-tags` or `unreachable` and `via: hook`. A failure therefore keeps the next 24 h quiet.
4. Output only when the recorded upstream version is **newer** than the installed one, and then exactly one line of `additionalContext`: `Nexus <new> is available upstream (<tag>); this project has <old>. Run python3 tools/nexus-update.py plan to see what would change. Nothing has been applied.`

It exits 0 on every path, swallows its own exceptions, and writes nothing but the record. `status` prints the record. Proven by piping JSON (implementation report B18–B20): silent without a baseline, when up to date, when throttled, when unreachable, when upstream has no tags and when the baseline is corrupt; one line when a `v9.9.9` tag exists upstream; template unaffected.

---

## 8. `apply` (*realized*)

Dry-run by default; `--apply` mutates. It computes the §5 table, turns the `update` and `add` rows (plus `mode-drift`, and any `customized` / `conflict` / `removed-locally` row whose path was named with `--restore`) into one write per file, and:

- refuses with exit 6 when `.nexus/state.json` changed in the last 60 s, unless `--in-session` (a Claude Code session looks live and `apply` rewrites the hooks that govern it);
- refuses a downgrade unless `--allow-downgrade`;
- copies every file it will modify, and the old `installed.json`, to `.nexus/backups/update-<version>-<timestamp>/` (or `--backup-dir`) before the first write;
- writes in group order `repo, runtime, vault-config, vault, instructions, tools, hooks`, every file via temp + rename, executable bits from the manifest; the hooks group is last and the run ends with the instruction to run `/hooks` when it was touched;
- per strategy: `replace` and `create-if-absent` write the upstream bytes; `sections` replaces each listed H2 section in place (a section new upstream is appended at EOF; a heading the host renamed is `removed-locally` and left alone); `index-entries` rewrites owned lines in place and inserts new ones after the last owned line of the same H2 section, else at the end of that section, else in a new section at EOF; `hooks-merge` removes the host's copy of each listed `nexus-*` entry and re-adds the upstream entry into the group with the same matcher (or a new group), keeping foreign entries and their order; `ensure-lines` appends missing lines once under a `# Nexus runtime` comment;
- rewrites `installed.json` with `origin: update`: `update`, `add`, `converged`, `adopt` and restored units get the upstream SHA, `obsolete` units are dropped, `customized`, `conflict` and `removed-locally` units keep their old baseline;
- then validates: `validate-vault.py` and its `--selftest`, every hook compiles, `settings.json` parses and registers only existing hooks. A failure is exit 5 with the files left in place and the backup path printed.

Blocking rows are left alone and the run exits 1; everything else is applied. When nothing needs writing the run prints so, writes nothing (no backup, no baseline rewrite) and exits 0 or 1 by the blocking rows. Re-running after success is therefore a no-op.

---

## 8a. `install`, `up` and the bootstrap (*realized*)

The same engine serves installation and retrofit, so a host is never populated by hand-copying:

- **`install`**: `apply` against an **empty baseline**. Every manifest unit is `add` (or `adopt` when identical content already exists, `unbaselined` when different content does). Two strategies behave specially when the local file is absent: `sections` writes a project stub (`# CLAUDE.md`, an explanatory sentence, an empty `## What this repository is`) followed by the owned sections, never the template's own project text; `index-entries` writes the template's index minus bullet lines that link to documents Nexus does not deliver. `hooks-merge` on an absent file writes the upstream file wholesale. The baseline is written with `origin: install`. Refuses (exit 2) where `.claude/hooks/nexus-bootstrap.py` already exists unless `--force`. Undelivered classes (`plans/`, `sessions/`, `feedback/`, history) never appear in the host.
- **`up`**: one command for any directory. No Nexus → `install`. Nexus without `installed.json` → **retrofit**: `baseline --guess` over every `v*` tag and recent `main` commits, the baseline written (`--apply` only), then `apply`; units that differ from the guessed release are `customized` and left alone. Baseline present → `apply`. All three are dry-run unless `--apply`.
- **Clean-tree guard**: with `--apply`, `install` and `up` refuse when `git status --porcelain` (tracked files) is non-empty, so the change lands as one commit; `--allow-dirty` overrides. The live-session guard of §8 applies as well.
- **What the tooling cannot do** is printed at the end of an install: run `/hooks` inside Claude Code, run `/project-ingest` for an existing project, describe the project in `CLAUDE.md`.
- **`nexus.py`** at the template root is the one-file bootstrap for a directory that has no updater yet: it ensures `git`, clones or fetches the cache, selects the highest `v*` tag (or `--ref`), extracts `tools/nexus-update.py` from that tag into a temporary file and runs it with `up` and all remaining arguments. It refuses a tag whose updater predates `up`. A local checkout may be given as `--upstream` (its working tree, or `--ref` inside it). Template-only; stdlib only.
- **Validation of undelivered links**: because `plans/` and `sessions/` are not shipped, `validate-vault.py` reports a dangling link into either as a **warning** (`LK002`), not an error; every other broken link stays `LK001`. Post-install validation therefore passes in a host that received binding documents citing template plans.

## 9. Exit codes

| Code | Meaning |
|---|---|
| 0 | success, dry-run, or up to date |
| 1 | findings reported: conflicts, unbaselined or refused units; or a refused rewrite |
| 2 | target does not look like a Nexus project |
| 3 | upstream unreachable, ref not found, or manifest/version missing there |
| 4 | internal error |
| 5 | manifest out of sync / post-apply validation failed |
| 6 | no baseline |

---

## 10. Selftest

`tools/nexus-update.py --selftest` MUST pass before a release is tagged. It builds a fixture template, proves every generation rule (T1), every extractor including refusal cases (T2), `manifest verify` (T3), `baseline` and `status` (T4), reading from a git ref (T5), every row of §5 against a fixture 1.1.0 release (T7), the cache clone, ref selection, `--guess`, `check` and `plan` through the CLI including the unreachable path (T8), `apply` on that host: dry-run writes nothing, clean rows written, blocking and customized rows untouched, backups taken, baseline recorded per §8, second run a no-op, `--restore` per path, the live-session guard, and the `hooks-merge` writer (T9), the feedback mailbox end to end (T10), `install` into an empty directory and into a project with its own `CLAUDE.md` / `settings.json` / `.gitignore`, the clean-tree guard, the retrofit of a `v1.0.0` archive with a customization, `up` as a no-op afterwards, and `nexus.py` from the cache and from a local checkout (T11), and finally that the real template's manifest is in sync (T6). The core freeze is proven by piping PreToolUse JSON into the gate (implementation report, rows B15–B17).
