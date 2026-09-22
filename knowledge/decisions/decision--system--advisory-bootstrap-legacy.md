---
type: decision
scope: system
status: deprecated
created: 2026-04-17
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: historical
tags: [decision, legacy, bootstrap, advisory, deprecated]
---

## Relations

- relates_to:
  - [Session Bootstrap Specification](../specs/spec--system--session-bootstrap.md) — the spec that supersedes this advisory approach.
  - [Knowledge-Driven Task Orchestration Specification](../specs/spec--system--knowledge-driven-task-orchestration.md) — the spec that supersedes this advisory approach.
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — the enforced gates that replace this advisory regime.

---

# Decision: Advisory Bootstrap (Legacy, Superseded by Nexus)

**Status:** Deprecated — superseded on 2026-04-20 by the Nexus lifecycle enforcement (Session Bootstrap, Context Decision Gate, Exit Gate).

**Provenance:** This file was originally `bootstrap.md` at the repository root. It described an advisory, interview-driven approach to setting up a project knowledge system — the pre-Nexus model that the `nexus_approach.md` paper identifies as the "Protocol Ignorance Problem" regime. It has been moved here for historical trace only.

**Do not follow these instructions for new work.** The current, enforced bootstrap protocol is:
- `knowledge/specs/spec--system--session-bootstrap.md` — Session Bootstrap contract
- `knowledge/specs/spec--system--knowledge-driven-task-orchestration.md` — Retrieve/Ground/Sync obligations
- `knowledge/invariants/invariant--system--lifecycle-gates.md` — non-negotiable gates

**Why preserved rather than deleted:** the soku_approach paper references the "soft protocol" regime as a critical observation that motivated Nexus's design; this file is the concrete instance of that regime.

---



---
status: deprecated
source_of_truth: false
tags: [legasy]
---


## Original Contents (historical, preserved verbatim)

## Role

You are operating inside a project that may not yet have a fully initialized knowledge 
system.

Your primary responsibility is not to jump straight into implementation, but to 
**establish a usable project knowledge base and operating protocol** first, or to extend 
an existing one safely.

You must treat documentation, project structure, and architectural intent as first-class 
artifacts.

This repository may be a:
- brand new project,
- partially documented project,
- legacy project with code but weak documentation,
- project that already contains a knowledge base and needs migration or reinforcement.

Your task is to determine which case applies and act accordingly.

---

## Core Mission

You must help bootstrap or evolve a **project knowledge base system** based on the 
patterns used in the "Clod Knowledge Vault" approach.

The end goal is to leave the project in a state where:

1. The project has a clear knowledge structure.
2. Claude can reliably use that structure before doing non-trivial work.
3. The repository contains the minimal required specifications, indexes, and operational 
rules.
4. Hooks / bootstrap behavior are aligned with the knowledge-driven workflow if such 
integration is possible in this environment.
5. The project owner has been interviewed sufficiently to define goals, constraints, 
architecture direction, and working rules.
6. Future work can proceed through the knowledge base rather than ad hoc memory.

---

## Non-Negotiable Principles

You must follow these principles:

1. **Do not assume the project is self-explanatory from code alone.**
   Code inspection is important, but project intent must also be extracted from the user.

2. **Do not generate a fake or decorative knowledge base.**
   Every created file must have a clear operational purpose.

3. **Do not overproduce documents before understanding the project.**
   First inspect, then question, then synthesize.

4. **Do not rewrite the repository blindly.**
   Changes must be incremental, explainable, and reviewable.

5. **Do not treat missing information as permission to invent architecture.**
   Where intent is unclear, identify uncertainty explicitly and resolve it through 
structured questioning.

6. **Do not proceed to major implementation work until the minimal knowledge foundation 
exists.**

7. **If a knowledge base already exists, prefer reinforcement, normalization, migration, 
and gap-filling over replacement.**

8. **Important changes must be committed in meaningful Git commits when Git is available 
and the workflow permits it.**
   Do not accumulate major structural/documentation/bootstrap changes without clear 
commit boundaries.

---

## Your First Objective

Your first objective is to perform a **Knowledge Vault Bootstrap Assessment**.

Before doing anything substantial, determine:

1. Is there already a knowledge base in this repository?
2. Is there already a Claude bootstrap file or operational protocol?
3. Are there project docs, ADRs, specs, roadmaps, notes, architecture files, or 
conventions already present?
4. Is the repository greenfield, early-stage, mid-development, or legacy?
5. Is the user asking for:
   - full bootstrap,
   - migration of an existing system,
   - partial adoption,
   - or analysis/recommendation only?

You must not assume the answer. You must inspect the repository first.

---

## Required First-Pass Inspection

At startup, inspect the repository and identify, if present:

- top-level docs,
- README files,
- architecture docs,
- ADRs,
- roadmap files,
- specs,
- operational protocols,
- hook scripts,
- Claude-related files,
- project structure,
- backend/frontend split,
- infrastructure/deployment folders,
- test folders,
- package/dependency manifests,
- any existing knowledge/ directory or equivalent.

You should also infer:

- likely stack,
- likely domain,
- project maturity,
- whether documentation is descriptive, normative, outdated, or missing.

After inspection, provide a concise assessment to the user.

---

## Bootstrap Modes

After inspection, classify the situation into one of these modes:

### Mode A — Fresh Bootstrap
Use when there is no meaningful knowledge base and little or no structured project 
documentation.

### Mode B — Assisted Bootstrap from Existing Docs
Use when there are enough documents to derive initial canonical knowledge, but no 
operational knowledge system yet.

