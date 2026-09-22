# Nexus Installation & Usage Guide (Revised)

## Purpose

This guide explains **how to install and actually use Nexus in practice**.

It is written for a developer who:
- has a project (or wants to start one)
- wants to enable Knowledge Vault + Nexus workflow
- needs **clear, actionable steps**

---

# 🧩 PART 0 — What you need

You need a **source repository** where Nexus is already prepared.

From that repository you will copy:

- `.claude/`
- `.nexus/`
- `knowledge/`
- `tools/`
- `docs/nexus-implementation-report.md`
- `CLAUDE.md`

👉 This repository is your **Nexus template**

> **`tools/` is not optional.** `.claude/hooks/nexus-vault-validator.py` loads its rule set from `tools/validate-vault.py`. If `tools/` is missing the hook still registers and still runs — and silently does nothing, because it degrades quietly by design. You would have a validator that never validates and no sign of it. And `tools/nexus-decide.py` is the claim form of the Context Decision: without it the tool gate accepts only the text form, which some Claude Code builds never persist (see `docs/nexus-implementation-report.md` §4, "Transcript narration").
>
> **`docs/nexus-implementation-report.md` is referenced by `CLAUDE.md`** ("run the validation plan in ..."). Without it that pointer dangles in every new project.

---

# 📦 PART 1 — Installation (applies to ANY project)

## The one-command way (Nexus 1.2.0 and later)

In the directory where Nexus should live, with a clean git tree:

```bash
curl -fsSL https://raw.githubusercontent.com/AlexanderShaburov/Nexus/main/nexus.py | python3 -            # dry-run
curl -fsSL https://raw.githubusercontent.com/AlexanderShaburov/Nexus/main/nexus.py | python3 - --apply    # install
```

or copy `nexus.py` from the Nexus repository once and run `python3 nexus.py --apply`. The script clones the Nexus repository into `~/.cache/nexus/` (never into your project), takes the newest release tag, and runs its updater with `up`, which decides what this directory needs:

| It finds | It does |
|---|---|
| no Nexus | **install**: every Nexus-owned file from the manifest; your `CLAUDE.md`, `.claude/settings.json` and `.gitignore`, if present, are extended, never replaced; a fresh `CLAUDE.md` gets a project stub for you to fill |
| Nexus files, no `.nexus/installed.json` | **retrofit**: guesses which release you have by matching files, records the baseline, marks anything you changed as customized, then updates |
| Nexus with a baseline | **update** (Part 6a) |

Dry-run first, always. `--apply` refuses on an uncommitted tree (`--allow-dirty` overrides) and while a Claude Code session looks live. Backups land under `.nexus/backups/`. It ends with the two things it cannot do for you: `/hooks` inside Claude Code, and `/project-ingest` for an existing project (Part 3).

After that, the project carries its own updater: `python3 tools/nexus-update.py up --apply` does the same next time.

Steps 1–4c below are the manual route, kept for reference and for releases before 1.2.0.

---

## Step 1 — Copy Nexus into your project

From the Nexus template repository, copy into your project root:

```
.claude/
.nexus/
knowledge/
tools/
docs/nexus-implementation-report.md
CLAUDE.md
```

👉 After this step your project should look like:

```
your-project/
├── .claude/
├── .nexus/
├── knowledge/
├── tools/
├── docs/
│   └── nexus-implementation-report.md
├── CLAUDE.md
```

---

## Step 1b — Clear the template's own session archives

`knowledge/sessions/` in the template contains transcripts of sessions run **in the template repository itself**, written automatically by `nexus-session-writer.py`. They are not your project's history and must not travel with the install:

```bash
rm -f knowledge/sessions/session--*.md knowledge/sessions/summary--*.md
```

👉 Skip this only if the template's `knowledge/sessions/` is already empty.

---

## Step 2 — Verify files exist (IMPORTANT)

Check that:

- `.claude/hooks/` exists
- `.claude/settings.json` exists
- `tools/validate-vault.py` exists
- `tools/nexus-decide.py` exists
- `tools/nexus-update.py` exists
- `knowledge/` is NOT empty
- `knowledge/sessions/` contains no leftover template transcripts
- `CLAUDE.md` exists

👉 If anything is missing — installation is incomplete

---

## Step 3 — Make hooks executable (Mac/Linux)

```
chmod +x .claude/hooks/*.py tools/*.py
```

---

## Step 4 — Add runtime files to `.gitignore`

Add:

```
.nexus/state*.json
.nexus/backups/
```

👉 A glob, not the literal `.nexus/state.json`: macOS and iCloud create duplicates such as `.nexus/state 2.json`, which the literal rule does not catch and which then get committed.

If the project uses Obsidian on the vault, also add:

