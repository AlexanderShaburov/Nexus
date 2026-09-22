---
type: spec
scope: system
status: approved
created: 2026-04-18
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [knowledge, decision-gate, lifecycle]
---

## Relations

- depends_on:
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — the per-turn decision implements the Retrieve obligation at turn granularity.
- relates_to:
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — the decision gate is the second non-negotiable gate.
  - [Plan: Context Decision claim via tool call](../plans/plan--system--context-decision-claim.md) — origin of Form A and the transcript failure it answers.
  - [Exit Gate Specification](spec--system--exit-gate.md) — paired closure gate; both must be present per turn.
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — the prompt and tool gates realize this spec.

---

# Context Decision Gate Specification

## Purpose

Context Decision Gate enforces explicit decision-making about Knowledge 
Base usage.

It prevents implicit ignorance of the Knowledge Vault and makes KB usage a 
conscious act.

---

## Mandatory Rule

Before starting task execution, the agent MUST explicitly answer:

> Is consulting the Knowledge Vault required to complete this task?

This step is mandatory for every task cycle.

---

## Allowed Responses

### YES

If YES, the agent MUST:

- identify relevant KB documents;
- read them;
- use retrieved context in reasoning.

---

### NO

If NO, the agent MUST explicitly justify:

- why the task is self-contained or trivial;
- why the current context is sufficient;
- why ignoring KB is safe;
- what risks are accepted.

---

## Invalid Responses

The following are INVALID:

- “No, not needed”
- “Context is sufficient” (without reasoning)
- implicit or skipped decision

---

## Enforcement

If the Decision Gate is:

- missing
- implicit
- unjustified

→ the response is considered INVALID.

---

## Decision Forms

The decision is stated **once per turn**, before the first mutating tool call, in one of two forms. Both are equivalent under this specification; the runtime checks them in this order.

### Form A — claim (tool-carried)

The first mutating tool call of the turn is a Bash call of fixed form:

```
python3 tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason "<why>"
python3 tools/nexus-decide.py --kb NO --reason "<why the KB is not needed and what risk is accepted>"
```

`tools/nexus-decide.py` decides nothing and writes nothing: it validates the arguments and prints the decision to the terminal in the shape of Form B, so the decision remains visible on screen and is persisted in the transcript as a tool call. The runtime reads the claim from the tool call's own parameters, which are persisted verbatim even in environments where the assistant's mid-turn text is persisted as a paraphrase (the failure that motivated this form; see `plans/plan--system--context-decision-claim.md`).

Recognition rules (mirrored by `parse_decision_claim` in `.claude/hooks/_nexus_common.py`):

- a single line and a single command; an optional leading `cd <dir> &&` is tolerated; shell operators, redirections, command substitution and backticks after the script path make the claim malformed;
- the script path resolves to `tools/nexus-decide.py` inside the project;
- only `--kb`, `--reason` and `--reads` are accepted; `--kb` is `YES` or `NO` (case-insensitive); `--reason` is required and at least 15 characters after whitespace normalization; `--reads` is required for `YES` and every path must be an existing file under the project.

A malformed claim is **denied with the defect named**; it does not fall through to Form B.

### Form B — text block

Plain text in the assistant's output of the current turn, before the mutating call:

```
### Context Decision
KB consult required: YES | NO
Reasoning: <why>
```

Form B is the fallback: it is consulted only when no claim has been seen in the turn. It depends on the transcript persisting assistant text verbatim.

### One decision per turn

Once either form has been accepted, later mutating calls in the same turn are not re-checked. The per-turn flag is reset on every new user prompt.

---

## Decision Trace

The decision MUST:

- be explicitly included in the output (Form B), or printed to the terminal by the claim (Form A);
- appear before main reasoning and before the first mutating tool call;
- not be hidden or omitted.

The runtime records the accepted decision in `.nexus/state.json` under `turn.decision` as `{kb, reason, reads, via: "claim"}` or `{kb, via: "text"}`.

