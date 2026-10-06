---
type: spec
scope: system
status: draft
created: 2026-10-06
updated: 2026-10-06
source_of_truth: false
knowledge_visibility: development
theme: progressive-resolution
governs: [process/]
tags: [spec, process-space, charter, navigation, iteration, progressive-resolution, frontmatter]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — the `status` enum and the date rules are reused unchanged; the field set here is a separate contract for a separate directory.
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — defines what `knowledge/` is; this spec defines what it is not, and where that goes instead.
- constrains:
  - [Session Bootstrap Specification](spec--system--session-bootstrap.md) — once this spec is approved, the Mandatory Startup Reading Set grows by the process documents named in §7.
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — §8 bounds the Planning Artifacts rule by the charter's planning horizon.
- relates_to:
  - [Open question: progressive resolution](../open-questions/question--system--progressive-resolution.md) — the origin; reopened on 2026-10-06 by this spec.
  - [Nexus Update Specification](spec--system--nexus-update.md) — `process/` is project-owned, never a Nexus-owned unit (§2).
  - [Knowledge Visibility Specification](spec--system--knowledge-visibility.md) — `state` plays in `process/` the role `knowledge_visibility` plays in the vault; the two never appear together.

---

# Process Space Specification

## Purpose

The Knowledge Vault answers *what is known* about a project. It does not answer *what this project is for*, *how to treat it*, or *where it stands right now*. After Session Bootstrap the agent knows the rules (invariants, architecture, orchestration, index) and nothing about the project's position. The observed consequence is work that is correct by the rules and misaligned with the project: detail produced before the whole is visible, far-horizon questions designed before near ones are answered.

The **process space** is a second top-level directory, `process/`, that holds the project's *charter* (its nature, goals and policies), its *navigation* (where it is, where it is heading, what it deliberately ignores), and the coarse-to-fine documents that move between them: roadmaps and iterations.

This spec defines:

- the directory, its boundary with `knowledge/`, and who owns it (§1–§2);
- the document kinds and their filenames (§3);
- the frontmatter contract, including the `state` lifecycle that the vault does not have (§4–§5);
- the body shape of each kind (§6);
- who writes what, when (§7);
- what the runtime reads and when (§8), and the horizon rule that is the point of the whole thing (§9).

It is written at the resolution it recommends: four document kinds, no new gate, advisory runtime behaviour. Anything beyond that waits until this level shows what is missing (§11).

---

## 1. Placement and boundary

```
<project>/
  knowledge/      # what is known: facts, contracts, rationale, history
  process/        # what the project is for and where it stands
```

`process/` is a sibling of `knowledge/`, not a subdirectory of it. Vault rules do not apply inside it: no `<type>--<scope>--<name>` naming, no `source_of_truth`, no `knowledge_visibility`, no index entry, no relations block. The vault's `status` enum and date format are reused so that one head holds one set of words.

| Question | Lives in | Example |
|---|---|---|
| What is true about the system? | `knowledge/architecture/`, `specs/` | the hook reads `.nexus/state.json` |
| Why was it chosen? | `knowledge/decisions/` | why the gate accepts a Bash claim |
| What is still unknown? | `knowledge/open-questions/` | should Nexus work at progressive resolution? |
| What is this project, what counts as good, how do we validate, when is work done? | `process/charter.md` | an exploratory project; a level is done when its question has an answer |
| Where are we now, what single question is being tested, what do we ignore for now? | `process/navigation.md` | Position: two files exist and are read at bootstrap |
| What is the road, coarsely? | `process/roadmap--*.md` | trace from a folder → mail → CRM |
| What is the one-screen contract of the current step? | `process/iteration--*.md` | Trace v0 |

A document that states a fact about the system belongs in `knowledge/`, whatever its author intended. A document that states intent, position or policy belongs in `process/`. A roadmap in `knowledge/plans/` is legal and stays legal; this spec adds a place for the *coarse* road and the *current* step, it does not move existing plans.

## 2. Ownership

`process/` is **project-owned**. It is never a Nexus-owned unit in `nexus.manifest.json`; the updater never reads, compares or writes it. Installation into a host MAY create `charter.md` and `navigation.md` from templates when they are absent (`create-if-absent` semantics, as for `.nexus/README.md`) and MUST never touch them afterwards.

In the Nexus template repository itself, `process/` describes Nexus as a project. That is the first test of the format: if Nexus's own navigation does not fit on one screen, the format is wrong.

## 3. Document kinds

