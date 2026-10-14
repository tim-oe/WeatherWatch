#!/usr/bin/env bash
# Restore a weather schema dump into the local MariaDB instance.
# Restores the dump as-is (all tables, including apscheduler_jobs and stale leftovers).
# Run on tec-weather2 after db-init.sh. Do not run pyway migrate first.
#
# Usage:
#   sudo ./scripts/db-restore.sh
#   sudo ./scripts/db-restore.sh /mnt/clones/data/weather-migration/db/weather.sql.gz
#   sudo ./scripts/db-restore.sh --force   # replace tables if weather is not empty
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

FORCE=0
DUMP_PATH=""

usage() {
  cat <<'EOF'
Usage: sudo ./scripts/db-restore.sh [dump.sql.gz] [--force]

Environment:
  MIG_ROOT   Staging root (default: /mnt/clones/data/weather-migration)
EOF
}

parse_args() {
  local arg
  for arg in "$@"; do
    case "${arg}" in
      -h|--help)
        usage
        exit 0
        ;;
      --force)
        FORCE=1
        ;;
      -*)
        die "unknown option: ${arg}"
        ;;
      *)
        [[ -z "${DUMP_PATH}" ]] || die "unexpected argument: ${arg}"
        DUMP_PATH="${arg}"
        ;;
    esac
  done
}

table_count() {
  mysql_n -e "SELECT COUNT(*) FROM information_schema.TABLES
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_TYPE='BASE TABLE'"
}

main() {
  parse_args "$@"
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  if [[ -z "${DUMP_PATH}" ]]; then
    DUMP_PATH="$(latest_migration_dump)"
  fi
  [[ -n "${DUMP_PATH}" ]] || die "no ${DUMP_NAME} dump under ${DB_DIR} (run db-dump.sh first)"
  [[ -f "${DUMP_PATH}" ]] || die "dump not found: ${DUMP_PATH}"

  verify_checksum "${DUMP_PATH}"

  local existing
  existing="$(table_count)"
  if [[ "${existing}" != "0" && "${FORCE}" -ne 1 ]]; then
    die "${DATABASE} already has ${existing} table(s). Pass --force to replace them from the dump."
  fi

  echo "Restoring ${DUMP_PATH} into ${DATABASE}"
  gunzip -c "${DUMP_PATH}" | "${MYSQL_BIN}"
  echo "Dump loaded."

  if [[ -f "${AQI_CLEAN_SQL}" ]]; then
    echo "Re-applying ${AQI_CLEAN_SQL}"
    "${MYSQL_BIN}" "${DATABASE}" <"${AQI_CLEAN_SQL}"
  else
    echo "WARN: ${AQI_CLEAN_SQL} not found; skipped aqi_clean re-apply" >&2
  fi

  echo
  echo "Tables now in ${DATABASE}:"
  mysql_exec "${DATABASE}" -e "SHOW TABLES"
  echo
  echo "Routines:"
  mysql_exec -e "SELECT ROUTINE_NAME, ROUTINE_TYPE
    FROM information_schema.ROUTINES
    WHERE ROUTINE_SCHEMA='${DATABASE}'"
  echo
  echo "Restore complete. Next: sudo ./scripts/db-inventory.sh and diff against the Phase 0 inventory."
}

main "$@"
