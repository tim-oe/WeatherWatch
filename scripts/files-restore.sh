#!/usr/bin/env bash
# Restore WeatherWatch host files archived by files-archive.sh.
# Run on the target (new) host before starting weather services.
#
# Usage:
#   sudo ./scripts/files-restore.sh
#   sudo ./scripts/files-restore.sh /mnt/clones/data/weather-migration/files/weather_files_HOST_STAMP.tar.gz
#   sudo MIG_ROOT=/mnt/clones/data/weather-migration ./scripts/files-restore.sh
#
# Restores:
#   /etc/environment
#
# Creates empty service dirs (not part of the archive):
#   /var/lib/weatherwatch/pix
#   /var/lib/weatherwatch/vid
#
# MariaDB drop-ins are ignored even if an older archive contains them.
# Extract goes through a temp dir so GNU tar does not scan live /etc/mysql.
set -euo pipefail

MIG_ROOT="${MIG_ROOT:-/mnt/clones/data/weather-migration}"
FILES_DIR="${MIG_ROOT}/files"
ARCHIVE_PATH=""
ENV_MEMBER="etc/environment"
DATA_DIRS=(
  /var/lib/weatherwatch/pix
  /var/lib/weatherwatch/vid
)

die() {
  echo "ERROR: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage: sudo ./scripts/files-restore.sh [archive.tar.gz]

Environment:
  MIG_ROOT   Staging root (default: /mnt/clones/data/weather-migration)
EOF
}

need_root() {
  [[ "${EUID}" -eq 0 ]] || die "run as root (needed to write /etc and data dirs)"
}

parse_args() {
  local arg
  for arg in "$@"; do
    case "${arg}" in
      -h|--help)
        usage
        exit 0
        ;;
      --include-mysql-conf)
        echo "WARN: --include-mysql-conf is ignored; MariaDB drop-ins are not restored" >&2
        ;;
      -*)
        die "unknown option: ${arg}"
        ;;
      *)
        [[ -z "${ARCHIVE_PATH}" ]] || die "unexpected argument: ${arg}"
        ARCHIVE_PATH="${arg}"
        ;;
    esac
  done
}

resolve_archive() {
  local latest
  if [[ -n "${ARCHIVE_PATH}" ]]; then
    [[ -f "${ARCHIVE_PATH}" ]] || die "archive not found: ${ARCHIVE_PATH}"
    return
  fi

  [[ -d "${FILES_DIR}" ]] || die "files dir missing: ${FILES_DIR}"
  latest="$(ls -1t "${FILES_DIR}"/weather_files_*.tar.gz 2>/dev/null | head -n1 || true)"
  [[ -n "${latest}" ]] || die "no weather_files_*.tar.gz under ${FILES_DIR}"
  ARCHIVE_PATH="${latest}"
}

verify_checksum() {
  local dir base sha
  dir="$(dirname "${ARCHIVE_PATH}")"
  base="$(basename "${ARCHIVE_PATH}")"
  sha="${dir}/${base}.sha256"
  [[ -f "${sha}" ]] || die "checksum missing: ${sha}"
  echo "Verifying ${sha}"
  (cd "${dir}" && sha256sum -c "${base}.sha256")
}

prepare_dest_dirs() {
  local dir
  mkdir -p /var/lib/weatherwatch
  for dir in "${DATA_DIRS[@]}"; do
    mkdir -p "${dir}"
    chmod 755 "${dir}"
    echo "Ensured empty data dir: ${dir}"
  done
  chmod 755 /var/lib/weatherwatch
}

extract_environment() {
  local tmp
  tar -tzf "${ARCHIVE_PATH}" | grep -qx "${ENV_MEMBER}" \
    || die "archive is missing ${ENV_MEMBER}"

  if [[ -f /etc/environment ]]; then
    cp -a /etc/environment "/etc/environment.pre-migration.$(date +%Y%m%d_%H%M%S)"
  fi

  tmp="$(mktemp -d)"
  # Extract off to the side so GNU tar never walks live /etc (and /etc/mysql).
  tar --no-recursion --anchored --no-wildcards \
    -xzf "${ARCHIVE_PATH}" -C "${tmp}" "${ENV_MEMBER}"
  [[ -f "${tmp}/${ENV_MEMBER}" ]] || die "extract did not produce /${ENV_MEMBER}"
  cp -a "${tmp}/${ENV_MEMBER}" /etc/environment
  rm -rf "${tmp}"
  chmod 644 /etc/environment
  echo "Restored /etc/environment"
}

main() {
  parse_args "$@"
  need_root
  resolve_archive
  verify_checksum
  prepare_dest_dirs
  extract_environment

  echo
  echo "Restore complete from:"
  echo "  ${ARCHIVE_PATH}"
  echo
  echo "Confirm:"
  echo "  ls -la /etc/environment /var/lib/weatherwatch/pix /var/lib/weatherwatch/vid"
}

main "$@"
