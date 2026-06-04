# Nexus Knowledge Runtime

## What this repository is

This repository contains a **knowledge-driven operating layer** for code work inside a project.

Its purpose is to help an agent work **through a project knowledge base**, rather than relying only on transient context or ad-hoc reading. In practice, this means:

- the agent is guided to read required project knowledge before acting;
- the agent is forced to make an explicit context decision before mutating work;
- the agent is required to close each turn with a structured completion block;
- the project can be gradually converted from legacy documentation into a normalized knowledge base.

This repository is not just a folder of documents. It is a **runtime discipline** made of:

- a project knowledge structure under `knowledge/`
- Claude hook enforcement under `.claude/hooks/`
- runtime session state under `.nexus/`
- optional operational skills such as `project-ingest`

---

## What problem this solves

LLM-driven work in real projects often fails for the same reasons:

- the agent starts acting before reading enough project context;
- important architecture and invariants are ignored;
- legacy documents, code, and notes contradict each other;
- the project has documentation, but no canonical operational memory;
- the agent finishes work without deciding whether the knowledge base must be updated.

Nexus addresses this by turning project knowledge into a **first-class execution dependency**.

---

## What Nexus means

**Nexus** is the name of the system used in this repository.

A practical canonical expansion is:

> **Structured Orchestration of Knowledge-Driven Interaction**

In practice, Nexus means that work is expected to flow through a gated lifecycle:

1. **Bootstrap**
2. **Context Decision**
3. **Execution**
4. **Exit / Closure**

---

## Core idea

The core idea is simple:

> The agent should not work from memory alone.  
> It should work through the knowledge system of the project.

That knowledge system is stored under:

```text
knowledge/
```

This directory is intended to become the **canonical operational source of truth** for the project.

Other materials may still exist, such as:

- old docs
- notes
- legacy specs
- exploratory markdown
- historical plans

But those should not automatically be treated as canonical. They should either be:

- normalized into `knowledge/`, or
- kept as legacy/reference/archive material.

---

## High-level architecture

### 1. `knowledge/`
The project knowledge base.

Typical categories include:

- `index/`
- `architecture/`
- `invariants/`
- `specs/`
- `decisions/`
- `patterns/`
- `plans/`
- `sessions/`
- `bugs/`
- `runbooks/`
- `glossary/`
- `open-questions/`
- `business/`

### 2. `.claude/hooks/`
The enforcement layer.

These hooks implement the runtime discipline that keeps the agent inside the Nexus workflow.

### 3. `.nexus/`
Runtime state used by the hooks.

This is where session-level state such as bootstrap progress is stored.

### 4. `CLAUDE.md`
The project-facing operating document that points Claude toward the knowledge system and the expected workflow.

### 5. `skills/` or `.claude/skills/`
Optional operational skills, including project ingestion skills for adapting existing projects into the knowledge system.

---

## What the hooks do

The hooks enforce the three most important disciplines.

### Bootstrap discipline
Before meaningful work begins, the agent must read the required startup context.

### Context Decision discipline
Before mutating work, the agent must explicitly state whether the knowledge base must be consulted.

### Exit discipline
Before ending the turn, the agent must emit a closure block describing whether:

- code changed
- KB changed
- session log was written
- writeback evaluation was performed

---

## Why this matters

Without enforcement, “use the knowledge base” quickly degrades into a suggestion.

With enforcement, the system becomes operational:

- the agent is slowed down at the right points;
- the project gains a stable memory structure;
- documentation work becomes part of execution, not an afterthought;
- legacy chaos can gradually be converted into canonical knowledge.

---

# Repository layout

A typical layout looks like this:

```text
.
├── .claude/
│   ├── hooks/
│   │   ├── _nexus_common.py
│   │   ├── nexus-bootstrap.py
│   │   ├── nexus-prompt-gate.py
│   │   ├── nexus-tool-gate.py
│   │   └── nexus-exit-gate.py
│   ├── settings.json
│   └── skills/
│       └── project-ingest.md
├── .nexus/
│   └── README.md
├── knowledge/
│   ├── index/
│   ├── architecture/
│   ├── invariants/
│   ├── specs/
│   ├── decisions/
│   ├── patterns/
│   ├── plans/
│   ├── sessions/
│   ├── bugs/
│   ├── runbooks/
│   ├── glossary/
│   ├── open-questions/
│   └── business/
├── CLAUDE.md
└── README.md
```

---

# Installation

## Option A — Install into a new project

Use this option when the target repository is new or mostly empty.

### Step 1 — Copy the Nexus runtime files

Copy into the target repository root:

