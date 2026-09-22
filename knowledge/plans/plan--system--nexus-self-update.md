---
type: plan
scope: system
status: in-progress
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
theme: nexus-self-update
tags: [plan, self-update, upgrade, manifest, baseline, three-way-merge, hooks]
---

## Relations

- depends_on:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — the components this plan makes updatable, and the runtime directory it extends.
  - [Knowledge Vault Specification](../specs/spec--system--knowledge-vault.md) — directory roles decide which vault paths Nexus owns and which belong to the host project.
  - [Document Frontmatter Specification](../specs/spec--system--document-frontmatter.md) — `scope: system` is the primary ownership signal for vault documents.
  - [Knowledge Visibility Specification](../specs/spec--system--knowledge-visibility.md) — this plan is a development-class document and must not be read as binding.
- relates_to:
  - [Plan: Nexus feedback channel](plan--system--nexus-feedback-channel.md) — the return path for improvements that hosts may no longer make in place once the core is frozen (§7.2a); shares the cache directory and the CLI.
  - [Plan: Context Decision claim via tool call](plan--system--context-decision-claim.md) — the previous change to the runtime; its rollout order (hooks last, test by piping JSON) is reused here.
  - [Runbook: Development Visibility Migration](../runbooks/runbook--system--development-visibility-migration.md) — the hand-written migration the patch bundle mechanism was built for; the updater generalizes that bundle.

---

# Plan: Nexus self-update

Plan status: **in_progress** (approved by the operator on 2026-09-22 with the decisions in §12; Phases 1 and 2 implemented the same day, see §10. Phases 3–5 not started. `v1.0.0` is tagged on `ac83f1c` and pushed; it is the first release the updater can target.)

The frontmatter `status` is `draft` because the closed enum in `spec--system--document-frontmatter.md` has no `proposed` value; the plan-level status lives in this line, as in `plan--system--context-decision-claim.md`.

---

## 1. Goal

A project with Nexus installed can learn that a newer Nexus exists upstream, see exactly what would change, and adopt it with one command, without hand-built patch bundles and without touching anything the project owns.

The mechanism is a **three-way comparison** (baseline as delivered / local now / upstream target) over an **ownership manifest**, driven by a stdlib-only CLI, with an optional, silent, throttled **SessionStart notifier**. Application is never automatic.

---

## 2. Where the brief diverges from the repository

Checked on 2026-09-22 against `main` at `28ab085`. Each item is a fact about the repository, and the design below follows the repository, not the brief.

| # | Brief says | Repository shows | Consequence |
|---|---|---|---|
| D1 | §1: `tools/` holds `validate-vault.py` and `build-patch-zip.sh` | also `tools/nexus-decide.py` (the Context Decision claim, added 2026-09-22) | `tools/*.py` is a Nexus-owned group of three, and the updater must update the claim script the tool gate depends on |
| D2 | §1: install copies `.claude/`, `.nexus/`, `knowledge/`, `CLAUDE.md` | `docs/NEXUS_INSTALLATION_GUIDE.md` Part 1 also copies `tools/` and `docs/nexus-implementation-report.md`; `.claude/` includes `.claude/skills/project-ingest/SKILL.md` | the ownership manifest covers six delivery roots, not four |
| D3 | §6.2: `scope: system` frontmatter identifies almost all owned vault files | true for 22 authored documents, but the session writer also emits `scope: system` on some archives (`session--nexus-self-update--2026-09-22--07fc5fdc.md`) and `scope: general` on others; `knowledge/.obsidian/*.json` has no frontmatter | ownership is decided by directory rule first and `scope:` second; `knowledge/sessions/` is excluded by directory regardless of scope |
| D4 | §6.2 / §7.7: manifest is `nexus.manifest.yaml`, stdlib only, reuse the validator's YAML subset | the validator's parser accepts scalars and flat lists only, which cannot express one strategy per path with per-path options | the manifest is **JSON** (`nexus.manifest.json`), parsed with `json` from the stdlib; see §3 |
| D5 | §8.4: plan document with `status: proposed` | `status` enum is closed: `draft`, `in-progress`, `review`, `approved`, `deprecated` | this document uses `status: draft` and carries "Plan status: proposed" in the body |
| D6 | §9.1 asks whether a remote exists | `origin` is `https://github.com/AlexanderShaburov/Nexus.git`; `git ls-remote` succeeds from this environment without a prompt; local `main` is one commit ahead of `origin/main` (`28ab085` unpushed); **no tags exist** | tracking a tag is impossible until a first release tag is created (§5, §12 Q2) |
| D7 | §10: the port must land first | landed: `tools/validate-vault.py` exists (commit `41e033c`), branch `port/nexus-hardening-2026-09-22` is merged | precondition satisfied |
| D8 | §0: `Liquid_Nexus` is the first retrofit target | `/Users/shaburov/Documents/Programming/PROJECTS/Liquid_Nexus` is not reachable from this environment; no sibling project with `.claude/hooks/nexus-bootstrap.py` is visible | the retrofit path (§9) is designed blind and must be rehearsed on a throwaway copy of the template before Liquid_Nexus |
| D9 | §3.2: `CLAUDE.md` is half Nexus, half project in hosts | the **template's own** `CLAUDE.md` is already mixed: "What this repository is" describes the template repository, the other five H2 sections are the protocol | the delivered `CLAUDE.md` must be owned per section, never as a whole; §3.3 |
| D10 | §6.4: 15 s hook timeout | confirmed: every hook in `.claude/settings.json` has `"timeout": 15` | the notifier budgets 6 s worst case (§6) |
| D11 | §4: the patch bundle exists | confirmed, plus `tools/build-patch-zip.sh` and `dist/` (gitignored) | bundles stay for one-off migrations with operator prompts (§12 Q4); the updater does not replace them in Phase 1 |

