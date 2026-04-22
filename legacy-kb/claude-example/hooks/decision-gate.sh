#!/usr/bin/env bash
# decision-gate.sh — Context Decision Gate enforcer
# Hook: UserPromptSubmit
# Spec: spec--system--context-decision-gate.md
#
# Enforcement:
#   * stdout is injected as additional context before the user's prompt.
#   * Requires the agent to emit an explicit "Decision Gate:" block BEFORE
#     any main reasoning or tool use, answering "Is KB consultation required?".
#   * Shallow / implicit / unjustified responses are declared INVALID.
#
# Note: hooks cannot parse free-form model output in real time; the Exit Gate
# (exit-gate.sh) and the Exit Gate spec are the downstream blocking check.
# This hook is the strongest per-prompt reminder + contract statement.

set -euo pipefail

cat <<'EOF'
====================================================================
CONTEXT DECISION GATE — REQUIRED (spec--system--context-decision-gate.md)
====================================================================

Before starting task execution for THIS prompt, you MUST explicitly
answer:

    Is consulting the Knowledge Base required to complete this task?

Your response MUST open with a "Decision Gate" block — placed BEFORE
any main reasoning, any tool use, and any implementation — in this
exact shape:

    Decision Gate:
    - KB consultation required: yes | no
    - Rationale: <reasoning>

Branch rules:

  IF yes:
    - List the specific Knowledge Vault documents you will read, by path.
    - Read them before reasoning or acting.
    - Use retrieved context in reasoning.

  IF no: provide a four-line justification, each on its own line:
    (1) why the task is self-contained or trivial;
    (2) why the current context is sufficient;
    (3) why ignoring the KB is safe;
    (4) what risks are accepted.

INVALID responses (cause the response to be considered INVALID):
  * "No, not needed"
  * "Context is sufficient" (without reasoning)
  * implicit decision / skipped decision
  * shallow answers without the four justification lines
  * Decision Gate placed AFTER reasoning or tool use

The Decision Gate MUST appear at the very top of your response and
MUST NOT be hidden or omitted.
====================================================================
EOF
exit 0
