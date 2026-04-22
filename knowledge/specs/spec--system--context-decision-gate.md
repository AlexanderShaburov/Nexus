---
type: spec
scope: system
status: approved
created: 2026-04-18
updated: 2026-04-19
source_of_truth: true
tags: [knowledge, decision-gate, lifecycle]
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

## Decision Trace

The decision MUST:

- be explicitly included in the output;
- appear before main reasoning;
- not be hidden or omitted.

