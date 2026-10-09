---
type: decision
scope: system
status: approved
created: 2026-10-09
updated: 2026-10-09
source_of_truth: true
knowledge_visibility: binding
tags: [decision, governance, process-space, second-layer, steering, charter]
---

## Relations

- relates_to:
  - [Process Space Specification](../specs/spec--system--process-space.md) — the rules of the second layer (approved 2026-10-09); amended by this decision (management cycle, warning instead of refusal, gate deferred).
  - `open-questions/question--system--progressive-resolution.md` (development class, not delivered to hosts; cited by path, not linked) — the origin of the second layer.
  - [Knowledge-Driven Task Orchestration Specification](../specs/spec--system--knowledge-driven-task-orchestration.md) — the first layer's contract, which this decision leaves unchanged.

---

# Decision: What the second layer of Nexus is for

## Context

Nexus has two layers. The first, knowledge of the project, is shipped (1.3.0) and runs in several host projects. The second, management of the project, exists only in this repository: a draft specification (`spec--system--process-space.md`), a charter and a navigation under `process/`, and an experimental `## Steering` section in `CLAUDE.md`.

The charter's goal-change policy says that a change to the charter's *Goal* or *Nature* is recorded as a decision in the vault. This is that record: on 2026-10-09 the operator paused the second layer's development and restated its purpose; the charter was changed accordingly in the same session.

## Previous understanding

The second layer was conceived as a **carrier of position**. The vault answers *what is known*; `process/` was to answer *what the project is for* and *where it stands*, so that after bootstrap the agent knows the position and works within it. The charter (2026-10-06) stated the goal as: "Nexus ... guarantees the agent works, in every turn, with the project's current context", of which management of the project was one kind.

From that purpose followed the route in the navigation's net: write the net, make it mechanically checkable (P5), teach bootstrap to read `process/` (P6), then build a **position gate** that denies the first mutating call of a turn when the claimed step is not enabled in the net (P7), then install in a host and release. The specification's §8.6 and its "One gate, then" paragraph recorded the reasoning of 2026-10-06: every rule left to goodwill turns into a ritual, so the position decision must be gated like the gates of the first layer.

Along the way, two observations accumulated:

- the navigation written for Nexus itself failed its cold reading (2026-10-08): a position carrier that a fresh reader cannot read carries nothing;
- the experimental Steering instruction (2026-10-08), tested in two dry runs and one ordinary session, showed the agent naming unchecked assumptions, offering continue / defer / change route, and proposing a route revision instead of defending the net. The operator judged this useful as behaviour and unproven as a mechanism.

## New understanding

The second layer is a system of **joint management of the project by operator and agent**: continuous management activity in which both define and refine goals, assess the position, plan the next intermediate result, choose the work, hold the direction and revise the route when circumstances change. The agent carries a substantial share of the analytical, organizational and technical work of management: it surfaces significant uncertainties and proposes intermediate goals, milestones, dependencies and options. The operator stays an informed participant who understands the position, the grounds of proposals and their consequences, and makes the final choice. The final decision is the operator's; the responsibility for keeping the process purposeful is shared.

At every significant step both must be able to say: where the project is relative to its goals; where and why it is moving now; what concrete result the next work should produce; how that result will be used; and whether direction has been lost or detail has come too early.

The method is an **iterative management cycle with a bounded horizon of justified planning**: strategic goal; assessment of position; planning horizon; nearest intermediate goal and milestones; planning and execution of work; evaluation and route revision; repeat. It is written into `spec--system--process-space.md`. Two rules complete it: at closure the expected result is compared with the obtained one and the deviation feeds planning; a route revision is triggered by a milestone reached, a significant obstacle, new knowledge that changes assumptions, or the initiative of either side, with the agent free to propose and the operator deciding.

The Petri net stays as the internal representation of states, results, transitions and dependencies: an instrument of account and analysis, not a system of permissions. The position gate becomes a **deferred hypothesis**, kept in the specification as a design, built only if practice shows that the habit does not hold. The horizon rule changes from refusal to warning: the agent explains the risk of premature detail and proposes a fitting scale; the operator chooses, knowingly.

## Grounds for the revision

1. Carrying position is necessary but not the point. The failures the second layer exists for (modules designed before the core hypothesis was checked; a file rewritten on a word of agreement without asking whether that was the step) are failures of management, not of memory. A correct position in the agent's context does not by itself produce the question "is this the step?".
2. The gate-first route rested on an unchecked assumption, that goodwill rots into ritual, and the first evidence (the Steering runs) points the other way, at least at this scale. Building the gate first would have been work below an unverified assumption, which is exactly what the horizon rule forbids.
3. A gate that denies work is a poor fit for exploratory projects: research does not need a transition to begin, and a change of direction is a management decision, not a rule violation. The first layer is strict about integrity of knowledge; the second must be disciplined about purpose and flexible about path.
4. The cycle is the same for research projects with high uncertainty and for projects with a known way to the goal; only the horizon differs. That makes it a better foundation than a mechanism tuned to one case.

## Consequences

- `process/charter.md`: Goal and Nature restated; the planning horizon is reset at every revision point; a negative result counts under the validation policy.
- `spec--system--process-space.md`: gains the management cycle and the two completing rules; §6 says the net is an account, not a permit; §8.6 is reclassified as a deferred hypothesis; §9 replaces refusal by warning and the operator's choice; §11 reflects the pause and the revision.
- `process/navigation.md`: the route is redrawn from the new goal. The critical path runs through "foundations aligned" and "the full cycle checked in real work"; the gate branch (P5, T4, P7) is kept, deferred. The paper-test iteration is deferred with it.
- Nothing is built: no hook, no format, no new document kind. The first layer's contracts are untouched.

## What remains a hypothesis

- That the full cycle can be run in real work and holds direction; only fragments have been observed.
- That steering as agent behaviour keeps holding without a gate, in ordinary sessions and in hosts.
- That a net of this shape stays one screen and stays current.
- That the agent can surface significant uncertainties in a host project, not only in Nexus itself.
- That the cycle applies to projects with a known path; only the research case has been tried.
- Every format detail of the specification (fields, states, validator codes): none has been checked by a tool or used in a host.

## Status

Approved by the operator on 2026-10-09, in the session that made the change.
