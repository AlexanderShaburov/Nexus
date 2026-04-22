---
name: project-ingest
description: Inspect an existing or partially documented project, classify code and documents, construct or update the Knowledge Vault, label non-canonical materials as legacy/source/archive, detect code↔documentation mismatches, and produce an ingestion report. Use this when a Knowledge Vault has been installed but the project already exists or contains pre-existing code/docs outside knowledge/.
license: Internal
---

# PROJECT KNOWLEDGE INGESTION

This skill adapts an **existing project** into a **knowledge-driven project**.

It is used **after** the Knowledge Vault / Nexus foundation exists, but **before** the agent can safely assume that `knowledge/` already reflects the real project.

The goal is **not** to copy everything into the Knowledge Vault.
The goal is to:

1. inspect the real project,
2. identify trustworthy sources,
3. extract canonical knowledge,
4. build or update `knowledge/`,
5. classify pre-existing materials correctly,
6. surface contradictions and unknowns,
7. leave the project in a state where `knowledge/` can become the operational source of truth.

---

# CRITICAL UNDERSTANDING

What exists before this skill runs:
- a real project may already exist,
- code may be ahead of documentation,
- documentation may be outdated, partial, duplicated, or contradictory,
- important knowledge may be scattered across README files, docs, plans, ADRs, notes, comments, config, and code structure,
- `knowledge/` may be empty, incomplete, or only contain the Nexus/system foundation.

What this skill must do:
- convert project understanding into structured operational knowledge,
- distinguish **canonical knowledge** from **legacy material**,
- avoid promoting uncertain or stale documents into canon without validation,
- preserve useful legacy material without allowing it to silently outrank `knowledge/`.

What this skill must NOT do:
- blindly move all documents into `knowledge/`,
- assume every markdown file is authoritative,
- invent architecture that is not supported by code or documents,
- silently resolve contradictions without naming them,
- destroy historical materials without explicit user intent.

---

# WHEN TO USE THIS SKILL

Use this skill when:
- the project already exists and a Knowledge Vault has just been installed,
- the project has code and/or documentation outside `knowledge/`,
- the user wants the agent to inspect and normalize an existing repository,
- the user wants the agent to build a Knowledge Vault from legacy project materials,
- the user wants code ↔ documentation inconsistencies surfaced before normal work continues.

---

# DO NOT USE THIS SKILL

Do **not** use this skill when:
- the project is already knowledge-driven and `knowledge/` is known to be current,
- the task is a normal feature, bugfix, refactor, or review,
- the user only wants one document summarized,
- the user only wants a small update to the existing Knowledge Vault.

For normal work, use the regular Knowledge Vault protocol instead.

---

# REQUIRED OUTCOMES

By the end of this skill, the agent must produce:

1. a workspace classification,
2. a project summary,
3. a source inventory,
4. a source classification,
5. a proposed or completed Knowledge Vault update,
6. a legacy handling decision,
7. a code ↔ documentation inconsistency list,
8. an ingestion report with next actions.

---

# SOURCE PRIORITY POLICY

This skill must enforce the following source-priority model:

## Canonical
Canonical operational knowledge belongs in `knowledge/`.
After ingestion, `knowledge/` should be treated as the operational source of truth.

## Legacy
Documents outside `knowledge/` that may still contain useful information but have not yet been normalized into canonical knowledge.
These should be treated as **legacy** unless explicitly promoted.

## Raw Source Material
External references, source dumps, exported notes, transcripts, copied research, or other material that may inform knowledge extraction but is not itself canonical.

## Archive / Obsolete
Documents known to be superseded, duplicated, or no longer relevant for current operation.

### Mandatory rule
A document found outside `knowledge/` MUST NOT become canonical merely because it exists.
It must first be evaluated, then either:
- normalized into `knowledge/`,
- kept as legacy,
- kept as raw source material,
- or marked/archive-handled as obsolete.

---

# FIXED VS VARIABLE

## FIXED (must always happen)
- inspect the workspace,
- determine whether this is an existing project,
- ask the user the required orientation questions,
- inventory code and documentation,
- classify sources,
- extract canonical knowledge,
- handle legacy materials explicitly,
- check code ↔ documentation alignment,
- produce an ingestion report.

