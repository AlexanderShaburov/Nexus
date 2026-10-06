---
type: iteration
id: T2
status: approved
state: in_progress
owner: agent
horizon: near
created: 2026-10-06
updated: 2026-10-06
refs: [knowledge/specs/spec--system--process-space.md]
---

# Net paper test

## Question

Can a one-screen net of project states and transitions tell, mechanically, which work is permitted now and which is premature, while still reading cold? We start from the agreed charter and navigation and from the goal agreed on 2026-10-06: coordinated movement toward the goal without burrowing and without stalling.

## Input

- `process/navigation.md` with its first net, written for Nexus itself.
- Two known failures to test against. The arbitrage bot, where modules were designed before the core hypothesis, that safe arbitrage exists between the two venues, was checked. The Nexus session of 2026-10-06, where the agent rewrote the navigation file on a word of agreement without asking whether that was the step.

## Work

Run both cases through the net by hand, as the future tool gate would: name the transition the work corresponds to, check whether its inputs are marked, and record what the claim would have printed or denied. Then have the operator read the navigation file cold and say whether it is one screen and whether the position and the reason are clear from it.

## We deliberately ignore

- Any hook or tool code; the test is on paper.
- Computing criticality from the graph; `!` is placed by hand at this level.
- The exact wording of the claim's output and of the Closure Block; only whether a denial would have occurred.
- Machine validation of the net's grammar.

## Artifact

The result of the two runs, recorded as the `check:` of P5 in the net when positive, and this document closed.

## Success

The net denies the arbitrage case, because an input place is unmarked; it surfaces the Nexus case, because no transition matches the work; and the operator finds the navigation file one screen and readable cold. If the Nexus case is only surfaced and the operator finds that insufficient, the result is "P5 not yet": the escape hatch is strengthened before any hook is built.

## Unknowns to observe

- Whether `--step none` is a hole wide enough to let burrowing through.
- Whether the operator can keep a net of this shape current, or whether it rots like a plan.
- Whether nine places and six transitions is already too many for one screen when a second track appears.
