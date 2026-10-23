#!/usr/bin/env bash
# Restore a weather schema dump into the local MariaDB instance.
# Restores the dump as-is (all tables, including apscheduler_jobs and stale leftovers).
# Run on tec-weather2 after db-init.sh. Do not run pyway migrate first.
#
# Usage:
#   sudo ./scripts/db-restore.sh /mnt/clones/data/weather-migration/db/weather.sql
#   sudo ./scripts/db-restore.sh /mnt/clones/data/weather-migration/db/weather.sql --force
# Running with no arguments prints this syntax and exits.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

FORCE=0
DUMP_PATH=""

usage() {
  cat <<EOF
Usage: sudo ./scripts/db-restore.sh <dump.sql> [--force]

Read a plain SQL dump from the clones share into the local MariaDB.

Arguments:
  dump.sql   SQL file to load. Typical path:
             ${DB_DIR}/${DUMP_NAME}
  --force    Replace tables when ${DATABASE} is not empty

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
        echo "ERROR: unknown option: ${arg}" >&2
        usage >&2
        exit 1
        ;;
      *)
        if [[ -n "${DUMP_PATH}" ]]; then
          echo "ERROR: unexpected argument: ${arg}" >&2
          usage >&2
          exit 1
        fi
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
  if [[ -z "${DUMP_PATH}" ]]; then
    usage >&2
    exit 1
  fi

  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  [[ -f "${DUMP_PATH}" ]] || die "dump not found: ${DUMP_PATH}"

  verify_checksum "${DUMP_PATH}"

  local existing
  existing="$(table_count)"
  if [[ "${existing}" != "0" && "${FORCE}" -ne 1 ]]; then
    die "${DATABASE} already has ${existing} table(s). Pass --force to replace them from the dump."
  fi

  echo "Restoring ${DUMP_PATH} into ${DATABASE}"
  "${MYSQL_BIN}" <"${DUMP_PATH}"
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
