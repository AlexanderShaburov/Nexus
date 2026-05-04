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

# 🎯 FINAL PRINCIPLE

> You do not manage the Knowledge Vault manually.  
> You manage the system by giving tasks to Claude.
