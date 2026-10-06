---
type: charter
status: approved
state: active
owner: operator
created: 2026-10-06
updated: 2026-10-06
review_by: 2027-01-06
---

# Nexus charter

## Nature

Exploratory. One level is proven: project context now reaches every working step, through the vault and the three gates. The next level, a Nexus that also knows what the project is for and where it stands, has never been built by us; there is confidence and no proof yet.

## Goal

Nexus is a layer over Claude Code that guarantees the agent works, in every turn, with the project's current context. That context is of two kinds: **knowledge of the project** (decisions taken, constraints, relations, what is deprecated) and **management of the project** (goals, current position, horizon, the dynamics of its movement). Nexus does not do the operator's work: it keeps the account of the project and steers it, so that the operator is occupied with the questions that matter, where to go, by which methods, with which resources, rather than with restoring context.

A good outcome: in any host project the agent, after bootstrap, knows what has been decided and what is deprecated, where the project is now and which single question is being tested, and acts within those bounds without being reminded.

## Validation policy

A change counts as confirmed only after it has been checked in real work, never on the strength of a specification or a selftest alone. The concrete check for the current hypothesis is defined in `navigation.md` or in the current iteration.

## Planning horizon

Only the nearest confirmable iteration is planned in detail. The steps after it may be marked in the roadmap at low resolution. Far tasks are not elaborated until their real conditions become visible.

## Definition of done

The iteration's question has an answer, the answer is written where it belongs (vault for facts, `process/` for position), the vault validates clean, and the work is committed.

## Goal-change policy

Only the operator changes this charter. The agent proposes in text. A change to Goal or Nature is recorded as a `decision` in the vault; a change to the policies below it needs only a bump of `updated`.
