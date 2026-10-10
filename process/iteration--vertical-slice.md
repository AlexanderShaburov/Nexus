---
type: iteration
id: T9
status: approved
state: done
owner: agent
horizon: near
created: 2026-10-10
updated: 2026-10-10
closed: 2026-10-10
depends_on: [process/iteration--deliver-second-layer.md, process/iteration--activate-in-host.md]
refs: [knowledge/specs/spec--system--management-algorithm.md, knowledge/specs/spec--system--process-space.md, knowledge/specs/spec--system--session-bootstrap.md]
---

# First vertical slice of the management algorithm

**Closed 2026-10-10, the same day, with the question answered.** Three sessions in Liquid_Nexus (archives `session--framing-reset--2026-10-10--0c13976f.md`, `--6700c04a.md`, `--d7a45bcc.md` there, copied to `experiment_2_results/` here, with the host's summary of the day). Expected: goal agreed before the charter; an objective proposed unprompted; bounded work; a session ended mid-objective; a fresh session continuing from `Step:`; the objective closed with an assessment against the Project Goal. Obtained, by the operator's judgement of observed behaviour: (1) Project Goal held without substitution, positive: with no charter the host's agent named node 0 → block 1 itself, wrote no file, separated the project's goal from the product's and named the choice "verified tool or a company" before the operator widened the goal to a business; the charter was written from the agreed text, `status: review` first, `approved` on the operator's word. (2) Current Objective chosen inside the horizon with its reason, positive: horizon one iteration, four candidates, T1 chosen as the only transition resting on none of the four named uncertainties. (3) Work held in the direction of the goal, partial: no deviation occurred, so the strong form, preventing a departure on its own, was not exercised. (4) Evaluation and proposal, partial: expected-vs-obtained and the OBJ/FIT reasoning were observed for a task; the closure of the Current Objective with an assessment against the Project Goal was not, because the host's T1 closes on a cold reading by a person outside the project. (5) Position carried between sessions, positive twice: sessions opened with "let us continue" restored `Step: 5.4 of T1`, named the next operation and performed it; eight reads in one turn instead of a session of reconstruction. The main engineering unknown is answered at this scale: a recorded `Step:` changes the agent's behaviour. P13 marked; P15 marked within the tested scenario (restoration of the Program Counter and continuation of an unfinished objective); the closure of an objective with node 7 and the choice of the next cycle, and the strong form of (3), are **not confirmed** and move to T5c.

Found on the way: the host's agent treated the `## Work` items of its contract as phases under the Phase progression rule and paused between them, on its own admission an interpretation; fixed 2026-10-10 by one sentence in `spec--system--knowledge-driven-task-orchestration.md`, delivered with the next release. The `Step:` semantics needed one correction by the operator (5.3 written where 5.4 was meant), after which the host's agent rested the counter at 5.2 between tasks; recorded as an observation, the algorithm is not changed on one case. The Context Decision claim rejects a directory in `--reads`, which cost the host's agent one call. The session-writer fixes held in the host: every archive carries its last answer. The feedback channel was offered by the host's agent and not used without the operator's word. None of these is work now; they are recorded for priority later.

Proposed 2026-10-10 after the management algorithm was recorded (P14) and the host experiment T5b stalled on an unagreed goal. The operator approved the plan the same day with three refinements, written into the Work and Success sections below: the charter's `status: approved` is read as the record of an agreement that took place, not as proof that the goal is still current, and re-agreement is not asked for without grounds while a significant contradiction found is presented to the operator; `Step:` names a concrete current or next operation of the algorithm for the current objective, and on resumption the agent continues that operation, not only states it; the continuity check (a session ended mid-objective, a fresh session continuing it) is mandatory, followed by a normal closure of the objective.

The aim is one working end-to-end management cycle in a real host, not a full realization of the algorithm. Everything realized here uses existing documents and mechanisms; the only code change is the bootstrap line about the charter's status and the step.

## Question

Does the smallest realization of the algorithm give one working management cycle in a real host: can the agent, from what the runtime injects, restore the position and the agreed Project Goal without substituting it, propose a justified Current Objective unprompted, do bounded work holding the link to the goal, continue an unfinished objective in a fresh session from the saved `Step:`, and close it with an evaluation against the goal and a proposal for what comes next?

## Input

- The approved algorithm, `spec--system--management-algorithm.md` v4, and its realization table (§5): the Program Counter and Execution Context were the missing elements on the critical path; everything else of the slice exists as mechanism, rule or habit.
- Liquid_Nexus at Nexus 1.4.0 (P12), with the reconstruction of its position made on 2026-10-09 (the host's session e5f044cf and its summary), the operator's five corrections, and no `process/` directory.
- The three refinements of 2026-10-10 above.

## Work

In Nexus, done in this iteration's first step (2026-10-10):

1. `spec--system--process-space.md`: §0 replaced by a pointer to the algorithm spec; `## Now` gains `Step:` and `Came from:` (§6); the charter row of §7 says the goal is agreed first, then the file; §8.1 names the status line; §11 updated.
2. `CLAUDE.md` `## Steering`: item 1 gains the entry behaviour of node 0 (name and continue the step; without an agreed goal propose goal formation, not objectives); item 6 writes `Step:` and `Came from:` at closure.
3. `nexus-bootstrap.py` / `_nexus_common.py`: with a charter whose `status` is not `approved`, one line says no agreed Project Goal is recorded; with an approved charter, the instruction to name and continue the step. Mirrored in `spec--system--session-bootstrap.md` and the architecture; check B23 in the validation plan.
4. Nexus's own navigation carries `Step:` and `Came from:` first.
5. Release 1.5.0; the operator runs `up` in Liquid_Nexus.

In Liquid_Nexus, three sessions, the operator judging at each:

6. **Session 1, entry with history and no state.** The agent does not repeat the reconstruction of 2026-10-09; it runs block 1 with the operator: needs, desired result, essential characteristics and criteria, divergences of interest named. The operator agrees a Project Goal, at least preliminary. From the agreed text the agent writes `process/charter.md` (`status: approved` once the operator confirms every section) and `process/navigation.md` with the six lines of `## Now`, `Step:` pointing at node 2 or 3 of the algorithm.
7. **Session 2, fresh, ordinary task.** Expected: the first message states position and step; the agent proposes a Current Objective inside the horizon with its reason, without being asked; the operator agrees; an iteration file is written; one or two units of work are done with a steering line each (a candidate the host already named: recording the result of the 2026-09-23 conversation in the vault); the operator ends the session mid-objective; `Step:` names the next operation, `Came from:` the last transition.
8. **Session 3, fresh, no instruction about `process/`.** Expected: the first message names the saved step and continues it; no new goal formation, no new route; the objective is closed with expected-vs-obtained, an assessment of the Project Goal presented to the operator, and a proposal to continue or revise; `Step:` moves to the outer cycle.
9. **Closure here.** The operator's judgement of the five properties, the expected-vs-obtained comparison and the unknowns are recorded in this file; P13 and P15 are marked or the negative result goes under Unknowns with a proposed correction. Defects of the delivered rules found in the host go into feedback notes there.

Expected size: one step here (done), one release, three sessions in the host. Budget by the charter's horizon: the slice is not extended with mechanisms the three sessions do not need.

## We deliberately ignore

- A separate Execution State file or a fifth document kind; validator rules for `process/`; the per-turn digest; the staleness line.
- An interpreter of the algorithm, recovery after an abnormal end, parallel sessions, a task system, a state machine, KPIs.
- The full cycle with the agent leading (T5c): the slice ends with one objective closed and the next direction proposed, not chosen.
- Block 5's inner loop beyond what one or two units of work exercise.
- Other hosts.

## Artifact

In Nexus: the amended specs, the Steering entry behaviour, the bootstrap status line, this contract, Nexus's navigation with `Step:` and `Came from:`, release 1.5.0. In Liquid_Nexus: an agreed Project Goal in `process/charter.md`, a navigation with six `## Now` lines, one iteration file, one closed Current Objective, the session archives of the three sessions. In this file: the operator's judgement and the closure.

## Success

Judged by the operator from observed behaviour in the host, never from the technical checks:

1. The agent restores the Project Goal and the position without substituting the goal (sessions 2 and 3 state the agreed goal, not the product's).
2. It proposes a justified Current Objective inside the Planning Horizon on its own, with "why this and why now", and the operator accepts it with corrections rather than rejecting it.
3. It does the work holding the link to the agreed goal (the steering line names the goal and the objective before work).
4. It evaluates the result and proposes continuation or revision on its own at closure (expected vs obtained, assessment of the Project Goal).
5. It saves and restores the position of execution between sessions: session 3 continues the operation named in `Step:` without redefining the goal or the route.

Negative outcomes are results: "stated the step and re-planned anyway", "wrote `Step:` and did not read it as a position", "held the goal only after the operator's reminder".

## Unknowns to observe

- Whether a recorded `Step:` changes the agent's behaviour at all. **Answered 2026-10-10: yes, twice.**
- Whether the bootstrap line keeps the agent from substituting a goal. **Answered for the "no charter" path: the agent proposed goal formation, not files.** The "charter not approved" path was not seen live: the charter stayed in `review` for one turn without a fresh session.
- Whether six lines of `## Now` stay cold-readable in a host. One phrase failed ("`process/` created in this session") and was replaced by a date by the host's agent itself; otherwise held.
- Whether the Execution Context in the iteration file is enough to continue mid-objective. Held for two resumptions; no step delta was missed.
- Which defects the host finds first and whether the feedback channel is used unprompted. **Found: the phase rule against block 5; the channel was offered, not used.**
- Where the counter rests between tasks: the host's agent used 5.2 ("pick the next task") after 5.4; whether that or a direct continuation of the approved plan is the better convention is left to further trials.
