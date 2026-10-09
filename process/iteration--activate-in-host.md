---
type: iteration
id: T5b
status: approved
state: in_progress
owner: agent
horizon: near
created: 2026-10-09
updated: 2026-10-09
depends_on: [process/iteration--deliver-second-layer.md]
refs: [knowledge/specs/spec--system--process-space.md, knowledge/specs/spec--system--architecture-review.md]
---

# Recover the position of Liquid_Nexus and let the runtime carry it

Proposed 2026-10-09 after T5a delivered the second layer's infrastructure to Liquid_Nexus. The operator approved the direction the same day, and then the contract with two refinements written into step 1 and step 2 (the separation of facts, interpretations and questions is a matter of substance, not of marking every sentence; there is no fixed limit on repeated reconstructions, the agent stops when a repetition no longer brings the picture closer and offers the choice). The refinement that shapes the whole iteration: writing `charter.md` and `navigation.md` is not the goal. The goal is the **actual position of Liquid_Nexus, recovered from what the project already knows**. The host's agent first studies the project's documents, plans, decisions and history and presents a substantive reconstruction of its purpose, its results so far and its uncertainties, keeping three things apart: confirmed facts, the agent's interpretations, and questions only the operator can settle. Only after the operator has agreed to the reconstruction are the two process documents written, from it. The full management cycle in the host is the next iteration (T5c), not this one.

This work happens in Liquid_Nexus, in its own Claude Code sessions, by its own agent, under its own `CLAUDE.md` and the documents 1.4.0 delivered. This file is the contract kept in the Nexus template; the operator carries the brief below into the host. Nexus itself changes only if the host's work shows a defect in the delivered rules, and then through a feedback note from the host, not by hand.

## Question

Can the second layer be activated in a real project other than Nexus from the delivered documents alone: does the host's agent recover a position the operator recognizes as true, do the two documents written from it fit the project, and does the runtime then carry that position into a fresh session without anyone being told to read anything?

## Input

- Liquid_Nexus at Nexus 1.4.0 (T5a): the bootstrap hook reads `process/` when a charter exists, the process-space rules, the second-layer decision and the Steering section are in the host; `process/` does not exist there; the hook says so in one line.
- The host's own knowledge: its vault (index, architecture, specs, decisions, plans, sessions, open questions), its `CLAUDE.md`, its git history. What this template knows of it is one sentence from 2026-10-03: the project aims to describe how an organisation works by non-invasive observation, without interviews or disruption, from traces of activity; and that work on it once drifted into theory far from the project's position. Everything else is to be found there.
- The rules for the two documents: `spec--system--process-space.md` §4 (frontmatter), §6 (sections of `charter.md`; `## Now` with its four lines and `## Net` for `navigation.md`), §9 (the horizon rule: the net may be small and the far places one line each). The reconstruction itself is a review-class task, so `spec--system--architecture-review.md` applies: binding and development documents are both examined before anything is called missing or unknown.

## Work

In Liquid_Nexus, in this order; the operator decides at steps 2 and 4.

