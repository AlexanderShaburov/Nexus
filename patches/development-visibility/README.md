# Nexus Patch — Development-Phase Knowledge Visibility (v1.1.0)

This patch retrofits the **knowledge visibility** mechanism into an existing Nexus-based project. After applying, architecture reviews, gap analyses, and roadmap planning include active design work (drafts, roadmaps, proposals, in-review specs) — not just authoritative documents.

| | |
|---|---|
| Patch ID | `development-visibility` |
| Patch version | `1.1.0` |
| Source commit | `445dcd0c83f54d0d49d5048cf4f2b6217df2d12f` |
| Source repo | Nexus |
| Status | Production |
| Required runtime | `python3` ≥ 3.10 (already required by Nexus hooks) |

> **What changed in v1.1.0:** added the operator post-apply verification prompt at `prompts/post-apply-development-visibility-migration.md`. Payload and surgical edits are byte-identical to v1.0.0; bundle behaviour is unchanged.

For the case note, alternatives, and rationale, see (after applying) `knowledge/decisions/decision--system--development-visibility-failure.md`.

---

## TL;DR

```bash
# 1. Unzip or copy this directory into your project root
unzip nexus-development-visibility-patch.zip

# 2. Dry-run first (default — no changes made)
./patches/development-visibility/apply.sh --project-root .

# 3. Apply for real
./patches/development-visibility/apply.sh --project-root . --apply

# 4. Reload hooks in Claude Code
#    (in the CC TUI)  /hooks

# 5. Paste the post-apply verification prompt into Claude Code
#    (read-only first pass: verify, inventory, smoke-test, readiness report)
cat ./patches/development-visibility/prompts/post-apply-development-visibility-migration.md
```

---

## What this patch does

1. Adds 6 new vault documents (1 invariant, 2 specs, 1 decision, 1 runbook, 1 audit report).
2. Surgically edits 5 existing system files to wire the new behaviour into the agent's bootstrap, frontmatter contract, and project navigation:
   - `CLAUDE.md` — adds a "Knowledge Visibility" section.
   - `knowledge/index/index--system--project-navigation.md` — adds 2 spec entries + 1 invariant entry.
   - `knowledge/specs/spec--system--document-frontmatter.md` — registers the `knowledge_visibility` field.
   - `knowledge/specs/spec--system--session-bootstrap.md` — inserts STEP 3 "ACTIVE DESIGN TRACKS".
   - `.claude/hooks/nexus-bootstrap.py` — mirrors the STEP 3 block in the runtime injection.

After the patch:

- Review-class agent tasks ("what specs are missing?", "what gaps remain?", "review this architecture", "create a roadmap") must execute a **dual analysis** (Binding State + Development State) and **classify every gap** as one of `Truly Missing` / `Exists As Draft` / `Exists But Not Normalized` / `Superseded Gap`.
- The new invariant `invariant--system--review-classification.md` is auto-loaded at every session bootstrap.

---

## Safety properties

| Property | Value |
|---|---|
| Dry-run by default | ✅ — must pass `--apply` to mutate |
| Idempotent | ✅ — re-running after success is a no-op |
| Partial application prevented | ✅ — if any anchor is missing, the whole file is refused |
| Backups before modifying | ✅ — `.nexus/backups/development-visibility-<YYYYMMDD-HHMMSS>/` |
| Refuses on missing anchor | ✅ — never corrupts heavily-customized files |
| Refuses on ambiguous anchor | ✅ — fails if an anchor matches more than once |
| Promotes drafts to binding | ❌ — never |
| Marks drafts `source_of_truth: true` | ❌ — never |
| Deletes any file | ❌ — never |
| Modifies `.claude/settings.json` | ❌ — never |
| Modifies project knowledge documents | ❌ — only the 5 system files listed above |
| Edits frontmatter (`updated:`, `knowledge_visibility:`) on the 5 system files | ❌ — content-additive only; the fallback mapping correctly classifies those files as `binding` without an explicit field, and the project's own `updated:` date is left intact |

---

## Usage

```text
./apply.sh [--apply] [--force] [--backup-dir DIR] [--project-root PATH] [--help]
```

| Flag | Default | Effect |
|---|---|---|
| (none) | dry-run | Show what would change; do not modify any file. |
| `--apply` | off | Actually mutate the project. |
| `--force` | off | Skip the "looks like a Nexus project" guard. **Not recommended.** Use only if you know the target structure is non-standard. |
| `--backup-dir DIR` | `.nexus/backups/development-visibility-<TS>/` | Override the backup location. |
| `--project-root PATH` | current directory | Operate on a project at a different path. |
| `--help` | | Show flag help. |

You can also override the Python interpreter via the `PYTHON` env var:

