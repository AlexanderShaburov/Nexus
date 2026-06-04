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
- `CLAUDE.md`

👉 This repository is your **Nexus template**

---

# 📦 PART 1 — Installation (applies to ANY project)

## Step 1 — Copy Nexus into your project

From the Nexus template repository, copy into your project root:

```
.claude/
.nexus/
knowledge/
CLAUDE.md
```

👉 After this step your project should look like:

```
your-project/
├── .claude/
├── .nexus/
├── knowledge/
├── CLAUDE.md
```

---

## Step 2 — Verify files exist (IMPORTANT)

Check that:

- `.claude/hooks/` exists
- `.claude/settings.json` exists
- `knowledge/` is NOT empty
- `CLAUDE.md` exists

👉 If anything is missing — installation is incomplete

---

## Step 3 — Make hooks executable (Mac/Linux)

```
chmod +x .claude/hooks/*.py
```

---

## Step 4 — Add runtime file to `.gitignore`

Add:

```
.nexus/state.json
```

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

This part is the **only** correct way to upgrade an existing Nexus-based project to a newer Nexus version. **Do not** re-copy the runtime — you would overwrite the project's `CLAUDE.md` and the navigation index.

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

## Step 5 — Verify the patch took effect

Run a quick agent smoke test (specific tests live in the patch's own README and in the companion migration runbook):

```text
> Tell me what specs are missing from this project. Use the architecture-review workflow.
```

For the development-visibility patch, the response MUST include `## Binding State`, `## Development State`, and `## Gap Classification` with every finding classified.

---

## Step 6 — What to do if the patch refuses

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