Not a divergence but worth recording: `.nexus/` in the template contains a stray `state 2.json` (macOS duplicate, gitignored by the glob). The manifest's never-touch rule covers `.nexus/state*.json`.

---

## 3. Ownership manifest

### 3.1 File and location

`nexus.manifest.json` at the template root, next to `nexus.version`. JSON because the only stdlib parser the project accepts is `json`; the frontmatter YAML subset cannot hold nested per-path options (D4). The file is generated by `tools/nexus-update.py manifest generate` and checked by `--selftest`, never hand-edited.

`nexus.version` is one line of semver and the single source of the version number. The generator copies it into the manifest; the selftest fails if they differ.

Neither file is delivered to hosts. A host records what it has in `.nexus/installed.json` (§4).

### 3.2 Shape

```json
{
  "manifest_version": 1,
  "nexus_version": "1.0.0",
  "generated_from": "<commit sha>",
  "generated_at": "2026-09-22",
  "entries": [
    {"path": ".claude/hooks/_nexus_common.py",      "strategy": "replace", "group": "hooks", "mode": "755"},
    {"path": ".claude/hooks/nexus-bootstrap.py",    "strategy": "replace", "group": "hooks", "mode": "755"},
    {"path": "tools/nexus-update.py",               "strategy": "replace", "group": "tools", "mode": "755"},
    {"path": "knowledge/specs/spec--system--exit-gate.md", "strategy": "replace", "group": "vault"},
    {"path": "CLAUDE.md",                           "strategy": "sections", "group": "instructions",
     "sections": ["## How work proceeds here", "## Mandatory Startup Reading Set", "## Read Priority (when consulting the vault)",
                  "## Knowledge Visibility (review / gap-analysis)", "## Writing rules (if you modify the vault)", "## When editing hooks"]},
    {"path": "knowledge/index/index--system--project-navigation.md", "strategy": "index-entries", "group": "vault"},
    {"path": ".claude/settings.json",               "strategy": "hooks-merge", "group": "hooks"},
    {"path": ".gitignore",                          "strategy": "ensure-lines", "group": "repo",
     "lines": [".nexus/state*.json", ".nexus/backups/", ".nexus/update-check.json"]},
    {"path": ".nexus/README.md",                    "strategy": "create-if-absent", "group": "runtime"},
    {"path": "knowledge/.obsidian/app.json",        "strategy": "create-if-absent", "group": "vault-config"}
  ],
  "never_touch": [".nexus/state*.json", ".nexus/session-theme.txt", ".nexus/session-file.txt",
                  ".nexus/installed.json", ".nexus/update-check.json", ".nexus/unlock.txt",
                  ".claude/settings.local.json",
                  "knowledge/sessions/**", "knowledge/business/**", "knowledge/feedback/**"]
}
```

`group` orders application (§7.4) and lets `plan` summarize by kind. `mode` restores the executable bit the installation guide otherwise asks for by hand.

### 3.3 Strategies