- `.claude/hooks/`
- `.claude/settings.json`
- `.nexus/README.md`
- `knowledge/` skeleton
- `CLAUDE.md`
- optional skill files under `.claude/skills/` or project-local skills directory

### Step 2 — Ensure the hook files are executable

On Unix-like systems:

```bash
chmod +x .claude/hooks/*.py
```

### Step 3 — Make sure runtime state is ignored

Add this to `.gitignore` if not already present:

```gitignore
.nexus/state.json
```

### Step 4 — Seed the minimum required knowledge files

At minimum, provide:

- a navigation index under `knowledge/index/`
- a system architecture document under `knowledge/architecture/`
- at least one invariant under `knowledge/invariants/`
- the required system specs under `knowledge/specs/`

### Step 5 — Reload Claude hooks

After installing or changing `.claude/settings.json`, open Claude Code and run:

```text
/hooks
```

This reloads hook configuration.

### Step 6 — Start the session

Once the session starts, Nexus bootstrap will require the startup reading set before work proceeds.

---

## Option B — Install into an existing project

Use this option when the project already contains code, documents, legacy notes, or inconsistent project memory.

> If the existing project already has Nexus installed and you only need to bring it up to date with a newer Nexus version, **don't reinstall** — use a **patch bundle** instead. See [Updating an existing Nexus project](#updating-an-existing-nexus-project) below.

### Step 1 — Install the same runtime files

Copy into the existing repository root:

- `.claude/hooks/`
- `.claude/settings.json`
- `.nexus/README.md`
- `knowledge/` skeleton
- `CLAUDE.md`
- optional skills

### Step 2 — Do **not** immediately treat all old documentation as canonical

This is critical.

Existing materials may include:

- old architecture notes
- outdated specs
- duplicated markdown
- exploratory notes
- conflicting design descriptions

These should not automatically become part of the knowledge base.

### Step 3 — Run the project ingestion skill

Use the ingestion skill to inspect the workspace, classify source material, and build or update the project knowledge base.

Recommended canonical skill name:

```text
/project-ingest
```

If your Claude environment uses skill files directly rather than slash commands, place the skill at a path such as:

```text
.claude/skills/project-ingest.md
```

or another supported skills directory.

### Step 4 — Review the ingestion results

The ingestion workflow should:

- inspect the repository structure
- classify whether the workspace is an existing project
- ask the user for missing project context
- inventory code and documents
- classify legacy materials
- build or update `knowledge/`
- identify code ↔ documentation mismatches
- produce a final ingestion report

### Step 5 — Confirm canonical source of truth

After ingestion, the intended model is:

- `knowledge/` = canonical operational memory
- old docs outside `knowledge/` = legacy, raw source, historical, or archive

---

# Updating an existing Nexus project

If a project already has Nexus installed (it has `.claude/hooks/nexus-*.py`, `.nexus/`, and `knowledge/`), do not reinstall by re-copying the runtime — you will overwrite project-specific content in `CLAUDE.md` and the navigation index. Use a **patch bundle** instead.

## What a patch bundle is

A patch bundle is a self-contained directory under `patches/<patch-id>/` that ships:

- new files to add to the target project (`payload/`);
- surgical edits for existing system files (anchor-based; never overwrites project-local content);
- an `apply.sh` / `apply.py` worker;
- a human-readable `README.md` and `manifest.txt`;
- a machine-readable `PATCH_MANIFEST.yaml` describing patch id, version, source commit, file strategy, and safety properties.

Patch bundles are dry-run by default, idempotent, refuse to corrupt heavily-customized files, and create timestamped backups before mutating anything.

## When to use install vs patch

| Situation | Use |
|---|---|
| Brand-new repository, no Nexus yet | **Install** (Option A above) |
| Existing project with no Nexus yet | **Install + ingest** (Option B above) |
| Existing Nexus project, new Nexus feature available | **Patch** (this section) |
| Need to inventory existing project drafts after a patch | The patch's companion runbook under `knowledge/runbooks/` |

## How to apply a patch bundle

```bash
# from the existing target project's root
unzip nexus-<patch-id>-patch-v<version>.zip
./nexus-<patch-id>-patch/apply.sh                # dry-run (default)
./nexus-<patch-id>-patch/apply.sh --apply        # actually apply
```

Then reload Claude Code hooks (in the CC TUI):

```text
/hooks
```

The patch's own `README.md` (inside the bundle) documents the flags, the exit codes, the validation it performs, and the post-patch operator smoke tests.

## Patches shipped with this repository