1. **Reconstruction.** The host's agent reads the project's knowledge in the vault's read priority, then its plans, sessions and git history, and presents in one message, in the operator's language: (a) the project's purpose and what a good outcome would be; (b) results achieved so far, with the document or commit that shows each; (c) what is in progress or was abandoned; (d) the significant uncertainties; (e) the questions only the operator can settle. Three kinds of statement are kept apart in substance: **confirmed facts** (a document or commit is named), **the agent's interpretations** (its reading of the facts, open to correction), **the operator's questions** (what the agent cannot decide). The form is the agent's choice; what matters is that the origin of every significant claim is clear and facts are not mixed with hypotheses. Marking every sentence is not required. Review-class discipline applies: nothing is called missing without both binding and development documents having been examined.
2. **Agreement.** The operator corrects the reconstruction, answers the questions that have answers now, and names the ones that stay open. The agreed text is the input of step 3. If the operator finds the reconstruction substantially wrong, step 1 is repeated with the corrections. There is no fixed number of repetitions: when a repetition no longer brings the picture closer to a true one, the agent stops, explains the obstacle (what cannot be recovered from the project's knowledge, and why) and offers the choice of what to do next; the aim is accuracy sufficient for management, not an exhaustive description. A reconstruction that cannot be brought to that accuracy is a negative result and is recorded here.
3. **The two documents.** From the agreed reconstruction the host's agent writes `process/charter.md` (owner: operator; the operator confirms every section before it counts) and `process/navigation.md` (owner: agent) in the shape the rules give, plus the host's own `process/README.md` if the operator wants one. Nothing is copied from Nexus's charter or navigation; the horizon rule holds: the nearest step in detail, the rest one line each, the open operator questions in the navigation's uncertainty points. No iteration file is written in this step: the current transition of the host's net gets its contract when T5c begins, and the net may say that the next step is being chosen. The host's `validate-vault.py` stays clean (`process/` is outside it, but the session writes nothing else to `knowledge/` without reason).
4. **The check.** The operator opens a fresh session in Liquid_Nexus with an ordinary task and mentions nothing about `process/`. Expected: the bootstrap context lists the charter and the navigation as items 5 and 6; the agent's first message carries the confirmation block and then states, in two sentences, where Liquid_Nexus stands and what it is heading for; the operator judges whether that statement is true of the project. Positive, negative, or "true but useless" are all results; the last one is recorded as such.
5. **Closure here.** The result, the operator's judgement, the expected-vs-obtained comparison and the unknowns are recorded in this file; P13 is marked or the negative result goes under Unknowns and T5b stays open with a proposed correction. Any defect of the delivered rules found on the way goes into a feedback note in the host (`knowledge/feedback/`, `feedback push`) and is read here before T5c is planned.

Expected size: two or three sessions in the host (reconstruction and agreement; the documents; the check), none here beyond the closure; no change to Nexus; no new mechanism, template or validator rule. Budget, by T8's lesson: repetitions of step 1 continue while each one brings the picture closer; the agent, not a count, calls the stop and offers the choice.

### Brief for the first host session (final, 2026-10-09; the operator pastes it, in their own language)

> We are activating the second layer of Nexus in this project. Do not create `process/` yet.
>
> First recover the actual position of this project from its own knowledge: the vault in its read priority, then `knowledge/plans/`, `knowledge/sessions/`, `knowledge/open-questions/` and the git history. Present one message with: the project's purpose and what a good outcome would be; results achieved so far, each with the document or commit that shows it; what is in progress or abandoned; the significant uncertainties; the questions only I can settle.
>
> Keep confirmed facts, your interpretations and my questions apart in substance: the origin of every significant claim must be clear, and facts must not be mixed with hypotheses. The form is yours. Review discipline applies (`spec--system--architecture-review.md`): examine binding and development documents both before calling anything missing. The aim is accuracy sufficient for managing the project, not an exhaustive description.
>
> I will correct and answer. If a round of corrections no longer brings the picture closer to a true one, stop, explain what cannot be recovered from the project's knowledge and why, and offer me the choice of what to do next.
>
> Only after I have agreed to the reconstruction do we write `process/charter.md` and `process/navigation.md`, by the rules in `spec--system--process-space.md`, from the agreed text; nothing is copied from the Nexus template's own charter. Then I open a fresh session and expect you to state this project's position and heading from what the runtime injects, without being told to read anything.

## We deliberately ignore

- Running the management cycle in the host (T5c): the host's net may end with "next step being chosen".
- Templates for `charter.md` and `navigation.md`, a `process/` index, validator rules for `process/`, the per-turn digest, the staleness line: nothing is added to Nexus during this iteration.
- Correcting the host's vault beyond what the reconstruction needs to cite; findings about the host's knowledge go into the reconstruction as interpretations or operator questions, not into edits.
- Other hosts.
- Whether the Steering section's habits hold in the host (steps 2 to 5 of the cycle in the turn): observed if it happens, not tested here.

## Artifact

In Liquid_Nexus: the agreed reconstruction (kept where the host keeps such things, at least in the session archive); `process/charter.md` confirmed by the operator; `process/navigation.md` with `## Now` and a `## Net` whose marking is the recovered position; both committed. In this file: the operator's judgement of step 4 and the closure. In the Nexus net: P13 marked with that judgement as its check.

## Success

- The reconstruction names its sources, keeps facts, interpretations and operator questions apart, and the operator agrees to it with corrections rather than rejecting it.
- The two documents exist, read cold, follow the rules' shape, and the operator confirms the charter section by section.
- In a fresh session of Liquid_Nexus, with no instruction to read anything, the bootstrap context lists both documents and the agent's first message states the project's position and heading; the operator confirms that the statement is substantively correct.
- Nexus was not changed by hand in the host; any defect of the rules found is a feedback note.

What this does **not** show: that the cycle holds direction in the host, or that the agent leads there. That is T5c.

## Unknowns to observe

- Whether the host's knowledge is enough to reconstruct a position at all, or whether the project's purpose lives mostly in the operator's head; how many operator questions the reconstruction needs.
- Whether the charter sections (nature, goal, validation policy, horizon, definition of done, goal-change policy) fit a project of this kind, or one of them has nothing true to say.
- Whether the net of a real project fits on one screen at the first attempt, and whether a marking with no `← now` reads as a position or as an omission.
- Whether the host's agent, reading the Steering section, states the position after bootstrap in a form the operator can use, or recites it.
- Which defects of the delivered rules the host finds first, and whether the feedback channel is used for them without prompting.
