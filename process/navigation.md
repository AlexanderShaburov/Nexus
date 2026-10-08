---
type: navigation
status: approved
state: active
owner: agent
created: 2026-10-06
updated: 2026-10-08
---

# Nexus navigation

## Now

Position: Nexus has two layers of context. Layer one, knowledge of the project, is shipped as 1.3.0 and runs in several host projects (P1). Layer two, management of the project, is built in this repository only: its rules are a draft specification (P2), the charter and this navigation are agreed (P3). On 2026-10-08 the operator restated what the layer is for: joint, purposeful steering of the project by operator and agent, against burrowing and premature detail. The paper test of the net (T2) has run. The net denies the arbitrage case and surfaces the Nexus case, so it is checkable on paper; but this file failed its cold reading, so P5 stays unmarked. Results: process/iteration--net-paper-test.md.

Heading: does steering as agent behaviour hold the project's direction in ordinary work? An experimental Steering section in CLAUDE.md (2026-10-08) is checked by the operator in a fresh session, without announcing the check. This is a test of the agent, not of the net, so it is not a transition below; the net keeps T2 as its formal current step until the result says what P5 and the gate are for.

Why here: the layer exists for steering. Whether a habit is enough, or a gate is needed, decides the purpose of P5, T4 and P7, so it is the question everything downstream waits on. Testing the habit costs one session and no code; building the gate first would be work below an unverified assumption, that goodwill rots into ritual.

Ignoring: the position gate (T4), a Mermaid view of the net, any change to P5 or to the shape of the net, until the steering check has a result. T1, the cold-read check, keeps running at each session start without extra work. Anything concerning the hosts' own projects.

## Net

Places (project states; [x] established, with its check):
- [x] P1 layer-one-shipped — the knowledge layer is released as 1.3.0. check: runs in several host projects.
- [x] P2 rules-drafted — the process-space specification exists as a draft. check: knowledge/specs/spec--system--process-space.md.
- [x] P3 files-agreed — charter and navigation exist and the operator agreed to them. check: commits 6a10d66 and 255e83d.
- [ ] P4 files-carry-position — a fresh agent states the position and the reason from the two files alone.
- [ ] P5 net-checkable — the net supports a mechanical enabling check and still reads cold.
- [ ] P6 runtime-reads — bootstrap and PreCompact load process/; the position survives both.
- [ ] P7 position-gated — the position claim is enforced at the first mutating call of a turn.
- [ ] P8 host-runs — one host project runs the second layer.
- [ ] P9 released — the second layer is shipped as the next Nexus version.

Transitions (work; inputs → outputs; ! critical, ? feasibility unknown, ← now current):
- T1 cold-read-check: P3 → P4  ! — at session start a fresh agent states position and reason from the two files; the operator judges
- T2 write-net-paper-test: P3 → P5  !?  ← now — run two known cases through the net on paper: the arbitrage bot and Nexus itself
  task: process/iteration--net-paper-test.md
- T3 teach-bootstrap: P4 P5 → P6 — the Mandatory Startup Reading Set grows by process/
- T4 build-position-gate: P5 P6 → P7 — the claim gains --step and the tool gate checks the net
- T5 install-in-host: P7 → P8 — one host receives process/ and runs it
- T6 release: P8 → P9 — tag and ship

## Uncertainty points

- Whether a net of this shape stays one screen once the project has more than one line of work.
- Whether the agent keeps the net current without a gate forcing it, or whether it rots like a plan.
- Whether "--step none", for work that changes no project state, is a hole wide enough to let burrowing through.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions (T1): the agent states position and reason from the two files alone; the operator judges. First run 2026-10-06: position right, reason absent; the file was amended.
- Paper test (T2): the net denies the arbitrage case and surfaces the Nexus case; the operator reads the file cold and finds it one screen. Run 2026-10-06/08: both cases as expected; cold reading failed. P5 not marked.
- Steering check (2026-10-08): the operator runs a fresh session with an ordinary task and judges whether the agent names the milestone or uncertainty the work serves, notices premature depth or a route change, and offers the choice instead of blocking or complying silently.
- After the runtime change (T3): the same check as T1, with no manual reading.
- After the first host (T5): the host's operator can tell where their project is from its navigation alone.
