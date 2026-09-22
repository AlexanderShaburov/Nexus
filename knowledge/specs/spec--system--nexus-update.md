---
type: spec
scope: system
status: review
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
theme: nexus-self-update
governs: [nexus.version, nexus.manifest.json, tools/nexus-update.py, .nexus/installed.json, .nexus/update-check.json, .nexus/unlock.txt]
tags: [spec, self-update, manifest, baseline, three-way, cli]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — `scope: system` and the visibility class decide which vault documents Nexus owns.
  - [Knowledge Visibility Specification](spec--system--knowledge-visibility.md) — the fallback mapping is applied verbatim when `knowledge_visibility` is absent.
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — `sessions/`, `business/` and `feedback/` are project directories and are never owned.
- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2d and §3 describe the files this spec governs.
  - [Plan: Nexus self-update](../plans/plan--system--nexus-self-update.md) — design origin; this spec is promoted to binding when `apply` (Phase 3) lands.
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — updating the runtime rewrites the hooks that enforce the gates; hence "never automatic".

---

# Nexus Update Specification

## Purpose

Define how a host project learns that a newer Nexus exists, sees what would change, and adopts it, without touching anything the project owns. This document is the behavioural contract for `tools/nexus-update.py`. It is in **review** until the `apply` subcommand exists; the subcommands marked *realized* are implemented and covered by `--selftest`, the ones marked *pending* are specified here so the realized ones are built toward them.

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
| `index-entries` | one bullet line of the navigation index | first Markdown link target, as written | the line, normalized |
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

- Written only by `baseline` (*realized*) and, later, `apply`/`install` (*pending*). Atomic write (temp + rename).
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

## 6. Core freeze in hosts (*pending*, Phase 3)

Every unit with strategy `replace` in `installed.json` is Nexus core. The tool gate denies `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on a core path unless the path is listed in `.nexus/unlock.txt` (operator-written, one relative path per line). The freeze is inactive when `installed.json` is absent, so it never applies in the template. Bash writes are not caught; the three-way table remains the safety net.

---

## 7. `check` (*realized*) and the SessionStart notifier (*pending*, Phase 4)

`check` resolves the target ref, reads its version, writes `.nexus/update-check.json` (`checked_at`, `status` ok|unreachable, `upstream_version`, `upstream_ref`, `upstream_commit`, `error`) and prints one of: newer available, up to date, or older. It always records the attempt, including failures, so the notifier can throttle on it. Exit 0 on a completed comparison, 3 when upstream is unreachable.

The notifier hook will call the same logic with a 5 s budget, once per 24 h, and emit at most one line of context; it never blocks a session and never fetches objects.

---

## 8. `apply` (*pending*, Phase 3)

Dry-run by default; `--apply` mutates. Backups under `.nexus/backups/<version>-<timestamp>/` before the first write. Groups are written in the order `repo, runtime, vault-config, vault, instructions, tools, hooks`; every file via temp + rename; hooks last, followed by the instruction to run `/hooks`. Refuses when the session state file changed in the last 60 s unless `--in-session`. After writing: `installed.json` is rewritten with `origin: update`, then `validate-vault.py`, `validate-vault.py --selftest` and the static checks of the implementation report run; a failure is exit 5 with the backup path printed. Blocking rows are left alone and the run exits 1; everything else is applied. Re-running after success is a no-op.

---

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

`tools/nexus-update.py --selftest` MUST pass before a release is tagged. It builds a fixture template, proves every generation rule (T1), every extractor including refusal cases (T2), `manifest verify` (T3), `baseline` and `status` (T4), reading from a git ref (T5), every row of §5 against a fixture 1.1.0 release (T7), the cache clone, ref selection, `--guess`, `check` and `plan` through the CLI including the unreachable path (T8), and finally that the real template's manifest is in sync (T6).
