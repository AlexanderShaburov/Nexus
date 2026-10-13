---
type: plan
scope: system
status: in-progress
created: 2026-10-13
updated: 2026-10-13
source_of_truth: false
knowledge_visibility: development
plan_status: in_progress
theme: progressive-resolution
tags: [plan, second-layer, management-algorithm, hooks, user-prompt-submit, program-counter, experiment]
---

## Relations

- depends_on:
  - [Management Algorithm Specification](../specs/spec--system--management-algorithm.md) — §§1–3 are the text delivered; the handler cuts it by the headings of §1–§4.
  - [Process Space Specification](../specs/spec--system--process-space.md) — §8.3 is the contract of what the runtime delivers at every prompt; `Step:` and `Came from:` (§6) are the position read.
  - [Nexus Update Specification](../specs/spec--system--nexus-update.md) — §2.2 defines the hook entry as the unit a host receives; it decided how the hooks are registered.
- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2g describes the three prompt hooks.

---

# Plan: the management algorithm and the saved position delivered at every prompt

Plan status: **in progress**. Built and checked by tests and one live session in the template on 2026-10-13; released as Nexus 1.6.0 for an experiment in a host. Whether it changes the agent's behaviour is not shown. This is an experiment the operator decided on, not a confirmed part of the second layer.

## 1. Why

Three observations in a row on 2026-10-11, in two projects, showed the same gap: when a piece of work ended or failed by its criterion, the agent named a next step without evaluating the result against the Project Goal (node 7 of the algorithm skipped) and without applying the plan-fit decision on its own. The likely cause recorded then, and not verified: the algorithm's document is not in the mandatory reading set, so a session acts from the project's records and the `## Steering` section, which has no line for what follows the end or failure of work (`process/navigation.md`, Uncertainty points; `process/iteration--host-cycle.md`).

The change tests that cause directly: put the algorithm's own text and the saved position in front of the agent at every prompt, as context it receives, not as a file it may choose to open.

## 2. What is built

At every `UserPromptSubmit` three hooks answer, each with its own output under Claude Code's limit of 10,000 characters per hook:

| Hook | Delivers | Writes |
|---|---|---|
| `nexus-prompt-gate.py` | the turn contract (or the bootstrap reminder), then instructions for reading the operator's message against the current operation, then the saved position parsed from `## Now` of `process/navigation.md`: charter status, node, Current Objective, `Step:` and `Came from:` verbatim, the iteration contracts in progress | the per-turn runtime state, as before; nothing in `process/` |
| `nexus-algorithm-core.py` | §§1–2 of the algorithm spec, verbatim: definitions and the diagram | nothing |
| `nexus-algorithm-reading.py` | §3 of the algorithm spec, verbatim: reading and transition rules | nothing |

The two algorithm hooks are launchers of one line of work each; the text is cut by `nexus-management-algorithm.py`, which reads the spec at every call, so the spec stays the single source and no copy of the algorithm exists in a hook.

Nothing is guessed and nothing is silently cut. Each failure has its own explicit message in place of the content: the spec unreadable (`ALGORITHM UNAVAILABLE`), a heading of §1–§4 missing, repeated or out of order (`ALGORITHM FORMAT ERROR`), a part over 9,800 characters (`ALGORITHM PART TOO LARGE`), the navigation unreadable or without exactly one `Step:`, `Came from:` and `Heading:` (`PROGRAM COUNTER UNAVAILABLE`), a `Step:` that does not begin with a node (`PROGRAM COUNTER FORMAT UNCLEAR`), the main output over the limit (`NEXUS MANAGEMENT CONTEXT TOO LARGE`; the turn contract is then not repeated and the rules of `CLAUDE.md` stand). Without `process/charter.md` the position block says the second layer is not active.

The hooks gate nothing. They do not check that a transition is correct, and they never move the position: recording a real transition in `Step:` and `Came from:` remains the agent's work.

`CLAUDE.md` `## Steering` gained one paragraph saying the same, and the format of `Step:`.

## 3. A defect found before release, and its fix