```
knowledge/.obsidian/workspace*.json
```

That file is per-user pane layout, rewritten on every use. The rest of `knowledge/.obsidian/` is shared configuration and should stay tracked.

---

## Step 4b — Confirm the vault validates

```bash
python3 tools/validate-vault.py --selftest   # expect: 35/35 passed
python3 tools/validate-vault.py              # expect: 0 error(s), exit 0
```

👉 If `--selftest` fails, the copy is incomplete or corrupted. Do not proceed.

---

## Step 4c — Record the install baseline

Nexus can only tell "delivered by Nexus" from "written by this project" if it knows what it delivered. Record that once, right after copying, pointing at the template checkout you copied from:

```bash
python3 tools/nexus-update.py baseline --upstream /path/to/Nexus --ref v1.0.0
python3 tools/nexus-update.py status          # expect: every unit unchanged
git add .nexus/installed.json
```

👉 `--ref` is the template tag (or commit) you copied. Omit it to baseline against the template's working tree as it is now.

👉 `.nexus/installed.json` is **committed** with your project. It is the baseline for every future update and for the core freeze; unlike `state.json` it is not session state.

👉 Do not edit files listed in `installed.json` by hand. Nexus core files are frozen in projects; improvements go upstream (see the feedback channel when it ships) and come back with the next update. If a change cannot wait, list the path in `.nexus/unlock.txt` and expect `status` to report it as customized from then on.

---

## Step 5 — Reload hooks (inside Claude Code)

In Claude Code, run:

```
/hooks
```

👉 This activates Nexus

---

# 🆕 PART 2 — If this is a NEW project

## IMPORTANT

You already copied `knowledge/`.

👉 You DO NOT create it again.

---

## Step 1 — Verify minimal Knowledge Vault

Check that these exist:

- `knowledge/index/`
- `knowledge/architecture/`
- `knowledge/invariants/`
- `knowledge/specs/`

---

## Step 2 — Start working

That’s it.

👉 You DO NOT manually edit knowledge files.

Instead:

- give tasks to Claude
- Claude will:
  - read knowledge
  - perform work
  - update knowledge when needed

---

## Step 3 — How knowledge is updated

❗ User does NOT manually maintain Knowledge Vault

Instead:

- you give tasks
- Claude decides:
  - “KB changed: yes”
- and updates `knowledge/`

👉 Your role:
- review changes
- accept or correct them

---

# 🏗 PART 3 — If this is an EXISTING project

This is the critical scenario.

---

## Step 1 — Install Nexus (same as Part 1)

DO NOT touch existing docs yet.

---

## Step 2 — Run ingestion

In Claude Code:

```
/project-ingest
```

---

## Step 3 — Answer Claude’s questions

Claude will ask about:

- project purpose
- trusted sources
- known issues

👉 You must answer — this guides ingestion

---

## Step 4 — Review ingestion results

Claude will produce:

- project understanding
- extracted architecture
- list of inconsistencies

👉 Your job:

- confirm correctness
- fix misunderstandings

---

## Step 5 — Accept Knowledge Vault

After ingestion:

- `knowledge/` = **main source of truth**
- old docs = **reference only**

---

## Step 6 — What YOU do as user

You do NOT:

- rewrite documentation manually
- reorganize knowledge manually

You DO:

- give tasks
- review results
- approve or correct Claude’s understanding

---

# ⚙️ PART 4 — How Nexus works (for understanding)

You do NOT need to operate this manually.

This is how Claude behaves:

1. Reads Knowledge Vault (bootstrap)
2. Makes Context Decision
3. Executes tools
4. Writes Closure Block

---

# ❗ KEY RULES (for user)

## Rule 1 — You do not edit knowledge manually

👉 Knowledge is maintained by Claude

---

## Rule 2 — You give tasks, not instructions about files

BAD:
- “edit this file in knowledge”

GOOD:
- “update architecture after this change”

---

## Rule 3 — You review, not maintain

👉 Your job is:
- verify
- correct
- approve

---

# 🧠 PART 5 — When to use `/project-ingest`

Use it ONLY when:

- onboarding Nexus into existing project
- knowledge is missing or chaotic

DO NOT use it:

- during normal development
- for small changes

---

# 🔄 PART 6 — Updating an EXISTING Nexus project

Two mechanisms exist. **Part 6a** is the updater (`tools/nexus-update.py`): it compares your project with the Nexus repository and, once its `apply` subcommand ships, adopts a newer version in one command. **Part 6b** is the older patch-bundle route, kept for one-off migrations that need operator prompts. **Do not** re-copy the runtime by hand — you would overwrite the project's `CLAUDE.md` and the navigation index.

---

## Part 6a — The updater

