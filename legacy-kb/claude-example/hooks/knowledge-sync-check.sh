#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
KNOWLEDGE VAULT PROTOCOL — REQUIRED

This project uses the Knowledge Vault as the primary operational memory.

For any non-trivial task:
1. Follow knowledge/specs/spec--system--knowledge-driven-task-orchestration.md
2. Use knowledge/index/index--system--project-navigation.md as the routing map
3. Retrieve relevant knowledge documents before implementation
4. Apply invariants, architecture, specs, decisions, and patterns as constraints
5. After completing the work, evaluate whether knowledge/ must be updated
6. Use knowledge/specs/spec--devops--knowledge-sync-classification.md for knowledge-impact review
7. If knowledge-bearing changes or new durable findings emerged, update the appropriate files in knowledge/
EOF