| Strategy | Unit of ownership | Used for | Behaviour on update |
|---|---|---|---|
| `replace` | whole file | hooks, `tools/*.py`, `.claude/skills/project-ingest/SKILL.md`, every `scope: system` vault document outside `index/` and `sessions/`, `docs/nexus-implementation-report.md` | three-way on the file's SHA-256; clean update writes the upstream bytes via temp file + rename |
| `sections` | one H2 section: the heading line through the line before the next H2 (or EOF) | `CLAUDE.md` | each listed section is its own three-way unit, keyed by heading text; sections not listed are project-owned and never read. A listed heading absent locally → **added at the end** of the file if the section is new upstream, otherwise reported as `removed-locally` and left alone. A heading found twice → refused, no edit |
| `index-entries` | one bullet line, keyed by its Markdown link target | `knowledge/index/index--system--project-navigation.md` | a line is owned if its first link target is an owned path. Owned lines are three-way units; project lines and prose are untouched. New upstream lines are inserted after the nearest preceding owned line of the same H2 section, else appended to that section, else the section is created at EOF. Duplicate key → refused |
| `hooks-merge` | one hook command entry | `.claude/settings.json` | an entry is owned if its `command` ends with `/.claude/hooks/nexus-*.py`. For each event: owned entries are made equal to upstream (matcher, timeout, statusMessage); foreign entries and their order are preserved; other top-level keys are preserved. Written with `json.dumps(indent=2)`; if the file is not valid JSON → refused |
| `ensure-lines` | one line | `.gitignore` | each listed line is present exactly once; nothing is ever removed; missing lines are appended under a `# Nexus` comment |
| `create-if-absent` | whole file | `.nexus/README.md`, `knowledge/.obsidian/{app,appearance,core-plugins,graph}.json` | written only when missing; never compared, never reported |
| `never-touch` | pattern | runtime state, session archives, business documents, local settings | invisible to `plan` and `apply`; `status` lists them once so the boundary is explicit |

### 3.4 Generation rules (template side)

`manifest generate` walks the template working tree and applies, in order:

