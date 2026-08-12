#!/usr/bin/env bash
# Archive WeatherWatch host files for station migration.
# Run on the source (old) host after weather services are stopped.
#
# Usage:
#   sudo ./scripts/files-archive.sh
#   sudo MIG_ROOT=/mnt/clones/data/weather-migration ./scripts/files-archive.sh
#
# Archives:
#   /etc/environment
#
# pix/vid are created empty on the target by files-restore.sh.
# MariaDB drop-ins are not archived: the Trixie package install is vanilla.
set -euo pipefail

MIG_ROOT="${MIG_ROOT:-/mnt/clones/data/weather-migration}"
FILES_DIR="${MIG_ROOT}/files"
STAMP="$(date +%Y%m%d_%H%M%S)"
HOST="$(hostname -s)"
ARCHIVE_NAME="weather_files_${HOST}_${STAMP}.tar.gz"
ARCHIVE_PATH="${FILES_DIR}/${ARCHIVE_NAME}"
MANIFEST_PATH="${FILES_DIR}/weather_files_${HOST}_${STAMP}.manifest"

REQUIRED_PATHS=(
  /etc/environment
)

die() {
  echo "ERROR: $*" >&2
  exit 1
}

need_root() {
  [[ "${EUID}" -eq 0 ]] || die "run as root (needed to read /etc/environment)"
}

ensure_staging() {
  mkdir -p "${MIG_ROOT}/files" "${MIG_ROOT}/db" "${MIG_ROOT}/inventory"
  [[ -w "${FILES_DIR}" ]] || die "not writable: ${FILES_DIR}"
}

collect_paths() {
  local path
  INCLUDE_PATHS=()

  for path in "${REQUIRED_PATHS[@]}"; do
    [[ -e "${path}" ]] || die "required path missing: ${path}"
    INCLUDE_PATHS+=("${path}")
  done
}

write_manifest() {
  local path size
  {
    echo "host=${HOST}"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "archive=${ARCHIVE_NAME}"
    echo "mig_root=${MIG_ROOT}"
    echo "paths:"
    for path in "${INCLUDE_PATHS[@]}"; do
      if [[ -d "${path}" ]]; then
        size="$(du -sb "${path}" 2>/dev/null | awk '{print $1}')"
        echo "  - path=${path} type=dir bytes=${size:-unknown}"
      else
        size="$(stat -c '%s' "${path}" 2>/dev/null || echo unknown)"
        echo "  - path=${path} type=file bytes=${size}"
      fi
    done
  } >"${MANIFEST_PATH}"
}

build_archive() {
  local -a tar_args=()
  local path

  for path in "${INCLUDE_PATHS[@]}"; do
    tar_args+=("${path#/}")
  done

  echo "Creating ${ARCHIVE_PATH}"
  tar -C / -czf "${ARCHIVE_PATH}" "${tar_args[@]}"
  (
    cd "${FILES_DIR}"
    sha256sum "${ARCHIVE_NAME}" >"${ARCHIVE_NAME}.sha256"
  )
}

main() {
  need_root
  ensure_staging
  collect_paths
  write_manifest
  build_archive

  echo
  echo "Archive complete."
  echo "  archive:  ${ARCHIVE_PATH}"
  echo "  checksum: ${FILES_DIR}/${ARCHIVE_NAME}.sha256"
  echo "  manifest: ${MANIFEST_PATH}"
  echo
  echo "Verify with:"
  echo "  (cd ${FILES_DIR} && sha256sum -c ${ARCHIVE_NAME}.sha256)"
}

main "$@"