| Patch | Description |
|---|---|
| `patches/development-visibility/` | Adds the three knowledge-visibility classes (binding / development / historical), the dual-analysis review workflow, and the four-way gap classification. See `patches/development-visibility/README.md`. |

## Building a distributable zip

The patch bundle ships as a directory; producers turn it into a distributable zip via:

```bash
./tools/build-patch-zip.sh patches/development-visibility
# → dist/nexus-development-visibility-patch-v1.0.0.zip
```

Output goes to `dist/` by default; pass a second argument to override.

---

# Using the project ingestion skill

## What it is

`project-ingest` is an operational skill for adapting an existing project into the Nexus knowledge model.

It is intended for situations where:

- the repository already contains code;
- project documentation exists, but is inconsistent;
- there is little or no structured KB yet;
- legacy materials need to be reviewed and normalized.

## What it should do

The skill should perform a structured workflow:

1. inspect the workspace
2. classify the environment
3. ask the user the required project questions
4. inventory code and documents
5. classify source materials
6. extract canonical project knowledge
7. build or update `knowledge/`
8. identify legacy materials
9. compare code and docs for mismatches
10. produce an ingestion report

## What it should **not** do

The skill should not:

- silently delete old documentation
- silently move files without classification
- assume every existing markdown file is canonical
- invent architecture not supported by code or trustworthy docs

---

# Handling legacy documentation

This is one of the most important parts of the system.

Old documentation should usually be classified into one of these groups:

### `legacy_reference`
Useful historical material, but not canonical.

### `raw_source_material`
Input material that may contain facts, but has not been normalized.

### `obsolete_or_superseded`
Outdated material replaced by newer knowledge.

### `duplicate`
Redundant material that repeats content already captured elsewhere.

### `canonical_candidate`
A strong candidate for normalization into `knowledge/`.

---

## Recommended rule

> Old documentation must be classified before it is trusted.

That means the ingestion flow should first decide what a document **is**, and only then decide whether it belongs inside the knowledge system.

---

# Recommended workflow for a new project

1. Install the Nexus runtime.
2. Create the initial `knowledge/` skeleton.
3. Seed architecture, invariants, and startup docs.
4. Reload hooks with `/hooks`.
5. Start normal task work.
6. Update `knowledge/` as the project evolves.

---

# Recommended workflow for an existing project

1. Install the Nexus runtime.
2. Do **not** assume old docs are canonical.
3. Place the ingestion skill in the skills directory.
4. Run `/project-ingest`.
5. Review ingestion findings.
6. Normalize important knowledge into `knowledge/`.
7. Mark old docs as legacy/raw/archive where appropriate.
8. Continue normal work through the Nexus lifecycle.

---

# Minimal operator checklist

Use this checklist when enabling Nexus in a repository.

## Required
- [ ] `.claude/hooks/` copied
- [ ] `.claude/settings.json` present
- [ ] `knowledge/` created
- [ ] startup reading set exists
- [ ] `.nexus/state.json` ignored
- [ ] `/hooks` run after config install/update

## Recommended
- [ ] `CLAUDE.md` updated to point at Nexus
- [ ] `project-ingest` skill installed
- [ ] legacy docs classified
- [ ] canonical naming normalized
- [ ] at least one architecture doc and one invariant exist

---

# Naming recommendation

To avoid ambiguity, prefer the following canonical naming model:

- **System name:** Nexus knowledge runtime
- **Root directory:** `knowledge/`
- **Canonical term:** knowledge / knowledge base / knowledge system

Avoid mixing root concepts like:

- `world`
- `vault`

unless they are explicitly defined and intentionally preserved.

---

# Example: where to place the ingestion skill

A practical local placement is:

```text
.claude/skills/project-ingest.md
```

If you maintain reusable global skills, the same skill may also be placed in your global skills directory.

The exact loading behavior depends on your Claude environment, but the content of the skill should remain the same.

---

# Operational expectations

After installation, the repository should support this working mode:

- the agent starts a session;
- bootstrap forces minimum reading;
- mutating work requires an explicit context decision;
- turn closure requires a closure block;
- existing projects can be normalized through `project-ingest`;
- over time, `knowledge/` becomes the reliable project memory.

---

# Status of this repository

This repository is best understood as a **template and runtime kit** for installing Nexus into a project.

It gives you:

- the knowledge structure
- the enforcement hooks
- the runtime state model
- the operating discipline
- the project ingestion mechanism

It does **not** magically create a perfect knowledge base on its own.  
That still requires project-specific ingestion, review, and normalization.

---

# Final principle

The most important principle in this repository is:

> Do not rely on memory alone. Use the knowledge system.