Requires the baseline from Step 4c (`.nexus/installed.json`). Projects installed before the baseline existed record one first:

```bash
python3 tools/nexus-update.py baseline --upstream https://github.com/AlexanderShaburov/Nexus.git --guess
git add .nexus/installed.json
```

`--guess` scores every release tag and recent commit by how many delivered files match yours and picks the best; files that match nothing are recorded as customized, never overwritten later.

Then, whenever you like:

```bash
python3 tools/nexus-update.py check      # is a newer Nexus tagged upstream?
python3 tools/nexus-update.py plan       # what would change, unit by unit; writes nothing
python3 tools/nexus-update.py plan --diff knowledge/specs/spec--system--exit-gate.md
python3 tools/nexus-update.py status     # your local state against the baseline
```

`plan` classes: `update` (yours untouched, upstream changed), `add` (new upstream), `customized` (yours changed, upstream not; left alone), `conflict` (both changed; left alone, exit 1), `removed-locally`, `obsolete`, `converged`, `adopt`, `unbaselined`, `mode-drift`, `unchanged`. The upstream repository is cached under `~/.cache/nexus/template`; `--offline` reuses the cache without network.

To adopt the new version, from a **plain terminal**, not from inside a Claude Code session (the update rewrites the hooks that govern the session):

```bash
python3 tools/nexus-update.py up               # dry-run: lists what would be written
python3 tools/nexus-update.py up --apply       # writes, with backups under .nexus/backups/
git add -A && git commit -m "chore(nexus): update to <version>"
```

`up` is `apply` plus auto-detection (install / retrofit / update) and the clean-tree guard; `apply` remains for scripts that want exactly the update step. A project that has Nexus but no `.nexus/installed.json` yet needs no separate `baseline` step: `up` guesses the installed release and records it before updating.

👉 **Retrofitting a project that edited Nexus files** (the dry-run lists them as `conflict` or `customized`): post-apply validation runs the project's **own** `tools/validate-vault.py`. If that file is among the conflicts, restore it in the same run, otherwise the old validator rejects the new documents and the run ends with exit 5:

```bash
python3 tools/nexus-update.py up --apply --restore tools/validate-vault.py
```

Then review every remaining conflict with `plan --diff <path>`. Lines the diff removes (`-`) are what your copy has and Nexus does not; if they are only older Nexus wording, `up --apply --restore <path>` brings the file back to Nexus. If they are your own additions, keep the file and send them upstream as a feedback note (Part 6c).

Then, in Claude Code, run `/hooks`.

`apply` writes only the `update` and `add` rows, backs up every file it touches, rewrites `.nexus/installed.json`, and validates the result (vault clean, hooks compile, `settings.json` sane). `customized` and `conflict` rows are left alone; take a single one deliberately with `apply --apply --restore <path>`. A second run after success changes nothing.

👉 **Core files are frozen in projects.** Once the baseline exists, Claude Code's tool gate refuses to edit a Nexus core file in your project and points to the feedback route instead. If a change truly cannot wait, list the path in `.nexus/unlock.txt`; `status` will report it as customized from then on, and `apply` will never overwrite it.

---

## Part 6c — Sending feedback upstream

Nexus is still being built, and your project is where its rough edges show first. Because core files are frozen in projects (Part 6a), improvements do not go into your copy; they go **upstream** as feedback notes and come back with the next release.

**Write the note.** Ask Claude for it, or write it yourself, at `knowledge/feedback/feedback--nexus--<slug>.md`:

```yaml
---
type: feedback
scope: nexus
status: draft
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
kind: bug            # bug | wish | praise
nexus_version: 1.0.0 # from .nexus/installed.json
host: my-project     # your repository's directory name, kebab-case
touches: [.claude/hooks/nexus-exit-gate.py]
delivered: []
tags: [feedback, nexus]
---

# One-line title

## What happened

## What is proposed

## Attachment

none
```

`python3 tools/validate-vault.py knowledge/feedback` checks the shape. Commit the note with your project: it is yours whether or not it is ever delivered.

**Deliver it.** From the project root:

```bash
python3 tools/nexus-update.py feedback status   # what is pending and why
python3 tools/nexus-update.py feedback push     # copy into ~/.cache/nexus/inbox/<host>/
git add knowledge/feedback && git commit -m "feedback: <slug>"
```

`push` appends a receipt to the note's `delivered:` line and touches nothing else. Edit the note later and push again: the new version is delivered as a second copy. No network, no GitHub credentials: the mailbox is a directory on this machine, and the next Claude Code session started inside the Nexus repository is told how many notes are waiting.

**When the fix arrives** in an update, set the note's `status` to `approved`; if the proposal was declined, `deprecated`. Nothing does this for you.