## VARIABLE (depends on the project)
- exact languages/frameworks,
- exact document locations,
- exact Knowledge Vault files created or updated,
- exact scope of legacy material,
- exact number and severity of inconsistencies,
- whether documents are physically moved, only relabeled, or only reported.

---

# STEP 0 — ORIENT THE USER

Before doing heavy restructuring, the agent must orient the user.

If the workspace clearly looks like an existing project, ask a short confirmation question such as:

> I detect an existing project with code and/or documentation outside `knowledge/`. Do you want me to run Project Knowledge Ingestion: inspect the project, classify legacy materials, build/update the Knowledge Vault, and surface code ↔ documentation inconsistencies?

If the workspace is ambiguous, ask:

> I see partial project signals, but the situation is ambiguous. Should I treat this directory as an existing project to ingest, or as a new workspace that still needs initial project definition?

If the workspace is effectively empty, do not continue with this skill. Use a new-project / initial-bootstrap flow instead.

---

# STEP 1 — CLASSIFY THE WORKSPACE

Inspect the repository/workspace and classify it into one of:
- `existing_project`
- `new_or_empty_workspace`
- `uncertain`

Use evidence such as:
- repository structure,
- build files,
- source directories,
- config files,
- README/docs presence,
- existing planning/ADR materials,
- runtime/deployment files,
- prior project conventions visible in code.

Record a brief justification for the classification.

If classification is `new_or_empty_workspace`, stop this skill and recommend the correct initialization flow.

---

# STEP 2 — ASK THE REQUIRED USER QUESTIONS

Before canonicalizing knowledge, ask the user the minimum required orientation questions.

Ask only what is needed, but ensure the following are covered when not already obvious:

1. **Project identity**
   - What is this project called?
   - What is its main purpose?

2. **Project goals**
   - What is the current intended outcome or business/domain goal?

3. **Trust model**
   - Which existing documents do you trust most?
   - Are there documents or folders that are known to be stale, draft-only, or unreliable?

4. **Legacy handling preference**
   - Do you want legacy documents to be physically moved/labeled now, or only classified in the report first?

5. **Code vs docs authority**
   - If code and docs disagree, should I treat current code behavior as the stronger reference unless explicitly told otherwise?

If the user has already answered some of these in context, do not repeat them.

---

# STEP 3 — BUILD A SOURCE INVENTORY

Create an inventory of the project’s knowledge-bearing materials.

Include, where present:
- README files,
- docs folders,
- ADRs,
- planning docs,
- architecture docs,
- invariant/spec/protocol files,
- configuration files,
- deployment/runtime docs,
- major code entry points,
- module boundaries,
- comments that encode operational assumptions,
- existing `knowledge/` contents.

The inventory should separate at least:
- code sources,
- documentation sources,
- system/runtime/config sources,
- existing knowledge sources.

---

# STEP 4 — CLASSIFY EACH SOURCE

Classify each meaningful document/source into one of the following categories:

- `canonical_candidate`
- `legacy_reference`
- `raw_source_material`
- `duplicate`
- `obsolete_or_superseded`
- `unclear_needs_review`

Use the following heuristics:

## canonical_candidate
Use when a source appears well-maintained, consistent, and relevant to ongoing operation.

## legacy_reference
Use when a source may still contain important project knowledge, but cannot yet be treated as canonical.

## raw_source_material
Use when a source is informative but should not directly define operational truth.

## duplicate
Use when content materially duplicates another stronger source.

## obsolete_or_superseded
Use when the source is clearly outdated or replaced.

## unclear_needs_review
Use when the source may matter but confidence is too low.

The agent must explain non-obvious classifications briefly.

---

# STEP 5 — EXTRACT CANONICAL KNOWLEDGE

From the most trustworthy sources, extract the project’s canonical operational knowledge.

This typically includes:
- project purpose,
- domain model,
- architecture,
- major entities,
- key workflows,
- invariants,
- operational constraints,
- deployment/runtime assumptions,
- conventions,
- current known decisions.

When extracting knowledge:
- distinguish **observed** facts from **inferred** conclusions,
- avoid overstating confidence,
- prefer code-backed conclusions when documentation is weak,
- prefer explicit documentation when code intent is not obvious,
- surface contradictions rather than smoothing them over.

---

# STEP 6 — BUILD OR UPDATE THE KNOWLEDGE VAULT

