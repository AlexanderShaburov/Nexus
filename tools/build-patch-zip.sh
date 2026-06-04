#!/usr/bin/env bash
# Build a distributable zip from a Nexus patch bundle.
#
# Usage:
#   ./tools/build-patch-zip.sh <patch-bundle-dir> [output-dir]
#
# Example:
#   ./tools/build-patch-zip.sh patches/development-visibility
#   ./tools/build-patch-zip.sh patches/development-visibility dist/
#
# The bundle directory MUST contain PATCH_MANIFEST.yaml — the patch id and
# version are read from there to name the output zip.
#
# Output filename pattern:  nexus-<patch-id>-patch-v<version>.zip
#
# Default output directory: dist/   (created if absent)

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <patch-bundle-dir> [output-dir]" >&2
  exit 2
fi

BUNDLE_DIR="$1"
OUTPUT_DIR="${2:-dist}"

if [ ! -d "${BUNDLE_DIR}" ]; then
  echo "ERROR: bundle directory not found: ${BUNDLE_DIR}" >&2
  exit 2
fi

MANIFEST="${BUNDLE_DIR}/PATCH_MANIFEST.yaml"
if [ ! -f "${MANIFEST}" ]; then
  echo "ERROR: ${MANIFEST} not found. Is this a Nexus patch bundle?" >&2
  exit 2
fi

# Resolve required tools.
command -v zip >/dev/null 2>&1 || {
  echo "ERROR: 'zip' is required but not found on PATH." >&2
  exit 4
}

PYTHON="${PYTHON:-python3}"
command -v "${PYTHON}" >/dev/null 2>&1 || {
  echo "ERROR: '${PYTHON}' is required but not found on PATH." >&2
  exit 4
}

# Read patch_id and patch_version from the manifest.
read PATCH_ID PATCH_VERSION <<<"$("${PYTHON}" - "${MANIFEST}" <<'PY'
import sys, re, pathlib
text = pathlib.Path(sys.argv[1]).read_text()
pid = pver = None
for line in text.splitlines():
    m = re.match(r"^patch_id:\s*(\S+)", line)
    if m: pid = m.group(1).strip().strip("'\"")
    m = re.match(r"^patch_version:\s*(\S+)", line)
    if m: pver = m.group(1).strip().strip("'\"")
if not pid or not pver:
    print("ERROR: PATCH_MANIFEST.yaml missing patch_id or patch_version", file=sys.stderr)
    sys.exit(3)
print(f"{pid} {pver}")
PY
)"

if [ -z "${PATCH_ID:-}" ] || [ -z "${PATCH_VERSION:-}" ]; then
  echo "ERROR: failed to parse PATCH_MANIFEST.yaml" >&2
  exit 3
fi

mkdir -p "${OUTPUT_DIR}"
OUTPUT_DIR_ABS="$(cd "${OUTPUT_DIR}" && pwd)"
ZIP_NAME="nexus-${PATCH_ID}-patch-v${PATCH_VERSION}.zip"
ZIP_PATH="${OUTPUT_DIR_ABS}/${ZIP_NAME}"

# Make sure shipped scripts are executable inside the zip.
chmod +x "${BUNDLE_DIR}/apply.sh" "${BUNDLE_DIR}/apply.py" 2>/dev/null || true

# Build the zip. Bundle the directory itself so unzip creates a top-level folder
# named after the patch — matches the README's example unzip usage:
#   unzip nexus-development-visibility-patch.zip
#   → produces nexus-development-visibility-patch/
BUNDLE_PARENT="$(cd "$(dirname "${BUNDLE_DIR}")" && pwd)"
BUNDLE_LEAF="$(basename "${BUNDLE_DIR}")"

# Stage to a temp dir so we can rename the top-level folder cleanly.
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf "${STAGE_DIR}"' EXIT

TOP_DIR_NAME="nexus-${PATCH_ID}-patch"
cp -R "${BUNDLE_PARENT}/${BUNDLE_LEAF}" "${STAGE_DIR}/${TOP_DIR_NAME}"

# Clean any pycache that may have crept in.
find "${STAGE_DIR}/${TOP_DIR_NAME}" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

# Remove any pre-existing zip at the target path.
rm -f "${ZIP_PATH}"

( cd "${STAGE_DIR}" && zip -q -r "${ZIP_PATH}" "${TOP_DIR_NAME}" )

# Echo summary.
echo "=== Nexus patch zip built ==="
echo "  patch id:        ${PATCH_ID}"
echo "  patch version:   ${PATCH_VERSION}"
echo "  output:          ${ZIP_PATH}"
echo "  unzip produces:  ${TOP_DIR_NAME}/"
echo
echo "Distribute the file:"
echo "  ${ZIP_PATH}"
