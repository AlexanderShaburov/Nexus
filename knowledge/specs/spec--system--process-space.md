---
type: spec
scope: system
status: draft
created: 2026-10-06
updated: 2026-10-09
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
  - [Decision: What the second layer of Nexus is for](../decisions/decision--system--second-layer-purpose.md) — the 2026-10-09 revision of the purpose: joint management, the cycle, the gate deferred.
  - [Open question: progressive resolution](../open-questions/question--system--progressive-resolution.md) — the origin; reopened on 2026-10-06 by this spec.
  - [Nexus Update Specification](spec--system--nexus-update.md) — `process/` is project-owned, never a Nexus-owned unit (§2).
  - [Knowledge Visibility Specification](spec--system--knowledge-visibility.md) — `state` plays in `process/` the role `knowledge_visibility` plays in the vault; the two never appear together.

---

# Process Space Specification

## Purpose

The Knowledge Vault answers *what is known* about a project. It does not answer *what this project is for*, *how to treat it*, or *where it stands right now*. After Session Bootstrap the agent knows the rules (invariants, architecture, orchestration, index) and nothing about the project's position. The observed consequence is work that is correct by the rules and misaligned with the project: detail produced before the whole is visible, far-horizon questions designed before near ones are answered.

The **process space** is a second top-level directory, `process/`, that holds the project's *charter* (its nature, goals and policies), its *navigation* (where it is, where it is heading, what it deliberately ignores), and the coarse-to-fine documents that move between them: roadmaps and iterations.

Carrying the position is necessary and not the point. The directory exists to serve **joint management of the project** by operator and agent (`decisions/decision--system--second-layer-purpose.md`, 2026-10-09): continuous management activity in which both define and refine goals, assess the position, plan the next intermediate result, choose the work, hold the direction and revise the route. The agent carries a substantial share of that work and proposes; the operator understands and decides. The documents below are the written account of that activity, kept so that at every significant step both can say where the project is, where and why it is moving, what result the next work should produce, how it will be used, and whether detail has come too early. The method is the management cycle, stated first.

This spec defines:

- the management cycle the directory serves (§0);
- the directory, its boundary with `knowledge/`, and who owns it (§1–§2);
- the document kinds and their filenames (§3);
- the frontmatter contract, including the `state` lifecycle that the vault does not have (§4–§5);
- the body shape of each kind (§6);
- who writes what, when (§7);
- what the runtime reads and when (§8), and the horizon rule that is the point of the whole thing (§9).

It is written at the resolution it recommends: four document kinds, no new gate, advisory runtime behaviour. Anything beyond that waits until this level shows what is missing (§11).

---

## 0. The management cycle

The second layer organizes project work as an **iterative cycle with a bounded horizon of justified planning**. The cycle is the same for a research project with high uncertainty and for a project with a known way to its goal; only the horizon differs. Each step names the document that carries it (§3).

