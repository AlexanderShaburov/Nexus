## Scope

This document:

- describes the conceptual model of the approach;
- records the observations that led to the emergence of the approach;
- is not a complete implementation specification.

Implementation details will be moved into separate documents:

- Session Bootstrap spec
- Context Decision Gate spec
- Exit Gate spec

# Session-Oriented Knowledge Integration Approach

## (A session-oriented approach to Knowledge Vault integration)

---

## 1. Problem

Previous attempts to introduce the Knowledge Vault (KB) as the agent’s 
primary working context revealed systemic problems.

The problem is two-sided in nature and manifests itself in two extreme 
protocol operating modes.

### 1.1 Protocol Dominance Problem

When attempting to introduce a strict mandatory protocol:

- the agent is required to perform fixed KB-related steps;
- the protocol begins to substitute for the thinking process itself;
- a significant portion of attention shifts from solving the task to 
formally executing the procedure.

As a result, it was observed that:

- the agent relies less on its own analytical capabilities;
- decisions become more formal and mechanical;
- flexibility and adaptability in handling the task are lost.

👉 The protocol begins to dominate thinking.

### 1.2 Protocol Ignorance Problem

When shifting to softer recommendations and reminders:

- the KB is perceived as an external and optional source;
- repeated instructions turn into “noise” (boilerplate);
- the agent stops taking the KB into account during its work.

As a result, it was observed that:

- the KB is effectively not used;
- context is reconstructed from code from scratch every time;
- accumulated knowledge does not influence decisions being made.

👉 The protocol begins to be ignored.

### 1.3 Systemic Contradiction

Thus, a key contradiction emerges:

- a rigid protocol leads to the Protocol Dominance Problem;
- a soft protocol leads to the Protocol Ignorance Problem.

At the same time:

- the Knowledge Vault does not become part of the session’s stable working 
context;
- the protocol is not integrated into the natural decision-making process;
- a knowledge-driven work cycle does not form.

---

## 2. Key observation: per-request reminders do not create stable behavior

During real work, the following behavior was observed:

- over the course of a long session (several hours of work);
- with reminders about the need to use the KB in every request;
- with no context limitations (the entire session fit within the model’s 
context window);

the agent did not refer to the Knowledge Vault even once.

This indicates that:

- repeated instructions at the level of individual requests do not create 
stable behavior;
- the KB is perceived as an external, optional element;
- the presence of instructions does not mean they are integrated into the 
thinking process.

### 2.1 Reconsidering the “short-term memory” model

Although the agent formally operates with “short-term memory”:

- its size (on the order of ~1M tokens) allows it to retain long sessions;
- within a single session, context effectively becomes stable;

however, even with the entire context present in memory:

- the Knowledge Vault remains outside the working space of decision-making.

👉 The problem is not the size of memory, but the structure of context.

### 2.2 The limitations of per-request instructions

An approach based on reminders in every request leads to:

- a boilerplate effect;
- gradual disregard of the instructions;
- a transition to the Protocol Ignorance Problem.

👉 Instructions repeated at every step lose their significance.

---

## 3. Key observation: the absence of session capture breaks continuity of 
work

During the work process, it was found that the agent systematically fails 
to comply with requirements for recording session results.

Despite explicit instructions being present:

- in Claude MD:
  - maintaining a communication log;
- in the Knowledge Vault:
  - saving session results in the `sessions` directory;

the agent:

- does not record the communication log;
- does not create session files;
- does not record the results of the work.

### 3.1 Consequences

This leads to the following problems:

- no accumulated work history exists;
- context between sessions is lost;
- the reasoning path cannot be reconstructed;
- the Knowledge Vault does not reflect the actual state of the project.

### 3.2 Break between sessions

As a result:

- each new session begins without relying on the previous one;
- the agent is forced to reconstruct context from code all over again;
- previously obtained knowledge is not used.

👉 A break in continuity of work emerges.

---

## 4. Key observation: code by itself does not restore project context

During the work, the agent explicitly relied on arguments such as:

- “it is enough to read the code”;
- “grep over the code gives everything needed.”

This shows that, in the absence of a stable mechanism for consulting the 
KB, the agent tends to treat code as a sufficient source of context.

### 4.1 What code actually provides

Code analysis makes it possible to recover:

- the current behavior of the system;
- the actual implementation;
- real dependencies and relationships between components.

