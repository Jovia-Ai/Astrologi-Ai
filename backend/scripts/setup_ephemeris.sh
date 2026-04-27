#!/usr/bin/env bash
# Swiss Ephemeris setup — production-ready.
#
# Downloads the minimum set of Swiss Ephemeris data files required by the
# Astrologi-AI backend into `backend/ephemeris/`. Idempotent: skips files
# already present. Safe to run from repo root or from `backend/`.
#
# Override target dir with SE_EPHE_PATH (absolute or relative to CWD).
#
# References:
#   - docs/setup_ephemeris.md
#   - backend/app/core/ephemeris_guard.py (REQUIRED_EPHE_FILES)
set -euo pipefail

# Find repo root: the parent of `backend/`.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Resolve target dir.
EPHE_DIR_DEFAULT="${REPO_ROOT}/backend/ephemeris"
EPHE_DIR="${SE_EPHE_PATH:-${EPHE_DIR_DEFAULT}}"

# Required minimum set (kept in sync with REQUIRED_EPHE_FILES in
# backend/app/core/ephemeris_guard.py — change both together).
REQUIRED_FILES=(
  "seas_18.se1"
  "sepl_18.se1"
  "semo_18.se1"
)

# GitHub mirror of the official Astrodienst Swiss Ephemeris distribution.
# Astrodienst's own HTTP path (https://www.astro.com/ftp/swisseph/ephe/)
# currently returns 404 for individual files, so we use the maintained
# mirror as primary. License and contents are identical (AGPL/dual-licensed,
# unchanged binary data).
BASE_URL_PRIMARY="https://raw.githubusercontent.com/aloistr/swisseph/master/ephe"
BASE_URL_FALLBACK="https://www.astro.com/ftp/swisseph/ephe"

mkdir -p "${EPHE_DIR}"
cd "${EPHE_DIR}"

echo "Swiss Ephemeris setup → ${EPHE_DIR}"
for f in "${REQUIRED_FILES[@]}"; do
  if [ -f "${f}" ] && [ -s "${f}" ]; then
    echo "  ✓ ${f} already present"
    continue
  fi
  echo "  ↓ downloading ${f}"
  # `--fail` → non-zero exit on HTTP error
  # `--silent --show-error` → quiet on success, loud on error
  # `--retry 3 --retry-delay 2` → resilient to flaky networks
  # `--location` → follow redirects (GitHub raw uses CDN redirects)
  if ! curl --fail --silent --show-error --location --retry 3 --retry-delay 2 \
    -o "${f}" "${BASE_URL_PRIMARY}/${f}"; then
    echo "  ⚠ primary mirror failed, trying fallback"
    rm -f "${f}"
    curl --fail --silent --show-error --location --retry 3 --retry-delay 2 \
      -o "${f}" "${BASE_URL_FALLBACK}/${f}"
  fi
  if [ ! -s "${f}" ]; then
    echo "ERROR: ${f} downloaded empty; aborting." >&2
    rm -f "${f}"
    exit 1
  fi
done

echo "Swiss Ephemeris setup complete."
