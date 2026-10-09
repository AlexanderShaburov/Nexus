---
type: iteration
id: T8
status: approved
state: done
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
closed: 2026-10-09
depends_on: [process/iteration--foundations-alignment.md]
refs: [knowledge/specs/spec--system--process-space.md, knowledge/specs/spec--system--session-bootstrap.md]
---

# Run the cycle once on real work

Proposed and agreed 2026-10-09. The operator asked that two results be judged apart: the technical one (the documents are read automatically, position and objective restored) and the managerial one (the restored position is actually used to hold direction, choose actions, compare expected with obtained and decide the route together). Records of six steps are not proof of the cycle; the work done is. The revision branch is not to be forced: if the obtained result matches the expected one, keeping the route is a valid outcome of the revision.

Status 2026-10-09, same session: the hook change is built (`_nexus_common.py` gains `process_documents()` and `required_files()`; the bootstrap hook lists the process documents and records them in the state; the tool gate's ledger and the prompt gate's reminder use the recorded set) and checked by piping against a copy of the repository: reading set with and without a charter, ledger pending until the process documents are read, reminder naming them, completion on the last read. Mirrors updated: bootstrap spec, rules §8 and §11, architecture, `CLAUDE.md`, validation plan (B2, B2a). The live check (fresh session; compaction) is the operator's and has not happened yet.

Status 2026-10-09, live check, step 1 (session start): positive. The bootstrap context of a fresh session listed the three process documents as items 5 to 7 and the agent's first message stated position and heading from them.

Status 2026-10-09, live check, step 2 (compaction): a defect, then a fix. On `/compact` the CLI reported `PreCompact [nexus-bootstrap.py] failed: Hook JSON output validation failed — hookSpecificOutput.hookEventName` does not accept `"PreCompact"`. Cause: the hook emitted the reading set as `hookSpecificOutput` on both events, and Claude Code accepts that shape for `SessionStart` but not for `PreCompact`, which fires *before* compaction; the event that fires *after* compaction is `SessionStart` with `source: compact`, and that run of the same hook had already been doing the actual re-injection. Fix, minimal: on `PreCompact` the hook resets the session state and prints nothing; on `SessionStart` it injects as before and names the source in the `Event:` line. No new hook, gate or field; the `PreCompact` registration stays, so the gates are re-armed before compaction even if the post-compaction `SessionStart` were missing. Checked by piping on a copy of the repository: `PreCompact` exits 0 with empty stdout and resets `state.json` to `pending` with six required files; `SessionStart` with `source: compact` emits the reading set with items 5 to 7 and `Event: SessionStart (source: compact)`. Mirrors updated: architecture §2 and control flow, bootstrap spec Trigger, rules §8.2, validation plan (hook table, B2a). Deviation from the expected size: one more round than planned; the live check of compaction is to be repeated. Technical result of step 2 stays open until that repeat.

Status 2026-10-09, live check, step 1 repeated, and a deviation found and removed: the fresh session's bootstrap context listed the three process documents and the agent stated the position from them (positive, second time). But after the agent read all seven files in one parallel batch, the prompt gate still asked for `process/charter.md`: the read had happened and the ledger had not recorded it. Classified by the operator as a reliability defect of the accounting, not as agent behaviour. Cause, confirmed by reproduction on a copy (20 of 20 rounds lost entries; 4 left `state.json` torn, which the gate reads as *no state* and fails open): Claude Code runs the `PreToolUse` hooks of parallel tool calls concurrently, and the tool gate did load → append → save on `state.json` with no lock and a non-atomic write. Fix, minimal: the gate runs under an `flock` on `.nexus/state.lock`, and `save_state` writes a temp file and renames it; no new hook, gate or field, and the first layer is not weakened but tightened (the fail-open on a torn file is gone). After the fix 30 of 30 rounds complete with a full ledger. Mirrors: architecture §2 and §3, bootstrap spec (ledger paragraph), validation plan (S9, B2), `.nexus/README.md`, `.gitignore` and the updater's `never_touch` and ensure-lines. Deviation from the expected size: one more hook change than planned, found by the live check itself. Open from step 1: nothing; step 2 (compaction) still to be repeated.