1. **Strategic goal.** A managed project has an explicitly stated strategic goal: without it there is no way to choose a direction or judge progress. The operator may refine or revise it; it is never replaced silently in the course of particular tasks. Carried by `charter.md` (`## Goal`); a change is recorded as a decision in the vault. A project without a charter has not decided what it is; the second layer is simply not active there.
2. **Position and circumstances.** Operator and agent assess where the project is relative to the goal: results obtained, knowledge held, significant uncertainties, resources, constraints, strengths, weaknesses, opportunities and threats, as far as they matter. For a research project the position is the set of established results and the critical uncertainties still open; for a project with a known path it is the milestones reached. The agent does the analytical and preparatory work and proposes conclusions and alternatives; the operator takes part in judging them. The depth of the assessment is set by real need, never by a fixed procedure. Carried by `navigation.md` (`Position:` and the marking of the net).
3. **Planning horizon.** From what is known, the limit is set within which further action can be planned with justification. The unknown part of the route is not described in detail in advance; beyond the horizon there may be presumed stages, hypotheses and directions, with no false precision. Carried by the charter's `## Planning horizon` and by the `horizon` field of roadmaps and iterations (§9).
4. **Nearest intermediate goal and milestones.** Within the horizon, operator and agent state the nearest significant goal: a result whose achievement lets the project advance to the strategic goal with justification. The intermediate results, milestones, significant dependencies and conditions of achievement are named. A milestone marks a substantive result or decision, not an amount of work done; a negative result of an investigation is a full result when it removes an uncertainty and lets a decision be taken. One nearest goal at a time at this level; whether more than one line of work fits the format is an open uncertainty. Carried by `navigation.md` (`Heading:`, `Why here:`, the places and transitions of the net).
5. **Planning and execution.** For the chosen goal the necessary structure of tasks and work is formed, with expected results and dependencies. The agent proposes the plan and the means, takes on the organizational and technical work, and keeps the operator able to choose and to check with understanding. Every significant piece of work keeps its link to the strategic goal, the nearest milestone and the expected result. Depth of elaboration matches present need: detailed specifications, formats and component architecture wait until the significant questions they depend on are resolved. This is not a prohibition on research: when there is a justified reason to change the scale or the direction of the work, the agent says so and proposes options, and the operator decides (§9). Carried by `iteration--*.md`.
6. **Evaluation and route revision.** Work continues until the intermediate or strategic goal is reached, or until circumstances significantly change what the previous route can achieve or whether it is worth following. At the revision point operator and agent evaluate the results and the new knowledge, compare the expected result with the obtained one and feed the deviation into further planning, check the previous assumptions, restate the position relative to the strategic goal, revise the goal or the route where needed, set a new horizon and form the next stretch of work. Then the cycle repeats. A revision is triggered by a milestone reached, a significant obstacle, new knowledge that changes assumptions, or the initiative of either side; the agent may propose a revision at any time, and the operator decides. Carried by the closure of an iteration and the rewrite of `navigation.md` (§7).

The net in `navigation.md` is the internal representation of states, results, transitions and dependencies that this cycle produces: an instrument of account and analysis, not a system of permissions and prohibitions. The first layer is strict about integrity of knowledge; the second is disciplined about purpose and flexible about path.

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
| Where are we now, what single question is being tested, why there and now, what do we ignore for now? | `process/navigation.md` | Position: two files exist and are read at bootstrap |
| What is the road, coarsely? | `process/roadmap--*.md` | trace from a folder → mail → CRM |
| What is the one-screen contract of the current transition? | `process/iteration--*.md` | Net paper test |

A document that states a fact about the system belongs in `knowledge/`, whatever its author intended. A document that states intent, position or policy belongs in `process/`. A roadmap in `knowledge/plans/` is legal and stays legal; this spec adds a place for the *coarse* road and the *current* step, it does not move existing plans.

## 2. Ownership

`process/` is **project-owned**. It is never a Nexus-owned unit in `nexus.manifest.json`; the updater never reads, compares or writes it. Installation into a host MAY create `charter.md` and `navigation.md` from templates when they are absent (`create-if-absent` semantics, as for `.nexus/README.md`) and MUST never touch them afterwards.

In the Nexus template repository itself, `process/` describes Nexus as a project. That is the first test of the format: if Nexus's own navigation does not fit on one screen, the format is wrong.

## 3. Document kinds

| `type` | Filename | Cardinality | Role |
|---|---|---|---|
| `charter` | `charter.md` | exactly one | nature of the project, goal, what counts as good, policies |
| `navigation` | `navigation.md` | exactly one | current position, heading, the net of project states and transitions, uncertainty and validation points |
| `roadmap` | `roadmap--<name>.md` | one per track | the whole road at low resolution |
| `iteration` | `iteration--<slug>.md` | many | one-screen contract of one transition of the net: question, input, work, deliberately ignored, artifact, success, unknowns |

Filenames are lowercase kebab-case. The two fixed files carry no suffix: there is only ever one of each. The other two carry `<type>--<name>.md` without a `scope` segment: the directory already belongs to one project, and directions inside the project are distinguished by the `track` field, not by the filename.

No other kind is defined. A fifth kind is added by amending this spec when a document is written that fits none of the four, not before.

Besides the four kinds, the directory holds one `README.md`: a few lines for a person opening the directory, naming the two fixed files and pointing here. It carries no frontmatter, is not a document kind, and the validator (§10) ignores it.

## 4. Frontmatter

Every document in `process/` MUST begin with a YAML block. Two groups of fields answer two independent questions.

**What is this document, and is it agreed?**