In other words, code answers the question well:

- **how** the system is currently built.

### 4.2 What code does not provide

It is impossible to reliably reconstruct the following from code:

- project goals;
- reasons behind architectural decisions;
- implicit constraints;
- the historical context of changes;
- decisions that were already made and later abandoned.

In other words, code does not fully answer the question:

- **why** the system is built the way it is.

### 4.3 Why reconstructing context from code alone is a mistake

Trying to replace the KB with code analysis alone leads to the following:

- context is replaced by implementation;
- architectural meaning is lost;
- previously made decisions start being reassembled from scratch;
- the risk of violating invariants increases.

👉 Using code alone for decision-making is incomplete and potentially 
erroneous.

---

## 5. Key observation: there is no stable lifecycle control for working 
with the KB

Observations across sessions show that the problem is not only the 
presence or absence of instructions, but also the absence of stable 
lifecycle control points.

In practice, this manifested as follows:

- entering a new session does not guarantee restoring context from the KB;
- starting work on a response does not require an explicit decision about 
whether the KB is needed;
- completing a response does not guarantee that acquired knowledge will be 
written back into the KB.

### 5.1 Observed consequence

Because mandatory control points are absent:

- the KB may fail to enter the session context;
- the KB may be ignored at the moment of solving the task;
- the results of the work may fail to be returned to the KB.

### 5.2 Practical conclusion from the observations

The problem is not local, but lifecycle-based in nature:

- context is not initialized reliably;
- KB usage is not made the subject of a mandatory decision;
- writeback does not close the work cycle.

👉 Therefore, the problem lies not in one isolated rule, but in the 
absence of a stable lifecycle model for working with the Knowledge Vault.

---

## 6. Evolution of approaches

The current approach is the result of a sequence of attempts to integrate 
the Knowledge Vault into the agent’s workflow.

Two main approaches were implemented, and each revealed critical 
limitations.

### 6.1 Approach 1 — Rigid protocol (Deterministic Orchestration)

A mechanism was implemented:

- via a hook;
- with a rigidly defined action protocol;
- with mandatory execution of Knowledge Vault-related steps.

The agent was required to:

- read specific documents;
- follow a fixed sequence of steps;
- use the KB in every process.

#### Results

- the approach demonstrated stable and correct results;
- the Knowledge Vault was indeed used;
- formal discipline of work was ensured.

#### Identified problems

However, observations showed that:

- the agent perceives protocol steps as trivial operations;
- reliance on analytical capabilities decreases;
- depth of reasoning is reduced;
- the agent avoids using its strongest abilities.

👉 This corresponds to the Protocol Dominance Problem.

### 6.2 Approach 2 — Soft protocol (Advisory Model)

The approach was changed:

- rigid enforcement was replaced with recommendations;
- reminders about the need to work with the KB were added;
- the agent was given back freedom of decision-making.

#### Results

- the agent actively uses its analytical capabilities;
- the quality of reasoning improves;
- token consumption drops sharply (by multiples).

Within a session in which the agent had been introduced to the Knowledge 
Base and the working procedure:

- the agent actively uses the Knowledge Vault;
- an effective combination is observed:
  - KB + agent analytics.

👉 Within a single session, an optimal operating mode is achieved.

#### Identified problems

However, further observations revealed a critical limitation.

At the start of a new session:

- the agent does not reproduce knowledge about the Knowledge Vault;
- it completely ignores the previously established rules;
- it perceives repeated instructions as “noise” (boilerplate);
- it does not refer to the KB even once;
- context is once again built exclusively from code.

👉 Thus, the approach does not ensure stability across sessions.

This corresponds to:

- the Protocol Ignorance Problem;
- and indicates the absence of a mechanism for session-level context 
initialization.

### 6.3 The limitations of both approaches

Thus:

- a rigid protocol suppresses thinking;
- a soft protocol is ignored.

Neither approach ensures:

- stable use of the Knowledge Vault;
- preservation of the agent’s analytical capabilities;
- a closed knowledge-driven cycle across sessions.

### 6.4 The need for a combined approach

Based on these observations, a requirement is formulated.

👉 What is needed is an approach that:

- does not suppress the agent’s thinking;
- but also does not allow the Knowledge Vault to be ignored;
- integrates the KB into the work process;
- but does not replace thinking with a formal protocol.

👉 This leads to the development of a combined approach that unites:

