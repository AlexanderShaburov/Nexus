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

Position: Nexus has two layers. Layer one, knowledge of the project, is released and runs in several host projects. Layer two, joint management of the project by operator and agent: its purpose is recorded (decision `knowledge/decisions/decision--system--second-layer-purpose.md`), its rules are approved and binding since 2026-10-09 (`spec--system--process-space.md`), the cycle ran once end to end on real work here (T8; technical result positive, managerial positive but limited), and on 2026-10-09 the layer's infrastructure reached its first host: Nexus 1.4.0 is released and Liquid_Nexus runs it with its own data shown intact (T5a). In that host the layer is **inactive**: it has no charter, and the runtime says so in one line. The second layer has never been active outside this repository; the position gate stays a deferred hypothesis.

Heading: revision point, 2026-10-09. T5a has fired; the next objective is proposed and not yet agreed, so no transition is current. The agent's proposal: split the former T5b in two. First (T5b activate-in-host) Liquid_Nexus gets its own charter and navigation, written by operator and agent in dialogue in a session there, from the host's real state and purpose, with only the delivered documents as rules; the check is the next fresh session in the host stating the host's position and heading from what the runtime injected, and the operator judging it true. Second (T5c host-cycle, not elaborated) one cycle of real work in the host with the agent leading. The alternative: both in one iteration.

Why here: every path to the goal (P9) passes through P8, one host running the layer; the infrastructure is there, so the next unknown on the path is whether the format fits a real project that is not Nexus and whether the host's agent, without the designers' memory and without templates, can write the two documents from the rules alone. That is a smaller and earlier uncertainty than the cycle itself, and the cycle rests on it; hence the split. The limited managerial result of T8 (the agent's initiative) is tested in T5c, where the agent must lead.

Ignoring: building the position gate; validator rules for process documents; the per-turn digest and the staleness line; any picture of the net; how the route is shown to people (a map with plain names, levels of detail by activity); install templates for charter and navigation (the host writes its own); a new installer or a rollback command (the updater and git suffice); other hosts. Anything concerning the hosts' own projects beyond carrying `process/`.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [x] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone. check: 2026-10-09, session start, position and heading stated from the two files and confirmed by the operator the same day.
- [x] P10 foundations-aligned — charter, rules and navigation agree with the management goal and cycle, and operator and agent confirm there is no substantive contradiction. check: operator's confirmation on 2026-10-09, session archive session--progressive-resolution--2026-10-09--537ddd7b.md; commits 650abc5, 7ae79a9, e7aa68c.
- [x] P11 cycle-checked — one real piece of Nexus work has gone through all six steps of the cycle, and the operator judges that the direction held. check: operator's judgement 2026-10-09: technical result positive, managerial positive but limited (direction held, obstacles removed without widening, expected compared with obtained; the agent's independence shown only in part); contract process/iteration--run-cycle.md, closed; session archives 537ddd7b, 2ab1e556, fd9a877a, ab71248a of 2026-10-09.
- [x] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both. check: live 2026-10-09, fresh session twice and compaction once after the fixes; the agent restated the position from the injected documents each time; commits fa16c69, b041b48, fc48009.
- [x] P12 host-updated — Liquid_Nexus carries Nexus 1.4.0 with every system component the second layer needs, its own data and settings untouched; the layer is not active there yet. check: operator's report 2026-10-09: `up` 1.3.0 → 1.4.0 without errors, `status` 61 unchanged / 0 customized / 0 refused, checksum comparison of the protected areas identical, a fresh session there bootstrapped and reported the layer inactive; tag v1.4.0 on 413b96f; contract process/iteration--deliver-second-layer.md, closed.
- [ ] P13 host-position-carried — Liquid_Nexus has its own charter and navigation, and a fresh session there states the host's position from what the runtime injected; the operator judges it true.
- [ ] P8 host-runs — one host project runs the second layer.
- [ ] P9 released — the second layer is shipped as the next Nexus version.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold. Deferred branch.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn. Deferred branch.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T7 align-foundations: P3 → P10  ! — done 2026-10-09; contract process/iteration--foundations-alignment.md
- T1 cold-read-check: P3 → P4  ! — at session start a fresh agent states position and reason from the two files; the operator judges
- T8 run-cycle: P10 P4 → P11 P6  ! — done 2026-10-09; contract process/iteration--run-cycle.md. One real piece of Nexus work through all six steps (bootstrap reads process/ at session start and after compaction; absorbed the former T3 teach-bootstrap). Feasibility was unknown and is now shown, with the managerial result limited
- T5a deliver-second-layer: P6 → P12  ! — done 2026-10-09; contract process/iteration--deliver-second-layer.md. Release 1.4.0 with the process-space rules; Liquid_Nexus updated with the existing updater; protected areas byte-identical; no new mechanism
- T5b activate-in-host: P12 → P13  !? — Liquid_Nexus's charter and navigation written by operator and agent in dialogue there, from the delivered rules alone; the next fresh session states the host's position. Proposed 2026-10-09 as the next objective, not yet agreed; no `← now` until it is
- T5c host-cycle: P13 → P8  !? — one cycle of real work in the host with the agent leading; the first test of the layer outside Nexus. Not elaborated until T5b is done
- T6 release: P8 → P9 — tag and ship
- T2 write-net-paper-test: P3 → P5  ? — deferred 2026-10-09 with the gate; paper half held, cold reading failed; contract kept in process/iteration--net-paper-test.md
- T4 build-position-gate: P5 P6 → P7 — deferred hypothesis: built only if real work shows that steering as agent behaviour does not hold the direction

## Uncertainty points

- Whether the full cycle holds the direction when the agent leads; it ran once (T8) with the direction held, but part of the decisions followed the operator's direct instructions, so the agent's independence in management is shown only in part.
- Whether a hook change in Nexus needs one live-check round per lifecycle event it touches (T8 needed three where one was planned).
- How the net represents a revision point: between the firing of the current transition and the agreement on the next objective there is no `← now`, and the rules demand exactly one. Observed 2026-10-09: the gap lasted one turn; the next contract was drafted the same day and took the mark while still a draft.
- Whether the process-space format fits a real project other than Nexus, and whether a host's agent writes a charter and navigation from the delivered rules alone, without templates and without the designers' memory (T5b).
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
- Delivery to the first host (T5a): `up --apply` in Liquid_Nexus exits 0 with validation clean; the update commit touches only Nexus-owned paths and the baseline; a fresh session there reports the missing charter in one line. Not a proof of the layer, by the operator's boundary. Done 2026-10-09, all three observed by the operator; P12 marked.
- Activation in the first host (T5b): after the charter and navigation exist in Liquid_Nexus, a fresh session there lists them as items 5 and 6 and states the host's position and heading unprompted; the operator judges whether the statement is true of the host.
- After the first host runs the layer (T5c): the host's operator can tell where their project is from its navigation alone.