| `type` | Filename | Cardinality | Role |
|---|---|---|---|
| `charter` | `charter.md` | exactly one | nature of the project, goal, what counts as good, policies |
| `navigation` | `navigation.md` | exactly one | current position, heading, horizon, critical path, uncertainty and validation points |
| `roadmap` | `roadmap--<name>.md` | one per track | the whole road at low resolution |
| `iteration` | `iteration--<slug>.md` | many | one-screen contract of one step: question, input, deliberately ignored, artifact, success, unknowns |

Filenames are lowercase kebab-case. The two fixed files carry no suffix: there is only ever one of each. The other two carry `<type>--<name>.md` without a `scope` segment: the directory already belongs to one project, and directions inside the project are distinguished by the `track` field, not by the filename.

No other kind is defined. A fifth kind is added by amending this spec when a document is written that fits none of the four, not before.

## 4. Frontmatter

Every document in `process/` MUST begin with a YAML block. Two groups of fields answer two independent questions.

**What is this document, and is it agreed?**

| Field | Required | Values | Meaning |
|---|---|---|---|
| `type` | yes | `charter`, `navigation`, `roadmap`, `iteration` | document kind; MUST equal the filename prefix (or the fixed name) |
| `status` | yes | `draft`, `review`, `approved`, `deprecated` | maturity of the document: has the operator agreed to it? Same closed enum as the vault; `in-progress` is not used here because the work's progress is `state` |
| `owner` | yes | `operator`, `agent` | who may change the document without asking in the turn |

**Where does the work stand?**

| Field | Required | Values | Meaning |
|---|---|---|---|
| `state` | yes | `active`, `planned`, `in_progress`, `done`, `deferred`, `dropped`, `superseded` | lifecycle of the work the document describes (§5) |
| `horizon` | `roadmap`, `iteration` | `near`, `mid`, `far` | how close the subject is to observed reality, and therefore how much resolution it may receive (§9) |
| `track` | no | kebab-case slug | the direction inside the project this document belongs to |
| `review_by` | no | `YYYY-MM-DD` | after this date the document is *unconfirmed* until the operator re-confirms it, whatever `updated` says |
| `closed` | when `state` is `done`, `dropped` or `superseded` | `YYYY-MM-DD` | when the work ended |

**Dates and links**

| Field | Required | Values | Meaning |
|---|---|---|---|
| `created` | yes | `YYYY-MM-DD` | as in the vault |
| `updated` | yes | `YYYY-MM-DD` | bumped on every meaningful change; never earlier than `created` |
| `part_of` | no | list of repo-relative paths | what this belongs to: an iteration to a roadmap, a roadmap to the charter |
| `depends_on` | no | list of repo-relative paths | what must be done first |
| `superseded_by` | when `state: superseded` | one repo-relative path | the document that replaced this one |
| `refs` | no | list of repo-relative paths | vault documents this rests on or produced |
| `tags` | no | list | as in the vault |

Unknown fields are an error. `source_of_truth`, `knowledge_visibility`, `plan_status` and the `type: feedback` fields MUST NOT appear in `process/`: their questions are answered by `state` and `owner` here.

Example, charter:

```yaml
---
type: charter
status: approved
state: active
owner: operator
created: 2026-10-06
updated: 2026-10-06
review_by: 2027-01-06
---
```

Example, iteration:

```yaml
---
type: iteration
status: approved
state: in_progress
owner: agent
horizon: near
track: trace
created: 2026-10-06
updated: 2026-10-06
part_of: [process/roadmap--trace.md]
depends_on: []
refs: [knowledge/open-questions/question--system--progressive-resolution.md]
---
```

## 5. The `state` lifecycle

`state` is the field the vault lacks: not *is this document mature* but *where is this work*.

| `type` | Allowed `state` | Transitions |
|---|---|---|
| `charter`, `navigation` | `active` only | none: the single instance is always in force; it is edited, never closed |
| `roadmap` | `active`, `superseded` | `active → superseded` with `superseded_by` and `closed` |
| `iteration` | `planned`, `in_progress`, `done`, `deferred`, `dropped`, `superseded` | `planned → in_progress → done`; `in_progress → deferred → in_progress`; any → `dropped`; any → `superseded` |

Meaning of each value:

- `active` — in force now.
- `planned` — agreed, not started.
- `in_progress` — being worked; the navigation's current step points here.
- `done` — the iteration's question has an answer (not: all its ideas are implemented). `closed` set.
- `deferred` — paused with a stated condition for resuming, in the body under `## Deferred until`. Still a process document, still visible.
- `dropped` — abandoned; the body keeps one line on why. `closed` set.
- `superseded` — replaced by another document; `superseded_by` and `closed` set.

**Boundary with `knowledge/open-questions/`.** An iteration that has a contract (a question, an input, a success criterion) and is paused stays in `process/` as `deferred`. An idea that has no contract yet, or that sits beyond the current horizon, goes to `knowledge/open-questions/` as one line or one short note. The test is: *could the agent start this tomorrow from the document alone?* Yes → `process/`; no → `open-questions/`.

**Actuality.** A document is *current* when its `state` is `active` or `in_progress`, and either `review_by` is absent or in the future. A document past its `review_by` is *unconfirmed*: the runtime may say so (§8), nothing else changes until the operator re-confirms by bumping `review_by` and `updated`.

## 6. Body shape

Each kind has a fixed set of H2 sections, in order, each present even when short. The whole document SHOULD fit on one screen; a charter section is one to three lines, not an essay. The constraint is the point: the moment a section wants to become a chapter, that chapter is knowledge and belongs in `knowledge/`.

### `charter.md`

- `## Nature` — repeatable, exploratory, or mixed. Do we know how to do this at the start?
- `## Goal` — what the project is for, and what a good outcome looks like.
- `## Validation policy` — how a discovery or hypothesis is checked before it counts.
- `## Planning horizon` — how far ahead is elaborated, and in which unit (one iteration, one phase, one quarter).
- `## Definition of done` — when a piece of work is closed.
- `## Goal-change policy` — who may change this charter, under what conditions, and how the change is recorded.

### `navigation.md`

- `## Now` — three labelled lines, read by the runtime (§8): `Position:` where the project really is, as facts; `Heading:` the one question being tested, with a pointer to the `in_progress` iteration; `Ignoring:` what is deliberately out of scope at this level.
- `## Horizon` — what is visible ahead but not elaborated, one line each.
- `## Critical path` — the few things that must happen in order.
- `## Uncertainty points` — what we may not know enough about, including whether the project is feasible as currently conceived.
- `## Validation points` — where and how we will see whether we are on track.

### `roadmap--<name>.md`

- `## Road` — the levels in order, one line each, each marked `near`, `mid` or `far`.
- `## Done` — levels completed, with their iteration links.

A roadmap is coarse by contract. A level marked `far` is one line. Elaboration happens in an iteration, when the level becomes `near`.

### `iteration--<slug>.md`

The one-screen contract:

- `## Question` — the single question this iteration answers.
- `## Input` — what it starts from.
- `## We deliberately ignore` — the list that protects the iteration from premature complexity.
- `## Artifact` — what exists afterwards that did not before.
- `## Success` — how we know the question is answered.
- `## Unknowns to observe` — what to watch for; feeds the next iteration or `open-questions/`.
- `## Deferred until` — present only when `state: deferred`.

## 7. Who writes what, when

| Document | Created by | Changed by | When |
|---|---|---|---|
| `charter.md` | operator and agent in dialogue, at install or at the first session that finds it missing | operator (`owner: operator`): the agent proposes a change in text and does not edit the file | rarely; by the charter's own goal-change policy |
| `navigation.md` | agent, from the charter and the current state of the repository, confirmed by the operator | agent (`owner: agent`), as part of the Exit Gate writeback evaluation, whenever the position moved | at closure of meaningful work |
| `roadmap--*.md` | agent, on operator agreement | agent; a level's `near`/`mid`/`far` mark changes only with the operator's agreement | when a level is done or the road changes |
| `iteration--*.md` | agent, on operator agreement, from the one-screen contract | agent for `state` transitions and `## Unknowns to observe`; the contract sections change only with the operator's agreement | at start, at pause, at close |

`owner: operator` is a rule of this spec, not a gate: the agent reads it and proposes instead of editing. It becomes a tool-gate denial only if this level shows that the rule is not enough (§11).

The writeback evaluation that the Exit Gate already requires gains one question: *did the project's position move, and does `navigation.md` say so?* This is advisory and lives in the spec text, not in the Closure Block.

## 8. What the runtime reads

Contract for the hooks; realization status in §10.

