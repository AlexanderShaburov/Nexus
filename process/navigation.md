---
type: navigation
status: approved
state: active
owner: agent
created: 2026-10-06
updated: 2026-10-10
---

# Nexus navigation

## Now

Position: Nexus has two layers. Layer one, knowledge of the project, is released and runs in several host projects. Layer two, joint management of the project by operator and agent: its purpose is recorded (`knowledge/decisions/decision--system--second-layer-purpose.md`), its rules are binding (`spec--system--process-space.md`), its algorithm is one approved artifact (`spec--system--management-algorithm.md`, v4, P14), and on 2026-10-10 its first vertical slice ran in Liquid_Nexus under Nexus 1.5.0 (T9, closed): the Project Goal of the host was formed with the operator in block 1 and recorded in an approved charter; the host's agent chose its Current Objective inside a one-iteration horizon with its reason; two fresh sessions restored `Step:` and continued the operation. The operator judged properties 1 (goal held without substitution), 2 (objective chosen unprompted) and 5 (position carried between sessions) positive, and 3 (work held in the direction of the goal) and 4 (evaluation and proposal) partial. P13 and P15 are marked, P15 within the tested scenario. **Not confirmed:** the strong form of 3 (the agent preventing a departure from the goal on its own) and the closure of a Current Objective with an assessment against the Project Goal and the choice of the next cycle. One rule defect found by the host (the phase rule applied to work items of a contract) is fixed in the orchestration spec here and not yet released.

Heading: T5c, one full management cycle in Liquid_Nexus with the agent leading, accepted by the operator on 2026-10-10 as the next Current Objective; its contract (`process/iteration--host-cycle.md`) is drafted and awaits approval, with two conditions already in it: the strong form of holding direction is tested by a controlled deviation the operator introduces, and the host's T1 keeps its own criteria. Release 1.5.1 with the phase-rule sentence is out; the host's update to it is the next separate action. No transition is current until the contract is approved.

Why here: every path to the goal (P9) passes through P8, one host running the layer. P8 now rests only on T5c, and T5c is exactly the test of what T9 could not show: whether the agent closes an objective against the Project Goal, chooses the next cycle and holds the direction without the operator's prompt. The host's T1 closes on a cold reading by a second person, which sets the timing; the Nexus side has nothing larger to do than deliver the one-sentence fix.

Ignoring: the position gate; validator rules for process documents; the per-turn `## Now` digest and the staleness line; a separate Execution State file; an interpreter of the algorithm, recovery after an abnormal end, parallel sessions, a task system; templates for charter and navigation; any picture of the net; other hosts; the small findings of T9 (`--reads` rejecting a directory, the resting place of the counter between tasks, the unused feedback channel) until they are given a priority.

Step: 4 of the outer cycle, for T5c — the objective is accepted and its criteria are being agreed (the contract is drafted); next: 5.1 of T5c once the contract is approved, beginning with the host's update to 1.5.1. No transition is current until then.

