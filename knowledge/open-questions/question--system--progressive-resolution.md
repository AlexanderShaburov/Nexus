---
type: question
scope: system
status: draft
created: 2026-10-03
updated: 2026-10-06
source_of_truth: false
knowledge_visibility: development
theme: progressive-resolution
tags: [method, progressive-resolution, navigation, iteration, parking-lot, open-question]
---

## Relations

- relates_to:
  - [Knowledge-Driven Task Orchestration Specification](../specs/spec--system--knowledge-driven-task-orchestration.md) — the Planning Artifacts rule there ("structured sections → MUST be externalized as a plan") pulls toward early detail; this question asks whether that pull is right.
  - [Session Bootstrap Specification](../specs/spec--system--session-bootstrap.md) — the Mandatory Startup Reading Set tells the agent the rules but not the project's current position.
  - [Knowledge Visibility Specification](../specs/spec--system--knowledge-visibility.md) — the binding / development split already models "what is true now" versus "what is intended".
  - [Review Classification Invariant](../invariants/invariant--system--review-classification.md) — a future Position document would be one more place a review must look.

---

# Open question: should Nexus work at progressive resolution?

Parked by the operator on 2026-10-03. **Reopened by the operator on 2026-10-06.** The operational answer is being written as [Process Space Specification](../specs/spec--system--process-space.md) (draft): a `process/` directory beside the vault with `charter.md` and `navigation.md`. This note stays as the record of where the question came from; the sub-questions in §4 are answered there (who updates navigation: the agent at closure; where it lives: `process/`, outside the vault's `type` enum; the Planning Artifacts rule: bounded by the charter's horizon, spec §9).

## 1. Where the question comes from

The operator's host project Liquid_Nexus (a sibling repository, outside this vault) aims to describe how an organisation works by non-invasive observation: no interviews, no disruption of staff, only traces of activity. Working on it led, partly on the agent's advice, to a pause for studying Petri nets. The study is enjoyable but the operator's unease grew: the theory sits far from the project's current position, and nothing else visible needs it yet.

Discussing which chapters to study at which depth with another assistant produced a general observation about working with Claude under Nexus: the collaboration tends to **over-detail too early**.

The operator's image: a painter first lays out the composition in rough zones, then refines each zone, and paints hair and the glint in the eye last. Under Nexus the pair tends to paint every character in final detail before the composition exists. The operator finds it uncomfortable to specify contracts for a product they cannot yet see as a whole; this costs comfort and motivation.

The written form of the idea is the operator's recap `nexus_progressive_resolution_recap_ru.md` at the repository root (Russian, produced with another assistant, intentionally left untouched). Its terms are explicitly provisional: Progressive Resolution, Contextual Alignment, Proximity, Just-in-Time Elaboration, the navigation model Position / Heading / Horizon / Resolution, a one-screen iteration contract with a "We deliberately ignore" block, and a Vision / Current Model / Next Experiment triad per active direction.

## 2. What is being asked

Can Nexus give a host project a way to **raise resolution gradually**: see the whole picture coarsely, move, look, like or dislike, then refine only where the current level has produced a real need?

Two subjects are mixed in the recap and should be separated when the question is reopened:

1. the method for developing Nexus-the-product (traces from a project folder, then mail, CRM, Petri nets);
2. the method Nexus hands to **any host project** through its documents, gates and prompts.

The operator's intent is primarily (2).

## 3. First-pass assessment by the agent (2026-10-03, not a decision)

- **The real gap.** After bootstrap the agent knows the rules (invariants, architecture, orchestration, index) but not the project's position: where it is and which single question is being tested. `plans/` is a roadmap, not navigation. A short, binding Position document (Vision / Current Model / Next Experiment) read at bootstrap and updated at closure is the cheapest and most valuable part of the idea.
- **Already present.** `open-questions/` is the Parking Lot and the "Unknowns to observe" list. The binding / development / historical split already covers "Current Model: facts only". The phase-progression rule already pauses between phases.
- **Known tension.** The orchestration spec requires any structured multi-step answer to be externalised as a plan. If the idea is accepted, plans should be bounded to one iteration and far-horizon items become one line in `open-questions/`, not a plan.
- **Terminology.** Progressive Resolution and Just-in-Time Elaboration overlap and could merge. Contextual Alignment is a question, operational only through a Position document. The navigation model and the iteration contract are the operational core. The "We deliberately ignore" block could become an advisory routing rule (idea outside the iteration → `open-questions/`), not a blocking gate.
- **Risk.** Nexus is already heavy. Apply the method to itself: Trace v0 is one Position document and one question, "does the agent understand where the project is after bootstrap?". New frontmatter types, a fifth Closure field, a Parking Lot gate wait until that level shows what is missing.

## 4. Open sub-questions for when this is reopened

- Who updates Position: the operator by hand, or the agent inside the Exit Gate writeback evaluation?
- Does Position live in the Mandatory Startup Reading Set for hosts, and under which existing `type`?
- How does the Planning Artifacts rule in the orchestration spec change so it stops pulling toward early detail?
- Should the recap be normalised into the vault (English, `decision` for the why, `pattern` for the iteration contract), and when?
