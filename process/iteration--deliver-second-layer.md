---
type: iteration
id: T5a
status: draft
state: planned
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
depends_on: [process/iteration--run-cycle.md]
refs: [knowledge/specs/spec--system--nexus-update.md, knowledge/specs/spec--system--process-space.md]
---

# Deliver the second layer's infrastructure to Liquid_Nexus

Proposed 2026-10-09 after the investigation of the update mechanism; the operator approved the direction (test the second layer in the host Liquid_Nexus) and the split of the former T5 into two steps. This is the first step. Its boundary, set by the operator: the release and the update **deliver infrastructure only**; they prove nothing about the second layer in hosts. The host's `process/charter.md` and `process/navigation.md` are never copied from Nexus: they belong to the host and are written for its own purposes, in the next step. Every own file and setting of the host must survive the update byte for byte.

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
3. **Release 1.4.0**, on the operator's machine, in the shape of `v1.2.0` and `v1.3.0`: bump `nexus.version`, regenerate the manifest, selftest, one commit `release: Nexus 1.4.0`, annotated tag `v1.4.0`, push with tags. The release note says what the version carries and that it delivers infrastructure, not a tested second layer.
4. **Update Liquid_Nexus**, from a plain terminal with no Claude Code session open there, one command per turn, the operator pasting the output back: `git status` (clean tree, or commit first); `feedback status` and `feedback push` if notes wait; `status` (what drifted since 2026-09-22); `up` as a dry run, read the whole table, resolve any `customized` or `conflict` row deliberately before applying; `up --apply`; `git diff --stat`; commit; `/hooks` in the next Claude Code session.
5. **Check the result in the host**: `status` clean; a fresh session's bootstrap context lists four vault items and the one line about the missing charter; `CLAUDE.md` carries the Steering section after the host's own sections; the host's own documents, sessions, feedback notes, hooks and `settings.local.json` are unchanged (step 6 below says how this is shown).

Data-safety checks, each a visible fact, not a belief:

6. Before `up --apply`: the dry-run table names every path that will be written, and every one of them is a Nexus-owned unit of the manifest; nothing under `process/`, `knowledge/sessions/`, `knowledge/feedback/`, `knowledge/business/`, no document whose `scope` is not `system`, no host section of `CLAUDE.md`, no host hook, no `settings.local.json`. After `up --apply`: `git diff --stat HEAD` lists only those paths plus `.nexus/installed.json`; `git diff` of `CLAUDE.md`, `.claude/settings.json` and the navigation index shows changes only inside Nexus-owned sections, entries and lines; the backup directory under `.nexus/backups/` holds the previous copy of every written file and the previous baseline. Recovery, if anything is wrong: the update is one commit on a clean tree, so `git revert` (or `git checkout -- .` before committing) restores the host; the backup directory is the second copy.

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

- On the scratch copy: `apply --apply` from the release candidate exits 0 with validation clean, and the component list of step 2 is complete in the `plan` table; the bootstrap hook behaves both ways (no charter: one line; charter present: items 5 and 6).
- In Liquid_Nexus: `up --apply` exits 0 with post-apply validation clean; `status` shows 0 customized, 0 conflict, 0 refused; `git diff --stat` of the update commit lists only Nexus-owned paths and the baseline; the facts of step 6 hold; a fresh session there shows the one line about the missing charter and the Steering section is in `CLAUDE.md`.
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