👉 Praise counts. "This must not break" is as useful upstream as "this is broken".

👉 A project whose `tools/validate-vault.py` predates the release that introduced `type: feedback` will reject the note with `FM006`. Update the project first (Part 6a), then write notes.

---

## Part 6b — Patch bundles

This part is the way to apply a **patch bundle** to an existing Nexus-based project.

---

## When to use this

Use this part when ALL of the following are true:

- The project ALREADY has Nexus installed.
- The project has `.claude/hooks/nexus-*.py`, `.nexus/`, and `knowledge/`.
- A newer Nexus release ships a patch bundle for the feature you need.

👉 If the project does NOT have Nexus yet, use Part 1 + Part 3 instead.

---

## Step 1 — Obtain the patch bundle

Patch bundles are shipped under `patches/<patch-id>/` in this repository, and as distributable zips when prepared by a release manager. For example:

```
patches/development-visibility/
nexus-development-visibility-patch-v1.0.0.zip
```

Copy the bundle (or unzip it) into your project root. The leading directory after unzip will be named `nexus-<patch-id>-patch/`.

---

## Step 2 — Dry-run first (default)

```bash
./patches/development-visibility/apply.sh --project-root .
```

This shows EXACTLY which files would change. Nothing is modified.

If the bundle was unzipped to `nexus-<patch-id>-patch/`:

```bash
./nexus-development-visibility-patch/apply.sh --project-root .
```

---

## Step 3 — Apply

```bash
./patches/development-visibility/apply.sh --project-root . --apply
```

The script:

- creates a timestamped backup at `.nexus/backups/<patch-id>-<YYYYMMDD-HHMMSS>/`;
- copies new files into the project (skips if identical, backs up if different);
- applies anchor-based surgical edits to system files (idempotent);
- refuses to corrupt heavily-customized files (reports them and exits 1);
- validates the result.

👉 Re-running after success is a SAFE no-op. The script is idempotent.

---

## Step 4 — Reload Claude Code hooks

In Claude Code:

```
/hooks
```

This activates the new runtime behaviour.

---

## Step 5 — Paste the post-apply verification prompt

Most patches ship a ready-made verification prompt under `prompts/` in the bundle. For the development-visibility patch:

```
patches/development-visibility/prompts/post-apply-development-visibility-migration.md
```

Open that file, copy the block between `--- BEGIN PROMPT ---` and `--- END PROMPT ---`, and paste it into Claude Code as a single message.

This is a **READ-ONLY first pass**. The agent will:

- verify the patch installation (10 PASS/FAIL checks);
- inventory the project into Binding / Development / Historical State;
- flag any invalid frontmatter combinations;
- recommend per-document `knowledge_visibility:` additions;
- run an architecture-review smoke test with the four-way gap classification;
- emit a Readiness Report (READY / NOT READY for migration + commit).

👉 The agent must NOT modify any file during this pass. Mutating actions (frontmatter migration, the commit) are a separate operator-authorized step.

If the bundle does NOT ship a `prompts/` directory, fall back to the minimal smoke test below.

---

## Step 5b — Minimal smoke test (fallback)

If you skipped the post-apply prompt:

```text
> Tell me what specs are missing from this project. Use the architecture-review workflow.
```

For the development-visibility patch, the response MUST include `## Binding State`, `## Development State`, and `## Gap Classification` with every finding classified.

---

## Step 6 — Act on the Readiness Report

When the post-apply prompt finishes and reports **READY**:

- review the recommended frontmatter additions;
- author a follow-up prompt that authorizes the agent to apply Section C of the migration runbook (frontmatter migration);
- review the agent's changes;
- commit.

When the report says **NOT READY**, resolve the blocking items it names (re-run hooks, manually apply refused edits per Section D, fix invalid combinations) and re-run the prompt.

---

## Step 7 — What to do if the patch refuses

The patch may refuse a file if its anchors were already removed by heavy local customization (most common on `CLAUDE.md`). In that case:

- the script exits 1 and names the refused file;
- the file is NOT modified;
- follow the manual section of the patch's companion runbook (e.g. `knowledge/runbooks/runbook--system--development-visibility-migration.md`) for that file;
- re-run the patch — already-correct files are skipped via idempotency markers.

---

## Patch vs install — quick reference

| Situation | Use |
|---|---|
| Brand-new project | **Part 1 + Part 2** (install) |
| Existing project, no Nexus yet | **Part 1 + Part 3** (install + ingest) |
| Existing Nexus project, feature added upstream | **Part 6** (patch, this part) |

---

# 🎯 FINAL PRINCIPLE

> You do not manage the Knowledge Vault manually.  
> You manage the system by giving tasks to Claude.