```bash
PYTHON=/opt/homebrew/bin/python3 ./apply.sh --apply
```

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (or successful dry-run) |
| 1 | One or more edits were refused (manual patch needed for those files) |
| 2 | Target does not look like a Nexus project (use `--force` to override) |
| 3 | Bundle payload or target file missing |
| 4 | Internal error or missing `python3` |
| 5 | Post-apply validation failed |

---

## Bundle layout

```
patches/development-visibility/
├── README.md              ← this file
├── PATCH_MANIFEST.yaml    ← machine-readable manifest (patch id, files, strategy, safety, prompts)
├── manifest.txt           ← human-readable file list + SHA-256 checksums (payload only)
├── apply.sh               ← bash entry point
├── apply.py               ← python worker (does all real work)
├── prompts/               ← operator-facing prompts, NOT copied into target
│   └── post-apply-development-visibility-migration.md
└── payload/               ← 6 new files copied verbatim into the target
    ├── docs/
    │   └── development-visibility-patch-report.md
    └── knowledge/
        ├── decisions/
        │   └── decision--system--development-visibility-failure.md
        ├── invariants/
        │   └── invariant--system--review-classification.md
        ├── runbooks/
        │   └── runbook--system--development-visibility-migration.md
        └── specs/
            ├── spec--system--architecture-review.md
            └── spec--system--knowledge-visibility.md
```

---

## What the patch validates after applying

1. `.claude/hooks/nexus-bootstrap.py` contains `STEP 3 — ACTIVE DESIGN TRACKS`.
2. Each of the 5 new vault files (excluding the audit report) is present with `knowledge_visibility: binding` and `source_of_truth: true`.
3. `CLAUDE.md` references both new specs (`knowledge-visibility.md` and `architecture-review.md`).

If validation fails, the script exits 5 and reports which check failed.

---

## After applying — operator post-apply prompt (recommended)

After `apply.sh --apply` succeeds AND you have reloaded hooks with `/hooks`, paste the contents of

```
prompts/post-apply-development-visibility-migration.md
```

into Claude Code as a single message. This is a **read-only first pass** that:

1. verifies patch installation (10 PASS/FAIL checks);
2. confirms STEP 3 is visible in the bootstrap injection;
3. inventories every doc into Binding / Development / Historical State;
4. flags any invalid `knowledge_visibility` combinations;
5. recommends per-document frontmatter additions (grouped by target class);
6. runs an architecture-review smoke test with the four-way gap classification;
7. produces a Readiness Report.

The agent must NOT modify any file during this pass. Mutating actions (frontmatter migration per Section C of the migration runbook, and the subsequent commit) are deliberate operator-authorized follow-ups.

### Minimal smoke test (if you want to skip the full prompt)

```text
> Tell me what specs are missing from this project. Use the architecture-review workflow.
```

The agent's response must include `## Binding State`, `## Development State`, and `## Gap Classification` with every finding classified as one of the four classes. If it does not, the patch is not fully active — re-run `/hooks` after `apply.sh --apply`.

---

## What this patch does NOT automate

The patch handles the **system-file** part of the migration (Sections A and parts of D in the migration runbook). It does **NOT** automate:

- **Section B** — inventorying your project's existing drafts, roadmaps, and proposals.
- **Section C** — applying `knowledge_visibility:` markings to *your* development documents. This requires human judgement (is this draft genuinely active development, or abandoned and should be `historical`?).
- **Section E** — running the live review smoke tests.

Those remain operator tasks. The migration runbook walks through each one.

---

## When patches refuse to apply

The most common reason is a heavily customized `CLAUDE.md` or navigation index where the original anchor text has been edited away. When this happens:

1. The script reports the refused file and exits 1.
2. **No partial edit is applied** — the file is left exactly as it was.
3. Follow the manual section of `knowledge/runbooks/runbook--system--development-visibility-migration.md` (Section D for CLAUDE.md / bootstrap copies) for that file.
4. Re-run the patch — files that have already been correctly patched (manually or otherwise) will be skipped via the idempotency markers.

---

## Backups

By default, backups go to `.nexus/backups/development-visibility-<YYYYMMDD-HHMMSS>/`, preserving directory structure. Add `.nexus/backups/` to your `.gitignore` if you do not want backups checked in:

```gitignore
# Nexus patch backups (regenerated per patch run)
.nexus/backups/
```

To restore a single file from a backup:

```bash
cp .nexus/backups/development-visibility-<TS>/CLAUDE.md CLAUDE.md
```

---

## Producing the distributable zip

If you have the source Nexus repository, build a distributable zip via:

```bash
./tools/build-patch-zip.sh patches/development-visibility
```

The zip name follows the pattern `nexus-<patch-id>-patch-v<version>.zip`.

---

## Provenance

This patch corresponds exactly to upstream commit `445dcd0c83f54d0d49d5048cf4f2b6217df2d12f` in the Nexus repository. Payload files in `payload/` are byte-identical copies of the canonical files in that commit. Surgical-edit anchors target the file state immediately preceding that commit.
