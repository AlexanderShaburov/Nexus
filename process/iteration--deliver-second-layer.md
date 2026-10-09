---
type: iteration
id: T5a
status: approved
state: in_progress
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
depends_on: [process/iteration--run-cycle.md]
refs: [knowledge/specs/spec--system--nexus-update.md, knowledge/specs/spec--system--process-space.md]
---

# Deliver the second layer's infrastructure to Liquid_Nexus

Proposed 2026-10-09 after the investigation of the update mechanism; the operator approved the direction (test the second layer in the host Liquid_Nexus), the split of the former T5 into two steps, and this contract the same day with two refinements, written into steps 3 and 6: the release must match the rehearsed state, and the host's own data must be shown intact by checksums over the protected areas, untracked files included, not by `git diff` alone. The host is not updated without the operator's separate consent after reading the dry run. This is the first step. Its boundary, set by the operator: the release and the update **deliver infrastructure only**; they prove nothing about the second layer in hosts. The host's `process/charter.md` and `process/navigation.md` are never copied from Nexus: they belong to the host and are written for its own purposes, in the next step. Every own file and setting of the host must survive the update byte for byte.

Status 2026-10-09, steps 1 and 2 done. Step 1: `spec--system--process-space.md` promoted to `approved` / binding (its link to the open question now cites the path); the decision record cites the open question by path; the index line updated; the one-sentence amendment the rules promised at approval added to the orchestration spec's Planning Artifacts section; manifest regenerated (34 entries, 61 units) and verified; vault clean; validator selftest 35/35; updater selftest passed. Step 2, on a scratch copy of a 1.3.0 host with planted host-owned files (a host spec, a host session, `settings.local.json`, a host section in `CLAUDE.md`, a note under `business/`, and an untracked host decision): `plan` against the working tree lists update 11, add 6, no blocking rows, and the add rows include `spec--system--process-space.md`, its index entry, the decision and the Steering section; `apply --apply` exits 0 with validation clean; `status` 61 unchanged, 0 customized; the checksum inventory of the protected areas (104 files, the untracked note included) is identical before and after; `git diff --name-only` lists only Nexus-owned paths; the second run is a no-op. The bootstrap hook of the copy prints the one line about the missing charter without `process/`, and lists `process/charter.md` and `process/navigation.md` as items 5 and 6 when they are placed there. Two lessons for step 4, from fixtures that broke the rehearsal before the clean run: the inventory command must be null-safe (`find -print0 | sort -z | xargs -0`, a legacy file name with a space broke the first attempt) and must exclude `__pycache__/` (the post-apply hook compilation creates it; gitignored in the host); and post-apply validation covers every `knowledge/**/*.md` of the host, so a host document without frontmatter fails the update with exit 5 after the files are written. Hence step 4 begins with `python3 tools/validate-vault.py` in the host before `up`. Step 3 (release 1.4.0) not started.

## Question

Can the existing updater (`tools/nexus-update.py`, contract `spec--system--nexus-update.md`) carry a release that contains every system component the second layer needs into Liquid_Nexus, with no loss of the host's own data and settings, and without a new installer or a new mechanism?

## Input

- Liquid_Nexus has a committed baseline at Nexus 1.3.0 (retrofitted and updated 2026-09-22; core freeze on; `status` clean that day). Its state today is unknown until checked there.
- The updater and its selftest are green; the manifest is in sync; the GitHub remote carries `v1.0.0`, `v1.2.0`, `v1.3.0`. Nothing after `v1.3.0` is tagged: 31 commits, among them the bootstrap reading of `process/`, the `PreCompact` fix and the ledger lock.
- Rehearsal of 2026-10-09 on a scratch copy of a 1.3.0 host against `main`: `plan` shows update 10, add 4, no blocking rows; `apply --apply` writes them and then **fails post-apply validation** (exit 5, files left in place) on three `LK001` links from delivered binding documents to undelivered ones: `spec--system--session-bootstrap.md` and `decision--system--second-layer-purpose.md` link to `spec--system--process-space.md` (draft, not in the manifest), and the decision also links to `open-questions/question--system--progressive-resolution.md` (development class).
- The process-space rules say they become `approved` after the cycle has run once in real work; T8 closed with that result on 2026-10-09, and the operator agreed to the promotion.

