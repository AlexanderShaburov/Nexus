#!/usr/bin/env bash

# vault-validate.sh — validates knowledge vault files on Write/Edit operations
# Runs as PostToolUse hook. Receives hook JSON on stdin.
# Exit 2 + stderr when a file inside knowledge/ violates vault structure rules.

set -euo pipefail

VALID_TYPES=(
  "index"
  "architecture"
  "decisions"
  "invariants"
  "specs"
  "plans"
  "bugs"
  "patterns"
  "glossary"
  "runbooks"
  "sessions"
  "business"
  "open-questions"
)

VALID_STATUSES=(
  "active"
  "draft"
  "in-progress"
  "in_progress"
  "deprecated"
  "archived"
  "fixed"
  "open"
  "proposed"
  "implemented"
  "rejected"
  "superseded"
)

FORBIDDEN_NAMES=(
  "notes.md"
  "misc.md"
  "temp.md"
  "todo.md"
  "scratch.md"
  "draft.md"
  "untitled.md"
)

ERRORS=()

error() {
  ERRORS+=("$1")
}

# Read hook JSON from stdin, extract tool_input.file_path
# Reads only first 4KB to avoid blocking on large Write content.
extract_file_path() {
  local input
  input=$(head -c 4096 2>/dev/null || true)
  if [[ -z "$input" ]]; then
    echo ""
    return
  fi
  local path
  path=$(echo "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
  echo "${path:-}"
}

extract_front_matter() {
  local file_path="$1"
  awk '
  BEGIN { in_block=0; seen=0 }
  /^---$/ {
    seen++
    if (seen == 1) { in_block=1; next }
    if (seen == 2) { exit }
  }
  in_block { print }
  ' "$file_path"
}

# --- Main ---

FILE_PATH="$(extract_file_path)"

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Normalize absolute path to relative (handles macOS /var → /private/var symlink)
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [[ "$FILE_PATH" == "$PROJECT_ROOT"/* ]]; then
  FILE_PATH="${FILE_PATH#$PROJECT_ROOT/}"
elif [[ -d "$(dirname "$FILE_PATH")" ]]; then
  RESOLVED="$(cd "$(dirname "$FILE_PATH")" && pwd -P)/$(basename "$FILE_PATH")"
  if [[ "$RESOLVED" == "$PROJECT_ROOT"/* ]]; then
    FILE_PATH="${RESOLVED#$PROJECT_ROOT/}"
  fi
fi

# Only validate files inside knowledge/
if [[ "$FILE_PATH" != knowledge/* ]]; then
  exit 0
fi

# Skip .gitkeep files
FILENAME="$(basename "$FILE_PATH")"
if [[ "$FILENAME" == ".gitkeep" ]]; then
  exit 0
fi

REL_PATH="${FILE_PATH#knowledge/}"
FOLDER="$(dirname "$REL_PATH")"

# Validate folder is a known type
FOLDER_VALID=false
for t in "${VALID_TYPES[@]}"; do
  if [[ "$FOLDER" == "$t" ]]; then
    FOLDER_VALID=true
    break
  fi
done

if [[ "$FOLDER_VALID" == false ]]; then
  error "FOLDER: '$FOLDER' is not a valid vault type. Valid: ${VALID_TYPES[*]}"
fi

# Check for forbidden names
BASENAME_LOWER="$(echo "$FILENAME" | tr '[:upper:]' '[:lower:]')"
for forbidden in "${FORBIDDEN_NAMES[@]}"; do
  if [[ "$BASENAME_LOWER" == "$forbidden" ]]; then
    error "NAMING: '$FILENAME' is a forbidden generic name. Use <type>--<scope>--<statement>.md"
  fi
done

# Validate naming convention (skip index/ folder)
if [[ "$FOLDER" != "index" ]]; then
  NAMING_REGEX='^[a-z][a-z0-9_]*--[a-z][a-z0-9_-]*--[a-z][a-z0-9_-]+\.md$'

  if [[ ! "$FILENAME" =~ $NAMING_REGEX ]]; then
    error "NAMING: '$FILENAME' violates naming convention. Required: <type>--<scope>--<statement>.md"
  fi

  if [[ "$FILENAME" =~ [A-Z] ]]; then
    error "NAMING: '$FILENAME' contains uppercase characters. Must be lowercase only."
  fi

  if [[ "$FILENAME" =~ [[:space:]] ]]; then
    error "NAMING: '$FILENAME' contains spaces. Use kebab-case."
  fi

  # Validate type prefix matches folder (normalize underscores and hyphens)
  TYPE_PREFIX="${FILENAME%%--*}"
  FOLDER_SINGULAR="${FOLDER%s}"
  FOLDER_NORMALIZED="$(echo "$FOLDER_SINGULAR" | sed 's/[-_]/./g')"
  TYPE_NORMALIZED="$(echo "$TYPE_PREFIX" | sed 's/[-_]/./g')"

  if [[ "$TYPE_NORMALIZED" != "$FOLDER_NORMALIZED" && "$TYPE_PREFIX" != "$FOLDER" ]]; then
    error "NAMING: Type prefix '$TYPE_PREFIX' does not match folder '$FOLDER'."
  fi
fi

# Validate frontmatter
ABSOLUTE_PATH="$PROJECT_ROOT/$FILE_PATH"
if [[ ! -f "$ABSOLUTE_PATH" ]]; then
  error "FILE: '$FILE_PATH' does not exist on disk."
else
  FIRST_LINE="$(head -n 1 "$ABSOLUTE_PATH")"
  if [[ "$FIRST_LINE" != "---" ]]; then
    error "FRONT MATTER: File must start with '---'."
  else
    FRONT_MATTER="$(extract_front_matter "$ABSOLUTE_PATH")"

    if [[ -z "$FRONT_MATTER" ]]; then
      error "FRONT MATTER: No front matter content found between --- markers."
    else
      for field in type scope status date source_of_truth tags; do
        if ! echo "$FRONT_MATTER" | grep -qE "^${field}:"; then
          error "FRONT MATTER: Missing required field '$field'."
        fi
      done

      STATUS_VAL="$(echo "$FRONT_MATTER" | sed -n 's/^status:[[:space:]]*\([^[:space:]]*\).*/\1/p' | head -1)"
      if [[ -n "$STATUS_VAL" ]]; then
        STATUS_VALID=false
        for s in "${VALID_STATUSES[@]}"; do
          if [[ "$STATUS_VAL" == "$s" ]]; then
            STATUS_VALID=true
            break
          fi
        done
        if [[ "$STATUS_VALID" == false ]]; then
          error "FRONT MATTER: status '$STATUS_VAL' is invalid. Valid: ${VALID_STATUSES[*]}"
        fi
      fi

      DATE_VAL="$(echo "$FRONT_MATTER" | sed -n 's/^date:[[:space:]]*\([^[:space:]]*\).*/\1/p' | head -1)"
      if [[ -n "$DATE_VAL" && ! "$DATE_VAL" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        error "FRONT MATTER: date '$DATE_VAL' must be YYYY-MM-DD format."
      fi

      SOT_VAL="$(echo "$FRONT_MATTER" | sed -n 's/^source_of_truth:[[:space:]]*\([^[:space:]]*\).*/\1/p' | head -1)"
      if [[ -n "$SOT_VAL" && "$SOT_VAL" != "true" && "$SOT_VAL" != "false" ]]; then
        error "FRONT MATTER: source_of_truth must be 'true' or 'false', got '$SOT_VAL'."
      fi
    fi
  fi
fi

# Report errors
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  {
    echo "VAULT VALIDATION FAILED for: $FILE_PATH"
    echo ""
    for e in "${ERRORS[@]}"; do
      echo "  * $e"
    done
    echo ""
    echo "Fix ALL violations before proceeding."
  } >&2
  exit 2
fi

exit 0
