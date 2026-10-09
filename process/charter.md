---
type: charter
status: approved
state: active
owner: operator
created: 2026-10-06
updated: 2026-10-09
review_by: 2027-01-09
---

# Nexus charter

## Nature

Exploratory. One level is proven: project context now reaches every working step, through the vault and the three gates. The next level, a Nexus in which operator and agent manage the project together, has never been built by us; fragments of the behaviour have been seen, the full cycle has not. Confidence, no proof yet.

## Goal

Nexus is a layer over Claude Code with two parts. The first keeps **knowledge of the project** (decisions taken, constraints, relations, what is deprecated) in front of the agent at every working step; it is shipped. The second is **joint management of the project** by operator and agent: together they define and refine goals, assess the position, plan the next intermediate result, choose the work, hold the direction and revise the route when circumstances change. The agent carries a substantial share of the analytical, organizational and technical work of management: it surfaces significant uncertainties and proposes intermediate goals, milestones, dependencies and options. The operator stays an informed participant, understands the position and the grounds of each proposal, and makes the final choice. The decision is the operator's; the responsibility for keeping the work purposeful is shared.

A good outcome: in any host project, at every significant step, both operator and agent can say where the project is relative to its goals, where and why it is moving now, what concrete result the next work should produce, how that result will be used, and whether direction has been lost or detail has come too early. The agent raises these questions itself, without being reminded; the method is the management cycle in `knowledge/specs/spec--system--process-space.md`.

## Validation policy

A change counts as confirmed only after it has been checked in real work, never on the strength of a specification or a selftest alone. A negative result counts when it removes an uncertainty and lets a decision be taken. The concrete check for the current hypothesis is defined in `navigation.md` or in the current iteration.

## Planning horizon

Only the nearest confirmable iteration is planned in detail. The steps after it may be marked in the roadmap at low resolution. Far tasks are not elaborated until their real conditions become visible. The horizon is set by what is known and is set anew at every revision point; when the agent sees work going beyond it, it says so and proposes a fitting scale, and the operator chooses.

## Definition of done

The iteration's question has an answer, the answer is written where it belongs (vault for facts, `process/` for position), the expected result has been compared with the obtained one, the vault validates clean, and the work is committed.

## Goal-change policy

Only the operator changes this charter. The agent proposes in text. A change to Goal or Nature is recorded as a `decision` in the vault; a change to the policies below it needs only a bump of `updated`. Changes so far: 2026-10-09, `knowledge/decisions/decision--system--second-layer-purpose.md`.