| Field | Required | Values | Meaning |
|---|---|---|---|
| `type` | yes | `charter`, `navigation`, `roadmap`, `iteration` | document kind; MUST equal the filename prefix (or the fixed name) |
| `status` | yes | `draft`, `review`, `approved`, `deprecated` | maturity of the document: has the operator agreed to it? Same closed enum as the vault; `in-progress` is not used here because the work's progress is `state` |
| `owner` | yes | `operator`, `agent` | who may change the document without asking in the turn |
| `id` | `iteration` | `T<n>` | the transition in `navigation.md` `## Net` that this iteration is the contract of; MUST exist there |

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
id: T2
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

**Cold-readability rule.** A process document MUST be understandable to a reader who has only `charter.md` and the document itself: no session context, no memory of the conversation that produced it. In practice: name the current change and say which step of it has been reached, not only the landmarks around it; explain every tool, code or internal name in the same sentence or leave it out; write "ignoring" items as what they are, not as labels. The first navigation written for Nexus failed this test on its first review (landmarks without the change they belonged to, and four unexplained labels under *Ignoring*), which is why the rule is here.

### `charter.md`

- `## Nature` — repeatable, exploratory, or mixed. Do we know how to do this at the start?
- `## Goal` — what the project is for, and what a good outcome looks like.
- `## Validation policy` — how a discovery or hypothesis is checked before it counts.
- `## Planning horizon` — how far ahead is elaborated, and in which unit (one iteration, one phase, one quarter).
- `## Definition of done` — when a piece of work is closed.
- `## Goal-change policy` — who may change this charter, under what conditions, and how the change is recorded.

### `navigation.md`

- `## Now` — four labelled lines, read by the runtime (§8): `Position:` where the project really is, as facts; `Heading:` the one question being tested, with a pointer to the `in_progress` iteration; `Why here:` why this question now and not another, in terms of the charter's goal and the critical path, so that going deep here is distinguishable from burrowing; `Ignoring:` what is deliberately out of scope at this level. The `Why here` line was added on 2026-10-06 after the first cold reading of Nexus's own navigation: the agent stated the position correctly and could not say why the project worked there.
- `## Net` — the project as a net of states and transitions, in the sense of a Petri net: places are project states, transitions are work, the marking is the position. Two lists with a one-line grammar, readable by eye and by a regular expression:

  ```
  - [x] P<n> <slug> — <phrase>. check: <what established it>
  - [ ] P<n> <slug> — <phrase>
  - T<n> <slug>: <P..> → <P..>  [!] [?] [← now] — <phrase>
    task: process/iteration--<slug>.md
  ```

  A marked place MUST carry `check:`. `!` marks a critical transition: every path from the marking to the goal passes through it. `?` marks a transition whose feasibility is unknown. `← now` marks the one transition being worked; it MUST be *enabled*, that is, all its input places marked, or the file is invalid. This is a check on the honesty of the account, not a permit for the work: a file that calls current a step whose inputs are not established misstates the position, and the remedy is to correct the net (mark what is established, with its check, or redraw the route), never to stop the work. The net describes; it does not grant or deny. The `task:` line names the iteration contract; it is required on the `← now` transition, allowed on the next one, and absent further out (§9). The net replaced the earlier `## Horizon` and `## Critical path` sections on 2026-10-06: a critical path is a degenerate net, and a far place is simply an unmarked place that no elaborated transition leads to yet. Graph structure (inputs, outputs, what a transition unlocks) lives only here; the iteration file never restates it.
- `## Uncertainty points` — what we may not know enough about, including whether the project is feasible as currently conceived.
- `## Validation points` — where and how we will see whether we are on track.

### `roadmap--<name>.md`

- `## Road` — the levels in order, one line each, each marked `near`, `mid` or `far`.
- `## Done` — levels completed, with their iteration links.

A roadmap is coarse by contract. A level marked `far` is one line. Elaboration happens in an iteration, when the level becomes `near`.

### `iteration--<slug>.md`

The one-screen contract:

- `## Question` — the single question this iteration answers.
- `## Input` — what it starts from, as prose; the input places are in the net.
- `## Work` — what will actually be done: the length of the step, not its direction.
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

The writeback evaluation that the Exit Gate already requires gains one question: *did the project's position move, and does `navigation.md` say so?* At the closure of an iteration a second one: *does the obtained result match the expected one, and where it does not, what does the deviation change in the plan?* (§0, step 6). Both are advisory and live in the spec text, not in the Closure Block.

