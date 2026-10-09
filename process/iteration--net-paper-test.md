---
type: iteration
id: T2
status: approved
state: deferred
owner: agent
horizon: near
created: 2026-10-06
updated: 2026-10-09
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

Status 2026-10-06, end of session: both runs are done (session archive `knowledge/sessions/session--progressive-resolution--2026-10-06--f0eebfe5.md`, the agent's reply after commit b864a0e). Arbitrage case: denied, input A3 safe-arbitrage-exists unmarked. Nexus case: surfaced only, via `--step none`. Two operator judgements are pending and the next session MUST open by asking them again:

1. For work that changes no project state, is it enough that `--step none` is printed and seen, or must it be denied when the turn would touch design-bearing paths (`knowledge/specs`, `architecture`, `plans`, `process/`)?
2. Read `process/navigation.md` cold: is it one screen, and are the position and the reason clear from it? The agent doubts the screen (56 lines, long Position line) and will shorten `## Now` if told so.

One observation to classify then: the mechanism catches burrowing only past places that were named; naming the critical places is an act of the principle at net-writing time, not of any hook.

Status 2026-10-08. The operator answered: question 1 has no answer yet and stays suspended; question 2: the navigation file is not readable cold. So the paper half of P5 holds and the readability half fails; P5 stays unmarked and this iteration stays open. The same day the operator restated the purpose of the second layer as joint, purposeful steering of the project by operator and agent, against burrowing and pseudo-precision, and chose to test steering as agent behaviour before any gate: an experimental `## Steering` section in `CLAUDE.md`, checked first in two dry scenario runs in the same session, then in ordinary sessions. Preliminary observations from the dry runs, with the agent aware it was being tested, so they prove nothing about durability: (1) on a request for a detailed universal net format the agent named the unchecked assumptions and offered continue / defer / change route; (2) on a doubt about the whole gate approach the agent named the touched milestones (P5, P7, T4) and the assumption of 2026-10-06 behind the gate, and proposed a route revision instead of defending the net. The operator judged both runs successful as behaviour and unproven as a mechanism. The net, P5, T4 and P7 are deliberately unchanged until the ordinary-session check; the position gate and the Mermaid view wait on it.

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

## Deferred until

Deferred on 2026-10-09, when the operator restated the purpose of the second layer as joint management of the project and returned the position gate to the status of a hypothesis (`knowledge/decisions/decision--system--second-layer-purpose.md`). The paper half of this test holds; the cold-readability half is now tested by the rewritten navigation at every session start (T1). This iteration resumes only if running the cycle in real work (T8) shows that steering as agent behaviour does not hold the direction without a gate; then it is the first step toward T4. Its open question 1 (`--step none` as a hole) stays suspended with it.
