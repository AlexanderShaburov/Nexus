---
type: iteration
id: T8
status: approved
state: in_progress
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
depends_on: [process/iteration--foundations-alignment.md]
refs: [knowledge/specs/spec--system--process-space.md, knowledge/specs/spec--system--session-bootstrap.md]
---

# Run the cycle once on real work

Proposed and agreed 2026-10-09. The operator asked that two results be judged apart: the technical one (the documents are read automatically, position and objective restored) and the managerial one (the restored position is actually used to hold direction, choose actions, compare expected with obtained and decide the route together). Records of six steps are not proof of the cycle; the work done is. The revision branch is not to be forced: if the obtained result matches the expected one, keeping the route is a valid outcome of the revision.

Status 2026-10-09, same session: the hook change is built (`_nexus_common.py` gains `process_documents()` and `required_files()`; the bootstrap hook lists the process documents and records them in the state; the tool gate's ledger and the prompt gate's reminder use the recorded set) and checked by piping against a copy of the repository: reading set with and without a charter, ledger pending until the process documents are read, reminder naming them, completion on the last read. Mirrors updated: bootstrap spec, rules §8 and §11, architecture, `CLAUDE.md`, validation plan (B2, B2a). The live check (fresh session; compaction) is the operator's and has not happened yet.

## Question

Can operator and agent run the management cycle once, end to end, on a real piece of Nexus work, with the direction held and the expected result compared with the obtained one at closure? The piece of work proposed: the position survives session start and context compaction without manual reading.

## Input

- The foundations of the second layer, confirmed consistent on 2026-10-09 (charter, rules with the cycle in §0, this navigation).
- The runtime as it is: bootstrap injects the Mandatory Startup Reading Set from the vault only; `process/` is read by hand because the Steering section of `CLAUDE.md` says so; after compaction nothing brings the position back.
- The bootstrap contract, which already says what should happen (rules §8.1 and §8.2): when `process/charter.md` exists, the reading set grows by the charter, the navigation and every iteration in progress, at session start and at compaction.

## Work

Run the six steps on this one objective, with the agent proposing and the operator deciding at steps 4, 5.1 and 6. The work inside: the bootstrap hook adds the three kinds of process document to the reading set when a charter exists, so that the tool gate's read ledger covers them and the position is reinjected at compaction; the texts that mirror the hook (bootstrap spec, rules §8 and §11, architecture, `CLAUDE.md` reading set and Steering step 1) say the same; the validation plan for hooks is run. Expected size: one change in one hook plus its mirrors, one to two sessions, no new gate, no new field, no new hook. At closure: compare this expectation with what happened, and record the operator's judgement of the run as the check of P11.

## We deliberately ignore

- The per-turn digest of `## Now`, the staleness line, the validator rules for `process/`: comfort, not necessity for the first run.
- The position gate and anything that denies work.
- Installing in a host: the cycle must run here first.
- Making the first run exercise the revision branch (exit B of the block) on purpose; it is tested when a real obstacle appears.

## Artifact

A fresh session and a post-compaction session both begin with the position, heading and reason stated from what the runtime injected, without the operator asking; P11 and P6 marked with the operator's judgement as their check; this file closed with the expected-vs-obtained comparison.

## Success

- The operator starts a fresh session with an ordinary task and the agent's first message states where the project is and what is being tested, without being told to read anything.
- The operator compacts the context mid-session and the agent restates the position afterwards.
- The six steps are visible in the session archive and in this file: objective stated, plan proposed and agreed, work done, result checked, expected compared with obtained, position revised in the navigation.
- The operator judges that the direction held: no work was done outside the stated objective without the choice being offered.

## Unknowns to observe

- Whether the cycle's steps feel like ritual on a piece of work this small, or carry weight.
- Whether a trigger for revision (step 6) fires during the run, and which one.
- Whether the operator can tell the cycle ran from the archive alone, or only from memory of the session.
