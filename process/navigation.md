---
type: navigation
status: approved
state: active
owner: agent
created: 2026-10-06
updated: 2026-10-06
---

# Nexus navigation

## Now

Position: Per the charter, Nexus has two layers of context. The first layer, knowledge of the project, is done: released as version 1.3.0 and running in several host projects (P1). The second layer, management of the project, is the current change, built in this repository only. Reached: the layer's rules exist as a draft specification (P2); the charter and this navigation exist and are agreed (P3). On 2026-10-06 the operator and the agent agreed the goal of the layer, coordinated movement toward the goal without burrowing and without stalling, and chose a net of project states and transitions as its carrier; this file now holds that net. The runtime does not read these files yet, and no host has them.

Heading: T2, the paper test of the net: is a one-screen net structured enough for a mechanical check of which work is permitted now, while still reading cold? Contract: process/iteration--net-paper-test.md.

Why here: T2 is critical and its feasibility is unknown. Every path to the release passes through P5: the runtime reading (T3) and the position gate (T4) both consume it. If a net cannot be both machine-checkable and one-screen readable, the layer does not work as conceived, and no hook would fix that. Checking it on paper is cheap; building hooks first would be work below an unproven critical transition.

Ignoring: T1, the cold-read check, is permitted too and stays open: its first run on 2026-10-06 gave "position right, reason absent", and the next run happens at the next session start without extra work. The runtime (T3), the gate (T4), hosts (T5) and release (T6) wait on P5. Anything concerning the hosts' own projects.

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
- Paper test (T2): the net denies the arbitrage case and surfaces the Nexus case; the operator reads the file cold and finds it one screen.
- After the runtime change (T3): the same check as T1, with no manual reading.
- After the first host (T5): the host's operator can tell where their project is from its navigation alone.