Came from: node 7 on 2026-10-10 — after ВЫХОД А of T9 the Project Goal of Nexus was assessed and confirmed unchanged, and T5c was accepted by the operator as the next objective with two conditions.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [x] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone. check: 2026-10-09, session start, confirmed by the operator the same day.
- [x] P10 foundations-aligned — charter, rules and navigation agree with the management goal and cycle. check: operator's confirmation on 2026-10-09; commits 650abc5, 7ae79a9, e7aa68c.
- [x] P11 cycle-checked — one real piece of Nexus work has gone through all six steps of the cycle. check: operator's judgement 2026-10-09: technical result positive, managerial positive but limited; contract process/iteration--run-cycle.md, closed.
- [x] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both. check: live 2026-10-09; commits fa16c69, b041b48, fc48009.
- [x] P12 host-updated — Liquid_Nexus carries Nexus 1.4.0 with every system component the second layer needs. check: operator's report 2026-10-09; tag v1.4.0 on 413b96f; contract process/iteration--deliver-second-layer.md, closed.
- [x] P14 algorithm-recorded — the management algorithm exists as one approved artifact with a single entry, goal formation with the operator, the work block with two exits, review of the goal, the end of the project, and the definitions of Program Counter and Execution Context. check: operator approved v4 on 2026-10-10 after the diagram rendered from the file; knowledge/specs/spec--system--management-algorithm.md, commit f079bcf.
- [x] P13 host-position-carried — Liquid_Nexus has its own charter with an agreed Project Goal and a navigation with `Step:`, and a fresh session there states the host's position and step from what the runtime injected. check: 2026-10-10, host session 6700c04a opened with "let us continue": position, `Step: 5.4 of T1` and the next operation stated from the injected documents and matching the navigation; the operator accepted it in the host and judged property 1 positive here; contract process/iteration--vertical-slice.md.
- [x] P15 host-continues — in Liquid_Nexus a fresh session continues an unfinished Current Objective from the saved `Step:` without redefining the goal or rebuilding the route. check: 2026-10-10, host sessions 6700c04a and d7a45bcc both restored the counter and performed the operation named; the operator's judgement of property 5 positive. **Marked within the tested scenario only:** the closure of the objective with an assessment against the Project Goal and the choice of the next cycle were not observed and belong to T5c.
- [ ] P8 host-runs — one host project runs the second layer: one full cycle there with the agent leading, including the closure of a Current Objective against the Project Goal and the choice of the next cycle, and the agent holding the direction without the operator's prompt.
- [ ] P9 released — the second layer is shipped as the next Nexus version.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold. Deferred branch.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn. Deferred branch.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T7 align-foundations: P3 → P10  ! — done 2026-10-09; contract process/iteration--foundations-alignment.md
- T1 cold-read-check: P3 → P4  ! — done 2026-10-09
- T8 run-cycle: P10 P4 → P11 P6  ! — done 2026-10-09; contract process/iteration--run-cycle.md
- T5a deliver-second-layer: P6 → P12  ! — done 2026-10-09; contract process/iteration--deliver-second-layer.md
- T5b activate-in-host: P12 → P13  !? — superseded 2026-10-10 by T9 after a partial result; contract process/iteration--activate-in-host.md
- T9 vertical-slice: P12 P14 → P13 P15  !? — done 2026-10-10; contract process/iteration--vertical-slice.md. The recorded `Step:` changed the agent's behaviour; properties 1, 2, 5 positive, 3 and 4 partial
- T5c host-cycle: P13 P15 → P8  !? — accepted as the next objective 2026-10-10, contract drafted the same day and awaiting the operator's approval: two checks kept apart, the closure of the host's T1 by its own criteria with the node 7 assessment and the next objective (A), and a controlled deviation introduced by the operator, judged by the quality of the management decision (B); T5c succeeds only when both do. Nexus 1.5.1 with the phase-rule sentence released 2026-10-10 as its first step
  task: process/iteration--host-cycle.md
- T6 release: P8 → P9 — tag and ship
- T2 write-net-paper-test: P3 → P5  ? — deferred 2026-10-09 with the gate; contract kept in process/iteration--net-paper-test.md
- T4 build-position-gate: P5 P6 → P7 — deferred hypothesis: built only if real work shows that steering as agent behaviour does not hold the direction

## Uncertainty points

- Whether the agent closes a Current Objective against the Project Goal and chooses the next cycle on its own, and whether it prevents a departure from the goal without the operator's prompt. The two properties T9 left unconfirmed; T5c tests them.
- Whether the "charter not approved" line of bootstrap keeps the agent from planning work; the path was never seen live (the host's charter stayed in `review` for one turn).
- Where the counter rests between tasks (5.2 after each 5.4, as the host's agent chose, or a direct continuation of the approved plan); observation only, the algorithm is not changed on one case.
- Whether the host's T1 closes on the cold reading of a second person within a useful time; T5c's timing depends on it.
- Whether a hook change in Nexus needs one live-check round per lifecycle event it touches (T8 needed three where one was planned).
- Whether steering as agent behaviour keeps holding without a gate, or rots into ritual.
- Whether a net of this shape stays one screen and stays current once the project has more than one line of work.
- Whether the cycle applies to projects with a known path; only the research case has been tried.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions (T1): done 2026-10-09; P4 marked.
- Alignment (T7): done 2026-10-09; P10 marked.
- Cycle in practice (T8): done 2026-10-09; P11 and P6 marked.
- Delivery to the first host (T5a): done 2026-10-09; P12 marked.
- Activation in the first host (T5b): partial, 2026-10-10; superseded by T9.
- Vertical slice (T9): done 2026-10-10. Expected: five properties observed in three host sessions. Obtained: 1, 2, 5 positive, 3 and 4 partial, by the operator's judgement; the recorded `Step:` changed behaviour; restoration cost fell from a session to one turn. Deviation: the closure of the objective could not be observed because the host's T1 closes on a second person; moved to T5c. P13 and P15 marked.
- Host cycle (T5c): in Liquid_Nexus, with no instruction about `process/`, the agent closes T1 when its criterion is met (6а, node 7 with an assessment of the Project Goal presented to the operator), proposes the next objective with its reason, runs it, and at least once names on its own a piece of work that does not serve the objective and offers the choice. The operator judges properties 3 (strong form) and 4 (full form) by behaviour. Then P8 is marked.