- structural control points;
- freedom of execution between them.

---

## 7. Core idea of the approach

The approach is based on combining rigid control points with preserved 
freedom of thought between them.

The goal of the approach is to eliminate the contradiction between:

- the Protocol Dominance Problem;
- the Protocol Ignorance Problem;

by introducing a controlled lifecycle for the agent’s work.

### 7.1 Principle: control at the boundaries, freedom inside

The approach introduces three mandatory control points:

1. **Session Bootstrap** (entry)
2. **Context Decision Gate** (during the process)
3. **Exit Gate** (exit)

At the same time:

- between these points, the agent retains freedom of thought;
- the protocol does not replace the reasoning process, but governs its 
boundaries.

### 7.2 Resulting model

The agent’s work is structured as a closed cycle:

**Bootstrap → Decision → Execution → Exit**

where:

- entry and exit are strictly controlled;
- KB usage becomes the subject of a mandatory decision;
- the execution process remains free;
- the results of the work are closed through writeback and session 
capture.

### 7.3 Key effect of the approach

The approach ensures:

- integration of the Knowledge Vault into the working context;
- the impossibility of implicitly ignoring the KB;
- preservation of the agent’s analytical capabilities;
- accumulation of knowledge across sessions;
- synchronization between code and the Knowledge Vault.

👉 The Knowledge Vault becomes part of the execution environment, rather 
than a recommendation.

---

## 8. Session model of work

The following model of the agent’s working context is introduced:

**Agent working context** =
- session memory
- project code
- context from the Knowledge Vault

At the same time:

- session memory provides local continuity within the current work;
- project code remains the source of truth for implementation;
- the Knowledge Vault remains the source of truth for context.

👉 All three components must work together, but must not replace one 
another.

---

## 9. Operational model of work

The agent’s work is structured as a managed lifecycle with three mandatory 
control points:

1. **Session Bootstrap** — context initialization when entering a session;
2. **Context Decision Gate** — a mandatory decision about KB usage at the 
beginning of each cycle;
3. **Exit Gate** — mandatory closure of work results on exit.

Resulting scheme:

**Bootstrap → Decision → Execution → Exit**

---

## 10. Session Bootstrap

### 10.1 Purpose

Session Bootstrap is the mandatory entry point into a session.

Its task is to:

- restore project context;
- embed the Knowledge Vault into the agent’s initial state of thought;
- prevent the loss of context between sessions.

### 10.2 When it is performed

Session Bootstrap must be performed:

- at the start of a new session;
- when context is reset or compacted;
- when transitioning into a state where continuity with the previous 
context is no longer guaranteed.

### 10.3 Minimum mandatory actions

Within Session Bootstrap, the agent is required to:

1. read the minimum required set of Knowledge Vault documents;
2. read the latest relevant session record;
3. restore:
   - the current project state;
   - the active work area;
   - key constraints;
   - architectural invariants;
4. record that the session has been initialized.

👉 Without passing Bootstrap, the session is considered uninitialized.

### 10.4 Role of Bootstrap

Bootstrap must not replace the agent’s thinking.

Its role is:

- not to determine further steps;
- but to form the correct initial context state.

👉 Bootstrap sets the starting conditions, but does not govern the entire 
work process.

### 10.5 Bootstrap Validation (mandatory)

Session Bootstrap is considered complete only if the agent:

- lists the sources it has read (KB + session);
- briefly records:
  - the current project state;
  - the active task;
  - the constraints.

If this is missing:

- Bootstrap is considered not completed.

---

## 11. Context Decision Gate

### 11.1 Purpose

Context Decision Gate is a mandatory decision point at the beginning of 
each question–answer cycle.

Its task is to:

- prevent the agent from implicitly ignoring the Knowledge Vault;
- make the use or non-use of the KB a conscious and explicitly expressed 
decision.

### 11.2 Rule

After receiving a request and before starting work on the response, the 
agent must explicitly answer the question:

> Is consulting the Knowledge Vault required to complete this task?

This question is mandatory in every cycle, without exception.

### 11.3 If the answer is YES

If the agent answers that consulting the KB is required, it must:

- identify the relevant sections of the Knowledge Vault;
- read the corresponding documents;
- use the retrieved context in the solution.

### 11.4 If the answer is NO

If the agent answers that consulting the KB is not required, it must 
explicitly state:

- why the current task is considered self-contained or trivial;
- why the current context is sufficient;
- why the risks of ignoring the KB are considered acceptable.

Formal or implicit answers are not allowed.

👉 A “no” answer without justification is considered invalid.

### 11.5 Decision Trace

The answer to the Context Decision Gate must be:

- explicitly presented in the output;
- not hidden or omitted.

👉 The decision is part of the agent’s reasoning trace.

---

## 12. Exit Gate

### 12.1 Purpose

Exit Gate is the mandatory completion point of each work cycle.

Its task is to:

- record whether any meaningful changes were made;
- determine whether writeback is required;
- prevent the loss of knowledge between sessions.

### 12.2 Closure Block

Before completing the response, the agent must produce a Closure Block 
containing at minimum:

- `code changed: yes/no`
- `KB changed: yes/no`
- `session log written: yes/no`
- `writeback evaluation performed: yes/no`

### 12.3 Mandatory dependencies

If:

- `code changed = yes`

then:

- `writeback evaluation performed = yes` is mandatory.

If:

- a writeback evaluation has been performed;
- and the result is recognized as knowledge-bearing;

then:

- `KB changed = yes` is mandatory.

If:

- the agent believes that the KB does not need to be changed;

then it must:

- explicitly state the reason.

It is prohibited to:

- skip the explanation;
- leave the decision implicit;
- postpone writeback until later.

### 12.4 Session Persistence

Exit Gate must also ensure the persistence of session traces.

If the project uses:

- session files;
- a communication log;
- session frontmatter or metadata;

then the agent must:

- create a new session record when necessary;
- update the existing record of the current session;
- record the results of the completed work.

👉 The work is considered incomplete without preserving session traces.

### 12.5 Placement

The Closure Block must be:

- the last element of the response;
- always clearly separated from the main body of text.

👉 A response without a Closure Block is considered invalid.

---

## 13. Additional reinforcement mechanisms (optional)

In addition to the basic model, extra control mechanisms may be added in 
the future.

They are not part of the minimal core of the approach, but may be used as 
enforcement amplifiers when necessary.

These mechanisms must not be used until the base model has proven its 
stability.

### 13.1 Reactive signals from code activity

Additional signals may be possible, triggered:

- when critical directories or code zones are accessed;
- when working with architecturally significant files;
- when the codebase is accessed repeatedly without consulting the 
Knowledge Vault.

Examples:

- access to `shared/`, `state/`, `bootstrap/`, or other critical areas;
- several consecutive accesses to code without reading the KB;
- expansion of task scope without a context refresh.

### 13.2 Purpose

Such signals may be used to ask an additional question:

> Is the agent certain that refreshing context from the Knowledge Vault is 
not required?

### 13.3 Status

At the current stage, such mechanisms are considered:

- additional;
- experimental;
- optional for the base version of the approach.

👉 First, the operability of the base model without these reinforcements 
must be verified.

---

## 14. Principle of minimal intervention

The approach preserves:

- freedom of thought;
- the ability to explore;
- the agent’s initiative;
- the ability to perform deep code analysis.

The approach limits only:

- entry into the session;
- the requirement for an explicit decision about KB usage;
- exit from the work cycle;
- recording of knowledge-bearing results.

👉 Control is introduced not inside thinking, but at its boundaries.

---

## 15. Main difference from previous approaches

Previously, two extreme modes were used:

- a rigid deterministic protocol;
- a soft advisory approach.

The new approach differs in that it:

- does not attempt to fully control the agent’s thinking;
- but also does not leave KB work at the level of an optional reminder.

Instead:

- entry into the session is made mandatory and structured;
- the decision about KB usage is made mandatory and explicit;
- exit from the cycle is closed through mandatory writeback and session 
capture.

👉 This is a combined lifecycle-based approach.

---

## 16. Key formula

**Think freely.**  
**Initialize context explicitly.**  
**Decide consciously.**  
**Close with writeback.**

or, in abbreviated form:

**Bootstrap → Decide → Think → Write back**

---

## 17. Goal of the approach

The goal of the approach is to create a system in which:

- the Knowledge Vault becomes a stable external project context;
- the agent cannot implicitly forget about it;
- knowledge is not lost between sessions;
- code changes and knowledge about them remain synchronized;
- the agent’s analytical capabilities are preserved rather than suppressed 
by the protocol.