Create or update `knowledge/` so that the important operational knowledge becomes structured and retrievable.

This may include creating or updating files under folders such as:
- `knowledge/index/`
- `knowledge/architecture/`
- `knowledge/invariants/`
- `knowledge/specs/`
- `knowledge/decisions/`
- `knowledge/plans/`
- `knowledge/domain/`
- other project-specific knowledge folders if they already exist

The agent must keep the Knowledge Vault **curated**.
Do not dump raw material into canonical files.

When creating/updating knowledge documents, ensure they are:
- scoped,
- non-duplicative,
- navigable,
- explicit about uncertainty,
- aligned with actual project evidence.

---

# STEP 7 — HANDLE LEGACY DOCUMENTATION EXPLICITLY

Legacy documentation must be handled intentionally.

## Default policy
If the user did not request destructive reorganization, the safe default is:
- do **not** delete,
- do **not** silently move,
- classify legacy docs in the report,
- recommend target placement.

## Possible legacy handling actions
Depending on user instruction and project norms, the agent may recommend or perform one of the following:

### Option A — Keep in place, mark as legacy
Use when reorganization should be minimal.

### Option B — Move under a legacy container
Examples:
- `docs/legacy/`
- `legacy/`
- `archive/legacy-docs/`

Use when the user wants structural cleanup.

### Option C — Split by status
Examples:
- `docs/legacy/`
- `docs/raw/`
- `docs/archive/`

Use when the corpus is large and mixed.

## Mandatory rule for old documentation
Old documentation should generally be treated as **legacy** until validated.
It may still be extremely useful, but it should not silently outrank the curated Knowledge Vault.

---

# STEP 8 — CHECK CODE ↔ DOCUMENTATION CONSISTENCY

Review whether the actual codebase matches the existing documentation and the newly extracted project understanding.

Identify at least these mismatch types:
- docs describe behavior not present in code,
- code implements behavior not documented,
- naming/entity drift,
- stale architecture descriptions,
- outdated workflow descriptions,
- contradictions between multiple documents,
- runtime/deployment mismatch,
- missing documentation for critical behavior.

Do not hide inconsistencies.
Surface them explicitly.

If appropriate, organize them as:
- confirmed inconsistency,
- probable inconsistency,
- open question needing user confirmation.

---

# STEP 9 — DEFINE THE POST-INGEST OPERATING MODE

At the end of ingestion, the agent must state clearly what should now be treated as the operational source of truth.

The default target state is:
- `knowledge/` = canonical operational memory,
- legacy docs = historical/supporting material,
- raw materials = input corpus,
- archive = non-operational material.

If the Knowledge Vault is still incomplete, the agent must say so explicitly and name what remains to be ingested or validated.

---

# STEP 10 — PRODUCE THE INGESTION REPORT

Produce a structured report that includes:

## Required sections
1. Workspace Classification
2. Project Summary
3. Source Inventory Summary
4. Source Classification Summary
5. Knowledge Vault Changes
6. Legacy Documentation Handling
7. Code ↔ Documentation Findings
8. Open Questions / Uncertainties
9. Recommended Next Actions
10. Post-Ingest Source-of-Truth Statement

The report must make it easy for the user to answer:
- What did you learn?
- What became canonical?
- What is still legacy?
- What disagrees with what?
- What should happen next?

---

# OUTPUT CONTRACT

When this skill completes successfully, the agent must provide:

1. a short executive summary,
2. the ingestion report,
3. the list of created/updated Knowledge Vault files,
4. the list of legacy-handling recommendations or changes,
5. the list of code ↔ documentation mismatches,
6. the recommended next action.

---

# QUALITY BAR

This skill must behave like a careful project archivist + systems analyst, not like a blind file mover.

It should feel:
- deliberate,
- evidence-based,
- conservative about canonization,
- explicit about uncertainty,
- respectful of project history,
- useful for immediate follow-up work.

The skill succeeds when the project becomes easier to navigate, easier to reason about, and safer to modify through the Knowledge Vault.

---

# OPTIONAL FOLLOW-UP ACTIONS

After successful ingestion, the agent may recommend:
- a second-pass KB refinement,
- targeted legacy migration,
- ADR extraction,
- invariant extraction,
- architecture/code audit,
- documentation debt cleanup,
- opening a tracked inconsistency list or remediation plan.

