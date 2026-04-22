#!/usr/bin/env bash
# bootstrap-gate.sh — Session Bootstrap enforcer
# Hook: SessionStart (matchers: startup|resume|clear|compact)
# Spec: spec--system--session-bootstrap.md
#
# Enforcement:
#   * exit 2 (blocking) when required bootstrap artifacts are missing.
#   * stdout = additional context injected into the session: the mandatory
#     reading set, the Knowledge-Driven Mode rules, and the REQUIRED
#     verbatim "Session Bootstrap Completed" confirmation phrase.

set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

REQUIRED_DOCS=(
  "knowledge/index/index--system--project-navigation.md"
  "knowledge/specs/spec--system--knowledge-driven-task-orchestration.md"
  "knowledge/architecture/architecture--system--overall-structure.md"
)
INVARIANTS_DIR="knowledge/invariants"

missing=()
for doc in "${REQUIRED_DOCS[@]}"; do
  [[ -f "$ROOT/$doc" ]] || missing+=("$doc")
done

if [[ ! -d "$ROOT/$INVARIANTS_DIR" ]]; then
  missing+=("$INVARIANTS_DIR/ (directory)")
else
  # at least one non-hidden file must exist inside invariants/
  if ! find "$ROOT/$INVARIANTS_DIR" -maxdepth 1 -type f -name '*.md' ! -name '.*' | grep -q .; then
    missing+=("$INVARIANTS_DIR/ (no .md files)")
  fi
fi

if [[ ${#missing[@]} -gt 0 ]]; then
  {
    echo "SESSION BOOTSTRAP FAILED — required Knowledge Vault artifacts missing:"
    echo ""
    for m in "${missing[@]}"; do
      echo "  - $m"
    done
    echo ""
    echo "Per spec--system--session-bootstrap.md, bootstrap cannot proceed and all"
    echo "subsequent actions are considered INVALID until these artifacts exist."
    echo ""
    echo "Remediation:"
    echo "  1. Create the missing documents listed above (see example-kb/ for shape)."
    echo "  2. Ensure each file satisfies vault-validate.sh rules (frontmatter, naming)."
    echo "  3. Restart / resume the session so SessionStart bootstrap re-runs."
  } >&2
  exit 2
fi

cat <<'EOF'
====================================================================
SESSION BOOTSTRAP — REQUIRED (spec--system--session-bootstrap.md)
====================================================================

You are REQUIRED to execute this protocol BEFORE any other action.
This protocol executes exactly once per session (including after
context compaction, resume, and clear).

STEP 1 — READ, in full, the Mandatory Startup Reading Set:
  * knowledge/index/index--system--project-navigation.md
  * knowledge/specs/spec--system--knowledge-driven-task-orchestration.md
  * knowledge/architecture/architecture--system--overall-structure.md
  * knowledge/invariants/  (ALL files)

STEP 2 — Treat all invariants as NON-NEGOTIABLE constraints.

STEP 3 — Enter Knowledge-Driven Mode:
  * Knowledge Vault is the source of truth.
  * Memory is non-authoritative.
  * All work MUST be grounded in retrieved context.

STEP 4 — Before producing ANY other output, emit this confirmation
VERBATIM (Completion Confirmation per the spec):

    Session Bootstrap Completed

    Loaded:
      - navigation index
      - orchestration spec
      - system architecture
      - invariants

    Operational Mode:
      - Knowledge-Driven Mode: ACTIVE

PROHIBITED:
  * skipping any step
  * partial execution
  * beginning task execution before bootstrap completion
  * relying on prior memory instead of loaded knowledge

If this confirmation is absent from your first response, ALL subsequent
actions in this session are INVALID.
====================================================================
EOF
exit 0