## Work

In this order, each step checked before the next:

1. **Make the delivery complete and valid.** Promote `spec--system--process-space.md` to `approved` (binding; it then enters the manifest as a `replace` unit and its index line becomes an owned `index-entries` unit). In the decision record, cite the open question by path instead of linking it, the way the glossary cites the rename ADR. Regenerate the manifest (`manifest generate`, then `verify`), run `validate-vault.py` and `--selftest`.
2. **Prove completeness on the copy, before any tag.** On a scratch copy of a 1.3.0 host (`git archive v1.3.0`, baseline on `v1.3.0`): `plan --ref main` must list, as `update` or `add`, every component the second layer needs in a host: the four hooks (`_nexus_common.py`, `nexus-bootstrap.py`, `nexus-prompt-gate.py`, `nexus-tool-gate.py`), the three `CLAUDE.md` sections (How work proceeds here; Mandatory Startup Reading Set with item 5; Steering), `spec--system--process-space.md` and its index entry, `spec--system--session-bootstrap.md`, `decision--system--second-layer-purpose.md`, the architecture, the two `.gitignore` lines. `apply --apply` must exit 0 with validation clean. Then pipe `SessionStart` into the copy's bootstrap hook twice: without a charter it prints the one line that the second layer is not active; with a hand-written `process/charter.md` and `navigation.md` placed in the copy it lists them as items 5 and 6. Not delivered on purpose: `process/README.md`, charter and navigation templates, validator rules for `process/`.
3. **Release 1.4.0**, in the shape of `v1.2.0` and `v1.3.0`: bump `nexus.version`, regenerate the manifest, selftest, one commit `release: Nexus 1.4.0`. **Before the tag**: `manifest verify` on that commit, and the rehearsal of step 2 repeated against that exact commit (`--ref <release commit>`); the full set of step-2 checks is repeated only if the delivered content changed since the last rehearsal, otherwise `plan` + `apply --apply` + validation suffice. Then the annotated tag `v1.4.0` and the push with tags, by the operator. The release note says what the version carries and that it delivers infrastructure, not a tested second layer.
4. **Update Liquid_Nexus**, from a plain terminal with no Claude Code session open there, one command per turn, the operator pasting the output back: `git status` (clean tree, or commit first); `feedback status` and `feedback push` if notes wait; `status` (what drifted since 2026-09-22); `up` as a dry run, read the whole table, resolve any `customized` or `conflict` row deliberately before applying; `up --apply`; `git diff --stat`; commit; `/hooks` in the next Claude Code session.
5. **Check the result in the host**: `status` clean; a fresh session's bootstrap context lists four vault items and the one line about the missing charter; `CLAUDE.md` carries the Steering section after the host's own sections; the host's own documents, sessions, feedback notes, hooks and `settings.local.json` are unchanged (step 6 below says how this is shown).

Data-safety checks, each a visible fact, not a belief:

