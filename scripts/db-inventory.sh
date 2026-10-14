#!/usr/bin/env bash
# Diffable inventory of the weather schema. Run on tec-weather after stale
# drops (baseline) and again on tec-weather2 after restore.
#
# Usage:
#   sudo ./scripts/db-inventory.sh
#   sudo ./scripts/db-inventory.sh /path/to/outfile.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

HOST="$(hostname -s)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_PATH="${1:-${INV_DIR}/weather_inventory_${HOST}_${STAMP}.txt}"

has_column() {
  local table="$1" col="$2"
  local n
  n="$(mysql_n -e "SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_NAME='${table}' AND COLUMN_NAME='${col}'")"
  [[ "${n}" == "1" ]]
}

emit_table() {
  local table="$1"
  echo "===== TABLE ${table} ====="

  mysql_exec -e "SELECT
      TABLE_ROWS AS approx_rows,
      DATA_LENGTH AS data_bytes,
      INDEX_LENGTH AS index_bytes,
      CREATE_TIME,
      TABLE_COLLATION
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_NAME='${table}'\G"

  echo "-- COUNT(*)"
  mysql_exec "${DATABASE}" -e "SELECT COUNT(*) AS row_count FROM \`${table}\`"

  if has_column "${table}" id; then
    echo "-- MAX(id)"
    mysql_exec "${DATABASE}" -e "SELECT MAX(id) AS max_id FROM \`${table}\`"
  fi

  if has_column "${table}" read_time; then
    echo "-- MIN/MAX(read_time)"
    mysql_exec "${DATABASE}" -e "SELECT MIN(read_time) AS min_read_time, MAX(read_time) AS max_read_time FROM \`${table}\`"
  fi

  echo "-- SHOW CREATE TABLE"
  mysql_exec "${DATABASE}" -e "SHOW CREATE TABLE \`${table}\`\G"

  echo "-- PARTITIONS"
  mysql_exec -e "SELECT PARTITION_NAME, TABLE_ROWS, PARTITION_DESCRIPTION
    FROM information_schema.PARTITIONS
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_NAME='${table}'
      AND PARTITION_NAME IS NOT NULL
    ORDER BY PARTITION_ORDINAL_POSITION"
  echo
}

main() {
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  mkdir -p "$(dirname "${OUT_PATH}")"

  {
    echo "host=${HOST}"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "database=${DATABASE}"
    mysql_exec -e "SELECT VERSION() AS server_version,
      @@global.time_zone AS global_time_zone,
      @@session.time_zone AS session_time_zone,
      NOW() AS now_local,
      UTC_TIMESTAMP() AS now_utc\G"
    echo

    local table
    while IFS= read -r table; do
      [[ -n "${table}" ]] || continue
      emit_table "${table}"
    done < <(list_weather_tables)

    echo "===== ROUTINES ====="
    mysql_exec -e "SELECT ROUTINE_NAME, ROUTINE_TYPE
      FROM information_schema.ROUTINES
      WHERE ROUTINE_SCHEMA='${DATABASE}'
      ORDER BY ROUTINE_NAME"
  } >"${OUT_PATH}"

  echo "Inventory written to ${OUT_PATH}"
}

main "$@"
