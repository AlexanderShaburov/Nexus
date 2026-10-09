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

Position: Nexus has two layers. Layer one, knowledge of the project, is shipped as 1.3.0 and runs in several host projects. Layer two, joint management of the project by operator and agent, exists only in this repository: its rules are a draft specification, the charter and this navigation are agreed. On 2026-10-09 the operator paused building and restated what the layer is for: not carrying the position between sessions but managing the project together, as an iterative cycle with a bounded planning horizon (charter, Goal; rules §0; decision `knowledge/decisions/decision--system--second-layer-purpose.md`). The charter, the rules and this file were rewritten from that purpose the same day. The position gate, which the previous route ran through, is now a deferred hypothesis.

Heading: are the foundations of layer two consistent: strategic goal, management cycle, division of responsibility between operator and agent, planning rules and the three documents, with no substantive contradiction? The agent's part of the alignment is done; the operator's confirmation is pending. Contract: `process/iteration--foundations-alignment.md`.

Why here: everything downstream rests on these documents. The next step, running the cycle once in real work, tested against documents that still encoded the gate-first route would test the wrong thing. Alignment costs one session and no code.

Ignoring: building the position gate; teaching bootstrap to read `process/`; validator rules for process documents; any picture of the net; how the route is shown to people (a map with plain names, levels of detail by activity). All of it waits until the cycle has run once in real work. Anything concerning the hosts' own projects.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [ ] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone.
- [ ] P10 foundations-aligned — charter, rules and navigation agree with the management goal and cycle, and operator and agent confirm there is no substantive contradiction.
- [ ] P11 cycle-checked — one real piece of Nexus work has gone through all six steps of the cycle, and the operator judges that the direction held.
- [ ] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both.
- [ ] P8 host-runs — one host project runs the second layer.
- [ ] P9 released — the second layer is shipped as the next Nexus version.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold. Deferred branch.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn. Deferred branch.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T7 align-foundations: P3 → P10  !  ← now — bring charter, rules and navigation into one consistent system with the restated purpose; the operator confirms
  task: process/iteration--foundations-alignment.md
- T1 cold-read-check: P3 → P4  ! — at session start a fresh agent states position and reason from the two files; the operator judges
- T8 run-cycle: P10 → P11  !? — one real piece of Nexus work through all six steps of the cycle, assessment to revision; the operator judges whether the direction held
- T3 teach-bootstrap: P4 P11 → P6 — the Mandatory Startup Reading Set grows by process/
- T5 install-in-host: P6 → P8 — one host receives process/ and runs it
- T6 release: P8 → P9 — tag and ship
- T2 write-net-paper-test: P3 → P5  ? — deferred 2026-10-09 with the gate; paper half held, cold reading failed; contract kept in process/iteration--net-paper-test.md
- T4 build-position-gate: P5 P6 → P7 — deferred hypothesis: built only if real work shows that steering as agent behaviour does not hold the direction

## Uncertainty points

- Whether the full cycle can be run in real work and holds the direction; only fragments have been seen.
- Whether steering as agent behaviour keeps holding without a gate, in ordinary sessions and in hosts, or rots into ritual.
- Whether a net of this shape stays one screen and stays current once the project has more than one line of work, and whether one nearest goal at a time is enough.
- Whether the cycle applies to projects with a known path; only the research case has been tried.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions (T1): the agent states position and reason from the two files alone; the operator judges. First run 2026-10-06: position right, reason absent; the file was amended. 2026-10-08: the file failed its cold reading and was rewritten on 2026-10-09. 2026-10-09, start of session: position and heading stated and not contradicted by the operator; not counted as the check, the operator has not judged it.
- Alignment (T7): the operator confirms that the strategic goal, the cycle, the division of responsibility, the planning rules and the three documents form a consistent system; then P10 is marked.
- Cycle in practice (T8): one real piece of work goes through all six steps; the operator judges whether the direction held and whether the expected result was compared with the obtained one at closure.
- Steering check (2026-10-08): the operator ran dry runs and an ordinary session and judged the behaviour useful (the agent named unchecked assumptions, offered the choice, proposed a route revision) and the full cycle unconfirmed. Recorded 2026-10-09 in the decision.
- Paper test (T2): deferred with the gate; resumes only if T8 shows the habit insufficient.
- After the runtime change (T3): the same check as T1, with no manual reading.
- After the first host (T5): the host's operator can tell where their project is from its navigation alone.