1. `.claude/hooks/*.py`, `tools/*.py`, `.claude/skills/**` → `replace`, mode `755` for `*.py` and `*.sh`.
2. `knowledge/**/*.md` outside `sessions/`, `business/` and `feedback/` whose frontmatter `scope` is `system` **and** whose visibility class (explicit `knowledge_visibility`, else the fallback mapping of `spec--system--knowledge-visibility.md`) is `binding` → `replace`, except `knowledge/index/index--system--project-navigation.md` → `index-entries`. Historical system documents are template history and are not delivered (operator decision, §12 Q8); development documents (the template's own plans) are not delivered either, because a host reviews its own design tracks, not the template's. One binding document is excluded by name in the generator, `decisions/adr--system--rename-soki-to-nexus.md`: it is a rename record kept for its inbound references, binding by frontmatter but history by content. Demoting it to `historical` would make the exclusion redundant; that is a KB judgement left to the operator.
3. `knowledge/.obsidian/*.json` except `workspace*.json` → `create-if-absent`.
4. Fixed entries: `CLAUDE.md` (`sections`, headings read from the template's own `CLAUDE.md`: every H2 except "What this repository is"), `.claude/settings.json` (`hooks-merge`), `.gitignore` (`ensure-lines`), `.nexus/README.md` (`create-if-absent`), `docs/nexus-implementation-report.md` (`replace`).
5. Template-only paths are excluded by rule: `patches/**`, `legacy-kb/**`, `dist/**`, `docs/NEXUS_INSTALLATION_GUIDE.md`, `docs/nexus-self-update-brief.md`, `nexus_approach.md`, `README.md`, `nexus.version`, `nexus.manifest.json`.

`manifest verify` (run by `--selftest` and by the Phase 1 acceptance test) regenerates in memory and fails on any difference, so the committed manifest cannot drift from the tree. It also asserts: every hook registered in `.claude/settings.json` has a `replace` entry; no entry path matches a `never_touch` pattern; every `sections` heading exists exactly once in the template's `CLAUDE.md`.

Consequence of rule 2 for the template today: `adr--system--rename-soki-to-nexus.md`, `decision--system--advisory-bootstrap-legacy.md` and `prompt--system--hooks-genesis.md` stay out of the manifest. A host that already has them from an earlier copy keeps them untouched (they are simply not owned). The installation guide's "copy `knowledge/`" step will be replaced by the installer (§10a), which copies only manifest entries.

---

## 4. Install baseline in the host: `.nexus/installed.json`

```json
{
  "baseline_version": 1,
  "nexus_version": "1.0.0",
  "installed_at": "2026-09-22T14:05:00",
  "upstream": {"url": "https://github.com/AlexanderShaburov/Nexus.git", "ref": "v1.0.0", "commit": "<sha>"},
  "origin": "install | update | baseline",
  "units": {
    ".claude/hooks/nexus-bootstrap.py": {"strategy": "replace", "sha256": "…"},
    "CLAUDE.md#How work proceeds here": {"strategy": "sections", "sha256": "…"},
    "knowledge/index/index--system--project-navigation.md#../specs/spec--system--exit-gate.md": {"strategy": "index-entries", "sha256": "…"},
    ".claude/settings.json#Stop/nexus-exit-gate.py": {"strategy": "hooks-merge", "sha256": "…"}
  }
}
```

- One record per **unit**, not per file, so section- and line-level strategies get their own baselines. The SHA is of the unit content as delivered (for a section: heading line plus body, trailing whitespace stripped; for a hooks-merge entry: the canonical JSON of that entry).
- Written by `apply` after a successful update, by the installer step in Phase 1, and by `baseline` (§9).
- **Committed by the host project.** Unlike `state.json`, the baseline is shared state of the repository; the `.gitignore` glob `.nexus/state*.json` does not match it, and the manifest's `never_touch` keeps the updater from rewriting it outside `apply`/`baseline`.
- `units` for `create-if-absent` and `ensure-lines` are omitted: those strategies do not compare.

---

## 5. Reaching upstream

- **Cache clone**, not a submodule: `${NEXUS_UPSTREAM_CACHE:-${XDG_CACHE_HOME:-~/.cache}/nexus/template}`, created with `git clone --no-checkout --filter=blob:none` and refreshed with `git fetch --tags --prune`. One cache serves every project on the machine; no host repository is restructured. `--upstream <path>` accepts an existing local checkout instead (used for tests, and for this template updating a copy of itself).
- **Reading files**: `git show <ref>:<path>` and `git ls-tree -r <ref>` from the cache. Nothing is checked out into the host; the manifest of the *target* ref is read the same way, so the plan always uses the manifest that belongs to the version being installed.
- **Ref selection** (§12 Q2): default is the highest `v*` semver tag; `--ref <tag|branch|sha>` overrides. Because no tag exists today (D6), Phase 1 creates `v1.0.0`; until then `--ref main` is the only working target and the CLI says so explicitly instead of guessing.
- **Version comparison** is semver on `nexus.version` at the target ref versus `installed.json`. Downgrades are refused unless `--allow-downgrade`.
- **Credentials**: `GIT_TERMINAL_PROMPT=0` on every git call so the CLI and the hook never hang on a password prompt. Every git call runs through `subprocess.run(..., timeout=…)`; CLI timeout 60 s, hook timeout 5 s.
- **Offline**: the CLI reports exit 3 with the cache's last known state; the hook stays silent (§6).

---

## 6. SessionStart notifier

A new **non-enforcing** hook, `.claude/hooks/nexus-update-check.py`, registered on `SessionStart` only (not `PreCompact`), after `nexus-bootstrap.py`. It is a separate hook so that the bootstrap hook stays pure and the notifier can be removed by deleting one registration.

Behaviour, in order, and every branch except the last is silent:

1. If `.nexus/installed.json` is absent → exit 0, no output. A project that has never been baselined is told about the updater by the installation guide, not by every session start.
2. Read `.nexus/update-check.json` (`{"checked_at", "upstream_version", "upstream_commit", "status"}`). If `checked_at` is less than **24 h** old → skip the network and go to step 5 with the cached values.
3. Run `git ls-remote --tags --heads <upstream url>` with `timeout=5`, `GIT_TERMINAL_PROMPT=0`, stdout captured. This is the only network call; it never touches the cache clone and never fetches objects. On any non-zero exit, timeout or exception → write the cache file with `"status": "unreachable"` and the current timestamp (so the next 24 h are quiet too) → exit 0, no output.
4. Pick the highest `v*` tag (or `main` if the baseline's ref is a branch); the version string comes from the tag name, so no file read is needed. Write the cache file with `"status": "ok"`.
5. If `upstream_version > installed nexus_version` → emit exactly one line of `additionalContext`:

   `Nexus 1.4.0 is available upstream; this project has 1.2.0. Run python3 tools/nexus-update.py plan to see what would change. Nothing has been applied.`

   Otherwise exit 0 with no output.

Guarantees: never blocks (exit 0 on every path, exceptions swallowed like the session writer), never writes outside `.nexus/update-check.json`, worst-case runtime is the 5 s subprocess timeout plus file I/O, inside the 15 s hook timeout (D10). `.nexus/update-check.json` is added to `.gitignore` through the `ensure-lines` entry.

Rejected: a background `git fetch` in the hook (can exceed the timeout on a slow network, and the cache clone is the CLI's concern); checking on every `UserPromptSubmit` (noise); folding the check into `nexus-bootstrap.py` (couples an optional network feature to the mandatory gate).

---

## 7. Three-way comparison

### 7.1 Decision table

For every unit named by the target manifest, with `B` = baseline SHA from `installed.json`, `L` = SHA of the unit in the host now, `U` = SHA of the unit at the target ref:

| B | L | U | Class | `apply` does |
|---|---|---|---|---|
| present | = B | = B | `unchanged` | nothing |
| present | = B | ≠ B | `update` | write U, record U as new baseline |
| present | ≠ B | = B | `customized` | nothing; listed so the operator knows |
| present | ≠ B | ≠ B, = L | `converged` | nothing; record U as new baseline (the project already made the same change) |
| present | ≠ B | ≠ B, ≠ L | `conflict` | nothing; exit 1; optionally write `<path>.nexus-upstream` next to it (§12 Q3) |
| present | absent | any | `removed-locally` | nothing; the project deleted it on purpose; `--restore` recreates it |
| absent | absent | present | `add` | write U (new upstream unit) |
| absent | present | = L | `adopt` | nothing; record L as baseline (the project already has the upstream content, typical after a manual copy) |
| absent | present | ≠ L | `unbaselined` | nothing; exit 1; the file exists locally with no baseline and differs from upstream, so it cannot be told from a customization; §9 resolves this |
| present | any | absent | `obsolete` | nothing; upstream dropped the unit; reported once; never deleted automatically (`deletes_files: false` is kept from `apply.py`); `--prune` is a possible later flag |

Comparison is byte-exact after one normalization only: trailing whitespace on each line and a single trailing newline are stripped before hashing section and line units, because editors touch those without intent. Whole-file units are hashed as-is.

### 7.2 Edge cases the table does not cover

- **Renamed upstream path**: seen as `obsolete` + `add`. Correct but noisy; the manifest may later carry `renamed_from` so the pair is reported as one move and the local customization, if any, is carried over as a conflict rather than lost.
- **A section heading renamed upstream** (`sections` strategy): same as a file rename; the old heading becomes `obsolete` and the new one `add`. The generator warns when a heading listed in the previous manifest disappears, so the release notes can say so.
- **`index-entries` when a project edited an owned line's text but not its link**: the key matches, content differs → `customized`, and an upstream change to the same line is a `conflict`. The line is never rewritten.
- **A project moved an owned index line to another section**: the key still matches; position is not part of the unit, so it is `unchanged` and stays where the project put it.
- **`hooks-merge` when a project changed a Nexus hook's timeout**: that entry is `customized`; a later upstream change to the same entry is a `conflict`, reported per entry, and the rest of the file is still updated.
- **Executable bit lost** (copy through a filesystem that drops modes): `apply` restores `mode` on every written or unchanged `replace` unit; `status` reports `mode-drift`.
- **CRLF**: units are hashed as bytes for files and after `\r\n → \n` normalization for sections and lines. A file that a project converted to CRLF wholesale is `customized`; the updater does not convert line endings.
- **The updater updating itself**: `tools/nexus-update.py` is a `replace` unit in group `tools`. The running interpreter has already loaded the module, so replacing the file mid-run is safe on POSIX; the tools group is applied before hooks so a re-run for a second phase already uses the new code.
- **Hooks under a live session** (brief §3.5): `apply` writes group `hooks` last, each file via temp + `os.replace` so no hook is ever half-written on disk, and ends with the instruction to run `/hooks`. It also refuses with exit 6 when `.nexus/state.json` was modified in the last 60 s and `--in-session` was not passed, which catches the case where the agent runs `apply` inside the session it would rewrite. The operator's intended path is a plain terminal.

### 7.2a Core freeze in hosts (operator decision, 2026-09-22)

The `conflict` row exists because a host may edit an owned unit. The operator's direction is that hosts **must not** edit the Nexus core at all: they build around it (project knowledge, project sections of `CLAUDE.md`, project entries in the index, project hooks in `settings.json`) but never inside it. Improvements to Nexus travel through the feedback channel (`plan--system--nexus-feedback-channel.md`) and come back as an update.

Mechanism, all inside existing components:

- **Core** = every unit with strategy `replace` in `.nexus/installed.json`. No second list: the baseline is the freeze list. In the template repository itself there is no `installed.json`, so the freeze never applies upstream, which is where the core is edited.
- **`nexus-tool-gate.py`** gains one rule after the bootstrap and decision checks: for `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, if `tool_input.file_path` resolves to a core path and the path is not unlocked, deny with:

  `NEXUS CORE FILE: <path> is owned by Nexus <version>. Hosts do not edit the core. Record the change as a feedback note (knowledge/feedback/) or, if it cannot wait, unlock the path in .nexus/unlock.txt.`

  The rule reads `installed.json` once per call; absent file → rule inactive.
- **`.nexus/unlock.txt`**: one relative path per line, written by the operator only, never by a hook or by `apply`; listed in `never_touch`. An unlocked path is editable and is thereafter `customized` in the three-way table, so `apply` reports it and leaves it alone. `status` prints the unlock list so it cannot be forgotten.
- **Limits stated plainly.** The gate sees a path only on the editing tools; a write through Bash (`sed`, heredoc, `git checkout`) is not caught. The three-way comparison stays as the safety net: `status` reports `customized`, `plan` reports `customized` or `conflict`, and neither overwrites. The freeze turns conflicts from a workflow into a rare, visible exception.
- **Consequence for Q3 (§12):** conflict handling is report-only, host version kept, exit 1. The `--conflict-copies` flag is dropped from the CLI surface; if hand merging is ever needed, `plan --diff <path>` prints the upstream diff.
- **One-time untangling of already-diverged hosts** (Liquid_Nexus): the retrofit (§9) lists every core unit that differs. For each, exactly one of: port the change into the template and receive it back via `apply`; or reset it with `apply --restore <path>`. The freeze is switched on by the baseline write itself, so it takes effect the moment `installed.json` exists.

Spec mirror: this rule extends the tool-gate contract in `spec--system--context-decision-gate.md`, or rather warrants its own short section in the new `spec--system--nexus-update.md` (§10), and the architecture doc's PreToolUse control flow gains one branch. `CLAUDE.md` gate 2 text mentions the freeze in one sentence.

### 7.3 Partial application

As in `apply.py`: a unit is refused (ambiguous heading, duplicate key, unparsable JSON) individually; the rest of the plan still applies. Nothing is written until the whole plan has been computed, and the backup of every touched file is taken before the first write.

### 7.4 Order of application

`repo` (`.gitignore`) → `vault-config` → `vault` → `instructions` → `tools` → `hooks`, then `installed.json`, then post-apply validation (`validate-vault.py`, `validate-vault.py --selftest`, and the S1–S3 static checks from `docs/nexus-implementation-report.md`). A validation failure leaves the files in place, keeps the backup path on screen and exits 5; the operator restores from the backup or fixes forward.

---

## 8. CLI surface: `tools/nexus-update.py`

Stdlib only; shares the frontmatter parser with `tools/validate-vault.py` by importing it, as `nexus-decide.py` shares the claim parser with `_nexus_common.py`. Delivered to hosts as part of `tools/`.

| Subcommand | Reads network | Writes | Purpose |
|---|---|---|---|
| `status` | no | nothing | installed version, upstream ref, per-unit local state against the baseline (`unchanged` / `customized` / `removed-locally` / `mode-drift`), never-touch boundary |
| `check` | yes (ls-remote only) | `.nexus/update-check.json` | "is there a newer version"; same logic as the hook, verbose |
| `plan [--ref R]` | yes (fetch into cache) | nothing in the project | the full three-way table (§7.1), grouped, with a summary count per class; `--json` for tooling |
| `apply [--ref R] --apply` | yes | project files, backup, `installed.json` | dry-run without `--apply`, exactly like `apply.py`; `--backup-dir`, `--restore <path>`, `--allow-downgrade`, `--in-session`; `plan --diff <path>` shows the upstream diff of one unit for hand merging |
| `baseline --version V [--ref R] [--guess]` | yes | `.nexus/installed.json` only | retrofit for projects installed before baselines existed (§9) |
| `manifest generate\|verify` | no | `nexus.manifest.json` (generate only) | template side; `verify` is part of `--selftest` |
| `--selftest` | no | temp dirs only | fixtures for every row of §7.1, every strategy, the notifier's silent paths, and `manifest verify` |

Exit codes extend the existing contract so scripts written for `apply.py` keep their meaning:

| Code | Meaning |
|---|---|
| 0 | success, successful dry-run, or already up to date |
| 1 | conflicts or refused units reported; everything else applied |
| 2 | target does not look like a Nexus project |
| 3 | upstream unreachable, ref not found, or target manifest missing |
| 4 | internal error |
| 5 | post-apply validation failed |
| 6 | no baseline (`installed.json` absent) or refused because a session is live |

Common flags: `--project-root` (default: cwd), `--upstream <url|path>` (default: baseline's URL, else `origin` of the template), `--ref`, `--json`, `--quiet`.

---

## 9. Migration for already-installed projects (no baseline)

Every existing host, Liquid_Nexus included, has Nexus files but no `installed.json`. Until it does, `plan` reports every unit as `unbaselined` (§7.1) and refuses to apply. The retrofit is an explicit operator step that **never modifies a project file**:

1. `python3 tools/nexus-update.py baseline --version 0.9.0 --ref <commit-or-tag>` states which upstream state the project was installed from. `--guess` instead tries every tag and the last 50 commits of `main` in the cache, picks the ref with the most byte-identical units, and prints the score so the operator can confirm.
2. For every manifest unit, the tool compares local content against the chosen ref:
   - identical → baseline SHA = that content (`origin: baseline`);
   - different → baseline SHA = the **upstream** content at the chosen ref, and the unit is marked `"customized_at_baseline": true`. The first `plan` will therefore show it as `customized` (or `conflict` if upstream moved too), never as a clean `update`. This is the conservative reading: an unexplained difference is treated as the project's work.
   - absent locally → no unit record; a later `plan` reports `add`.
3. The tool prints the inventory (identical / customized / absent counts, and the customized list) and writes `installed.json` with `"origin": "baseline"`.
4. The operator reviews the customized list. Anything that is actually stale rather than customized can be reset with `apply --restore <path>` after the baseline exists, which is the only path that overwrites a customized unit and it is per-path and explicit.
5. Commit `installed.json`.

Rehearsal order (D8): a throwaway copy of this template with a few deliberate edits first, then Liquid_Nexus, then any other host (§12 Q5). The rehearsal script and its expected output go into `docs/nexus-implementation-report.md` as section S8.

Projects installed after Phase 1 get `installed.json` from the installer step (a `baseline --version <current>` run against the template checkout they copied from), added to the installation guide as Step 4c.

---

## 10. Phases

Phase boundaries are pause points per `spec--system--knowledge-driven-task-orchestration.md`; each phase ends with a report and waits for confirmation.

| Phase | Deliverable | Files | Acceptance |
|---|---|---|---|
| 0 | this proposal | `knowledge/plans/plan--system--nexus-self-update.md` | operator review; answers to §12 |
| 1 | version + manifest + baseline | `nexus.version` (`1.0.0`), `nexus.manifest.json`, `tools/nexus-update.py` with `manifest`, `baseline`, `status` and `--selftest`; tag `v1.0.0` on `main` after pushing `28ab085`; installation guide Step 4c; `.gitignore` line | **Done 2026-09-22.** `manifest verify` clean (36 entries: 27 replace, 5 create-if-absent, 1 each of sections, index-entries, hooks-merge, ensure-lines); `baseline` on a copy of the template: 51 units, all identical; selftest T1–T6 pass; report check S8 added. `baseline --guess` deferred to Phase 2 with the cache clone, since both need ref iteration. |
| 2 | `check` and `plan` | cache clone, ref selection, three-way engine, all strategies in read mode | **Done 2026-09-22.** Bare cache clone keyed by URL, `--offline`, highest-`v*` default with `--ref` override, `baseline --guess`, `check` writing `.nexus/update-check.json`, `plan` with `--diff`, `--json`, `--verbose`, `--allow-downgrade`; every row of §7.1 has a fixture (T7) against a fixture 1.1.0 release, cache/ref/check/plan through the CLI (T8). Rehearsal on a throwaway host against the real repo via `file://`: `check` up to date at `v1.0.0`, `plan` shows the doc edits made after the baseline as `update`, the new `.gitignore` line as `add`, the unlocked spec as `customized`. `spec--system--nexus-update.md` written in review class. |
| 3 | `apply` + core freeze | backups, temp+rename writes, group order, post-apply validation, `--restore`, report-only conflicts; the core-freeze rule in `nexus-tool-gate.py`, `.nexus/unlock.txt`, spec and architecture mirror (§7.2a) | idempotency: a second `apply --apply` is a no-op with exit 0; a customized unit survives an upstream change; the S1–S5 checks pass after apply; piping JSON into the gate: Edit on a core path denied, on an unlocked path allowed, on a project path allowed, with no `installed.json` allowed |
| 4 | notifier | `.claude/hooks/nexus-update-check.py`, registration in `.claude/settings.json`, entry in the architecture doc §2d and the implementation report | piping JSON into the hook: silent without baseline, silent when cached, silent when `git` fails (simulated with a bogus URL), one line when newer; runtime under 6 s with the network cut |
| 5 | retrofit | rehearsal on a template copy, then Liquid_Nexus, then others; runbook `runbook--system--nexus-update-retrofit.md` | each host has a committed `installed.json` and a clean `plan` |

### 10a. Design requirement: the same engine installs

Operator direction (2026-09-22): the goal is the mechanism, and the current install procedure (copy six roots by hand, then run `/project-ingest`) should later become one script run inside the target folder. That is not this plan's scope, but the design must be ready for it, and it already is: with no baseline and no local files every manifest unit classifies as `add` (§7.1), so **install is `apply` on an empty project**. A later `nexus-update.py install [--ref R]` subcommand is the same engine plus the post-install steps of the guide (`chmod`, `.gitignore` lines, baseline write, `validate-vault.py --selftest`), and nothing in Phases 1–5 may assume a host was populated by hand-copying. Vault ingestion (`/project-ingest`) stays a separate, agent-driven step.

Vault writeback per phase: architecture §2d + §3 (new runtime files), a new `spec--system--nexus-update.md` (behavioural contract: strategies, decision table, exit codes, notifier guarantees) in Phase 2, a `decision--system--nexus-self-update.md` recording the alternatives in §11 when the plan is approved, and index entries for all of them.

---

## 11. Alternatives considered

- **Git submodule or subtree for the Nexus parts.** Clean provenance, but requires restructuring every host and cannot express a file owned per section (D9, brief §3.2). Rejected unless the operator wants the restructuring.
- **Keep hand-written patch bundles and add an index.** Does not solve the scaling problem; kept only for one-off migrations that need operator prompts (§12 Q4).
- **Two-way diff against upstream with a "customized" list maintained by hand.** Cheaper to build, but the list rots the moment someone forgets it, and it cannot distinguish "customized" from "stale". The baseline file costs one JSON write per apply and removes the guesswork.
- **Marker comments (`<!-- nexus:begin -->`) to delimit owned regions of `CLAUDE.md`.** Robust to heading edits, but retrofitting markers into existing hosts is itself an anchored edit of the riskiest file, and every host would carry Nexus-specific noise in its project memory. Heading-keyed sections need no retrofit; a renamed heading degrades to `obsolete` + `add`, which is visible rather than silent.
- **YAML manifest with a hand-written parser.** The only stdlib-free parser the project owns handles the frontmatter subset; extending it to nested mappings for one file is more code than the manifest itself. JSON is already parsed by every hook.
- **Checking on every prompt or fetching in the hook.** See §6.

---

## 12. Open questions for the operator

Brief §9, plus what the repository added. Decisions recorded on 2026-09-22 are marked **decided**; the rest stay open.

1. **Remote and credentials.** `origin` is the private GitHub repository and is reachable from this environment without a prompt. Open: is the same true from the machines where Liquid_Nexus and the other hosts live?
2. **Track tags or `main`?** **Decided: tags (`v*`)**, `--ref main` for testing; `v1.0.0` is created in Phase 1 after `28ab085` is pushed.
3. **Conflicts.** **Decided: hosts do not edit the core at all** (§7.2a: the tool gate denies edits to `replace` units, `.nexus/unlock.txt` is the operator's escape hatch). A conflict is therefore an exception; it is reported, the host's version stays, exit 1. No `.nexus-upstream` copies; `plan --diff` serves hand merging.
4. **`patches/`.** Proposed: keep the bundle format for migrations that need operator prompts; the updater does not read or replace bundles. Open.
5. **Which hosts** besides Liquid_Nexus. **Decided: two or three more exist; none is in scope until the mechanism works.** Phase 5 targets Liquid_Nexus only; the others follow the same runbook later.
6. **JSON manifest** instead of YAML (D4). **Decided: JSON** (explained 2026-09-22: stdlib `json` versus no YAML parser; operator agreed with the plan as explained).
7. **Section ownership of `CLAUDE.md` by H2 heading** (§3.3). **Decided: yes** (explained 2026-09-22: Nexus owns the six listed sections; every other section is the host's and is never read).
8. **Historical system documents.** **Decided: excluded from the manifest.** Documents that do not take part in running the system are template history and are not carried to hosts (§3.4 rule 2).
9. **Live-session guard** (§7.2, last item): refuse `apply` when `state.json` changed in the last 60 s unless `--in-session`. Open.
10. **Installer.** **Decided as a design requirement, not as scope:** a one-command install run inside the target folder is wanted later; the engine must serve it (§10a).
11. **Feedback from hosts to Nexus.** **Decided: separate plan**, `plan--system--nexus-feedback-channel.md`; the updater only lends it the cache directory and the `feedback push` subcommand.

---

## 13. Risks

- The `index-entries` strategy is the most intricate piece of text surgery in the design; it is also the file projects extend most. Fixtures for it come first in Phase 2, and a refusal always leaves the file untouched.
- A host that hand-copied a newer Nexus without updating `installed.json` sees `adopt` rows, which is correct, but a host that hand-copied a *partial* newer Nexus sees a mixture of `adopt` and `update` and must not be surprised; `plan` output must be readable enough that the mixture is obvious.
- The notifier is one more subprocess at every session start. Its silent-failure contract must be tested with the network cut, not assumed.
