#!/usr/bin/env bash
# Nexus Development Visibility patch — bash entry point.
#
# Default behaviour is DRY-RUN. Pass --apply to actually mutate the project.
#
# Usage:
#   ./apply.sh                       # dry-run, project is current working directory
#   ./apply.sh --apply               # apply for real
#   ./apply.sh --force               # skip "looks like a Nexus project" guard
#   ./apply.sh --backup-dir DIR      # override backup destination
#   ./apply.sh --project-root PATH   # operate on a project elsewhere
#   ./apply.sh --help
#
# Exit codes:
#   0  success
#   1  some edits were refused (manual patch needed)
#   2  target does not look like a Nexus project (use --force to override)
#   3  payload or target file missing
#   4  internal error
#   5  post-apply validation failed
#
# Python 3.10+ is required (matches the Nexus runtime requirement).

set -euo pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Resolve python interpreter.
PYTHON="${PYTHON:-}"
if [ -z "${PYTHON}" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
  else
    echo "ERROR: python3 is required but not found on PATH." >&2
    echo "Install python3 or set PYTHON=/path/to/python3 in the environment." >&2
    exit 4
  fi
fi

# Default project root is current working directory unless caller overrides.
PROJECT_ROOT_ARG=""
PASSTHRU=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT_ARG="$2"
      shift 2
      ;;
    --project-root=*)
      PROJECT_ROOT_ARG="${1#*=}"
      shift
      ;;
    --help|-h)
      "${PYTHON}" "${SELF_DIR}/apply.py" --help
      exit 0
      ;;
    *)
      PASSTHRU+=("$1")
      shift
      ;;
  esac
done

if [ -z "${PROJECT_ROOT_ARG}" ]; then
  PROJECT_ROOT_ARG="${PWD}"
fi

exec "${PYTHON}" "${SELF_DIR}/apply.py" \
  --bundle-dir "${SELF_DIR}" \
  --project-root "${PROJECT_ROOT_ARG}" \
  "${PASSTHRU[@]+"${PASSTHRU[@]}"}"