**Marking rule.** A place changes from `[ ]` to `[x]` only at the closure of the turn that established it, only with its `check:`, and the `← now` mark moves in the same edit. The charter's validation policy applies: a check is real work observed, never a specification or a selftest alone.

## 8. What the runtime reads

Contract for the hooks; realization status in §10.

1. **Session Bootstrap** (`SessionStart`, `PreCompact`): when `process/charter.md` exists, the Mandatory Startup Reading Set includes `process/charter.md`, `process/navigation.md`, and every `process/iteration--*.md` with `state: in_progress`. When `charter.md` is absent, bootstrap says so in one line and nothing else changes: a project without a charter is a project that has not decided what it is, which is allowed. *Realized 2026-10-09*: `nexus-bootstrap.py` lists the documents as items 5 and following of STEP 1 and records them in the session state's `required_files`; the tool gate's read ledger must cover them before bootstrap completes; the prompt gate names the unread ones; after the confirmation block the agent states the position in two sentences. Mirrored in `spec--system--session-bootstrap.md`.
2. **Compaction** is the critical point: it loses position first. The full `navigation.md` returns right after it. *Realized 2026-10-09* by the same mechanism: the reading set is injected by the `SessionStart` hook, which Claude Code fires after compaction with `source: compact`; the `PreCompact` run of the same hook only resets the session state before compaction and prints nothing, because the installed Claude Code rejects `hookSpecificOutput` for that event (found in the first live check, 2026-10-09).
3. **Per turn** (`UserPromptSubmit`): the four lines of `## Now` from `navigation.md`, verbatim, after the turn contract. Not the whole file: the cost repeats every turn.
4. **Staleness** (`SessionStart` only, advisory, one line): any `process/` document whose `review_by` has passed, and any `iteration` with `state: in_progress` whose `updated` is older than 14 days. The number is a first guess and is changed here when it proves wrong.
5. **Validation** (`PostToolUse`, advisory, as for the vault): the rules of §4–§6 as a second rule set in `tools/validate-vault.py`, selected by the `process/` path, with codes `PR…`. The CLI validates both directories in one run.

6. **Position gate** (`PreToolUse`), **a deferred hypothesis, not part of the route** since 2026-10-09. The design is kept so that it need not be reinvented: the Context Decision claim (`spec--system--context-decision-gate.md`, Form A) gains `--step T<n>`. Before the first mutating call of a turn the gate reads `## Net` and denies, naming the defect, when the transition is unknown, when an input place is unmarked, when the transition has already fired (all outputs marked), or when it has no `task:` contract. Two escape hatches, both explicit and both printed in full so the operator sees them: `--step none --reason` for work that changes no project state, and `--override --reason` for firing a transition that is not enabled. The gate checks structure, never words: what it verifies are facts about the net, not the agent's assertion that the work is on the path. Designed 2026-10-06. It is built only if real work shows that steering as agent behaviour (the experimental `## Steering` section of `CLAUDE.md`, 2026-10-08) does not hold the direction without it; the condition and the evidence are recorded in `navigation.md` when they appear.

Nothing in `process/` is gated, then, at this level. Everything is read, reported on, and never blocked on. The history of this paragraph is the history of the layer's purpose: the first version said nothing is gated; the dialogue of 2026-10-06 reversed that for the position decision, on the assumption that every rule Nexus leaves to goodwill turns into a ritual; the revision of 2026-10-09 (`decisions/decision--system--second-layer-purpose.md`) found that assumption unchecked and the first evidence pointing the other way, and returned the gate to the status of a hypothesis. Formal checks of the net's state (§6, §10) verify that the account is consistent; they never become a prohibition on changing the direction of work.

## 9. The horizon rule

This is the lever the rest exists for. It rests on a principle agreed on 2026-10-06, stated first.

**Critical transition first.** A transition is critical when every path from the current marking to the goal passes through it. Criticality is a property of position in the net, not of difficulty or cost. The dangerous case is a critical transition whose feasibility is unknown: everything done around it is pseudo-progress, real work without movement, because the place everything depends on stays unmarked. Therefore: critical transitions are identified before anything else, which is why the net exists from the first day and not "when more than one step is visible"; for a critical transition of unknown feasibility the first work the agent proposes is to establish whether it can fire at all, at the coarsest sufficient precision, and it names work downstream of it as resting on nothing yet; and infeasibility is a signal, not a failure, with three exits (solve the transition another way, rebuild the net so the path to the goal bypasses it, or admit that the goal in this form does not exist), chosen by the operator but raised by the agent, loudly and first, because people work where it is clear rather than where it is frightening. The horizon rule below is this principle applied to resolution: a place whose inputs are unmarked is described in one line, because any more precision rests on nothing.

