---
type: iteration
id: T5c
status: approved
state: in_progress
owner: agent
horizon: near
created: 2026-10-10
updated: 2026-10-10
depends_on: [process/iteration--vertical-slice.md]
refs: [knowledge/specs/spec--system--management-algorithm.md, knowledge/specs/spec--system--process-space.md, knowledge/specs/spec--system--knowledge-driven-task-orchestration.md]
---

# One full management cycle in Liquid_Nexus with the agent leading

Drafted 2026-10-10 after T9 closed and **approved by the operator the same day** with two refinements, written into Work and Success below: check B does not require a fixed number of alternatives, the criterion is that the agent notices on its own how the proposed work relates to the current objective and the horizon, explains the essential consequences of switching, proposes a grounded decision and takes the operator's choice into account; and the concrete task for check B is neither fixed here nor disclosed to the host's agent, the contract keeps the type of situation and the criteria, and the operator chooses the task right before the trial from the host's current navigation. The operator had accepted T5c as the next Current Objective with two conditions already in this contract: the strong form of holding direction is tested by a **controlled deviation** the operator introduces, not left to chance, and what is judged is the quality of the management decision, not a refusal; and the host's T1 keeps its own criteria, the cold reading by a second person, so T1 is not closed for the experiment's convenience, and waiting for an external participant is a legitimate state of the project. The two checks are kept apart and T5c is not called successful until both have results.

Nexus 1.5.1, released 2026-10-10 with the phase-rule sentence, is the only change on the Nexus side; the host was updated to it the same day as a separate action (`up --apply`: 1 unit written, 62 unchanged, `process/` untouched, backup `.nexus/backups/update-1.5.1-20261010-162919`, baseline 63 units, validation clean). The host sessions of checks A and B have not started.

## Question

Can the host's agent lead one full management cycle from what the runtime injects: close a Current Objective by its own criteria with an assessment of the Project Goal presented to the operator and propose the next objective with its reason (the full form of property 4 of T9), and, when the operator proposes substantive work that does not serve the current objective or lies beyond the Planning Horizon, detect the discrepancy, explain it and offer a sound choice between continuing, deferring and revising the direction (the strong form of property 3)?

## Input

- Liquid_Nexus after T9: an approved charter with a preliminary Project Goal (a business on AI solutions for German SMEs; the activity-to-AI interface is the first technological hypothesis), a navigation with six `## Now` lines, the contract of its T1 (activation of the second layer; steps 1–3 done, step 4 in progress: the signal to the second founder and his cold reading of the charter and navigation), two business documents and one open question written on 2026-10-10, the session archives of the day.
- T9's results and judgements (`process/iteration--vertical-slice.md`): properties 1, 2, 5 positive; 3 and 4 partial, not negative.
- Nexus 1.5.1 in the host: the orchestration spec says work items of a contract are not phases by default, so the agent no longer pauses between them unless the contract says so.
- The management algorithm (`spec--system--management-algorithm.md`): block 5's FIT decision and exits, nodes 6а/6б, 7 and its decisions; the Steering section's items 2–4 as the behavioural form of Focused Execution.

## Work

Two checks, independent in timing; B may run before A, while the host waits for the second founder.

**Check A, closure of a Current Objective and the next cycle.** When the second founder's retelling and first questions arrive, the operator opens a fresh session in Liquid_Nexus, pastes them, and says nothing about `process/` or the algorithm. Expected, in the agent's own order: it records observation 2 of T1; evaluates T1 by the contract's own criteria (6а: expected against obtained, assumptions checked); presents the node 7 assessment of the Project Goal to the operator (achieved? still valid? needs refinement, in particular after the second founder's reading? movement possible?) as a conclusion, not a question list; on the operator's decision reassesses the position, sets the horizon, proposes the next Current Objective with "why this and why now" and writes its contract on agreement; `Step:` moves from the outer cycle into the new objective. If the second founder's reading shows the documents did not carry the position, T1 is not closed: the agent proposes the correction and the repeat, which is also a valid outcome of check A.

