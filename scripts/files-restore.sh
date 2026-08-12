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
# Creates empty service dirs (pix/vid are not part of the initial archive):
#   /var/lib/weatherwatch/pix
#   /var/lib/weatherwatch/vid
#
# MariaDB drop-ins are extracted to a review dir only (not into /etc/mysql),
# because stock package files differ between Bookworm 10.11 and Trixie 11.8.
# Pass --include-mysql-conf to also install etc/mysql/mariadb.conf.d into place.
set -euo pipefail

MIG_ROOT="${MIG_ROOT:-/mnt/clones/data/weather-migration}"
FILES_DIR="${MIG_ROOT}/files"
INCLUDE_MYSQL_CONF=0
ARCHIVE_PATH=""

RESTORE_PREFIXES=(
  etc/environment
)
MYSQL_PREFIX="etc/mysql/mariadb.conf.d"
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
Usage: sudo ./scripts/files-restore.sh [archive.tar.gz] [--include-mysql-conf]

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
        INCLUDE_MYSQL_CONF=1
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

list_members() {
  tar -tzf "${ARCHIVE_PATH}"
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

extract_selected() {
  local -a members=()
  local member prefix
  local review_dir

  mapfile -t members < <(list_members)

  local -a restore_members=()
  local -a mysql_members=()

  for member in "${members[@]}"; do
    for prefix in "${RESTORE_PREFIXES[@]}"; do
      if [[ "${member}" == "${prefix}" || "${member}" == "${prefix}/"* ]]; then
        restore_members+=("${member}")
        continue 2
      fi
    done
    if [[ "${member}" == "${MYSQL_PREFIX}" || "${member}" == "${MYSQL_PREFIX}/"* ]]; then
      mysql_members+=("${member}")
    fi
  done

  [[ ${#restore_members[@]} -gt 0 ]] || die "archive has none of the expected restore paths"

  # Backup existing /etc/environment if present
  if [[ -f /etc/environment ]]; then
    cp -a /etc/environment "/etc/environment.pre-migration.$(date +%Y%m%d_%H%M%S)"
  fi

  echo "Restoring ${#restore_members[@]} path(s) onto /"
  tar -C / -xzf "${ARCHIVE_PATH}" "${restore_members[@]}"

  if [[ ${#mysql_members[@]} -gt 0 ]]; then
    review_dir="${MIG_ROOT}/files/mysql-conf-review-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${review_dir}"
    tar -C "${review_dir}" -xzf "${ARCHIVE_PATH}" "${mysql_members[@]}"
    echo "MariaDB drop-ins extracted for review under:"
    echo "  ${review_dir}/${MYSQL_PREFIX}"

    if [[ "${INCLUDE_MYSQL_CONF}" -eq 1 ]]; then
      mkdir -p /etc/mysql/mariadb.conf.d
      echo "Installing MariaDB drop-ins into /etc/mysql/mariadb.conf.d (--include-mysql-conf)"
      tar -C / -xzf "${ARCHIVE_PATH}" "${mysql_members[@]}"
    else
      echo "Skipped installing mysql conf (pass --include-mysql-conf to apply)."
    fi
  fi
}

fix_perms() {
  chmod 644 /etc/environment || true
}

main() {
  parse_args "$@"
  need_root
  resolve_archive
  verify_checksum
  prepare_dest_dirs
  extract_selected
  fix_perms

  echo
  echo "Restore complete from:"
  echo "  ${ARCHIVE_PATH}"
  echo
  echo "Confirm:"
  echo "  ls -la /etc/environment /var/lib/weatherwatch/pix /var/lib/weatherwatch/vid"
}

main "$@"