- `horizon: far` → the document, or the roadmap line, is at most a few lines: a name, a question, why it matters. No design, no options, no sub-steps.
- `horizon: mid` → the question and the unknowns may be elaborated; the solution may not.
- `horizon: near` → full one-screen iteration contract; a plan in `knowledge/plans/` may exist for it.

The agent reads the charter's planning horizon and the iteration's `horizon` before elaborating anything. When the work asked for, or the work it is about to do, goes beyond them, it does not refuse and does not comply silently: it says so, explains the risk of premature detail (precision that rests on an unchecked assumption, and the work that will be redone when the assumption falls), proposes the scale that fits the horizon, and offers the choice: continue, defer, or change the route. The operator chooses, knowingly, and the agent does what was chosen. The default proposal is *one line in the roadmap or in open-questions now, elaboration when reality has produced a need for it*; the line is kept, so nothing is lost. The first version of this rule (2026-10-06) made the refusal explicit and mandatory; the revision of 2026-10-09 replaced it by warning and the operator's choice, because research needs no permission to begin and a change of direction is a management decision, not a violation.

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
| `PR011` | `## Net` parses under the grammar of §6; every place and transition id is unique; every transition input and output names an existing place; a marked place carries `check:` |
| `PR012` | exactly one `← now` transition, and it is enabled; its `task:` file exists and carries the matching `id` |
| `PR013` | an `iteration` with `id` names a transition that exists in the net |

## 11. Realization status and what waits

| Item | Status on 2026-10-09 |
|---|---|
| this spec | draft; the purpose and the cycle (§0) were revised on 2026-10-09 with the charter; becomes `approved` after the full cycle has run once in real work |
| `process/charter.md`, `process/navigation.md` for Nexus | written 2026-10-06; charter's Goal restated 2026-10-09; navigation's route redrawn from the new goal the same day |
| the net's paper test (P5 in Nexus's own net) | deferred 2026-10-09 with the gate; paper half held, cold reading failed; contract `process/iteration--net-paper-test.md` |
| alignment of the foundations with the new purpose | in progress 2026-10-09; contract `process/iteration--foundations-alignment.md` |
| the full cycle run once in real work | in progress 2026-10-09; the critical transition of unknown feasibility; the work inside it is §8.1–8.2; contract `process/iteration--run-cycle.md` |
| agent behaviour (steps 2, 5, 6 of §0 in the turn) | experimental `## Steering` section in `CLAUDE.md`, 2026-10-08; a habit under test, not a contract; this spec gains a behavioural section only if the habit proves worth a contract |
| position gate (§8.6) | deferred hypothesis; built only if the habit proves insufficient |
| validator rule set `PR…` | pending; after the two files exist |
| bootstrap and PreCompact reading (§8.1–8.2) | built 2026-10-09; checked by piping the hook (reading set, ledger, reminder); the live check in a fresh session and after compaction is the operator's |
| per-turn `## Now` digest (§8.3) | pending |
| staleness line (§8.4) | pending |
| install templates for hosts (§2) | pending; after the Nexus files prove the shape |
| amendment to the orchestration spec (§9) | with approval of this spec |

Hypotheses, by the charter's validation policy: every item above that is not marked done, and in particular that the full cycle holds direction in real work, that steering as behaviour keeps holding without a gate, that a net of this shape stays one screen and stays current, that the cycle applies to projects with a known path, and every format detail of §4–§6 and §10, none of which has been checked by a tool or used in a host.

Deliberately **not** in this version, and only added when this level shows the need: a fifth Closure Block field, a tool-gate denial for `owner: operator`, a `process/` index, relations blocks, per-track navigation files, any kind beyond the four. How the route is shown to people (a PERT-like map with substantive names, the level of detail chosen by the activity, language without internal Nexus labels) is the presumed next horizon after the cycle is checked; it is named here so that it is not forgotten, and not designed.
