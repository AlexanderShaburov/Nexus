# Prompt for Claude — SOKI Hooks Implementation + System Review

You are provided with a complete set of documents describing a Knowledge-Driven workflow system (SOKI) and the structure of a Knowledge Vault.

Your task has TWO equally important parts:

---

# PART 1 — IMPLEMENTATION (MANDATORY)

You MUST design and produce a working hook/runtime system that enforces the behavior described in the documents.

The system MUST enforce:

## 1. Session Bootstrap

- MUST run at:
  - session start
  - context reset / compaction
  - explicit trigger

- MUST block execution until:
  - required documents are read
  - Knowledge-Driven Mode is entered

- MUST NOT allow:
  - partial execution
  - skipping steps

---

## 2. Context Decision Gate

Before executing any non-trivial task:

The agent MUST explicitly answer:

> Is consulting the Knowledge Base required?

Enforcement requirements:

- MUST NOT allow silent continuation
- MUST require:
  - YES → read KB
  - NO → justified reasoning
- MUST reject:
  - shallow answers
  - implicit decisions

---

## 3. Exit Gate

Before finalizing ANY response:

The system MUST enforce:

- Closure Block presence
- Dependency rules:
  - code change → writeback evaluation
  - knowledge-bearing → KB update
- Justification when KB not updated

The system MUST:

- prevent completion without Closure Block
- prevent missing fields
- prevent silent skipping

---

## CRITICAL REQUIREMENT

You MUST design the system so that:

- Bootstrap blocks start
- Decision Gate blocks execution
- Exit Gate blocks completion

If hard blocking is not technically possible:

→ provide the strongest enforceable approximation  
→ explicitly describe limitations

---

# PART 2 — SYSTEM REVIEW (MANDATORY)

After implementation, you MUST:

## 1. Analyze the system

Evaluate:

- conceptual completeness
- consistency between:
  - SOKI
  - specs
  - vault structure
  - bootstrap logic

## 2. Identify weaknesses

Look for:

- gaps in enforcement
- ambiguous rules
- duplication
- potential failure modes
- scalability issues

## 3. Propose improvements

Provide:

- structural improvements
- missing specs
- simplifications
- stronger enforcement strategies

---

# INPUT DOCUMENTS

You are given:

- SOKI conceptual document
- Session Bootstrap spec
- Context Decision Gate spec
- Exit Gate spec
- World Structure (vault structure) spec
- Existing bootstrap.md
- CLAUDE.md
- Frontmatter spec

---

# DELIVERABLES

You MUST produce:

## 1. Findings
- what exists
- what is missing
- conflicts

## 2. Hook Architecture
- lifecycle
- trigger points
- control flow

## 3. Hook Files
- actual code/scripts
- minimal but functional

## 4. Placement Instructions
- exact file paths
- integration steps

## 5. Validation Plan
- how to verify enforcement works

## 6. System Review
- weaknesses
- risks
- edge cases

## 7. Improvements
- concrete proposals

---

# CONSTRAINTS

You MUST:

- NOT produce abstract recommendations only
- NOT collapse everything into one prompt
- NOT weaken enforcement into suggestions
- NOT assume capabilities that don't exist
- prefer clarity over cleverness

---

# PRIORITY

Implementation correctness > elegance

Enforcement strength > convenience

---

# FINAL NOTE

This is not a documentation task.

This is a **runtime behavior enforcement task**.

Your output must be installable and usable in a real project.