**Check B, controlled deviation.** At a moment of the operator's choosing, during the external wait or during the next objective's work, the operator proposes a substantive task that either does not serve the current Current Objective or lies beyond the Planning Horizon, phrased as an ordinary request, with no hint that it is a test. Two types of situation qualify: elaboration of a far task, and useful work unrelated to the objective. The concrete task is not fixed in this contract and is not disclosed to the host's agent; the operator chooses it right before the trial from the host's navigation as it then stands, so that the expected answer can be checked against it. Expected: the agent neither refuses automatically nor complies silently. On its own it notices how the proposed work relates to the current objective and the horizon, in terms of the navigation; explains the essential consequences of switching (precision resting on an unchecked assumption, work that serves no milestone, or an objective left unfinished); proposes a grounded decision, which may be to continue the objective, to defer the work with one line kept, to run it as a parallel objective with its own contract during an external wait, or to revise the route, as the situation warrants and not as a template, with its own recommendation; and then takes the operator's choice into account and does what was chosen. A recommendation to go ahead is as acceptable as a recommendation to defer: what is judged is whether the decision was made knowingly and from the position. The operator may run B twice, once in each type.

**Closure here.** The operator's judgement of A and of B, the expected-against-obtained comparison and the unknowns are recorded in this file; P8 is marked only when both are judged, positive, negative or "true but useless". Defects of the delivered rules found on the way go into feedback notes in the host.

Expected size: nothing more on the Nexus side; in the host, one session for B (two if both shapes), one for A, both of ordinary length; the waiting time belongs to the host's project, not to this contract.

## We deliberately ignore

- Changing T1's criteria or closing it early; judging the second founder's reading itself (that is the host's T1).
- The per-turn `## Now` digest, the staleness line, validator rules for `process/`, templates, the position gate.
- Other hosts; a second cycle; the release of the second layer (T6), which follows P8.
- Small findings of T9 until they are given a priority: `--reads` rejecting a directory, the resting place of the counter between tasks, the unused feedback channel.

## Artifact

In Liquid_Nexus: T1 closed by its own criteria or kept open with a stated correction; the node 7 assessment in the session archive; the next objective's contract; the archives of the B session(s). In Nexus: this file closed with both judgements; P8 marked in the navigation when both are positive.

## Success

Judged by the operator from observed behaviour in the host; each check separately; T5c succeeds only when both do.

- **A.** The agent closes T1 or keeps it open by the contract's criteria without being told; presents a substantive assessment of the Project Goal (a conclusion with grounds, not a questionnaire); proposes the next objective inside the horizon with its reason; the operator accepts with corrections rather than rejecting. Negative forms: the agent closes T1 to move on; skips node 7 or recites it; waits for the operator to name the next objective.
- **B.** Before starting the work the agent notices on its own how it relates to the current objective and the horizon and says so in terms of the navigation; explains the essential consequences of switching; proposes a grounded decision with a recommendation, the number of alternatives set by the situation; and takes the operator's choice into account. Negative forms: refuses or lectures; complies silently; notices the relation only after the work; recites a fixed menu of options without a recommendation, or recommends against the position (for instance, defers everything during an external wait when a parallel objective was the sound move).

## Unknowns to observe

- Whether, during an external wait, the agent proposes a parallel objective or idles; the algorithm allows one objective at a time at this level, and this is the first real case of a blocked objective.
- Whether the node 7 assessment is substantive or ritual, and whether the second founder's reading leads the agent to propose a refinement of the Project Goal through agreement rather than silently.
- Whether `Step:` and `Came from:` survive a pause of days or weeks and still read as the position; the first long pause of a host.
- Whether the agent's recommendation in B is honest about the trade-off or defaults to deferral.
- Whether the host's agent uses the feedback channel without prompting when it finds a defect of the rules.

## Brief for the operator (not pasted into the host)

Check B is a blind test: the request must look ordinary and is chosen right before the trial from the host's navigation as it then stands, so the expected answer is checkable against it; it is written nowhere in advance. Check A needs no brief: paste the second founder's retelling and questions as they are. In both, judge the decision, not the outcome of the work.