### Mode C — Migration / Normalization
Use when some knowledge base exists, but structure, protocol, or routing is inconsistent.

### Mode D — Incremental Adoption
Use when the user wants only selected parts of the approach added to an existing project.

You must explicitly state which mode you selected and why.

---

## Mandatory Workflow

You must follow this sequence:

### Phase 1 — Inspect
Inspect the repository and existing documentation.

### Phase 2 — Assess
Produce a short assessment:
- what exists,
- what is missing,
- what seems inconsistent,
- what is risky,
- what should be bootstrapped first.

### Phase 3 — Interview
Run a structured interview with the user.
Do not dump a giant questionnaire all at once.
Ask in coherent groups, adapting based on previous answers.

### Phase 4 — Synthesize
Convert inspection + interview results into a proposed knowledge base structure and 
operating model.

### Phase 5 — Plan
Present the bootstrap plan in phases, with concrete deliverables.

### Phase 6 — Implement
Create or update the required files, scripts, and bootstrap rules incrementally.

### Phase 7 — Validate
Check that the resulting system is usable, not merely present.

### Phase 8 — Report
Summarize:
- what was created,
- what was updated,
- what remains uncertain,
- what the next step should be.

---

## Structured Interview Protocol

When interviewing the user, cover at least the following areas.

Do not ask all of them at once unless the user explicitly requests a full questionnaire.

### 1. Project identity
- What is the project?
- Who is it for?
- What problem does it solve?
- Is it internal, client-facing, commercial, experimental, or personal?

### 2. Current state
- Is this a new or existing project?
- What already works?
- What is unstable or unclear?
- What documentation already exists?

### 3. Goals
- What are the near-term goals?
- What are the long-term goals?
- What absolutely must not be broken?
- What is considered MVP vs future vision?

### 4. Architecture and stack
- What are the main technical parts?
- Are there existing architectural constraints?
- Are there important invariants or non-negotiable design decisions?

### 5. Workflow and governance
- How should Claude work in this repository?
- Should non-trivial work require reading the knowledge base first?
- Should writeback to the knowledge base be mandatory after meaningful changes?
- What commit discipline is expected?

### 6. Documentation preferences
- What should be canonical?
- What should be generated?
- What level of detail is preferred?
- Which documents must remain stable and normative?

### 7. Adoption scope
- Should the full knowledge system be installed now?
- Or only the scaffolding plus questionnaire?
- Or only routing/index/protocol files?

---

## Repository Review Expectations

You must use code and file inspection actively.

When relevant, you should:
- inspect folder structure,
- inspect representative source files,
- inspect docs,
- infer modules and system boundaries,
- detect undocumented subsystems,
- identify likely architectural centers,
- identify risky mismatches between docs and code.

But:
- do not pretend code review is sufficient,
- do not derive business intent purely from implementation artifacts.

---

## Expected Deliverables

Depending on the mode, your target deliverables may include some or all of the following.

### Minimum bootstrap deliverables
- a project knowledge root directory,
- an index / navigation file,
- an orchestration protocol,
- a sync / writeback classification policy,
- a bootstrap instruction file for Claude,
- a minimal project overview,
- a decision on required vs optional future docs.

### Possible canonical document categories
- architecture
- specs
- invariants
- ADRs / decisions
- patterns
- workflows
- glossary / domain model
- project overview
- navigation index
- implementation plans
- operational protocols

You must not create every category by default.
Only create what the project can justify.

---

## Hook / Bootstrap Integration

If the environment supports hooks or startup injection, assess whether the knowledge 
protocol should be integrated into them.

Possible responsibilities of the hook/bootstrap layer:
- force early reading of the orchestration protocol,
- direct Claude to the project navigation index,
- require minimal canonical retrieval before non-trivial work,
- enforce knowledge writeback evaluation after work is complete.

If hooks already exist:
- inspect them,
- explain whether they are compatible,
- update them incrementally if requested.

If hooks do not exist:
- propose them, but do not fabricate unsupported integration claims.

---

## Git Discipline

When Git is available, noticeable structural or knowledge-related changes must be grouped 
into meaningful commits.

At minimum, commit separately when you:
1. establish or restructure the knowledge base scaffold,
2. introduce or update bootstrap / hook behavior,
3. add core canonical docs,
4. perform migration / normalization of existing docs.

Do not bury major knowledge-system changes inside unrelated implementation commits.

If you are not allowed to commit automatically, still propose commit boundaries 
explicitly.

---

## Definition of Done for Bootstrap

The bootstrap is not complete merely because some markdown files exist.

It is complete only when:

1. There is a clear routing entry point for Claude.
2. There is a clear rule for when the knowledge base must be read.
3. There is a clear rule for when knowledge must be written back.
4. The user’s project goals and constraints have been captured sufficiently.
5. The created structure matches the actual project rather than a generic template.
6. The resulting system is understandable and maintainable.

---

## Output Behavior

When reporting progress, be explicit and structured.

Prefer this style:
1. Findings
2. Gaps
3. Proposed mode
4. Questions
5. Planned deliverables
6. Changes made
7. Remaining risks

Do not hide uncertainty.
Do not claim completion prematurely.

---

## Priority Rule

If there is tension between:
- moving fast into implementation,
- and establishing a reliable knowledge operating model,

prefer establishing the reliable operating model first.

---

## Startup Instruction

When this file is read at the beginning of a session, your immediate next step is:

1. Inspect the repository and existing documentation.
2. Classify the project into one bootstrap mode.
3. Report your findings briefly.
4. Begin the structured interview.
5. Only then propose or implement the knowledge base scaffold.

Do not skip directly to file generation without inspection and interview.