1. **Session Bootstrap** (`SessionStart`, `PreCompact`): when `process/charter.md` exists, the Mandatory Startup Reading Set includes `process/charter.md`, `process/navigation.md`, and every `process/iteration--*.md` with `state: in_progress`. When `charter.md` is absent, bootstrap says so in one line and nothing else changes: a project without a charter is a project that has not decided what it is, which is allowed.
2. **PreCompact** is the critical point: compaction loses position first. The full `navigation.md` returns there.
3. **Per turn** (`UserPromptSubmit`): the three lines of `## Now` from `navigation.md`, verbatim, after the turn contract. Not the whole file: the cost repeats every turn.
4. **Staleness** (`SessionStart` only, advisory, one line): any `process/` document whose `review_by` has passed, and any `iteration` with `state: in_progress` whose `updated` is older than 14 days. The number is a first guess and is changed here when it proves wrong.
5. **Validation** (`PostToolUse`, advisory, as for the vault): the rules of §4–§6 as a second rule set in `tools/validate-vault.py`, selected by the `process/` path, with codes `PR…`. The CLI validates both directories in one run.

Nothing in `process/` is ever gated. The runtime reads it, reports on it, and never blocks on it.

## 9. The horizon rule

This is the lever the rest exists for.

- `horizon: far` → the document, or the roadmap line, is at most a few lines: a name, a question, why it matters. No design, no options, no sub-steps.
- `horizon: mid` → the question and the unknowns may be elaborated; the solution may not.
- `horizon: near` → full one-screen iteration contract; a plan in `knowledge/plans/` may exist for it.

The agent reads the charter's planning horizon and the iteration's `horizon` before elaborating anything, and declines to elaborate beyond them. The refusal is explicit: *this is beyond the current horizon; recorded as one line in the roadmap / open-questions*. This is not a loss of information: the line is kept, the elaboration waits until reality has produced a need for it.

**Amendment to the Planning Artifacts rule.** `spec--system--knowledge-driven-task-orchestration.md` requires a structured multi-step answer to be externalized as a plan. In a project with a charter, that rule is bounded: a plan covers at most the current iteration (`horizon: near`). Structured thoughts about later levels go to the roadmap as one line each, not to `plans/`. When this spec is approved, the orchestration spec is amended to say so.

## 10. Validation rules

For `tools/validate-vault.py`; codes reserved here so that the implementation and the spec agree from the start.

| Code | Rule |
|---|---|
| `PR001` | required fields present: `type`, `status`, `state`, `owner`, `created`, `updated` |
| `PR002` | `type` in the four kinds; `status` in the vault enum minus `in-progress`; `state` in the seven values; `owner` in `operator`, `agent`; `horizon` in `near`, `mid`, `far` |
| `PR003` | `type` agrees with the filename: `charter.md`, `navigation.md`, `roadmap--*.md`, `iteration--*.md` |
| `PR004` | `state` is allowed for the `type` (§5 table) |
| `PR005` | `closed` present iff `state` is `done`, `dropped` or `superseded`; `superseded_by` present iff `state: superseded` |
| `PR006` | `horizon` present on `roadmap` and `iteration`; absent elsewhere |
| `PR007` | no vault-only field (`source_of_truth`, `knowledge_visibility`, `plan_status`, feedback fields) and no unregistered field |
| `PR008` | dates are `YYYY-MM-DD`; `updated ≥ created`; `closed ≥ created` |
| `PR009` | the body carries the fixed H2 sections of §6 for its `type`, in order |
| `PR010` | `part_of`, `depends_on`, `refs`, `superseded_by` point at existing files |
| `PR100` | warning: `review_by` has passed |
| `PR101` | warning: `iteration` in `in_progress` with `updated` older than 14 days |
| `PR102` | warning: `charter.md` exists and `navigation.md` does not, or vice versa |

## 11. Realization status and what waits

| Item | Status on 2026-10-06 |
|---|---|
| this spec | draft; becomes `approved` after the two fixed files exist for Nexus itself and have survived a few sessions |
| `process/charter.md`, `process/navigation.md` for Nexus | next step, hand-written in dialogue |
| validator rule set `PR…` | pending; after the two files exist |
| bootstrap and PreCompact reading (§8.1–8.2) | pending |
| per-turn `## Now` digest (§8.3) | pending |
| staleness line (§8.4) | pending |
| install templates for hosts (§2) | pending; after the Nexus files prove the shape |
| amendment to the orchestration spec (§9) | with approval of this spec |

Deliberately **not** in this version, and only added when this level shows the need: a fifth Closure Block field, a tool-gate denial for `owner: operator`, a `process/` index, relations blocks, per-track navigation files, any kind beyond the four.