As first written, the algorithm handler was registered twice in `.claude/settings.json`, as `python3 "…/nexus-management-algorithm.py" --part core` and `--part reading`. The updater recognises a hook entry only by a command that ends in `/.claude/hooks/nexus-*.py` and keys it `<event>/<basename>` (update spec §2.2). Both entries were therefore foreign to it: the manifest verified clean, and a host would have received the handler and the new prompt gate, whose instructions refer to parts 1/2 and 2/2, but not the two registrations, so the algorithm itself would never have arrived. The validation plan's check S3 also read both commands as missing files.

Fix: one launcher per part (`nexus-algorithm-core.py`, `nexus-algorithm-reading.py`), each registered like every other hook. No change to the updater and none to the unit key, so the version of the updater already installed in a host (1.5.1) delivers them. The handler still accepts `--part`.

## 4. Checks passed (2026-10-13)

- `python3 -m unittest discover -s tests -p 'test_nexus_management_context.py'`: 14 tests, on a temporary project. Three distinct registrations; **every registration is a unit the updater recognises**; both parts identical to the spec's text; all three outputs under the limit; the position re-read at the next prompt; the two algorithm hooks leave the turn index alone; bootstrap pending keeps the position; missing navigation, unclear step, missing spec, missing section, oversize part, no charter and an unapproved charter each produce their explicit message.
- The validation plan of `docs/nexus-implementation-report.md`: S1–S6, S8, S9 and the new S10 pass; the manifest is in sync; `nexus-update.py --selftest` passes; the vault validates clean.
- The three hooks run concurrently against a copy of the repository, 20 rounds: three valid outputs every round, the bootstrap state intact, the turn index advanced once per round.
- **Rehearsal of the host update with the 1.5.1 updater.** A scratch project installed at `v1.5.1` through `nexus.py`, given an approved charter, a navigation with `Step:` and an iteration in progress, and a section of its own in `CLAUDE.md`, then updated by its own `tools/nexus-update.py up --apply` to a scratch 1.6.0: plan with no blocking rows (2 updates, 5 additions), the three registrations in `settings.json`, the three files under `process/` byte-identical, the host's own `CLAUDE.md` section kept, post-apply validation clean, a second run a no-op, and the three hooks answering in the updated project with the host's own node and objective.
- One live session in the template (the form with two `--part` registrations, before the fix): the agent reported receiving the text of §§1–3 in context, named the node, the objective and the last transition as recorded, and left the position unchanged on a diagnostic question and on a question about the project's position.

## 5. Not proven

- **That the agent's behaviour changes.** The gap this targets, the review of the Project Goal after work ends or fails and the plan-fit decision applied unprompted, has not been observed with the mechanism in place. A session that knows it is being asked about the algorithm shows nothing about this.
- **The launcher registrations in a live session.** The live check ran on the earlier registration form. The launchers are proven by piping the hook payload, not by Claude Code invoking them; by the project's own rule a hook change needs one live round per lifecycle event it touches, here `UserPromptSubmit`.
- That Claude Code keeps delivering three outputs of this size in full, in every version and when other `UserPromptSubmit` hooks of the user are present. The limit of 10,000 characters per hook is an observed property of the installed Claude Code, not a documented contract checked here.
- The cost: about 15,000 characters arrive at **every** prompt, including in a host without a charter, where the position block says the second layer is inactive and the two algorithm parts are delivered all the same. Its effect on long sessions, on compaction and on the agent's attention to the rest of the context is not measured.
- Whether the text is used as a working procedure or decays into a preamble that is skipped, the same question the `## Steering` section carries.
- A host whose copy of the algorithm spec differs from the template's: the format errors are tested, the situation was not met.

## 6. Relation to the route

This work is not a step of the Current Objective in progress (`process/iteration--host-cycle.md`, one full management cycle in Liquid_Nexus) and does not close or replace it. It was accepted by the operator on 2026-10-13 as a bounded technical task. It does change the conditions of that objective: its contract said nothing more would change on the Nexus side, and the one element of its check A still unobserved will be observed in a host that runs 1.6.0. Whether the mechanism becomes part of the second layer is decided from what the host experiment shows.
