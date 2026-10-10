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

Position: Nexus has two layers. Layer one, knowledge of the project, is released and runs in several host projects. Layer two, joint management of the project by operator and agent: its purpose is recorded (decision `knowledge/decisions/decision--system--second-layer-purpose.md`), its rules are approved and binding since 2026-10-09 (`spec--system--process-space.md`), the cycle ran once end to end on real work here (T8; technical result positive, managerial positive but limited), and Nexus 1.4.0 runs in Liquid_Nexus with the layer inactive there (P12). The first attempt to activate it in that host (T5b, 2026-10-09/10) gave a partial result: the host's agent reconstructed the project's position from the host's own knowledge and found that no project goal was recorded, but did not hold that finding as a precondition and proposed writing the charter with the product's goal in it; the operator stopped the experiment. The cause was in the delivered rules, which made the charter file the proof of a goal. On 2026-10-10 the operator's original flowchart of the management algorithm was recovered, revised in four rounds and approved as v4; it is recorded as `knowledge/specs/spec--system--management-algorithm.md` (P14). The same day two defects of the session archive were fixed (archive renamed past midnight; last answer of a session lost).

Heading: does the first vertical slice of the algorithm give one working management cycle in a real host? In Liquid_Nexus: the Project Goal is formed with the operator and recorded; the agent proposes a Current Objective inside the horizon unprompted; bounded work is done with its link to the goal held; a session ends mid-objective and a fresh session continues from the saved `Step:` without redefining the goal or the route; the objective is then closed with an evaluation against the Project Goal and a proposal for what comes next. Contract: `process/iteration--vertical-slice.md` (T9), approved 2026-10-10 with three refinements (the charter's `approved` status records an agreement, it is not re-asked without grounds; `Step:` names a concrete operation for the current objective and is continued, not only stated; the continuity check is mandatory).

Why here: every path to the goal (P9) passes through P8, one host running the layer, and P8 rests on P13, the host carrying its own position. T5b showed that P13 rests on something earlier: a Project Goal agreed before any document is written, and a position of execution that survives sessions. The algorithm now has that entry and that counter on paper (P14); whether they change the agent's behaviour in a host is the next unknown on the critical path, and it is cheaper to test than the full cycle (T5c), which rests on it.

Ignoring: the position gate; validator rules for process documents; the per-turn `## Now` digest and the staleness line; a separate Execution State file or document kind; an interpreter of the algorithm, recovery after an abnormal end, parallel sessions, a task system; templates for charter and navigation; any picture of the net; other hosts. Anything concerning the hosts' own projects beyond carrying `process/`.

Step: 5.4 of T9 — the slice is implemented in Nexus (the algorithm spec, the process-space and bootstrap amendments, the Steering entry behaviour, this navigation) and statically checked; release 1.5.0 is prepared. Next: 5.3 of T9 in the host — the operator runs `up` in Liquid_Nexus and opens session 1 (goal formation), by the instruction in the iteration contract.

Came from: 6б of T5b on 2026-10-10 — the host experiment stalled on an unagreed goal; the delivered rules were the cause; the algorithm was recovered and recorded, T5b was superseded by T9, and the route was redrawn through P14.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [x] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone. check: 2026-10-09, session start, position and heading stated from the two files and confirmed by the operator the same day.
- [x] P10 foundations-aligned — charter, rules and navigation agree with the management goal and cycle, and operator and agent confirm there is no substantive contradiction. check: operator's confirmation on 2026-10-09, session archive session--progressive-resolution--2026-10-09--537ddd7b.md; commits 650abc5, 7ae79a9, e7aa68c.
- [x] P11 cycle-checked — one real piece of Nexus work has gone through all six steps of the cycle, and the operator judges that the direction held. check: operator's judgement 2026-10-09: technical result positive, managerial positive but limited; contract process/iteration--run-cycle.md, closed; session archives 537ddd7b, 2ab1e556, fd9a877a, ab71248a of 2026-10-09.
- [x] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both. check: live 2026-10-09, fresh session twice and compaction once after the fixes; commits fa16c69, b041b48, fc48009.
- [x] P12 host-updated — Liquid_Nexus carries Nexus 1.4.0 with every system component the second layer needs, its own data and settings untouched; the layer is not active there yet. check: operator's report 2026-10-09: `up` 1.3.0 → 1.4.0 without errors, `status` 61 unchanged / 0 customized / 0 refused; tag v1.4.0 on 413b96f; contract process/iteration--deliver-second-layer.md, closed.
- [x] P14 algorithm-recorded — the management algorithm exists as one approved artifact with a single entry, goal formation with the operator, the work block with two exits, review of the goal, the end of the project, and the definitions of Program Counter and Execution Context; it says what is realized and what is not. check: operator approved v4 on 2026-10-10 after the diagram rendered from the file; knowledge/specs/spec--system--management-algorithm.md, commit f079bcf.
- [ ] P13 host-position-carried — Liquid_Nexus has its own charter with an agreed Project Goal and a navigation with `Step:`, and a fresh session there states the host's position and step from what the runtime injected; the operator judges it true.
- [ ] P15 host-continues — in Liquid_Nexus a session ends with a Current Objective unfinished, and a fresh session continues it from the saved `Step:` without redefining the goal or rebuilding the route; the objective is then closed with an evaluation against the Project Goal and a proposal for what comes next; the operator judges all five properties of the slice by observed behaviour.
- [ ] P8 host-runs — one host project runs the second layer.
- [ ] P9 released — the second layer is shipped as the next Nexus version.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold. Deferred branch.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn. Deferred branch.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T7 align-foundations: P3 → P10  ! — done 2026-10-09; contract process/iteration--foundations-alignment.md
- T1 cold-read-check: P3 → P4  ! — at session start a fresh agent states position and reason from the two files; the operator judges
- T8 run-cycle: P10 P4 → P11 P6  ! — done 2026-10-09; contract process/iteration--run-cycle.md
- T5a deliver-second-layer: P6 → P12  ! — done 2026-10-09; contract process/iteration--deliver-second-layer.md
- T5b activate-in-host: P12 → P13  !? — superseded 2026-10-10 by T9 after a partial result: reconstruction of the host's position worked; activation stalled on an unagreed goal, and the delivered rules were the cause; contract process/iteration--activate-in-host.md
- T9 vertical-slice: P12 P14 → P13 P15  !?  ← now — the first realization slice of the algorithm: `Step:` and `Came from:` in the navigation, the bootstrap status line and step, the Steering entry behaviour, release 1.5.0; then three sessions in Liquid_Nexus (goal formation; objective, bounded work, session ended mid-objective; continuation and closure). The operator judges the five properties by behaviour
  task: process/iteration--vertical-slice.md
- T5c host-cycle: P15 → P8  !? — one full cycle of real work in the host with the agent leading, from the position the slice leaves. Not elaborated until T9 is done
- T6 release: P8 → P9 — tag and ship
- T2 write-net-paper-test: P3 → P5  ? — deferred 2026-10-09 with the gate; contract kept in process/iteration--net-paper-test.md
- T4 build-position-gate: P5 P6 → P7 — deferred hypothesis: built only if real work shows that steering as agent behaviour does not hold the direction

## Uncertainty points

- Whether a recorded `Step:` changes the agent's behaviour at all: whether a fresh session continues the operation named there and holds the agreed goal without the operator's prompt, or reads it and re-plans from scratch anyway. This is the engineering unknown T9 tests; if negative, the next candidate is the per-turn digest (§8.3), not a gate.
- Whether the agent holds "no agreed goal" as a precondition when the bootstrap line says so, instead of substituting the nearest available goal (observed in T5b before the rule existed).
- Whether `## Now` with six lines still reads cold and stays one screen.
- Whether the full cycle holds the direction when the agent leads; it ran once (T8) with the agent's independence shown only in part (T5c).
- How the net represents a revision point: resolved in principle on 2026-10-10 by deriving `← now` from the Program Counter (a counter in nodes 6–4 means no current transition); to be seen in practice in T9's closure.
- Whether a hook change in Nexus needs one live-check round per lifecycle event it touches (T8 needed three where one was planned).
- Whether steering as agent behaviour keeps holding without a gate, in ordinary sessions and in hosts, or rots into ritual.
- Whether a net of this shape stays one screen and stays current once the project has more than one line of work.
- Whether the cycle applies to projects with a known path; only the research case has been tried.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions (T1): done 2026-10-09; P4 marked.
- Alignment (T7): done 2026-10-09; P10 marked.
- Cycle in practice (T8): done 2026-10-09; P11 and P6 marked; the route kept.
- Delivery to the first host (T5a): done 2026-10-09; P12 marked.
- Activation in the first host (T5b): partial, 2026-10-10. Expected: a fresh session there states the host's position from the two documents. Obtained: the documents were never written; the host's agent found the missing goal and did not hold it; the operator pointed at §0 and the agent corrected itself. Deviation fed into planning: the entry of the algorithm redesigned, the rules corrected, T9 opened.
- Vertical slice (T9): in Liquid_Nexus, session 1: the Project Goal is agreed with the operator before the charter is written, and the agent names the divergences of interest rather than hiding them; session 2: a fresh session states position and step, proposes a Current Objective inside the horizon with its reason unprompted, does bounded work with a steering line, and is ended by the operator mid-objective with `Step:` and `Came from:` written; session 3: a fresh session continues that operation without redefining the goal or the route, closes the objective with expected-vs-obtained and an assessment of the Project Goal, and proposes continuation or revision. The operator judges each of the five properties by observed behaviour, never by the technical checks; "true but useless" and negative outcomes are results.
- After the first host runs the layer (T5c): the host's operator can tell where their project is from its navigation alone.
