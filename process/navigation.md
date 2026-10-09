---
type: navigation
status: approved
state: active
owner: agent
created: 2026-10-06
updated: 2026-10-09
---

# Nexus navigation

## Now

Position: Nexus has two layers. Layer one, knowledge of the project, is shipped as 1.3.0 and runs in several host projects. Layer two, joint management of the project by operator and agent, exists only in this repository: its purpose is recorded (decision `knowledge/decisions/decision--system--second-layer-purpose.md`), its foundations are confirmed consistent (P10), and on 2026-10-09 the management cycle ran once end to end on a real piece of work (T8, `process/iteration--run-cycle.md`): the runtime now reads `process/` at session start and after compaction, checked live, and the operator judged the technical result positive and the managerial result positive but limited, since the agent's independence in management was shown only in part. The position gate stays a deferred hypothesis; nothing in the run called for it. The second layer has never left this repository.

Heading: revision point, 2026-10-09. T8 has fired; the next objective is proposed by the agent and not yet agreed, so no transition is current. The agent's proposal: T5, install the second layer in one host and run the cycle there once with the agent leading, which tests the two open uncertainties at once (does the cycle apply outside the research case; does the agent propose first when the operator does not lead). The smaller alternative: a second run here, on a piece of work the agent chooses and leads, before any host.

Why here: every path to the goal (P9) passes through P8, one host running the layer, and the feasibility of that step is unknown: the cycle has been tried only on Nexus itself, a research project, by the two people who designed it. The limited managerial result says the layer's weakest part is the agent's initiative, and a host is where that is tested without the designers' memory to lean on.

Ignoring: building the position gate; validator rules for process documents; the per-turn digest and the staleness line; any picture of the net; how the route is shown to people (a map with plain names, levels of detail by activity). Approving the process-space rules (they say they become `approved` after the cycle has run once): a decision for the operator, proposed, not taken here. Anything concerning the hosts' own projects beyond carrying `process/`.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [x] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone. check: 2026-10-09, session start, position and heading stated from the two files and confirmed by the operator the same day.
- [x] P10 foundations-aligned — charter, rules and navigation agree with the management goal and cycle, and operator and agent confirm there is no substantive contradiction. check: operator's confirmation on 2026-10-09, session archive session--progressive-resolution--2026-10-09--537ddd7b.md; commits 650abc5, 7ae79a9, e7aa68c.
- [x] P11 cycle-checked — one real piece of Nexus work has gone through all six steps of the cycle, and the operator judges that the direction held. check: operator's judgement 2026-10-09: technical result positive, managerial positive but limited (direction held, obstacles removed without widening, expected compared with obtained; the agent's independence shown only in part); contract process/iteration--run-cycle.md, closed; session archives 537ddd7b, 2ab1e556, fd9a877a, ab71248a of 2026-10-09.
- [x] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both. check: live 2026-10-09, fresh session twice and compaction once after the fixes; the agent restated the position from the injected documents each time; commits fa16c69, b041b48, fc48009.
- [ ] P8 host-runs — one host project runs the second layer.
- [ ] P9 released — the second layer is shipped as the next Nexus version.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold. Deferred branch.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn. Deferred branch.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T7 align-foundations: P3 → P10  ! — done 2026-10-09; contract process/iteration--foundations-alignment.md
- T1 cold-read-check: P3 → P4  ! — at session start a fresh agent states position and reason from the two files; the operator judges
- T8 run-cycle: P10 P4 → P11 P6  ! — done 2026-10-09; contract process/iteration--run-cycle.md. One real piece of Nexus work through all six steps (bootstrap reads process/ at session start and after compaction; absorbed the former T3 teach-bootstrap). Feasibility was unknown and is now shown, with the managerial result limited
- T5 install-in-host: P6 → P8  !? — one host receives process/ and runs the cycle once there. Proposed as the next objective on 2026-10-09, not yet agreed; no `← now` until it is: the net has no mark for a revision point (gap named in T8's closure)
- T6 release: P8 → P9 — tag and ship
- T2 write-net-paper-test: P3 → P5  ? — deferred 2026-10-09 with the gate; paper half held, cold reading failed; contract kept in process/iteration--net-paper-test.md
- T4 build-position-gate: P5 P6 → P7 — deferred hypothesis: built only if real work shows that steering as agent behaviour does not hold the direction

## Uncertainty points

- Whether the full cycle holds the direction when the agent leads; it ran once (T8) with the direction held, but part of the decisions followed the operator's direct instructions, so the agent's independence in management is shown only in part.
- Whether a hook change in Nexus needs one live-check round per lifecycle event it touches (T8 needed three where one was planned).
- How the net represents a revision point: between the firing of the current transition and the agreement on the next objective there is no `← now`, and the rules demand exactly one.
- Whether steering as agent behaviour keeps holding without a gate, in ordinary sessions and in hosts, or rots into ritual.
- Whether a net of this shape stays one screen and stays current once the project has more than one line of work, and whether one nearest goal at a time is enough.
- Whether the cycle applies to projects with a known path; only the research case has been tried.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions (T1): the agent states position and reason from the two files alone; the operator judges. First run 2026-10-06: position right, reason absent; the file was amended. 2026-10-08: the file failed its cold reading and was rewritten on 2026-10-09. 2026-10-09, start of session: position and heading stated and confirmed by the operator; P4 marked.
- Alignment (T7): the operator confirms that the strategic goal, the cycle, the division of responsibility, the planning rules and the three documents form a consistent system; then P10 is marked. Done 2026-10-09: confirmed and marked.
- Cycle in practice (T8): one real piece of work goes through all six steps. Technical result: a fresh session and a post-compaction session begin with the position stated from what the runtime injected. Managerial result: the operator judges whether the restored position was actually used to hold direction, choose actions, compare expected with obtained and decide the route together; records of six steps are not proof, the work done is. If the obtained result matches the expected one, keeping the route is a valid outcome of the revision step. Done 2026-10-09: technical positive (session start twice, compaction once after two fixes found by the check itself); managerial positive but limited (the agent's independence shown only in part); P11 and P6 marked; the route kept.
- Steering check (2026-10-08): the operator ran dry runs and an ordinary session and judged the behaviour useful (the agent named unchecked assumptions, offered the choice, proposed a route revision) and the full cycle unconfirmed. Recorded 2026-10-09 in the decision.
- Paper test (T2): deferred with the gate; resumes only if T8 shows the habit insufficient.
- After the runtime change (T3, absorbed in T8): the same check as T1, with no manual reading. Done 2026-10-09, see T8.
- After the first host (T5): the host's operator can tell where their project is from its navigation alone.
