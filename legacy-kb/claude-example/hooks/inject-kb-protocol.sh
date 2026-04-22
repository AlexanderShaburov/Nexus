#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

ORCH="$ROOT/knowledge/specs/spec--system--knowledge-driven-task-orchestration.md"
INDEX="$ROOT/knowledge/index/index--system--project-navigation.md"
SYNC="$ROOT/knowledge/specs/spec--devops--knowledge-sync-classification.md"

missing=()

[[ -f "$ORCH" ]] || missing+=("$ORCH")
[[ -f "$INDEX" ]] || missing+=("$INDEX")
[[ -f "$SYNC" ]] || missing+=("$SYNC")

if [[ ${#missing[@]} -gt 0 ]]; then
  printf 'Knowledge Vault hook warning: missing required files:\n' >&2
  printf '  - %s\n' "${missing[@]}" >&2
  exit 0
fi

cat <<EOF
KNOWLEDGE VAULT PROTOCOL — REQUIRED

This project uses the Knowledge Vault as the primary operational memory.

Before working on any non-trivial task, you MUST:
1. Read and follow:
   - knowledge/specs/spec--system--knowledge-driven-task-orchestration.md
2. Use the routing and reading priority from:
   - knowledge/index/index--system--project-navigation.md
3. Retrieve the minimal relevant canonical knowledge documents before implementation.
4. Apply retrieved constraints from invariants, architecture, specs, decisions, and patterns.
5. After completing the work, determine whether the Knowledge Vault must be updated.
6. Use:
   - knowledge/specs/spec--devops--knowledge-sync-classification.md
   to evaluate whether the performed changes are knowledge-bearing.
7. If knowledge-bearing changes, bugs, decisions, patterns, or clarified behavior emerged, update the appropriate files in knowledge/.
8. For non-trivial tasks, do not skip structured knowledge writeback.
9. Do not rely on memory alone. Use the vault.
EOF