Status 2026-10-09, live check, step 2 repeated: positive. `/compact` ran with `PreCompact` reporting success; the post-compaction `SessionStart` (`source: compact`) injected the reading set with the three process documents as items 5 to 7; the agent read the seven files in one parallel batch, the ledger recorded all of them at the first attempt (first live run of the lock), and the agent restated the position from the injected documents before being asked anything else. The operator confirmed the technical result the same day. Observed and not counted as a defect: after `/compact` the agent did not speak until the next user message; most likely the ordinary wait for a prompt, not a hang.

Operator's judgement, 2026-10-09 (the check of P11): technical result positive. Managerial result positive but limited: the original objective was held throughout, obstacles were investigated and removed without unjustified widening of the project, expected results were compared with obtained ones; but the agent's independence in management is shown only in part, since some decisions were taken after direct instructions from the operator. Closed with this result.

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

Closed 2026-10-09. Expected: one change in one hook plus its mirrors, one to two sessions, no new gate, field or hook. Obtained: three hook changes (the reading set grows by the process documents; `PreCompact` reset-only because the CLI rejects context injection there; a lock and an atomic write in the tool gate because parallel reads lost ledger entries), each with its mirrors; four sessions on one day; six commits before this closure (`fa16c69`, `0e8e1bd`, `1dd56b8`, `b041b48`, `a044dab`, `fc48009`); no new gate, field or hook, as expected. Causes of the deviation: the first two extra rounds came from facts about the runtime that no document held and only the live check could produce (an undocumented event-schema restriction of the installed Claude Code; a latent race that only a parallel bootstrap batch exercises). Neither changes the route: both were found by the check the iteration had planned, and both tightened the first layer. What the deviation changes in the plan: a hook change is to be budgeted with one live-check round per lifecycle event it touches, not one round in total. The question of this iteration has an answer: the cycle can be run once on real work and the direction holds; the independence of the agent's management is only partly shown. One thing the plan did not foresee: at a revision point, after the current transition fires and before the next objective is agreed, the net has no transition to mark `← now`, and the grammar in the rules (§6) demands exactly one; this closure leaves the mark absent on purpose and names the gap below.

Live check protocol (for the session that reads this at bootstrap; written 2026-10-09):

1. Technical, session start. The operator opens a fresh session with an ordinary task and does not mention `process/`. Expected: the bootstrap context lists `process/charter.md`, `process/navigation.md` and this file as items 5 to 7; the agent's first message carries the confirmation block and then two sentences: where the project stands and that the question being tested is this run of the cycle. If the list lacks the process documents, or the agent reads them only because `CLAUDE.md` says so, the technical result is negative: say so, do not work around it.
2. Technical, compaction. The operator runs `/compact` mid-session. Expected: the bootstrap context returns with the same list; the agent restates the position without being asked.
3. Managerial. Through the ordinary task of that session the agent is expected to: link the work to this objective or say that it serves none and offer the choice; propose before acting where a decision is the operator's; at closure compare what was expected with what was obtained. The operator judges whether the restored position was actually used, not whether it was recited. Records of six steps are not proof.
4. Closure, if both results are positive: mark P11 and P6 in the navigation with the operator's judgement as their check, close this iteration with the expected-vs-obtained comparison, and run the revision step: assess the position, set the horizon, propose the next objective. Keeping the route is a valid outcome. If a result is negative: record it here under Unknowns, keep this iteration open, and propose the correction as a route decision for the operator.

## Unknowns to observe

Observed at closure, 2026-10-09:

- Ritual or weight: not judged by the operator; the steps were visible in the work (objective, agreed plan, three rounds of work and check, comparison, revision), whether they carried weight on a piece this small is still open.
- Trigger for revision: two obstacles fired during the run (the `PreCompact` schema, the ledger race); both were absorbed as rounds inside the iteration and neither changed the route. The revision proper was triggered by the milestone reached.
- Archive alone: not checked; the operator judged from the session.

Still open, carried to the next iteration:

- The agent's independence in management: several decisions were taken after direct instructions from the operator. Whether the agent proposes first, unprompted, in a session where the operator does not lead.
- How the net represents a revision point: between the firing of the current transition and the agreement on the next objective there is no `← now` transition, and the grammar demands one. Either the rules admit the state or the closure must always carry the next contract as a draft, as T7's closure observed.
- Whether a hook change in Nexus is to be budgeted with one live-check round per lifecycle event it touches.