6. Before `up --apply`: the dry-run table names every path that will be written, and every one of them is a Nexus-owned unit of the manifest; nothing under `process/`, `knowledge/sessions/`, `knowledge/feedback/`, `knowledge/business/`, no document whose `scope` is not `system`, no host section of `CLAUDE.md`, no host hook, no `settings.local.json`. **Checksum inventory** (the operator's refinement): before `up --apply`, record the list and SHA-256 of every file, tracked or not, under the protected areas (`process/`, `knowledge/sessions/`, `knowledge/feedback/`, `knowledge/business/`, every `knowledge/**/*.md` not named in the manifest, `.claude/settings.local.json`, `.nexus/` except `installed.json` and `backups/`, and every file outside the Nexus-owned paths) with plain `find | sort | xargs sha256sum` into a file outside the repository; after `up --apply`, record again and `diff` the two: a changed hash is a modification, a line present only before is a deletion, a line present only after is an unexpected creation. Expected: an empty diff. No new Nexus tool: shell only, the exact command pasted into this file with its result. After `up --apply`: `git diff --stat HEAD` lists only the Nexus-owned paths plus `.nexus/installed.json`; `git diff` of `CLAUDE.md`, `.claude/settings.json` and the navigation index shows changes only inside Nexus-owned sections, entries and lines; the backup directory under `.nexus/backups/` holds the previous copy of every written file and the previous baseline. Recovery, if anything is wrong: the update is one commit on a clean tree, so `git revert` (or `git checkout -- .` before committing) restores the host; the backup directory is the second copy.

Expected size: two document edits and a manifest regeneration in the template; one release; one `up` in the host; one session here plus the operator's commands on the host's machine. Live-check budget, by T8's lesson: one round on the host; a defect found there is a new round, recorded here, not a reason to add mechanism.

## We deliberately ignore

- Templates for `charter.md` and `navigation.md` at install (`spec--system--process-space.md` §2 allows them; the host writes its own in the next step).
- A validator rule that softens links into the development class the way `LK002` does for `plans/` and `sessions/`: new mechanism; at most a feedback note.
- A `rollback` subcommand: git and the backup directory are the recovery path.
- `.nexus/README.md` in the host stays the old text (create-if-absent); cosmetic.
- Other hosts; the GitHub-issue transport of the feedback channel; anything about the host's own project.
- Activating the second layer in the host and running the cycle there: the next step (T5b), out of this contract.

## Artifact

Tag `v1.4.0` on GitHub with `nexus.version` 1.4.0 and a manifest that carries the process-space rules. In Liquid_Nexus: one commit that updates Nexus to 1.4.0, `.nexus/installed.json` at 1.4.0, `status` clean. In this file: the rehearsal result, the host's `up` table as pasted, the data-safety facts of step 6, and the expected-vs-obtained comparison.

## Success

- On the scratch copy: `apply --apply` from the exact release commit exits 0 with validation clean, and the component list of step 2 is complete in the `plan` table; the bootstrap hook behaves both ways (no charter: one line; charter present: items 5 and 6).
- In Liquid_Nexus: the checksum inventory of the protected areas is identical before and after (empty diff); `up --apply` exits 0 with post-apply validation clean; `status` shows 0 customized, 0 conflict, 0 refused; `git diff --stat` of the update commit lists only Nexus-owned paths and the baseline; the facts of step 6 hold; a fresh session there shows the one line about the missing charter and the Steering section is in `CLAUDE.md`.
- Nothing of the host's own was written, renamed or deleted; `process/` does not exist in the host unless the host had it before.
- The operator can say from the pasted output alone which files changed and why each is Nexus-owned.

What this does **not** show, by the operator's boundary: that the second layer works in a host. That is T5b.

## Unknowns to observe

- The host's actual `status` today: drift since 2026-09-22, `customized` or `conflict` rows, entries in `.nexus/unlock.txt`, uncommitted changes.
- Whether the host's own vault validates under the 1.4.0 validator: post-apply validation runs the whole vault, so the host's own documents can fail it.
- Whether GitHub is reachable from the host's machine today (it was on 2026-09-22).
- Whether the seven Nexus headings of the host's `CLAUDE.md` and the Nexus lines of its index are intact; otherwise sections and entries arrive as `removed-locally` plus `add`, not `update`.
- Whether feedback notes wait in the host; they are the input for the next template fixes.
- Whether the operator finds the one-command-per-turn procedure on the host workable, or wants the agent to prepare a single script to paste.
