#!/usr/bin/env bash
# Report tables in `weather` that are not in the canonical migration set.
# Writes a report and a DROP TABLE script; does not execute the drops.
# Refuses to run unless a pre-migration archive already exists on the share.
#
# Usage:
#   sudo ./scripts/db-stale-tables.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

HOST="$(hostname -s)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_PATH="${DB_DIR}/stale_tables_${HOST}_${STAMP}.txt"
DROP_PATH="${DB_DIR}/stale_tables_${HOST}_${STAMP}.drop.sql"

is_canonical() {
  local name="$1" t
  for t in "${CANONICAL_TABLES[@]}"; do
    [[ "${name}" == "${t}" ]] && return 0
  done
  return 1
}

main() {
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  local archive
  archive="$(latest_premigration_archive)"
  [[ -n "${archive}" ]] || die "no weather_premigration_*.sql.gz in ${DB_DIR}; run db-archive.sh first"

  local -a stale=()
  local table
  while IFS= read -r table; do
    [[ -n "${table}" ]] || continue
    if ! is_canonical "${table}"; then
      stale+=("${table}")
    fi
  done < <(list_weather_tables)

  {
    echo "host=${HOST}"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "gated_on_archive=${archive}"
    echo "canonical=${CANONICAL_TABLES[*]}"
    echo
    if [[ ${#stale[@]} -eq 0 ]]; then
      echo "No stale tables."
    else
      echo "Stale tables:"
      echo
      printf '%s\n' "table	table_rows	data_bytes	index_bytes	create_time"
      for table in "${stale[@]}"; do
        mysql_n -e "SELECT CONCAT_WS(CHAR(9),
            TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH, CREATE_TIME)
          FROM information_schema.TABLES
          WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_NAME='${table}'"
      done
    fi
  } >"${REPORT_PATH}"

  {
    echo "-- Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) on ${HOST}"
    echo "-- Review ${REPORT_PATH} before applying."
    echo "-- Apply with: sudo mariadb ${DATABASE} < ${DROP_PATH}"
    echo
    if [[ ${#stale[@]} -eq 0 ]]; then
      echo "-- none"
    else
      for table in "${stale[@]}"; do
        echo "DROP TABLE IF EXISTS \`${table}\`;"
      done
    fi
  } >"${DROP_PATH}"

  cat "${REPORT_PATH}"
  echo
  echo "Report: ${REPORT_PATH}"
  echo "Drops:  ${DROP_PATH}"
  if [[ ${#stale[@]} -gt 0 ]]; then
    echo "Review the report, then apply with:"
    echo "  sudo ${MYSQL_BIN} ${DATABASE} < ${DROP_PATH}"
  fi
}

main "$@"
