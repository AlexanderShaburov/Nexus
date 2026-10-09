---
type: iteration
id: T7
status: approved
state: done
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
refs: [knowledge/decisions/decision--system--second-layer-purpose.md, knowledge/specs/spec--system--process-space.md]
---

# Foundations alignment

## Question

Do the strategic goal of the second layer, the management cycle, the division of responsibility between operator and agent, the planning rules and the three existing documents (charter, process-space rules, navigation) form one consistent system, with no substantive conceptual contradiction?

## Input

- The operator's restatement of 2026-10-09: the second layer is joint management of the project by operator and agent, organized as an iterative cycle with a bounded horizon of justified planning (recorded in `knowledge/decisions/decision--system--second-layer-purpose.md`).
- The three documents as they stood on 2026-10-08, written under the previous understanding: a carrier of position with a position gate on the route.
- The agent's comparison of the two (session of 2026-10-09): most of the charter and the horizon rule already fit; the real contradictions were the mandatory gate, the route of the net that ran through it, the mandatory refusal beyond the horizon, and the realization table that presented the gate as the next step.

## Work

Rewrite, in this order and only as far as needed: the charter (Goal, Nature, two policy lines) with the decision record the charter's own policy requires; the rules (the cycle as §0, the net as an account not a permit, the gate deferred, warning instead of refusal, the realization table); the navigation (position, heading, the route redrawn from the new goal, the gate branch kept and deferred). The operator reads the result and confirms or names what still contradicts.

## We deliberately ignore

- Any new mechanism, hook, format, validator rule or document kind.
- The design of the position gate: kept as written, status changed only.
- How the route is shown to people (a map with plain names, levels of detail): the presumed next horizon, named and not designed.
- The format details of the rules (fields, states, codes): unverified, untouched.

## Artifact

The three documents and the decision record, committed; P10 marked in the net with the operator's confirmation as its check.

## Success

Operator and agent can both say that the five elements (goal, cycle, division of responsibility, planning rules, documents) are consistent and that no substantive contradiction remains. This does not show that the system of management works; running the cycle once in real work is the next transition (T8).

Closed 2026-10-09. Expected: three documents rewritten and a decision record, one session, no code. Obtained: the same, plus one iteration contract (this file), the paper-test iteration deferred, and the stale Mermaid view deleted; three commits; the operator confirmed consistency in the same session. Deviation: none of substance. One thing the plan did not foresee: the net's grammar requires a contract on the current transition, so closing one step forces the next step's contract to exist at least as a draft; the cycle's step 4 therefore happens inside the closure of step 6, not after it.

## Unknowns to observe

- Whether the rewritten navigation reads cold at the next session start (T1).
- Whether the operator finds the cycle in the rules complete enough to run a real piece of work through it, or whether a step is missing.
- Which trigger for a route revision turns out to fire first in practice: a milestone, an obstacle, new knowledge, or someone's initiative.
